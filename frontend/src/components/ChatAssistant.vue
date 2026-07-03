<script setup>
import { ref, computed, nextTick, onMounted } from "vue";
import { Send, Loader, Bot, Circle } from "lucide-vue-next";
import { useAuthStore } from "../stores/auth";

const props = defineProps({
  token: {
    type: String,
    required: true,
  },
});

const authStore = useAuthStore();

const messages = ref([]);
const userInput = ref("");
const loading = ref(false);
const conversationHistory = ref([]);
const messagesContainer = ref(null);

onMounted(() => {
  // Add initial greeting
  messages.value.push({
    id: 1,
    role: "assistant",
    content: "Hello! I'm your AI assistant. Tell me what kind of device you need, and I'll help you find the perfect match from our inventory.",
    timestamp: new Date(),
  });
});

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const sendMessage = async () => {
  if (!userInput.value.trim()) return;

  const userMessage = userInput.value;
  userInput.value = "";

  // Add user message to UI
  messages.value.push({
    id: messages.value.length + 1,
    role: "user",
    content: userMessage,
    timestamp: new Date(),
  });

  await scrollToBottom();

  loading.value = true;

  try {
    const response = await fetch("/api/ai/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${props.token}`,
        "X-CSRF-Token": authStore.csrfToken,
      },
      credentials: "include",
      body: JSON.stringify({
        message: userMessage,
        conversation_history: conversationHistory.value,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();

    // Add assistant message to UI
    messages.value.push({
      id: messages.value.length + 1,
      role: "assistant",
      content: data.message,
      recommendations: data.recommendations || [],
      timestamp: new Date(),
    });

    // Update conversation history for context
    conversationHistory.value.push({
      role: "user",
      content: userMessage,
    });
    conversationHistory.value.push({
      role: "assistant",
      content: data.message,
    });

    // Keep only last 6 messages for context
    if (conversationHistory.value.length > 6) {
      conversationHistory.value = conversationHistory.value.slice(-6);
    }
  } catch (error) {
    console.error("Chat error:", error);
    messages.value.push({
      id: messages.value.length + 1,
      role: "assistant",
      content: "Sorry, I encountered an error. Please try again.",
      timestamp: new Date(),
    });
  } finally {
    loading.value = false;
    await scrollToBottom();
  }
};

const handleKeydown = (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
};

const emit = defineEmits(['rent']);

const rentDevice = (device) => {
  emit("rent", device);
};

const getStatusDot = (status) => {
  const colors = {
    Available: "text-amber-500",
    "In Use": "text-blue-500",
  };
  return colors[status] || "text-neutral-400";
};
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Messages Container -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 space-y-4 bg-neutral-50/80"
    >
      <div
        v-for="msg in messages"
        :key="msg.id"
        :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <div
          :class="[
            'max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed',
            msg.role === 'user'
              ? 'bg-gradient-to-br from-primary-600 to-primary-500 text-white shadow-md shadow-primary-600/15'
              : 'bg-white border border-neutral-200 text-neutral-900 shadow-sm',
          ]"
        >
          <p>{{ msg.content }}</p>

          <!-- Recommendations -->
          <div v-if="msg.recommendations && msg.recommendations.length > 0" class="mt-4 space-y-3">
            <div
              v-for="rec in msg.recommendations"
              :key="rec.id"
              class="bg-neutral-50 border border-neutral-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow"
            >
              <div class="flex justify-between items-start gap-3">
                <div class="min-w-0">
                  <p class="font-semibold text-neutral-900 text-sm">{{ rec.name }}</p>
                  <p class="text-xs text-neutral-500 mt-0.5 font-medium tracking-wide uppercase">{{ rec.brand }}</p>
                  <p class="text-xs text-neutral-600 mt-2 leading-relaxed">{{ rec.reason }}</p>
                </div>
                <span
                  v-if="rec.status === 'Available'"
                  class="inline-flex items-center gap-1 px-2 py-1 bg-amber-50 border border-amber-200 text-amber-700 rounded-full text-xs font-medium flex-shrink-0"
                >
                  <Circle class="w-1.5 h-1.5 fill-amber-500 text-amber-500" />
                  {{ rec.status }}
                </span>
                <span
                  v-else
                  class="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 border border-blue-200 text-blue-700 rounded-full text-xs font-medium flex-shrink-0"
                >
                  <Circle class="w-1.5 h-1.5 fill-blue-500 text-blue-500" />
                  {{ rec.status }}
                </span>
              </div>
              <button
                v-if="rec.status === 'Available'"
                class="mt-3 w-full py-2.5 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 text-white text-xs font-semibold rounded-xl transition-all duration-200 shadow-sm hover:shadow-md active:scale-[0.98]"
                @click="rentDevice(rec)"
              >
                Rent This Device
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="loading" class="flex justify-start">
        <div class="flex items-center gap-2.5 px-4 py-3 bg-white border border-neutral-200 rounded-2xl shadow-sm">
          <Loader class="w-4 h-4 text-primary-600 animate-spin" />
          <span class="text-sm text-neutral-500">Thinking...</span>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="border-t border-neutral-200 p-4 bg-white">
      <div class="flex gap-2">
        <textarea
          v-model="userInput"
          @keydown="handleKeydown"
          :disabled="loading"
          placeholder="Ask me about devices..."
          class="flex-1 px-4 py-2.5 border border-neutral-200 rounded-xl text-sm resize-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none transition disabled:bg-neutral-50 placeholder:text-neutral-400 bg-neutral-50/50"
          rows="2"
        />
        <button
          @click="sendMessage"
          :disabled="loading || !userInput.trim()"
          class="px-4 py-2.5 bg-gradient-to-br from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 disabled:from-neutral-300 disabled:to-neutral-300 text-white rounded-xl transition-all duration-200 flex items-center justify-center shadow-sm hover:shadow-md active:scale-[0.98] disabled:shadow-none"
        >
          <Send class="w-4 h-4" />
        </button>
      </div>
      <p class="text-xs text-neutral-400 mt-2">Press Enter to send &bull; Shift+Enter for new line</p>
    </div>
  </div>
</template>
