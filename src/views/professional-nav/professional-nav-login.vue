<template>
  <div class="login-container">
    <!-- 页面标题 -->
    <div class="login-title">OpenDigger 职业导航平台</div>

    <!-- 动态切换的表单容器 -->
    <div class="form-box">
      <!-- 1. 登录表单（默认显示） -->
      <form v-show="currentForm === 'login'" @submit.prevent="handleLogin">
        <div class="form-item">
          <label class="form-label">账号</label>
          <input 
            v-model="loginForm.account" 
            type="text" 
            placeholder="请输入账号" 
            class="form-input"
            required
          />
        </div>
        <div class="form-item">
          <label class="form-label">密码</label>
          <input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码（8~16位，含数字和字母）" 
            class="form-input"
            required
          />
        </div>
        <!-- 登录密码错误提示 -->
        <div v-show="loginPwdError" class="error-text">{{ loginPwdError }}</div>
        <button type="submit" class="submit-btn">登录</button>
        <button type="button" @click="$router.push('/professional-nav')" class="back-btn">返回首页</button>
        
        <!-- 底部注册/忘记密码跳转链接 -->
        <div class="form-footer">
          <span @click="currentForm = 'forgetVerify'" class="link-text">忘记密码？</span>
          <span @click="currentForm = 'register'" class="link-text">还没有账号？立即注册</span>
        </div>
      </form>

      <!-- 2. 注册表单 -->
      <form v-show="currentForm === 'register'" @submit.prevent="handleRegister">
        <div class="form-item">
          <label class="form-label">姓名</label>
          <input 
            v-model="registerForm.name" 
            type="text" 
            placeholder="请输入姓名" 
            class="form-input"
            required
          />
        </div>
        <div class="form-item">
          <label class="form-label">所属院校</label>
          <input 
            v-model="registerForm.school" 
            type="text" 
            placeholder="请输入院校名称" 
            class="form-input"
            required
          />
        </div>
        <div class="form-item">
          <label class="form-label">专业</label>
          <input 
            v-model="registerForm.major" 
            type="text" 
            placeholder="请输入专业名称" 
            class="form-input"
            required
          />
        </div>
        <div class="form-item">
          <label class="form-label">账号</label>
          <input 
            v-model="registerForm.account" 
            type="text" 
            placeholder="请设置登录账号" 
            class="form-input"
            required
          />
        </div>
        <div class="form-item">
          <label class="form-label">密码</label>
          <input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="请设置密码（8~16位，含数字和字母）" 
            class="form-input"
            required
          />
        </div>
        <div class="form-item">
          <label class="form-label">确认密码</label>
          <input 
            v-model="registerForm.confirmPwd" 
            type="password" 
            placeholder="请再次输入密码" 
            class="form-input"
            required
          />
        </div>
        <!-- 注册密码错误提示 -->
        <div v-show="registerPwdError" class="error-text">{{ registerPwdError }}</div>
        <button type="submit" class="submit-btn">注册</button>
        <button type="button" @click="currentForm = 'login'" class="back-btn">返回登录</button>
      </form>

      <!-- 3. 忘记密码-身份验证表单 -->
      <form v-show="currentForm === 'forgetVerify'" @submit.prevent="handleForgetVerify">
        <div class="form-item">
          <label class="form-label">账号</label>
          <input 
            v-model="forgetVerifyForm.account" 
            type="text" 
            placeholder="请输入注册时的账号" 
            class="form-input"
            required
          />
        </div>
        <div class="form-item">
          <label class="form-label">姓名</label>
          <input 
            v-model="forgetVerifyForm.name" 
            type="text" 
            placeholder="请输入注册时的姓名" 
            class="form-input"
            required
          />
        </div>
        <!-- 身份验证错误提示 -->
        <div v-show="verifyError" class="error-text">{{ verifyError }}</div>
        <button type="submit" class="submit-btn">验证身份</button>
        <button type="button" @click="currentForm = 'login'" class="back-btn">返回登录</button>
      </form>

      <!-- 4. 忘记密码-重置密码表单 -->
      <form v-show="currentForm === 'forgetReset'" @submit.prevent="handleForgetReset">
        <div class="form-item">
          <label class="form-label">新密码</label>
          <input 
            v-model="forgetResetForm.newPwd" 
            type="password" 
            placeholder="请设置新密码（8~16位，含数字和字母）" 
            class="form-input"
            required
          />
        </div>
        <div class="form-item">
          <label class="form-label">确认新密码</label>
          <input 
            v-model="forgetResetForm.confirmNewPwd" 
            type="password" 
            placeholder="请再次输入新密码" 
            class="form-input"
            required
          />
        </div>
        <!-- 重置密码错误提示 -->
        <div v-show="resetError" class="error-text">{{ resetError }}</div>
        <button type="submit" class="submit-btn">确认重置</button>
        <button type="button" @click="currentForm = 'forgetVerify'" class="back-btn">返回验证</button>
      </form>
    </div>

    <!-- 底部版权 -->
    <div class="login-footer">© 2026 高雅人士小组 版权所有</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// 创建axios实例（统一配置）
