import { defineStore } from "pinia";
import { ref } from "vue";

const API_URL = import.meta.env.VITE_API_URL || "https://the-rental-shop.onrender.com";

export const useChatStore = defineStore("chat", () => {
  const messages = ref([]);
  const conversationHistory = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const addMessage = (role, content, recommendations = []) => {
    messages.value.push({
      id: messages.value.length + 1,
      role,
      content,
      recommendations,
      timestamp: new Date(),
    });
  };

  const sendMessage = async (userMessage, token, csrfToken) => {
    loading.value = true;
    error.value = null;

    try {
      addMessage("user", userMessage);

      const response = await fetch(`${API_URL}/api/ai/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          "X-CSRF-Token": csrfToken,
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

      addMessage("assistant", data.message, data.recommendations || []);

      // Update conversation history
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

      return data;
    } catch (err) {
      error.value = err.message;
      addMessage("assistant", "Sorry, I encountered an error. Please try again.");
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const clearChat = () => {
    messages.value = [];
    conversationHistory.value = [];
    error.value = null;
  };

  return {
    messages,
    conversationHistory,
    loading,
    error,
    addMessage,
    sendMessage,
    clearChat,
  };
});
