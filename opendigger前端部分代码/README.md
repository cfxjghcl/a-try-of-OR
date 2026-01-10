## **基于OpenDigger+FastAPI+Vue搭建动态可视化平台**

### **核心目标**

本教程旨在完整演示一个前后端分离项目的开发全过程。我们将使用 FastAPI 后端方案和 Vue 前端方案，搭建一个可以动态展示 OpenDigger 开源项目数据的可视化平台，并同步展示从仓库创建到功能迭代的完整 Git 使用流程。

### **最终技术栈**

*   **后端**：Python, FastAPI, APScheduler, Requests, Pandas
*   **前端**：Vue.js, Vite, Apache **ECharts, Axios**, Vue Router, Pinia
*   **版本控制**：Git



### **目录结构**

```
opendigger-viz-platform/
│
├── .gitignore
├── README.md
│
├── backend/                  # 后端代码
│   ├── data/                 # 数据缓存目录
│   ├── .venv/                # Python虚拟环境
│   ├── main.py               # FastAPI主文件
│   ├── data_fetcher.py       # 数据拉取模块
│   ├── config.json           # 后端配置文件
│   └── requirements.txt      # 后端依赖
│
└── frontend/                 # 前端代码
    ├── public/
    ├── src/
    │   ├── components/       # Vue组件
    │   │   └── RepoChart.vue # 核心图表组件
    │   ├── views/            # 路由对应页面
    │   │   ├── HomeView.vue  # 首页（数据大屏）
    │   │   └── FavoritesView.vue # 收藏页
    │   ├── router/           # Vue Router配置
    │   │   └── index.js
    │   ├── stores/           # Pinia状态管理
    │   │   └── index.js
    │   ├── App.vue           # 根组件
    │   └── main.js           # 入口文件（注册路由、Pinia）
    ├── tests/                # Vitest测试目录
    │   └── unit/             # 单元测试文件夹
    │       └── RepoChart.spec.js # 图表组件测试用例
    ├── index.html
    ├── package.json
    └── vite.config.js
```

------

### **第一部分：远程仓库创建与本地环境初始化**

**目标**：建立项目的远程代码托管中心，克隆到本地，并搭建好前后端的基础目录结构，完成框架的首次提交。

#### **步骤1：在Gitee (或GitHub) 创建远程仓库**

1.  登录您的 Gitee 或 GitHub 账号。
2.  点击右上角的“+”号，选择“新建仓库”。
3.  **填写仓库信息**：
    *   **仓库名称**: `opendigger-viz-platform`
    *   **仓库介绍**: (可选) `一个基于 FastAPI 和 Vue.js 的 OpenDigger 数据可视化平台。`
    *   **是否开源**: 选择“公开”。
    *   **初始化仓库**: **务必勾选** `使用 Readme 文件初始化这个仓库`。这会创建一个包含 `README.md` 的 `main` 分支，是后续克隆的基础。
    *   (可选) **添加 .gitignore**: 可以选择 `Python` 或 `Node` 模板，后续我们再进行合并和完善。
4.  点击“创建仓库”。现在，您拥有了一个项目的远程“家”。

#### **步骤2：克隆远程仓库到本地**

1. 在您刚创建的仓库页面，找到并复制仓库的 HTTPS 或 SSH URL。

2. 在本地，打开 Visual Studio Code (VS Code) 或你喜欢的终端。

3. **使用 `git clone` 命令** 将远程仓库下载到你的电脑上。这会自动创建一个名为 `opendigger-viz-platform` 的文件夹。

   ```bash
   git clone <你复制的仓库URL>
   ```

4. 进入项目目录：

   ```bash
   cd opendigger-viz-platform
   ```

   *   **Git知识点**：`git clone` 不仅下载了文件，还自动设置好了本地仓库与远程仓库的连接 (`origin`)，这是后续 `push` 和 `pull` 的基础。

#### **步骤3：在本地搭建前后端框架**

