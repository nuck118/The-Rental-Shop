<script setup>
import { onMounted } from "vue";
import { RouterView } from "vue-router";
import { useAuthStore } from "./stores/auth";

const authStore = useAuthStore();

onMounted(() => {
  // Start inactivity monitor if user is already authenticated (e.g., page refresh)
  if (authStore.isAuthenticated) {
    authStore.startInactivityMonitor();
  }
});
</script>

<template>
  <router-view v-slot="{ Component, route }">
    <transition name="page" mode="out-in">
      <component :is="Component" :key="route.path" />
    </transition>
  </router-view>
</template>