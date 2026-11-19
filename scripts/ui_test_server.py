"""浏览器验收的独立服务：只写data/ui-test，不动用户MySQL。"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import uvicorn
from api.main import create_app
from config.config import ROOT_DIR, Settings

path = ROOT_DIR / 'data/ui-test'
path.mkdir(parents=True, exist_ok=True)
settings = Settings(database_url=f'sqlite:///{(path / "test.db").as_posix()}', data_dir=path, llm_provider='disabled', llm_api_key='', milvus_uri='', redis_url='', mcp_url='')
uvicorn.run(create_app(settings), host='127.0.0.1', port=18001)
