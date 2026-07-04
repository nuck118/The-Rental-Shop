<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { Mail, Lock, LogIn } from "lucide-vue-next";

const router = useRouter();
const authStore = useAuthStore();

const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

const handleSignin = async () => {
  error.value = "";
  if (!username.value || !password.value) {
    error.value = "Please enter both username and password";
    return;
  }

  loading.value = true;
  const success = await authStore.login(username.value, password.value);
  loading.value = false;

  if (success) {
    router.push("/dashboard");
  } else {
    error.value = "Invalid username or password";
  }
};

const handleKeydown = (e) => {
  if (e.key === "Enter") handleSignin();
};
</script>

<template>
  <div class="min-h-screen bg-white flex flex-col">
    <div class="flex-1 flex items-center justify-center px-6">
      <div class="w-full max-w-sm">
        <!-- Logo -->
        <div class="mb-12">
          <div class="w-10 h-10 bg-neutral-900 flex items-center justify-center mb-5">
            <span class="text-white text-lg font-bold">TRS</span>
          </div>
          <h1 class="text-2xl font-bold text-neutral-900 tracking-tight">The Rental Shop</h1>
          <p class="text-neutral-500 text-sm mt-1.5">Hardware Rental Management</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSignin" class="space-y-6">
          <!-- Username -->
          <div>
            <label for="username" class="block text-xs font-medium text-neutral-600 mb-2 uppercase tracking-wider">Username</label>
            <div class="relative border-b border-neutral-200 focus-within:border-primary-500 transition-colors duration-200">
              <Mail class="absolute left-0 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
              <input
                id="username"
                v-model="username"
                type="text"
                placeholder="Enter your username"
                @keydown="handleKeydown"
                class="w-full pl-6 pr-0 py-2 bg-transparent border-none text-sm text-neutral-900 placeholder:text-neutral-400 focus:outline-none focus:ring-0"
              />
            </div>
          </div>

          <!-- Password -->
          <div>
            <label for="password" class="block text-xs font-medium text-neutral-600 mb-2 uppercase tracking-wider">Password</label>
            <div class="relative border-b border-neutral-200 focus-within:border-primary-500 transition-colors duration-200">
              <Lock class="absolute left-0 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
              <input
                id="password"
                v-model="password"
                type="password"
                placeholder="Enter your password"
                @keydown="handleKeydown"
                class="w-full pl-6 pr-0 py-2 bg-transparent border-none text-sm text-neutral-900 placeholder:text-neutral-400 focus:outline-none focus:ring-0"
              />
            </div>
          </div>

          <!-- Error -->
          <transition name="toast">
            <div v-if="error" class="error-banner">
              <span class="w-1.5 h-1.5 bg-primary-500 flex-shrink-0"></span>
              {{ error }}
            </div>
          </transition>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="loading"
            class="btn-editorial-primary w-full"
          >
            <LogIn v-if="!loading" class="w-4 h-4" />
            <svg v-else class="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            {{ loading ? "Signing in..." : "Sign In" }}
          </button>
        </form>

        <p class="text-center text-neutral-400 text-xs mt-10">
          &copy; {{ new Date().getFullYear() }} The Rental Shop
        </p>
      </div>
    </div>
  </div>
</template>