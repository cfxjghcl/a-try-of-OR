<template>
  <div class="intro-page">
    <h2>OpenDigger 职业导航平台 - 网页介绍</h2>
    <div class="intro-content">
      <p>本平台基于 OpenDigger 开源项目数据开发，专注于职业/专业/技能相关信息展示，旨在为用户提供全面的职业导航服务。</p>
      <p>开发团队：高雅人士小组</p>
      <p>数据来源：OpenDigger 开源社区</p>
    </div>
    <button @click="goBack" class="back-btn">返回首页</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
const goBack = () => router.push('/professional-nav')
</script>

<style scoped>
.intro-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  color: #333;
}
.intro-content {
  margin: 20px 0;
  line-height: 1.8;
  font-size: 16px;
}
.back-btn {
  padding: 8px 20px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>