const request = axios.create({
  // 保留你的后端地址（正确）
  baseURL: 'http://127.0.0.1:5000/api', 
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  },
  // 【修改1】：新增withCredentials，解决跨域cookie传递
  withCredentials: true
})

// 请求拦截器：添加token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      // 【修改2】：去掉Bearer前缀，后端直接读取token
      config.headers.Authorization = token
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一处理错误
request.interceptors.response.use(
  (response) => {
    const res = response.data
    // 【修改3】：兼容200和201状态码（注册成功返回201）
    if (res.code !== 200 && res.code !== 201) {
      return Promise.reject(new Error(res.msg || '请求失败'))
    }
    return res
  },
  (error) => {
    // 【修改4】：更精准的错误提示，适配后端返回格式
    let errorMsg = '网络异常，请稍后重试'
    if (error.response) {
      // 后端返回的错误信息
      errorMsg = error.response.data?.msg || `请求失败（${error.response.status}）`
      // 401单独提示登录失效
      if (error.response.status === 401) {
        errorMsg = '登录状态失效，请重新登录'
        // 清空失效的token
        localStorage.removeItem('token')
        localStorage.removeItem('userLogin')
      }
    } else if (error.message.includes('Network Error')) {
      errorMsg = '连接后端失败，请检查：1.后端是否启动 2.地址/端口是否正确'
    }
    return Promise.reject(new Error(errorMsg))
  }
)

// 切换表单：login-登录 register-注册 forgetVerify-身份验证 forgetReset-重置密码
const currentForm = ref('login')

// 1. 登录表单数据
const loginForm = ref({
  account: '',
  password: ''
})
const loginPwdError = ref('') // 登录密码格式错误提示

// 2. 注册表单数据
const registerForm = ref({
  name: '',
  school: '',
  major: '',
  account: '',
  password: '',
  confirmPwd: ''
})
const registerPwdError = ref('') // 注册密码格式错误提示

// 3. 忘记密码-身份验证表单数据
const forgetVerifyForm = ref({
  account: '',
  name: ''
})
const verifyError = ref('') // 身份验证错误提示

// 4. 忘记密码-重置密码表单数据
const forgetResetForm = ref({
  newPwd: '',
  confirmNewPwd: ''
})
const resetError = ref('') // 重置密码错误提示

// 密码格式校验函数（核心：8~16位，同时包含数字和字母）
const checkPwdFormat = (pwd) => {
  // 正则：8-16位，包含至少1个数字和1个字母
  const pwdReg = /^(?=.*[0-9])(?=.*[a-zA-Z]).{8,16}$/
  if (!pwdReg.test(pwd)) {
    return '密码必须为8~16位，且同时包含数字和字母！'
  }
  return '' // 校验通过返回空
}

// 登录处理（调用后端接口）
const handleLogin = async () => {
  // 清空之前的错误提示
  loginPwdError.value = ''
  
  if (!loginForm.value.account || !loginForm.value.password) {
    loginPwdError.value = '账号和密码不能为空！'
    return
  }

  // 校验密码格式
  const pwdError = checkPwdFormat(loginForm.value.password)
  if (pwdError) {
    loginPwdError.value = pwdError
    return
  }

  try {
    // 【修改5】：适配后端登录参数（后端接收username，不是account）
    const res = await request.post('/auth/login', {
      username: loginForm.value.account, // 关键：account改为username
      password: loginForm.value.password
    })
    // 登录成功 - 保留你的存储逻辑，补充token存储
    localStorage.setItem('userLogin', 'true')
    localStorage.setItem('userName', res.data.name || loginForm.value.account)
    localStorage.setItem('token', res.data.token) // 保存后端返回的token
    alert('登录成功！')
    router.push('/professional-nav')
  } catch (error) {
    loginPwdError.value = error.message
  }
}

