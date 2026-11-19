"""python -m agent.milvus_data_sync：按主键同步，不drop集合。"""
from agent.database import Database
from agent.retrieval import MenuRetriever
from config.config import Settings


def insert_data():
    settings = Settings()
    if not settings.milvus_uri:
        raise ValueError('请先设置 MILVUS_URI 和 EMBEDDING_MODEL')
    db = Database(settings)
    retriever = MenuRetriever(db, settings)
    try:
        db.initialize()
        retriever.connect()
        return retriever.sync()
    finally:
        retriever.close()
        db.close()


if __name__ == '__main__':
    print(f'已同步 {insert_data()} 道菜品')
