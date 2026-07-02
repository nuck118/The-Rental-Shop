import { defineStore } from "pinia";
import { ref } from "vue";

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
      const response = await fetch("/api/hardware?status=Available&skip=" + (page - 1) * limit + "&limit=" + limit, {
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
      const response = await fetch("/api/hardware?status=In+Use&skip=" + (page - 1) * limit + "&limit=" + limit, {
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
      const response = await fetch("/api/hardware", {
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

  const fetchAllDevices = async (token, page = 1, limit = 12) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch("/api/hardware?skip=" + (page - 1) * limit + "&limit=" + limit, {
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
  };
});
