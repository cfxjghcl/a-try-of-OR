<template>
  <div class="market-demand-container">
    <!-- 1. 页面导航栏 -->
    <div class="market-nav">
      <button @click="$router.back()" class="back-btn">← 返回</button>
      <h1 class="market-title">{{ careerInfo.name }} 市场需求分析</h1>
    </div>

    <!-- 加载中提示 -->
    <div v-if="loading" class="loading">正在加载市场需求数据...</div>

    <div v-else class="market-content">
      <!-- 职业基础信息卡片 -->
      <div class="career-base-card">
        <div class="base-item">
          <span class="label">职业名称：</span>
          <span class="value">{{ careerInfo.name || "暂无数据" }}</span>
        </div>
        <div class="base-item">
          <span class="label">所属行业：</span>
          <span class="value">{{ careerInfo.industry || "暂无数据" }}</span>
        </div>
        <div class="base-item">
          <span class="label">全国平均需求量：</span>
          <span class="value">{{ careerInfo.totalDemand }} 个/月</span>
        </div>
        <div class="base-item">
          <span class="label">全国平均就业率：</span>
          <span class="value">{{ careerInfo.totalEmploymentRate }}%</span>
        </div>
      </div>

      <!-- 图表1：一线城市需求量&就业率对比 -->
      <div class="chart-card">
        <h2 class="card-title">一线城市该职业需求与就业率对比（基于OpenDigger数据）</h2>
        <div id="cityDemandChart" style="width: 100%; height: 400px;"></div>
        <div class="chart-note">
          注：需求量单位为「岗位数/月」，就业率为该城市该职业投递者的成功入职比例
        </div>
      </div>

      <!-- 图表2：知名企业该职业需求情况 -->
      <div class="chart-card">
        <h2 class="card-title">全国知名企业该职业需求分布（基于OpenDigger数据）</h2>
        <div id="companyDemandChart" style="width: 100%; height: 400px;"></div>
        <div class="chart-note">
          注：需求占比为该企业该职业岗位数占全国该职业总岗位数的比例
        </div>
      </div>

      <!-- 数据解读与建议 -->
      <div class="analysis-card">
        <h2 class="card-title">数据解读与求职建议</h2>
        <div class="analysis-content">
          <div class="analysis-item">
            <h3 class="item-title">📍 城市选择建议</h3>
            <p>{{ analysis.citySuggest }}</p>
          </div>
          <div class="analysis-item">
            <h3 class="item-title">🏢 企业投递建议</h3>
            <p>{{ analysis.companySuggest }}</p>
          </div>
          <div class="analysis-item">
            <h3 class="item-title">💡 竞争力提升建议</h3>
            <ul class="suggest-list">
              <li v-for="(item, index) in analysis.competitionSuggest" :key="index">{{ item }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'

// 初始化路由和参数
const router = useRouter()
const route = useRoute()
const careerId = route.params.id // 获取职业ID
const loading = ref(true) // 加载状态

// 图表实例（用于销毁，防止内存泄漏）
let cityDemandChart = null
let companyDemandChart = null

// 1. 职业基础信息
const careerInfo = ref({
  name: '', // 职业名称
  industry: '', // 所属行业
  totalDemand: 0, // 全国平均需求量（岗位数/月）
  totalEmploymentRate: 0 // 全国平均就业率（%）
})

// 2. 城市需求&就业率数据
const cityData = ref({
  cities: ['北京', '上海', '广州', '深圳', '杭州'], // 一线城市/新一线核心城市
  demand: [], // 各城市需求量（岗位数/月）
  employmentRate: [] // 各城市就业率（%）
})

// 3. 企业需求数据
const companyData = ref({
  companies: [], // 知名企业名称
  demandRatio: [] // 各企业需求占比（%）
})

// 4. 数据解读与建议
const analysis = ref({
  citySuggest: '',
  companySuggest: '',
  competitionSuggest: []
})

// 5. 模拟调用OpenDigger API获取市场需求数据
const getMarketData = async () => {
  try {
    loading.value = true
    // 模拟接口请求延迟
    await new Promise(resolve => setTimeout(resolve, 800))

    // 模拟OpenDigger返回的市场需求数据（真实项目替换为API请求）
    const openDiggerMockData = {
      careerInfo: {
        name: 'Python后端开发工程师',
        industry: '互联网/软件/IT服务',
        totalDemand: 12500, // 全国月均需求量
        totalEmploymentRate: 88.5 // 全国平均就业率
      },
      cityData: {
        cities: ['北京', '上海', '广州', '深圳', '杭州'],
        demand: [3200, 2800, 1500, 2100, 1800], // 各城市月均需求量（岗位数）
        employmentRate: [89.2, 87.8, 85.5, 90.1, 88.9] // 各城市就业率
      },
      companyData: {
        companies: [
          '阿里巴巴', '腾讯', '字节跳动', '百度', '美团', 
          '京东', '小米', '华为', '网易', '拼多多'
        ],
        demandRatio: [18.5, 15.2, 12.8, 9.5, 8.7, 7.3, 6.9, 6.5, 5.8, 4.8] // 需求占比（%）
      },
      analysis: {
        citySuggest: '从数据来看，深圳的该职业就业率最高（90.1%），北京需求量最大（3200个/月）；广州需求量相对较低但竞争压力更小，适合新手入行；杭州作为互联网新一线城市，需求和就业率均处于中上水平，生活成本低于北上深，性价比高。',
        companySuggest: '阿里巴巴、腾讯、字节跳动是该职业需求前三的企业，合计占比达46.5%；这类头部企业对技术要求更高，但薪资和发展空间更优；中小互联网企业（如美团、京东）需求稳定，入职门槛相对友好，适合有1-2年经验的开发者。',
        competitionSuggest: [
          '优先掌握头部企业核心技术栈（如阿里的Django/FastAPI、腾讯的微服务架构）',
          '积累高并发、高可用项目经验，提升简历竞争力',
          '关注企业招聘JD中的高频关键词，针对性强化技能（如Redis、MySQL优化、容器化部署）',
          '一线城市求职可侧重大厂校招/社招，新一线城市可关注本地龙头企业的岗位',
          '提升软技能（项目复盘、技术沟通），增加面试通过率'
        ]
      }
    }

    // 赋值到页面数据
    careerInfo.value = openDiggerMockData.careerInfo
    cityData.value = openDiggerMockData.cityData
    companyData.value = openDiggerMockData.companyData
    analysis.value = openDiggerMockData.analysis

    // 初始化所有图表
    initCityDemandChart()
    initCompanyDemandChart()
  } catch (error) {
    console.error('获取市场需求数据失败：', error)
    alert('数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 6. 初始化城市需求&就业率对比图表
const initCityDemandChart = () => {
  const chartDom = document.getElementById('cityDemandChart')
  if (!chartDom) return
  
  cityDemandChart = echarts.init(chartDom)
  const option = {
    title: { 
      text: '一线城市需求量 vs 就业率', 
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: function (params) {
        let res = params[0].name + '<br/>'
        params.forEach(item => {
          if (item.seriesName === '需求量') {
            res += `${item.seriesName}：${item.value} 个/月<br/>`
          } else {
            res += `${item.seriesName}：${item.value}%<br/>`
          }
        })
        return res
      }
    },
    legend: {
      data: ['需求量', '就业率'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '8%',
      top: '15%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: cityData.value.cities,
        axisLabel: { fontSize: 14 }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '需求量（个/月）',
        min: 0,
        max: 4000,
        interval: 1000,
        axisLabel: {
          formatter: '{value}'
        }
      },
      {
        type: 'value',
        name: '就业率（%）',
        min: 80,
        max: 95,
        interval: 5,
        axisLabel: {
          formatter: '{value}%'
        },
        position: 'right',
        offset: 0
      }
    ],
    series: [
      {
        name: '需求量',
        type: 'bar',
        data: cityData.value.demand,
        itemStyle: { color: '#007bff' },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}'
        }
      },
      {
        name: '就业率',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        data: cityData.value.employmentRate,
        itemStyle: { color: '#28a745' },
        lineStyle: { width: 3 },
        symbol: 'circle',
        symbolSize: 8,
        label: {
          show: true,
          position: 'top',
          formatter: '{c}%'
        },
        areaStyle: { color: 'rgba(40, 167, 69, 0.1)' }
      }
    ]
  }
  cityDemandChart.setOption(option)
  window.addEventListener('resize', resizeCharts)
}

// 7. 初始化企业需求分布图表
const initCompanyDemandChart = () => {
  const chartDom = document.getElementById('companyDemandChart')
  if (!chartDom) return
  
  companyDemandChart = echarts.init(chartDom)
  const option = {
    title: { 
      text: '知名企业需求占比', 
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}：{c}%（占全国总需求比例）'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center',
      textStyle: { fontSize: 12 }
    },
    series: [
      {
        name: '需求占比',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        label: {
          show: true,
          position: 'outside',
          formatter: '{b}: {c}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: true
        },
        data: companyData.value.companies.map((name, index) => ({
          name,
          value: companyData.value.demandRatio[index]
        }))
      }
    ],
    color: [
      '#007bff', '#28a745', '#ffc107', '#dc3545', '#17a2b8',
      '#6f42c1', '#fd7e14', '#20c997', '#e83e8c', '#6c757d'
    ]
  }
  companyDemandChart.setOption(option)
  window.addEventListener('resize', resizeCharts)
}

// 8. 图表自适应窗口大小
const resizeCharts = () => {
  cityDemandChart && cityDemandChart.resize()
  companyDemandChart && companyDemandChart.resize()
}

// 9. 生命周期钩子
onMounted(() => {
  getMarketData() // 页面挂载时加载数据
})

onUnmounted(() => {
  // 销毁所有图表实例，防止内存泄漏
  cityDemandChart && cityDemandChart.dispose()
  companyDemandChart && companyDemandChart.dispose()
  window.removeEventListener('resize', resizeCharts)
})
</script>

<style scoped>
/* 全局容器 */
.market-demand-container {
  width: 90%;
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  box-sizing: border-box;
}

/* 导航栏 */
.market-nav {
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
.market-title {
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
.market-content {
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

/* 图表卡片通用样式 */
.chart-card {
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
.chart-note {
  margin-top: 15px;
  font-size: 12px;
  color: #666;
  text-align: center;
  font-style: italic;
}

/* 数据解读卡片 */
.analysis-card {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.analysis-item {
  margin-bottom: 10px;
}
.analysis-item:last-child {
  margin-bottom: 0;
}
.item-title {
  font-size: 18px;
  margin: 0 0 10px 0;
  color: #007bff;
}
.analysis-content p {
  font-size: 16px;
  line-height: 1.8;
  margin: 0;
  color: #333;
}
.suggest-list {
  padding-left: 20px;
  font-size: 16px;
  line-height: 1.8;
  margin: 0;
  color: #333;
}
.suggest-list li {
  margin-bottom: 8px;
}
.suggest-list li:last-child {
  margin-bottom: 0;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .market-demand-container {
    width: 95%;
    padding: 15px;
  }
  .market-title {
    font-size: 20px;
  }
  .card-title {
    font-size: 18px;
  }
  .base-item {
    flex-direction: column;
    align-items: flex-start;
  }
  .label {
    margin-bottom: 5px;
  }
  /* 移动端图表高度适配 */
  #cityDemandChart, #companyDemandChart {
    height: 300px !important;
  }
  .analysis-item h3 {
    font-size: 16px;
  }
  .analysis-content p, .suggest-list li {
    font-size: 14px;
  }
}
</style>