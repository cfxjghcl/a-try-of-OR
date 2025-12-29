<template>
  <div style="padding: 20px;">
    <h1>技术栈热度可视化</h1>
    
    <div v-if="loading" style="text-align: center; padding: 50px;">
      <div>加载中...</div>
    </div>
    
    <div v-else>
      <div v-if="techData.length === 0" style="color: #666; text-align: center; padding: 50px;">
        暂无数据
      </div>
      
      <div v-else>
        <!-- 统计信息 -->
        <div style="margin-bottom: 20px; padding: 15px; background: #f5f5f5; border-radius: 5px;">
          <div style="display: flex; justify-content: space-around; text-align: center;">
            <div>
              <div style="font-size: 12px; color: #666;">技术栈总数</div>
              <div style="font-size: 24px; font-weight: bold;">{{ techData.length }}</div>
            </div>
            <div>
              <div style="font-size: 12px; color: #666;">最高热度</div>
              <div style="font-size: 24px; font-weight: bold;">{{ maxHeat }}</div>
            </div>
            <div>
              <div style="font-size: 12px; color: #666;">平均热度</div>
              <div style="font-size: 24px; font-weight: bold;">{{ avgHeat.toFixed(2) }}</div>
            </div>
          </div>
        </div>
        
        <!-- 词云 -->
        <TechCloud :data="techData" />
        
        <!-- 数据表格 -->
        <div style="margin-top: 30px;">
          <h3>详细数据</h3>
          <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
              <thead>
                <tr style="background: #f5f5f5;">
                  <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">排名</th>
                  <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">技术栈</th>
                  <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">热度</th>
                  <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">更新时间</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="(item, index) in sortedData" 
                  :key="item.skill"
                  :style="{ backgroundColor: index % 2 === 0 ? '#f9f9f9' : 'white' }"
                >
                  <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">{{ index + 1 }}</td>
                  <td style="padding: 10px; border: 1px solid #ddd;">
                    <a 
                      :href="`https://github.com/${item.skill}`" 
                      target="_blank"
                      style="color: #0366d6; text-decoration: none;"
                    >
                      {{ item.skill }}
                    </a >
                  </td>
                  <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">
                    <span :style="{ 
                      color: item.heat >= 2 ? '#ff4757' : '#a4b0be', 
                      fontWeight: 'bold' 
                    }">
                      {{ item.heat }}
                    </span>
                  </td>
                  <td style="padding: 10px; border: 1px solid #ddd;">
                    {{ formatDate(item.updated_at) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TechCloud from '@/components/TechCloud.vue';
import { getTechHeat } from '@/api/tech';

export default {
  name: 'TechView',
  components: {
    TechCloud
  },
  data() {
    return {
      loading: true,
      techData: []
    };
  },
  computed: {
    sortedData() {
      return [...this.techData].sort((a, b) => b.heat - a.heat);
    },
    maxHeat() {
      return Math.max(...this.techData.map(item => item.heat));
    },
    avgHeat() {
      const sum = this.techData.reduce((acc, item) => acc + item.heat, 0);
      return sum / this.techData.length;
    }
  },
  async mounted() {
    await this.loadData();
  },
  methods: {
    async loadData() {
      this.loading = true;
      try {
        this.techData = await getTechHeat();
      } catch (error) {
        console.error('加载数据失败:', error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(date) {
      if (!date) return '未知';
      try {
        return new Date(date).toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch {
        return date;
      }
    }
  }
};
</script>