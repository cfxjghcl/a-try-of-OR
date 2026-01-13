import axios from 'axios';

// Flask后端地址（根据实际端口调整）
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true // 跨域传递token/cookie
});

// 请求拦截器：添加token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = token;
    }
    console.log(`发起请求: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：统一处理返回结果
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API请求错误:', error.message);
    return Promise.reject(error);
  }
);

// API方法定义
export const opendiggerApi = {
  // 原有接口
  getPlatforms() { return apiClient.get('/platforms'); },
  getEntities(platform) { return apiClient.get(`/entities/${platform}`); },
  getMetrics(entityType) { return apiClient.get(`/metrics/${entityType}`); },
  getRepos(platform, org) { return apiClient.get(`/repos/${platform}/${org}`); },
  getUserData(platform, entity, metric) { return apiClient.get(`/data/${platform}/${entity}/${metric}`); },
  getRepoData(platform, entity, repo, metric) { return apiClient.get(`/data/${platform}/${entity}/${repo}/${metric}`); },
  
  // 新增：薪资趋势接口
  getSalaryTrend() { return apiClient.get('/salary-trend'); }
};

export default apiClient;