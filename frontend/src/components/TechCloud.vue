<template>
  <div>
    <div ref="chartRef" style="width: 100%; height: 600px;"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import 'echarts-wordcloud';

export default {
  name: 'TechCloud',
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart();
    });
  },
  methods: {
    initChart() {
      if (!this.data || this.data.length === 0) {
        console.warn('没有数据，无法绘制图表');
        return;
      }

      // 转换数据格式
      const wordData = this.data.map(item => {
        // 提取项目名（去掉组织名）
        const projectName = item.skill.includes('/') 
          ? item.skill.split('/')[1] 
          : item.skill;
        
        return {
          name: projectName,
          value: item.heat * 10, // 放大热度值，使差异更明显
          originalHeat: item.heat,
          fullName: item.skill,
          updated_at: item.updated_at || new Date().toISOString()
        };
      });

      // 初始化图表
      const chart = echarts.init(this.$refs.chartRef);
      
      const option = {
        title: {
          text: '技术栈热度词云',
          left: 'center',
          textStyle: {
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          show: true,
          formatter: function (params) {
            return `
              <div style="padding: 5px;">
                <strong>${params.data.fullName}</strong><br/>
                热度: ${params.data.originalHeat}<br/>
                更新时间: ${new Date(params.data.updated_at).toLocaleString()}
              </div>
            `;
          }
        },
        series: [{
          type: 'wordCloud',
          shape: 'circle',
          left: 'center',
          top: 'center',
          width: '95%',
          height: '90%',
          sizeRange: [20, 80],
          rotationRange: [-45, 45],
          rotationStep: 45,
          gridSize: 15,
          drawOutOfBound: false,
          textStyle: {
            fontWeight: 'bold',
            color: function () {
              // 随机颜色
              const colors = [
                '#5470c6', '#91cc75', '#fac858', '#ee6666',
                '#73c0de', '#3ba272', '#fc8452', '#9a60b4',
                '#ea7ccc', '#60acfc'
              ];
              return colors[Math.floor(Math.random() * colors.length)];
            }
          },
          emphasis: {
            textStyle: {
              shadowBlur: 15,
              shadowColor: '#333'
            }
          },
          data: wordData
        }]
      };

      chart.setOption(option);

      // 响应窗口大小变化
      window.addEventListener('resize', () => {
        chart.resize();
      });
    }
  },
  watch: {
    data: {
      handler() {
        this.initChart();
      },
      deep: true
    }
  }
};
</script>

<style scoped>
/* 如果需要，可以添加一些样式 */
</style>