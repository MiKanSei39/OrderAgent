from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from agent.faq import get_similarity_score
from agent.schemas import SHANGHAI


def events(response):
    import json
    return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith('data: ')]


def test_health_and_original_menu(client):
    assert client.get('/health').json()['database'] == 'sqlite'
    result = client.get('/menu/list').json()
    assert result['count'] == result['total'] == 5
    assert {row['dish_name'] for row in result['menu_items']} == {'宫保鸡丁', '麻婆豆腐', '清炒时蔬', '红烧鲈鱼', '蒜蓉西兰花'}


def test_menu_filters_false_is_not_ignored(client):
    rows = client.get('/menu/list', params={'is_vegetarian': 'false'}).json()['menu_items']
    assert len(rows) == 3 and not any(row['is_vegetarian'] for row in rows)
    featured = client.get('/menu/list', params={'is_featured': True, 'max_spice_level': 0}).json()['menu_items']
    assert [row['dish_name'] for row in featured] == ['清炒时蔬']


def test_menu_limit_and_sql_injection(client):
    page = client.get('/menu/list', params={'limit': 1, 'offset': 1}).json()
    assert page['count'] == 1 and page['total'] == 5
    assert client.get('/menu/list', params={'category': "川菜' OR 1=1 --"}).json()['count'] == 0
    assert client.get('/menu/list', params={'keyword': '%'}).json()['count'] == 0
    assert client.get('/menu/list', params={'limit': 0}).status_code == 422
    assert client.get('/menu/list', params={'max_spice_level': 4}).status_code == 422


def test_faq_threshold_empty_and_unrelated(client):
    assert client.get('/faq/suggest', params={'query': ''}).json()['suggestions'] == []
    assert client.get('/faq/suggest', params={'query': '火星量子计算XYZ'}).json()['suggestions'] == []
    phone = client.get('/faq/suggest', params={'query': '电话'}).json()['suggestions'][0]
    assert phone['id'] == 'phone' and '021-12345678' in phone['answer']
    assert get_similarity_score('', '') == 0
    assert 0 <= get_similarity_score('你好', '你好') <= 1


def test_faq_stream_and_history_without_llm(client):
    response = client.post('/chat', json={'query': '营业时间是什么时候？'})
    assert response.status_code == 200 and response.headers['content-type'].startswith('text/event-stream')
    result = events(response)
    assert any(item['type'] == 'source' for item in result)
    assert '10:00' in ''.join(item.get('content', '') for item in result)
    assert result[-1]['type'] == 'done'
    history = client.get('/chat/history').json()['messages']
    assert [item['role'] for item in history] == ['user', 'assistant']
    assert client.post('/chat', json={'query': '   '}).status_code == 422


def test_no_confirmation_no_order(client, payload):
    draft = client.post('/reservation/draft', json=payload)
    assert draft.status_code == 200
    assert draft.json()['status'] == 'pending_confirmation'
    assert client.get('/reservation/list').json()['total'] == 0
    assert client.get('/reservation/pending').json()['pending']['token'] == draft.json()['token']


def test_confirmation_and_idempotence(client, payload):
    token = client.post('/reservation/draft', json=payload).json()['token']
    first = client.post('/reservation/confirm', json={'token': token})
    second = client.post('/reservation/confirm', json={'token': token})
    assert first.status_code == second.status_code == 200
    assert first.json()['reservation']['id'] == second.json()['reservation']['id']
    assert first.json()['reservation']['num_children'] == 1
    assert client.get('/reservation/list').json()['total'] == 1
    assert client.get('/reservation/pending').json()['pending'] is None


def test_chat_confirmation_requires_prior_draft(client, payload):
    result = events(client.post('/chat', json={'query': '确认预订'}))
    assert not any(item['type'] == 'reservation_created' for item in result)
    client.post('/reservation/draft', json=payload)
    result = events(client.post('/chat', json={'query': '确认预订'}))
    assert any(item['type'] == 'reservation_created' for item in result)
    assert client.get('/reservation/list').json()['total'] == 1


