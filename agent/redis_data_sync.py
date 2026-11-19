"""python -m agent.redis_data_sync；仅同步本应用命名空间，不 FLUSHDB。"""
import asyncio
import json

from agent.faq import FAQ_ITEMS
from config.config import Settings


async def sync_faq_to_redis(settings=None, items=None, replace=False):
    from redis.asyncio import Redis
    settings = settings or Settings()
    if not settings.redis_url:
        raise ValueError('请先设置 REDIS_URL')
    client = Redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=3)
    namespace = settings.faq_namespace
    records = FAQ_ITEMS if items is None else items
    try:
        pipe = client.pipeline(transaction=True)
        if replace:
            old_ids = await client.smembers(f'{namespace}:ids')
            for item_id in old_ids:
                pipe.delete(f'{namespace}:item:{item_id}')
            pipe.delete(f'{namespace}:ids')
        for item in records:
            payload = {**item, 'aliases': json.dumps(item.get('aliases', []), ensure_ascii=False)}
            pipe.hset(f'{namespace}:item:{item["id"]}', mapping=payload)
            pipe.sadd(f'{namespace}:ids', item['id'])
        if records or replace:
            await pipe.execute()
        return len(records)
    finally:
        await client.aclose()


if __name__ == '__main__':
    print(f'已同步 {asyncio.run(sync_faq_to_redis())} 条FAQ')
