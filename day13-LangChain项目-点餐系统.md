# LangChain项目-点餐系统

> LangChain项目资料
> 链接: https://pan.baidu.com/s/1G8lTev4xMiEoXyiR2Ycf7g 提取码: gtb5 

##  一、项目介绍

### 1.1 项目说明

本项目使用`langchain`构建一个智能点餐`Agent`，该`Agent`为用户解决如下问题：

- 基于FAQ回答常见/静态问题；

- 基于用户口味进行菜品推荐；

### 1.2 项目结构

本项目代码结构如下：

```
├── [.venv] 							# 虚拟环境
├── [agent] 							# agent构建代码目录
│  		├── langchain_assistant.py 		# 构建agent主代码文件
│  		├── milvus_data_sync.py  		# milvus数据同步代码文件
│  		├── [prompt] 
│  		│    	├── system_prompt.txt 
│  		├── redis_data_sync.py  	    # redis数据同步代码文件
├── [api]  							 	 # 定义api接口代码目录
│  		├── main.py  					# 项目所有接口定义目录
├── [models] 						 	# 嵌入模型目录
├── [ui] 							 	# 前端代码目录
├── [configs]  							
│  		├── config.py  					# 定义项目需要的配置常量
├── .env   							 	# 项目依赖的环境变量
├── .gitignore  					 	# git忽略文件
├── menu.sql   
├── pyproject.toml  				 	# 项目元数据和依赖声明
├── run.py  						 	# 后端服务执行入口
├── uv.lock 						 	# uv虚拟环境依赖锁文件
```

### 1.3 前端启动入口

前端启动前，需要保证在Windows当中已安装了Node.js运行环境。**npm 是 Node.js 的包管理器** - npm (Node Package Manager) 随 Node.js 一起安装。在课程资料目录下面，已经提供了`.msi`安装文件。双击下载的` .msi `文件，按照向导完成安装。

安装完成后，通过如下命令能够正常查看版本号，即安装完成。

```bash
node --version
npm --version
```

安装完成后，进入到前端ui目录下面，通过如下命令，即可启动前端脚本：

```bash
start.bat
```

启动后，如下输出即表示启动成功：

```
========================================
   点餐系统 - 前端启动
========================================

正在检查Node.js环境...
✅ Node.js环境正常

正在检查依赖包...
✅ 依赖包已存在

🚀 正在启动开发服务器...
📝 前端地址: http://localhost:3000
📝 确保后端API运行在: http://localhost:8000

按 Ctrl+C 停止服务
========================================

> aimenu-frontend@1.0.0 dev
> vite
```

### 1.4 **后端启动入口**

在项目根目录下面，通过以下命令启动：

```bash
python run.py
```

 启动后，如下输出即表示后端启动成功：

```
(.venv) OrderAgent> python .\run.py
INFO:__main__:🍽️ 点餐系统 v1.0
INFO:__main__:==================================================
INFO:__main__:✅ 环境配置检查通过
INFO:__main__:🚀 正在启动API服务...
INFO:__main__:📍 服务地址: http://localhost:8000
INFO:__main__:📖 API文档: http://localhost:8000/docs
INFO:__main__:==================================================
INFO:     Started server process [13812]
INFO:     Started server process [13812]
INFO:     Waiting for application startup.
INFO:sentence_transformers.SentenceTransformer:Use pytorch device_name: cpu
INFO:sentence_transformers.SentenceTransformer:Load pretrained SentenceTransformer: D:\OrderAgent\models\bge-m3
Loading weights: 100%|█| 391/391 [00:00<00:00, 6527.44it/s, Materializing param=pooler 
INFO:api.main:startup 初始化完成
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## 二、基础配置

### 2.1 虚拟环境配置

本项目中虚拟环境使用`UV`进行管理。`uv`是一个用 Rust 编写的极快的 Python 包和项目管理器，使用`uv`安装相关包时，非常方便、快速。另外，`uv`在依赖解析方面会比`pip`更加先进。`uv`官网地址：https://docs.astral.sh/uv/。 

![image-20260412125137638](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260412125137638.png)

在`Windows`当中安装`uv`的命令如下：

```shell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

安装好`uv`之后，就可以使用`uv`来创建并管理`python`依赖。

创建项目目录，并且创建虚拟环境，步骤如下：

**1）创建基解释器环境：**

创建项目空目录，并且`cd`到空目录中，使用如下命令创建一个`python`版本为`3.12`的虚拟环境:

```bash
uv venv --python 3.12
```

**2）初始化项目：**

通过`uv init` 会创建`pyproject.yaml`文件

```bash
uv init
```

**3）安装依赖：**

通过`uv add`方式所安装的依赖，会记录在`pyproject.yaml`和`uv.lock`文件中。

```bash
uv add langchain
uv add langchain-openai
uv add langchain-huggingface
uv add python-dotenv
uv add pymysql
uv add pymilvus
uv add torch
uv add sentence-transformers
uv add sqlalchemy
uv add langchain_mcp_adapters
uv add fastapi
uv add redis
```

其中`pyproject.yaml`内容如下：

```yaml
[project]
name = "orderagent"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.136.0",
    "langchain>=1.2.15",
    "langchain-huggingface>=1.2.1",
    "langchain-mcp-adapters>=0.2.2",
    "langchain-openai>=1.1.12",
    "pymilvus>=2.6.12",
    "pymysql>=1.1.2",
    "python-dotenv>=1.2.2",
    "redis>=7.4.0",
    "sentence-transformers>=5.4.0",
    "sqlalchemy>=2.0.49",
]
```

### 2.2 版本控制

在项目根目录下，配置`git`：

```bash
git init
```

### 2.3 **环境变量管理**

本项目中所有环境变量，通过`.env`文件管理，在项目启动时，通过`load_dotenv`来加载环境变量。项目中通过环境变量管理如下配置：

- `LLM`相关配置：`base_url`, `api_key`等；
- `LangSmith`相关配置。

### 2.4 数据库表结构

项目所包含的数据表包含如下两项：

- `menu_items`：包含餐厅中所包含的所有菜品以及特色菜品相关信息

- `reservation_order`: 创建，查看预订单

登录mysql数据库并建表：

```bash
mysql --default-character-set=utf8mb4 -uroot -p
```

具体表结构如下所示：

