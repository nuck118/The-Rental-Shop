import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

const routes = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/signin",
    component: () => import("../views/SigninView.vue"),
  },
  {
    path: "/dashboard",
    component: () => import("../views/DashboardView.vue"),
    meta: { requiresAuth: true },
  },
  // Catch-all: redirect unknown routes based on auth state
  {
    path: "/:pathMatch(.*)*",
    redirect: (to) => {
      // We can't access Pinia stores directly in redirect function,
      // so we check localStorage for the token
      const token = localStorage.getItem("token");
      return token ? "/dashboard" : "/signin";
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next("/signin");
  } else if (to.path === "/signin" && authStore.isAuthenticated) {
    next("/dashboard");
  } else {
    next();
  }
});

export default router;
