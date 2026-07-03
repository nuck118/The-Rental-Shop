<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useDeviceStore } from "../stores/device";
import DeviceCard from "../components/DeviceCard.vue";
import ChatAssistant from "../components/ChatAssistant.vue";
import { Package, Truck, LogOut, X, Bot, ChevronLeft, ChevronRight, Search, CheckCircle, AlertCircle, ArrowUpDown } from "lucide-vue-next";

const router = useRouter();
const authStore = useAuthStore();
const deviceStore = useDeviceStore();

const activeTab = ref("available");
const showProfileMenu = ref(false);
const showChatPanel = ref(false);
const showChatButton = ref(true);
const showStatusDropdown = ref(false);
const showBrandDropdown = ref(false);
const showSortDropdown = ref(false);
const sortField = ref("name");
const sortDirection = ref("asc");

// Toast notification state
const toast = ref(null); // { type: 'success'|'error', message: string }
let toastTimer = null;
const showToast = (type, message) => {
  clearTimeout(toastTimer);
  toast.value = { type, message };
  toastTimer = setTimeout(() => { toast.value = null; }, 4000);
};

// Search and filter state
const searchQuery = ref("");
const selectedStatus = ref("all");
const selectedBrand = ref("all");

// Get unique brands from devices
const brands = computed(() => {
  const allBrands = new Set();
  deviceStore.allDevices.forEach(d => { if (d.brand) allBrands.add(d.brand); });
  return ["all", ...Array.from(allBrands).sort()];
});

const sortOptions = [
  { value: "name-asc", label: "Name (A-Z)" },
  { value: "name-desc", label: "Name (Z-A)" },
  { value: "brand-asc", label: "Brand (A-Z)" },
  { value: "brand-desc", label: "Brand (Z-A)" },
  { value: "purchase_date-asc", label: "Purchase Date (Oldest)" },
  { value: "purchase_date-desc", label: "Purchase Date (Newest)" },
];

// Filter devices based on search, filters, and active tab
const filteredDevices = computed(() => {
  let devices = deviceStore.allDevices;

  if (activeTab.value === "available") {
    devices = devices.filter(d => d.status === "Available");
  } else if (activeTab.value === "rented") {
    // My Rentals: only devices this user rented
    devices = devices.filter(d => d.status === "In Use" && d.assigned_to === authStore.user?.username);
  }
  // all tab shows everything, with optional filters
  if (selectedStatus.value !== "all" && activeTab.value === "all") {
    devices = devices.filter(d => d.status === selectedStatus.value);
  }
  if (selectedBrand.value !== "all" && activeTab.value === "all") {
    devices = devices.filter(d => d.brand === selectedBrand.value);
  }
  if (searchQuery.value && activeTab.value === "all") {
    const q = searchQuery.value.toLowerCase();
    devices = devices.filter(d => d.name.toLowerCase().includes(q) || d.brand.toLowerCase().includes(q));
  }

  // Sort devices
  const [field, direction] = sortField.value.split("-");
  devices = [...devices].sort((a, b) => {
    let aVal = a[field] || "";
    let bVal = b[field] || "";
    if (field === "purchase_date") {
      aVal = aVal ? new Date(aVal).getTime() : 0;
      bVal = bVal ? new Date(bVal).getTime() : 0;
    } else {
      aVal = String(aVal).toLowerCase();
      bVal = String(bVal).toLowerCase();
    }
    if (aVal < bVal) return direction === "asc" ? -1 : 1;
    if (aVal > bVal) return direction === "asc" ? 1 : -1;
    return 0;
  });

  return devices;
});

const filteredTotalPages = computed(() => Math.ceil(filteredDevices.value.length / deviceStore.itemsPerPage));

const filteredPages = computed(() => {
  const pages = [];
  const total = filteredTotalPages.value;
  const current = deviceStore.currentPage;
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i);
  } else if (current <= 4) {
    for (let i = 1; i <= 5; i++) pages.push(i);
    pages.push("..."); pages.push(total);
  } else if (current >= total - 3) {
    pages.push(1); pages.push("...");
    for (let i = total - 4; i <= total; i++) pages.push(i);
  } else {
    pages.push(1); pages.push("...");
    for (let i = current - 1; i <= current + 1; i++) pages.push(i);
    pages.push("..."); pages.push(total);
  }
  return pages;
});

const paginatedDevices = computed(() => {
  const start = (deviceStore.currentPage - 1) * deviceStore.itemsPerPage;
  return filteredDevices.value.slice(start, start + deviceStore.itemsPerPage);
});

const tabs = [
  { id: "available", label: "Available", icon: Package },
  { id: "rented", label: "My Rentals", icon: Truck },
  { id: "all", label: "All Devices", icon: Package },
];

const statusOptions = ["all", "Available", "In Use", "Repair", "Unknown"];

const switchTab = (tabId) => {
  activeTab.value = tabId;
  deviceStore.currentPage = 1;
};

