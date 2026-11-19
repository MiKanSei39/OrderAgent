"""检查项目依赖，不修改数据、不输出密钥。"""
from pathlib import Path
import socket
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.config import Settings


def main():
    from sqlalchemy import create_engine, text
    settings = Settings()
    engine = create_engine(settings.database_url)
    try:
        with engine.connect() as conn:
            count = conn.scalar(text('SELECT COUNT(*) FROM menu_items'))
            print('SQL:', engine.dialect.name, '菜单条数:', count)
    finally:
        engine.dispose()
    if settings.redis_url:
        from redis import Redis
        with Redis.from_url(settings.redis_url, socket_connect_timeout=3) as client:
            print('Redis:', client.ping())
    if settings.milvus_uri:
        from pymilvus import MilvusClient
        client = MilvusClient(uri=settings.milvus_uri, token=settings.milvus_token, timeout=5)
        print('Milvus:', client.list_collections())
        client.close()
    print('模型:', settings.llm_provider, settings.llm_model, '密钥已配置:', bool(settings.llm_api_key))
    for port in (8000, 18088, 3000):
        with socket.socket() as conn:
            try:
                conn.bind(('127.0.0.1', port))
                print(f'端口{port}: 可绑定')
            except OSError as exc:
                print(f'端口{port}: 不可绑定 ({getattr(exc, "winerror", exc.errno)})')


if __name__ == '__main__':
    main()
