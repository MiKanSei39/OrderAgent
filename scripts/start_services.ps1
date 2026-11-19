param([string]$Connection = 'podman-bbb', [switch]$IncludeRedis)
$ErrorActionPreference = 'Stop'
$podmanExe = (Get-Command podman.exe).Source

function Invoke-Podman {
    param([string[]]$Arguments)
    & $podmanExe --connection $Connection @Arguments
    if ($LASTEXITCODE -ne 0) { throw ('Podman命令失败：' + $Arguments[0]) }
}

function Ensure-Container {
    param([string]$Name, [string[]]$CreateArguments)
    & $podmanExe --connection $Connection container exists $Name
    if ($LASTEXITCODE -eq 0) {
        $info = (& $podmanExe --connection $Connection inspect $Name | ConvertFrom-Json)[0]
        $hasProxy = @($info.Config.Env | Where-Object { $_ -match '^(HTTP_PROXY|HTTPS_PROXY|ALL_PROXY|http_proxy|https_proxy|all_proxy)=.+' }).Count -gt 0
        if ($hasProxy) {
            # 原地修正环境，不删除容器、镜像或卷；需重启一次生效。
            Invoke-Podman -Arguments @('update','--env','HTTP_PROXY=','--env','HTTPS_PROXY=','--env','ALL_PROXY=','--env','http_proxy=','--env','https_proxy=','--env','all_proxy=','--env','NO_PROXY=*','--env','no_proxy=*',$Name)
            Invoke-Podman -Arguments @('restart',$Name)
        } elseif (-not $info.State.Running) {
            Invoke-Podman -Arguments @('start',$Name)
        }
    } else {
        Invoke-Podman -Arguments $CreateArguments
    }
}

& $podmanExe --connection $Connection network exists milvus-net
if ($LASTEXITCODE -ne 0) { Invoke-Podman -Arguments @('network','create','milvus-net') }

Ensure-Container -Name 'etcd' -CreateArguments @('run','-d','--name','etcd','--network','milvus-net','--cgroups=disabled','--http-proxy=false','--restart=unless-stopped','-v','etcd-data:/etcd','quay.io/coreos/etcd:v3.5.18','etcd','-advertise-client-urls=http://127.0.0.1:2379','-listen-client-urls','http://0.0.0.0:2379','--data-dir','/etcd')
Ensure-Container -Name 'minio' -CreateArguments @('run','-d','--name','minio','--network','milvus-net','--cgroups=disabled','--http-proxy=false','--restart=unless-stopped','-e','MINIO_ROOT_USER=minioadmin','-e','MINIO_ROOT_PASSWORD=minioadmin','-v','minio-data:/bitnami/minio/data','-p','127.0.0.1:9001:9001','docker.io/bitnamilegacy/minio:2024.3.15')
Ensure-Container -Name 'milvus' -CreateArguments @('run','-d','--name','milvus','--network','milvus-net','--cgroups=disabled','--http-proxy=false','--restart=unless-stopped','-e','ETCD_ENDPOINTS=etcd:2379','-e','MINIO_ADDRESS=minio:9000','-e','NO_PROXY=*','-e','no_proxy=*','-v','milvus-data:/var/lib/milvus','-p','127.0.0.1:19530:19530','-p','127.0.0.1:19091:9091','docker.io/milvusdb/milvus:v2.6.7','milvus','run','standalone')

if ($IncludeRedis) {
    Ensure-Container -Name 'orderagent-redis' -CreateArguments @('run','-d','--name','orderagent-redis','--network','milvus-net','--cgroups=disabled','--http-proxy=false','--restart=unless-stopped','-p','127.0.0.1:6379:6379','-v','orderagent-redis-data:/data','docker.io/library/redis:7.2-alpine','redis-server','--appendonly','yes')
}

Write-Output '容器已启动，Milvus仍需等待健康检查。SDK: 127.0.0.1:19530；健康检查: http://127.0.0.1:19091/healthz'
Invoke-Podman -Arguments @('ps','--format','{{.Names}} {{.Status}} {{.Ports}}')