```mysql
CREATE DATABASE menu CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

```mysql
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
USE `menu`;
-- ----------------------------
-- Table structure for menu_items
-- ----------------------------
DROP TABLE IF EXISTS `menu_items`;
CREATE TABLE `menu_items`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '菜品ID，主键自增',
  `dish_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '菜品名称',
  `price` decimal(8, 2) NOT NULL COMMENT '价格（元）',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '菜品描述',
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '菜品分类',
  `spice_level` tinyint NULL DEFAULT 0 COMMENT '辣度等级：0-不辣，1-微辣，2-中辣，3-重辣',
  `flavor` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '口味特点',
  `main_ingredients` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '主要食材，多个食材用逗号分隔',
  `cooking_method` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '烹饪方法',
  `is_vegetarian` tinyint(1) NULL DEFAULT 0 COMMENT '是否素食：0-否，1-是',
  `allergens` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '过敏原信息，多个过敏原用逗号分隔',
  `is_available` tinyint(1) NULL DEFAULT 1 COMMENT '是否可供应：0-不可用，1-可用',
  `is_featured` tinyint(1) NULL DEFAULT 0 COMMENT '是否特色主菜：0-否，1-是',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_category`(`category`) USING BTREE,
  INDEX `idx_is_available`(`is_available`) USING BTREE,
  INDEX `idx_is_vegetarian`(`is_vegetarian`) USING BTREE,
  INDEX `idx_price`(`price`) USING BTREE,
  INDEX `idx_spice_level`(`spice_level`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '菜单表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of menu_items
-- ----------------------------
INSERT INTO `menu_items` VALUES (1, '宫保鸡丁', 28.00, '经典川菜，鸡肉丁配花生米，酸甜微辣，口感丰富', '川菜', 2, '酸甜微辣', '鸡胸肉,花生米,青椒,红椒,葱段', '爆炒', 0, '花生,可能含有麸质', 1,1,now(),now());
INSERT INTO `menu_items` VALUES (2, '麻婆豆腐', 18.00, '四川传统名菜，嫩滑豆腐配麻辣汤汁，下饭神器', '川菜', 3, '麻辣鲜香', '嫩豆腐,牛肉末,豆瓣酱,花椒', '烧炒', 0, '大豆,可能含有麸质', 1, 0,now(),now());
INSERT INTO `menu_items` VALUES (3, '清炒时蔬', 15.00, '新鲜时令蔬菜清炒，营养健康，口感清爽', '素食', 0, '清淡爽口', '时令蔬菜,蒜蓉', '清炒', 1, '', 1, 1,now(),now());
INSERT INTO `menu_items` VALUES (4, '红烧鲈鱼', 45.00, '新鲜鲈鱼红烧制作，肉质鲜美，营养丰富', '鲁菜', 1, '咸鲜微甜', '鲈鱼,生抽,老抽,冰糖,葱姜', '红烧', 0, '鱼类', 1, 1,now(),now());
INSERT INTO `menu_items` VALUES (5, '蒜蓉西兰花', 12.00, '新鲜西兰花配蒜蓉，营养丰富，适合减肥人群', '素食', 0, '蒜香清淡', '西兰花,大蒜,橄榄油', '蒸炒', 1, '无过敏源', 1,0,now(),now());

drop table IF EXISTS reservation_order;
CREATE TABLE reservation_order(
  id int AUTO_INCREMENT COMMENT '预订单ID，主键自增',
  num_people int NOT NULL COMMENT '客人人数',
  num_children int NOT NULL COMMENT '儿童人数',
  arrival_time datetime NOT NULL COMMENT '到达时间',
  seat_preference varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '座位偏好',
  main_dish_preference varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '主菜偏好',
  other_comments text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '其他备注需求',
  created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '预订单表' ROW_FORMAT = Dynamic;
```

## 三、核心智能体构建

`Agent `构建所包含的内容如下：

- 系统提示词：定义`Agent`的角色及任务；定义权责边界，

- 工具定义：基于`Agent`设计内容，定义相关工具，包含详细的工具功能描述，入参描述，出参描述等。

- 记忆模块：基于数据库实现`Agent`的短期记忆。

### 3.1 提示词构建

在项目根目录下创建一个目录`agent`并在该目录下创建一个子目录`prompt`，并创建文件`system_prompt.txt`文件用来存放提示词。

`Prompt`提示词基于实际业务场景对`Agent`所需要完成的任务来编写，如下所示：

```markdown
# 基本信息
## 角色
你是一个餐厅智能助手，你需要根据用户的输入，来进行回答，或者完成预订任务。

## 能力
### 回答相关问题
当用户仅询问一些餐厅的基础问题时，需要根据已有的信息和相关工具来进行回答
**只能回答与餐厅相关的问题，不能回答与其他主题相关的问题。另外，在进行回答时，不可捏造任何信息。**

### 完成预订任务
当用户明确表示需要预订时，需要在客人所提供的信息基础上，进行预订，如果用户有相关信息没有提供，需要主动向用户询问，
要完成一个预订，所需要包含的信息如下所示：
1. 客人人数
2. 到达时间
3. 座位偏好
4. 主菜偏好
5. 其他备注需求

获取到所有相关信息之后，需要和用户进行二次确认，确认完成之后，才能够进行下单，如果用户需要更改相关信息，需满足用户需求，及时进行修改调整

## 注意事项：
1. 工具仅在需要时才调用，不需要时，不能随意调用工具，否则因为调用工具导致的延迟，会影响用户体验。
2. 在进行回答时，不可捏造任何信息。
3. 在回复时，应该注意不要重复前面所说过的内容，避免用户产生疑惑，要保存逻辑连贯

## 其他相关信息：
餐厅相关信息如下：
1. 位置：上海黄浦区人民广场六合大厦
2. 名字：六合餐厅
3. 大堂电话：021-12345678
4. 营业时间：周日至周四：早10点至晚21点，周五周六：早10点至晚23点
```

这一段 `Prompt `的实现逻辑：

- 用“角色 + 能力 + 约束 + 餐厅事实”把 `Agent `行为框定在“餐厅场景”内，降低幻觉风险。

- 预订任务通过列出必要字段，促使` Agent` 缺字段就追问、齐字段就二次确认再执行工具。

### 3.2 定义智能体

在项目根目录下创建一个`.env`文件用来存放模型需要的`KEY`：

```
DEEPSEEK_MODEL=deepseek-v4-pro
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_KEY=sk-******
```

并在当前`agent`目录下创建一个`langchain_assistant.py`文件，定义智能体如下：

```python
import os
import asyncio
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
from langchain.messages import AnyMessage, HumanMessage, AIMessage, ToolMessage, ToolCall
from pathlib import Path

load_dotenv()

ROOT = Path(__file__).parent.parent
MODEL = os.getenv("DEEPSEEK_MODEL")
AGENT = None

with open(ROOT / "agent/prompt/system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


async def get_agent():
    global AGENT
    if AGENT is None:
        # 初始化模型
        model = init_chat_model(model=MODEL)
        # 设置工具
        all_tools = []
        # 设置checkpointer
        checkpointer = InMemorySaver()
        # 创建agent
        AGENT = create_agent(
            model=model,
            tools=all_tools,
            checkpointer=checkpointer,
            system_prompt=SYSTEM_PROMPT
        )
    return AGENT

async def test_agent():
    # 调用agent
    agent = await get_agent()
    # 定义配置信息
    config = {"configurable": {"thread_id": "123"}}
    # 用户输入
    query = "你能为我做什么？"
    response = await agent.ainvoke(
        {"messages": [HumanMessage(query)]},
        config=config
    )
    print("="*100)
    print(">>> Human: ", query)
    print(">>> Assistant: ", response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(test_agent())
```

### 3.3 业务功能实现

主要实现特色菜的查询和根据口味推荐菜品，这里主要使用工具来实现。需要专门在`agent`下创建`tools`文件夹，并新建`utils.py`脚本存放项目常用函数和工具。

创建`configs`目录并在该目录下创建`config.yaml`文件，定义配置信息如下：

```python
mysql:
  host: localhost
  user: root
  port: 3306
  password: "123456"
  database: "menu"
  charset: utf8mb4

milvus:
  uri: "http://localhost:19530"
  token: ""
  collection_name: "menu_items"

redis:
  host: "localhost"
  port: 6379
  password: ""
  db: 0
  faq_redis_namespace: "faq"
```

创建`config_loader.py`文件，加载、校验以上配置信息：

```python
from pathlib import Path
from typing import Dict, Any
import yaml

CONFIG_DIR = Path(__file__).parent
CONFIG_PATH = CONFIG_DIR / "config.yaml"
REQUIRE_KEYS = {
    "mysql": {"host", "port", "user", "password", "database", "charset"},
    "milvus": {"uri", "token", "collection_name"},
    "redis": {"host", "port", "password", "db", "faq_redis_namespace"}
}


def load_yml_config(path: Path) -> Dict[str, Any]:
    """加载yaml文件"""
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, Dict):
        raise ValueError(f"配置文件 {path} 格式错误")
    return data


def require_section(data: Dict[str, Any], section: str) -> Dict[str, Any]:
    """一级 section 校验"""
    section_data = data.get(section)
    if not isinstance(section_data, Dict):
        raise ValueError(f"{section} 缺少配置，或者配置格式错误")
    return section_data


def require_keys(section_data: Dict[str, Any], section: str) -> Dict[str, Any]:
    """二级 key 校验"""
    missing_keys = [key for key in REQUIRE_KEYS[section] if key not in section_data]
    if missing_keys:
        raise ValueError(f"{section} 缺少相关 key: {missing_keys}")
    return section_data


def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileExistsError(f"配置文件不存在: {CONFIG_PATH}")

    data = load_yml_config(CONFIG_PATH)

    config = {}
    for section in REQUIRE_KEYS:
        section_data = require_section(data, section)
        config[section] = require_keys(section_data, section)  # 返回section_data
    return config


APP_CONFIG = load_config()
MYSQL_CONFIG = APP_CONFIG["mysql"]
MILVUS_CONFIG = {
    "uri": APP_CONFIG["milvus"]["uri"],
    "token": APP_CONFIG["milvus"]["token"]
}
MILVUS_COLLECTION_NAME = APP_CONFIG["milvus"]["collection_name"]
REDIS_CONFIG = APP_CONFIG["redis"]
```

#### 3.3.1 特色菜品工具定义

在`utils.py`中定义`search_menu`工具。用于从 MySQL 当中读取相关数据，该工具依赖LLM提供入参，并在sql中通过`limit`限定查询数据量：

```python
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
from pathlib import Path
from decimal import Decimal
from langchain.tools import tool
from configs.config_loader import MYSQL_CONFIG

@tool
def search_menu(
    max_spice_level: int = None,  # -10，5000000
    is_featured: bool = None,
    is_vegetarian: bool = None,
    # keyword: str = None,
    category: str = None,
    limit: int = 5
):
    """
    按明确结构化条件查询菜品，适合查询特色菜、素食、辣度、菜品分类相关的问题。
    不能用于根据口味、风味、食材偏好、饮食偏好或身体状态推荐菜品。
    """
    # 默认条件：菜品必须可供应
    where = ["is_available = %s"]
    params = [1]

    # 追加特色菜品查询条件
    if is_featured is not None:
        where.append("is_featured = %s")
        params.append(1 if is_featured else 0)
    
    # 追加菜品辣度等级条件
    if max_spice_level is not None:
        # 裁剪，收敛辣度区间，以适配业务要求
        max_spice_level = max(0, min(max_spice_level, 3))
        where.append("spice_level <= %s")
        params.append(max_spice_level)

    # # 追加关键字模糊匹配条件
    # if keyword:
    #     keyword_pattern = f"%{keyword.strip()}%"
    #     where.append(
    #         "(dish_name like %s or description like %s or flavor like %s or main_ingredients like %s)"
    #     )
    #     params.extend([keyword_pattern, keyword_pattern, keyword_pattern, keyword_pattern])
    
    # 追加菜系条件
    if category:
        where.append("category = %s")
        params.append(category.strip())

    # 追加荤素条件
    if is_vegetarian:
        where.append("is_vegetarian = %s")
        params.append(1 if is_vegetarian else 0)
    
    limit = max(1, min(limit, 20))
    params.append(limit)  # 由LLM传入

    with pymysql.connect(**MYSQL_CONFIG) as conn:  # 硬编码不可取
        with conn.cursor(DictCursor) as cursor:
            sql = """
                select 
                    dish_name as 主菜名称,
                    price as 价格,
                    description as 描述,
                    category as 分类,
                    spice_level as 辣度等级,
                    flavor as 口味,
                    main_ingredients as 主要食材,
                    cooking_method as 烹饪方法,
                    is_vegetarian as 是否为素食,
                    allergens as 过敏信息
                from 
                    menu_items
                where
                    {where_sql}
                order by
                    is_featured desc, price asc
                limit %s
            """
            cursor.execute(sql.format(where_sql=" and ".join(where)), params)
            results = cursor.fetchall()

            return [
                {
                    key: float(value) if isinstance(value, Decimal) else value
                    for key, value in res.items()
                }
                for res in results
            ]
```

测试该工具

```python
if __name__ == "__main__":
    #import asyncio
    #asyncio.run(test_agent())
    result = search_main_dishes() #单独测试该工具，需要将该方法前的@tool注释掉才能调用该方法
    print(result)
```

**注意：**

须用模块指令执行测试：

```bash
cd <项目根目录路径: .../OrderAgent>
python -m agent.tools.utils
```

执行结果显示如下：

```
[{'主菜名称': '宫保鸡丁', '价格': Decimal('28.00'), '描述': '经典川菜，鸡肉丁配花生米，酸甜微辣，口感丰富', '分类': '川菜', ' 辣度等级': 2, '口味': '酸甜微辣', '主要食材': '鸡胸肉,花生米,青椒,红椒,葱段', '烹饪方法': '爆炒', '是否为素食': 0, '过敏信息': '花生,可能含有麸 质'}, {'主菜名称': '清炒时蔬', '价格': Decimal('15.00'), '描述': '新鲜时令蔬菜清炒，营养健康，口感清爽', '分类': '素食', ' 辣度等级': 0, '口味': '清淡爽口', '主要食材': '时令蔬菜,蒜蓉', '烹饪方法': '清炒', '是否为素食': 1, '过敏信息': ''}, {'主菜名称': '红烧鲈鱼', '价格': Decimal('45.00'), '描述': '新鲜鲈鱼红烧制作，肉质鲜美，营养丰富', '分类': '鲁菜', ' 辣度等级': 1, '口味': '咸鲜微甜', '主要食材': ' 鲈鱼,生抽,老抽,冰糖,葱姜', '烹饪方法': '红烧', '是否为素食': 0, '过敏信息': '鱼类'}]
```

**优化工具参数：**

工具入参由LLM决定，如果不做补充不加约束可能导致入参不合理，比如数值范围错误。可以用`args_schema`提升LLM对该工具参数的理解能力，首先在`tools`文件夹下新建`args_schema.py`用于定义各个工具的参数schema：

```python
from pydantic import BaseModel, Field

class SearchMenuToolArgsInfo(BaseModel):
    is_featured: bool | None = Field(
        default=None, 
        description="是否只查特色菜，用户明确询问特色菜时传True，没有提到则传None"
    )
    max_spice_level: int | None = Field(
        default=None, 
        ge=0, 
        le=3, 
        description="用户能接受的最高辣度，范围0-3，0表示不辣、1表示微辣、2表示中辣、3表示重辣，没有辣度要求时传None"
    )
    is_vegetarian: bool | None = Field(
        default=None, 
        description="是否只查询素食，用户明确询问素食时传True，没有提到则传None"
    )
    category: str | None = Field(
        default=None, 
        description="明确的菜品类别，例如：川菜、鲁菜、粤菜。如果没有明确类别要求时传None"
    )
    limit: int = Field(
        default=5, 
        ge=1, 
        le=20, 
        description="最多查询多少菜品数量，范围1-20，默认5"
    )
```

然后，将`SearchMenuToolArgsInfo`绑定到`utils.py`脚本中的`search_menu`工具上：

```python
from agent.tools.args_schema import SearchMenuToolArgsInfo

@tool(args_schema=SearchMenuToolArgsInfo)  # 添加相应的参数schema
def search_menu(
    max_spice_level: int = None,  # 不加约束，可能传入极端值 -10，5000000
    is_featured: bool = None,
    is_vegetarian: bool = None,
    category: str = None,
    limit: int = 5
):
    pass
```

定义好工具后，在`langchain_assistant.py`中将`search_menu`工具绑定到之前定义的 `get_agent` 函数中：

```python
...  # 省略其他导包
from agent.tools.utils import (
    search_menu,   # 后续还有其他工具会导入
)

...  # 省略中间代码

# 更新绑定工具到 agent
async def get_agent():
    global AGENT
    if AGENT is None:
        ...  					   # 省略
        all_tools = [search_menu]  # 设置工具
        AGENT = create_agent(
            tools=all_tools,       # 绑定工具
            ...
        )
    return AGENT
```

#### 3.3.2 Milvus 介绍和使用

##### 1、Milvus架构

Milvus因其强大的性能（可支持数百亿级别的向量存储和检索），以及可扩缩容等相关特点，在实际生产环境下，使用非常普遍。

Milvus的架构如下图所示：

![image-20260412202514337](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260412202514337.png)

Milvus 的组件解耦良好，其中三个最关键的任务 —— 搜索、数据插入以及索引 / 压缩 —— 被设计为易于并行化的进程，复杂逻辑被分离出来。这确保了相应的查询节点、数据节点和索引节点能够独立地进行纵向和横向扩展，从而优化性能和成本效率。

##### 2、Milvus Collection及数据类型

Milvus 通过 "`数据库` — `Collections` — `实体`" 的结构管理数据。Collections 和实体就类似关系型数据库中的表和记录。具体来说，Collection 是一个二维表，具有固定的列和变化的行。每列代表一个字段，每行代表一个实体。

![image-20260412202553415](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260412202553415.png)

Collection 通过 Collection Schema 来定义有哪些字段以及字段的类型、索引等。

以下是Milvus所支持的数据类型：

| 字段类型     |            | 字段                  | 描述                                                |
| ------------ | ---------- | --------------------- | --------------------------------------------------- |
| **向量字段** | 密集向量   | `FLOAT_VECTOR`        | 32位浮点数列表                                      |
|              |            | `FLOAT16_VECTOR`      | 16位半精度浮点数列表                                |
|              |            | `BFLOAT16_VECTOR`     | 16位浮点数列表，精度稍低，但指数范围与 Float32 相同 |
|              |            | `INT8_VECTOR`         | 8位有符号整数向量                                   |
|              | 稀疏向量   | `SPARSE_FLOAT_VECTOR` | 非零数字及其序列号列表                              |
|              | 二进制向量 | `BINARY_VECTOR`       | 一个0和1的列表                                      |
| **标量字段** |            | `VARCHAR`             | 字符串                                              |
|              |            | `BOOL`                | 存储true或false                                     |
|              |            | `INT`                 | INT8、INT16、INT32、INT64                           |
|              |            | `FLOAT`               | 32位浮点数                                          |
|              |            | `DOUBLE`              | 64位双精度浮点数                                    |
|              |            | `ARRAY`               | 相同数据类型元素的有序集合                          |
|              |            | `JSON`                | 结构化的键值数据                                    |

一个 Collection Schema 有一个主键、最多四个向量字段和若干标量字段。主键用于唯一标识一个实体，只接受 Int64 或 VarChar 值。插入实体时，默认情况下应包含主键值。但是，如果在创建 Collections 时启用了 AutoId，Milvus 将在插入数据时生成主键值，此时插入的实体中不应包含主键值。

向量字段是最重要的字段，可以分为稠密向量或者是稀疏向量。

**稠密向量**通常由基于 Transformer Encoder 架构的深度学习模型（如 Sentence-BERT）生成。

**稀疏向量**用于表示文本中的关键词及其对应权重，其构建方式经历了从早期基于 TF-IDF 等统计方法的传统词袋模型，到如今基于深度学习模型的学习式构建方法的发展演进。

使用深度学习模型构建稀疏向量的原理如下图所示（分词过程和稠密向量生成当中类似）：

![image-20260412202912284](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260412202912284.png)

通过深度学习模型生成一个稀疏向量时，不再“只看一句话的总体意思”，而是让模型推理：这句话里哪些词重要、重要到什么程度，并把这些重要词单独拎出来加权表示。

下面以 BGE-M3 为例，来展示稠密向量和稀疏向量的不同：

```python
# pip install FlagEmbedding==1.3.5
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel(model_name_or_path=r"D:\lessons\demo_class\LangChainDemo\models\bge-m3")

res = model.encode(["标量字段通常用来存储一些元数据，并可以在搜索时通过元数据进行过滤"],return_sparse=True,return_dense=True)
print('encode结果为：',res,end='\n\n')

# 1、打印稀疏向量
print('稀疏向量为：',res["lexical_weights"],end='\n\n')

# 2、将稀疏向量当中的id转换为token，并打印
sparse_vecs = model.convert_id_to_token(res["lexical_weights"])
print('稀疏向量转换为token后的结果为：',sparse_vecs,end='\n\n')

# 3、打印稠密向量
print('稠密向量为：',res["dense_vecs"],end='\n\n')
```

标量字段通常用来存储一些元数据，并可以在搜索时通过元数据进行过滤，以提高搜索结果的正确性。

##### 3、Mivus索引

索引是建立在数据之上的附加结构，可以加快搜索速度。不同字段数据类型适用不同的索引类型。

**1）稠密向量**

稠密向量可使用 `HNSW`（分层导航小世界）索引。

`HNSW`（分层导航小世界）是当下常用的一种基于图的索引算法，可以提高搜索高维浮点数向量时的性能。它具有出色的搜索精度和低延迟，但需要较高的内存开销来维护其分层图结构。该算法构建了一个多层图（类似不同缩放级别的地图），**底层**包含所有数据点，而**上层**则由从底层采样的数据点子集组成。在这种层次结构中，每一层都包含代表数据点的节点，节点之间由表示其接近程度的边连接。上层提供远距离跳转，以快速接近目标，而下层则进行细粒度搜索，以获得最准确的结果。其工作原理如下：

- **入口点**：搜索从顶层的一个固定入口点开始，该入口点是图中的一个预定节点。

- **贪婪搜索**：算法贪婪地移动到当前层的近邻，直到无法再接近查询向量为止。上层起到导航作用，作为粗过滤器，为下层的精细搜索找到潜在的入口点。

- **层层下降**：一旦当前层达到局部最小值，算法就会利用预先建立的连接跳转到下层，并重复贪婪搜索。

- **最后细化**：这一过程一直持续到最底层，在最底层进行最后的细化步骤，找出最近的邻居。

  <img src="https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260412203048459.png" alt="image-20260412203048459" style="zoom:67%;" />

  另外一种稠密向量所支持的索引类型是FLAT, FLAT 索引是用于对浮点向量进行索引和搜索的最简单、最直接的方法之一。它采用暴力搜索的方式，每个查询向量直接与数据集中的每个向量进行比较，无需任何高级的预处理或数据结构化操作。这种方法能保证准确性，提供 100% 的召回率，因为每一个潜在的匹配项都会被评估。

**2）稀疏向量**

`SPARSE_INVERTED_INDEX` 索引是 Milvus 用于高效存储和搜索稀疏向量的一种索引类型。这种索引类型利用倒排索引的原理，为稀疏数据创建高效的搜索结构。

以下是倒排索引示意图：

![image-20260412203133252](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260412203133252.png)

在实际查询时，先通过倒排索引查询到包含query当中token的文档有哪些，然后计算查询和各个文档之间的相似度分数。

在计算查询和文档之间的相似度分数时，有两种指标类型（metric type）:

- IP: 即 Inner Product 内积，例如查询所对应的稀疏向量为：{27:0.7, 100:0.4}，doc1 所对应的稀疏向量为：{27:0.5, 100:0.3, 5369:0.6}，则相似度分数为 similarity = (0.5×0.7) + (0.3×0.4) = 0.35 + 0.12 = 0.47
- BM25: 通过对 query 与文档中重合的词项进行加权求和，综合考虑词频（TF）、逆文档频率（IDF: 反映了一个词在全部文档当中的重要性，词出现的文档数量越少，IDF越高）以及文档长度归一化，从而计算二者的相关性得分。

##### 4、Milvus安装

Milvus 提供了多个版本以在不同场景下选择合适的使用方式：

- `Milvus Lite`：本地轻量化运行，通过 `pip install pymilvus[milvus-lite]` 即可安装。但 Milvus Lite 有一些限制，比如 Milvus Lite 仅支持 [FLAT](#FLAT) 索引类型。无论在 Collections 中指定了哪种索引类型，它都使用 FLAT 类型。另外，Milvus Lite仅支持在MacOs和Linux上面使用。
- `Milvus Standalone`：单点部署，支持通过 Docker 部署。
- `Milvus Distributed`：分布式部署，支持在 Kubernetes 集群上部署。

本项目使用 `Milvus Standalone` 方式部署，用以做代码演示。在课程资料当中提供了 `milvus` 的镜像包：`milvus_image.tar`。通过如下 `Docker `命令即可将其 `load` 到本地镜像仓库当中：

```bash
docker load -i milvus_image.tar
```

`load` 完成后，将课程资料当中提供了另外两个脚本：`standalone_embed.sh`，`standalone.bat`。

在虚拟机 `Linux` 环境下，先把前面的镜像加载到本地镜像仓库之后，再通过 `shell` 脚本即可启动 `Milvus` 服务，命令如下：

```bat
bash standalone_embed.sh start
```

在Windows当中使用 `Docker Desktop` 时，同样也是先把镜像加载到本地镜像仓库之后，通过命令 `docker load -i milvus_image.tar` 加载镜像

![image-20260412212013526](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260412212013526.png)

再通过bat脚本启动Milvus服务，命令如下：

```bat
standalone.bat start
```

启动完成后，可以通过 `Milvus` 官方所提供的图形化客户端工具 `Attu`，查看 `Milvus` 服务上的数据，安装包同样在课程资料当中，选择 `token`，直接连接即可，如下图所示：

![image-20260412213648238](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260412213648238.png)

##### 5、Milvus使用

> 注意：需要执行安装 `uv add sentence-transformers`

```python
#import torch
from pymilvus import MilvusClient, DataType
from langchain_huggingface import HuggingFaceEmbeddings

def get_client():
    return MilvusClient(uri="http://localhost:19530", token="")

def get_embeddings():
    """初始化 BGE-base-zh embeddings"""
    return HuggingFaceEmbeddings(
        model_name="./models/bge-base-zh",
        model_kwargs={
            #"device": "cuda" if torch.cuda.is_available() else "cpu",
            "device": "cpu",
            "trust_remote_code": True, 
        },
        encode_kwargs={
            "normalize_embeddings": True,  # 配合 COSINE 使用
            "batch_size": 32,
        },
    )

def insert_data():
    client = get_client()
    collection_name = "demo_collection"
    
    # 安全删除集合（开发环境）
    if client.has_collection(collection_name):
        client.drop_collection(collection_name)
    
    # 创建 Schema：dim=768
    schema = (MilvusClient.create_schema(auto_id=True)
        .add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        .add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=768) 
        .add_field(field_name="text", datatype=DataType.VARCHAR, max_length=2000)
    )
    
    # 索引：COSINE + HNSW
    index_params = MilvusClient.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="HNSW",
        metric_type="COSINE",  # 配合 normalize_embeddings
    )
    
    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        index_params=index_params
    )
    
    # 测试数据
    texts = [
        "这是一碗面条",
        "这是一碗米饭", 
        "这是一碗牛肉面",
        "这是一碗鸡汤面",
        "这是一碗素面"
    ]
    
    # 编码向量
    embeddings = get_embeddings()
    vector_list = embeddings.embed_documents(texts)  # List[List[float]], dim=768
    
    # 组装数据
    data_to_insert = [
        {"vector": vec, "text": txt} 
        for vec, txt in zip(vector_list, texts)
    ]
    
    # 插入
    res = client.insert(collection_name=collection_name, data=data_to_insert)
    print(f"插入成功: {res}")
    
