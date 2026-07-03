import { defineStore } from "pinia";
import { ref, computed } from "vue";

const storedUser = localStorage.getItem("user");

export const useAuthStore = defineStore("auth", () => {
  const user = ref(storedUser ? JSON.parse(storedUser) : null);
  const token = ref(localStorage.getItem("token") || null);
  const csrfToken = ref(null);
  const isAuthenticated = computed(() => !!token.value);

  /**
   * Fetch a fresh CSRF token from the backend.
   * The backend sets the signed token as an HttpOnly cookie.
   */
  const fetchCsrfToken = async () => {
    try {
      const response = await fetch("/api/auth/csrf-token", {
        method: "GET",
        credentials: "include",
      });
      if (!response.ok) {
        throw new Error("Failed to fetch CSRF token");
      }
      const data = await response.json();
      csrfToken.value = data.csrf_token;
      return data.csrf_token;
    } catch (error) {
      console.error("CSRF token fetch failed:", error);
      return null;
    }
  };

  const login = async (username, password) => {
    try {
      // Ensure we have a CSRF token before submitting the login form
      const currentCsrfToken = csrfToken.value || (await fetchCsrfToken());
      if (!currentCsrfToken) {
        throw new Error("CSRF token not available");
      }

      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": currentCsrfToken,
        },
        credentials: "include",
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Invalid credentials");
      }

      const data = await response.json();
      token.value = data.token;
      user.value = data.user;
      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      // Refresh CSRF token after login
      await fetchCsrfToken();
      return true;
    } catch (error) {
      console.error("Login failed:", error);
      return false;
    }
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    csrfToken.value = null;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };

  return {
    user,
    token,
    csrfToken,
    isAuthenticated,
    fetchCsrfToken,
    login,
    logout,
  };
});
