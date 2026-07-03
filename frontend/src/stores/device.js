import { defineStore } from "pinia";
import { ref, computed } from "vue";

// API configuration with timeout for Render cold starts
const API_TIMEOUT = 120000; // 2 minutes for Render cold starts

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

export const useDeviceStore = defineStore("device", () => {
  const availableDevices = ref([]);
  const rentedDevices = ref([]);
  const deviceHistory = ref([]);
  const allDevices = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const currentPage = ref(1);
  const itemsPerPage = ref(12);
  const totalDevices = ref(0);

  const fetchAvailableDevices = async (token, page = 1, limit = 12) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetchWithTimeout(getApiUrl(`api/hardware?status=Available&skip=${(page - 1) * limit}&limit=${limit}`), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Failed to fetch devices");
      const devices = await response.json();
      availableDevices.value = devices;
      totalDevices.value = devices.length;
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  const fetchRentedDevices = async (token, page = 1, limit = 12) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetchWithTimeout(getApiUrl(`api/hardware?status=In+Use&skip=${(page - 1) * limit}&limit=${limit}`), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Failed to fetch devices");
      const devices = await response.json();
      rentedDevices.value = devices;
      totalDevices.value = devices.length;
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  const fetchDeviceHistory = async (token) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetchWithTimeout(getApiUrl("api/hardware"), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Failed to fetch history");
      deviceHistory.value = await response.json();
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  const fetchAllDevices = async (token, page = 1, limit = 100) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetchWithTimeout(getApiUrl(`api/hardware?skip=0&limit=${limit}`), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Failed to fetch all devices");
      const devices = await response.json();
      allDevices.value = devices;
      totalDevices.value = devices.length;
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  const rentDevice = async (token, hardwareId, csrfToken) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetchWithTimeout(getApiUrl(`api/hardware/${hardwareId}/rent`), {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "X-CSRF-Token": csrfToken,
        },
        credentials: "include",
      });
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to rent device");
      }
      const device = await response.json();
      await fetchAllDevices(token);
      return device;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const returnDevice = async (token, hardwareId, csrfToken) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetchWithTimeout(getApiUrl(`api/hardware/${hardwareId}/return`), {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "X-CSRF-Token": csrfToken,
        },
        credentials: "include",
      });
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to return device");
      }
      const device = await response.json();
      await fetchAllDevices(token);
      return device;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const totalPages = computed(() => Math.ceil(totalDevices.value / itemsPerPage.value));

  return {
    availableDevices,
    rentedDevices,
    deviceHistory,
    allDevices,
    loading,
    error,
    currentPage,
    itemsPerPage,
    totalDevices,
    totalPages,
    fetchAvailableDevices,
    fetchRentedDevices,
    fetchDeviceHistory,
    fetchAllDevices,
    rentDevice,
    returnDevice,
  };
});