def search_data(query: str):
    client = get_client()
    collection_name = "demo_collection"
    
    # 编码查询向量
    embeddings = get_embeddings()
    query_vector = embeddings.embed_query(query)  # List[float], dim=768
    
    # 搜索
    search_res = client.search(
        collection_name=collection_name,
        data=[query_vector],
        anns_field="vector",
        output_fields=["text"],
        limit=3
    )
    
    print(f"搜索结果: {search_res}")
    # 4、解析搜索结果
    if search_res:
        all_results = search_res[0]
        # all_results: 列表
        final_result = []

        for item in all_results:
            item_str = item["entity"]['text']
            final_result.append(item_str)
        
        return final_result
    else:
        return "在当前库里面没有找到和用户喜好相关的菜品"

if __name__ == "__main__":
    #insert_data()
    query = "我想吃牛肉面"
    search_results = search_data(query)
    print("最终搜索结果：", search_results)
```

> **注意：**
>
> - `get_client`、`get_embeddings`都可以采取单例复用的懒加载形式，同时`get_embeddings`中应使用**绝对路径**：
>
>     ```python
>     from pathlib import Path
>     from langchain_huggingface import HuggingFaceEmbeddings
>     from configs.config_loader import MILVUS_CONFIG
>     
>     ROOT = Path(__file__).parent.parent.parent
>     
>     def get_client():
>         global MILVUS_CLIENT
>         if MILVUS_CLIENT is None:
>             MILVUS_CLIENT = MilvusClient(**MILVUS_CONFIG)
>         return MILVUS_CLIENT
>     
>     def get_embedding():
>         global EMBEDDING
>         if EMBEDDING is None:
>             EMBEDDING = HuggingFaceEmbeddings(
>                 model_name=str(ROOT / "models/bge-base-zh"),
>                 model_kwargs={"device": "cpu"},
>                 encode_kwargs={"normalize_embeddings": True}
>             )
>         return EMBEDDING
>     ```
>
> - `get_client`、`get_embeddings`应作为常用函数迁移到`utils.py`脚本

#### 3.3.3 根据口味推荐菜品

该工具基于用户口味/菜品偏好，匹配相关菜品，用以进行菜品推荐。在实现上，先通过数据批处理脚本，将菜品相关数据同步至向量数据库中；其次，再在工具内部基于向量相似度进行语义搜索。

##### 1）数据同步批处理脚本：

在`agent`目录下创建同步脚本：`milvus_data_sync.py`

```python
"""
同步数据至Milvus当中去
"""
import pymysql
from pymysql.cursors import DictCursor
from pymilvus import DataType, IndexType
from pathlib import Path
from decimal import Decimal
from configs.config_loader import MYSQL_CONFIG, MILVUS_COLLECTION_NAME
from agent.tools.utils import get_client, get_embedding


