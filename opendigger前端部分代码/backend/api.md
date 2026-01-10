# OpenDigger 数据看板 API 文档

## 概述

- 接口BaseURL：`http://127.0.0.1:8000`
- 接口用途：支持前端「平台→组织/用户→指标→仓库」四级联动筛选，提供指标数据查询服务
- 数据来源：OpenDigger 官方静态数据（`https://oss.open-digger.cn/`）
- 缓存策略：本地 CSV 缓存（首次请求实时拉取，后续直接读取缓存）

## 全局说明

### 响应格式规范

#### 1. 成功响应（200 OK）

```json
{
  "code": 200,  // 仅部分接口返回（列表类接口直接返回数据数组）
  "message": "success",
  "data": {}  // 业务数据（根据接口类型变化）
}
```

- 列表类接口（如平台、组织、指标、仓库列表）直接返回数据数组，无外层包装
- 数据查询接口返回 `{"data": [...)]}` 格式

#### 2. 错误响应（4xx/5xx）

```json
{
  "detail": "错误描述信息"
}
```

### 通用错误码

| 状态码 | 说明       | 示例                                |
| ------ | ---------- | ----------------------------------- |
| 400    | 参数无效   | 不支持的平台、无效的实体类型        |
| 404    | 资源不存在 | 组织无仓库、OpenDigger 未导出该数据 |
| 500    | 服务器错误 | 缓存读取失败、数据处理异常          |

## 接口详情

### 1. 获取支持的平台

- 接口路径：`GET /api/platforms`
- 接口描述：前端第一步，加载平台下拉框选项
- 请求参数：无
- 响应示例（200 OK）：

```json
[
  {"value": "github", "label": "GitHub", "description": "GitHub 开源平台"},
  {"value": "gitee", "label": "Gitee", "description": "Gitee 开源平台"}
]
```

- 字段说明：
  - `value`：平台标识（前端传递参数用）
  - `label`：平台显示名称（前端下拉框显示）
  - `description`：平台描述（可选，用于前端提示）

### 2. 获取平台下的组织/用户

- 接口路径：`GET /api/entities/{platform}`

- 接口描述：前端第二步，选择平台后加载对应的组织/用户列表

- 请求参数：

  | 参数名   | 类型   | 位置 | 必选 | 说明                             |
  | -------- | ------ | ---- | ---- | -------------------------------- |
  | platform | string | 路径 | 是   | 平台标识（如 `github`、`gitee`） |

- 响应示例（200 OK）：

```json
[
  {"value": "vuejs", "label": "Vue.js", "type": "org", "description": "Vue 官方组织"},
  {"value": "torvalds", "label": "Linus Torvalds", "type": "user", "description": "Linux 创始人"}
]
```

- 字段说明：
  - `value`：实体标识（前端传递参数用）
  - `label`：实体显示名称
  - `type`：实体类型（`org`=组织，`user`=用户）
  - `description`：实体描述

### 3. 获取对应类型的指标

- 接口路径：`GET /api/metrics/{entity_type}`

- 接口描述：前端第三步，根据组织/用户类型加载对应的指标列表

- 请求参数：

  | 参数名      | 类型   | 位置 | 必选 | 说明                                |
  | ----------- | ------ | ---- | ---- | ----------------------------------- |
  | entity_type | string | 路径 | 是   | 实体类型（`org`=组织，`user`=用户） |

- 响应示例（200 OK，组织类型指标）：

```json
[
  {"value": "openrank", "label": "全域 OpenRank", "description": "仓库全域影响力指数"},
  {"value": "activity", "label": "活跃度", "description": "仓库月度活跃度"},
  {"value": "stars", "label": "星标数", "description": "仓库累计星标数"}
]
```

- 响应示例（200 OK，用户类型指标）：

```json
[
  {"value": "openrank", "label": "全域 OpenRank", "description": "开发者全域影响力指数"},
  {"value": "activity", "label": "活跃度", "description": "开发者月度活跃度"}
]
```

- 字段说明：
  - `value`：指标标识（前端传递参数用）
  - `label`：指标显示名称
  - `description`：指标说明

### 4. 获取组织下的可查询仓库

- 接口路径：`GET /api/repos/{platform}/{org}`

- 接口描述：前端第四步，选择组织后加载该组织下的可查询仓库（仅组织类型可用）

- 请求参数：

  | 参数名   | 类型   | 位置 | 必选 | 说明                    |
  | -------- | ------ | ---- | ---- | ----------------------- |
  | platform | string | 路径 | 是   | 平台标识（如 `github`） |
  | org      | string | 路径 | 是   | 组织标识（如 `vuejs`）  |