def test_revised_draft_revokes_old_token(client, payload):
    old = client.post('/reservation/draft', json=payload).json()['token']
    new = client.post('/reservation/draft', json=payload | {'num_people': 4}).json()['token']
    assert client.post('/reservation/confirm', json={'token': old}).status_code == 409
    assert client.post('/reservation/confirm', json={'token': new}).json()['reservation']['num_people'] == 4


def test_cancel_draft_never_cancels_existing_orders(client, payload):
    first = client.post('/reservation/draft', json=payload).json()['token']
    client.post('/reservation/confirm', json={'token': first})
    second = client.post('/reservation/draft', json=payload).json()['token']
    client.delete('/reservation/pending')
    assert client.post('/reservation/confirm', json={'token': second}).status_code == 409
    assert client.get('/reservation/list').json()['total'] == 1


def test_session_isolation(client, payload):
    owner = client.headers['X-Session-ID']
    token = client.post('/reservation/draft', json=payload).json()['token']
    client.headers['X-Session-ID'] = str(uuid4())
    assert client.get('/reservation/pending').json()['pending'] is None
    assert client.post('/reservation/confirm', json={'token': token}).status_code == 409
    assert client.get('/chat/history').json()['messages'] == []
    client.headers['X-Session-ID'] = owner
    client.post('/reservation/confirm', json={'token': token})
    client.headers['X-Session-ID'] = str(uuid4())
    assert client.get('/reservation/list').json()['count'] == 0


@pytest.mark.parametrize('changes', [
    {'num_people': 0}, {'num_people': 21}, {'num_children': 4}, {'num_children': -1},
    {'arrival_time': '2023-01-01 18:00'}, {'arrival_time': '9999-99-99 99'},
    {'arrival_time': (datetime.now(SHANGHAI) + timedelta(days=2)).replace(hour=3).isoformat()},
    {'seat_preference': '  '}, {'main_dish_preference': ''}, {'other_comments': ''},
])
def test_reservation_rejects_invalid_data(client, payload, changes):
    assert client.post('/reservation/draft', json=payload | changes).status_code == 422
    assert client.get('/reservation/list').json()['total'] == 0


def test_missing_field_is_not_silently_filled(client, payload):
    del payload['other_comments']
    assert client.post('/reservation/draft', json=payload).status_code == 422


def test_recommendation_constraints(client):
    rows = client.get('/menu/recommend', params={'query': '素食，清淡不辣，花生过敏'}).json()['items']
    assert rows and all(row['is_vegetarian'] and row['spice_level'] == 0 for row in rows)
    assert not any('花生' in row['allergens'] for row in rows)
    soy = client.get('/menu/recommend', params={'query': '大豆过敏'}).json()['items']
    assert not any('豆腐' in row['main_ingredients'] for row in soy)


def test_bad_session_rejected(client):
    client.headers['X-Session-ID'] = '123'
    assert client.get('/reservation/list').status_code == 400


def test_api_prefix_matches_public_routes(client):
    assert client.get('/api/menu/list').json() == client.get('/menu/list').json()


def test_expired_draft_is_not_shown_or_confirmed(client, payload):
    from sqlalchemy import update
    from agent.database import ReservationDraft, local_now
    token = client.post('/reservation/draft', json=payload).json()['token']
    with client.app.state.database.engine.begin() as conn:
        conn.execute(update(ReservationDraft).where(ReservationDraft.token == token).values(created_at=local_now() - timedelta(minutes=31)))
    assert client.get('/reservation/pending').json()['pending'] is None
    assert client.post('/reservation/confirm', json={'token': token}).status_code == 409


def test_friday_late_opening_and_weekday_closing(client, payload):
    now = datetime.now(SHANGHAI)
    friday = (now + timedelta(days=((4 - now.weekday()) % 7 or 7))).replace(hour=22, minute=0)
    monday = (now + timedelta(days=((0 - now.weekday()) % 7 or 7))).replace(hour=22, minute=0)
    assert client.post('/reservation/draft', json=payload | {'arrival_time': friday.isoformat()}).status_code == 200
    assert client.post('/reservation/draft', json=payload | {'arrival_time': monday.isoformat()}).status_code == 422


def test_vegetarian_negation_is_respected(client):
    rows = client.get('/menu/recommend', params={'query': '不想吃素食'}).json()['items']
    assert rows and not any(row['is_vegetarian'] for row in rows)
