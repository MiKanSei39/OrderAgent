"""FAQ 使用确定性检索，不为固定问题消耗大模型调用。"""
from difflib import SequenceMatcher
import re
import unicodedata

FAQ_ITEMS = [
    {'id': 'business_hours', 'question': '营业时间是什么时候？', 'answer': '六合餐厅周日至周四10:00—21:00，周五、周六10:00—23:00营业。', 'aliases': ['几点开门', '几点关门', '营业时间', '什么时候营业']},
    {'id': 'address', 'question': '餐厅位置在哪里？', 'answer': '六合餐厅位于上海市黄浦区人民广场六合大厦。', 'aliases': ['地址', '在哪里', '位置在哪', '餐厅位置', '你们在哪']},
    {'id': 'phone', 'question': '餐厅联系方式是什么？', 'answer': '大堂联系电话：021-12345678。', 'aliases': ['联系电话', '电话', '怎么联系', '联系方式']},
    {'id': 'parking', 'question': '停车方便吗？', 'answer': '目前未提供可核实的专用停车场或车位信息，请拨打021-12345678确认；不能保证有空车位。', 'aliases': ['停车', '停车场', '车位']},
    {'id': 'promotion', 'question': '有什么优惠活动？', 'answer': '课程FAQ示例活动：单次消费满200元九折，满500元八折。实际优惠规则与叠加条件请联系大堂确认。', 'aliases': ['优惠活动', '打折', '折扣', '优惠']},
]


def _normalize_text(text: str) -> str:
    return re.sub(r'[^\w\u4e00-\u9fff]', '', unicodedata.normalize('NFKC', text or '').lower())


def get_similarity_score(query: str, faq_question: str) -> float:
    q, c = _normalize_text(query), _normalize_text(faq_question)
    if not q or not c:
        return 0.0
    sequence = SequenceMatcher(None, q, c).ratio()
    union = set(q) | set(c)
    jaccard = len(set(q) & set(c)) / len(union)
    bonus = 0.2 if q in c or c in q else 0
    return min(1.0, 0.6 * sequence + 0.4 * jaccard + bonus)


class FaqService:
    def __init__(self, settings):
        self.settings = settings
        self.items = [dict(item) for item in FAQ_ITEMS]
        self.redis = None
        self.mode = 'local'

    async def start(self):
        if not self.settings.redis_url:
            return
        from redis.asyncio import Redis
        self.redis = Redis.from_url(self.settings.redis_url, decode_responses=True, socket_connect_timeout=3, socket_timeout=3)
        await self.redis.ping()
        key = f'{self.settings.faq_namespace}:ids'
        ids = sorted(await self.redis.smembers(key))
        if not ids:
            from agent.redis_data_sync import sync_faq_to_redis
            await sync_faq_to_redis(self.settings)
            ids = sorted(await self.redis.smembers(key))
        pipe = self.redis.pipeline()
        for item_id in ids:
            pipe.hgetall(f'{self.settings.faq_namespace}:item:{item_id}')
        import json
        self.items = []
        for row in await pipe.execute():
            if row.get('question') and row.get('answer'):
                row['aliases'] = json.loads(row.get('aliases', '[]'))
                self.items.append(row)
        self.mode = 'redis'

    def suggest(self, query, limit=3):
        if not _normalize_text(query):
            return []
        matches = []
        for item in self.items:
            score = max(get_similarity_score(query, candidate) for candidate in [item['question'], *item.get('aliases', [])])
            # 只对有明确业务词的短问题提供直达，不把长预订请求误判为FAQ。
            if len(query) <= 30 and any(alias in query for alias in item.get('aliases', [])):
                score = max(score, 0.88)
            if score >= self.settings.faq_threshold:
                matches.append({k: v for k, v in item.items() if k != 'aliases'} | {'score': round(score, 4)})
        return sorted(matches, key=lambda x: x['score'], reverse=True)[:limit]

    def direct_answer(self, query):
        # 包含预订、菜单、价格等复合需求时必须交给Agent，不只返回FAQ半句话。
        if any(word in query for word in ('预订', '预定', '预约', '推荐', '吃', '菜', '确认', '修改', '改成')):
            return None
        matches = self.suggest(query, 5)
        return '\n'.join(item['answer'] for item in matches if item['score'] >= 0.85) or None

    async def close(self):
        if self.redis:
            await self.redis.aclose()
