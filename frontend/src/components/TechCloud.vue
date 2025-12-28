<template>
  <div ref="chart" style="width:100%;height:500px;"></div>
</template>

<script>
import * as echarts from 'echarts';
import 'echarts-wordcloud';

export default {
  props: ['data'],
  mounted() {
    this.renderChart();
  },
  methods: {
    renderChart() {
      const chart = echarts.init(this.$refs.chart);
      const option = {
        series: [{
          type: 'wordCloud',
          data: this.data.map(item => ({
            name: item.skill,
            value: item.heat
          }))
        }]
      };
      chart.setOption(option);
    }
  }
};
</script>