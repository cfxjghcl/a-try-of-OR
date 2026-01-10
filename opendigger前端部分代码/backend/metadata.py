# metadata.py - 新增仓库列表配置
from typing import List, Dict

# ===================== 基础配置（开发者可扩展）=====================
# 1. 支持的平台（不变）
SUPPORTED_PLATFORMS: List[Dict] = [
    {"value": "github", "label": "GitHub", "description": "GitHub 开源平台"},
    {"value": "gitee", "label": "Gitee", "description": "Gitee 开源平台"}
]

# 2. 平台→组织/用户映射（不变）
PLATFORM_ENTITIES: Dict[str, List[Dict]] = {
    "github": [
        {"value": "vuejs", "label": "Vue.js", "type": "org", "description": "Vue 官方组织"},
        {"value": "apache", "label": "Apache", "type": "org", "description": "Apache 软件基金会"},
        {"value": "torvalds", "label": "Linus Torvalds", "type": "user", "description": "Linux 创始人"},
        {"value": "yyx990803", "label": "Evan You", "type": "user", "description": "Vue 作者"}
    ],
    "gitee": [
        {"value": "anolis", "label": "Anolis OS", "type": "org", "description": "龙蜥操作系统"},
        {"value": "aliyun", "label": "阿里云", "type": "org", "description": "阿里云开源组织"}
    ]
}

# 3. 新增：组织→仓库映射（从 OpenDigger repo_list.csv 提取，仅保留已导出的仓库）
ORG_REPOS: Dict[str, List[Dict]] = {
    # GitHub - vuejs 组织下的可查询仓库（来自 OpenDigger repo_list.csv）
    "github_vuejs": [
        {"value": "vue", "label": "vue", "description": "Vue 核心库"},
        {"value": "vue-router", "label": "vue-router", "description": "Vue 路由库"},
        {"value": "vuex", "label": "vuex", "description": "Vue 状态管理库"},
        {"value": "vue-cli", "label": "vue-cli", "description": "Vue 脚手架工具"}
    ],
    # GitHub - apache 组织下的可查询仓库
    "github_apache": [
        {"value": "echarts", "label": "echarts", "description": "可视化图表库"},
        {"value": "flink", "label": "flink", "description": "流处理框架"},
        {"value": "spark", "label": "spark", "description": "大数据处理框架"}
    ],
    # Gitee - anolis 组织下的可查询仓库
    "gitee_anolis": [
        {"value": "anolisos", "label": "anolisos", "description": "龙蜥操作系统核心仓库"},
        {"value": "openanolis", "label": "openanolis", "description": "龙蜥开源社区仓库"}
    ],
    # Gitee - aliyun 组织下的可查询仓库
    "gitee_aliyun": [
        {"value": "aliyun-cli", "label": "aliyun-cli", "description": "阿里云 CLI 工具"},
        {"value": "oss-java-sdk", "label": "oss-java-sdk", "description": "OSS Java SDK"}
    ]
}

# 4. 指标分类（不变）
REPO_METRICS: List[Dict] = [
    {"value": "openrank", "label": "全域 OpenRank", "description": "仓库全域影响力指数"},
    {"value": "community_openrank", "label": "社区 OpenRank", "description": "仓库社区贡献度指数"},
    {"value": "activity", "label": "活跃度", "description": "仓库月度活跃度"},
    {"value": "stars", "label": "星标数", "description": "仓库累计星标数"},
    {"value": "technical_fork", "label": "技术分叉", "description": "仓库技术分叉数"},
    {"value": "issues_new", "label": "新问题数", "description": "月度新增 Issues 数"},
    {"value": "change_requests", "label": "变更请求数", "description": "月度 PR 数"}
]

USER_METRICS: List[Dict] = [
    {"value": "openrank", "label": "全域 OpenRank", "description": "开发者全域影响力指数"},
    {"value": "community_openrank", "label": "社区 OpenRank", "description": "开发者社区贡献度指数"},
    {"value": "activity", "label": "活跃度", "description": "开发者月度活跃度"},
    {"value": "new_contributors", "label": "新贡献者数", "description": "开发者带来的新贡献者数"},
    {"value": "contributors", "label": "贡献者数", "description": "开发者参与项目的贡献者数"}
]

# ===================== 工具函数（新增获取仓库列表）=====================
def get_platforms() -> List[Dict]:
    return SUPPORTED_PLATFORMS

def get_entities(platform: str) -> List[Dict]:
    return PLATFORM_ENTITIES.get(platform, [])

def get_metrics(entity_type: str) -> List[Dict]:
    if entity_type == "org":
        return REPO_METRICS
    elif entity_type == "user":
        return USER_METRICS
    return []

def get_repos(platform: str, org: str) -> List[Dict]:
    """根据平台+组织获取可查询的仓库列表"""
    key = f"{platform}_{org}"
    return ORG_REPOS.get(key, [])

# 其他工具函数（不变）
def is_supported_platform(platform: str) -> bool:
    return platform in [p["value"] for p in SUPPORTED_PLATFORMS]

def is_valid_entity(platform: str, entity: str) -> bool:
    entities = get_entities(platform)
    return any(e["value"] == entity for e in entities)

def get_entity_type(platform: str, entity: str) -> str:
    entities = get_entities(platform)
    for e in entities:
        if e["value"] == entity:
            return e["type"]
    return ""