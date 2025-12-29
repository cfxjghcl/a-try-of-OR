<template>
  <div id="app">
    <!-- 最简导航 -->
    <div style="background: #4a6fa5; padding: 15px 20px; color: white; font-weight: bold;">
      技术栈热度分析系统
    </div>
    
    <div style="padding: 20px;">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
body {
  margin: 0;
  font-family: Arial, sans-serif;
}
</style>