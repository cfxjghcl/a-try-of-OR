<template>
  <div class="container">
    <h1>前后端连接测试</h1>
    <p>当前时间：{{ currentTime }}</p >
    
    <div class="test-section">
      <h2>后端连接测试</h2>
      
      <div class="api-info">
        <strong>后端地址：</strong>
        <code>http://localhost:5000/api/test-connection</code>
      </div>
      
      <button 
        @click="testBackendConnection" 
        :disabled="testing"
        class="test-btn"
        :class="{ 'testing': testing }"
      >
        {{ testing ? '测试中...' : '点击测试后端连接' }}
      </button>
      
      <button @click="clearResults" class="clear-btn">
        清除结果
      </button>
    </div>
    
    <div v-if="result" class="result-box" :class="result.success ? 'success' : 'error'">
      <h3>
        {{ result.success ? '✅ 连接成功！' : '❌ 连接失败' }}
      </h3>
      
      <div v-if="result.data" class="response-data">
        <h4>返回数据：</h4>
        <pre>{{ JSON.stringify(result.data, null, 2) }}</pre>
      </div>
      
      <div v-if="result.error" class="error-message">
        <h4>错误信息：</h4>
        <div>{{ result.error }}</div>
      </div>
      
      <div v-if="result.responseTime !== undefined" class="response-time">
        <strong>响应时间：</strong> {{ result.responseTime }}ms
      </div>
    </div>
    
    <div class="quick-links">
      <h3>快速测试链接</h3>
      <div class="link-buttons">
        <a 
          href=" " 
          target="_blank"
          class="link-btn health-btn"
        >
          测试后端健康检查
        </a >
        <a 
          href="http://localhost:5000/api/test-connection" 
          target="_blank"
          class="link-btn test-btn"
        >
          直接访问测试API
        </a >
        <a 
          href="http://localhost:5173" 
          class="link-btn refresh-btn"
        >
          刷新前端页面
        </a >
      </div>
    </div>
    
    <div class="debug-info">
      <h4>调试信息</h4>
      <div><strong>前端地址：</strong> http://localhost:5173</div>
      <div><strong>后端地址：</strong> http://localhost:5000</div>
      <div><strong>当前状态：</strong> 
        <span v-if="testing" style="color: orange;">测试中...</span>
        <span v-else style="color: green;">就绪</span>
      </div>
      <div class="debug-tip">
        提示：按 F12 打开浏览器开发者工具，查看 Console 和 Network 标签页获取详细信息
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      currentTime: new Date().toLocaleString(),
      testing: false,
      result: null
    }
  },
  mounted() {
    setInterval(() => {
      this.currentTime = new Date().toLocaleString()
    }, 1000)
  },
  methods: {
    async testBackendConnection() {
      this.testing = true
      this.result = null
      
      const startTime = Date.now()
      
      try {
        console.log('开始测试后端连接...')
        const response = await fetch('http://localhost:5000/api/test-connection')
        const responseTime = Date.now() - startTime
        
        console.log('响应状态:', response.status, response.statusText)
        
        if (response.ok) {
          const data = await response.json()
          console.log('后端返回数据:', data)
          
          this.result = {
            success: true,
            data: data,
            responseTime: responseTime
          }
        } else {
          throw new Error(`HTTP错误: ${response.status} ${response.statusText}`)
        }
      } catch (error) {
        const responseTime = Date.now() - startTime
        console.error('连接失败:', error)
        
        this.result = {
          success: false,
          error: error.message,
          responseTime: responseTime
        }
      } finally {
        this.testing = false
      }
    },
    
    clearResults() {
      this.result = null
    }
  }
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
  line-height: 1.6;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 { color: #333; margin-bottom: 10px; }
h2, h3, h4 { color: #444; margin-bottom: 15px; }
p { color: #666; margin-bottom: 20px; }

.test-section {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.api-info {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.test-btn, .clear-btn {
  padding: 12px 24px;
  font-size: 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-right: 10px;
}

.test-btn {
  background-color: #007bff;
  color: white;
}

.test-btn:hover:not(:disabled) { background-color: #0056b3; }
.test-btn:disabled { background-color: #6c757d; cursor: not-allowed; }
.test-btn.testing { background-color: #ffc107; }

.clear-btn {
  background-color: #6c757d;
  color: white;
}

.clear-btn:hover { background-color: #545b62; }

.result-box {
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.result-box.success {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.result-box.error {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.response-data, .error-message { margin-top: 15px; }

.response-data pre {
  background-color: white;
  padding: 15px;
  border-radius: 6px;
  overflow: auto;
  font-size: 14px;
  border: 1px solid #ddd;
  margin-top: 10px;
}

.error-message div {
  background-color: white;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
}

.response-time {
  margin-top: 10px;
  font-size: 14px;
}

.quick-links {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.link-buttons {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.link-btn {
  padding: 8px 16px;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  display: inline-block;
  transition: opacity 0.2s;
}

.link-btn:hover { opacity: 0.9; }
.health-btn { background-color: #28a745; }
.test-btn { background-color: #17a2b8; }
.refresh-btn { background-color: #6c757d; }

.debug-info {
  margin-top: 30px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  font-size: 14px;
}

.debug-tip {
  margin-top: 10px;
  color: #666;
  font-style: italic;
}

@media (max-width: 600px) {
  .container { padding: 10px; }
  .test-btn, .clear-btn { width: 100%; margin-bottom: 10px; margin-right: 0; }
  .link-buttons { flex-direction: column; }
  .link-btn { width: 100%; text-align: center; }
}
</style>
