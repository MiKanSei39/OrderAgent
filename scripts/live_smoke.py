"""真实Poke多轮工具联调；使用临时SQLite，不往用户MySQL里写测试订单。"""
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
import tempfile
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from api.main import create_app
from config.config import ROOT_DIR, Settings
from agent.schemas import SHANGHAI


def ask(client, query):
    response = client.post('/chat', json={'query': query})
    response.raise_for_status()
    events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith('data: ')]
    text = ''.join(item.get('content', '') for item in events if item['type'] in ('token', 'error'))
    print('USER:', query, flush=True)
    print('TOOLS:', [item.get('name') for item in events if item['type'] == 'tool'], flush=True)
    print('ASSISTANT:', text, flush=True)
    assert not any(item['type'] == 'error' for item in events), text
    return events


def main():
    with tempfile.TemporaryDirectory(prefix='live-smoke-', dir=ROOT_DIR / 'data') as directory:
        path = Path(directory)
        settings = Settings(database_url=f'sqlite:///{(path / "test.db").as_posix()}', data_dir=path)
        if not settings.llm_api_key:
            raise RuntimeError('需要有效POKE_API_KEY，这个脚本会真实调用模型')
        session_id = str(uuid4())
        with TestClient(create_app(settings)) as client:
            client.headers['X-Session-ID'] = session_id
            first = ask(client, '请推荐两道不辣的素食，必须根据实际菜单。')
            assert any(item['type'] == 'tool' for item in first)
            tomorrow = (datetime.now(SHANGHAI) + timedelta(days=1)).strftime('%Y-%m-%d')
            ask(client, f'帮我预订{tomorrow}晚上18:30，共3人，其中1位0-5岁儿童；座位靠窗，主菜清淡不辣，其他备注无。请先生成待确认草稿，不要直接下单。')
            draft = client.get('/reservation/pending').json()['pending']
            assert draft and draft['reservation']['num_people'] == 3
            assert client.get('/reservation/list').json()['total'] == 0
            ask(client, '人数改成4人，儿童仍是1位，其他信息不变。请更新确认单。')
            revised = client.get('/reservation/pending').json()['pending']
            assert revised and revised['reservation']['num_people'] == 4
            assert client.post('/reservation/confirm', json={'token': draft['token']}).status_code == 409
            final = ask(client, '确认预订')
            assert any(item['type'] == 'reservation_created' for item in final)
            assert client.get('/reservation/list').json()['total'] == 1
        # 换一个应用实例，模拟重启，检查业务和checkpoint都没有丢。
        with TestClient(create_app(settings)) as client:
            client.headers['X-Session-ID'] = session_id
            assert len(client.get('/chat/history').json()['messages']) == 8
            assert client.get('/reservation/list').json()['reservations'][0]['num_people'] == 4
            remembered = ask(client, '刚才我们把人数从几人改成几人了？请查询实际订单编号。')
            assert any(item['type'] == 'tool' and item['name'] == 'reservation_status' for item in remembered)
            text = ''.join(item.get('content', '') for item in remembered if item['type'] == 'token')
            assert '3' in text and '4' in text
            assert len(client.get('/chat/history').json()['messages']) == 10
        assert (path / 'checkpoints.sqlite').stat().st_size > 0
        print('PASS: Poke工具调用、多轮修改、二次确认、过期令牌、订单唯一性、重启后记忆与实时订单查询。', flush=True)


if __name__ == '__main__':
    main()