现在，我们将在克隆下来的项目目录中，搭建实际的开发框架。

1. **手动创建后端目录**：

   ```bash
   mkdir backend
   ```

2. **使用Vue构建工具创建前端**：
   在**项目根目录** (`opendigger-viz-platform`) 下，运行Vue官方脚手架命令。它会自动帮我们创建 `frontend` 目录和所有必要的文件（后面再详细介绍）。

3. **完善 `.gitignore` 文件**：
   脚手
   架工具可能已经创建或修改了 `.gitignore`。我们需要确保它包含了前后端的所有忽略规则。打开根目录的 `.gitignore` 文件，确保其内容至少包含以下部分（如果已有，则合并补充）：

   ```gitignore
   # Python
   __pycache__/
   *.pyc
   .venv/
   venv/
   env/
   .env*
   
   # Node.js
   /frontend/node_modules/
   /frontend/dist/
   .npm/
   
   # IDE / OS
   .idea/
   .vscode/
   .DS_Store
   ```

   *   **注意**：这里的 `/frontend/node_modules/` 写法更精确，指明是 `frontend` 目录下的 `node_modules`。

#### **步骤4：提交框架并推送到远程仓库**

我们的本地项目框架已经搭建完毕，是时候将这个“骨架”同步到 Gitee/GitHub 了。

1. **查看状态**：检查一下哪些新文件被创建了。

   ```bash
   git status
   ```

   你会看到 `backend/` 目录和整个 `frontend/` 目录都是新文件。

2. **暂存所有变更**：

   ```bash
   git add .
   ```

3. **提交变更**：写一个清晰的提交信息，说明我们做了什么。

   ```bash
   git commit -m "feat: Setup project structure with backend folder and Vue frontend scaffold"
   ```

4. **推送到远程仓库**：将本地的这次提交同步到 Gitee/GitHub。

   ```bash
   git push origin main
   ```

   *   **Git知识点**：`git push` 是将本地提交上传到远程仓库的核心命令。`origin` 是我们克隆时Git默认设置的远程仓库别名，`main` 是我们要推送到的分支。

现在，刷新你的 Gitee/GitHub 仓库页面，你会看到 `backend` 和 `frontend` 目录已经出现了。项目的基础框架搭建完毕，并且版本历史清晰，后续的开发就可以在此基础上进行。

------

### **第二部分：后端服务开发 (FastAPI)**

**目标**：搭建一个能自动同步数据并提供API接口的稳定后端。

#### **步骤1：创建后端文件**

进入`backend`目录，并创建以下文件结构和内容：

*   `backend/requirements.txt`
*   `backend/config.json`
*   `backend/data_fetcher.py`
*   `backend/main.py`

1. **`requirements.txt`** (项目依赖)

   ```text
   fastapi
   uvicorn[standard]
   requests
   apscheduler
   pandas
   ```

2. **`config.json`** (数据源配置)

   ```json
   {
     "repositories": [
       { "platform": "github", "org": "vuejs", "repo": "vue" },
       { "platform": "github", "org": "apache", "repo": "echarts" },
       { "platform": "gitee", "org": "anolis", "repo": "cloud-kernel" }
     ],
     "metrics": [ "activity", "openrank" ],
     "data_source": {
       "base_url": "https://oss.open-digger.cn/{platform}/{org}/{repo}/{metric}.json"
     }
   }
   ```

