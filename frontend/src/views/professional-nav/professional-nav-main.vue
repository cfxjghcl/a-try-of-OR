<template>
  <div class="main-container">
    <!-- 顶部导航区 -->
    <header class="header">
      <div class="header-left">
        <h1 class="logo">OpenDigger 职业导航平台</h1>
      </div>
      <div class="header-middle">
        <div class="search-box">
          <input 
            v-model="searchKey" 
            type="text" 
            placeholder="搜索专业/职业/技能..." 
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch">搜索</button>
        </div>
      </div>
      <div class="header-right">
        <button @click="openCollectModal" class="user-btn">我的收藏</button>
        <button @click="openHistoryModal" class="user-btn">历史记录</button>
        <button 
          v-if="!isLogin" 
          @click="$router.push('/professional-nav/login')" 
          class="login-btn"
        >
          登录
        </button>
        <span v-else class="user-name">{{ userName }}</span>
      </div>
    </header>

    <!-- 滚动公告栏 -->
    <div class="notice-bar">
      <marquee behavior="scroll" direction="left" scrollamount="5">
        {{ noticeContent }}
      </marquee>
    </div>

<!-- 主体内容区 -->
<main class="content">
  <!-- 侧边菜单（子页面入口） -->
  <aside class="sidebar">
    <ul class="menu-list">
      <li @click="$router.push('/professional-nav/intro')" class="menu-item">网页介绍</li>
      <li @click="$router.push('/professional-nav/career')" class="menu-item">职业详情</li>
      <li @click="$router.push('/professional-nav/major')" class="menu-item">专业详情</li>
      <li @click="$router.push('/professional-nav/skill')" class="menu-item">技能详情</li>
      <li @click="$router.push('/professional-nav/market')" class="menu-item">市场职业需求</li>
      <li @click="$router.push('/professional-nav/feedback')" class="menu-item">建议与反馈</li>
    </ul>
  </aside>

  <!-- 核心内容：新增 router-view 用于渲染子页面 + 保留原有主内容 -->
  <div class="content-main">
    <!-- 子页面渲染容器：点击侧边菜单/登录按钮时，子页面会显示在这里 -->
    <router-view v-slot="{ Component }">
      <component :is="Component" v-if="Component" />
      <!-- 没有子页面时，显示原有热门专业/为你推荐内容 -->
      <div v-else>
        <!-- 热门专业模块（对接后端） -->
        <section class="hot-major">
          <h2 class="section-title">热门专业</h2>
          <div class="major-card-list">
            <div 
              v-for="major in hotMajorList" 
              :key="major.id" 
              class="major-card"
              @click="goToMajorDetail(major.id)"
            >
              <h3 class="major-name">{{ major.name }}</h3>
              <p class="major-category">所属大类：{{ major.category }}</p>
              <p class="major-employment">就业率：{{ major.employmentRate }}%</p>
              <p class="major-salary">平均薪资：{{ major.averageSalary }}元/月</p>
            </div>
            <div v-if="hotMajorList.length === 0" class="empty-tip">暂无热门专业数据</div>
          </div>
        </section>

        <!-- 为你推荐模块 -->
        <section class="recommend">
          <h2 class="section-title">为你推荐</h2>
          <div class="recommend-list">
            <div 
              v-for="item in recommendList" 
              :key="item.id" 
              class="recommend-item"
              @click="handleRecommendClick(item.type, item.id)"
            >
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </section>
      </div>
    </router-view>
  </div>
</main>

    <!-- 我的收藏弹窗 -->
    <div class="modal-mask" v-if="showCollectModal" @click="closeCollectModal">
      <div class="modal-content" @click.stop>
        <h3 class="modal-title">我的收藏</h3>
        <button class="close-btn" @click="closeCollectModal">×</button>
        <div class="collect-list">
          <div v-for="item in collectList" :key="item.id" class="collect-item">
            <span>{{ item.name }}</span>
            <button @click="removeCollect(item.id)">取消收藏</button>
          </div>
          <div v-if="collectList.length === 0" class="empty-tip">暂无收藏内容</div>
        </div>
      </div>
    </div>

    <!-- 历史记录弹窗 -->
    <div class="modal-mask" v-if="showHistoryModal" @click="closeHistoryModal">
      <div class="modal-content" @click.stop>
        <h3 class="modal-title">历史记录</h3>
        <button class="close-btn" @click="closeHistoryModal">×</button>
        <div class="history-list">
          <div v-for="(item, index) in historyList" :key="index" class="history-item">
            <span>{{ item.content }} - {{ item.time }}</span>
          </div>
          <div v-if="historyList.length === 0" class="empty-tip">暂无浏览记录</div>
        </div>
      </div>
    </div>

    <!-- 底部版权区 -->
    <footer class="footer">
      <p>© 2026 高雅人士小组 版权所有</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
