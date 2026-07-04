import { defineStore } from "pinia";
import { ref, computed } from "vue";

// API configuration with timeout for Render cold starts
const API_TIMEOUT = 120000; // 2 minutes for Render cold starts

// Inactivity timeout: 30 minutes
const INACTIVITY_TIMEOUT_MS = 30 * 60 * 1000;
const INACTIVITY_CHECK_INTERVAL_MS = 30 * 1000; // check every 30 seconds

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

const storedUser = localStorage.getItem("user");

export const useAuthStore = defineStore("auth", () => {
  const user = ref(storedUser ? JSON.parse(storedUser) : null);
  const token = ref(localStorage.getItem("token") || null);
  const csrfToken = ref(null);
  const isAuthenticated = computed(() => !!token.value);

  // Inactivity tracking
  let lastActivityTime = Date.now();
  let inactivityInterval = null;
  let activityListeners = [];

  /**
   * Reset the inactivity timer on user activity.
   */
  const resetInactivityTimer = () => {
    lastActivityTime = Date.now();
  };

  /**
   * Check if the user has been inactive too long and log them out if so.
   */
  const checkInactivity = () => {
    if (!token.value) return; // not logged in, nothing to check
    const elapsed = Date.now() - lastActivityTime;
    if (elapsed >= INACTIVITY_TIMEOUT_MS) {
      logout();
    }
  };

  /**
   * Start monitoring for inactivity. Sets up event listeners and a periodic check.
   */
  const startInactivityMonitor = () => {
    // Clear any existing monitor first
    stopInactivityMonitor();

    // Reset the timer
    resetInactivityTimer();

    // Set up event listeners for user activity
    const events = ["mousedown", "keydown", "mousemove", "scroll", "touchstart", "click", "wheel"];
    events.forEach((event) => {
      const handler = () => resetInactivityTimer();
      window.addEventListener(event, handler, { passive: true });
      activityListeners.push({ event, handler });
    });

    // Start periodic check
    inactivityInterval = setInterval(checkInactivity, INACTIVITY_CHECK_INTERVAL_MS);
  };

  /**
   * Stop monitoring for inactivity. Cleans up listeners and interval.
   */
  const stopInactivityMonitor = () => {
    if (inactivityInterval) {
      clearInterval(inactivityInterval);
      inactivityInterval = null;
    }
    activityListeners.forEach(({ event, handler }) => {
      window.removeEventListener(event, handler);
    });
    activityListeners = [];
  };

  /**
   * Fetch a fresh CSRF token from the backend.
   * The backend sets the signed token as an HttpOnly cookie.
   */
  const fetchCsrfToken = async () => {
    try {
      const response = await fetchWithTimeout(getApiUrl("api/auth/csrf-token"), {
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
      // Fetch a CSRF token (returns empty string if CSRF is disabled on backend)
      const currentCsrfToken = csrfToken.value || (await fetchCsrfToken());

      const headers = {
        "Content-Type": "application/json",
      };
      // Only send CSRF header if we have a valid token
      if (currentCsrfToken) {
        headers["X-CSRF-Token"] = currentCsrfToken;
      }

      const response = await fetchWithTimeout(getApiUrl("api/auth/login"), {
        method: "POST",
        headers,
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
      // Start inactivity monitoring on successful login
      startInactivityMonitor();
      return true;
    } catch (error) {
      console.error("Login failed:", error);
      return false;
    }
  };

  const logout = () => {
    // Stop inactivity monitoring
    stopInactivityMonitor();
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
    startInactivityMonitor,
    stopInactivityMonitor,
  };
});