3. **`data_fetcher.py`** (数据同步脚本)

   ```python
   import json
   from pathlib import Path
   import requests
   import pandas as pd
   import warnings
   warnings.filterwarnings('ignore', message='Unverified HTTPS request')
   
   BACKEND_ROOT = Path(__file__).parent
   CONFIG_FILE = BACKEND_ROOT / "config.json"
   DATA_DIR = BACKEND_ROOT / "data"
   if not DATA_DIR.exists():
       DATA_DIR.mkdir(exist_ok=True)
   
   def sync_opendigger_data():
       print("--- [FETCH] 开始同步OpenDigger数据 ---")
       try:
           with open(CONFIG_FILE, "r", encoding="utf-8") as f:
               config = json.load(f)
           repos = config["repositories"]
           metrics = config["metrics"]
           base_url = config["data_source"]["base_url"]
       except Exception as e:
           print(f"--- [错误] 读取配置失败: {e} ---")
           return
   
       for repo_info in repos:
           platform, org, repo = repo_info["platform"], repo_info["org"], repo_info["repo"]
           repo_filename = f"{platform}_{org}_{repo}"
           
           for metric in metrics:
               api_url = base_url.format(platform=platform, org=org, repo=repo, metric=metric)
               save_path = DATA_DIR / f"{repo_filename}_{metric}.csv"
               try:
                   response = requests.get(api_url, timeout=30, verify=False)
                   response.raise_for_status()
                   data = response.json()
                   if not isinstance(data, dict):
                       raise ValueError("数据格式非键值对")
                   
                   formatted_data = [{"month": k, "count": v} for k, v in data.items() if len(k) == 7 and '-' in k]
                   if not formatted_data:
                       raise ValueError("无有效时间数据")
                   
                   df = pd.DataFrame(formatted_data)
                   df.to_csv(save_path, index=False, encoding="utf-8-sig")
                   print(f"✅ 成功: {platform}/{org}/{repo} - {metric}")
               except requests.exceptions.HTTPError as e:
                   if e.response.status_code == 404:
                       print(f"❌ 跳过 (404): {platform}/{org}/{repo} - {metric}")
                   else:
                       print(f"❌ HTTP错误: {platform}/{org}/{repo} - {metric} -> {e}")
               except Exception as e:
                   print(f"❌ 处理失败: {platform}/{org}/{repo} - {metric} -> {e}")
       print("--- [FETCH] 数据同步完成 ---")
   
   if __name__ == "__main__":
       sync_opendigger_data()
   ```

4. **`main.py`** (API主服务)

   ```python
   from fastapi import FastAPI, HTTPException
   from fastapi.middleware.cors import CORSMiddleware
   from pathlib import Path
   import pandas as pd
   from apscheduler.schedulers.asyncio import AsyncIOScheduler
   from data_fetcher import sync_opendigger_data
   
   app = FastAPI(title="OpenDigger数据API")
   scheduler = AsyncIOScheduler()
   BASE_DIR = Path(__file__).parent
   DATA_DIR = BASE_DIR / "data"
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
   )
   
   @app.on_event("startup")
   async def startup_event():
       print("=== 后端服务启动，执行首次数据同步... ===")
       sync_opendigger_data()
       scheduler.add_job(sync_opendigger_data, "cron", hour=3, minute=0)
       scheduler.start()
       print("=== 定时任务已启动 (每天03:00) ===")
   
   @app.get("/api/data/{platform}/{org}/{repo}/{metric}")
   async def get_project_metric(platform: str, org: str, repo: str, metric: str):
       file_name = f"{platform}_{org}_{repo}_{metric}.csv"
       file_path = DATA_DIR / file_name
       if not file_path.exists():
           raise HTTPException(status_code=404, detail="数据不存在")
       try:
           df = pd.read_csv(file_path)
           return {"data": df[["month", "count"]].values.tolist()}
       except Exception as e:
           raise HTTPException(status_code=500, detail=f"数据处理失败: {e}")
   ```

#### **步骤2：启动并测试后端**

1. 在**项目根目录**打开一个**新的终端**，进入后端目录并设置虚拟环境：

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

3. 启动服务：

   ```bash
   uvicorn main:app --reload
   ```

   你应该能看到数据开始同步的日志，以及服务运行在 `http://127.0.0.1:8000` 的提示。

4. **测试接口**：打开浏览器访问 `http://127.0.0.1:8000/api/data/github/vuejs/vue/activity`，如果能看到JSON数据，说明后端工作正常！

#### **步骤3：提交后端代码**

