// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src') // ✅ 配置@指向src目录
    }
  },
  // 可选：跨域代理（解决前端调用后端接口跨域）
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000', // Flask后端地址
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  }
})