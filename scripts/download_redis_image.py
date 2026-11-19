"""通过Windows可用网络下载官方Redis镜像的OCI归档，逐blob校验SHA256。

仅在Podman虚拟机无法访问镜像仓库时使用；不会改全局代理或仓库配置。
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
import tarfile

import httpx

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = 'https://registry-1.docker.io/v2/library/redis'
ACCEPT = ', '.join(['application/vnd.oci.image.index.v1+json', 'application/vnd.docker.distribution.manifest.list.v2+json', 'application/vnd.oci.image.manifest.v1+json', 'application/vnd.docker.distribution.manifest.v2+json'])


def main():
    with httpx.Client(timeout=90, follow_redirects=True) as client:
        auth = client.get('https://auth.docker.io/token', params={'service': 'registry.docker.io', 'scope': 'repository:library/redis:pull'})
        auth.raise_for_status()
        headers = {'Authorization': 'Bearer ' + auth.json()['token'], 'Accept': ACCEPT}
        response = client.get(REGISTRY + '/manifests/7.2-alpine', headers=headers)
        response.raise_for_status()
        index = response.json()
        if 'manifests' in index:
            platform = next(item for item in index['manifests'] if item.get('platform', {}).get('os') == 'linux' and item.get('platform', {}).get('architecture') == 'amd64')
            response = client.get(REGISTRY + '/manifests/' + platform['digest'], headers=headers)
            response.raise_for_status()
            assert 'sha256:' + hashlib.sha256(response.content).hexdigest() == platform['digest']
        manifest_bytes = response.content
        manifest = response.json()
        manifest_digest = hashlib.sha256(manifest_bytes).hexdigest()
        descriptors = [manifest['config'], *manifest['layers']]

        def download(descriptor):
            digest = descriptor['digest']
            result = client.get(REGISTRY + '/blobs/' + digest, headers={'Authorization': headers['Authorization']})
            result.raise_for_status()
            assert 'sha256:' + hashlib.sha256(result.content).hexdigest() == digest, '镜像blob校验失败'
            print('已校验blob', digest[:19], len(result.content), 'bytes', flush=True)
            return 'blobs/sha256/' + digest.split(':')[1], result.content

        with ThreadPoolExecutor(max_workers=4) as pool:
            blobs = list(pool.map(download, descriptors))
        archive_index = {'schemaVersion': 2, 'manifests': [{'mediaType': manifest.get('mediaType', 'application/vnd.oci.image.manifest.v1+json'), 'digest': 'sha256:' + manifest_digest, 'size': len(manifest_bytes), 'annotations': {'org.opencontainers.image.ref.name': 'docker.io/library/redis:7.2-alpine'}}]}
        output = ROOT / 'data/redis-7.2-alpine.oci.tar'
        output.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(output, 'w') as archive:
            entries = [('oci-layout', b'{"imageLayoutVersion":"1.0.0"}'), ('index.json', json.dumps(archive_index).encode()), ('blobs/sha256/' + manifest_digest, manifest_bytes), *blobs]
            for name, content in entries:
                entry = tarfile.TarInfo(name)
                entry.size = len(content)
                archive.addfile(entry, io.BytesIO(content))
        print('官方Redis OCI镜像已保存：', output, flush=True)


if __name__ == '__main__':
    main()