回到**第一个终端**（项目根目录的那个），提交我们完成的后端代码。

```bash
git add backend/
git commit -m "feat(backend): Implement FastAPI server with data fetching and API endpoint"
```

*   **Git知识点**：`feat(backend):` 是一种更详细的提交规范，指明了本次提交是关于`backend`的`feat`（新功能）。

---

### **第三部分：前端应用开发 (Vue)**

**目标**：使用您提供的代码，构建一个美观、交互性强的PC端可视化界面。

#### **步骤1：初始化Vue项目**

1. 在**项目根目录**（`opendigger-viz-platform`）下，运行官方脚手架：

   ```bash
   npm create vue@latest
   ```

2. 在交互式提问中，进行如下选择：

   *   `Project name`: **frontend**
   *   `Add Vue Router?`: **Yes**
   *   `Add Pinia?`: **Yes**
   *   (其他全部选 **No**，保持项目简洁)

#### **步骤2：安装依赖并整理文件结构**

1. 进入新创建的 `frontend` 目录并安装核心依赖：

   ```bash
   cd frontend
   npm install
   ```

2. 安装额外的库：

   ```bash
   npm install echarts axios
   ```

3. **整理文件**：Vue脚手架会生成一些示例文件，我们需要清理和调整。

   *   删除 `src/components/` 下的所有文件。
   *   删除 `src/views/AboutView.vue`。
   *   在 `src/stores/` 目录下，将 `counter.js` 重命名为 `favorites.js`。

#### **步骤3：编写前端核心代码**

现在，我们将您提供的代码片段填入对应的文件中。

1. **`src/main.js`** (注册路由和Pinia)

   ```javascript
   import { createApp } from 'vue'
   import { createPinia } from 'pinia'
   import App from './App.vue'
   import router from './router'
   
   // 引入一个全局CSS，让界面更美观
   import './assets/main.css' 
   
   const app = createApp(App)
   app.use(createPinia())
   app.use(router)
   app.mount('#app')
   ```

2. **`src/assets/main.css`** (新建此文件，提供基础样式)

   ```css
   body {
     margin: 0;
     font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
     background-color: #f8fafc;
     color: #1e293b;
   }
   ```

3. **`src/router/index.js`** (配置路由)

   ```javascript
   import { createRouter, createWebHistory } from 'vue-router'
   import HomeView from '../views/HomeView.vue'
   import FavoritesView from '../views/FavoritesView.vue'
   
   const router = createRouter({
     history: createWebHistory(import.meta.env.BASE_URL),
     routes: [
       { path: '/', name: 'home', component: HomeView },
       { path: '/favorites', name: 'favorites', component: FavoritesView }
     ]
   })
   export default router
   ```

4. **`src/stores/favorites.js`** (状态管理)

   ```javascript
   import { ref } from 'vue'
   import { defineStore } from 'pinia'
   
   export const useFavoritesStore = defineStore('favorites', () => {
     const favoriteProjects = ref([])
   
     const addFavorite = (project) => {
       const isExist = favoriteProjects.value.some(item => item.fullName === project.fullName)
       if (!isExist) {
         favoriteProjects.value.push(project)
         alert(`已收藏项目：${project.name}`)
       } else {
         alert(`项目${project.name}已在收藏夹中`)
       }
     }
   
     const removeFavorite = (fullName) => {
       favoriteProjects.value = favoriteProjects.value.filter(item => item.fullName !== fullName)
     }
     return {
       favoriteProjects,
       addFavorite,
       removeFavorite
     }
   })
   ```

5. **`src/App.vue`** (根组件，PC端导航布局)

6. **`src/views/HomeView.vue`** (首页)

7. **`src/views/FavoritesView.vue`** (收藏页)

8. **`src/components/RepoChart.vue`** (核心图表组件)
   *(由于这4个`.vue`文件代码较长，为保持教程流畅性，此处省略，**可以直接使用附录种完整代码**)*

