@echo off
echo === 最后一步修复 ===
echo.

echo [1] 删除 aboutview.vue（如果存在）...
del src\views\AboutView.vue 2>nul
if exist "src\views\aboutview.vue" (
    del src\views\aboutview.vue
    echo ✅ 已删除 aboutview.vue
) else (
    echo ℹ️  aboutview.vue 不存在或已删除
)

echo [2] 确保路由文件正确...
(
echo import { createRouter, createWebHistory } from 'vue-router'
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
echo     component: () => import('@/views/TechView.vue')
echo   },
echo   {
echo     path: '/health',
echo     name: 'Health',
echo     component: () => import('@/views/HealthView.vue')
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

echo [3] 创建最简单的视图文件（如果不存在）...
if not exist "src\views\TechView.vue" (
    echo 创建 TechView.vue...
    echo ^<template^>^<h1^>技术栈页面^</h1^>^</template^> > src\views\TechView.vue
)

if not exist "src\views\HealthView.vue" (
    echo 创建 HealthView.vue...
    echo ^<template^>^<h1^>健康检测页面^</h1^>^</template^> > src\views\HealthView.vue
)

echo [4] 清理缓存...
rmdir /s /q node_modules\.vite 2>nul

echo.
echo ✅ 修复完成！
echo 现在运行：npm run dev
echo.
pause