def insert_data():
    """插入数据"""
    # ========== 获取/组装文档列表 ==========
    with pymysql.connect(**MYSQL_CONFIG) as conn:
        with conn.cursor(DictCursor) as cursor:
            sql = """
                select
                    dish_name as 主菜名称,
                    price as 价格,
                    description as 描述,
                    category as 菜品类别,
                    spice_level as 辣度等级,
                    flavor as 口味,
                    main_ingredients as 主要食材,
                    cooking_method as 烹饪方法,
                    is_vegetarian as 是否素食,
                    allergens as 过敏源,
                    is_featured as 是否特色菜
                from
                    menu_items
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            
            results_lst = []
            for res in results:
                string = ""
                for key, value in res.items():
                    if isinstance(value, Decimal):
                        value = float(value)
                    string += f"{key}: {value}\n"  # 组装各个字段的数据

                results_lst.append(string)  # 结合业务数据组装完成后的文档列表
            print(results_lst)
    # ========== 生成向量 ==========
    embedding = get_embedding()
    # list[list[float]]
    vector_list = embedding.embed_documents(results_lst)  # dim = 768
    print(vector_list)
    # ========== 向量入库 ==========
    # 连接 Milvus
    client = get_client()
    # 定义集合名
    collection_name = MILVUS_COLLECTION_NAME
    if client.has_collection(collection_name):
        client.drop_collection(collection_name)
    # 创建 Schema，定义 3 个字段
    schema = (MilvusClient.create_schema(auto_id=True) \
        .add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        .add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=768)  # 注意： 768维必须和你用的模型对应
        .add_field(field_name="text", datatype=DataType.VARCHAR, max_length=2000)  
    )
    # 创建索引
    index_params = MilvusClient.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="HNSW",
        metric_type="COSINE"
    )
    # 创建集合
    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        index_params=index_params
    )
    # 构造待入库的数据
    data: List[Dict] = [
        {"text": text, "vector": vector} 
        for text, vector in zip(results_lst, vector_list)
    ]
    # 数据入库
    result = client.insert(
        collection_name=collection_name,
        data=data
    )
    # 关闭连接
    client.close()
    print("向量数据入库成功", result)
    
    
def search_data(query: str):
    """检索数据"""
    # query向量化
    embedding = get_embedding()
    query_vector = embedding.embed_query(query)  # query: List[float]

    client = get_client()
    result = client.search(
        collection_name=MILVUS_COLLECTION_NAME,
        data=[query_vector],  # 注意，data: List[List[float]]
        anns_field="vector",
        output_fields=["text"],
        limit=2
    )
    if result:
        docs = [items.get("entity", {}).get("text") for items in result[0]]
        print(docs)

if __name__ == "__main__":
    #insert_data()
    query = "我最近减肥，想吃清淡爽口的"
    search_results = search_data(query)
    print("最终搜索结果：", search_results)
```

##### 2）工具定义

然后在`utils.py`中添加关于推荐菜品的工具：

```python
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from configs.config_loader import MILVUS_CONFIG, MILVUS_COLLECTION_NAME

ROOT = Path(__file__).parent.parent.parent

EMBEDDING = None
MILVUS_CLIENT = None


def get_embedding():
    global EMBEDDING
    if EMBEDDING is None:
        EMBEDDING = HuggingFaceEmbeddings(
            model_name=str(ROOT / "models/bge-base-zh"),
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    return EMBEDDING

def get_client():
    global MILVUS_CLIENT
    if MILVUS_CLIENT is None:
        MILVUS_CLIENT = MilvusClient(**MILVUS_CONFIG)
    return MILVUS_CLIENT


@tool
def user_flavor_search(query: str):
    """
    根据用户的口味、风味、食材偏好、饮食偏好或者身体状态描述做语义检索，并推荐相关菜品。
    适合处理清淡、鲜香、花生口味、减肥、上火、烦躁、不想吃太咸等不能只靠固定字段精确查询的问题。
    """
    # query向量化
    embedding = get_embedding()
    query_vector = embedding.embed_query(query)  # query: List[float]
	
    client = get_client()
    # result: List[List[dict]] = [[{id, distance, entity: {test}}, {...}, {...}]]
    result = client.search(
        collection_name=MILVUS_COLLECTION_NAME,
        data=[query_vector],  # 注意，使用 list[list[float]] 类型
        anns_field="vector",
        output_fields=["text"],
        limit=3
    )
    if result:
        menu_docs = []
        for item in result[0]:
            score = item.get("distance")  # 获取相似度分数
            text = item.get("eitity", {}).get("text")  # 获取相似文本
            if score is not None and score < 0.5:  # 排除召回相关性过低的内容
                continue
            menu_docs.append(text)
        return menu_docs
    return "抱歉，尚未找到匹配您喜好的相关菜品"
```

接下来测试该工具：

```python
if __name__ == "__main__":
    #import asyncio
    #asyncio.run(test_agent())
    #result = search_main_dishes().invoke({})
    #print(result)
    res = user_flavor_search.invoke({"user_query":"我想吃辣的菜"})
    print(res)
```

输出结果为：

```
当前查找结果为： data: [[{'id': 465590369019453399, 'distance': 0.5642827749252319, 'entity': {'text': '主菜名称: 麻婆豆腐\n价格: 18.0\n描述: 四川传统名菜，嫩滑豆腐配麻辣汤汁，下饭神器\n分类: 川菜\n 辣度等级: 3\n口味: 麻辣鲜香\n主要食材: 嫩豆腐,牛肉末,豆瓣酱,花椒\n烹饪方法: 烧炒\n是否为素食: 0\n过敏信息: 大豆,可能含有麸质\n'}}]]      
['主菜名称: 麻婆豆腐\n价格: 18.0\n描述: 四川传统名菜，嫩滑豆腐配麻辣汤汁，下饭神器\n分类: 川菜\n 辣度等级: 3\n口味: 麻辣鲜香\n主要食材: 嫩豆腐,牛肉末,豆瓣酱,花椒\n烹饪 方法: 烧炒\n是否为素食: 0\n过敏信息: 大豆,可能含有麸质\n']
```

**优化工具参数：**

同理，在`tools`目录的`args_schema.py`脚本中为`user_flavor_search`工具添加参数schema约束：

先定义参数schema：

```python
from pydantic import BaseModel, Field

class UserFlavorSearchToolArgsInfo(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=1000,
        description="用户关于口味、风味、食材偏好、饮食偏好或身体状况的原始描述"
    )
```

再添加到工具：

```python
from agent.tools.args_schema import UserFlavorSearchToolArgsInfo

@tool(args_schema=UserFlavorSearchToolArgsInfo)
def user_flavor_search(query: str):
    pass
```

**优化 agent 函数：**

在`langchain_assistant.py`中将`user_flavor_search`工具绑定到之前定义的 `get_agent` 函数中：

```python
...  # 省略其他导包
from agent.tools.utils import (
    search_menu,   # 后续还有其他工具会导入
)

...  # 省略中间代码

# 更新绑定工具到 agent
async def get_agent():
    global AGENT
    if AGENT is None:
        ...  					   # 省略
        all_tools = [search_menu]  # 设置工具
        AGENT = create_agent(
            tools=all_tools,       # 绑定工具
            ...
        )
    return AGENT
```

**优化测试方式：**

直接调用`user_flavor_search`工具测试成功，并不意味着Agent能正确识别现有的两个工具，尤其是当前两个工具实际上都具备一定的根据口味推荐菜品的能力。

因此，先定义个工具追踪器`tool_tracing`，专门用于展现Agent的工具调用过程和执行结果。由于`tool_tracing`仅做测试使用，直接定义在`langchain_assistant.py`中：

```python
def tool_tracing(query: str, response: Dict[str, List[AnyMessage]]) -> List[ToolCall]:
    print("="*100)
    print(">>> Human: ", query)
    print(">>> Trace: ")
    tool_calls = []
    for message in response["messages"]:
        if isinstance(message, AIMessage) and message.tool_calls:
            for tool_call in message.tool_calls:
                print(f"    tool_call: {tool_call['name']}  args={tool_call['args']}")
                tool_calls.append(tool_call)
        elif isinstance(message, ToolMessage):
            print(f"    tool_result: {message.name} => {message.content}")
    print(">>> Assistant: ", response["messages"][-1].content)
    return tool_calls
```

然后，继续在`langchain_assistant.py`中定义`test_agent`函数，专门用于测试Agent工具调用，同时为了：

```python
async def test_agent():
    # 获取 agent
    agent = await get_agent()
    config = {"configurable": {"thread_id": "123"}}
    # 用户输入
    queries = [
        "你们有哪些特色菜",
        "推荐几款不太辣的菜？",
        # "素食有哪些",
        # "酸甜的有吗？",
        "最近减肥，怎么吃", 
        # "不想吃重口，但又想吃点有味道的",
        # "你觉得我喜欢什么口味的",
        # "我们刚才聊了什么，你一共推荐了几个菜",
        "想吃泰式辣咖喱"
    ]
    # 调用 agent
    for query in queries:
        response = await agent.ainvoke(
            {"messages": [HumanMessage(query)]},
            config=config
        )
        tool_calls = tool_tracing(query, response)
```

#### 3.3.4 make_reservation：预订工具

该工具是`Agent`用于实际预订：确定预订所需要的信息，写入到数据库当中去。

由于该工具所需参数较多，为了让大模型能够更加精准地传参，因此首先通过`pydantic BaseModel`定义入参`schema`信息：

```python
from pydantic import BaseModel,Field

class ReservationToolArgsInfo(BaseModel):
    num_people:int = Field(
        ge=1,
        le=20,
        description="预约的总⼈数, 范围1-20"
    )
    num_children:int = Field(
        default=0,
        ge=0,
        le=100,
        description="预约的0-5岁⼉童⼈数"
    )
    arrival_time:str = Field(
        pattern=r"^\d{4}-\d{2}-\d{2} \d{2}$",  # 只校验格式，不校验逻辑，如：9999-99-99 99
        description="预约的到达时间,格式：YYYY-MM-DD HH"
    )
    seat_preference:str = Field(
        default="", 
        description="预约的座位偏好，当⽤户没有特殊需求时，传递空字符串即可"
    )
    main_dish_preference:str = Field(
        default="", 
        description="预约的主菜偏好，当⽤户没有特殊需求时，传递空字符串即可"
    )
    other_comments:str = Field(
        default="", 
        description="预约的其他备注，当⽤户没有特殊需求时，传递空字符串即可"
    )
```

定义完`schema`后，在`utils.py`即可通过`tool`当中的`args_schema`参数传入`ReservationToolArgsInfo`：

```python
from sqlalchemy import text, create_engine
from configs.config_loader import MYSQL_CONFIG

DB_ENGINE = None

# 提供另一种MySQL连接方式
def mysql_connection():
    global DB_ENGINE
    if DB_ENGINE is None:
        DB_ENGINE = create_engine(
            url=f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}",
            pool_size=15  # 连接池大小
        )
    return DB_ENGINE


@tool(args_schema=ReservationToolArgsInfo)
def make_reservation(
    num_people: int,
    arrival_time: str,
    num_children: int = 0,
    seat_preference: str = "",
    main_dish_preference: str = "",
    other_comments: str = ""
):
    """
    用户预约订位
    """
    try:
        with pymysql.connect(**MYSQL_CONFIG) as conn:
            with conn.cursor() as cursor:
                sql = """
                    insert into reservation_order(
                        num_people, 
                        num_children, 
                        arrival_time, 
                        seat_preference, 
                        main_dish_preference, 
                        other_comments
                    )
                    values(%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    num_people, 
                    num_children, 
                    arrival_time, 
                    seat_preference, 
                    main_dish_preference, 
                    other_comments
                ))
                conn.commit()  # 提交事务
                return "预订成功！"
    except Exception as e:
        return f"预订失败：{e}，请稍后重试"
