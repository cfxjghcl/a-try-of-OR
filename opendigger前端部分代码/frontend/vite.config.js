import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src') // 配置@别名，确保路由里的@/xxx路径生效
    }
  },
  server: {
    open: '/professional-nav' // 启动项目后自动打开 professional-nav 页面
  }
})