#### **步骤4：启动并测试前端**

1. 确保你的后端服务仍在运行。

2. 在 `frontend` 目录下，运行开发服务器：

   ```bash
   npm run dev
   ```

3. 打开浏览器访问终端提示的地址 (通常是 `http://localhost:5173`)。你应该能看到一个设计精良、功能齐全的可视化平台！

   *   **测试功能**：点击图表上的“收藏”按钮，然后切换到“我的收藏”页面查看。刷新页面，收藏应该依然存在。

#### **步骤5：提交前端代码**

前端功能完成，是时候进行一次重要的提交了。

```bash
# 回到项目根目录的终端
git add frontend/
git commit -m "feat(frontend): Implement Vue app with Home, Favorites pages and chart component"
```

---

### **第四部分：项目收尾与Git远程推送**

#### **步骤1：更新`README.md`**

现在项目可以运行了，回到根目录，更新`README.md`中的“如何运行”部分。

#### **步骤2：推送到GitHub**

1. 在 GitHub 上创建一个新的空仓库 (不要勾选任何初始化选项)。

2. 复制仓库的URL，然后在本地终端运行：

   ```bash
   git remote add origin <你的GitHub仓库URL>
   git branch -M main
   git push -u origin main
   ```

**至此，您已经从零开始，完整地搭建了一个专业的前后端分离项目，并拥有了清晰的Git提交历史。这个教程本身，就是一个极佳的、可供他人学习和复刻的示例！**



---

### **附录： 完整的前端代码结构和实现**

请按照以下结构组织你的 `frontend/src/` 目录，并用提供的代码覆盖或创建相应的文件。

```
frontend/src/
├── assets/         # (可以为空)
├── components/
│   └── RepoChart.vue   # 核心图表组件 (增强版)
├── router/
│   └── index.js      # 路由配置文件
├── stores/
│   └── favorites.js  # Pinia状态管理 (收藏夹)
├── views/
│   ├── HomeView.vue    # 首页大屏视图
│   └── FavoritesView.vue # 我的收藏视图
├── App.vue         # 根组件 (导航栏布局)
└── main.js         # 应用入口 (挂载Router和Pinia)
```

---

### **三、 完整代码 (请直接复制替换)**

#### **1. `main.js` - 应用入口**

在这里我们将初始化Pinia和Vue Router。

```javascript
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
```

#### **2. `router/index.js` - 路由配置 (新建)**

创建 `src/router/` 目录，并在其中新建 `index.js`。

```javascript
import { createRouter, createWebHistory } from 'vue-router'
// 引入路由对应需要渲染的组件
import HomeView from '../views/HomeView.vue'
import FavoritesView from '@/views/FavoritesView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/favorites',
      name: 'favorites',
      component: FavoritesView,
    },
  ],
})

export default router
```

#### **3. `stores/favorites.js` - 状态管理 (新建)**

创建 `src/stores/` 目录，并在其中新建 `favorites.js`。

```javascript
// frontend/src/stores/favorites.js（建议单独建一个文件，更清晰）
import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useFavoritesStore = defineStore('favorites', () => {
  // 1. 定义状态（对应选项式的 state）
  const favoriteProjects = ref([]) // 收藏列表（用 ref 包装数组）

  // 2. 定义操作方法（对应选项式的 actions）
  const addFavorite = (project) => {
    // 避免重复收藏（检查项目 fullName 是否已存在）
    const isExist = favoriteProjects.value.some(item => item.fullName === project.fullName)
    if (!isExist) {
      favoriteProjects.value.push(project) // 往数组里添加项目
      alert(`已收藏项目：${project.name}`)
    } else {
      alert(`项目${project.name}已在收藏夹中`)
    }
  }

  const removeFavorite = (fullName) => {
    // 过滤掉要删除的项目
    favoriteProjects.value = favoriteProjects.value.filter(item => item.fullName !== fullName)
  }

  // 3. （可选）定义计算属性（对应选项式的 getters，这里暂时用不到）
  // const favoriteCount = computed(() => favoriteProjects.value.length) // 示例：收藏数量

  // 4. 返回需要暴露的状态和方法
  return {
    favoriteProjects,
    addFavorite,
    removeFavorite
    // favoriteCount // 若定义了计算属性，需在这里返回
  }
})
```

