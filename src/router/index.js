import { createRouter, createWebHistory } from 'vue-router'
// 导入职业导航核心组件
import ProfessionalNavMain from '../views/professional-nav/professional-nav-main.vue'
import ProfessionalNavLogin from '../views/professional-nav/professional-nav-login.vue'
import ProfessionalNavIntro from '../views/professional-nav/professional-nav-intro.vue'
import ProfessionalNavCareer from '../views/professional-nav/professional-nav-career.vue'
import ProfessionalNavMajor from '../views/professional-nav/professional-nav-major.vue'
import ProfessionalNavSkill from '../views/professional-nav/professional-nav-skill.vue'
import ProfessionalNavMarket from '../views/professional-nav/professional-nav-market.vue'
import ProfessionalNavFeedback from '../views/professional-nav/professional-nav-feedback.vue'
// 导入搜索结果页组件
import ProfessionalNavSearch from '../views/professional-nav/professional-nav-search.vue'

// ========== 薪资趋势页面导入（文件在views根目录） ==========
import SalaryTrend from '../views/SalaryTrend.vue'

// 未实现的页面先注释
// import CareerDetail from '../views/CareerDetail.vue'
// import UserProfile from '../views/UserProfile.vue'

const routes = [
  // 根路径重定向到职业导航主页面
  {
    path: '/',
    redirect: '/professional-nav'
  },
  // 职业导航主路由（嵌套子路由）
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
      { path: 'search', name: 'ProfessionalNavSearch', component: ProfessionalNavSearch },
      // 薪资趋势子路由
      { path: 'salary-trend', name: 'SalaryTrend', component: SalaryTrend },
    ]
  },
  // 登录页独立路由
  {
    path: '/professional-nav/login',
    name: 'ProfessionalNavLogin',
    component: ProfessionalNavLogin
  },
  // 薪资趋势独立路由（方便测试）
  {
    path: '/salary-trend',
    name: 'SalaryTrendStandalone',
    component: SalaryTrend,
    meta: { title: '薪资趋势可视化' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 全局路由守卫：验证登录状态
router.beforeEach((to, from, next) => {
  const needLoginPages = ['SalaryTrend', 'SalaryTrendStandalone']
  const token = localStorage.getItem('token')

  if (needLoginPages.includes(to.name) && !token) {
    next({ name: 'ProfessionalNavLogin' })
  } else {
    next()
  }
})

export default router