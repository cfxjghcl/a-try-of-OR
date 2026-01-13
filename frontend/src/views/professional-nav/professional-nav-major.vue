<template>
  <div class="major-detail-container">
    <!-- 1. 页面导航栏 -->
    <div class="major-nav">
      <button @click="$router.back()" class="back-btn">← 返回</button>
      <h1 class="major-title">{{ majorInfo.name }} 专业详情</h1>
    </div>

    <!-- 加载中提示 -->
    <div v-if="loading" class="loading">正在加载专业数据...</div>

    <!-- 2. 专业基础信息卡片 -->
    <div v-else class="major-base-card">
      <div class="base-item">
        <span class="label">所属大类：</span>
        <span class="value">{{ majorInfo.category || "暂无数据" }}</span>
      </div>
      <div class="base-item">
        <span class="label">核心就业方向：</span>
        <span class="value">{{ majorInfo.careerDirection?.join("、") || "暂无数据" }}</span>
      </div>
      <div class="base-item">
        <span class="label">平均薪资：</span>
        <span class="value">{{ majorInfo.averageSalary || "暂无数据" }} 元/月</span>
      </div>
      <div class="base-item">
        <span class="label">行业需求热度：</span>
        <div class="heat-bar">
          <div class="heat-fill" :style="{ width: majorInfo.heat + '%' }"></div>
        </div>
        <span class="heat-text">{{ majorInfo.heat }}%</span>
      </div>
    </div>

    <!-- 3. OpenDigger数据适配性分析 -->
    <div v-if="!loading" class="major-analysis-card">
      <h2 class="card-title">专业适配性分析（基于OpenDigger开源数据）</h2>
      
      <!-- 3.1 技能匹配度分析 -->
      <div class="analysis-item">
        <h3 class="item-title">核心技能匹配度</h3>
        <div class="skill-list">
          <div 
            v-for="skill in majorAnalysis.skillMatch" 
            :key="skill.name" 
            class="skill-item"
          >
            <span class="skill-name">{{ skill.name }}</span>
            <div class="match-bar">
              <div class="match-fill" :style="{ width: skill.matchRate + '%' }"></div>
            </div>
            <span class="match-rate">{{ skill.matchRate }}%</span>
          </div>
        </div>
      </div>

      <!-- 3.2 岗位适配推荐 -->
      <div class="analysis-item">
        <h3 class="item-title">适配岗位推荐</h3>
        <div class="career-list">
          <div 
            v-for="career in majorAnalysis.careerRecommend" 
            :key="career.id" 
            class="career-card"
            @click="goToCareerDetail(career.id)"
          >
            <h4 class="career-name">{{ career.name }}</h4>
            <p class="career-match">匹配度：{{ career.matchRate }}%</p>
            <p class="career-salary">薪资范围：{{ career.salaryRange }}</p>
          </div>
        </div>
      </div>

      <!-- 3.3 行业趋势分析 -->
      <div class="analysis-item">
        <h3 class="item-title">行业趋势（近1年）</h3>
        <div class="trend-chart">
          <div id="trendChart" style="width: 100%; height: 300px;"></div>
        </div>
      </div>
    </div>

    <!-- 4. 个性化学习建议 -->
    <div v-if="!loading" class="major-suggest-card">
      <h2 class="card-title">个性化学习建议</h2>
      
      <!-- 4.1 核心技能学习 -->
      <div class="suggest-item">
        <h3 class="item-title">核心技能学习清单</h3>
        <ul class="suggest-list">
          <li v-for="(item, index) in learnSuggest.coreSkills" :key="index">
            {{ item }}
          </li>
        </ul>
      </div>

      <!-- 4.2 学习资源推荐 -->
      <div class="suggest-item">
        <h3 class="item-title">推荐学习资源</h3>
        <div class="resource-list">
          <a 
            v-for="(resource, index) in learnSuggest.resources" 
            :key="index" 
            :href="resource.url" 
            target="_blank" 
            class="resource-item"
          >
            {{ resource.name }} - {{ resource.type }}
          </a>
        </div>
      </div>

      <!-- 4.3 进阶学习路径 -->
      <div class="suggest-item">
        <h3 class="item-title">进阶学习路径</h3>
        <div class="path-list">
          <div 
            v-for="(stage, index) in learnSuggest.learningPath" 
            :key="index" 
            class="path-stage"
          >
            <span class="stage-num">第{{ index + 1 }}阶段</span>
            <span class="stage-content">{{ stage }}</span>
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
const majorId = route.params.id // 获取专业ID
const loading = ref(true) // 加载状态
let trendChart = null // 图表实例（用于销毁）

