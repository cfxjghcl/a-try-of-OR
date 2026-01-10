<template>
  <!-- 仅保留路由出口：所有页面（职业导航）都会渲染在这里 -->
  <router-view />
</template>

<script setup>
// 空脚本：无需任何代码，不影响页面渲染
</script>

<style scoped>
/* 仅保留全局基础样式，保证页面布局正常 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Microsoft Yahei", sans-serif;
  background-color: #f8f9fa;
  color: #333;
}

/* 清除默认链接样式（如果有） */
a {
  text-decoration: none;
  color: inherit;
}

/* 清除默认列表样式 */
ul, li {
  list-style: none;
}
</style>