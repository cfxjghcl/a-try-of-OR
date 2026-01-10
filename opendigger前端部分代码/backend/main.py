from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd
import requests
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# 导入独立元数据
import metadata as meta

# --- 初始化配置 ---
app = FastAPI(title="OpenDigger 动态API", description="按 OpenDigger 特性区分指标类型")
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# --- 跨域配置 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 核心接口（按前端联动逻辑设计）---
@app.get("/api/platforms", summary="获取支持的平台")
async def get_platforms():
    """前端第一步：加载平台下拉框"""
    return meta.get_platforms()

@app.get("/api/entities/{platform}", summary="获取平台下的组织/用户")
async def get_entities(platform: str):
    """前端第二步：选择平台后，加载对应的组织/用户（含类型标识）"""
    if not meta.is_supported_platform(platform):
        raise HTTPException(status_code=400, detail=f"不支持的平台：{platform}")
    entities = meta.get_entities(platform)
    return entities

@app.get("/api/metrics/{entity_type}", summary="获取对应类型的指标")
async def get_metrics(entity_type: str):
    """前端第三步：选择组织/用户后，根据类型加载指标（org→仓库指标，user→开发者指标）"""
    if entity_type not in ["org", "user"]:
        raise HTTPException(status_code=400, detail=f"无效的类型：{entity_type}，仅支持 org/user")
    metrics = meta.get_metrics(entity_type)
    return metrics

# 在原有接口基础上，新增 /api/repos/{platform}/{org} 接口
@app.get("/api/repos/{platform}/{org}", summary="获取组织下的可查询仓库")
async def get_repos(platform: str, org: str):
    """前端第四步：选择组织后，加载该组织下的可查询仓库（仅 org 类型可用）"""
    # 校验参数
    if not meta.is_supported_platform(platform):
        raise HTTPException(status_code=400, detail=f"不支持的平台：{platform}")
    if not meta.is_valid_entity(platform, org):
        raise HTTPException(status_code=400, detail=f"平台 {platform} 无该组织：{org}")
    if meta.get_entity_type(platform, org) != "org":
        raise HTTPException(status_code=400, detail=f"{org} 不是组织类型，无仓库列表")
    
    # 获取仓库列表
    repos = meta.get_repos(platform, org)
    if not repos:
        raise HTTPException(status_code=404, detail=f"该组织暂无可查询的仓库")
    return repos

@app.get("/api/data/{platform}/{entity}/{metric}", summary="获取开发者指标数据（无仓库）")
async def get_user_data(platform: str, entity: str, metric: str):
    """获取开发者指标（无需仓库名）：https://oss.open-digger.cn/{platform}/{user}/{metric}.json"""
    # 校验参数
    if not meta.is_supported_platform(platform):
        raise HTTPException(status_code=400, detail="不支持的平台")
    if not meta.is_valid_entity(platform, entity):
        raise HTTPException(status_code=400, detail=f"平台 {platform} 无该实体：{entity}")
    entity_type = meta.get_entity_type(platform, entity)
    if entity_type != "user":
        raise HTTPException(status_code=400, detail=f"该实体是 {entity_type}，请使用仓库数据接口")
    if metric not in [m["value"] for m in meta.get_metrics("user")]:
        raise HTTPException(status_code=400, detail=f"开发者不支持该指标：{metric}")
    
    # 数据路径和请求逻辑
    file_name = f"{platform}_{entity}_{metric}.csv"
    file_path = DATA_DIR / file_name
    api_url = f"https://oss.open-digger.cn/{platform}/{entity}/{metric}.json"
    
    return await fetch_and_save_data(api_url, file_path)

@app.get("/api/data/{platform}/{entity}/{repo}/{metric}", summary="获取仓库指标数据（需仓库）")
async def get_repo_data(platform: str, entity: str, repo: str, metric: str):
    """获取仓库指标（需仓库名）：https://oss.open-digger.cn/{platform}/{org}/{repo}/{metric}.json"""
    # 校验参数
    if not meta.is_supported_platform(platform):
        raise HTTPException(status_code=400, detail="不支持的平台")
    if not meta.is_valid_entity(platform, entity):
        raise HTTPException(status_code=400, detail=f"平台 {platform} 无该实体：{entity}")
    entity_type = meta.get_entity_type(platform, entity)
    if entity_type != "org":
        raise HTTPException(status_code=400, detail=f"该实体是 {entity_type}，请使用开发者数据接口")
    if metric not in [m["value"] for m in meta.get_metrics("org")]:
        raise HTTPException(status_code=400, detail=f"仓库不支持该指标：{metric}")
    
    # 数据路径和请求逻辑
    file_name = f"{platform}_{entity}_{repo}_{metric}.csv"
    file_path = DATA_DIR / file_name
    api_url = f"https://oss.open-digger.cn/{platform}/{entity}/{repo}/{metric}.json"
    
    return await fetch_and_save_data(api_url, file_path)

# --- 通用工具函数 ---
async def fetch_and_save_data(api_url: str, file_path: Path):
    """通用数据获取和保存逻辑"""
    # 已存在则直接返回
    if file_path.exists():
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
            return {"data": df[["month", "count"]].values.tolist()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"读取缓存失败：{str(e)}")
    
    # 实时请求 OpenDigger 数据
    try:
        response = requests.get(api_url, timeout=30, verify=False)
        response.raise_for_status()
        data = response.json()
        
        # 筛选有效时间键（只保留月度 YYYY-MM，可选季度/年度）
        formatted_data = [
            {"month": date_str, "count": value}
            for date_str, value in data.items()
            if len(date_str) == 7 and date_str.count("-") == 1  # 仅保留月度数据
        ]
        
        if not formatted_data:
            raise HTTPException(status_code=404, detail="无有效月度数据")
        
        # 保存为 CSV
        pd.DataFrame(formatted_data).to_csv(file_path, index=False, encoding="utf-8-sig")
        return {"data": formatted_data}
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"OpenDigger 未导出该数据（404）")
        else:
            raise HTTPException(status_code=500, detail=f"请求失败：{str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据处理失败：{str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)