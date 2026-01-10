// src/api/api.js
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等全局参数
    console.log(`发起请求: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// API方法定义
export const opendiggerApi = {
  // 1. 获取平台列表
  getPlatforms() {
    return apiClient.get('/api/platforms');
  },
  // 2. 获取平台下的组织/用户
  getEntities(platform) {
    return apiClient.get(`/api/entities/${platform}`);
  },
  // 3. 获取对应类型的指标
  getMetrics(entityType) {
    return apiClient.get(`/api/metrics/${entityType}`);
  },
  // 新增：获取组织下的仓库列表
  getRepos(platform, org) {
    return apiClient.get(`/api/repos/${platform}/${org}`);
  },
  // 4. 获取开发者数据（无仓库）
  getUserData(platform, entity, metric) {
    return apiClient.get(`/api/data/${platform}/${entity}/${metric}`);
  },
  // 5. 获取仓库数据（有仓库）
  getRepoData(platform, entity, repo, metric) {
    return apiClient.get(`/api/data/${platform}/${entity}/${repo}/${metric}`);
  }
};

// 其他API模块可以按功能分组
export const favoritesApi = {
  // 收藏相关的API方法
  // getFavorites(), addFavorite(), removeFavorite() 等
};

export default apiClient;