<template>
  <div class="feedback-container">
    <!-- 页面标题 -->
    <h1 class="feedback-title">建议与反馈</h1>

    <!-- 反馈表单卡片 -->
    <div class="feedback-card" v-if="!submitSuccess">
      <form class="feedback-form" @submit.prevent="handleSubmit">
        <!-- 建议与需求输入框 -->
        <div class="form-group">
          <label class="form-label" for="suggestion">您的建议与需求 <span class="required">*</span></label>
          <textarea
            id="suggestion"
            v-model="formData.suggestion"
            class="form-control"
            placeholder="请详细描述您的建议、需求或遇到的问题..."
            rows="6"
            required
          ></textarea>
        </div>

        <!-- 邮箱地址输入框 -->
        <div class="form-group">
          <label class="form-label" for="email">您的邮件地址 <span class="required">*</span></label>
          <input
            type="email"
            id="email"
            v-model="formData.email"
            class="form-control"
            placeholder="请输入您的邮箱地址，方便我们回复您"
            required
          />
        </div>

        <!-- 按钮组 -->
        <div class="btn-group">
          <button type="button" class="btn btn-back" @click="goToHome">返回首页</button>
          <button type="submit" class="btn btn-submit" :disabled="isSubmitting">
            <span v-if="isSubmitting">提交中...</span>
            <span v-else>提交建议</span>
          </button>
        </div>
      </form>
    </div>

    <!-- 提交成功提示弹窗 -->
    <div class="success-modal" v-if="submitSuccess">
      <div class="success-content">
        <div class="success-icon">✅</div>
        <h2 class="success-title">提交成功！</h2>
        <p class="success-desc">感谢您的建议，您的建议是我们前进最大的动力</p>
        <button class="btn btn-home" @click="goToHome">返回首页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// 初始化路由
const router = useRouter()

// 表单数据
const formData = ref({
  suggestion: '', // 建议内容
  email: ''       // 邮箱地址
})

// 状态控制
const isSubmitting = ref(false)    // 提交中状态
const submitSuccess = ref(false)   // 提交成功状态

// 提交表单处理
const handleSubmit = async () => {
  try {
    isSubmitting.value = true
    
    // 模拟接口请求（真实项目替换为后端API）
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 提交成功，显示提示弹窗
    submitSuccess.value = true
    
    // 清空表单（可选）
    formData.value = { suggestion: '', email: '' }
  } catch (error) {
    console.error('提交反馈失败：', error)
    alert('提交失败，请稍后重试！')
  } finally {
    isSubmitting.value = false
  }
}

// 返回首页
const goToHome = () => {
  // 假设首页路由为 '/'，可根据实际项目调整
  router.push('/')
}
</script>

<style scoped>
/* 全局容器 */
.feedback-container {
  width: 100%;
  max-width: 800px;
  margin: 50px auto;
  padding: 0 20px;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  box-sizing: border-box;
}

/* 页面标题 */
.feedback-title {
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
  text-align: center;
  margin-bottom: 30px;
}

/* 反馈卡片 */
.feedback-card {
  background-color: #fff;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
}

/* 表单样式 */
.feedback-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 16px;
  font-weight: 500;
  color: #495057;
}

.required {
  color: #dc3545;
}

.form-control {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 16px;
  color: #495057;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-control::placeholder {
  color: #adb5bd;
}

/* 按钮组 */
.btn-group {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 10px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-back {
  background-color: #e9ecef;
  color: #495057;
}

.btn-back:hover {
  background-color: #dee2e6;
}

.btn-submit {
  background-color: #007bff;
  color: #fff;
}

.btn-submit:disabled {
  background-color: #6ea8fe;
  cursor: not-allowed;
}

.btn-submit:hover:not(:disabled) {
  background-color: #0056b3;
}

/* 提交成功弹窗 */
.success-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.success-content {
  background-color: #fff;
  padding: 40px;
  border-radius: 12px;
  text-align: center;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 5px 30px rgba(0, 0, 0, 0.2);
}

.success-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.success-title {
  font-size: 24px;
  font-weight: bold;
  color: #28a745;
  margin-bottom: 15px;
}

.success-desc {
  font-size: 18px;
  color: #495057;
  margin-bottom: 30px;
  line-height: 1.6;
}

.btn-home {
  background-color: #007bff;
  color: #fff;
  padding: 12px 30px;
}

.btn-home:hover {
  background-color: #0056b3;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .feedback-title {
    font-size: 24px;
  }
  
  .feedback-card {
    padding: 25px 20px;
  }
  
  .form-control {
    font-size: 14px;
    padding: 10px 12px;
  }
  
  .btn-group {
    flex-direction: column;
    justify-content: center;
  }
  
  .btn {
    width: 100%;
    padding: 10px 20px;
  }
  
  .success-icon {
    font-size: 50px;
  }
  
  .success-title {
    font-size: 20px;
  }
  
  .success-desc {
    font-size: 16px;
  }
}
</style>