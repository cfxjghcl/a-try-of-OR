import { createRouter, createWebHistory } from 'vue-router'
// 导入职业导航相关组件（新增搜索结果页）
import ProfessionalNavMain from '../views/professional-nav/professional-nav-main.vue'
import ProfessionalNavLogin from '../views/professional-nav/professional-nav-login.vue'
import ProfessionalNavIntro from '../views/professional-nav/professional-nav-intro.vue'
import ProfessionalNavCareer from '../views/professional-nav/professional-nav-career.vue'
import ProfessionalNavMajor from '../views/professional-nav/professional-nav-major.vue'
import ProfessionalNavSkill from '../views/professional-nav/professional-nav-skill.vue'
import ProfessionalNavMarket from '../views/professional-nav/professional-nav-market.vue'
import ProfessionalNavFeedback from '../views/professional-nav/professional-nav-feedback.vue'
// 新增：导入搜索结果页
import ProfessionalNavSearch from '../views/professional-nav/professional-nav-search.vue'

const routes = [
  // 根路径重定向到职业导航主页面
  {
    path: '/',
    redirect: '/professional-nav'
  },
  // 职业导航主路由
  {
    path: '/professional-nav',
    name: 'ProfessionalNavMain',
    component: ProfessionalNavMain,
    children: [
      { path: 'intro', name: 'ProfessionalNavIntro', component: ProfessionalNavIntro },
      { path: 'career', name: 'ProfessionalNavCareer', component: ProfessionalNavCareer },
      { path: 'major', name: 'ProfessionalNavMajor', component: ProfessionalNavMajor },
      { path: 'skill', name: 'ProfessionalNavSkill', component: ProfessionalNavSkill },
      { path: 'market', name: 'ProfessionalNavMarket', component: ProfessionalNavMarket },
      { path: 'feedback', name: 'ProfessionalNavFeedback', component: ProfessionalNavFeedback },
      // 新增：搜索结果页子路由
      { path: 'search', name: 'ProfessionalNavSearch', component: ProfessionalNavSearch }
    ]
  },
  // 登录页独立路由
  {
    path: '/professional-nav/login',
    name: 'ProfessionalNavLogin',
    component: ProfessionalNavLogin
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router