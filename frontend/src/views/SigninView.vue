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
  <div class="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Header -->
      <div class="text-center mb-12">
        <div class="inline-flex items-center justify-center w-12 h-12 bg-primary-600 rounded-lg mb-4">
          <Lock class="w-6 h-6 text-white" />
        </div>
        <h1 class="text-3xl font-light text-neutral-900 tracking-tight">The Rental Shop</h1>
        <p class="text-neutral-500 mt-2 text-sm font-light">Hardware Rental Management</p>
      </div>

      <!-- Form Card -->
      <div class="bg-white rounded-lg border border-neutral-200 p-8 shadow-sm">
        <form @submit.prevent="handleSignin" class="space-y-6">
          <!-- Username Field -->
          <div>
            <label for="username" class="block text-sm font-medium text-neutral-700 mb-2">
              Username
            </label>
            <div class="relative">
              <Mail class="absolute left-3 top-3 w-5 h-5 text-neutral-400" />
              <input
                id="username"
                v-model="username"
                type="text"
                placeholder="Enter your username"
                @keydown="handleKeydown"
                class="w-full pl-10 pr-4 py-2.5 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition text-sm"
              />
            </div>
          </div>

          <!-- Password Field -->
          <div>
            <label for="password" class="block text-sm font-medium text-neutral-700 mb-2">
              Password
            </label>
            <div class="relative">
              <Lock class="absolute left-3 top-3 w-5 h-5 text-neutral-400" />
              <input
                id="password"
                v-model="password"
                type="password"
                placeholder="Enter your password"
                @keydown="handleKeydown"
                class="w-full pl-10 pr-4 py-2.5 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition text-sm"
              />
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-primary-50 border border-primary-200 text-primary-700 px-4 py-3 rounded-lg text-sm">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-neutral-300 text-white font-medium py-2.5 px-4 rounded-lg transition duration-200 flex items-center justify-center gap-2 text-sm"
          >
            <LogIn class="w-4 h-4" />
            {{ loading ? "Signing in..." : "Sign In" }}
          </button>
        </form>


      </div>
    </div>
  </div>
</template>
