<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useDeviceStore } from "../stores/device";
import DeviceCard from "../components/DeviceCard.vue";
import { Package, Truck, History, LogOut, Menu, X, Bot, ChevronLeft, ChevronRight, Search } from "lucide-vue-next";

const router = useRouter();
const authStore = useAuthStore();
const deviceStore = useDeviceStore();

const activeTab = ref("available");
const showProfileMenu = ref(false);
const showChatPanel = ref(false);
const showChatButton = ref(true);

// Search and filter state
const searchQuery = ref("");
const statusFilter = ref("all");
const brandFilter = ref("all");
const deviceTypeFilter = ref("all");

// Get unique brands from devices
const brands = computed(() => {
  const allBrands = new Set();
  deviceStore.allDevices.forEach(d => {
    if (d.brand) allBrands.add(d.brand);
  });
  return ["all", ...Array.from(allBrands).sort()];
});

// Filter devices based on search and filters
const filteredDevices = computed(() => {
  let devices = deviceStore.allDevices;
  
  if (statusFilter.value !== "all") {
    devices = devices.filter(d => d.status === statusFilter.value);
  }
  
  if (brandFilter.value !== "all") {
    devices = devices.filter(d => d.brand === brandFilter.value);
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    devices = devices.filter(d => 
      d.name.toLowerCase().includes(query) || 
      d.brand.toLowerCase().includes(query)
    );
  }
  
  return devices;
});

// Calculate pagination for filtered devices
const filteredTotalPages = computed(() => Math.ceil(filteredDevices.value.length / deviceStore.itemsPerPage));

const filteredPages = computed(() => {
  const pages = [];
  const total = filteredTotalPages.value;
  const current = deviceStore.currentPage;
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i);
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i);
      pages.push("...");
      pages.push(total);
    } else if (current >= total - 3) {
      pages.push(1);
      pages.push("...");
      for (let i = total - 4; i <= total; i++) pages.push(i);
    } else {
      pages.push(1);
      pages.push("...");
      for (let i = current - 1; i <= current + 1; i++) pages.push(i);
      pages.push("...");
      pages.push(total);
    }
  }
  return pages;
});

const paginatedDevices = computed(() => {
  const start = (deviceStore.currentPage - 1) * deviceStore.itemsPerPage;
  return filteredDevices.value.slice(start, start + deviceStore.itemsPerPage);
});

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push("/signin");
    return;
  }

  await deviceStore.fetchAvailableDevices(authStore.token, 1, deviceStore.itemsPerPage);
  await deviceStore.fetchRentedDevices(authStore.token, 1, deviceStore.itemsPerPage);
  await deviceStore.fetchDeviceHistory(authStore.token);
  await deviceStore.fetchAllDevices(authStore.token, 1, deviceStore.itemsPerPage);
});

const handleLogout = () => {
  authStore.logout();
  router.push("/signin");
};

const handleRent = (device) => {
  alert(`Renting ${device.name} - Feature coming soon`);
};

const handleReturn = (device) => {
  alert(`Returning ${device.name} - Feature coming soon`);
};

const tabs = [
  { id: "available", label: "Available Devices", icon: Package },
  { id: "rented", label: "Rented Devices", icon: Truck },
  { id: "history", label: "History", icon: History },
  { id: "all", label: "All Devices", icon: Package },
];

const handlePageChange = (page) => {
  if (page < 1 || page > deviceStore.totalPages) return;
  deviceStore.currentPage = page;
  
  if (activeTab.value === "available") {
    deviceStore.fetchAvailableDevices(authStore.token, page, deviceStore.itemsPerPage);
  } else if (activeTab.value === "rented") {
    deviceStore.fetchRentedDevices(authStore.token, page, deviceStore.itemsPerPage);
  } else if (activeTab.value === "all") {
    deviceStore.fetchAllDevices(authStore.token, page, deviceStore.itemsPerPage);
  }
};

const pages = computed(() => {
  const pages = [];
  const total = deviceStore.totalPages;
  const current = deviceStore.currentPage;
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i);
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i);
      pages.push("...");
      pages.push(total);
    } else if (current >= total - 3) {
      pages.push(1);
      pages.push("...");
      for (let i = total - 4; i <= total; i++) pages.push(i);
    } else {
      pages.push(1);
      pages.push("...");
      for (let i = current - 1; i <= current + 1; i++) pages.push(i);
      pages.push("...");
      pages.push(total);
    }
  }
  return pages;
});
</script>

