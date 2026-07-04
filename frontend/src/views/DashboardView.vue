<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useDeviceStore } from "../stores/device";
import DeviceCard from "../components/DeviceCard.vue";
import ChatAssistant from "../components/ChatAssistant.vue";
import ReturnModal from "../components/ReturnModal.vue";
import { Package, Truck, LogOut, X, Bot, ChevronLeft, ChevronRight, Search, CheckCircle, AlertCircle, ArrowUpDown, Menu, Filter } from "lucide-vue-next";

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
const showMobileFilters = ref(false);
const sortField = ref("name-asc");
const sortDirection = ref("asc");
const showReturnModal = ref(false);
const deviceToReturn = ref(null);

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
  if (selectedStatus.value !== "all") {
    devices = devices.filter(d => d.status === selectedStatus.value);
  }
  if (selectedBrand.value !== "all") {
    devices = devices.filter(d => d.brand === selectedBrand.value);
  }
  if (searchQuery.value) {
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
  sortField.value = option.value;
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
    showToast("success", `${deviceName} has been rented.`);
    if (!showChatPanel.value) switchTab("rented");
  } catch (err) {
    showToast("error", err.message);
  }
};

const handleReturn = (deviceOrId) => {
  const device = typeof deviceOrId === "object" ? deviceOrId : null;
  if (device) {
    deviceToReturn.value = device;
    showReturnModal.value = true;
  }
};

