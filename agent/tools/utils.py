from dataclasses import dataclass
from datetime import datetime

from langchain.tools import ToolRuntime, tool

from agent.database import Database
from agent.retrieval import MenuRetriever, dietary_constraints, safe_candidates
from agent.schemas import ReservationInput, SHANGHAI


@dataclass
class RestaurantContext:
    session_id: str
    user_query: str
    database: Database
    retriever: MenuRetriever


@tool
def search_menu(runtime: ToolRuntime[RestaurantContext], max_spice_level: int | None = None, is_featured: bool | None = None, is_vegetarian: bool | None = None, category: str | None = None, keyword: str | None = None, limit: int = 5):
    """按明确条件查询实际菜单：特色菜、菜系、荤素、最高辣度0-3、菜名；最多20道。口味偏好推荐请用user_flavor_search。"""
    from agent.schemas import SearchMenuInput
    args = SearchMenuInput(max_spice_level=max_spice_level, is_featured=is_featured, is_vegetarian=is_vegetarian, category=category, keyword=keyword, limit=limit)
    inferred = dietary_constraints(runtime.context.user_query)
    filters = args.model_dump()
    if inferred.get('max_spice_level') is not None:
        filters['max_spice_level'] = min(inferred['max_spice_level'], 3 if max_spice_level is None else max_spice_level)
    if inferred.get('is_vegetarian') is not None:
        filters['is_vegetarian'] = inferred['is_vegetarian']
    items, _ = runtime.context.database.menu(**filters)
    return safe_candidates(items, inferred['exclude_allergens'])


@tool
def user_flavor_search(query: str, runtime: ToolRuntime[RestaurantContext], limit: int = 3, max_spice_level: int | None = None, is_vegetarian: bool | None = None, exclude_allergens: list[str] | None = None):
    """依据口味、食材、清淡或饮食偏好推荐实际在售菜品；明确过敏/忌口必须加入exclude_allergens，辣度0-3，最多10道。"""
    if not 1 <= limit <= 10 or (max_spice_level is not None and not 0 <= max_spice_level <= 3):
        return {'error': 'limit应为1-10，辣度应为0-3'}
    return runtime.context.retriever.search(query + '；' + runtime.context.user_query, limit, max_spice_level, is_vegetarian, exclude_allergens)


@tool
def make_reservation(num_people: int, num_children: int, arrival_time: str, seat_preference: str, main_dish_preference: str, other_comments: str, runtime: ToolRuntime[RestaurantContext]):
    """信息齐全后生成待确认预订草稿，不会直接下单。必须先询问人数(含儿童)、到店时间、座位、主菜和备注，不能替用户猜测缺失信息。由用户后续明确确认才入库。"""
    try:
        data = ReservationInput(num_people=num_people, num_children=num_children, arrival_time=arrival_time, seat_preference=seat_preference, main_dish_preference=main_dish_preference, other_comments=other_comments)
        draft = runtime.context.database.draft(runtime.context.session_id, data)
        # 确认令牌只返回当前浏览器，不送进模型上下文。
        return {key: value for key, value in draft.items() if key != 'token'}
    except ValueError as exc:
        # 验证错误可被Agent纠正，但不返回数据库/网络机密。
        return {'status': 'validation_error', 'message': str(exc)}


@tool
def current_restaurant_time() -> str:
    """获取当前上海日期、时间和星期，用于解析今晚、明天等相对时间。"""
    return datetime.now(SHANGHAI).strftime('%Y-%m-%d %H:%M:%S %A Asia/Shanghai')


@tool
def reservation_status(runtime: ToolRuntime[RestaurantContext]):
    """查询当前会话真实订单和待确认草稿，询问是否订好、订单编号或内容时调用。"""
    orders, total = runtime.context.database.reservations(runtime.context.session_id, limit=10)
    pending = runtime.context.database.pending(runtime.context.session_id)
    if pending:
        pending = {key: value for key, value in pending.items() if key != 'token'}
    return {'confirmed_orders': orders, 'total': total, 'pending': pending}


async def get_mcp_tools(settings):
    if not settings.mcp_url:
        return []
    from langchain_mcp_adapters.client import MultiServerMCPClient
    connection = {'transport': settings.mcp_transport, 'url': settings.mcp_url}
    if settings.mcp_token:
        connection['headers'] = {'Authorization': f'Bearer {settings.mcp_token}'}
    client = MultiServerMCPClient({'amap-maps': connection})
    return await client.get_tools()
