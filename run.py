"""python run.py；也可使用 uv run python run.py。"""
import logging
import uvicorn
from config.config import Settings


def main():
    settings = Settings()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(name)s: %(message)s')
    logging.info('六合餐厅智能点餐系统：http://%s:%s，接口文档：/docs', settings.host, settings.port)
    uvicorn.run('api.main:app', host=settings.host, port=settings.port)


if __name__ == '__main__':
    main()
