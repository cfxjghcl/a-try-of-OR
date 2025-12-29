import { createRouter, createWebHistory } from 'vue-router'
import TechView from '../views/TechView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: TechView },
    { path: '/tech', redirect: '/' }
  ]
})

export default router