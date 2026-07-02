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

const getStatusColor = (status) => {
  const colors = {
    Available: "bg-green-100 text-green-700",
    "In Use": "bg-blue-100 text-blue-700",
    Repair: "bg-yellow-100 text-yellow-700",
    Unknown: "bg-neutral-100 text-neutral-700",
  };
  return colors[status] || "bg-neutral-100 text-neutral-700";
};
</script>

<template>
  <div class="bg-white rounded-lg border border-neutral-200 hover:border-neutral-300 hover:shadow-sm transition p-4">
    <div class="flex justify-between items-start mb-3">
      <div class="flex-1">
        <h3 class="font-medium text-neutral-900 text-sm">{{ device.name }}</h3>
        <p class="text-xs text-neutral-500 mt-1">{{ device.brand }}</p>
      </div>
      <span :class="['px-2 py-1 rounded-full text-xs font-medium', getStatusColor(device.status)]">
        {{ device.status }}
      </span>
    </div>

    <div class="space-y-2 mb-4 text-xs text-neutral-600">
      <p v-if="device.purchase_date">
        <span class="font-medium text-neutral-700">Purchased:</span> {{ new Date(device.purchase_date).toLocaleDateString() }}
      </p>
      <p v-if="device.assigned_to">
        <span class="font-medium text-neutral-700">Assigned to:</span> {{ device.assigned_to }}
      </p>
      <p v-if="device.notes" class="text-neutral-700">{{ device.notes }}</p>
    </div>

    <div class="flex gap-2">
      <button
        v-if="showRentButton"
        @click="$emit('rent', device)"
        class="flex-1 bg-primary-600 hover:bg-primary-700 text-white py-2 px-3 rounded-lg text-xs font-medium transition flex items-center justify-center gap-1"
      >
        <Package class="w-3 h-3" />
        Rent
      </button>
      <button
        v-if="showReturnButton"
        @click="$emit('return', device)"
        class="flex-1 bg-neutral-600 hover:bg-neutral-700 text-white py-2 px-3 rounded-lg text-xs font-medium transition flex items-center justify-center gap-1"
      >
        <Trash2 class="w-3 h-3" />
        Return
      </button>
    </div>
  </div>
</template>
