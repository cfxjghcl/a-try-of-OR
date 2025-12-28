<template>
  <div ref="chartRef" style="width: 100%; height: 600px;"></div>
</template>

<script>
import * as echarts from 'echarts'
import 'echarts-wordcloud'

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
      this.initChart()
    })
  },
  methods: {
    initChart() {
      if (!this.data || this.data.length === 0) {
        console.warn('没有数据，无法绘制图表')
        return
      }
      
      // 为了更好的视觉效果，可以放大heat值
      const maxHeat = Math.max(...this.data.map(item => item.heat))
      const scaleFactor = maxHeat <= 2 ? 10 : 1  // 如果heat值小，放大10倍
      
      const wordData = this.data.map(item => ({
        name: item.skill.split('/').pop(),  // 只显示项目名，不显示组织名
        value: item.heat * scaleFactor,
        originalHeat: item.heat,
        fullName: item.skill,
        updated_at: item.updated_at
      }))
      
      const chart = echarts.init(this.$refs.chartRef)
      
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
          formatter: function(params) {
            return `
              <div style="padding: 5px;">
                <strong>${params.data.fullName}</strong><br/>
                热度: ${params.data.originalHeat}<br/>
                更新时间: ${params.data.updated_at}
              </div>
            `
          }
        },
        series: [{
          type: 'wordCloud',
          shape: 'circle',
          left: 'center',
          top: 'center',
          width: '95%',
          height: '90%',
          sizeRange: [20, 80],  // 文字大小范围
          rotationRange: [-45, 45],  // 旋转角度范围
          rotationStep: 45,
          gridSize: 15,
          drawOutOfBound: false,
          textStyle: {
            fontWeight: 'bold',
            color: function () {
              // 更丰富的颜色方案
              const colors = [
                '#5470c6', '#91cc75', '#fac858', '#ee6666',
                '#73c0de', '#3ba272', '#fc8452', '#9a60b4',
                '#ea7ccc', '#60acfc'
              ]
              return colors[Math.floor(Math.random() * colors.length)]
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
      }
      
      chart.setOption(option)
      
      // 响应窗口大小变化
      window.addEventListener('resize', () => {
        chart.resize()
      })
    }
  },
  watch: {
    data: {
      handler() {
        this.initChart()
      },
      deep: true
    }
  }
}
</script>