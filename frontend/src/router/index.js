import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    component: () => import("../views/HomeView.vue"),
  },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