- 响应示例（200 OK）：

```json
[
  {"value": "vue", "label": "vue", "description": "Vue 核心库"},
  {"value": "vue-router", "label": "vue-router", "description": "Vue 路由库"}
]
```

- 字段说明：
  - `value`：仓库标识（前端传递参数用）
  - `label`：仓库显示名称
  - `description`：仓库描述

### 5. 获取开发者指标数据（无仓库）

- 接口路径：`GET /api/data/{platform}/{entity}/{metric}`

- 接口描述：查询用户类型的指标数据（无需仓库名）

- 请求参数：

  | 参数名   | 类型   | 位置 | 必选 | 说明                      |
  | -------- | ------ | ---- | ---- | ------------------------- |
  | platform | string | 路径 | 是   | 平台标识（如 `github`）   |
  | entity   | string | 路径 | 是   | 用户标识（如 `torvalds`） |
  | metric   | string | 路径 | 是   | 指标标识（如 `openrank`） |

- 响应示例（200 OK）：

```json
{
  "data": [
    ["2023-01", 120.5],
    ["2023-02", 135.2],
    ["2023-03", 150.8]
  ]
}
```

- 字段说明：
  - `data`：二维数组，每个元素为 `[月份, 指标值]`
  - 月份格式：`YYYY-MM`
  - 指标值：数字类型（保留1位小数）

### 6. 获取仓库指标数据（需仓库）

- 接口路径：`GET /api/data/{platform}/{entity}/{repo}/{metric}`

- 接口描述：查询组织下仓库的指标数据（需仓库名）

- 请求参数：

  | 参数名   | 类型   | 位置 | 必选 | 说明                      |
  | -------- | ------ | ---- | ---- | ------------------------- |
  | platform | string | 路径 | 是   | 平台标识（如 `github`）   |
  | entity   | string | 路径 | 是   | 组织标识（如 `vuejs`）    |
  | repo     | string | 路径 | 是   | 仓库标识（如 `vue`）      |
  | metric   | string | 路径 | 是   | 指标标识（如 `activity`） |

- 响应示例（200 OK）：

```json
{
  "data": [
    ["2023-01", 890],
    ["2023-02", 950],
    ["2023-03", 1020]
  ]
}
```

- 字段说明：同「开发者指标数据」

## 前端联动逻辑示例

1. 加载平台：调用 `/api/platforms` → 渲染平台下拉框
2. 选择平台（如 `github`）：调用 `/api/entities/github` → 渲染组织/用户下拉框
3. 选择实体（如 `vuejs`，类型为 `org`）：调用 `/api/metrics/org` → 渲染指标下拉框
4. 选择指标（如 `activity`）：调用 `/api/repos/github/vuejs` → 渲染仓库下拉框
5. 选择仓库（如 `vue`）：调用 `/api/data/github/vuejs/vue/activity` → 获取数据并渲染图表
6. 若选择用户实体（如 `torvalds`）：调用 `/api/metrics/user` → 选择指标后调用 `/api/data/github/torvalds/openrank` → 渲染图表

## 扩展说明

### 1. 新增平台

- 修改 `metadata.py` 的 `SUPPORTED_PLATFORMS` 数组，添加新平台配置
- 在 `PLATFORM_ENTITIES` 中添加该平台对应的组织/用户列表
- （可选）在 `ORG_REPOS` 中添加该平台组织下的仓库列表

### 2. 新增指标

- 若为组织指标：修改 `metadata.py` 的 `REPO_METRICS` 数组
- 若为用户指标：修改 `metadata.py` 的 `USER_METRICS` 数组
- 确保指标标识（`value`）与 OpenDigger 官方一致（如 `openrank`、`activity`）

### 3. 新增组织/仓库

- 新增组织：在 `PLATFORM_ENTITIES` 中添加组织配置（`type="org"`）
- 新增仓库：在 `ORG_REPOS` 中添加该组织下的仓库列表（键格式：`{platform}_{org}`）

## 调试工具

FastAPI 自带 Swagger UI 调试界面，启动后端后访问：
`http://127.0.0.1:8000/docs`
可直接在网页上测试所有接口，查看请求参数、响应格式和错误信息。

## 注意事项

1. 接口参数严格区分实体类型：`org` 类型需调用仓库数据接口，`user` 类型需调用开发者数据接口
2. 指标数据缓存有效期：本地 CSV 缓存长期有效，若需更新数据可删除 `data` 目录下对应的 CSV 文件
3. 跨域支持：当前配置允许所有域名访问（`allow_origins=["*"]`），生产环境可改为指定前端域名