import { defineStore } from 'pinia';

// 定义图表存储，持久化动态添加的图表
export const useChartStore = defineStore('chart', {
  state: () => ({
    // 存储动态图表列表（结构和之前的 dynamicCharts 一致）
    dynamicCharts: []
  }),
  actions: {
    // 添加图表
    addChart(chart) {
      this.dynamicCharts.push(chart);
    },
    // 删除图表
    removeChart(chartId) {
      this.dynamicCharts = this.dynamicCharts.filter(chart => chart.id !== chartId);
    },
    // 清空图表（可选，如需重置功能）
    clearCharts() {
      this.dynamicCharts = [];
    }
  },
  // 可选：持久化到 localStorage，页面刷新也不丢失
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'opendigger_charts', // 存储在 localStorage 的 key
        storage: localStorage,
        paths: ['dynamicCharts'] // 只持久化 dynamicCharts 字段
      }
    ]
  }
});