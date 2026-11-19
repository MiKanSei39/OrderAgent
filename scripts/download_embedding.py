"""下载可信的BAAI中文小型嵌入模型到项目目录，不下载课程的多GB bge-m3。"""
import argparse
from pathlib import Path

from huggingface_hub import snapshot_download


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', default='https://huggingface.co')
    parser.add_argument('--model', default='BAAI/bge-small-zh-v1.5')
    parser.add_argument('--output', default=str(Path(__file__).resolve().parents[1] / 'models' / 'bge-small-zh-v1.5'))
    args = parser.parse_args()
    path = snapshot_download(repo_id=args.model, local_dir=args.output, endpoint=args.endpoint, allow_patterns=['*.json', '*.safetensors', '*.txt', '1_Pooling/*'], max_workers=4)
    print('嵌入模型已下载到：', path)


if __name__ == '__main__':
    main()
