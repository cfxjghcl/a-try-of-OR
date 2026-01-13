<template>
  <div class="career-detail-container">
    <!-- 1. 页面导航栏 -->
    <div class="career-nav">
      <button @click="$router.back()" class="back-btn">← 返回</button>
      <h1 class="career-title">{{ careerInfo.name }} 职业详情</h1>
    </div>

    <!-- 加载中提示 -->
    <div v-if="loading" class="loading">正在加载职业数据...</div>

    <div v-else class="career-content">
      <!-- 2. 职业基础信息卡片 -->
      <div class="career-base-card">
        <div class="base-item">
          <span class="label">所属领域：</span>
          <span class="value">{{ careerInfo.field || "暂无数据" }}</span>
        </div>
        <div class="base-item">
          <span class="label">核心工作内容：</span>
          <span class="value">{{ careerInfo.workContent || "暂无数据" }}</span>
        </div>
        <div class="base-item">
          <span class="label">从业技术门槛：</span>
          <span class="value">{{ careerInfo.techThreshold || "暂无数据" }}</span>
        </div>
      </div>

      <!-- 3. OpenDigger数据可视化图表区 -->
      <div class="career-chart-card">
        <h2 class="card-title">职业数据趋势（基于OpenDigger开源数据）</h2>
        
        <!-- 3.1 就业率趋势图 -->
        <div class="chart-item">
          <h3 class="chart-title">近5年就业率变化</h3>
          <div id="employmentRateChart" style="width: 100%; height: 300px;"></div>
        </div>

        <!-- 3.2 薪资趋势图 -->
        <div class="chart-item">
          <h3 class="chart-title">近5年平均薪资变化（元/月）</h3>
          <div id="salaryChart" style="width: 100%; height: 300px;"></div>
        </div>

        <!-- 3.3 职业稳定性趋势图 -->
        <div class="chart-item">
          <h3 class="chart-title">近5年职业稳定性评分（0-100）</h3>
          <div id="stabilityChart" style="width: 100%; height: 300px;"></div>
        </div>
      </div>

      <!-- 4. 星级评分区（新增综合评分） -->
      <div class="career-rating-card">
        <h2 class="card-title">职业综合评分</h2>
        <div class="rating-list">
          <!-- 就业率星级 -->
          <div class="rating-item">
            <span class="rating-label">就业率：</span>
            <div class="star-container">
              <span 
                v-for="i in 5" 
                :key="`employment-${i}`" 
                class="star"
                :class="{ active: i <= careerRating.employmentRate }"
              >★</span>
            </div>
            <span class="rating-desc">{{ getRatingDesc(careerRating.employmentRate) }}</span>
          </div>

          <!-- 薪资星级 -->
          <div class="rating-item">
            <span class="rating-label">薪资水平：</span>
            <div class="star-container">
              <span 
                v-for="i in 5" 
                :key="`salary-${i}`" 
                class="star"
                :class="{ active: i <= careerRating.salary }"
              >★</span>
            </div>
            <span class="rating-desc">{{ getRatingDesc(careerRating.salary) }}</span>
          </div>

          <!-- 难度（技术门槛）星级 -->
          <div class="rating-item">
            <span class="rating-label">从业难度：</span>
            <div class="star-container">
              <span 
                v-for="i in 5" 
                :key="`difficulty-${i}`" 
                class="star"
                :class="{ active: i <= careerRating.difficulty }"
              >★</span>
            </div>
            <span class="rating-desc">{{ getDifficultyDesc(careerRating.difficulty) }}</span>
          </div>

          <!-- 新增：综合评分星级 -->
          <div class="rating-item total-rating">
            <span class="rating-label">综合评分：</span>
            <div class="star-container">
              <span 
                v-for="i in 5" 
                :key="`total-${i}`" 
                class="star"
                :class="{ active: i <= totalRating }"
              >★</span>
            </div>
            <span class="rating-desc">{{ getRatingDesc(Math.round(totalRating)) }}（平均{{ totalRating.toFixed(1) }}星）</span>
          </div>
        </div>
      </div>

      <!-- 5. 职业发展建议 -->
      <div class="career-suggest-card">
        <h2 class="card-title">职业发展建议</h2>
        <ul class="suggest-list">
          <li v-for="(item, index) in careerSuggest" :key="index">{{ item }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'

// 初始化路由和参数
const router = useRouter()
const route = useRoute()
const careerId = route.params.id // 获取职业ID
const loading = ref(true) // 加载状态

// 图表实例（用于销毁，防止内存泄漏）
let employmentRateChart = null
let salaryChart = null
let stabilityChart = null

// 1. 职业基础信息
const careerInfo = ref({
  name: '', // 职业名称
  field: '', // 所属领域
  workContent: '', // 核心工作内容
  techThreshold: '' // 从业技术门槛
})

// 2. OpenDigger数据（可视化用）
const careerData = ref({
  years: ['2020', '2021', '2022', '2023', '2024'], // 近5年
  employmentRate: [85, 88, 86, 90, 92], // 就业率（%）
  salary: [12000, 13500, 14800, 15500, 16800], // 平均薪资（元/月）
  stability: [80, 82, 85, 83, 88] // 稳定性评分（0-100）
})

// 3. 星级评分（1-5星）
const careerRating = ref({
  employmentRate: 4, // 就业率星级
  salary: 4, // 薪资星级
  difficulty: 3 // 从业难度星级
})

// 4. 新增：计算综合评分（平均值，保留1位小数）
const totalRating = computed(() => {
  const { employmentRate, salary, difficulty } = careerRating.value
  // 取三个维度的平均值
  const average = (employmentRate + salary + difficulty) / 3
  return Number(average.toFixed(1)) // 保留1位小数
})

// 5. 职业发展建议
const careerSuggest = ref([])

// 星级描述计算
const getRatingDesc = (star) => {
  const descMap = {
    1: '极低',
    2: '较低',
    3: '中等',
    4: '较高',
    5: '极高'
  }
  return descMap[star] || '中等'
}

// 难度描述计算
const getDifficultyDesc = (star) => {
  const descMap = {
    1: '极低',
    2: '较低',
    3: '中等',
    4: '较高',
    5: '极高'
  }
  return descMap[star] || '中等'
}

// 6. 模拟调用OpenDigger API获取职业数据
const getCareerData = async () => {
  try {
    loading.value = true
    // 模拟接口请求延迟
    await new Promise(resolve => setTimeout(resolve, 800))

    // 模拟OpenDigger返回的职业数据（真实项目替换为API请求）
    const openDiggerMockData = {
      careerInfo: {
        name: 'Python后端开发工程师',
        field: '计算机/互联网/软件',
        workContent: '负责后端服务开发、接口设计、数据库优化、项目部署维护等',
        techThreshold: '掌握Python核心语法、至少1个后端框架（Django/Flask/FastAPI）、MySQL/Redis、Linux基础'
      },
      careerData: {
        years: ['2020', '2021', '2022', '2023', '2024'],
        employmentRate: [85, 88, 86, 90, 92],
        salary: [12000, 13500, 14800, 15500, 16800],
        stability: [80, 82, 85, 83, 88]
      },
      careerRating: {
        employmentRate: 4, // 就业率：较高
        salary: 4, // 薪资：较高
        difficulty: 3 // 难度：中等
      },
      careerSuggest: [
        '优先掌握Python3.x核心语法，熟练使用Django/Flask框架开发实战项目',
        '深入学习MySQL优化、Redis缓存、消息队列等中间件技术',
        '参与开源项目积累实战经验，提升代码质量和工程化能力',
        '关注云原生技术（Docker/K8s），掌握项目部署和运维基础',
        '定期刷题提升算法能力，重点关注后端面试高频考点'
      ]
    }

    // 赋值到页面数据
    careerInfo.value = openDiggerMockData.careerInfo
    careerData.value = openDiggerMockData.careerData
    careerRating.value = openDiggerMockData.careerRating
    careerSuggest.value = openDiggerMockData.careerSuggest

    // 初始化所有图表
    initEmploymentRateChart()
    initSalaryChart()
    initStabilityChart()
  } catch (error) {
    console.error('获取职业数据失败：', error)
    alert('数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 7. 初始化就业率趋势图
const initEmploymentRateChart = () => {
  const chartDom = document.getElementById('employmentRateChart')
  if (!chartDom) return
  
  employmentRateChart = echarts.init(chartDom)
  const option = {
    title: { text: '近5年就业率变化趋势', left: 'center' },
    tooltip: { trigger: 'axis', formatter: '{b}年：{c}%' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: careerData.value.years
    },
    yAxis: {
      type: 'value',
      min: 70,
      max: 100,
      axisLabel: { formatter: '{value}%' }
    },
    series: [
      {
        name: '就业率',
        type: 'line',
        smooth: true,
        data: careerData.value.employmentRate,
        itemStyle: { color: '#28a745' },
        areaStyle: { color: 'rgba(40, 167, 69, 0.1)' },
        markLine: { data: [{ type: 'average', name: '平均值' }] }
      }
    ]
  }
  employmentRateChart.setOption(option)
  window.addEventListener('resize', resizeCharts)
}

// 8. 初始化薪资趋势图
const initSalaryChart = () => {
  const chartDom = document.getElementById('salaryChart')
  if (!chartDom) return
  
  salaryChart = echarts.init(chartDom)
  const option = {
    title: { text: '近5年平均薪资变化趋势', left: 'center' },
    tooltip: { trigger: 'axis', formatter: '{b}年：{c} 元/月' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: careerData.value.years
    },
    yAxis: {
      type: 'value',
      min: 10000,
      max: 20000,
      axisLabel: { formatter: '{value} 元' }
    },
    series: [
      {
        name: '平均薪资',
        type: 'bar',
        data: careerData.value.salary,
        itemStyle: { color: '#007bff' },
        label: {
          show: true,
          position: 'top',
          formatter: '{c} 元'
        }
      }
    ]
  }
  salaryChart.setOption(option)
  window.addEventListener('resize', resizeCharts)
}

// 9. 初始化稳定性趋势图
const initStabilityChart = () => {
  const chartDom = document.getElementById('stabilityChart')
  if (!chartDom) return
  
  stabilityChart = echarts.init(chartDom)
  const option = {
    title: { text: '近5年职业稳定性变化趋势', left: 'center' },
    tooltip: { trigger: 'axis', formatter: '{b}年：{c} 分' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: careerData.value.years
    },
    yAxis: {
      type: 'value',
      min: 70,
      max: 100,
      axisLabel: { formatter: '{value} 分' }
    },
    series: [
      {
        name: '稳定性评分',
        type: 'line',
        smooth: true,
        data: careerData.value.stability,
        itemStyle: { color: '#ffc107' },
        areaStyle: { color: 'rgba(255, 193, 7, 0.1)' },
        markPoint: { data: [{ type: 'max', name: '最高' }, { type: 'min', name: '最低' }] }
      }
    ]
  }
  stabilityChart.setOption(option)
  window.addEventListener('resize', resizeCharts)
}

// 10. 图表自适应窗口大小
const resizeCharts = () => {
  employmentRateChart && employmentRateChart.resize()
  salaryChart && salaryChart.resize()
  stabilityChart && stabilityChart.resize()
}

// 11. 生命周期钩子
onMounted(() => {
  getCareerData() // 页面挂载时加载数据
})

onUnmounted(() => {
  // 销毁所有图表实例，防止内存泄漏
  employmentRateChart && employmentRateChart.dispose()
  salaryChart && salaryChart.dispose()
  stabilityChart && stabilityChart.dispose()
  window.removeEventListener('resize', resizeCharts)
})
</script>

<style scoped>
/* 全局容器 */
.career-detail-container {
  width: 90%;
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  box-sizing: border-box;
}

/* 导航栏 */
.career-nav {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}
.back-btn {
  padding: 8px 15px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 20px;
  transition: background-color 0.3s;
}
.back-btn:hover {
  background-color: #0056b3;
}
.career-title {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

/* 加载中 */
.loading {
  text-align: center;
  padding: 50px 0;
  font-size: 16px;
  color: #666;
}

/* 内容容器 */
.career-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 基础信息卡片 */
.career-base-card {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.base-item {
  display: flex;
  margin-bottom: 18px;
  font-size: 16px;
  line-height: 1.6;
}
.base-item:last-child {
  margin-bottom: 0;
}
.label {
  font-weight: bold;
  width: 120px;
  color: #555;
  flex-shrink: 0;
}
.value {
  flex: 1;
  color: #333;
}

/* 图表卡片 */
.career-chart-card {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.card-title {
  font-size: 20px;
  font-weight: bold;
  margin: 0 0 20px 0;
  color: #2c3e50;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}
.chart-item {
  margin-bottom: 30px;
}
.chart-item:last-child {
  margin-bottom: 0;
}
.chart-title {
  font-size: 18px;
  margin: 0 0 15px 0;
  color: #333;
}

/* 星级评分卡片 */
.career-rating-card {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.rating-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.rating-item {
  display: flex;
  align-items: center;
  font-size: 18px;
}
/* 新增：综合评分样式高亮 */
.total-rating {
  border-top: 1px dashed #eee;
  padding-top: 20px;
  margin-top: 10px;
}
.total-rating .rating-label {
  color: #007bff;
  font-weight: bold;
}
.total-rating .star {
  font-size: 28px;
}
.rating-label {
  font-weight: bold;
  width: 100px;
  color: #555;
  flex-shrink: 0;
}
.star-container {
  display: flex;
  gap: 5px;
  margin: 0 15px;
}
.star {
  font-size: 24px;
  color: #ddd;
  transition: color 0.3s;
}
.star.active {
  color: #ffc107;
}
.rating-desc {
  color: #666;
  font-size: 16px;
}

/* 职业建议卡片 */
.career-suggest-card {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.suggest-list {
  padding-left: 20px;
  font-size: 16px;
  line-height: 1.8;
  margin: 0;
  color: #333;
}
.suggest-list li {
  margin-bottom: 10px;
}
.suggest-list li:last-child {
  margin-bottom: 0;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .career-detail-container {
    width: 95%;
    padding: 15px;
  }
  .career-title {
    font-size: 20px;
  }
  .card-title {
    font-size: 18px;
  }
  .chart-title {
    font-size: 16px;
  }
  .base-item {
    flex-direction: column;
    align-items: flex-start;
  }
  .label {
    margin-bottom: 5px;
  }
  .rating-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .star-container {
    margin: 0;
  }
  /* 响应式下综合评分样式适配 */
  .total-rating .star {
    font-size: 24px;
  }
}
</style>