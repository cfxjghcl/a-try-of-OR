@echo off
echo 正在修复前端问题...
echo.

echo [1] 修复 App.vue...
(
echo ^<template^>
echo   ^<div id="app"^>
echo     ^<router-view /^>
echo   ^</div^>
echo ^</template^>
echo.
echo ^<script^>
echo export default {
echo   name: 'App'
echo }
echo ^</script^>
echo.
echo ^<style^>
echo #app {
echo   font-family: Arial, sans-serif;
echo   margin: 0;
echo   padding: 0;
echo }
echo ^</style^>
) > src\App.vue

echo [2] 修复 main.js...
(
echo import { createApp } from 'vue'
echo import App from './App.vue'
echo import router from './router'
echo.
echo const app = createApp(App)
echo app.use(router)
echo app.mount('#app')
) > src\main.js

echo [3] 创建路由文件...
mkdir src\router 2>nul
(
echo import { createRouter, createWebHistory } from 'vue-router'
echo import TechView from '@/views/TechView.vue'
echo import HealthView from '@/views/HealthView.vue'
echo.
echo const routes = [
echo   {
echo     path: '/',
echo     name: 'Home',
echo     redirect: '/tech'
echo   },
echo   {
echo     path: '/tech',
echo     name: 'Tech',
echo     component: TechView
echo   },
echo   {
echo     path: '/health',
echo     name: 'Health',
echo     component: HealthView
echo   }
echo ]
echo.
echo const router = createRouter({
echo   history: createWebHistory(),
echo   routes
echo })
echo.
echo export default router
) > src\router\index.js

echo [4] 创建缺失的组件...
mkdir src\views 2>nul
mkdir src\components 2>nul
mkdir src\api 2>nul

echo [5] 安装依赖...
call npm install echarts echarts-wordcloud

echo.
echo ✅ 修复完成！
echo 现在运行：npm run dev
echo.
pause