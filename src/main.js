import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
// 导入封装好的请求工具
import request from './utils/request'

const app = createApp(App)
app.use(router)
// 全局挂载，所有页面可通过this.$request调用
app.config.globalProperties.$request = request
app.mount('#app')