#### **4. `App.vue` - 根组件 (PC端布局)**

这是应用的整体框架，包含了专业的顶部导航栏。

```vue
<!-- src/App.vue -->
<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="logo">OpenDigger 可视化平台</div>
      <nav class="app-nav">
        <router-link to="/" class="nav-link">首页大屏</router-link>
        <router-link to="/favorites" class="nav-link">我的收藏</router-link>
      </nav>
    </header>
    <main class="app-main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup></script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2.5rem; /* 使用rem单位，更具弹性 */
  height: 70px;
  background-color: var(--card-bg-color);
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color-dark);
}

.app-nav {
  display: flex;
  gap: 1rem;
}

.nav-link {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-color-light);
  text-decoration: none;
  border-radius: 6px;
  transition: background-color 0.2s, color 0.2s;
  position: relative;
}

.nav-link:hover {
  background-color: #f1f5f9;
  color: var(--text-color-dark);
}

/* 激活状态的链接样式 */
.nav-link.router-link-exact-active {
  color: var(--primary-color);
  background-color: var(--primary-color-light);
}

/* 内容区 */
.app-main-content {
  flex-grow: 1; /* 占据剩余所有空间 */
  width: 100%;
  max-width: 1600px; /* 限制最大宽度，防止内容过散 */
  margin: 0 auto;
  padding: 2.5rem; /* 使用rem增加呼吸感 */
}
</style>
```

#### **5. `views/HomeView.vue` - 首页大屏 (新建)**

创建 `src/views/` 目录，并新建 `HomeView.vue`。

```vue
<!-- src/views/HomeView.vue -->
<template>
  <div class="home-view">
    <header class="view-header">
      <h1>开源洞察数据看板</h1>
      <p>探索知名开源项目的多维度数据指标</p>
    </header>
    <div class="chart-grid">
      <div v-for="chart in chartList" :key="chart.title" class="chart-card">
        <RepoChart 
          :platform="chart.platform"
          :org="chart.org"
          :repo="chart.repo"
          :metric="chart.metric"
          :title="chart.title"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import RepoChart from '../components/RepoChart.vue';
// chartList 内容不变
const chartList = [
  { platform: "github", org: "vuejs", repo: "vue", metric: "activity", title: "VueJS - 月度活跃度" },
  { platform: "github", org: "vuejs", repo: "vue", metric: "openrank", title: "VueJS - OpenRank趋势" },
  { platform: "github", org: "apache", repo: "echarts", metric: "activity", title: "ECharts - 月度活跃度" },
  { platform: "github", org: "apache", repo: "echarts", metric: "openrank", title: "ECharts - OpenRank趋势" },
  { platform: "gitee", org: "anolis", repo: "cloud-kernel", metric: "activity", title: "Anolis Cloud-Kernel - 月度活跃度" },
  { platform: "gitee", org: "anolis", repo: "cloud-kernel", metric: "openrank", title: "Anolis Cloud-Kernel - OpenRank趋势" }
];
</script>

<style scoped>
.view-header {
  text-align: center;
  margin-bottom: 3rem;
}

.view-header h1 {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
}

.view-header p {
  font-size: 1.125rem;
  color: var(--text-color-light);
}

/* 核心：响应式网格布局 */
.chart-grid {
  display: grid;
  /* 
   * `repeat(auto-fill, ...)`: 自动填充尽可能多的列
   * `minmax(400px, 1fr)`: 每列最小宽度400px，最大平分剩余空间(1fr)
   * 这使得网格在不同屏幕宽度下能自动调整列数 (例如 1, 2, 3, 4列)
  */
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-card {
  background-color: var(--card-bg-color);
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
  overflow: hidden; /* 防止子元素溢出圆角 */
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}
</style>
```

