from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, UUID4
from starlette.concurrency import run_in_threadpool

from agent.database import Database
from agent.schemas import ReservationInput
from agent.service import AssistantService
from config.config import ROOT_DIR, Settings


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    session_id: UUID4 | None = None


class ConfirmRequest(BaseModel):
    token: str = Field(min_length=40, max_length=64)


def session_id(request: Request, response: Response) -> str:
    value = request.headers.get('X-Session-ID') or request.cookies.get('orderagent_session')
    if value:
        try:
            if UUID(value).version != 4:
                raise ValueError()
            value = str(UUID(value))
        except ValueError:
            raise HTTPException(400, '无效的会话ID，请新建会话')
    else:
        value = str(uuid4())
    response.set_cookie('orderagent_session', value, httponly=True, samesite='strict', max_age=2592000)
    return value


def create_app(settings: Settings | None = None):
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app):
        db = Database(settings)
        service = AssistantService(db, settings)
        app.state.database, app.state.assistant = db, service
        try:
            await run_in_threadpool(db.initialize)
            await service.start()
            yield
        finally:
            await service.close()
            db.close()

    app = FastAPI(title='六合餐厅 · 智能点餐系统', version='1.0.0', lifespan=lifespan)
    router = APIRouter()

    @router.get('/health')
    async def health(request: Request):
        service = request.app.state.assistant
        return {'status': 'ok', 'database': service.database.engine.dialect.name, 'faq': service.faq.mode, 'retrieval': service.retriever.mode, 'llm': {'configured': bool(settings.llm_api_key) and settings.llm_provider != 'disabled', 'provider': settings.llm_provider, 'model': settings.llm_model}, 'mcp': service.mcp_status, 'timezone': 'Asia/Shanghai'}

    @router.get('/session')
    async def session(sid: str = Depends(session_id)):
        return {'session_id': sid}

    @router.post('/chat')
    async def chat(body: ChatRequest, request: Request, sid: str = Depends(session_id)):
        query = body.query.strip()
        if not query:
            raise HTTPException(422, '问题不能为空')
        if body.session_id:
            sid = str(body.session_id)
        result = StreamingResponse(request.app.state.assistant.stream(query, sid), media_type='text/event-stream', headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no', 'X-Session-ID': sid})
        result.set_cookie('orderagent_session', sid, httponly=True, samesite='strict', max_age=2592000)
        return result

    @router.get('/chat/history')
    async def history(request: Request, sid: str = Depends(session_id)):
        return {'messages': await run_in_threadpool(request.app.state.database.history, sid), 'session_id': sid}

    @router.get('/faq/suggest')
    async def faq(request: Request, query: str = Query('', max_length=500), limit: int = Query(3, ge=1, le=10)):
        return {'success': True, 'query': query, 'suggestions': request.app.state.assistant.faq.suggest(query, limit)}

    @router.get('/menu/list')
    async def menu(request: Request, limit: int = Query(100, ge=1, le=100), offset: int = Query(0, ge=0), is_featured: bool | None = None, is_vegetarian: bool | None = None, max_spice_level: int | None = Query(None, ge=0, le=3), category: str | None = Query(None, max_length=50), keyword: str | None = Query(None, max_length=100)):
        items, total = await run_in_threadpool(request.app.state.database.menu, limit=limit, offset=offset, is_featured=is_featured, is_vegetarian=is_vegetarian, max_spice_level=max_spice_level, category=category, keyword=keyword)
        return {'success': True, 'menu_items': items, 'count': len(items), 'total': total, 'message': 'success'}

    @router.get('/menu/recommend')
    async def recommend(request: Request, query: str = Query(min_length=1, max_length=500), limit: int = Query(3, ge=1, le=10)):
        return await run_in_threadpool(request.app.state.assistant.retriever.search, query, limit)

    @router.post('/reservation/draft')
    async def draft(body: ReservationInput, request: Request, sid: str = Depends(session_id)):
        service = request.app.state.assistant
        async with service.session_lock(sid):
            return await run_in_threadpool(service.database.draft, sid, body)

    @router.get('/reservation/pending')
    async def pending(request: Request, sid: str = Depends(session_id)):
        return {'pending': await run_in_threadpool(request.app.state.database.pending, sid)}

    @router.post('/reservation/confirm')
    async def confirm(body: ConfirmRequest, request: Request, sid: str = Depends(session_id)):
        service = request.app.state.assistant
        try:
            async with service.session_lock(sid):
                reservation = await run_in_threadpool(service.database.confirm, sid, body.token)
            return {'success': True, 'reservation': reservation, 'message': '预订成功'}
        except ValueError as exc:
            raise HTTPException(409, str(exc))

    @router.delete('/reservation/pending')
    async def cancel_draft(request: Request, sid: str = Depends(session_id)):
        async with request.app.state.assistant.session_lock(sid):
            await run_in_threadpool(request.app.state.database.invalidate, sid)
        return {'success': True, 'message': '已取消待确认草稿，不影响已确认订单'}

    @router.get('/reservation/list')
    async def reservations(request: Request, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), sid: str = Depends(session_id)):
        rows, total = await run_in_threadpool(request.app.state.database.reservations, sid, limit, offset)
        return {'success': True, 'reservations': rows, 'count': len(rows), 'total': total, 'message': 'success'}

    app.include_router(router)
    app.include_router(router, prefix='/api', include_in_schema=False)
    dist = ROOT_DIR / 'ui/dist'
    if (dist / 'assets').is_dir():
        app.mount('/assets', StaticFiles(directory=dist / 'assets'), name='assets')

    @app.get('/', include_in_schema=False)
    async def home():
        if (dist / 'index.html').is_file():
            return FileResponse(dist / 'index.html')
        return {'message': 'API已启动。进入ui目录运行npm install和npm run dev，或npm run build后重启后端。', 'docs': '/docs'}

    return app


app = create_app()
