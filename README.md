# 六合餐厅 · LangChain智能点餐系统

在原课程项目基础上补齐的可运行前后端应用。保留原菜单、MySQL表名、系统提示词和特色菜工具入口；真实调用Poke模型。

## 本机启动

1. 确保MySQL运行，密码继续使用你维护的原.env。
2. Podman Desktop启动podman-bbb；在项目根目录执行：

       powershell -ExecutionPolicy Bypass -File scripts/start_services.ps1 -IncludeRedis

3. 双击根目录start.bat，浏览器打开 **http://localhost:18088**。
4. 接口文档：http://localhost:18088/docs；状态：http://localhost:18088/health。

手动启动：

    uv sync
    cd ui
    npm ci
    npm run build
    cd ..
    uv run python run.py

前端开发：后端启动后在ui运行npm run dev或双击ui/start.bat，访问http://localhost:3000。Vite将/api代理到18088；更换后端端口时通过API_TARGET调整代理目标。

### 为什么不是8000？

本机Windows开发时将7994—8093列入Hyper-V/WSL TCP保留区间，8000报WinError 10013；9091也被保留。另外18000由用户留给酒馆，点餐项目不占用。因此本机配置使用API端口18088、Milvus健康端口19091。不要为了运行项目删除系统保留端口。

## 已实现功能

- **智能聊天**：LangChain create_agent、工具调用、FastAPI SSE流式输出，界面展示工具状态并支持停止接收。
- **菜单查询**：特色菜、菜系、荤素、辣度、关键词；参数校验、参数化SQL和分页。
- **口味推荐**：本地中文BGE + Milvus HNSW/COSINE语义检索；实时SQL过滤停售菜、辣度、素食和已知过敏原。
- **FAQ**：Redis存储、输入防抖建议、序列/Jaccard/包含关系评分与阈值过滤；固定答案不调用模型。
- **多轮预订**：追问缺项、生成草稿、修改、取消草稿、二次确认后写入订单。
- **预订安全**：上海时间、营业时间、儿童/总人数校验；草稿30分钟有效、旧令牌失效，重复确认不重复插单。
- **持久记忆**：LangGraph SQLite checkpoint存模型记忆；MySQL存聊天记录、草稿和订单；同一浏览器刷新或服务重启可继续。
- **前端**：Vue3/Vite，智能助手/菜单/我的预订三页，手机布局，Markdown净化渲染和错误状态提示。
- **高德MCP接入代码**：可配置自己的地址；未配置时不编造实时路线，初始化失败不影响其他功能。

## 配置与凭据

加载顺序：进程环境 + 原.env，再由项目专用.env.local覆盖。当前.env.local不保存密钥；MySQL密码继续从原.env加载。

| 配置 | 用途 |
| --- | --- |
| POKE_API_KEY | 当前从系统环境继承，不写前端或日志 |
| POKE_BASE_URL / LLM_MODEL | Poke的/v1地址与已实测可调用的gpt-5.5 |
| LLM_PROVIDER | poke、openai、deepseek、disabled；切换需显式配置 |
| HOST, PORT, USER, PASSWORD, DATABASE, CHARSET | 兼容原MySQL配置；也支持优先级更高的MYSQL_*变量 |
| STORAGE_BACKEND / DATABASE_URL | 默认MySQL；SQLite仅为显式演示选项，MySQL失败不会偷偷回退 |
| REDIS_URL / FAQ_NAMESPACE | 当前本机6379，独立命名空间orderagent:faq |
| MILVUS_URI / MILVUS_COLLECTION | 当前本机19530，独立集合orderagent_menu |
| EMBEDDING_MODEL | models/bge-small-zh-v1.5，本机实测512维，程序自动探测维度 |
| AMAP_MCP_URL / AMAP_MCP_TRANSPORT / AMAP_MCP_TOKEN | 可选高德MCP；不使用教程里不明归属的公共凭据 |
| API_HOST / API_PORT | 只监听本机；本机实际端口18088 |

原.env已经被原项目Git跟踪，新增.gitignore不会自动取消已有跟踪。**公开仓库前请检查历史凭据与Git索引。** 本次没有改动你的密码、全局模型服务商或Git索引。

