<template>
  <div class="chart-container">
    <div class="chart-header" v-if="title">
      <h3>{{ title }}</h3>
      <button @click="handleFavorite" class="favorite-btn">❤️</button>
    </div>
    <div ref="chartRef" class="chart-dom"></div>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-if="error" class="error">⚠️ {{ error }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, shallowRef, nextTick, watch } from 'vue';
import * as echarts from 'echarts';
import { opendiggerApi } from '../api/api';
import { useFavoritesStore } from '../stores/favorites';

const props = defineProps({
  platform: { type: String, required: true },
  org: { type: String, required: true }, // 接收 chart.entity（组织/用户）
  repo: { type: String, default: '' },   // 仓库名（user类型为空）
  metric: { type: String, required: true },
  title: { type: String, default: '' },
  loading: { type: Boolean, default: false }, // 从父组件接收加载状态
  error: { type: String, default: '' },       // 从父组件接收错误状态
  chartData: { type: Array, default: () => [] } // 从父组件接收已请求的数据
});

const favoritesStore = useFavoritesStore();
const chartRef = ref(null);
const chartInstance = shallowRef(null);

// 收藏功能（保留原有逻辑，user类型隐藏收藏按钮可自行扩展）
const handleFavorite = () => {
  if (!props.repo) return; // 开发者类型无仓库，不支持收藏
  const platformDomain = props.platform === 'github' ? 'github.com' : 'gitee.com';
  const project = {
    name: props.repo,
    fullName: `${props.org}/${props.repo}`,
    url: `https://${platformDomain}/${props.org}/${props.repo}`,
    metric: props.metric,
    title: props.title || `${props.org}/${props.repo} - ${props.metric}`,
    platform: props.platform
  };
  favoritesStore.addFavorite(project);
};

// 初始化图表（优先使用父组件传递的 chartData，无数据再请求）
const initChart = () => {
  if (!chartRef.value) return;

  // 销毁已有实例
  if (chartInstance.value) {
    chartInstance.value.dispose();
  }

  // 若父组件已传递数据，直接渲染
  if (props.chartData.length) {
    renderChart(props.chartData);
    return;
  }

  // 父组件无数据（异常情况），主动请求（兜底逻辑）
  fetchChartData();
};

// 渲染图表
const renderChart = (data) => {
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', axisLabel: { rotate: 30 }, data: data.map(item => item[0]) },
    yAxis: { type: 'value', min: 0 },
    series: [{ data: data.map(item => item[1]), type: 'line', smooth: true }],
    grid: { left: '5%', right: '5%', bottom: '15%' }
  };
  chartInstance.value = echarts.init(chartRef.value);
  chartInstance.value.setOption(option);
  window.addEventListener('resize', () => chartInstance.value?.resize());
};

// 兜底：主动请求数据（父组件未传递数据时使用）
const fetchChartData = async () => {
  try {
    // 根据是否有仓库名，调用不同的后端接口
    let res;
    if (props.repo) {
      // 仓库类型（org）
      res = await opendiggerApi.getRepoData(props.platform, props.org, props.repo, props.metric);
    } else {
      // 开发者类型（user）
      res = await opendiggerApi.getUserData(props.platform, props.org, props.metric);
    }
    const chartData = res.data.data;
    if (chartData.length) {
      renderChart(chartData);
    } else {
      props.error = '无有效数据';
    }
  } catch (err) {
    props.error = `加载失败：${err.message}`;
  }
};

// 监听参数变化，重新初始化图表
watch(
  [() => props.platform, () => props.org, () => props.repo, () => props.metric, () => props.chartData],
  () => nextTick(initChart),
  { immediate: true }
);

onMounted(() => nextTick(initChart));
onUnmounted(() => {
  window.removeEventListener('resize', () => chartInstance.value?.resize());
  chartInstance.value?.dispose();
});
</script>

<style scoped>
/* 样式不变，保持原有即可 */
.chart-container { width: 100%; height: 300px; position: relative; }
.chart-header { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
.chart-dom { width: 100%; height: 250px; }
.favorite-btn { background: transparent; border: none; cursor: pointer; color: #999; }
.favorite-btn:hover { color: #f00; }
.loading, .error { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #666; }
.error { color: #f00; }
</style>