```

```python
if __name__ == "__main__":
    #import asyncio
    #asyncio.run(test_agent())
    #result = search_main_dishes().invoke({})
    #print(result)
    #res = user_flavor_search.invoke({"user_query":"我想吃辣的菜"})
    #print(res)

    res = make_reservation.invoke({
       "num_people": 4,
       "num_children": 1,
       "arrival_time": "2023-08-01 18",
       "seat_preference": "靠窗",
       "main_dish_preference": "牛排",
       "other_comment": "希望有个好位置"
    })
    print(res)
```

**优化测试方式：**

优化`test_agent`，添加三个入参、两个函数来实现Agent追问后用户补充信息，并判断预订信息是否真的入库**（可作为作业）**

```python
def has_successful_tool_result(tool_name: str, result: Dict, success_text: str = "预订成功") -> bool:
    """判断指定工具是否已经成功执行"""
    return any(
        isinstance(message, ToolMessage) and 
        message.name == tool_name and 
        success_text in message.content for message in result["messages"]
    )


def has_tool_call(tool_name: str, tool_calls: List[ToolCall]) -> bool:
    """判断本轮对话结果中是否调用过指定的工具"""
    return any(tool_call["name"] == tool_name for tool_call in tool_calls)


async def test_agent(
    max_rounds: int = 5,
    reservation_created: bool = False,
    early_stop: bool = False
):
    # 获取 agent
    agent = await get_agent()
    config = {"configurable": {"thread_id": "123"}}
    # 用户输入
    queries = [
        # "你们有哪些特色菜",
        # "推荐几款不太辣的菜？",
        # "素食有哪些",
        # "酸甜的有吗？",
        # "最近减肥，怎么吃",
        # "不想吃重口，但又想吃点有味道的",
        # "你觉得我喜欢什么口味的",
        # "我们刚才聊了什么，你一共推荐了几个菜",
        # "想吃泰式辣咖喱"
        "我们两个人，没有小孩，今晚8点到"
    ]
    # 调用 agent
    for query in queries:
        response = await agent.ainvoke(
            {"messages": [HumanMessage(query)]},
            config=config
        )
        tool_calls = tool_tracing(query, response)
        # 判断预订工具调用是否成功
        if has_successful_tool_result("make_reservation", response):
            reservation_created = True

    rounds = 1
    while not reservation_created and rounds <= max_rounds:
        new_query = input(">>> 请您输入: ")
        if not new_query:
            print(">>> 输入为空，已结束本次预订流程")
            early_stop = True
            break
        # 调用agent
        new_result = await agent.ainvoke(
            {"messages": [HumanMessage(new_query)]},
            config=config
        )
        # 追踪工具调用情况
        tool_calls = tool_tracing(new_query, new_result)
        # 判断预订工具是否真的执行成功
        if has_successful_tool_result("make_reservation", new_result):
            reservation_created = True
            break
        # 工具调用正确，但预订信息写入失败
        if has_tool_call("make_reservation", tool_calls):
            print(">>> 预订工具已经调用，但没有成功写入，请根据追踪消息检查问题")
            early_stop = True
            break
        rounds += 1

    if not reservation_created and not early_stop:
        print(f">>> 已经达到最大追问轮数{max_rounds}，本次没有写入预订记录"
```

#### 3.3.5 高德MCP工具：提供相关导航信息

高德MCP工具通过魔搭MCP工具箱定义:

![image-20260412155524367](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260412155524367.png)

在`utils.py`中继续定义高德MCP工具，代码如下：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

async def get_mcp_tools():  # 异步函数
    global MCP_TOOLS
    if MCP_TOOLS is None:
		mcp_client = MultiServerMCPClient(
            {
                "amap-maps": {
                "transport": "sse",
                "url": "https://mcp.api-inference.modelscope.net/ccaef2a2308042/sse"
                }
            }
        )
        MCP_TOOLS = await mcp_client.get_tools()
        print(f"MCP 工具初始化完成，共计: {len(MCP_TOOLS)} 个")
    return MCP_TOOLS
```

上述代码，我们只需要添加在`create_agent`方法中即可，具体如手续过程。

### 3.4 **封装agent构造函数**

将所有相关工具定义好之后，将agent封装成一个独立的函数，在该独立的函数当中，构造全局单例agent实例：

```python
import os
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage, ToolCall
from agent.tools.utils import (
    search_menu,
    user_flavor_search,
    make_reservation,
    get_mcp_tools
)

load_dotenv()

ROOT = Path(__file__).parent.parent
MODEL = os.getenv("DEEPSEEK_MODEL")
AGENT = None

with open(ROOT / "agent/prompt/system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


async def get_agent():
    global AGENT
    if AGENT is None:
        # 初始化模型
        model = init_chat_model(model=MODEL, extra_body={"thinking": {"type": "disabled"}})
        # 设置工具
        mcp_tools = await get_mcp_tools()
        all_tools = [search_menu, user_flavor_search, make_reservation] + mcp_tools
        # 设置 checkpointer
        checkpointer = InMemorySaver()
        # 创建 agent
        AGENT = create_agent(
            model=model,
            tools=all_tools,
            checkpointer=checkpointer,
            system_prompt=SYSTEM_PROMPT
        )
    return AGENT
```

测试该Agent：将`test_agent`函数中的`queries`列表中的问题设置为：你能为我做什么？

```python
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent())
```

运行结果如下：

```
我可以帮助您完成以下任务：

1. **回答餐厅相关问题**：提供有关兰庭玉树太仓餐厅的信息，例如位置、电话、营业时间等 。

2. **完成餐厅预订**：如果您有预订需求，我可以帮助您完成预订，包括询问并确认相关信息 ，如人数、到达时间、座位和菜品偏好等。

如果您有任何具体需求或者问题，请告诉我！
```

### 3.5 定义Agent调用过程

提供Agent的调用过程，该功能以用户提出相关问题后，`Agent` 进行回复时，前端流式（打字机式）输出`Agent`回复内容，而不是等到`Agent`完全生成完回复之后，再进行回复。

要想实现该效果，需要使用到`SSE`技术。

SSE（Mozilla文档：https://developer.mozilla.org/zh-TW/docs/Web/API/Server-sent_events/Using_server-sent_events）是服务端向客户端发送数据流的一种通信技术:

<img src="https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418133628085.png" alt="image-20260418133628085" style="zoom:67%;" />

整体流程如下：

- 将 `agent` 流式输出定义为一个全局异步生成器函数；
- 在接口当中返回：`StreamingResponse `实例，该实例接收前面所定义的全局异步生成器

#### 3.5.1 定义`agent`流式输出

在`langchain_assistant.py`文件中上述的基础上再定义一个方法，用来将`agent`流式输出定义为全局异步生成器函数：

```python
async def assistant_query(user_query: str, session_id: str = "123"):
    """
    接收来自前端的用户query，使用agent进行回复
    """
    agent = await get_agent()
    # 1、调用前，新添加一个system prompt，让agent感知当前的时间
    from datetime import datetime
    from langchain.messages import ToolMessage
    current_date = datetime.now().strftime("%Y-%m-%d")
    day_of_week = datetime.now().weekday() + 1
    time_system_prompt = {"role":"system","content":f"当前日期为：{current_date}，当前是周{day_of_week}"}

    # 2、config如何去构建：在实际的生产环境下，每个用户的每一次会话，在后端系统当中，都会有一个session_id，可以拿这个session_id作为thread_id传进去
    config = {"configurable": {"thread_id": session_id}}
    # res = await agent.ainvoke({"messages":[time_system_prompt,{"role":"user","content":user_query}]},config=config)

    # 3、如何去调用agent: 通过流式输出
    async for chunk in agent.astream({"messages":[time_system_prompt,{"role":"user","content":user_query}]}, config=config, stream_mode="messages"):
        # chunk首先一个tuple:(AIMessageChunk/ToolMessage,_)
        message = chunk[0]
        if type(message) == ToolMessage:
            continue
        # 这个message 需要通过什么方式，给到谁：需要通过接口的方式，给到前端，然后让前端去展示？
        # SSE: Server-Sent Events 
        # SSE的数据结构：data: {"type":"token","content":"你好"}\n\n

        # 快速地将这个方法产出的token，给到后端接口，让后端接口去输出给前端
        import json
        payload = {"content":message.content,"type":"token"}
        payload_str = json.dumps(payload,ensure_ascii=False)
        yield f'data: {payload_str}\n\n'
```

#### 3.5.2 定义后端接口

在`api`目录下创建`main.py`文件，并定义一个接口提供前端调用的后端接口：

```python
"""
定义后端的所有的接口
"""
# 1、导入FastAPI
from fastapi import FastAPI
from starlette.responses import StreamingResponse
from pydantic import BaseModel
from  agent.langchain_assistant import assistant_query

# 2、创建一个application 简称app
app = FastAPI()
client = None

class ChatRequest(BaseModel):  # 你也可以将数据模型都归类到 api/models.py 中
    query:str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    智能对话接口
    接收用户问题，返回智能助手回复
    """
    session_id = "123"  # 理论上可以前端传入，也可以后端透传
    return StreamingResponse(
        assistant_query(request.query, session_id), # 这个函数是一个生成器函数，能够逐步生成回复内容
        media_type="text/event-stream" # 这种格式是为了实现流式响应，能够逐步返回数据，而不是等到所有数据准备好后一次性返回
    )
```

#### 3.5.3 启动服务

在项目的根目录下创建一个`run.py`启动服务

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api.main:app",host="0.0.0.0",port=8000)
```

运行后，我们看到docs如下：`http://localhost:8000/docs#/`

![image-20260418135710878](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418135710878.png)



测试，调用，输入内容：

![image-20260418140106568](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418140106568.png)

![image-20260418135946494](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418135946494.png)

之后，我们看到回复结果如下：
![image-20260418153545039](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418153545039.png)

#### 3.5.4 启动前端服务

-  项目结构

  ```
  ui/
  ├── src/
  │   ├── api/           # API服务层
  │   ├── components/    # Vue组件
  │   ├── assets/        # 静态资源
  │   ├── App.vue        # 根组件
  │   └── main.js        # 应用入口
  ├── package.json       # 项目配置
  ├── vite.config.js     # Vite配置
  └── index.html         # HTML模板
  ```

-  安装依赖

  ```bash
  cd ui
  npm install
  ```

-  运行项目

  ```bash
  npm run dev
  ```

  > 提示：开发环境下，Vite会将 `/api` 路径代理到 `http://localhost:8000`，确保后端服务在该地址运行。

  运行完成后，在地址栏输入：`http://localhost:3000`

  ![image-20260418154332968](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418154332968.png)

  接下来，可以通过页面实现聊天过程：`你好，你能为我做什么？`

  ![image-20260418155027221](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418155027221.png)

  测试工具调用情况：`你们这里有什么菜可以推荐吗？`

  <img src="https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418155331657.png" alt="image-20260418155331657" style="zoom:67%;" />

  `我想吃豆腐类的菜品，有什么推荐吗？`

  <img src="https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418155623687.png" alt="image-20260418155623687" style="zoom:67%;" />

  `你们这里可以接受预定吗？`

  <img src="https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418155805075.png" alt="image-20260418155805075" style="zoom:67%;" />

  `请帮我预定一下，明天晚上8点的靠窗的位置，2个人，不带小朋友的，主菜偏辣一点的`

  <img src="https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418160257514.png" alt="image-20260418160257514" style="zoom:67%;" />

  这个时候我们去数据库中查询看看是否有预定的记录：

  ![image-20260418160410043](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418160410043.png)

## 四、FAQ

例如，本项目中可以问`你们餐厅位置在哪里？`，那么像这种问题如果也交给大模型处理就完全没必要了，因为这种问题，可以认为是一个静态、固定的答案，也就是`FAQ`了。

**FAQ** 是 **Frequently Asked Questions** 的缩写，中文译为"**常见问题解答**"。

`FAQ` 是一份整理好的文档或页面，集中列出某个主题、产品、服务或领域中用户最常提出的问题，并提供对应的标准答案。

**主要作用**

| 作用           | 说明                                   |
| -------------- | -------------------------------------- |
| ✅ 提升效率     | 用户可快速自助查找答案，减少重复咨询   |
| ✅ 降低客服压力 | 减少人工客服处理基础问题的负担         |
| ✅ 改善用户体验 | 新用户能快速上手，老用户可快速定位问题 |
| ✅ 统一信息口径 | 避免因人工回复不一致造成的误解         |

**具体实现流程**

该接口在用户输入问题过程当中调用，每当用户输入停顿时，即调用该接口匹配`FAQ`库当中的相关问题：

![image-20260418182252353](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418182252353.png)

具体实现逻辑如下：

- 获取用户问题；
- 查找当前库中所有`FAQ`问题；
- 计算用户问题和库中所有`FAQ`问题的相似度评分；
- 按照特定阈值进行筛选，得到最相似的`n`个问题；
- 回复相关问题和答案；

用户点击相关问题时，直接回复答案，无需调用`/chat`接口。

本项目需通过`Redis`来实现`faq`功能。在项目资料中已经提供`redis:7.2`的`tar`包文件，首先将该文件通过如下命令导入到`docker`当中：

```bash
docker load -i redis.tar
```

通过如下命令即可将docker运行起来：

```bash
docker run -d --name my-redis -p 6379:6379 redis:7.2
```

![image-20260418184024482](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418184024482.png)

### 4.1 Redis基本操作

在agent目录中创建`redis_demo.py`文件，具体内容如下：

```python
from redis import Redis
def redis_command_demo1():
    """
    redis相关的命令demo演示
    """
    # 1、获取到client对象
    client = Redis.from_url("redis://localhost:6379",decode_responses=True)

    # 2、使用client对象，执行一些命令:
        # 命令很多，可以将命令做一些分类：
            # 字符串相关的命令
            # hash map相关的命令
            # list相关的命令
            # set相关的命令
            # zset相关的命令

    # 2.1 字符串相关的命令：执行set命令，创建一个value类型为string的key-value对
    client.set("name","张三")

    # 执行get命令，获取到key为name的value
    name = client.get("name")
    print(name)

    # 2.2 hash map 相关的命令：创建一个value为hash map 的 key-value对
    client.hset(
        "faq:items:address:test",
        mapping={
            "question":"地址是多少？",
            "answer":"上海杨浦区"
        }
    )

    # 获取到某一个key所对应hash map
    faq_item = client.hgetall("faq:items:address:test")
    print(faq_item)

    # # 2.3 set相关的命令：value为一个集合的key-value对
    # 添加了一个 key=faq:items value={"address","phone","email"} 的一个key-value对
    client.sadd(
        "faq:items3",
        "addres","phone","email"
    )

    # result就是key=faq:items 对应的value集合
    result = client.smembers(
        "faq:items3"
    )
    print(result)
    

def redis_command_demo2():
    """
    redis的pipeline命令的演示：
    1、
    """
    # 1、获取到client对象
    client = Redis.from_url("redis://localhost:6379",decode_responses=True)

    # 2、通过client，获取到pipeline对象
    pipeline = client.pipeline()

    # 3、使用pipeline声明，需要执行的命令
    pipeline.set("name3","张三")
    import time
    time.sleep(30)
    pipeline.get("name2")

    pipeline.hset(
        "faq:items:phone:test",
        mapping={
            "question":"手机号是多少？",
            "answer":"13800000000"
        }
    )

    # 4、 执行pipeline中的命令
    results = pipeline.execute()
    print(results)

redis_command_demo1()
```

测试完成，先在`utils.py`中添加`get_redis_client`方法，以备后续使用：

```python
from redis.asyncio import Redis
from configs.config_loader import MYSQL_CONFIG, MILVUS_CONFIG, MILVUS_COLLECTION_NAME, REDIS_CONFIG

REDIS_CLIENT = None

cfg = REDIS_CONFIG

async def get_redis_client():
    global REDIS_CLIENT
    if REDIS_CLIENT is None:
        return Redis(
            host=cfg['host'], port=cfg['port'], db=cfg['db'],
            password=cfg['password'], decode_responses=True # 建议改为 True 可避免⼿动 decode
        )
    return REDIS_CLIENT
```



### 4.2 FAQ 数据同步至 Redis 中

构造 FAQ 数值对，并且将其通过批处理脚本，同步至Redis当中去，在`agent`目录下创建文件`redis_data_sync.py`，示例代码如下：

```python
"""
用来完成FAQ数据同步操作，例如：
1. 餐厅位置
2. 联系方式
3. 餐厅营业时间
4. 停车是否方便
5. 优惠活动
"""
import asyncio
from typing import List, Dict
from agent.tools.utils import get_redis_client
from configs.config_loader import REDIS_CONFIG


cfg = REDIS_CONFIG
REDIS_CLIENT = None
FAQ_ITEMS: List[Dict[str, str]] = [
    {"id": "business_hours", "question": "营业时间是什么时候？", "answer": "我们的营业时间是，周日至周四：早10点至晚21点，周五周六：早10点至晚23点"},
    {"id": "address", "question": "位置在哪⾥？", "answer": "我们位于上海⼈⺠⼴场。"},
    {"id": "phone", "question": "联系⽅式是什么？", "answer": "您可以添加官⽅微信 shanghai_123，或拨打电话 021-11111111。"},
    {"id": "parking", "question": "停⻋⽅便吗？", "answer": "可优先使⽤附近公共停⻋场或路边划线⻋位；⻋位实时情况建议电话确认：021-11111111。"},
    {"id": "promotion", "question": "有什么优惠活动？", "answer": "优惠活动：单次消费满200九折，满500⼋折。"},
]


# FAQ 数据同步到 Redis 的异步函数
async def sync_faq_to_redis(namespace: str = "faq", items: List[Dict[str, str]] = None, replace: bool = False):
    redis = await get_redis_client()
    faq_items = items or FAQ_ITEMS
    meta_key = f"{namespace}:meta"
    ids_key = f"{namespace}:ids"

    if replace:
        old_ids = await redis.smembers(ids_key)
        if old_ids:
            # decode_responses=False 时返回 bytes，需转为字符串
            keys_to_del = [f"{namespace}:item:{key}" for key in old_ids]  # "faq:item:phone"
            if keys_to_del:
                await redis.delete(*keys_to_del)
        await redis.delete(ids_key, meta_key)     

    pipe = redis.pipeline()  # 定义一个 redis 指令管道

    for item in faq_items:
        faq_id = item.get("id")
        question = item.get("question")
        answer = item.get("answer")

        if not all([faq_id, question, answer]):
            continue

        key = f"{namespace}:item:{faq_id}"  # "faq:item:phone"
        pipe.hset(key, mapping={"id": faq_id, "question": question, "answer": answer})
        pipe.sadd(ids_key, faq_id)  # {"faq:ids": {"business_hours", "address", "phone", ...}} 

    pipe.hset(meta_key, mapping={"count": str(len(faq_items))})

    res = await pipe.execute()  # [False, 1, ]

    written = sum(1 for x in res if isinstance(x, int) and x > 0)

    return written


async def test():
    written = await sync_faq_to_redis(  # 异步调用
        namespace=cfg["faq_redis_namespace"],
        replace=True
    )
    print(f"成功写入 redis 的指令数量：{written}")


if __name__ == "__main__":
    asyncio.run(test())
```

运行后，进入`redis`容器，通过`KEYS *`命令查看具体生成的`keys`如下：

![image-20260418230534777](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260418230534777.png)

### 4.2 FAQ 数据加载

数据写入至 Redis 后，在项目中，就需要定义一个方法，用以将 FAQ 数据加载到内存中，后面需要用于和用户输入问题进行数据比对。在`utils.py`文件中定义加载函数如下所示：

```python
#其他代码省略

class FaqItem(BaseModel):
    id:str
    question:str
    answer:str

async def load_faq_items_from_redis(namespace: str = "faq") -> List[FaqItem]:
    """
    从redis加载faq问题
    """
    # 1、构建client 对象
    redis_client = await get_redis_client()
    pipeline = redis_client.pipeline()

    # 2、从redis set 中获取到faq所对应的所有keys
    faq_ids = await redis_client.smembers(f"{namespace}:ids")
    # 3、加载faq_keys所对应的所有faq，每个faq，构造成FaqItem对象
    full_keys = [f"{namespace}:item:{faq_id}" for faq_id in faq_ids]
    for faq_key in full_keys:
        pipeline.hgetall(faq_key) # 注意：Pipeline 的命令不需要 await，直接调⽤即可
    all_faq_items = await pipeline.execute()  # List[Dict[str, str]]
    return [FaqItem(**item) for item in all_faq_items]


async def main():
    # 1、加载faq数据到redis中
    res = await load_faq_items_from_redis()
    print("当前加载的faq数据为：", res)

    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

运行结果如下：

```bash
当前加载的faq数据为： [FaqItem(id='promotion', question='有什么优惠活动？', answer='优惠活动：单次消费满200九折，满500八折。'), FaqItem(id='address', question='位置在哪里？', answer='我们位于上海人民广场。'), FaqItem(id='phone', question='联系方式是什么？', answer='您可以添加官方微信 shanghai_123，或拨打电话 021-11111111。'), FaqItem(id='parking', question='停车方便吗？', answer='可优先使用附近公共停车场或路边划线车位；车位实时情况建议电话确认：021-11111111。'), FaqItem(id='business_hours', question='营业时间是什么时候？', answer='我们的营业时间是每天早9点至晚10点。')]
```

### 4.3 计算用户问题和 FAQ 问题相似度得分

对于用户问题和`FAQ`问题，直接通过字符串之间相似度来进行相似度判断得分。当前得分函数用了三种策略：

- `SequenceMatcher.ratio()`（字符序列相似）：基于最长公共子序列（LCS）等，衡量字符级别的相似程度；
- `Jaccard（字符集合相似）`：使用两个字符串构成的集合的交集比上两个字符串当中字符构成的并集；
- 包含关系` bonus`：当一个字符串，完全包含另外一个字符串时，额外添加一些bouns

在`utils.py`文件中继续添加如下代码：

```python
from difflib import SequenceMatcher
import re

# 定义正则表达式，用于移除文本中的标点符号
PUNCT_RE = re.compile(r"[\s,，。.!！？?;；:：'\"“”‘’（）()\[\]【】<>《》、/\\|_\-]+")

# 对文本进行清洗的函数：
def _normalize_text(text: str) -> str:
    return PUNCT_RE.sub("", (text or "").strip())

def get_similarity_score(query:str, faq_question:str)->float:
    """
    使用简单的字符串匹配算法，计算query和faq_question的相似度得分
    (备注：实际生产环境下，可以通过更复杂的算法，比如进行embedding再来计算余弦相似度等，来计算相似度得分)
    """
    # 1、算法一：使用一个包：difflib.SequenceMatcher
        # 底层原理：递归地比较两个字符串的最长公共子序列
            # 例如： a = abcdef b = rtabcedgef
            # 第一步：找到这两个字符串里面最长的公共子序列：abc
            # 第二步：把a串切成三部分["","abc","def"] 把b串同样也切成三部分:["rt","abc","edgef"]
            # 第三步：分别比较a串和b串左侧和右侧的部分，再找出公共最长子序列，依此类推，直到找不到最长公共子序列
            # 第四步：计算得分：2*所有最长公共子序列的长度和 / (a的长度+b的长度)
            # 通过该算法，能够捕捉到query和faq_question之间的带位置信息的相似度
        # 该算法的问题：
            # 举例：query: 密码忘记了怎么办，question：忘记了密码怎么办 
            # 针对于这种基本包含的关键词一致，但是关键词的语序位置不一样的匹配，得分会偏低
    q = _normalize_text(query)
    c = _normalize_text(faq_question)

    sequence_matcher = SequenceMatcher(None, q, c)
    score = sequence_matcher.ratio()

    # 2、算法二：实现一个算法，只计算query包含的关键词/字和question包含的关键词/字，所构成一个词袋，之间的相似度。
        # 此处引入Jaccard相似度：Jaccard相似度用来计算两个集合之间的相似度
        # Jaccard相似度的定义： set a 和 set b 的交集的元素数量 / (set a 和 set b 的并集的数量)
    a = set(list(q))
    b = set(list(c))
    jaccard_score = len(a.intersection(b)) / len(a.union(b))

    bonus = 0.0
    if q in c or c in q:
        bonus = 0.2

    # 3、对这两个分数做一个加权
    return 0.6*score + 0.4*jaccard_score + bonus
```

### 4.4 `FAQ` 接口封装

具体实现逻辑如下：

- 获取用户问题；
- 查找当前库中所有`FAQ`问题；
- 计算用户问题和库中所有`FAQ`问题的相似度评分；
- 按照特定阈值进行筛选，得到最相似的`n`个问题；
- 回复相关问题和答案；

在`main.py`中实现`FAQ`接口如下：

```python
class FAQResponse(BaseModel):
    success:bool
    query:str
    # 针对于用户的一个query，需要给到前端多个faq，
    suggestions:list[FaqItem]

@app.get("/faq/suggest",response_model=FAQResponse)
async def faq_endpoint(query:str, limit:int=1):
    # 1、从redis中获取所有的faq 的数据
    faq_items = await load_faq_items_from_redis()
    # 2、将这些数据中的question和用户的query，进行比较，得到相似度得分
    scores_list = []
    for faq_item in faq_items:
        score = get_similarity_score(query, faq_item.question)
        scores_list.append((score, faq_item))
        # 此处可以根据实际情况，调整不同的阈值，来筛选出哪些question是和用户query相关的
        # 如果不配置阈值的，总能够得到一个结果
    # 3、将这些得分进行排序，得到最相似的前1条数据
    scores_list.sort(key=lambda x:x[0],reverse=True)
    # 4、将这个结果，返回给前端
    return FAQResponse(
        success=True,
        query=query,
        suggestions=[faq_item for score, faq_item in scores_list[:limit]]
    )
```

启动前端服务，运行如下：
![image-20260419111954158](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260419111954158.png)

## 五、预订单查询

该接口用于查询所有预订单，效果如下所示:

![image-20260419112405997](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260419112405997.png)

直接通过查询MySQL数据即可，代码如下：

```python
from typing import Optional,List
from agent.tools.utils import mysql_connection
from datetime import datetime
from sqlalchemy import text


...

class ReservationItem(BaseModel):
    id: int
    num_people: int
    num_children: int
    arrival_time: Optional[str] = None
    seat_preference: Optional[str] = None
    main_dish_preference: Optional[str] = None
    other_comments: Optional[str] = None
    created_at: Optional[str] = None

class ReservationListResponse(BaseModel):
    success: bool
    reservations: List[ReservationItem]
    count: int
    message: str    

@app.get("/reservation/list", response_model=ReservationListResponse)
async def reservation_list_endpoint(limit: int = 1):
    """
    获取到预订列表
    """
    # 获取到sqlalchemy.engine.Connection，这个对象和pymysql.Connection有点区别
    with mysql_connection().connect() as conn:
        sql = """
        select
            id,
            num_people,
            num_children,
            arrival_time,
            seat_preference,
            main_dish_preference,
            other_comments,
            created_at
        from
            menu.reservation_order
        """
        # 直接通过conn.execute().fetchall() 获取到的是一个列表，列表的每个元素是一个元组
        # results = conn.execute(text(sql)).fetchall()
        # 通过conn.execute().mappings().fetchall() 获取到的是一个列表，列表的每个元素是一个字典
        results = conn.execute(text(sql)).mappings().fetchall()
        # 把results 转换为 ReservationItem 模型的列表
        item_list = []
        for result in results:
            item = ReservationItem(
                id=result["id"],
                num_people=result["num_people"],
                num_children=result["num_children"],
                arrival_time=datetime.strftime(result["arrival_time"],"%Y-%m-%d %H:%M:%S"),
                seat_preference=result["seat_preference"],
                main_dish_preference=result["main_dish_preference"],
                other_comments=result["other_comments"],
                created_at=datetime.strftime(result["created_at"],"%Y-%m-%d %H:%M:%S"),
            )
            item_list.append(item)

    return ReservationListResponse(
        success=True,
        reservations=item_list,
        count=len(item_list),
        message="success"
    )
```

## 六、菜品查询

该接口用以查询所有菜品，效果如下：

![image-20260419112304166](https://bwf-llm.oss-cn-beijing.aliyuncs.com/llm/image-20260419112304166.png)

直接通过`MySQL`查询数据即可，代码如下：

```python
class MenuItem(BaseModel):
    pass

# 定义菜品列表响应模型
class MenuListResponse(BaseModel):
    """菜品列表响应"""
    success: bool
    menu_items: List[MenuItem] # 菜品列表
    count: int # 菜品数
    message: str # 响应消息提示

@app.get("/menu/list",response_model=MenuListResponse)
async def menu_list():
    """
    获取到菜单列表
    """
    pass
    
```