<template>
  <div class="min-h-screen bg-neutral-50">
    <!-- Header -->
    <header class="bg-white border-b border-neutral-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-light text-neutral-900 tracking-tight">The Rental Shop</h1>
          <p class="text-xs text-neutral-500 font-light mt-1">Hardware Rental Management</p>
        </div>

        <div class="flex items-center gap-4">
          <!-- Chat Button -->
          <button
            @click="showChatPanel = !showChatPanel"
            class="p-2 hover:bg-neutral-100 rounded-lg transition text-neutral-600 hover:text-primary-600"
            title="AI Assistant"
          >
            <MessageCircle class="w-5 h-5" />
          </button>

          <!-- Profile Menu -->
          <div class="relative">
            <button
              @click="showProfileMenu = !showProfileMenu"
              class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-neutral-100 transition"
            >
              <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white text-sm font-medium">
                {{ authStore.user?.username?.[0]?.toUpperCase() || "U" }}
              </div>
              <span class="text-sm text-neutral-700">{{ authStore.user?.username || "User" }}</span>
            </button>

            <div
              v-if="showProfileMenu"
              class="absolute right-0 mt-2 w-48 bg-white rounded-lg border border-neutral-200 shadow-sm z-10"
            >
              <button
                @click="handleLogout"
                class="w-full text-left px-4 py-2 text-sm text-primary-600 hover:bg-neutral-50 rounded-lg transition flex items-center gap-2"
              >
                <LogOut class="w-4 h-4" />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Tab Navigation -->
      <div class="flex gap-8 mb-8 border-b border-neutral-200">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-1 py-3 font-medium text-sm transition border-b-2 flex items-center gap-2',
            activeTab === tab.id
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-neutral-600 hover:text-neutral-900',
          ]"
        >
          <component :is="tab.icon" class="w-4 h-4" />
          {{ tab.label }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="deviceStore.loading" class="text-center py-12">
        <div class="inline-block">
          <div class="animate-spin rounded-full h-8 w-8 border-2 border-neutral-300 border-t-primary-600"></div>
        </div>
        <p class="mt-4 text-neutral-600 text-sm">Loading devices...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="deviceStore.error" class="bg-primary-50 border border-primary-200 text-primary-700 px-4 py-3 rounded-lg text-sm">
        {{ deviceStore.error }}
      </div>

      <!-- Available Devices Tab -->
      <div v-else-if="activeTab === 'available'">
        <div v-if="deviceStore.availableDevices.length === 0" class="text-center py-12">
          <Package class="w-12 h-12 text-neutral-300 mx-auto mb-4" />
          <p class="text-neutral-600 text-sm">No available devices at the moment</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <DeviceCard
            v-for="device in deviceStore.availableDevices"
            :key="device.id"
            :device="device"
            :show-rent-button="true"
            @rent="handleRent"
          />
        </div>
      </div>

      <!-- Rented Devices Tab -->
      <div v-else-if="activeTab === 'rented'">
        <div v-if="deviceStore.rentedDevices.length === 0" class="text-center py-12">
          <Truck class="w-12 h-12 text-neutral-300 mx-auto mb-4" />
          <p class="text-neutral-600 text-sm">You don't have any rented devices</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <DeviceCard
            v-for="device in deviceStore.rentedDevices"
            :key="device.id"
            :device="device"
            :show-return-button="true"
            @return="handleReturn"
          />
        </div>
      </div>

      <!-- History Tab -->
      <div v-else-if="activeTab === 'history'">
        <div v-if="deviceStore.deviceHistory.length === 0" class="text-center py-12">
          <History class="w-12 h-12 text-neutral-300 mx-auto mb-4" />
          <p class="text-neutral-600 text-sm">No device history available</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-neutral-100 border-b border-neutral-200">
              <tr>
                <th class="px-4 py-3 text-left font-medium text-neutral-700">Device Name</th>
                <th class="px-4 py-3 text-left font-medium text-neutral-700">Brand</th>
                <th class="px-4 py-3 text-left font-medium text-neutral-700">Status</th>
                <th class="px-4 py-3 text-left font-medium text-neutral-700">Purchased</th>
                <th class="px-4 py-3 text-left font-medium text-neutral-700">Assigned To</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-neutral-200">
              <tr v-for="device in deviceStore.deviceHistory" :key="device.id" class="hover:bg-neutral-50 transition">
                <td class="px-4 py-3 font-medium text-neutral-900">{{ device.name }}</td>
                <td class="px-4 py-3 text-neutral-600">{{ device.brand }}</td>
                <td class="px-4 py-3">
                  <span
                    :class="[
                      'px-2 py-1 rounded-full text-xs font-medium',
                      device.status === 'Available'
                        ? 'bg-green-100 text-green-700'
                        : device.status === 'In Use'
                          ? 'bg-blue-100 text-blue-700'
                          : device.status === 'Repair'
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-neutral-100 text-neutral-700',
                    ]"
                  >
                    {{ device.status }}
                  </span>
                </td>
                <td class="px-4 py-3 text-neutral-600 text-sm">
                  {{ device.purchase_date ? new Date(device.purchase_date).toLocaleDateString() : "—" }}
                </td>
                <td class="px-4 py-3 text-neutral-600">{{ device.assigned_to || "—" }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- All Devices Tab -->
      <div v-else-if="activeTab === 'all'">
        <div v-if="deviceStore.allDevices.length === 0" class="text-center py-12">
          <Package class="w-12 h-12 text-neutral-300 mx-auto mb-4" />
          <p class="text-neutral-600 text-sm">No devices in the database</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <DeviceCard
            v-for="device in deviceStore.allDevices"
            :key="device.id"
            :device="device"
            :show-rent-button="device.status === 'Available'"
            @rent="handleRent"
          />
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="deviceStore.totalPages > 1" class="mt-8 flex items-center justify-center gap-2">
        <button
          @click="handlePageChange(deviceStore.currentPage - 1)"
          :disabled="deviceStore.currentPage === 1"
          class="p-2 rounded-lg hover:bg-neutral-100 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          <ChevronLeft class="w-5 h-5 text-neutral-600" />
        </button>
        
        <button
          v-for="page in pages"
          :key="page"
          @click="typeof page === 'number' ? handlePageChange(page) : null"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition',
            typeof page === 'number' && deviceStore.currentPage === page
              ? 'bg-primary-600 text-white'
              : 'hover:bg-neutral-100 text-neutral-600',
            typeof page !== 'number' ? 'cursor-default' : '',
          ]"
        >
          {{ page }}
        </button>
        
        <button
          @click="handlePageChange(deviceStore.currentPage + 1)"
          :disabled="deviceStore.currentPage === deviceStore.totalPages"
          class="p-2 rounded-lg hover:bg-neutral-100 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          <ChevronRight class="w-5 h-5 text-neutral-600" />
        </button>
      </div>
    </main>

    <!-- Floating Chat Button -->
    <button
      v-if="showChatButton"
      @click="showChatPanel = !showChatPanel"
      class="fixed bottom-6 right-6 w-14 h-14 bg-primary-600 hover:bg-primary-700 text-white rounded-full shadow-lg flex items-center justify-center transition hover:scale-110 z-40"
      title="AI Assistant"
    >
      <Bot class="w-6 h-6" />
    </button>

    <!-- Chat Panel -->
    <div
      v-if="showChatPanel"
      class="fixed bottom-24 right-6 w-96 h-[500px] bg-white rounded-2xl shadow-2xl flex flex-col z-50 border border-neutral-200"
    >
      <div class="flex items-center justify-between px-4 py-3 border-b border-neutral-200 bg-primary-600 rounded-t-2xl">
        <h2 class="text-sm font-medium text-white">AI Assistant</h2>
        <button
          @click="showChatPanel = false"
          class="p-1 hover:bg-primary-700 rounded-lg transition text-white"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
      <ChatAssistant :token="authStore.token" />
    </div>
  </div>
</template>

<script>
import ChatAssistant from "../components/ChatAssistant.vue";
export default {
  components: {
    ChatAssistant,
  },
};
</script>
