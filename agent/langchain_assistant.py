# 导入模块
from pathlib import Path
import pymysql
from pymysql.cursors import DictCursor
from langchain.tools import tool
import os
from dotenv import load_dotenv


#====================================

# 加载环境配置文件
load_dotenv()

#====================================

# 应用根目录
ROOT_DIR = Path(__file__).parent.parent

#====================================
@tool
def search_main_dishes():
    """搜索餐厅的特殊菜品"""
    # 创建链接
    with pymysql.connect(
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT", "3306")),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
        charset=os.getenv("CHARSET")
    ) as conn:
        # 创建游标(字典格式游标)
        with conn.cursor(DictCursor) as cursor:
            # 执行检索
            cursor.execute("""
                select
                    `dish_name` as 菜品名称,
                    `price` as 价格,
                    `description` as 描述,
                    `category` as 类别,
                    `spice_level` as 辣度,
                    `flavor` as 口味,
                    `main_ingredients` as 主料,
                    `cooking_method` as 烹饪方式,
                    `is_vegetarian` as 是否素食,
                    `allergens` as 过敏源
                from
                    `menu_items`
                where
                    `is_featured`=1 AND `is_available`=1
            """)
            # 提取全部数据
            main_dishes = cursor.fetchall()
    #返回
    return main_dishes
# 创建智能体
# -单例模式：提供智能体
async def get_agent():
    """提供同一事件循环内的持久化Agent；API使用自身lifespan管理的实例。"""
    return await (await get_service()).get_agent()


_service = None


async def get_service():
    global _service
    if _service is None:
        from config.config import Settings
        from agent.database import Database
        from agent.service import AssistantService
        settings = Settings()
        db = Database(settings)
        db.initialize()
        _service = AssistantService(db, settings)
        await _service.start()
    return _service


async def assistant_query(user_query: str, session_id: str):
    async for chunk in (await get_service()).stream(user_query, session_id):
        yield chunk


async def test_agent():
    import asyncio
    from uuid import uuid4
    service = await get_service()
    session_id = str(uuid4())
    try:
        while query := await asyncio.to_thread(input, '你（回车退出）> '):
            async for chunk in service.stream(query, session_id):
                print(chunk, end='', flush=True)
    finally:
        await service.close()
        service.database.close()


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_agent())
