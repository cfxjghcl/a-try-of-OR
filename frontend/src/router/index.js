import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Home",
    redirect: "/tech",
  },
  {
    path: "/tech",
    name: "Tech",
    component: () => import("@/views/TechView.vue"),
  },
  {
    path: "/health",
    name: "Health",
    component: () => import("@/views/HealthView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
