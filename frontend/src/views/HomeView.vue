<script setup>
import { Wrench, ArrowRight } from "lucide-vue-next";
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <div class="min-h-screen bg-neutral-50 bg-grid-pattern flex flex-col items-center justify-center p-4 relative overflow-hidden">
    <!-- Decorative elements -->
    <div class="fixed top-[-10rem] right-[-10rem] w-[30rem] h-[30rem] bg-gradient-to-br from-primary-600/8 to-transparent rounded-full pointer-events-none"></div>
    <div class="fixed bottom-[-10rem] left-[-10rem] w-[25rem] h-[25rem] bg-gradient-to-tr from-primary-600/5 to-transparent rounded-full pointer-events-none"></div>

    <div class="text-center max-w-lg relative">
      <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-600 to-primary-500 rounded-2xl shadow-xl shadow-primary-600/20 mb-6 ring-4 ring-primary-50">
        <Wrench class="w-8 h-8 text-white" />
      </div>

      <h1 class="text-4xl sm:text-5xl font-bold text-neutral-900 tracking-tight leading-tight">
        The Rental Shop
      </h1>
      <p class="text-neutral-500 mt-4 text-base leading-relaxed">
        Hardware Rental Management — browse, rent, and return equipment with ease.
      </p>

      <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
        <router-link
          to="/signin"
          class="inline-flex items-center gap-2 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 text-white font-semibold px-6 py-3 rounded-xl transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-xl hover:shadow-primary-600/30 active:scale-[0.98] text-sm"
        >
          Sign In
          <ArrowRight class="w-4 h-4" />
        </router-link>
        <router-link
          to="/signin"
          class="inline-flex items-center gap-2 bg-white border border-neutral-200 hover:border-neutral-300 text-neutral-700 font-medium px-6 py-3 rounded-xl transition-all duration-200 shadow-sm hover:shadow-md text-sm"
        >
          Get Started
        </router-link>
      </div>

      <p class="text-xs text-neutral-400 mt-12">
        Authorized personnel only &bull; &copy; {{ new Date().getFullYear() }} The Rental Shop
      </p>
    </div>
  </div>
</template>
