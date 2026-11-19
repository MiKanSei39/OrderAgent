"""复用课程表名，参数化查询；草稿确认和写入处于同一个事务。"""
from datetime import datetime, timedelta
from decimal import Decimal
import json
import secrets

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, create_engine, func, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from agent.schemas import ReservationInput, SHANGHAI
from config.config import ROOT_DIR, Settings


def local_now():
    return datetime.now(SHANGHAI).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class MenuItem(Base):
    __tablename__ = 'menu_items'
    id: Mapped[int] = mapped_column(primary_key=True)
    dish_name: Mapped[str] = mapped_column(String(100))
    price: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    description: Mapped[str] = mapped_column(Text, default='')
    category: Mapped[str] = mapped_column(String(50))
    spice_level: Mapped[int] = mapped_column(Integer, default=0)
    flavor: Mapped[str] = mapped_column(String(100), default='')
    main_ingredients: Mapped[str] = mapped_column(Text, default='')
    cooking_method: Mapped[str] = mapped_column(String(50), default='')
    is_vegetarian: Mapped[bool] = mapped_column(Boolean, default=False)
    allergens: Mapped[str] = mapped_column(String(200), default='')
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=local_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=local_now, onupdate=local_now)


class ReservationOrder(Base):
    __tablename__ = 'reservation_order'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    num_people: Mapped[int] = mapped_column(Integer)
    num_children: Mapped[int] = mapped_column(Integer)
    arrival_time: Mapped[datetime] = mapped_column(DateTime)
    seat_preference: Mapped[str] = mapped_column(String(100))
    main_dish_preference: Mapped[str] = mapped_column(String(100))
    other_comments: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=local_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=local_now, onupdate=local_now)


class ReservationDraft(Base):
    __tablename__ = 'agent_reservation_draft'
    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(128), index=True)
    payload: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(16), default='pending')
    reservation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=local_now)


class ChatMessage(Base):
    __tablename__ = 'agent_chat_message'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(128), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=local_now)


def as_dict(row):
    result = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        if isinstance(value, Decimal):
            value = float(value)
        elif isinstance(value, datetime):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        result[column.name] = value
    return result


class Database:
    def __init__(self, settings: Settings):
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        connect_args = {'check_same_thread': False, 'timeout': 15} if str(settings.database_url).startswith('sqlite') else {'connect_timeout': 5}
        self.engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)

    def initialize(self):
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db, db.begin():
            if not db.scalar(select(func.count()).select_from(MenuItem)):
                records = json.loads((ROOT_DIR / 'data/menu.json').read_text(encoding='utf-8'))
                db.add_all(MenuItem(**record) for record in records)

    def menu(self, *, limit=100, offset=0, is_featured=None, max_spice_level=None, is_vegetarian=None, category=None, keyword=None):
        stmt = select(MenuItem).where(MenuItem.is_available.is_(True))
        for name, value in [('is_featured', is_featured), ('is_vegetarian', is_vegetarian), ('category', category)]:
            if value is not None:
                stmt = stmt.where(getattr(MenuItem, name) == value)
        if max_spice_level is not None:
            stmt = stmt.where(MenuItem.spice_level <= max_spice_level)
        if keyword:
            from sqlalchemy import or_
            stmt = stmt.where(or_(*(getattr(MenuItem, col).contains(keyword, autoescape=True) for col in ('dish_name', 'description', 'flavor', 'main_ingredients'))))
        with Session(self.engine) as db:
            total = db.scalar(select(func.count()).select_from(stmt.subquery()))
            rows = db.scalars(stmt.order_by(MenuItem.is_featured.desc(), MenuItem.price, MenuItem.id).limit(limit).offset(offset)).all()
            return [as_dict(row) for row in rows], total

    def draft(self, session_id: str, reservation: ReservationInput):
        payload = reservation.model_dump(mode='json')
        with Session(self.engine) as db, db.begin():
            db.execute(update(ReservationDraft).where(ReservationDraft.session_id == session_id, ReservationDraft.state == 'pending').values(state='invalid'))
            token = secrets.token_urlsafe(32)
            db.add(ReservationDraft(token=token, session_id=session_id, payload=json.dumps(payload, ensure_ascii=False)))
        return {'status': 'pending_confirmation', 'token': token, 'reservation': payload, 'message': '请核对预订信息，并点击确认预订或回复“确认预订”；尚未写入订单。'}

    def pending(self, session_id):
        with Session(self.engine) as db:
            row = db.scalars(select(ReservationDraft).where(ReservationDraft.session_id == session_id, ReservationDraft.state == 'pending', ReservationDraft.created_at >= local_now() - timedelta(minutes=30)).order_by(ReservationDraft.created_at.desc())).first()
            if row is None:
                return None
            return {'status': 'pending_confirmation', 'token': row.token, 'reservation': json.loads(row.payload)}

    def invalidate(self, session_id):
        with Session(self.engine) as db, db.begin():
            db.execute(update(ReservationDraft).where(ReservationDraft.session_id == session_id, ReservationDraft.state == 'pending').values(state='invalid'))

    def confirm(self, session_id, token):
        with Session(self.engine) as db, db.begin():
            row = db.get(ReservationDraft, token)
            if row is None or not secrets.compare_digest(row.session_id, session_id):
                raise ValueError('预订草稿不存在或不属于当前会话')
            if row.state == 'confirmed':
                return as_dict(db.get(ReservationOrder, row.reservation_id))
            if row.state != 'pending' or row.created_at < local_now() - timedelta(minutes=30):
                raise ValueError('草稿已失效，请重新填写并核对预订信息')
            data = ReservationInput.model_validate_json(row.payload).model_dump()
            claimed = db.execute(update(ReservationDraft).where(ReservationDraft.token == token, ReservationDraft.state == 'pending').values(state='processing'))
            if claimed.rowcount != 1:
                raise ValueError('预订正在处理，请刷新订单列表')
            data['arrival_time'] = data['arrival_time'].replace(tzinfo=None)
            order = ReservationOrder(**data)
            db.add(order)
            db.flush()
            row.state = 'confirmed'
            row.reservation_id = order.id
            return as_dict(order)

    def reservations(self, session_id, limit=20, offset=0):
        stmt = select(ReservationOrder).join(ReservationDraft, ReservationDraft.reservation_id == ReservationOrder.id).where(ReservationDraft.session_id == session_id, ReservationDraft.state == 'confirmed')
        with Session(self.engine) as db:
            total = db.scalar(select(func.count()).select_from(stmt.subquery()))
            rows = db.scalars(stmt.order_by(ReservationOrder.created_at.desc(), ReservationOrder.id.desc()).limit(limit).offset(offset)).all()
            return [as_dict(row) for row in rows], total

    def close(self):
        self.engine.dispose()

    def add_message(self, session_id, role, content):
        with Session(self.engine) as db, db.begin():
            db.add(ChatMessage(session_id=session_id, role=role, content=content))

    def history(self, session_id, limit=100):
        with Session(self.engine) as db:
            rows = db.scalars(select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.id.desc()).limit(limit)).all()
            return [as_dict(row) for row in reversed(rows)]
