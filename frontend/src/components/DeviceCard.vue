<script setup>
import { Package, Trash2 } from "lucide-vue-next";

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

const getStatusBadge = (status) => {
  const map = {
    Available: "badge-editorial-available",
    "In Use": "badge-editorial-inuse",
    Repair: "badge-editorial-repair",
    Unknown: "badge-editorial-unknown",
  };
  return map[status] || "badge-editorial-unknown";
};
</script>

<template>
  <div class="card-editorial-hover p-5 flex flex-col h-full animate-fade-in-up">
    <!-- Header -->
    <div class="flex justify-between items-start mb-4">
      <div class="flex-1 min-w-0">
        <h3 class="font-semibold text-neutral-900 text-sm truncate">{{ device.name }}</h3>
        <p v-if="device.brand" class="text-xs text-neutral-500 mt-1 truncate">{{ device.brand }}</p>
      </div>
      <span :class="['flex-shrink-0 ml-2', getStatusBadge(device.status)]">
        {{ device.status }}
      </span>
    </div>

    <!-- Details -->
    <div class="space-y-1.5 mb-5 flex-1 text-xs text-neutral-500">
      <p v-if="device.purchase_date">
        <span class="text-neutral-400">Purchased</span>
        <span class="text-neutral-700 ml-1">{{ new Date(device.purchase_date).toLocaleDateString() }}</span>
      </p>
      <p v-if="device.assigned_to">
        <span class="text-neutral-400">Assigned to</span>
        <span class="text-neutral-700 ml-1">{{ device.assigned_to }}</span>
      </p>
      <p v-if="device.notes" class="text-neutral-600 mt-2 leading-relaxed line-clamp-2">{{ device.notes }}</p>
    </div>

    <!-- Actions -->
    <div class="flex gap-2 mt-auto pt-4 border-t border-neutral-100">
      <button
        v-if="showRentButton"
        @click="$emit('rent', device)"
        class="btn-editorial-primary flex-1 py-2 text-xs"
      >
        <Package class="w-3.5 h-3.5" />
        Rent
      </button>
      <button
        v-if="showReturnButton"
        @click="$emit('return', device)"
        class="btn-editorial-secondary flex-1 py-2 text-xs"
      >
        <Trash2 class="w-3.5 h-3.5" />
        Return
      </button>
    </div>
  </div>
</template>