const handleStatusSelect = (s) => { selectedStatus.value = s; showStatusDropdown.value = false; };
const handleBrandSelect = (b) => { selectedBrand.value = b; showBrandDropdown.value = false; };
const handleSortSelect = (option) => {
  sortField.value = option.value.split("-")[0];
  sortDirection.value = option.value.split("-")[1];
  showSortDropdown.value = false;
};

onMounted(async () => {
  if (!authStore.isAuthenticated) { router.push("/signin"); return; }
  await deviceStore.fetchAllDevices(authStore.token);
});

const handleLogout = () => { authStore.logout(); router.push("/signin"); };

const refreshDevices = () => deviceStore.fetchAllDevices(authStore.token);

const handleRent = async (deviceOrId) => {
  const deviceId = typeof deviceOrId === "object" ? deviceOrId.id : deviceOrId;
  const deviceName = typeof deviceOrId === "object" ? deviceOrId.name : `Device #${deviceId}`;
  try {
    await deviceStore.rentDevice(authStore.token, deviceId, authStore.csrfToken);
    await refreshDevices();
    showToast("success", `✓ ${deviceName} has been rented. Find it in My Rentals.`);
    if (!showChatPanel.value) switchTab("rented");
  } catch (err) {
    showToast("error", err.message);
  }
};

const handleReturn = async (deviceOrId) => {
  const deviceId = typeof deviceOrId === "object" ? deviceOrId.id : deviceOrId;
  const deviceName = typeof deviceOrId === "object" ? deviceOrId.name : `Device #${deviceId}`;
  try {
    await deviceStore.returnDevice(authStore.token, deviceId, authStore.csrfToken);
    await refreshDevices();
    showToast("success", `✓ ${deviceName} has been returned successfully.`);
  } catch (err) {
    showToast("error", err.message);
  }
};

const handlePageChange = (page) => {
  if (page < 1 || page > filteredTotalPages.value) return;
  deviceStore.currentPage = page;
};
</script>

