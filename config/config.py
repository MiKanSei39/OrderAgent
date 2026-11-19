"""项目配置；不修改全局模型配置，不记录密钥。"""
from dataclasses import dataclass, field
from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / '.env', override=False)
load_dotenv(ROOT_DIR / '.env.local', override=True)


@dataclass
class Settings:
    database_url: str = field(default_factory=lambda: os.getenv('DATABASE_URL', ''))
    storage_backend: str = field(default_factory=lambda: os.getenv('STORAGE_BACKEND', 'mysql'))
    data_dir: Path = field(default_factory=lambda: Path(os.getenv('DATA_DIR', str(ROOT_DIR / 'data'))))
    llm_provider: str = field(default_factory=lambda: os.getenv('LLM_PROVIDER', 'poke'))
    llm_model: str = field(default_factory=lambda: os.getenv('LLM_MODEL', 'gpt-5.5'))
    llm_base_url: str = field(default_factory=lambda: os.getenv('POKE_BASE_URL', 'https://www.poke2api.com/v1'))
    llm_api_key: str = field(default_factory=lambda: os.getenv('POKE_API_KEY', ''))
    redis_url: str = field(default_factory=lambda: os.getenv('REDIS_URL', ''))
    faq_namespace: str = field(default_factory=lambda: os.getenv('FAQ_NAMESPACE', 'orderagent:faq'))
    milvus_uri: str = field(default_factory=lambda: os.getenv('MILVUS_URI', ''))
    milvus_token: str = field(default_factory=lambda: os.getenv('MILVUS_TOKEN', ''))
    milvus_collection: str = field(default_factory=lambda: os.getenv('MILVUS_COLLECTION', 'orderagent_menu'))
    embedding_model: str = field(default_factory=lambda: os.getenv('EMBEDDING_MODEL', str(ROOT_DIR / 'models' / 'bge-m3')))
    mcp_url: str = field(default_factory=lambda: os.getenv('AMAP_MCP_URL', ''))
    mcp_transport: str = field(default_factory=lambda: os.getenv('AMAP_MCP_TRANSPORT', 'sse'))
    mcp_token: str = field(default_factory=lambda: os.getenv('AMAP_MCP_TOKEN', ''))
    faq_threshold: float = field(default_factory=lambda: float(os.getenv('FAQ_THRESHOLD', '0.48')))
    host: str = field(default_factory=lambda: os.getenv('API_HOST', '127.0.0.1'))
    port: int = field(default_factory=lambda: int(os.getenv('API_PORT', '18088')))

    def __post_init__(self):
        self.data_dir = Path(self.data_dir).resolve()
        if self.llm_provider == 'openai':
            self.llm_base_url = os.getenv('OPENAI_BASE_URL', self.llm_base_url)
            self.llm_api_key = os.getenv('OPENAI_API_KEY', '')
        elif self.llm_provider == 'deepseek':
            self.llm_base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
            self.llm_api_key = os.getenv('DEEPSEEK_API_KEY', '')
        elif self.llm_provider not in ('poke', 'disabled'):
            raise ValueError('LLM_PROVIDER 仅支持 poke/openai/deepseek/disabled')
        self.llm_base_url = self.llm_base_url.rstrip('/')
        if not self.database_url:
            if self.storage_backend == 'sqlite':
                self.database_url = f'sqlite:///{(self.data_dir / "orderagent.db").as_posix()}'
            elif self.storage_backend == 'mysql':
                self.database_url = URL.create(
                    'mysql+pymysql', username=os.getenv('MYSQL_USER', os.getenv('USER', 'root')),
                    password=os.getenv('MYSQL_PASSWORD', os.getenv('PASSWORD', '')),
                    host=os.getenv('MYSQL_HOST', os.getenv('HOST', '127.0.0.1')),
                    port=int(os.getenv('MYSQL_PORT', os.getenv('PORT', '3306'))),
                    database=os.getenv('MYSQL_DATABASE', os.getenv('DATABASE', 'menu')),
                    query={'charset': 'utf8mb4'},
                )
            else:
                raise ValueError('STORAGE_BACKEND 仅支持 sqlite/mysql')


@lru_cache
def get_settings() -> Settings:
    return Settings()


MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', os.getenv('HOST', 'localhost')),
    'port': int(os.getenv('MYSQL_PORT', os.getenv('PORT', '3306'))),
    'user': os.getenv('MYSQL_USER', os.getenv('USER', 'root')),
    'password': os.getenv('MYSQL_PASSWORD', os.getenv('PASSWORD', '')),
    'database': os.getenv('MYSQL_DATABASE', os.getenv('DATABASE', 'menu')),
    'charset': os.getenv('CHARSET', 'utf8mb4'),
}
