<script setup>
import { Package, Trash2, Circle } from "lucide-vue-next";

defineProps({
  device: {
    type: Object,
    required: true,
  },
  showRentButton: {
    type: Boolean,
    default: false,
  },
  showReturnButton: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["rent", "return"]);

const getStatusColor = (status) => {
  const colors = {
    Available: "bg-amber-50 text-amber-700 border-amber-200",
    "In Use": "bg-blue-50 text-blue-700 border-blue-200",
    Repair: "bg-yellow-50 text-yellow-700 border-yellow-200",
    Unknown: "bg-neutral-100 text-neutral-600 border-neutral-200",
  };
  return colors[status] || "bg-neutral-100 text-neutral-600 border-neutral-200";
};

const getStatusDot = (status) => {
  const colors = {
    Available: "text-amber-500",
    "In Use": "text-blue-500",
    Repair: "text-yellow-500",
    Unknown: "text-neutral-400",
  };
  return colors[status] || "text-neutral-400";
};
</script>

<template>
  <div class="group bg-white rounded-xl border border-neutral-200 hover:border-neutral-300 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 p-5">
    <div class="flex justify-between items-start mb-4">
      <div class="flex-1 min-w-0">
        <h3 class="font-semibold text-neutral-900 text-base leading-tight truncate">{{ device.name }}</h3>
        <p class="text-xs text-neutral-500 mt-1 font-medium tracking-wide uppercase">{{ device.brand }}</p>
      </div>
      <span :class="['inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border', getStatusColor(device.status)]">
        <Circle :class="['w-2 h-2 fill-current', getStatusDot(device.status)]" />
        {{ device.status }}
      </span>
    </div>

    <div class="space-y-1.5 mb-5 text-xs text-neutral-600">
      <p v-if="device.purchase_date" class="flex items-center gap-2">
        <span class="inline-block w-1.5 h-1.5 rounded-full bg-neutral-300 flex-shrink-0"></span>
        <span class="font-medium text-neutral-500">Purchased:</span>
        <span>{{ new Date(device.purchase_date).toLocaleDateString() }}</span>
      </p>
      <p v-if="device.assigned_to" class="flex items-center gap-2">
        <span class="inline-block w-1.5 h-1.5 rounded-full bg-neutral-300 flex-shrink-0"></span>
        <span class="font-medium text-neutral-500">Assigned to:</span>
        <span>{{ device.assigned_to }}</span>
      </p>
      <p v-if="device.notes" class="mt-2 text-neutral-600 italic pl-3.5 border-l-2 border-neutral-200 leading-relaxed">{{ device.notes }}</p>
    </div>

    <div class="flex gap-2">
      <button
        v-if="showRentButton"
        @click="$emit('rent', device)"
        class="flex-1 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 text-white py-2.5 px-3 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center justify-center gap-1.5 shadow-sm hover:shadow-md active:scale-[0.98]"
      >
        <Package class="w-3.5 h-3.5" />
        Rent Now
      </button>
      <button
        v-if="showReturnButton"
        @click="$emit('return', device)"
        class="flex-1 bg-neutral-700 hover:bg-neutral-800 text-white py-2.5 px-3 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center justify-center gap-1.5 shadow-sm hover:shadow-md active:scale-[0.98]"
      >
        <Trash2 class="w-3.5 h-3.5" />
        Return
      </button>
    </div>
  </div>
</template>