#### **6. `views/FavoritesView.vue` - 我的收藏 (新建)**

在 `src/views/` 目录下，新建 `FavoritesView.vue`。

```vue
<!-- src/views/FavoritesView.vue -->
<template>
  <div class="favorites-view">
    <header class="view-header">
      <h2>我的收藏项目</h2>
    </header>
    <div v-if="favoritesStore.favoriteProjects.length === 0" class="empty-state">
      <p>暂无收藏项目</p>
      <span>去首页点击图表右上角的 ❤️ 按钮收藏你感兴趣的图表吧！</span>
    </div>
    <div v-else class="favorites-grid">
      <div v-for="project in favoritesStore.favoriteProjects" :key="`${project.fullName}-${project.metric}`" class="favorite-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>{{ project.title }}</h3>
            <a :href="project.url" target="_blank" rel="noopener noreferrer">{{ project.fullName }}</a>
          </div>
          <button @click="handleRemove(project)" class="remove-btn" title="取消收藏">×</button>
        </div>
        <div class="card-chart">
          <RepoChart :platform="project.platform" :org="project.fullName.split('/')[0]" :repo="project.fullName.split('/')[1]" :metric="project.metric" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useFavoritesStore } from '../stores/favorites';
import RepoChart from '../components/RepoChart.vue';
const favoritesStore = useFavoritesStore();

const handleRemove = (project) => {
  if (confirm(`确定要取消收藏「${project.title}」吗？`)) {
    favoritesStore.removeFavorite(`${project.fullName}-${project.metric}`);
  }
};
</script>

<style scoped>
.view-header h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.empty-state {
  text-align: center;
  padding: 5rem 1rem;
  background-color: var(--card-bg-color);
  border-radius: 12px;
  border: 2px dashed var(--border-color);
}
.empty-state p { font-size: 1.5rem; font-weight: 600; margin: 0 0 1rem; }
.empty-state span { color: var(--text-color-light); }

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 2rem;
}

.favorite-card {
  background-color: var(--card-bg-color);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}
.favorite-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.card-title-group h3 { margin: 0 0 0.25rem; font-size: 1.25rem; }
.card-title-group a { font-size: 0.9rem; color: var(--text-color-light); text-decoration: none; }
.card-title-group a:hover { text-decoration: underline; }

.remove-btn {
  background: transparent; border: none; color: var(--text-color-light);
  width: 36px; height: 36px; border-radius: 50%;
  font-size: 1.5rem; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background-color 0.2s, color 0.2s;
}
.remove-btn:hover { background-color: var(--danger-color-light); color: var(--danger-color); }

.card-chart {
  width: 100%;
  height: 350px; /* 在卡片内部，可以给图表一个固定高度以保持对齐 */
}
</style>
```

#### **7. `components/RepoChart.vue` - 核心图表组件 **

这是最关键的组件，我们对其UI和功能进行了全面优化。

```vue
<template>
  <div class="chart-container">
    <div class="chart-header" v-if="title">
      <h3>{{ title }}</h3>
      <button @click="handleFavorite" class="favorite-btn">❤️</button>
    </div>
    <div ref="chartRef" class="chart-dom"></div>
    <div v-if="loading" class="state-overlay">
      <div class="spinner"></div>
      <span>正在加载...</span>
    </div>
    <div v-if="error" class="state-overlay error-overlay">
      <span>⚠️ {{ error }}</span>
    </div>
  </div>
</template>

<script setup>
// 脚本逻辑不变，保持之前的图表渲染和数据请求
import { ref, onMounted, onUnmounted, shallowRef, nextTick } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';
import { useFavoritesStore } from '../stores/favorites';

const props = defineProps({
  platform: { type: String, required: true, default: 'github' },
  org: { type: String, required: true },
  repo: { type: String, required: true },
  metric: { type: String, required: true },
  title: { type: String, default: '' }
});

const favoritesStore = useFavoritesStore();
const chartRef = ref(null);
const chartInstance = shallowRef(null);
const loading = ref(true);
const error = ref(null);
const API_BASE_URL = 'http://127.0.0.1:8000';

const handleFavorite = () => {
  const platformDomain = props.platform === 'github' ? 'github.com' : 'gitee.com';
  const project = {
    name: props.repo,
    fullName: `${props.org}/${props.repo}`,
    url: `https://${platformDomain}/${props.org}/${props.repo}`,
    metric: props.metric,
    title: props.title,
    platform: props.platform
  };
  favoritesStore.addFavorite(project);
};

