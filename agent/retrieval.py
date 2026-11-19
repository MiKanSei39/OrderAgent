"""Milvus语义检索；未配置服务时明确使用本地TF-IDF词法检索。"""
from pathlib import Path
import re


def menu_document(item):
    labels = {'dish_name': '菜名', 'description': '描述', 'flavor': '口味', 'main_ingredients': '食材', 'category': '分类', 'allergens': '过敏原', 'price': '价格'}
    return '\n'.join(f'{label}：{item.get(key, "")}' for key, label in labels.items())


def dietary_constraints(query):
    result = {'exclude_allergens': []}
    if any(word in query for word in ('不辣', '不要辣', '不能吃辣', '清淡', '不吃辣')):
        result['max_spice_level'] = 0
    elif '微辣' in query or '不太辣' in query:
        result['max_spice_level'] = 1
    if any(word in query for word in ('不吃素', '不想吃素', '不要素食', '不喜欢素食')):
        result['is_vegetarian'] = False
    elif any(word in query for word in ('素食', '吃素', '素菜', '全素', '不吃肉')):
        result['is_vegetarian'] = True
    for term in ('花生', '大豆', '麸质', '鱼', '虾', '蟹', '海鲜', '鸡肉', '牛肉', '坚果', '豆腐'):
        if re.search(rf'{term}.{{0,5}}(?:过敏|不能吃|不耐受)|(?:过敏|不吃|不能吃|不要|忌口).{{0,5}}{term}', query):
            result['exclude_allergens'].append(term)
    return result


def safe_candidates(items, exclusions):
    aliases = {'坚果': ['坚果', '花生'], '海鲜': ['鱼', '虾', '蟹', '海鲜'], '大豆': ['大豆', '豆腐', '豆瓣'], '鸡肉': ['鸡肉', '鸡胸肉']}
    return [item for item in items if not any(
        word in (item['allergens'] + ',' + item['main_ingredients'])
        for term in exclusions for word in aliases.get(term, [term])
    )]


class MenuRetriever:
    def __init__(self, database, settings):
        self.database, self.settings = database, settings
        self.client = None
        self.embeddings = None
        self.mode = 'local-tfidf'

    def connect(self):
        if not self.settings.milvus_uri:
            return
        from pymilvus import MilvusClient
        from langchain_huggingface import HuggingFaceEmbeddings
        if not Path(self.settings.embedding_model).is_dir():
            raise ValueError('Milvus模式需要本地嵌入模型，请设置 EMBEDDING_MODEL；不会自动下载大模型')
        self.embeddings = HuggingFaceEmbeddings(model_name=self.settings.embedding_model, model_kwargs={'device': 'cpu', 'local_files_only': True}, encode_kwargs={'normalize_embeddings': True})
        self.client = MilvusClient(uri=self.settings.milvus_uri, token=self.settings.milvus_token, timeout=10)
        if not self.client.has_collection(self.settings.milvus_collection):
            self.sync()
        self.mode = 'milvus'

    def sync(self):
        if self.client is None:
            raise ValueError('请先配置并连接 MILVUS_URI')
        from pymilvus import DataType
        items, _ = self.database.menu(limit=10000)
        if not items:
            return 0
        docs = [menu_document(item) for item in items]
        vectors = self.embeddings.embed_documents(docs)
        dimension = len(vectors[0])
        name = self.settings.milvus_collection
        if not self.client.has_collection(name):
            schema = self.client.create_schema(auto_id=False, enable_dynamic_field=False)
            schema.add_field('id', DataType.INT64, is_primary=True)
            schema.add_field('vector', DataType.FLOAT_VECTOR, dim=dimension)
            schema.add_field('text', DataType.VARCHAR, max_length=8192)
            index = self.client.prepare_index_params()
            index.add_index(field_name='vector', index_type='HNSW', metric_type='COSINE', params={'M': 16, 'efConstruction': 200})
            self.client.create_collection(name, schema=schema, index_params=index)
        else:
            fields = self.client.describe_collection(name).get('fields', [])
            vector = next((field for field in fields if field['name'] == 'vector'), {})
            if int(vector.get('params', {}).get('dim', 0)) != dimension:
                raise ValueError('Milvus已有集合的向量维度不匹配，请设置新的 MILVUS_COLLECTION；不会删除旧集合')
        # 按菜品主键upsert，重复运行不会重复插入，不删除已有集合。
        self.client.upsert(name, data=[{'id': item['id'], 'vector': vector, 'text': doc} for item, vector, doc in zip(items, vectors, docs)])
        self.client.flush(name)
        return len(items)

    def search(self, query, limit=3, max_spice_level=None, is_vegetarian=None, exclude_allergens=None):
        inferred = dietary_constraints(query)
        if inferred.get('max_spice_level') is not None:
            max_spice_level = min(inferred['max_spice_level'], 3 if max_spice_level is None else max_spice_level)
        if inferred.get('is_vegetarian') is not None:
            is_vegetarian = inferred['is_vegetarian']
        items, _ = self.database.menu(limit=10000, max_spice_level=max_spice_level, is_vegetarian=is_vegetarian)
        items = safe_candidates(items, [*(exclude_allergens or []), *inferred['exclude_allergens']])
        if not items:
            return {'mode': self.mode, 'items': [], 'message': '没有符合条件且可供应的菜品；过敏需求请再与大堂确认交叉污染风险。'}
        if self.client:
            vector = self.embeddings.embed_query(query)
            allowed = {item['id']: item for item in items}
            # 只从实时SQL筛选出的候选ID中搜索，向量库中的旧/停售菜不会漏出。
            hits = self.client.search(self.settings.milvus_collection, data=[vector], filter=f'id in {list(allowed)}', output_fields=['id'], limit=min(limit, len(allowed)), search_params={'metric_type': 'COSINE', 'params': {'ef': 64}})
            ranked = [allowed[hit['id']] | {'score': round(hit['distance'], 4)} for hit in hits[0] if hit['id'] in allowed]
        else:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 2))
            matrix = vectorizer.fit_transform([menu_document(item) for item in items])
            scores = cosine_similarity(vectorizer.transform([query]), matrix)[0]
            ranked = sorted([item | {'score': round(float(score), 4)} for item, score in zip(items, scores)], key=lambda item: item['score'], reverse=True)[:limit]
        return {'mode': self.mode, 'items': ranked, 'message': '以实际菜单为准；未知交叉污染风险不可保证完全无过敏原。'}

    def close(self):
        if self.client:
            self.client.close()