<template>
  <div class="min-h-screen bg-neutral-50">
    <!-- Toast Notification -->
    <transition name="toast">
      <div
        v-if="toast"
        :class="[
          'fixed top-5 right-5 z-[100] flex items-center gap-3 px-5 py-3 rounded-xl shadow-lg text-sm font-medium transition-all',
          toast.type === 'success' ? 'bg-green-50 border border-green-200 text-green-800' : 'bg-red-50 border border-red-200 text-red-800'
        ]"
      >
        <CheckCircle v-if="toast.type === 'success'" class="w-5 h-5 flex-shrink-0" />
        <AlertCircle v-else class="w-5 h-5 flex-shrink-0" />
        <span>{{ toast.message }}</span>
        <button @click="toast = null" class="ml-2 opacity-60 hover:opacity-100"><X class="w-4 h-4" /></button>
      </div>
    </transition>
    <!-- Header with Tabs -->
    <header class="bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div class="flex items-center gap-4">
            <div>
              <h1 class="text-2xl font-light text-neutral-900 tracking-tight">The Rental Shop</h1>
              <p class="text-xs text-neutral-500 font-light mt-1">Hardware Rental Management</p>
            </div>
            
            <!-- Navigation Tabs -->
            <div class="flex gap-6">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="switchTab(tab.id)"
                :class="[
                  'px-1 py-2 font-medium text-sm transition border-b-2 flex items-center gap-2',
                  activeTab === tab.id
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-neutral-600 hover:text-neutral-900',
                ]"
              >
                <component :is="tab.icon" class="w-4 h-4" />
                {{ tab.label }}
              </button>
            </div>
          </div>

          <div class="flex items-center gap-4">
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
      </div>
    </header>

    <!-- Filter Bar -->
    <div class="bg-white border-b border-neutral-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex flex-wrap gap-4 items-center">
          <!-- Search -->
          <div class="relative flex-1 min-w-[200px]">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search devices..."
              class="w-full pl-9 pr-4 py-2 border border-neutral-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
            />
          </div>
          
          <!-- Status Filter Custom Dropdown -->
          <div class="relative">
            <button
              @click="showStatusDropdown = !showStatusDropdown"
              class="flex items-center gap-3 px-4 py-2 border border-neutral-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition bg-white min-w-[160px] justify-between"
            >
              <span class="text-neutral-700">
                {{ selectedStatus === 'all' ? 'All Status' : selectedStatus }}
              </span>
              <ChevronRight class="w-4 h-4 text-neutral-400 rotate-90" />
            </button>
            
            <div
              v-if="showStatusDropdown"
              class="absolute top-full left-0 mt-2 w-48 bg-white rounded-lg border border-neutral-200 shadow-lg z-50 overflow-hidden"
            >
              <button
                v-for="status in statusOptions"
                :key="status"
                @click="handleStatusSelect(status)"
                class="w-full text-left px-4 py-2.5 text-sm text-neutral-700 hover:bg-neutral-50 transition"
              >
                {{ status === 'all' ? 'All Status' : status }}
              </button>
            </div>
          </div>
          
          <!-- Brand Filter Custom Dropdown -->
          <div class="relative">
            <button
              @click="showBrandDropdown = !showBrandDropdown"
              class="flex items-center gap-3 px-4 py-2 border border-neutral-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition bg-white min-w-[160px] justify-between"
            >
              <span class="text-neutral-700">
                {{ selectedBrand === 'all' ? 'All Brands' : selectedBrand }}
              </span>
              <ChevronRight class="w-4 h-4 text-neutral-400 rotate-90" />
            </button>
            
            <div
              v-if="showBrandDropdown"
              class="absolute top-full left-0 mt-2 w-48 bg-white rounded-lg border border-neutral-200 shadow-lg z-50 overflow-hidden"
            >
              <button
                v-for="brand in brands"
                :key="brand"
                @click="handleBrandSelect(brand)"
                class="w-full text-left px-4 py-2.5 text-sm text-neutral-700 hover:bg-neutral-50 transition"
              >
                {{ brand === 'all' ? 'All Brands' : brand }}
              </button>
            </div>
          </div>

          <!-- Sort Dropdown -->
          <div class="relative">
            <button
              @click="showSortDropdown = !showSortDropdown"
              class="flex items-center gap-3 px-4 py-2 border border-neutral-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition bg-white min-w-[180px] justify-between"
            >
              <span class="text-neutral-700 flex items-center gap-2">
                <ArrowUpDown class="w-4 h-4 text-neutral-400" />
                Sort by {{ sortField.value }} ({{ sortDirection.value === 'asc' ? 'Ascending' : 'Descending' }})
              </span>
              <ChevronRight class="w-4 h-4 text-neutral-400 rotate-90" />
            </button>
            
            <div
              v-if="showSortDropdown"
              class="absolute top-full left-0 mt-2 w-48 bg-white rounded-lg border border-neutral-200 shadow-lg z-50 overflow-hidden"
            >
              <button
                v-for="option in sortOptions"
                :key="option.value"
                @click="handleSortSelect(option)"
                class="w-full text-left px-4 py-2.5 text-sm text-neutral-700 hover:bg-neutral-50 transition"
              >
                {{ option.label }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
        <div v-if="filteredDevices.length === 0" class="text-center py-12">
          <Package class="w-12 h-12 text-neutral-300 mx-auto mb-4" />
          <p class="text-neutral-600 text-sm">No available devices at the moment</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <DeviceCard
            v-for="device in paginatedDevices"
            :key="device.id"
            :device="device"
            :show-rent-button="true"
            @rent="handleRent"
          />
        </div>
      </div>

      <!-- Rented Devices Tab -->
      <div v-else-if="activeTab === 'rented'">
        <div v-if="filteredDevices.length === 0" class="text-center py-12">
          <Truck class="w-12 h-12 text-neutral-300 mx-auto mb-4" />
          <p class="text-neutral-600 text-sm">You don't have any rented devices</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <DeviceCard
            v-for="device in paginatedDevices"
            :key="device.id"
            :device="device"
            :show-return-button="true"
            @return="handleReturn"
          />
        </div>
      </div>

      <!-- All Devices Tab -->
      <div v-else-if="activeTab === 'all'">
        <div v-if="filteredDevices.length === 0" class="text-center py-12">
          <Package class="w-12 h-12 text-neutral-300 mx-auto mb-4" />
          <p class="text-neutral-600 text-sm">No devices found</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <DeviceCard
            v-for="device in paginatedDevices"
            :key="device.id"
            :device="device"
            :show-rent-button="device.status === 'Available'"
            @rent="handleRent"
          />
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="filteredTotalPages > 1" class="mt-8 flex items-center justify-center gap-2">
        <button
          @click="handlePageChange(deviceStore.currentPage - 1)"
          :disabled="deviceStore.currentPage === 1"
          class="p-2 rounded-lg hover:bg-neutral-100 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          <ChevronLeft class="w-5 h-5 text-neutral-600" />
        </button>
        
        <button
          v-for="page in filteredPages"
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
          :disabled="deviceStore.currentPage === filteredTotalPages"
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

      <!-- AI Chat Panel -->
      <div
        v-if="showChatPanel"
        class="fixed bottom-24 right-6 w-[400px] h-[600px] max-h-[calc(100vh-120px)] bg-white rounded-2xl shadow-2xl border border-neutral-200 overflow-hidden flex flex-col z-50 transition-all duration-300 transform origin-bottom-right"
      >
        <div class="p-4 bg-primary-600 text-white flex justify-between items-center">
          <div class="flex items-center gap-2">
            <Bot class="w-5 h-5" />
            <h3 class="font-medium">AI Assistant</h3>
          </div>
          <button @click="showChatPanel = false" class="text-primary-100 hover:text-white transition">
            <X class="w-5 h-5" />
          </button>
        </div>
        <div class="flex-1 overflow-hidden">
          <ChatAssistant :token="authStore.token" @rent="handleRent" />
        </div>
      </div>
  </div>
</template>

<style scoped>
/* Scoped styles if needed */
</style>
