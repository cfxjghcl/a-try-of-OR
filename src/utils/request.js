// 引入Axios
import axios from 'axios'

// 创建Axios实例，配置后端基础地址
const service = axios.create({
  baseURL: 'http://127.0.0.1:5000/api', // ✅ 地址正确，保留
  timeout: 5000, // 请求超时时间（5秒）
  headers: {
    'Content-Type': 'application/json' // 默认请求格式
  },
  withCredentials: true // 👉 新增：解决跨域时cookie传递问题（后端CORS需要）
})

// 请求拦截器（可选，比如添加token）
service.interceptors.request.use(
  (config) => {
    // 比如登录后把token加到请求头，传给后端
    const token = localStorage.getItem('token')
    if (token) {
      // 👉 调整：后端token验证是直接取token，不需要加Bearer前缀
      config.headers.Authorization = token 
    }
    return config
  },
  (error) => {
    console.error('请求出错：', error)
    return Promise.reject(error)
  }
)

// 响应拦截器（统一处理后端返回结果）
service.interceptors.response.use(
  (response) => {
    // 后端返回的数据都在response.data里
    const res = response.data
    // ✅ 适配后端：优先判断code，同时兼容msg字段（Flask常用）
    if (res.code !== 200 && res.code !== 201) { // 👉 补充：兼容201（注册成功的状态码）
      // ✅ 优先用res.msg，没有再用res.message，最后给默认提示
      alert(res.msg || res.message || '请求失败')
      return Promise.reject(res)
    } else {
      return res // 成功则返回数据
    }
  },
  (error) => {
    console.error('响应出错：', error)
    // ✅ 精准提示不同错误原因，方便定位
    if (error.message.includes('Network Error')) {
      alert('连接后端失败，请检查：1.后端是否启动 2.地址/端口是否正确')
    } else if (error.response?.status === 404) {
      alert(`接口不存在：${error.config.url}，请检查接口路径是否正确`)
    } else if (error.response?.status === 500) {
      alert('后端接口报错，请查看后端日志')
    } else if (error.response?.status === 401) {
      // 👉 新增：token失效/未登录的专属提示
      alert('登录状态失效，请重新登录')
      // 可选：自动跳转到登录页（后续加路由后可启用）
      // window.location.href = '/login'
    } else {
      // ✅ 适配后端返回的错误信息
      alert(error.response?.data?.msg || '请求失败：' + error.message)
    }
    return Promise.reject(error)
  }
)

// 导出配置好的Axios实例
export default service