// frontend/src/stores/favorites.js（建议单独建一个文件，更清晰）
import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useFavoritesStore = defineStore('favorites', () => {
  // 1. 定义状态（对应选项式的 state）
  const favoriteProjects = ref([]) // 收藏列表（用 ref 包装数组）

  // 2. 定义操作方法（对应选项式的 actions）
  const addFavorite = (project) => {
    // 避免重复收藏（检查项目 fullName 是否已存在）
    const isExist = favoriteProjects.value.some(item => item.fullName === project.fullName)
    if (!isExist) {
      favoriteProjects.value.push(project) // 往数组里添加项目
      alert(`已收藏项目：${project.name}`)
    } else {
      alert(`项目${project.name}已在收藏夹中`)
    }
  }

  const removeFavorite = (uniqueKey) => {
    favoriteProjects.value = favoriteProjects.value.filter(
      item => `${item.fullName}-${item.metric}` !== uniqueKey
    );
  };

  // 3. （可选）定义计算属性（对应选项式的 getters，这里暂时用不到）
  // const favoriteCount = computed(() => favoriteProjects.value.length) // 示例：收藏数量

  // 4. 返回需要暴露的状态和方法
  return {
    favoriteProjects,
    addFavorite,
    removeFavorite
    // favoriteCount // 若定义了计算属性，需在这里返回
  }
})