// 注册处理（调用后端接口）
const handleRegister = async () => {
  // 清空之前的错误提示
  registerPwdError.value = ''
  
  const { name, school, major, account, password, confirmPwd } = registerForm.value
  // 表单非空校验
  if (!name || !school || !major || !account || !password || !confirmPwd) {
    registerPwdError.value = '所有字段不能为空！'
    return
  }

  // 校验密码格式
  const pwdError = checkPwdFormat(password)
  if (pwdError) {
    registerPwdError.value = pwdError
    return
  }

  // 密码一致性校验
  if (password !== confirmPwd) {
    registerPwdError.value = '两次输入的密码不一致！'
    return
  }

  try {
    // 【修改6】：适配后端注册参数（username+email，补充email字段）
    await request.post('/auth/register', {
      username: account, // 账号对应后端的username
      email: `${account}@example.com`, // 后端需要email，临时拼接（可让用户输入）
      password: password,
      name: name,
      major: major,
      school: school
    })
    alert('注册成功！请返回登录页登录')
    currentForm.value = 'login'
    // 清空注册表单
    registerForm.value = {
      name: '',
      school: '',
      major: '',
      account: '',
      password: '',
      confirmPwd: ''
    }
  } catch (error) {
    registerPwdError.value = error.message
  }
}

// 忘记密码-身份验证处理（后端暂未实现，先做前端提示）
const handleForgetVerify = async () => {
  const { account, name } = forgetVerifyForm.value
  // 清空之前的错误提示
  verifyError.value = ''
  
  // 非空校验
  if (!account || !name) {
    verifyError.value = '账号和姓名不能为空！'
    return
  }
  
  try {
    // 【备注】：后端暂未实现忘记密码接口，先模拟成功
    // await request.post('/auth/forget/verify', { account, name })
    alert('身份验证成功！即将跳转到重置密码页面')
    // 验证成功，跳转到重置密码页面
    currentForm.value = 'forgetReset'
    // 清空验证表单
    forgetVerifyForm.value = { account: '', name: '' }
  } catch (error) {
    verifyError.value = error.message
  }
}

// 忘记密码-重置密码处理（后端暂未实现，先做前端提示）
const handleForgetReset = async () => {
  const { newPwd, confirmNewPwd } = forgetResetForm.value
  // 清空之前的错误提示
  resetError.value = ''
  
  // 非空校验
  if (!newPwd || !confirmNewPwd) {
    resetError.value = '新密码和确认密码不能为空！'
    return
  }

  // 校验新密码格式
  const pwdError = checkPwdFormat(newPwd)
  if (pwdError) {
    resetError.value = pwdError
    return
  }
  
  // 密码一致性校验
  if (newPwd !== confirmNewPwd) {
    resetError.value = '两次输入的新密码不一致！'
    return
  }
  
  try {
    // 【备注】：后端暂未实现重置密码接口，先模拟成功
    // await request.post('/auth/forget/reset', { account: forgetVerifyForm.value.account, newPassword: newPwd })
    alert('密码重置成功！请返回登录页登录')
    // 切回登录表单
    currentForm.value = 'login'
    // 清空重置密码表单
    forgetResetForm.value = { newPwd: '', confirmNewPwd: '' }
  } catch (error) {
    resetError.value = error.message
  }
}
</script>

<style scoped>
/* 整体容器 */
.login-container {
  width: 100%;
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
}

/* 页面标题 */
.login-title {
  font-size: 28px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30px;
  color: #2c3e50;
}

/* 表单容器 */
.form-box {
  background-color: #fff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

/* 表单项 */
.form-item {
  margin-bottom: 20px;
}
.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
}
.form-input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  outline: none;
  font-size: 14px;
  box-sizing: border-box;
}
.form-input:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

/* 错误提示 */
.error-text {
  color: #dc3545;
  font-size: 12px;
  margin-bottom: 10px;
  text-align: left;
}

/* 按钮样式 */
.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-bottom: 10px;
}
.submit-btn:hover {
  background-color: #0069d9;
}
.back-btn {
  width: 100%;
  padding: 12px;
  background-color: #6c757d;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-bottom: 15px;
}
.back-btn:hover {
  background-color: #5a6268;
}

/* 登录表单底部链接 */
.form-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  font-size: 14px;
}
.link-text {
  color: #007bff;
  cursor: pointer;
}
.link-text:hover {
  color: #0056b3;
  text-decoration: underline;
}

/* 底部版权 */
.login-footer {
  text-align: center;
  margin-top: 30px;
  color: #666;
  font-size: 14px;
}
</style>