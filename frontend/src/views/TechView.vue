
<template>
  <div>
    <h1>技术栈页面</h1>
    <h2>技术栈热度可视化</h2>
    <TechCloud :data="techData" />
    <p>数据条数：{{ techData.length }}</p >
  </div>
</template>

<script>
import TechCloud from '@/components/TechCloud.vue';
import { getTechHeat } from '@/api/tech';

export default {
  components: { TechCloud },
  data() {
    return { techData: [] };
  },
  async mounted() {
    this.techData = await getTechHeat();
  }
};
</script>