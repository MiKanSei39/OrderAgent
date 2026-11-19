from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest

from agent.schemas import SHANGHAI
from api.main import create_app
from config.config import Settings


@pytest.fixture
def settings(tmp_path):
    return Settings(storage_backend='sqlite', database_url=f'sqlite:///{(tmp_path / "test.db").as_posix()}', data_dir=tmp_path, llm_provider='disabled', llm_api_key='', redis_url='', milvus_uri='', mcp_url='')


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as client:
        client.headers['X-Session-ID'] = str(uuid4())
        yield client


@pytest.fixture
def payload():
    arrival = (datetime.now(SHANGHAI) + timedelta(days=2)).replace(hour=18, minute=30, second=0, microsecond=0)
    return {'num_people': 3, 'num_children': 1, 'arrival_time': arrival.isoformat(), 'seat_preference': '靠窗', 'main_dish_preference': '清淡不辣', 'other_comments': '无'}
