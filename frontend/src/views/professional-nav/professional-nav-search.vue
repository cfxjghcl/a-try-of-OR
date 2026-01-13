<template>
  <div class="search-result-page">
    <!-- 搜索条件展示 -->
    <div class="search-condition">
      <h2>搜索结果：{{ searchKeyword }}</h2>
      <button @click="$router.go(-1)" class="back-btn">返回</button>
    </div>

    <!-- 搜索结果列表 -->
    <div class="result-list">
      <!-- 匹配到的结果 -->
      <div v-if="resultList.length > 0" class="result-items">
        <div 
          v-for="item in resultList" 
          :key="item.id" 
          class="result-item"
          @click="goToDetail(item)"
        >
          <h3 class="item-title">{{ item.name }}</h3>
          <p class="item-type">[{{ item.type }}]</p>
          <p class="item-desc" v-if="item.desc">{{ item.desc }}</p>
          <p class="item-salary" v-if="item.averageSalary">平均薪资：{{ item.averageSalary }}元/月</p>
          <p class="item-employment" v-if="item.employmentRate">就业率：{{ item.employmentRate }}%</p>
        </div>
      </div>

      <!-- 无匹配结果 -->
      <div v-else class="empty-result">
        <p>未找到「{{ searchKeyword }}」相关的职业/专业/技能</p>
        <button @click="clearSearch" class="clear-btn">清空关键词重新搜索</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 搜索关键词（从路由参数获取）
const searchKeyword = ref(route.query.keyword || '')

// 全量数据（整合职业/专业/技能，可后续对接后端）
const allData = ref([
  // 专业数据
  { id: 1, name: '计算机科学与技术', type: '专业', category: '工学', employmentRate: 95, averageSalary: 8000 },
  { id: 2, name: '软件工程', type: '专业', category: '工学', employmentRate: 93, averageSalary: 8500 },
  { id: 3, name: '数据科学与大数据技术', type: '专业', category: '工学', employmentRate: 90, averageSalary: 9000 },
  // 职业数据
  { id: 4, name: '前端开发工程师', type: '职业', desc: '市场需求大，入门快', averageSalary: 9000 },
  { id: 5, name: 'Python后端开发工程师', type: '职业', desc: '数据分析/后端开发必备', averageSalary: 10000 },
  { id: 6, name: '大数据工程师', type: '职业', desc: '薪资高，就业前景好', averageSalary: 12000 },
  // 技能数据
  { id: 7, name: 'Python技能', type: '技能', desc: '数据分析必备，薪资可观' },
  { id: 8, name: 'MySQL数据库', type: '技能', desc: '后端/数据分析核心技能' },
  { id: 9, name: 'Vue.js', type: '技能', desc: '前端主流框架，就业面广' }
])

// 搜索结果列表
const resultList = ref([])

// 页面加载时筛选数据
onMounted(() => {
  filterData()
})

// 根据关键词筛选数据
const filterData = () => {
  if (!searchKeyword.value.trim()) {
    resultList.value = []
    return
  }
  // 模糊匹配：名称/类型包含关键词
  resultList.value = allData.value.filter(item => 
    item.name.toLowerCase().includes(searchKeyword.value.trim().toLowerCase()) ||
    item.type.toLowerCase().includes(searchKeyword.value.trim().toLowerCase())
  )
}

// 跳转到详情页
const goToDetail = (item) => {
  let path = ''
  switch (item.type) {
    case '专业':
      path = `/professional-nav/major?id=${item.id}`
      break
    case '职业':
      path = `/professional-nav/career?id=${item.id}`
      break
    case '技能':
      path = `/professional-nav/skill?id=${item.id}`
      break
    default:
      path = '/professional-nav'
  }
  router.push(path)
}

// 清空关键词
const clearSearch = () => {
  searchKeyword.value = ''
  resultList.value = []
  router.push({ path: '/professional-nav/search', query: { keyword: '' } })
}
</script>

<style scoped>
.search-result-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.search-condition {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #007bff;
}

.back-btn, .clear-btn {
  padding: 8px 16px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.back-btn:hover, .clear-btn:hover {
  background-color: #0069d9;
}

.result-list {
  width: 100%;
}

.result-items {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.result-item {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 20px;
  cursor: pointer;
  transition: transform 0.2s;
}

.result-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.item-title {
  font-size: 18px;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.item-type {
  font-size: 12px;
  color: #666;
  background-color: #e9ecef;
  padding: 2px 8px;
  border-radius: 12px;
  display: inline-block;
  margin-bottom: 10px;
}

.item-desc, .item-salary, .item-employment {
  font-size: 14px;
  color: #666;
  margin: 5px 0;
}

.empty-result {
  text-align: center;
  padding: 50px 0;
  color: #999;
}

.clear-btn {
  margin-top: 20px;
}
</style>