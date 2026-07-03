<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { Mail, Lock, LogIn, Wrench } from "lucide-vue-next";

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
  <div class="min-h-screen bg-neutral-50 bg-grid-pattern flex items-center justify-center p-4">
    <!-- Decorative corner accents -->
    <div class="fixed top-0 left-0 w-72 h-72 bg-gradient-to-br from-primary-600/5 to-transparent rounded-br-full pointer-events-none"></div>
    <div class="fixed bottom-0 right-0 w-96 h-96 bg-gradient-to-tl from-primary-600/5 to-transparent rounded-tl-full pointer-events-none"></div>

    <div class="w-full max-w-md relative">
      <!-- Header -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-primary-600 to-primary-500 rounded-xl shadow-lg shadow-primary-600/20 mb-5 ring-4 ring-primary-50">
          <Wrench class="w-7 h-7 text-white" />
        </div>
        <h1 class="text-3xl font-bold text-neutral-900 tracking-tight">The Rental Shop</h1>
        <p class="text-neutral-500 mt-2 text-sm">Hardware Rental Management</p>
      </div>

      <!-- Form Card -->
      <div class="bg-white rounded-2xl border border-neutral-200 p-8 shadow-xl shadow-neutral-200/50">
        <form @submit.prevent="handleSignin" class="space-y-5">
          <!-- Username Field -->
          <div>
            <label for="username" class="block text-sm font-semibold text-neutral-700 mb-1.5">
              Username
            </label>
            <div class="relative group">
              <Mail class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 group-focus-within:text-primary-500 transition-colors" />
              <input
                id="username"
                v-model="username"
                type="text"
                placeholder="Enter your username"
                @keydown="handleKeydown"
                class="w-full pl-10 pr-4 py-2.5 border border-neutral-200 rounded-xl focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none transition text-sm bg-neutral-50/50 focus:bg-white"
              />
            </div>
          </div>

          <!-- Password Field -->
          <div>
            <label for="password" class="block text-sm font-semibold text-neutral-700 mb-1.5">
              Password
            </label>
            <div class="relative group">
              <Lock class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 group-focus-within:text-primary-500 transition-colors" />
              <input
                id="password"
                v-model="password"
                type="password"
                placeholder="Enter your password"
                @keydown="handleKeydown"
                class="w-full pl-10 pr-4 py-2.5 border border-neutral-200 rounded-xl focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none transition text-sm bg-neutral-50/50 focus:bg-white"
              />
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm flex items-center gap-2">
            <div class="w-1.5 h-1.5 rounded-full bg-red-500 flex-shrink-0"></div>
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 disabled:from-neutral-300 disabled:to-neutral-300 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 text-sm shadow-lg shadow-primary-600/20 hover:shadow-xl hover:shadow-primary-600/30 active:scale-[0.98] disabled:shadow-none"
          >
            <LogIn class="w-4 h-4" />
            {{ loading ? "Signing in..." : "Sign In" }}
          </button>
        </form>

        <!-- Footer -->
        <p class="text-center text-xs text-neutral-400 mt-6">
          Authorized personnel only &bull; The Rental Shop
        </p>
      </div>
    </div>
  </div>
</template>