未配置Redis/Milvus时明确使用本地FAQ和TF-IDF词法检索，页脚及/health显示实际模式；这不冒充向量语义检索。显式配置了服务但连接失败时启动报错，不静默掩盖故障。

## Podman与嵌入模型

scripts/start_services.ps1复用已有镜像/容器和etcd-data、minio-data、milvus-data卷，不删除数据。容器不继承宿主机localhost代理，避免Milvus连不上etcd。服务端口只映射到127.0.0.1。

- Milvus SDK：127.0.0.1:19530
- Milvus健康：http://127.0.0.1:19091/healthz
- MinIO控制台：http://127.0.0.1:9001（课程开发实例默认账号，不应暴露公网）
- Redis：127.0.0.1:6379

换电脑首次下载嵌入模型：

    uv run python scripts/download_embedding.py

启动仅加载本地模型，不自动下载多GB的bge-m3。若Podman虚拟机无法下载Redis，可通过Windows可用网络下载官方OCI归档（每个blob校验SHA256）再导入：

    uv run python scripts/download_redis_image.py
    podman --connection podman-bbb load -i data/redis-7.2-alpine.oci.tar
    powershell -File scripts/start_services.ps1 -IncludeRedis

## 数据初始化与同步

    uv run python -m agent.redis_data_sync
    uv run python -m agent.milvus_data_sync
    uv run python scripts/probe_services.py

启动只创建缺失表，**菜单表为空时**才导入原menu.sql的5道菜。已有MySQL菜单和订单不覆盖。无需再运行带DROP的原menu.sql。

Milvus按菜品ID进行upsert，重复同步不增加逻辑重复数据、不删除原集合；切换模型维度不符时明确报错，请换新集合名后再同步。

新增表：agent_reservation_draft、agent_chat_message；原menu_items和reservation_order结构保留。

## 接口

同时支持原课程路径和/api前缀。

| 接口 | 功能 |
| --- | --- |
| POST /chat | 接收query和可选session_id；SSE输出meta/token/tool/source/reservation_pending/reservation_created/error/done |
| GET /chat/history | 当前会话历史 |
| GET /faq/suggest?query=电话&limit=3 | FAQ建议；空白/无关输入返回空列表 |
| GET /menu/list | 菜单、筛选、分页 |
| GET /menu/recommend?query=清淡素食 | 推荐，包含真实检索模式 |
| POST /reservation/draft | 校验并生成草稿，不下单 |
| GET或DELETE /reservation/pending | 查看或取消当前草稿 |
| POST /reservation/confirm | 携带token确认，幂等入库 |
| GET /reservation/list?limit=20&offset=0 | 当前会话订单，返回count和total |
| GET /session、GET /health | 会话及真实运行状态 |

浏览器使用随机UUID4作为X-Session-ID，刷新保留，新建会话生成新ID；支持HttpOnly Cookie。订单不公开给其他会话。新会话不删除旧订单，尚无登录账号与跨设备找回功能。本项目用于课程/本地演示，公网部署还需认证、HTTPS、限流和数据保留策略。

## 验证

    uv run pytest -q
    cd ui
    npm test
    npx playwright test

测试用独立临时SQLite，不向用户MySQL写测试订单。浏览器测试使用系统Edge和18001端口，覆盖桌面/手机、FAQ流式聊天、筛选、二次确认及刷新恢复。

真实Poke多轮联调（会消耗API额度，使用临时业务数据库）：

    uv run python scripts/live_smoke.py

验证工具调用、3人改4人、旧令牌拒绝、确认前零订单、确认后唯一订单、业务/checkpoint持久化。

## 教程示例修正

- 保留原config目录和.md提示词路径，不强迫改成示例目录名。
- 原特色菜工具端口转整数，修复多余SQL反引号，过滤不可供应菜品。
- FAQ示例电话与原提示词冲突时以021-12345678为准；折扣标注为课程活动，停车等未知信息不捏造。
- 麻婆豆腐含牛肉，不算素菜；空过敏原记录不代表绝对安全。
- 不照抄过期预订日期、固定全局会话123、虚假成功信息或每次DROP集合的逻辑。

要求原文day13-LangChain项目-点餐系统.md保留未改。
