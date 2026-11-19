"""在外层事务中验证真实MySQL写入/幂等，最后回滚，不保留测试订单。"""
from datetime import datetime, timedelta
from pathlib import Path
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import func, select
from agent.database import Database, ReservationOrder
from agent.schemas import ReservationInput, SHANGHAI
from config.config import Settings


def main():
    db = Database(Settings())
    engine = db.engine
    assert engine.dialect.name == 'mysql', '这个脚本仅用于真实MySQL验证'
    try:
        with engine.connect() as connection:
            transaction = connection.begin()
            before = connection.scalar(select(func.count()).select_from(ReservationOrder))
            db.engine = connection
            try:
                sid = str(uuid4())
                data = ReservationInput(num_people=3, num_children=1, arrival_time=(datetime.now(SHANGHAI) + timedelta(days=3)).replace(hour=18, minute=30), seat_preference='靠窗', main_dish_preference='清淡', other_comments='事务回滚测试')
                draft = db.draft(sid, data)
                assert db.reservations(sid)[1] == 0
                order = db.confirm(sid, draft['token'])
                assert order['num_people'] == 3
                assert db.confirm(sid, draft['token'])['id'] == order['id']
                assert db.reservations(sid)[1] == 1
            finally:
                transaction.rollback()
                db.engine = engine
            after = connection.scalar(select(func.count()).select_from(ReservationOrder))
            assert before == after, '测试事务未正确回滚'
        print('PASS: 真实MySQL草稿、确认入库和重复确认；测试事务已回滚，原有订单条数不变。')
    finally:
        db.engine = engine
        db.close()


if __name__ == '__main__':
    main()
