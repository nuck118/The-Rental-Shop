<script setup>
import { ref, computed, nextTick, onMounted } from "vue";
import { Send, Loader } from "lucide-vue-next";
import { useAuthStore } from "../stores/auth";

const API_TIMEOUT = 120000;

const getApiUrl = (path) => {
  const base = import.meta.env.VITE_API_URL?.replace(/\/+$/, '') || "https://the-rental-shop.onrender.com";
  return `${base}/${path.replace(/^\/+/, '')}`;
};

const fetchWithTimeout = (url, options = {}) => {
  return Promise.race([
    fetch(url, { ...options, signal: AbortSignal.timeout(API_TIMEOUT) }),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error("Request timeout - server may be waking up, please try again")), API_TIMEOUT)
    ),
  ]);
};

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

  messages.value.push({
    id: messages.value.length + 1,
    role: "user",
    content: userMessage,
    timestamp: new Date(),
  });

  await scrollToBottom();

  loading.value = true;

  try {
    const response = await fetchWithTimeout(getApiUrl("api/ai/chat"), {
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

    messages.value.push({
      id: messages.value.length + 1,
      role: "assistant",
      content: data.message,
      recommendations: data.recommendations || [],
      timestamp: new Date(),
    });

    conversationHistory.value.push({
      role: "user",
      content: userMessage,
    });
    conversationHistory.value.push({
      role: "assistant",
      content: data.message,
    });

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
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Messages Container -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 space-y-4 bg-neutral-50"
    >
      <div
        v-for="(msg, index) in messages"
        :key="msg.id"
        :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <div
          :class="[
            'max-w-[85%] sm:max-w-xs px-4 py-2.5 text-sm leading-relaxed animate-fade-in-up',
            msg.role === 'user'
              ? 'bg-neutral-900 text-white'
              : 'bg-white border border-neutral-200 text-neutral-900',
          ]"
        >
          <p>{{ msg.content }}</p>

          <!-- Recommendations -->
          <div v-if="msg.recommendations && msg.recommendations.length > 0" class="mt-3 space-y-2">
            <div
              v-for="rec in msg.recommendations"
              :key="rec.id"
              class="bg-neutral-50 border border-neutral-200 p-3"
            >
              <div class="flex justify-between items-start gap-2">
                <div class="flex-1 min-w-0">
                  <p class="font-semibold text-neutral-900 text-sm truncate">{{ rec.name }}</p>
                  <p class="text-xs text-neutral-600 truncate">{{ rec.brand }}</p>
                  <p class="text-xs text-neutral-500 mt-1.5 line-clamp-2">{{ rec.reason }}</p>
                </div>
                <span
                  :class="[
                    'px-2 py-0.5 text-xs font-medium flex-shrink-0',
                    rec.status === 'Available'
                      ? 'bg-neutral-100 text-neutral-700'
                      : 'bg-primary-50 text-primary-700',
                  ]"
                >
                  {{ rec.status }}
                </span>
              </div>
              <button
                v-if="rec.status === 'Available'"
                class="mt-2.5 w-full py-2 bg-neutral-900 hover:bg-neutral-800 text-white text-xs font-medium transition-colors"
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
        <div class="flex items-center gap-2 px-4 py-2.5 bg-white border border-neutral-200">
          <Loader class="w-3.5 h-3.5 text-neutral-900 animate-spin" />
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
          class="flex-1 px-0 py-2 border-b border-neutral-200 bg-transparent text-sm resize-none placeholder:text-neutral-400 focus:border-neutral-900 focus:outline-none focus:ring-0 transition-colors duration-200 disabled:opacity-50"
          rows="2"
        />
        <button
          @click="sendMessage"
          :disabled="loading || !userInput.trim()"
          class="px-4 py-2 bg-neutral-900 hover:bg-neutral-800 disabled:bg-neutral-200 disabled:text-neutral-400 text-white text-sm transition-colors flex items-center justify-center flex-shrink-0"
        >
          <Send class="w-4 h-4" />
        </button>
      </div>
      <p class="text-xs text-neutral-400 mt-2 hidden sm:block">Press Enter to send, Shift+Enter for new line</p>
    </div>
  </div>
</template>