const resizeChart = () => {
  if (chartInstance.value) {
    chartInstance.value.resize();
  }
};

onMounted(async () => {
  await nextTick();
  if (!chartRef.value) return;

  chartInstance.value = echarts.init(chartRef.value);
  window.addEventListener('resize', resizeChart);

  try {
    const response = await axios.get(`${API_BASE_URL}/api/data/${props.platform}/${props.org}/${props.repo}/${props.metric}`);
    const chartData = response.data.data;

    if (!Array.isArray(chartData) || chartData.length === 0) {
      throw new Error("暂无有效数据");
    }

    const option = {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', axisLabel: { rotate: 30 } },
      yAxis: { type: 'value' },
      series: [{
        data: chartData,
        type: 'line',
        smooth: true,
        areaStyle: {},
        lineStyle: { width: 2 }
      }],
      grid: { left: '5%', right: '5%', top: '10%', bottom: '15%' }
    };

    chartInstance.value.setOption(option);
  } catch (err) {
    error.value = `数据加载失败: ${err.message}`;
  } finally {
    loading.value = false;
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart);
  if (chartInstance.value) {
    chartInstance.value.dispose();
  }
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  padding: 3%; /* 内边距用百分比，随卡片宽度缩放 */
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2%; /* 与图表的间距用百分比 */
}

.chart-dom {
  flex-grow: 1; /* 占满剩余高度 */
  min-height: 250px;
}

/* 其他样式保持不变 */
.favorite-btn {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  border: none;
  background: #f1f5f9;
  cursor: pointer;
  font-size: 1.2rem;
}
.favorite-btn:hover {
  background: #fecaca;
  color: #b91c1c;
}

.state-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: rgba(255,255,255,0.8);
  border-radius: 12px;
}
.error-overlay { color: #b91c1c; }

.spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.5rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
```

#### **8. `src/assets/main.css` - 全局样式 **

```css
/* src/assets/main.css */

/* 1. CSS 变量定义 (方便全局修改主题) */
:root {
  --primary-color: #4f46e5;      /* 主题色 - 靛蓝 */
  --primary-color-light: #eef2ff; /* 主题浅色 */
  --text-color-dark: #1e293b;     /* 主要文字颜色 */
  --text-color-light: #64748b;    /* 次要文字颜色 */
  --bg-color: #f8fafc;           /* 全局背景色 */
  --card-bg-color: #ffffff;      /* 卡片背景色 */
  --border-color: #e2e8f0;       /* 边框颜色 */
  --danger-color: #dc2626;        /* 危险/删除颜色 */
  --danger-color-light: #fee2e2;  /* 危险浅色 */
}

/* 2. 全局样式重置 */
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-color-dark);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 3. 盒模型统一 */
*, *::before, *::after {
  box-sizing: border-box;
}
```



### **四、 最后一步：启动和运行**

现在你的前端代码已经完全重构好了。按照之前的步骤：

1.  **启动后端**：`cd backend` 然后 `uvicorn main:app --reload`
2.  **启动前端**：`cd frontend` 然后 `npm run dev`

打开浏览器访问 `http://localhost:5173` (或终端提示的地址)，你将会看到一个外观专业、布局清晰、交互流畅的PC端可视化平台！

