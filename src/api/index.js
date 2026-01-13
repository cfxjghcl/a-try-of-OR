// 导入核心接口封装
import { opendiggerApi } from './api.js';

// 导出薪资趋势接口（供SalaryTrend.vue调用）
export const getSalaryTrend = opendiggerApi.getSalaryTrend;

// 可选：导出其他接口（按需添加）
export const getPlatforms = opendiggerApi.getPlatforms;
export const getEntities = opendiggerApi.getEntities;