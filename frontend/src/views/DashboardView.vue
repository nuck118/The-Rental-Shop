<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useDeviceStore } from "../stores/device";
import DeviceCard from "../components/DeviceCard.vue";
import ChatAssistant from "../components/ChatAssistant.vue";
import { Package, Truck, LogOut, X, Bot, ChevronLeft, ChevronRight, Search, CheckCircle, AlertCircle, ArrowUpDown, Wrench, Circle } from "lucide-vue-next";

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
  { id: "all", label: "All Devices", icon: Wrench },
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
  <div class="min-h-screen bg-neutral-50 bg-grid-pattern">
    <!-- Toast Notification -->
    <transition name="toast">
      <div
        v-if="toast"
        :class="[
          'fixed top-5 right-5 z-[100] flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-xl text-sm font-medium transition-all',
          toast.type === 'success'
            ? 'bg-emerald-50 border border-emerald-200 text-emerald-800'
            : 'bg-red-50 border border-red-200 text-red-800'
        ]"
      >
        <CheckCircle v-if="toast.type === 'success'" class="w-5 h-5 flex-shrink-0 text-emerald-500" />
        <AlertCircle v-else class="w-5 h-5 flex-shrink-0 text-red-500" />
        <span>{{ toast.message }}</span>
        <button @click="toast = null" class="ml-2 opacity-50 hover:opacity-100 transition-opacity"><X class="w-4 h-4" /></button>
      </div>
    </transition>

    <!-- Header with glass effect -->
    <header class="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-neutral-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Left: Brand + Tabs -->
          <div class="flex items-center gap-8">
            <div class="flex items-center gap-3 flex-shrink-0">
              <div class="w-9 h-9 bg-gradient-to-br from-primary-600 to-primary-500 rounded-xl flex items-center justify-center shadow-sm">
                <Wrench class="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 class="text-lg font-bold text-neutral-900 tracking-tight leading-tight">The Rental Shop</h1>
                <p class="text-[10px] text-neutral-500 font-medium tracking-wide leading-tight">Hardware Management</p>
              </div>
            </div>

            <!-- Navigation Tabs -->
            <nav class="hidden md:flex items-center h-16 gap-1">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="switchTab(tab.id)"
                :class="[
                  'relative px-4 py-2 font-medium text-sm transition rounded-lg flex items-center gap-2',
                  activeTab === tab.id
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100',
                ]"
              >
                <component :is="tab.icon" class="w-4 h-4" />
                {{ tab.label }}
              </button>
            </nav>
          </div>

          <!-- Right: Profile Menu -->
          <div class="flex items-center gap-3">
            <!-- Mobile tab switcher -->
            <div class="md:hidden flex gap-1">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="switchTab(tab.id)"
                :class="[
                  'p-2 rounded-lg transition text-sm',
                  activeTab === tab.id
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100',
                ]"
              >
                <component :is="tab.icon" class="w-4 h-4" />
              </button>
            </div>

            <!-- Profile -->
            <div class="relative">
              <button
                @click="showProfileMenu = !showProfileMenu"
                class="flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-neutral-100 transition"
              >
                <div class="w-8 h-8 bg-gradient-to-br from-primary-600 to-primary-500 rounded-xl flex items-center justify-center text-white text-sm font-bold shadow-sm">
                  {{ authStore.user?.username?.[0]?.toUpperCase() || "U" }}
                </div>
                <span class="text-sm font-medium text-neutral-700 hidden sm:block">{{ authStore.user?.username || "User" }}</span>
              </button>

              <div
                v-if="showProfileMenu"
                class="absolute right-0 mt-2 w-48 bg-white rounded-xl border border-neutral-200 shadow-xl z-40 overflow-hidden"
              >
                <div class="px-4 py-3 border-b border-neutral-100">
                  <p class="text-sm font-medium text-neutral-900">{{ authStore.user?.username }}</p>
                  <p class="text-xs text-neutral-500 mt-0.5">Administrator</p>
                </div>
                <button
                  @click="handleLogout"
                  class="w-full text-left px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition flex items-center gap-2.5"
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
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div class="flex flex-wrap gap-2.5 items-center">
          <!-- Search -->
          <div class="relative flex-1 min-w-[200px]">
            <Search class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search devices..."
              class="w-full pl-10 pr-4 py-2 border border-neutral-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none transition bg-neutral-50/50 focus:bg-white"
            />
          </div>

          <!-- Status Filter -->
          <div class="relative">
            <button
              @click="showStatusDropdown = !showStatusDropdown"
              class="flex items-center gap-2.5 px-4 py-2 border border-neutral-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none transition bg-white min-w-[150px] justify-between hover:border-neutral-300"
            >
              <span class="text-neutral-600 text-sm">
                {{ selectedStatus === 'all' ? 'All Status' : selectedStatus }}
              </span>
              <ChevronRight class="w-3.5 h-3.5 text-neutral-400 rotate-90 flex-shrink-0" />
            </button>

            <div
              v-if="showStatusDropdown"
              class="absolute top-full left-0 mt-1.5 w-52 bg-white rounded-xl border border-neutral-200 shadow-xl z-50 overflow-hidden"
            >
              <button
                v-for="status in statusOptions"
                :key="status"
                @click="handleStatusSelect(status)"
                class="w-full text-left px-4 py-2.5 text-sm text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition flex items-center gap-2.5"
              >
                <Circle :class="[
                  'w-2 h-2 rounded-full flex-shrink-0',
                  status === 'Available' ? 'bg-amber-500' :
                  status === 'In Use' ? 'bg-blue-500' :
                  status === 'Repair' ? 'bg-yellow-500' :
                  status === 'Unknown' ? 'bg-neutral-400' :
                  'bg-transparent border border-neutral-300'
                ]" />
                {{ status === 'all' ? 'All Status' : status }}
              </button>
            </div>
          </div>

          <!-- Brand Filter -->
          <div class="relative">
            <button
              @click="showBrandDropdown = !showBrandDropdown"
              class="flex items-center gap-2.5 px-4 py-2 border border-neutral-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none transition bg-white min-w-[150px] justify-between hover:border-neutral-300"
            >
              <span class="text-neutral-600 text-sm">
                {{ selectedBrand === 'all' ? 'All Brands' : selectedBrand }}
              </span>
              <ChevronRight class="w-3.5 h-3.5 text-neutral-400 rotate-90 flex-shrink-0" />
            </button>

            <div
              v-if="showBrandDropdown"
              class="absolute top-full left-0 mt-1.5 w-52 bg-white rounded-xl border border-neutral-200 shadow-xl z-50 overflow-hidden"
            >
              <button
                v-for="brand in brands"
                :key="brand"
                @click="handleBrandSelect(brand)"
                class="w-full text-left px-4 py-2.5 text-sm text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition"
              >
                {{ brand === 'all' ? 'All Brands' : brand }}
              </button>
            </div>
          </div>

          <!-- Sort Dropdown -->
          <div class="relative">
            <button
              @click="showSortDropdown = !showSortDropdown"
              class="flex items-center gap-2.5 px-4 py-2 border border-neutral-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none transition bg-white min-w-[160px] justify-between hover:border-neutral-300"
            >
              <span class="text-neutral-600 text-sm flex items-center gap-2">
                <ArrowUpDown class="w-3.5 h-3.5 text-neutral-400" />
                {{ sortOptions.find(o => o.value === sortField.value + '-' + sortDirection.value)?.label || 'Sort' }}
              </span>
              <ChevronRight class="w-3.5 h-3.5 text-neutral-400 rotate-90 flex-shrink-0" />
            </button>

            <div
              v-if="showSortDropdown"
              class="absolute top-full right-0 mt-1.5 w-52 bg-white rounded-xl border border-neutral-200 shadow-xl z-50 overflow-hidden"
            >
              <button
                v-for="option in sortOptions"
                :key="option.value"
                @click="handleSortSelect(option)"
                class="w-full text-left px-4 py-2.5 text-sm text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition"
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
      <!-- Loading State -->
      <div v-if="deviceStore.loading" class="flex flex-col items-center justify-center py-20">
        <div class="relative w-12 h-12">
          <div class="absolute inset-0 rounded-full border-2 border-neutral-200"></div>
          <div class="absolute inset-0 rounded-full border-2 border-transparent border-t-primary-600 animate-spin"></div>
        </div>
        <p class="mt-5 text-neutral-500 text-sm font-medium">Loading devices...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="deviceStore.error" class="max-w-md mx-auto text-center py-16">
        <AlertCircle class="w-12 h-12 text-red-400 mx-auto mb-4" />
        <p class="text-neutral-700 font-medium mb-1">Something went wrong</p>
        <p class="text-neutral-500 text-sm">{{ deviceStore.error }}</p>
      </div>

      <!-- Empty State (Available) -->
      <div v-else-if="activeTab === 'available' && filteredDevices.length === 0" class="text-center py-20">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-amber-50 rounded-2xl mb-5">
          <Package class="w-8 h-8 text-amber-500" />
        </div>
        <h3 class="text-lg font-semibold text-neutral-900 mb-1">No Available Devices</h3>
        <p class="text-neutral-500 text-sm">All devices are currently rented or in repair.</p>
      </div>

      <!-- Empty State (Rented) -->
      <div v-else-if="activeTab === 'rented' && filteredDevices.length === 0" class="text-center py-20">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-50 rounded-2xl mb-5">
          <Truck class="w-8 h-8 text-blue-500" />
        </div>
        <h3 class="text-lg font-semibold text-neutral-900 mb-1">No Rentals Yet</h3>
        <p class="text-neutral-500 text-sm">Browse available devices and rent your first one.</p>
        <button @click="switchTab('available')" class="mt-5 inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition-all duration-200 shadow-sm hover:shadow-md active:scale-[0.98]">
          Browse Available
        </button>
      </div>

      <!-- Empty State (All) -->
      <div v-else-if="activeTab === 'all' && filteredDevices.length === 0" class="text-center py-20">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-neutral-100 rounded-2xl mb-5">
          <Search class="w-8 h-8 text-neutral-400" />
        </div>
        <h3 class="text-lg font-semibold text-neutral-900 mb-1">No Devices Found</h3>
        <p class="text-neutral-500 text-sm">Try adjusting your search or filters.</p>
      </div>

      <!-- Device Grids -->
      <template v-else>
        <!-- Available Devices Tab -->
        <div v-if="activeTab === 'available'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <DeviceCard
            v-for="device in paginatedDevices"
            :key="device.id"
            :device="device"
            :show-rent-button="true"
            @rent="handleRent"
          />
        </div>

        <!-- Rented Devices Tab -->
        <div v-else-if="activeTab === 'rented'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <DeviceCard
            v-for="device in paginatedDevices"
            :key="device.id"
            :device="device"
            :show-return-button="true"
            @return="handleReturn"
          />
        </div>

        <!-- All Devices Tab -->
        <div v-else-if="activeTab === 'all'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <DeviceCard
            v-for="device in paginatedDevices"
            :key="device.id"
            :device="device"
            :show-rent-button="device.status === 'Available'"
            @rent="handleRent"
          />
        </div>
      </template>

      <!-- Pagination -->
      <div v-if="filteredTotalPages > 1" class="mt-10 flex items-center justify-center gap-1.5">
        <button
          @click="handlePageChange(deviceStore.currentPage - 1)"
          :disabled="deviceStore.currentPage === 1"
          class="p-2.5 rounded-xl hover:bg-white hover:border-neutral-300 border border-transparent disabled:opacity-40 disabled:cursor-not-allowed transition bg-white/50"
        >
          <ChevronLeft class="w-4 h-4 text-neutral-500" />
        </button>

        <button
          v-for="page in filteredPages"
          :key="page"
          @click="typeof page === 'number' ? handlePageChange(page) : null"
          :class="[
            'min-w-[36px] h-9 rounded-xl text-sm font-medium transition',
            typeof page === 'number' && deviceStore.currentPage === page
              ? 'bg-primary-600 text-white shadow-sm'
              : typeof page === 'number'
                ? 'hover:bg-white hover:border-neutral-300 border border-transparent text-neutral-600 bg-white/50'
                : 'text-neutral-400 cursor-default px-2',
          ]"
        >
          {{ page }}
        </button>

        <button
          @click="handlePageChange(deviceStore.currentPage + 1)"
          :disabled="deviceStore.currentPage === filteredTotalPages"
          class="p-2.5 rounded-xl hover:bg-white hover:border-neutral-300 border border-transparent disabled:opacity-40 disabled:cursor-not-allowed transition bg-white/50"
        >
          <ChevronRight class="w-4 h-4 text-neutral-500" />
        </button>
      </div>
    </main>

    <!-- Floating Chat Button -->
    <button
      v-if="showChatButton"
      @click="showChatPanel = !showChatPanel"
      class="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 text-white rounded-full shadow-xl hover:shadow-2xl flex items-center justify-center transition-all duration-200 hover:scale-110 active:scale-95 z-40"
      title="AI Assistant"
    >
      <Bot class="w-6 h-6" />
    </button>

    <!-- AI Chat Panel -->
    <Transition name="chat">
      <div
        v-if="showChatPanel"
        class="fixed bottom-24 right-6 w-[400px] h-[600px] max-h-[calc(100vh-120px)] bg-white rounded-2xl shadow-2xl border border-neutral-200 overflow-hidden flex flex-col z-50"
      >
        <div class="p-4 bg-gradient-to-r from-primary-600 to-primary-500 text-white flex justify-between items-center flex-shrink-0">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 bg-white/15 rounded-lg flex items-center justify-center backdrop-blur-sm">
              <Bot class="w-4 h-4" />
            </div>
            <div>
              <h3 class="font-semibold text-sm">AI Assistant</h3>
              <p class="text-[11px] text-primary-100 font-medium">Ask me about devices</p>
            </div>
          </div>
          <button @click="showChatPanel = false" class="w-8 h-8 rounded-lg hover:bg-white/15 transition flex items-center justify-center">
            <X class="w-4 h-4" />
          </button>
        </div>
        <div class="flex-1 overflow-hidden">
          <ChatAssistant :token="authStore.token" @rent="handleRent" />
        </div>
      </div>
    </Transition>
  </div>
</template>