// 引入封装的axios请求工具（后续对接后端）
//import request from '@/utils/request'

// 路由实例
const router = useRouter()

// 响应式数据
const searchKey = ref('') // 搜索关键词
const isLogin = ref(localStorage.getItem('userLogin') === 'true') // 登录状态
const userName = ref(localStorage.getItem('userName') || '未登录') // 用户名
const noticeContent = ref('欢迎使用OpenDigger职业导航平台！数据来源：OpenDigger开源项目，实时更新职业/专业相关数据～') // 公告内容
const hotMajorList = ref([]) // 热门专业列表（对接后端）
const recommendList = ref([ // 为你推荐列表（可后续对接后端）
  { id: 1, title: '计算机科学与技术', desc: '热门专业，就业面广', type: 'major' },
  { id: 2, title: '前端开发工程师', desc: '市场需求大，入门快', type: 'career' },
  { id: 3, title: 'Python技能', desc: '数据分析必备，薪资可观', type: 'skill' }
])
// 弹窗控制
const showCollectModal = ref(false)
const showHistoryModal = ref(false)
// 收藏/历史记录（模拟数据，后续可对接后端）
const collectList = ref(JSON.parse(localStorage.getItem('collectList')) || [])
const historyList = ref(JSON.parse(localStorage.getItem('historyList')) || [])

// 生命周期：页面加载时获取热门专业数据
onMounted(() => {
  getHotMajorList()
})

// 直接加载模拟的热门专业数据（无需对接接口）
const getHotMajorList = () => {  // ✅ 用 { 大括号
hotMajorList.value = [ 
{ id: 1, name: '计算机科学与技术', category: '工学', employmentRate: 95, averageSalary: 8000 },
{ id: 2, name: '软件工程', category: '工学', employmentRate: 93, averageSalary: 8500 },
{ id: 3, name: '数据科学与大数据技术', category: '工学', employmentRate: 90, averageSalary: 9000 }
]
}  // ✅ 用 } 大括号
// 搜索功能
// 搜索功能
const handleSearch = () => {
  if (!searchKey.value) {
    alert('请输入搜索关键词')
    return
  }
  // 记录搜索历史
  addHistory(`搜索：${searchKey.value}`)
  // 跳转到搜索结果页，并传递关键词
  router.push({ 
    path: '/professional-nav/search', 
    query: { keyword: searchKey.value } 
  })
}

// 跳转到专业详情页
const goToMajorDetail = (majorId) => {
  addHistory(`查看专业：${hotMajorList.value.find(item => item.id === majorId)?.name}`)
  router.push({ path: '/professional-nav/major', query: { id: majorId } })
}

// 为你推荐项点击
const handleRecommendClick = (type, id) => {
  let path = ''
  let historyContent = ''
  switch (type) {
    case 'major':
      path = `/professional-nav/major?id=${id}`
      historyContent = `查看推荐专业：${recommendList.value.find(item => item.id === id)?.title}`
      break
    case 'career':
      path = `/professional-nav/career?id=${id}`
      historyContent = `查看推荐职业：${recommendList.value.find(item => item.id === id)?.title}`
      break
    case 'skill':
      path = `/professional-nav/skill?id=${id}`
      historyContent = `查看推荐技能：${recommendList.value.find(item => item.id === id)?.title}`
      break
  }
  addHistory(historyContent)
  router.push(path)
}

// 新增：跳转到登录页
const goToLogin = () => {
  console.log('点击了登录按钮，准备跳转') // 调试用
  router.push({ 
    path: '/professional-nav/login' 
  }).catch(err => {
    console.error('跳转失败：', err) // 打印错误原因
  })
}