// 1. 定义页面核心数据
const majorInfo = ref({
  name: '', // 专业名称
  category: '', // 所属大类
  careerDirection: [], // 核心就业方向
  averageSalary: 0, // 平均薪资
  heat: 0 // 行业需求热度
})

const majorAnalysis = ref({
  skillMatch: [], // 技能匹配度
  careerRecommend: [], // 适配岗位
  trendData: [] // 行业趋势数据
})

const learnSuggest = ref({
  coreSkills: [], // 核心技能清单
  resources: [], // 学习资源
  learningPath: [] // 进阶路径
})

// 2. 模拟调用OpenDigger API获取数据（真实项目替换为真实接口）
const getMajorData = async () => {
  try {
    loading.value = true
    // 模拟接口请求延迟
    await new Promise(resolve => setTimeout(resolve, 800))

    // 模拟OpenDigger返回的专业数据（真实项目替换为：await fetch(OpenDigger API)）
    const openDiggerMockData = {
      majorInfo: {
        name: '计算机科学与技术',
        category: '计算机类',
        careerDirection: ['后端开发', '前端开发', '大数据开发', '人工智能'],
        averageSalary: 15000,
        heat: 90
      },
      analysis: {
        skillMatch: [
          { name: 'Python', matchRate: 95 },
          { name: 'Java', matchRate: 90 },
          { name: 'JavaScript', matchRate: 85 },
          { name: 'SQL', matchRate: 92 },
          { name: '机器学习', matchRate: 75 }
        ],
        careerRecommend: [
          { id: 1, name: 'Python后端开发', matchRate: 95, salaryRange: '10k-25k' },
          { id: 2, name: '大数据工程师', matchRate: 88, salaryRange: '12k-30k' },
          { id: 3, name: '全栈开发工程师', matchRate: 85, salaryRange: '15k-28k' }
        ],
        trendData: [80, 82, 85, 88, 90, 92] // 近6个月热度
      },
      suggest: {
        coreSkills: [
          '熟练掌握Python/Java核心语法',
          '掌握至少1个后端框架（Django/SSM）',
          '熟悉MySQL/Redis等数据库操作',
          '了解常用数据结构与算法'
        ],
        resources: [
          { name: 'Python编程：从入门到实践', type: '书籍', url: 'https://book.douban.com/subject/26829017/' },
          { name: '尚硅谷Java教程', type: '视频', url: 'https://www.bilibili.com/video/BV1Rx411876f/' },
          { name: 'LeetCode算法刷题', type: '实战', url: 'https://leetcode.cn/' },
          { name: 'OpenDigger开源文档', type: '官方文档', url: 'https://open-digger.github.io/' }
        ],
        learningPath: [
          '基础阶段：掌握编程语言核心语法 + 计算机基础（计网/操作系统）',
          '进阶阶段：学习主流框架 + 实战小项目（如个人博客、管理系统）',
          '提升阶段：参与开源项目/企业级项目，积累实战经验',
          '就业阶段：针对性刷题 + 项目复盘，准备面试'
        ]
      }
    }

    // 赋值到页面数据
    majorInfo.value = openDiggerMockData.majorInfo
    majorAnalysis.value = openDiggerMockData.analysis
    learnSuggest.value = openDiggerMockData.suggest

    // 初始化趋势图表
    initTrendChart()
  } catch (error) {
    console.error('获取专业数据失败：', error)
    alert('数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 3. 初始化行业趋势ECharts图表
const initTrendChart = () => {
  const chartDom = document.getElementById('trendChart')
  if (!chartDom) return
  
  trendChart = echarts.init(chartDom)
  const option = {
    title: { text: '近6个月行业需求热度变化', left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月'],
      axisLabel: { fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      min: 70,
      max: 100,
      axisLabel: { formatter: '{value}%' }
    },
    series: [
      {
        name: '需求热度',
        type: 'line',
        smooth: true,
        data: majorAnalysis.value.trendData,
        itemStyle: { color: '#007bff' },
        areaStyle: { color: 'rgba(0, 123, 255, 0.1)' },
        markPoint: {
          data: [
            { type: 'max', name: '最大值' },
            { type: 'min', name: '最小值' }
          ]
        }
      }
    ]
  }
  trendChart.setOption(option)
  
  // 自适应窗口大小
  window.addEventListener('resize', resizeChart)
}

// 图表自适应
const resizeChart = () => {
  if (trendChart) {
    trendChart.resize()
  }
}

// 4. 跳转至岗位详情页
const goToCareerDetail = (careerId) => {
  router.push(`/professional-nav/career/${careerId}`)
}

// 5. 生命周期钩子
onMounted(() => {
  getMajorData() // 页面挂载时加载数据
})

onUnmounted(() => {
  // 销毁图表实例，防止内存泄漏
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }
  window.removeEventListener('resize', resizeChart)
})
</script>

<style scoped>
/* 全局样式 */
.major-detail-container {
  width: 90%;
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  box-sizing: border-box;
}

/* 导航栏 */
.major-nav {
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
.major-title {
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

/* 基础信息卡片 */
.major-base-card {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}
.base-item {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
  font-size: 16px;
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
.heat-bar {
  width: 200px;
  height: 10px;
  background-color: #eee;
  border-radius: 5px;
  margin: 0 10px;
  flex-shrink: 0;
}
.heat-fill {
  height: 100%;
  background-color: #007bff;
  border-radius: 5px;
  transition: width 0.5s ease;
}
.heat-text {
  color: #007bff;
  font-weight: bold;
  width: 50px;
  text-align: right;
  flex-shrink: 0;
}

/* 分析卡片 & 建议卡片通用样式 */
.major-analysis-card, .major-suggest-card {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}
.card-title {
  font-size: 20px;
  font-weight: bold;
  margin: 0 0 20px 0;
  color: #2c3e50;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}
.analysis-item, .suggest-item {
  margin-bottom: 25px;
}
.analysis-item:last-child, .suggest-item:last-child {
  margin-bottom: 0;
}
.item-title {
  font-size: 18px;
  margin: 0 0 15px 0;
  color: #333;
}

/* 技能匹配度 */
.skill-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.skill-item {
  display: flex;
  align-items: center;
  font-size: 16px;
}
.skill-name {
  width: 100px;
  flex-shrink: 0;
  color: #555;
}
.match-bar {
  flex: 1;
  height: 8px;
  background-color: #eee;
  border-radius: 4px;
  margin: 0 10px;
}
.match-fill {
  height: 100%;
  background-color: #28a745;
  border-radius: 4px;
  transition: width 0.5s ease;
}
.match-rate {
  width: 50px;
  text-align: right;
  color: #28a745;
  font-weight: bold;
  flex-shrink: 0;
}

/* 岗位推荐 */
.career-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}
.career-card {
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}
.career-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #007bff;
  transform: translateY(-2px);
}
.career-name {
  font-size: 16px;
  font-weight: bold;
  margin: 0 0 8px 0;
  color: #2c3e50;
}
.career-match {
  color: #28a745;
  margin: 0 0 8px 0;
  font-size: 14px;
}
.career-salary {
  color: #666;
  font-size: 14px;
  margin: 0;
}

/* 学习建议 */
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
.resource-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.resource-item {
  color: #007bff;
  text-decoration: none;
  font-size: 16px;
  line-height: 1.6;
}
.resource-item:hover {
  text-decoration: underline;
  color: #0056b3;
}
.path-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.path-stage {
  display: flex;
  align-items: flex-start;
  font-size: 16px;
  line-height: 1.6;
}
.stage-num {
  width: 80px;
  font-weight: bold;
  color: #007bff;
  flex-shrink: 0;
  margin-right: 10px;
}
.stage-content {
  flex: 1;
  color: #333;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .major-detail-container {
    width: 95%;
    padding: 15px;
  }
  .career-list {
    grid-template-columns: 1fr;
  }
  .base-item {
    flex-direction: column;
    align-items: flex-start;
  }
  .label {
    margin-bottom: 5px;
  }
  .heat-bar {
    width: 100%;
    margin: 5px 0;
  }
  .heat-text {
    align-self: flex-start;
    margin-top: 5px;
  }
  .major-title {
    font-size: 20px;
  }
  .card-title {
    font-size: 18px;
  }
  .item-title {
    font-size: 16px;
  }
}
</style>