const handleReturnConfirm = async (returnData) => {
  if (!deviceToReturn.value) return;
  
  const deviceId = deviceToReturn.value.id;
  const deviceName = deviceToReturn.value.name;
  
  try {
    await deviceStore.returnDevice(authStore.token, deviceId, authStore.csrfToken, returnData);
    await refreshDevices();
    showReturnModal.value = false;
    deviceToReturn.value = null;
    showToast("success", `${deviceName} has been returned.`);
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
          'fixed top-5 right-5 z-[100] flex items-center gap-3 px-4 py-3 text-sm font-medium shadow-dropdown transition-all',
          toast.type === 'success' ? 'bg-white border border-neutral-200 text-neutral-900' : 'error-banner'
        ]"
      >
        <CheckCircle v-if="toast.type === 'success'" class="w-4 h-4 text-neutral-600 flex-shrink-0" />
        <AlertCircle v-else class="w-4 h-4 flex-shrink-0" />
        <span>{{ toast.message }}</span>
        <button @click="toast = null" class="ml-2 opacity-50 hover:opacity-100 transition-opacity"><X class="w-3.5 h-3.5" /></button>
      </div>
    </transition>

    <!-- Header -->
    <header class="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-neutral-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <!-- Brand + Profile row on mobile -->
          <div class="flex items-center justify-between sm:block">
            <!-- Brand -->
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 sm:w-9 sm:h-9 bg-neutral-900 rounded-lg flex items-center justify-center">
                <span class="text-white text-xs sm:text-sm font-bold">TRS</span>
              </div>
              <div>
                <h1 class="text-sm sm:text-base font-bold text-neutral-900 tracking-tight">The Rental Shop</h1>
                <p class="text-[10px] sm:text-xs text-neutral-500 mt-0.5">Hardware Rental Management</p>
              </div>
            </div>

            <!-- Profile (mobile only) -->
            <div class="relative sm:hidden">
              <button
                @click="showProfileMenu = !showProfileMenu"
                class="flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-neutral-100 transition-colors"
              >
                <div class="w-8 h-8 bg-neutral-900 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                  {{ authStore.user?.username?.[0]?.toUpperCase() || "U" }}
                </div>
              </button>

              <transition name="dropdown">
                <div
                  v-if="showProfileMenu"
                  class="absolute right-0 mt-2 w-48 bg-white rounded-lg border border-neutral-200 shadow-lg z-10"
                >
                  <button
                    @click="handleLogout"
                    class="w-full text-left px-4 py-2.5 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors flex items-center gap-2 rounded-t-lg"
                  >
                    <LogOut class="w-4 h-4" />
                    Sign Out
                  </button>
                </div>
              </transition>
            </div>
          </div>

          <!-- Mobile Tabs -->
          <div class="sm:hidden">
            <div class="flex bg-neutral-100 rounded-lg p-0.5">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="switchTab(tab.id)"
                :class="[
                  'flex-1 px-2 py-2 text-xs font-medium rounded-md transition-all flex items-center justify-center gap-1',
                  activeTab === tab.id ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-600 hover:text-neutral-900',
                ]"
              >
                <component :is="tab.icon" class="w-3.5 h-3.5" />
                <span class="truncate">{{ tab.label }}</span>
              </button>
            </div>
          </div>

          <!-- Desktop tabs + Profile -->
          <div class="hidden sm:flex items-center gap-1">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="switchTab(tab.id)"
              :class="[
                'px-4 py-2 text-sm font-medium rounded-lg transition-all',
                activeTab === tab.id
                  ? 'bg-neutral-900 text-white'
                  : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100',
              ]"
            >
              <component :is="tab.icon" class="w-4 h-4 inline-block mr-1.5" />
              {{ tab.label }}
            </button>

            <!-- Profile (desktop) -->
            <div class="relative ml-2">
              <button
                @click="showProfileMenu = !showProfileMenu"
                class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-neutral-100 transition-colors"
              >
                <div class="w-8 h-8 bg-neutral-900 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                  {{ authStore.user?.username?.[0]?.toUpperCase() || "U" }}
                </div>
                <span class="text-sm text-neutral-700">{{ authStore.user?.username || "User" }}</span>
              </button>

              <transition name="dropdown">
                <div
                  v-if="showProfileMenu"
                  class="absolute right-0 mt-2 w-48 bg-white rounded-lg border border-neutral-200 shadow-lg z-10"
                >
                  <button
                    @click="handleLogout"
                    class="w-full text-left px-4 py-2.5 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors flex items-center gap-2 rounded-t-lg"
                  >
                    <LogOut class="w-4 h-4" />
                    Sign Out
                  </button>
                </div>
              </transition>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Filter Bar -->
    <div class="bg-white border-b border-neutral-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 sm:py-4">
        <!-- Desktop -->
        <div class="hidden sm:flex flex-wrap gap-2 sm:gap-3 items-center">
          <!-- Search -->
          <div class="relative flex-1 min-w-[200px]">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 pointer-events-none" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search devices..."
              class="w-full pl-10 pr-4 py-2 bg-neutral-50 border border-neutral-200 rounded-lg text-sm text-neutral-900 placeholder:text-neutral-400 focus:bg-white focus:border-neutral-900 focus:outline-none focus:ring-0 transition-all"
            />
          </div>

          <!-- Status -->
          <div class="relative">
            <button
              @click="showStatusDropdown = !showStatusDropdown"
              class="flex items-center gap-2 px-3 sm:px-4 py-2 border border-neutral-200 text-sm bg-white min-w-[120px] sm:min-w-[150px] justify-between hover:border-neutral-300 transition-colors rounded-lg"
            >
              <span class="text-neutral-700 truncate">{{ selectedStatus === 'all' ? 'All Status' : selectedStatus }}</span>
              <ChevronRight class="w-3.5 h-3.5 text-neutral-400 -rotate-90 flex-shrink-0" />
            </button>
            <transition name="dropdown">
              <div v-if="showStatusDropdown" class="dropdown-editorial">
                <button
                  v-for="status in statusOptions"
                  :key="status"
                  @click="handleStatusSelect(status)"
                  class="dropdown-editorial-item"
                >
                  {{ status === 'all' ? 'All Status' : status }}
                </button>
              </div>
            </transition>
          </div>

          <!-- Brand -->
          <div class="relative">
            <button
              @click="showBrandDropdown = !showBrandDropdown"
              class="flex items-center gap-2 px-3 sm:px-4 py-2 border border-neutral-200 text-sm bg-white min-w-[120px] sm:min-w-[150px] justify-between hover:border-neutral-300 transition-colors rounded-lg"
            >
              <span class="text-neutral-700 truncate">{{ selectedBrand === 'all' ? 'All Brands' : selectedBrand }}</span>
              <ChevronRight class="w-3.5 h-3.5 text-neutral-400 -rotate-90 flex-shrink-0" />
            </button>
            <transition name="dropdown">
              <div v-if="showBrandDropdown" class="dropdown-editorial">
                <button
                  v-for="brand in brands"
                  :key="brand"
                  @click="handleBrandSelect(brand)"
                  class="dropdown-editorial-item"
                >
                  {{ brand === 'all' ? 'All Brands' : brand }}
                </button>
              </div>
            </transition>
          </div>

          <!-- Sort -->
          <div class="relative">
            <button
              @click="showSortDropdown = !showSortDropdown"
              class="flex items-center gap-2 px-3 sm:px-4 py-2 border border-neutral-200 text-sm bg-white min-w-[120px] sm:min-w-[160px] justify-between hover:border-neutral-300 transition-colors rounded-lg"
            >
              <span class="text-neutral-700 flex items-center gap-2 truncate">
                <ArrowUpDown class="w-3.5 h-3.5 text-neutral-400 flex-shrink-0" />
                <span class="hidden sm:inline">Sort</span>
              </span>
              <ChevronRight class="w-3.5 h-3.5 text-neutral-400 -rotate-90 flex-shrink-0" />
            </button>
            <transition name="dropdown">
              <div v-if="showSortDropdown" class="dropdown-editorial">
                <button
                  v-for="option in sortOptions"
                  :key="option.value"
                  @click="handleSortSelect(option)"
                  class="dropdown-editorial-item"
                >
                  {{ option.label }}
                </button>
              </div>
            </transition>
          </div>
        </div>

        <!-- Mobile -->
        <div class="sm:hidden space-y-2">
          <div class="relative">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 pointer-events-none" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search devices..."
              class="w-full pl-10 pr-4 py-2.5 bg-neutral-50 border border-neutral-200 rounded-lg text-sm text-neutral-900 placeholder:text-neutral-400 focus:bg-white focus:border-neutral-900 focus:outline-none focus:ring-0 transition-all"
            />
          </div>

          <button
            @click="showMobileFilters = !showMobileFilters"
            class="flex items-center justify-center gap-2 w-full px-4 py-2.5 border border-neutral-200 text-sm text-neutral-700 bg-white hover:border-neutral-300 transition-colors rounded-lg"
          >
            <Filter class="w-4 h-4" />
            {{ showMobileFilters ? 'Hide Filters' : 'Filters' }}
          </button>

          <transition name="filters">
            <div v-if="showMobileFilters" class="grid grid-cols-2 gap-2">
              <div class="relative">
                <button
                  @click="showStatusDropdown = !showStatusDropdown"
                  class="w-full flex items-center justify-between gap-2 px-3 py-2 border border-neutral-200 text-xs bg-white rounded-lg"
                >
                  <span class="truncate">{{ selectedStatus === 'all' ? 'Status' : selectedStatus }}</span>
                  <ChevronRight class="w-3 h-3 text-neutral-400 flex-shrink-0" />
                </button>
                <transition name="dropdown">
                  <div v-if="showStatusDropdown" class="dropdown-editorial">
                    <button
                      v-for="status in statusOptions"
                      :key="status"
                      @click="handleStatusSelect(status)"
                      class="dropdown-editorial-item text-xs"
                    >
                      {{ status === 'all' ? 'All Status' : status }}
                    </button>
                  </div>
                </transition>
              </div>
              <div class="relative">
                <button
                  @click="showBrandDropdown = !showBrandDropdown"
                  class="w-full flex items-center justify-between gap-2 px-3 py-2 border border-neutral-200 text-xs bg-white rounded-lg"
                >
                  <span class="truncate">{{ selectedBrand === 'all' ? 'Brand' : selectedBrand }}</span>
                  <ChevronRight class="w-3 h-3 text-neutral-400 flex-shrink-0" />
                </button>
                <transition name="dropdown">
                  <div v-if="showBrandDropdown" class="dropdown-editorial">
                    <button
                      v-for="brand in brands"
                      :key="brand"
                      @click="handleBrandSelect(brand)"
                      class="dropdown-editorial-item text-xs"
                    >
                      {{ brand === 'all' ? 'All Brands' : brand }}
                    </button>
                  </div>
                </transition>
              </div>
              <div class="relative col-span-2">
                <button
                  @click="showSortDropdown = !showSortDropdown"
                  class="w-full flex items-center justify-between gap-2 px-3 py-2 border border-neutral-200 text-xs bg-white rounded-lg"
                >
                  <span class="flex items-center gap-2 truncate">
                    <ArrowUpDown class="w-3 h-3 text-neutral-400 flex-shrink-0" />
                    <span class="truncate">Sort: {{ sortOptions.find(o => o.value === sortField)?.label || 'Name (A-Z)' }}</span>
                  </span>
                  <ChevronRight class="w-3 h-3 text-neutral-400 flex-shrink-0" />
                </button>
                <transition name="dropdown">
                  <div v-if="showSortDropdown" class="dropdown-editorial">
                    <button
                      v-for="option in sortOptions"
                      :key="option.value"
                      @click="handleSortSelect(option)"
                      class="dropdown-editorial-item text-xs"
                    >
                      {{ option.label }}
                    </button>
                  </div>
                </transition>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <!-- Loading: Skeleton -->
      <div v-if="deviceStore.loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
        <div v-for="n in 6" :key="n" class="card-editorial p-5 space-y-4">
          <div class="flex justify-between items-start">
            <div class="space-y-2 flex-1">
              <div class="skeleton h-4 w-3/4"></div>
              <div class="skeleton h-3 w-1/2"></div>
            </div>
            <div class="skeleton h-5 w-16"></div>
          </div>
          <div class="space-y-2">
            <div class="skeleton h-3 w-2/3"></div>
            <div class="skeleton h-3 w-1/2"></div>
          </div>
          <div class="pt-4 border-t border-neutral-100">
            <div class="skeleton h-9 w-full"></div>
          </div>
        </div>
      </div>

      <!-- Error state -->
      <div v-else-if="deviceStore.error" class="error-banner">
        <AlertCircle class="w-4 h-4 flex-shrink-0" />
        <span>{{ deviceStore.error }}</span>
      </div>

      <!-- Available Devices -->
      <div v-else-if="activeTab === 'available'">
        <div v-if="filteredDevices.length === 0" class="empty-state">
          <Package class="empty-state-icon" />
          <p class="empty-state-title">No available devices</p>
          <p class="empty-state-text">All devices are currently in use or under repair</p>
        </div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
          <DeviceCard
            v-for="device in paginatedDevices"
            :key="device.id"
            :device="device"
            :show-rent-button="true"
            @rent="handleRent"
          />
        </div>
      </div>

      <!-- Rented Devices -->
      <div v-else-if="activeTab === 'rented'">
        <div v-if="filteredDevices.length === 0" class="empty-state">
          <Truck class="empty-state-icon" />
          <p class="empty-state-title">No rented devices</p>
          <p class="empty-state-text">You haven't rented any devices yet. Browse available devices to get started.</p>
        </div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
          <DeviceCard
            v-for="device in paginatedDevices"
            :key="device.id"
            :device="device"
            :show-return-button="true"
            @return="handleReturn"
          />
        </div>
      </div>

      <!-- All Devices -->
      <div v-else-if="activeTab === 'all'">
        <div v-if="filteredDevices.length === 0" class="empty-state">
          <Package class="empty-state-icon" />
          <p class="empty-state-title">No devices found</p>
          <p class="empty-state-text">Try adjusting your search or filter criteria</p>
        </div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
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
      <div v-if="filteredTotalPages > 1" class="mt-8 flex items-center justify-center gap-1">
        <button
          @click="handlePageChange(deviceStore.currentPage - 1)"
          :disabled="deviceStore.currentPage === 1"
          class="px-3 py-2 text-sm text-neutral-600 hover:bg-neutral-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
        <button
          v-for="page in filteredPages"
          :key="page"
          @click="typeof page === 'number' ? handlePageChange(page) : null"
          :class="[
            'px-3 py-2 text-sm font-medium transition-colors',
            typeof page === 'number' && deviceStore.currentPage === page
              ? 'bg-neutral-900 text-white'
              : 'hover:bg-neutral-100 text-neutral-600',
            typeof page !== 'number' ? 'cursor-default px-2 text-neutral-400' : '',
          ]"
        >
          {{ page }}
        </button>
        <button
          @click="handlePageChange(deviceStore.currentPage + 1)"
          :disabled="deviceStore.currentPage === filteredTotalPages"
          class="px-3 py-2 text-sm text-neutral-600 hover:bg-neutral-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </main>

    <!-- Floating Chat Button -->
    <button
      v-if="showChatButton"
      @click="showChatPanel = !showChatPanel"
      class="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 w-12 h-12 sm:w-14 sm:h-14 bg-primary-600 hover:bg-primary-700 text-white rounded-full flex items-center justify-center transition-colors z-40 shadow-card hover:shadow-card-hover"
    >
      <Bot class="w-5 h-5 sm:w-6 sm:h-6" />
    </button>

    <!-- AI Chat Panel -->
    <transition name="chat">
      <div
        v-if="showChatPanel"
        class="fixed bottom-20 right-4 left-4 sm:bottom-24 sm:right-6 sm:left-auto w-auto sm:w-[350px] md:w-[400px] h-[500px] sm:h-[600px] max-h-[calc(100vh-100px)] sm:max-h-[calc(100vh-120px)] bg-white border border-neutral-200 shadow-modal overflow-hidden flex flex-col z-50"
      >
        <div class="p-4 bg-neutral-900 text-white flex justify-between items-center">
          <div class="flex items-center gap-2">
            <Bot class="w-5 h-5" />
            <h3 class="font-medium text-sm">AI Assistant</h3>
          </div>
          <button @click="showChatPanel = false" class="text-neutral-400 hover:text-white transition-colors">
            <X class="w-4 h-4" />
          </button>
        </div>
        <div class="flex-1 overflow-hidden">
          <ChatAssistant :token="authStore.token" @rent="handleRent" />
        </div>
      </div>
    </transition>

    <!-- Return Modal -->
    <ReturnModal
      :show="showReturnModal"
      :device="deviceToReturn"
      @close="showReturnModal = false; deviceToReturn = null"
      @confirm="handleReturnConfirm"
    />
  </div>
</template>

<style scoped>
/* Scoped styles if needed */
</style>