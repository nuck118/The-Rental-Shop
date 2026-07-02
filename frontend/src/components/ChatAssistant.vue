<script setup>
import { ref, computed, nextTick, onMounted } from "vue";
import { Send, Loader } from "lucide-vue-next";

const props = defineProps({
  token: {
    type: String,
    required: true,
  },
});

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
      },
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

const rentDevice = (deviceId) => {
  console.log('Rent device:', deviceId);
  // TODO: Implement rent functionality
  alert(`Renting device ID: ${deviceId}`);
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
        v-for="msg in messages"
        :key="msg.id"
        :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <div
          :class="[
            'max-w-xs px-4 py-2 rounded-lg text-sm',
            msg.role === 'user'
              ? 'bg-primary-600 text-white'
              : 'bg-white border border-neutral-200 text-neutral-900',
          ]"
        >
          <p class="leading-relaxed">{{ msg.content }}</p>

          <!-- Recommendations -->
          <div v-if="msg.recommendations && msg.recommendations.length > 0" class="mt-3 space-y-2">
            <div
              v-for="rec in msg.recommendations"
              :key="rec.id"
              class="bg-white border border-primary-200 rounded-lg p-3 shadow-sm"
            >
              <div class="flex justify-between items-start">
                <div>
                  <p class="font-semibold text-neutral-900">{{ rec.name }}</p>
                  <p class="text-sm text-neutral-600">{{ rec.brand }}</p>
                  <p class="text-xs text-neutral-500 mt-1">{{ rec.reason }}</p>
                </div>
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium',
                    rec.status === 'Available'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-blue-100 text-blue-700',
                  ]"
                >
                  {{ rec.status }}
                </span>
              </div>
              <button
                v-if="rec.status === 'Available'"
                class="mt-3 w-full py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded transition"
                @click="rentDevice(rec.id)"
              >
                Rent This Device
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="loading" class="flex justify-start">
        <div class="flex items-center gap-2 px-4 py-2 bg-white border border-neutral-200 rounded-lg">
          <Loader class="w-4 h-4 text-primary-600 animate-spin" />
          <span class="text-sm text-neutral-600">Thinking...</span>
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
          class="flex-1 px-3 py-2 border border-neutral-200 rounded-lg text-sm resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition disabled:bg-neutral-50"
          rows="2"
        />
        <button
          @click="sendMessage"
          :disabled="loading || !userInput.trim()"
          class="px-3 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-neutral-300 text-white rounded-lg transition flex items-center justify-center"
        >
          <Send class="w-4 h-4" />
        </button>
      </div>
      <p class="text-xs text-neutral-500 mt-2">Press Enter to send, Shift+Enter for new line</p>
    </div>
  </div>
</template>
