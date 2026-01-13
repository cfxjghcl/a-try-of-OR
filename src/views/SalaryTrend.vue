<template>
  <div class="salary-trend-container">
    <h2>🔥 计算机相关职业薪资趋势（2020-2024）</h2>
    <!-- 加载状态 -->
    <div v-if="loading" class="loading">加载中...</div>
    <!-- 错误提示 -->
    <div v-if="error" class="error">{{ error }}</div>
    <!-- ECharts图表容器 -->
    <div v-else id="salary-chart" style="width: 100%; height: 600px;"></div>
  </div>
</template>

<script setup>
import { onMounted, ref, onUnmounted } from 'vue'
import * as echarts from 'echarts'
// 导入封装的薪资趋势接口（确保api/index.js中已定义）
import { getSalaryTrend } from '@/api/index'

// 状态管理
const loading = ref(true) // 加载状态
const error = ref('') // 错误信息
let chartInstance = null // ECharts实例（用于销毁，避免内存泄漏）

// 页面挂载后渲染图表
onMounted(async () => {
  try {
    // 1. 调用后端接口获取薪资数据
    const res = await getSalaryTrend()
    const salaryData = res.data // 后端返回的薪资数据结构：{years: [], backend: [], ...}

    // 2. 初始化ECharts实例
    const chartDom = document.getElementById('salary-chart')
    chartInstance = echarts.init(chartDom)

    // 3. 配置图表选项（适配后端返回的数据格式）
    const option = {
      title: {
        text: '各职业月薪趋势对比',
        left: 'center',
        textStyle: { fontSize: 18, fontWeight: 600 }
      },
      tooltip: {
        trigger: 'axis',
        formatter: '{b}年 {a}：{c} 元', // 鼠标悬浮提示格式
        axisPointer: { type: 'shadow' }
      },
      legend: {
        data: ['后端开发', '前端开发', '全栈开发', '数据科学', 'AI工程师'],
        top: 'bottom' // 图例放在底部
      },
      grid: {
        left: '5%',
        right: '5%',
        bottom: '15%',
        containLabel: true // 防止标签被裁剪
      },
      xAxis: {
        type: 'category',
        data: salaryData.years || [2020, 2021, 2022, 2023, 2024], // 兼容后端无数据的情况
        axisLabel: { fontSize: 12 },
        axisLine: { lineStyle: { color: '#ccc' } }
      },
      yAxis: {
        type: 'value',
        name: '月薪（元）',
        nameTextStyle: { fontSize: 12 },
        axisLabel: {
          formatter: '{value} 元' // 显示薪资单位
        },
        splitLine: { lineStyle: { color: '#f5f5f5' } }
      },
      // 系列数据：每个职业一条折线（适配后端返回的字段）
      series: [
        {
          name: '后端开发',
          type: 'line',
          data: salaryData.backend || [8000, 9500, 11000, 12500, 14000],
          smooth: true, // 线条平滑
          lineStyle: { width: 3, color: '#409eff' },
          itemStyle: { color: '#409eff', borderRadius: 4 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0)' }
          ]) }
        },
        {
          name: '前端开发',
          type: 'line',
          data: salaryData.frontend || [7500, 8800, 10000, 11500, 13000],
          smooth: true,
          lineStyle: { width: 3, color: '#67c23a' },
          itemStyle: { color: '#67c23a', borderRadius: 4 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0)' }
          ]) }
        },
        {
          name: '全栈开发',
          type: 'line',
          data: salaryData.fullstack || [10000, 12000, 14000, 16000, 18000],
          smooth: true,
          lineStyle: { width: 3, color: '#e6a23c' },
          itemStyle: { color: '#e6a23c', borderRadius: 4 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(230, 162, 60, 0.3)' },
            { offset: 1, color: 'rgba(230, 162, 60, 0)' }
          ]) }
        },
        {
          name: '数据科学',
          type: 'line',
          data: salaryData.data_science || [9000, 11000, 13500, 16000, 18500],
          smooth: true,
          lineStyle: { width: 3, color: '#f56c6c' },
          itemStyle: { color: '#f56c6c', borderRadius: 4 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0)' }
          ]) }
        },
        {
          name: 'AI工程师',
          type: 'line',
          data: salaryData.ai_engineer || [12000, 15000, 19000, 25000, 36000],
          smooth: true,
          lineStyle: { width: 3, color: '#909399' },
          itemStyle: { color: '#909399', borderRadius: 4 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(144, 147, 153, 0.3)' },
            { offset: 1, color: 'rgba(144, 147, 153, 0)' }
          ]) }
        }
      ]
    }

    // 4. 渲染图表
    chartInstance.setOption(option)

    // 5. 适配窗口大小变化（图表自适应）
    window.addEventListener('resize', () => {
      chartInstance.resize()
    })

    // 6. 加载完成，隐藏加载状态
    loading.value = false
  } catch (err) {
    // 捕获错误，显示提示
    loading.value = false
    error.value = '获取薪资数据失败：' + (err.message || '未知错误')
    console.error('薪资趋势页面加载失败：', err)
  }
})

// 页面卸载时销毁ECharts实例（避免内存泄漏）
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
/* 页面容器样式，适配你的项目风格 */
.salary-trend-container {
  max-width: 1200px;
  margin: 30px auto;
  padding: 0 20px;
  font-family: "Microsoft Yahei", sans-serif;
}

/* 标题样式 */
.salary-trend-container h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 20px;
  font-weight: 600;
}

/* 加载状态样式 */
.loading {
  text-align: center;
  padding: 100px 0;
  color: #666;
  font-size: 16px;
}

/* 错误提示样式 */
.error {
  text-align: center;
  padding: 100px 0;
  color: #dc3545;
  font-size: 16px;
}
</style>