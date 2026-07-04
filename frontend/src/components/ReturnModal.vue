<script setup>
import { ref, watch } from "vue";
import { X, CheckCircle, AlertCircle } from "lucide-vue-next";

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  device: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["close", "confirm"]);

const selectedCondition = ref("perfect");
const description = ref("");
const error = ref("");

const conditionOptions = [
  { value: "perfect", label: "Perfect", description: "Device is in perfect condition, ready for immediate use" },
  { value: "damaged", label: "Damaged", description: "Device has visible damage and needs repair" },
  { value: "other", label: "Other", description: "Other issues - please describe below" },
];

watch(() => props.show, (newVal) => {
  if (newVal) {
    // Reset form when modal opens
    selectedCondition.value = "perfect";
    description.value = "";
    error.value = "";
  }
});

const handleConfirm = () => {
  error.value = "";
  
  if (selectedCondition.value === "other" && !description.value.trim()) {
    error.value = "Please provide a description when selecting 'Other' condition";
    return;
  }
  
  emit("confirm", {
    return_condition: selectedCondition.value,
    description: description.value.trim() || null,
  });
};
</script>

<template>
  <transition name="modal">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="$emit('close')"></div>
      
      <!-- Modal -->
      <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-neutral-200 flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold text-neutral-900">Return Device</h3>
            <p v-if="device" class="text-sm text-neutral-500 mt-0.5">{{ device.name }}</p>
          </div>
          <button @click="$emit('close')" class="p-1 hover:bg-neutral-100 rounded-lg transition-colors">
            <X class="w-5 h-5 text-neutral-500" />
          </button>
        </div>
        
        <!-- Body -->
        <div class="p-6 space-y-6">
          <!-- Condition Selection -->
          <div>
            <label class="block text-sm font-medium text-neutral-900 mb-3">Device Condition</label>
            <div class="space-y-2">
              <button
                v-for="option in conditionOptions"
                :key="option.value"
                @click="selectedCondition = option.value"
                :class="[
                  'w-full text-left p-4 rounded-lg border-2 transition-all',
                  selectedCondition === option.value
                    ? 'border-neutral-900 bg-neutral-50'
                    : 'border-neutral-200 hover:border-neutral-300 bg-white'
                ]"
              >
                <div class="flex items-start gap-3">
                  <div :class="[
                    'w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5',
                    selectedCondition === option.value
                      ? 'border-neutral-900 bg-neutral-900'
                      : 'border-neutral-300'
                  ]">
                    <CheckCircle v-if="selectedCondition === option.value" class="w-3 h-3 text-white" />
                  </div>
                  <div class="flex-1">
                    <div class="font-medium text-neutral-900">{{ option.label }}</div>
                    <div class="text-xs text-neutral-500 mt-0.5">{{ option.description }}</div>
                  </div>
                </div>
              </button>
            </div>
          </div>
          
          <!-- Description (required for "other") -->
          <div v-if="selectedCondition === 'other'">
            <label class="block text-sm font-medium text-neutral-900 mb-2">
              Description <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="description"
              placeholder="Please describe the condition of the device..."
              rows="4"
              class="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-neutral-900 focus:outline-none focus:ring-0 transition-colors resize-none"
            ></textarea>
          </div>
          
          <!-- Error Message -->
          <div v-if="error" class="flex items-center gap-2 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">
            <AlertCircle class="w-4 h-4 flex-shrink-0" />
            <span>{{ error }}</span>
          </div>
        </div>
        
        <!-- Footer -->
        <div class="px-6 py-4 border-t border-neutral-200 bg-neutral-50 flex gap-3">
          <button
            @click="$emit('close')"
            class="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 bg-white border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleConfirm"
            class="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-neutral-900 rounded-lg hover:bg-neutral-800 transition-colors"
          >
            Confirm Return
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active > div > div:last-child,
.modal-leave-active > div > div:last-child {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-enter-from > div > div:last-child,
.modal-leave-to > div > div:last-child {
  transform: scale(0.95);
  opacity: 0;
}
</style>