// 打开/关闭收藏弹窗
const openCollectModal = () => {
  if (!isLogin.value) {
    alert('请先登录后查看收藏！')
    router.push('/professional-nav/login')
    return
  }
  showCollectModal.value = true
}
const closeCollectModal = () => {
  showCollectModal.value = false
}

// 打开/关闭历史记录弹窗
const openHistoryModal = () => {
  if (!isLogin.value) {
    alert('请先登录后查看历史！')
    router.push('/professional-nav/login')
    return
  }
  showHistoryModal.value = true
}
const closeHistoryModal = () => {
  showHistoryModal.value = false
}

// 添加历史记录
const addHistory = (content) => {
  if (!isLogin.value) return
  const now = new Date()
  const time = `${now.getFullYear()}-${(now.getMonth()+1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  historyList.value.unshift({ content, time })
  // 只保留最近20条记录
  if (historyList.value.length > 20) {
    historyList.value = historyList.value.slice(0, 20)
  }
  localStorage.setItem('historyList', JSON.stringify(historyList.value))
}

// 移除收藏
const removeCollect = (id) => {
  collectList.value = collectList.value.filter(item => item.id !== id)
  localStorage.setItem('collectList', JSON.stringify(collectList.value))
}
</script>

<style scoped>
/* 全局样式（亮色主题） */
.main-container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background-color: #f8f9fa;
}

/* 顶部导航 */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  border-bottom: 1px solid #e9ecef;
}
.logo {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}
.search-box {
  display: flex;
  width: 400px;
}
.search-box input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ced4da;
  border-radius: 4px 0 0 4px;
  outline: none;
  font-size: 14px;
}
.search-box button {
  padding: 0 20px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}
.search-box button:hover {
  background-color: #0069d9;
}
.user-btn {
  padding: 8px 16px;
  margin-right: 10px;
  background-color: #6c757d;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.user-btn:hover {
  background-color: #5a6268;
}
.login-btn {
  padding: 8px 20px;
  background-color: #28a745;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.login-btn:hover {
  background-color: #218838;
}
.user-name {
  margin-left: 10px;
  font-weight: 500;
  color: #2c3e50;
}

/* 滚动公告栏 */
.notice-bar {
  height: 40px;
  line-height: 40px;
  background-color: #e8f4f8;
  color: #007bff;
  padding: 0 20px;
  margin: 10px 0;
  border-radius: 4px;
  overflow: hidden;
}

/* 主体内容 */
.content {
  display: flex;
  gap: 20px;
  margin: 20px 0;
}

/* 侧边菜单 */
.sidebar {
  width: 200px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 10px 0;
}
.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.menu-item {
  padding: 12px 20px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}
.menu-item:hover {
  background-color: #e8f4f8;
  color: #007bff;
}

/* 核心内容区 */
.content-main {
  flex: 1;
}
.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 2px solid #007bff;
}

/* 热门专业卡片 */
.major-card-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
.major-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 20px;
  cursor: pointer;
  transition: transform 0.2s;
}
.major-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}
.major-name {
  font-size: 18px;
  color: #2c3e50;
  margin: 0 0 10px 0;
}
.major-category, .major-employment, .major-salary {
  font-size: 14px;
  color: #666;
  margin: 5px 0;
}

/* 为你推荐 */
.recommend-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 15px;
}
.recommend-item {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 15px;
  cursor: pointer;
}
.recommend-item h3 {
  font-size: 16px;
  color: #2c3e50;
  margin: 0 0 8px 0;
}
.recommend-item p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 弹窗样式 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  width: 500px;
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  position: relative;
}
.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 15px 0;
}
.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  border: none;
  background-color: transparent;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}
.collect-list, .history-list {
  max-height: 400px;
  overflow-y: auto;
}
.collect-item, .history-item {
  padding: 10px 0;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.collect-item button {
  padding: 4px 8px;
  background-color: #dc3545;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.empty-tip {
  text-align: center;
  padding: 20px 0;
  color: #999;
  font-size: 14px;
}

/* 底部版权 */
.footer {
  text-align: center;
  padding: 20px 0;
  border-top: 1px solid #e9ecef;
  margin-top: 30px;
  color: #666;
  font-size: 14px;
}

/* 通用样式 */
button {
  transition: background-color 0.2s;
}
</style>