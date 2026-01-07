import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    // 代理配置，解决CORS问题
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // 后端服务器地址
        changeOrigin: true,
      }
    },
    // 只监听localhost，避免防火墙警告
    host: 'localhost',
    port: 5173,
    open: false
  }
})