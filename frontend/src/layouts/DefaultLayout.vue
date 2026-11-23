<template>
  <div class="relative h-screen overflow-hidden md:flex">
    <!-- Mobile Menu Header -->
    <div class="bg-paper-sidebar text-gray-100 flex justify-between md:hidden shrink-0">
      <router-link to="/" class="block p-4 text-white font-bold">{{ SYSTEM_TITLE }}</router-link>
      <button @click="sidebarOpen = !sidebarOpen" class="p-4 focus:outline-none focus:bg-paper-active-link">
        <Bars3Icon class="h-6 w-6" />
      </button>
    </div>

    <!-- Sidebar (Expansível / Recolhível) -->
    <aside 
      :class="[
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        isCollapsed ? 'md:w-20' : 'md:w-64'
      ]" 
      class="bg-paper-sidebar text-gray-100 pt-7 pb-2 px-2 absolute inset-y-0 left-0 transform md:relative md:translate-x-0 transition-all duration-300 ease-in-out z-20 h-full shrink-0 flex flex-col justify-between"
    >
      <div>
        <!-- Logo HC-UFPE / EBSERH + Identidade e-DOT (clique para recolher/expandir) -->
        <div
          @click="toggleSidebar"
          title="Clique para recolher / expandir o menu"
          class="cursor-pointer px-2 mb-5 select-none group"
        >
          <div
            v-if="!isCollapsed"
            class="bg-white rounded-xl px-3 py-2 shadow-sm border border-white/20 mb-3 flex items-center justify-center group-hover:shadow transition"
          >
            <img src="/logo-hc-ebserh.png" alt="HC-UFPE EBSERH" class="h-8 w-auto object-contain" />
          </div>
          <div class="text-white flex items-center space-x-3 px-2 hover:opacity-90 transition duration-150" :class="isCollapsed ? 'justify-center' : ''">
            <CubeTransparentIcon class="h-7 w-7 shrink-0 text-emerald-400 group-hover:scale-105 transition-transform" />
            <div v-if="!isCollapsed" class="min-w-0">
              <span class="text-xl font-extrabold leading-none block truncate">
                {{ SYSTEM_TITLE }}
              </span>
              <span class="text-[11px] text-gray-300 block truncate mt-0.5">
                Busca Ativa &bull; CIHDOTT
              </span>
            </div>
          </div>
        </div>

        <div class="px-3 my-3">
          <div class="border-t border-white border-opacity-20"></div>
        </div>

        <!-- Links de Navegação -->
        <nav class="space-y-1.5">
          <router-link 
            to="/" 
            :title="isCollapsed ? 'Início' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-4']"
            class="flex items-center space-x-3 py-2.5 rounded-lg transition duration-200 hover:bg-paper-active-link hover:text-white"
          >
            <HomeIcon class="h-5 w-5 shrink-0"/>
            <span v-if="!isCollapsed" class="truncate text-sm font-medium">Início</span>
          </router-link>

          <router-link 
            v-if="authStore.isAuthenticated" 
            to="/historico-notificacoes" 
            :title="isCollapsed ? 'Histórico de Notificações' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-4']"
            class="flex items-center space-x-3 py-2.5 rounded-lg transition duration-200 hover:bg-paper-active-link hover:text-white"
          >
            <ClockIcon class="h-5 w-5 shrink-0 text-sky-400" />
            <span v-if="!isCollapsed" class="truncate text-sm font-medium">Histórico</span>
          </router-link>

          <router-link 
            v-if="authStore.isAuthenticated" 
            to="/equipe-teams" 
            :title="isCollapsed ? 'Configurar Equipe' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-4']"
            class="flex items-center space-x-3 py-2.5 rounded-lg transition duration-200 hover:bg-paper-active-link hover:text-white"
          >
            <UserGroupIcon class="h-5 w-5 shrink-0 text-emerald-400" />
            <span v-if="!isCollapsed" class="truncate text-sm font-medium">Equipe Teams</span>
          </router-link>

          <router-link 
            v-if="authStore.isAuthenticated" 
            to="/teste-notificacoes" 
            :title="isCollapsed ? 'Teste Teams' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-4']"
            class="flex items-center space-x-3 py-2.5 rounded-lg transition duration-200 hover:bg-paper-active-link hover:text-white"
          >
            <BellAlertIcon class="h-5 w-5 shrink-0 text-amber-400" />
            <span v-if="!isCollapsed" class="truncate text-sm font-medium">Teste Teams</span>
          </router-link>

          <router-link 
            v-if="authStore.isAuthenticated" 
            to="/configuracoes" 
            :title="isCollapsed ? 'Configurações' : ''"
            :class="[isCollapsed ? 'justify-center px-2' : 'px-4']"
            class="flex items-center space-x-3 py-2.5 rounded-lg transition duration-200 hover:bg-paper-active-link hover:text-white"
          >
            <Cog6ToothIcon class="h-5 w-5 shrink-0"/>
            <span v-if="!isCollapsed" class="truncate text-sm font-medium">Configurações</span>
          </router-link>
        </nav>
      </div>

      <!-- Rodapé de Versão da Sidebar -->
      <div v-if="!isCollapsed" class="px-4 pt-3 pb-1 border-t border-white/10 text-xs text-gray-400 mt-auto truncate transition-opacity duration-200">
        <p class="font-semibold text-gray-200 truncate">{{ APP_NAME }}</p>
        <p class="text-[11px] text-gray-400 truncate">Versão {{ APP_VERSION }} | HC-UFPE</p>
      </div>
      <div v-else class="px-2 pt-3 pb-1 border-t border-white/10 text-[10px] text-center text-gray-400 mt-auto">
        v{{ APP_VERSION }}
      </div>
    </aside>

    <!-- Content -->
    <div class="flex-1 flex flex-col bg-paper-bg overflow-y-auto h-full">
      <header class="flex justify-between items-center p-6 bg-white/80 backdrop-blur-md border-b border-gray-300 sticky top-0 z-10">
        <div>
          <h1 class="text-2xl font-semibold text-paper-text">{{ $route.name }}</h1>
        </div>
        <div class="flex items-center gap-3">
          <div
            v-if="authStore.isAuthenticated && monitorStatus"
            :title="monitorTooltip"
            :class="monitorBadgeClass"
            class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold"
          >
            <span class="h-2 w-2 rounded-full" :class="monitorDotClass"></span>
            <span>{{ monitorLabel }}</span>
          </div>
          <router-link v-if="!authStore.isAuthenticated" to="/login">
            <Button variant="primary">
              <template #icon>
                <ArrowRightOnRectangleIcon class="h-5 w-5" />
              </template>
              Login
            </Button>
          </router-link>
          <ProfileDropdown v-else />
        </div>
      </header>
      <main class="flex-1">
        <div class="container py-4 md:py-6">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../services/api';
import {
  HomeIcon,
  ClockIcon,
  UserGroupIcon,
  Cog6ToothIcon,
  CubeTransparentIcon,
  Bars3Icon,
  ArrowRightOnRectangleIcon,
  BellAlertIcon,
} from '@heroicons/vue/24/outline';
import ProfileDropdown from '../components/ProfileDropdown.vue';
import Button from '../components/Button.vue';
import { useAuthStore } from '../stores/auth';
import { APP_VERSION, APP_NAME, SYSTEM_TITLE } from '../config/version';

const sidebarOpen = ref(false);
const isCollapsed = ref(false);

const route = useRoute();
const authStore = useAuthStore();

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

// Close mobile sidebar on route change
watch(() => route.path, () => {
  sidebarOpen.value = false;
});

interface MonitorStatus {
  polling_ativo: boolean;
  intervalo_segundos: number;
  last_check_at: string | null;
  last_status: string;
  last_error: string | null;
  teams_ativo: boolean;
  teams_simulado: boolean;
}

const monitorStatus = ref<MonitorStatus | null>(null);
let monitorTimer: ReturnType<typeof setInterval> | null = null;

const carregarStatusMonitoramento = async () => {
  if (!authStore.isAuthenticated) return;
  try {
    const res = await api.get<MonitorStatus>('/api/notificacoes/csh/status-monitoramento');
    monitorStatus.value = res.data;
  } catch {
    // Silencioso no cabeçalho
  }
};

const monitorBadgeClass = computed(() => {
  if (!monitorStatus.value?.polling_ativo) return 'bg-gray-100 text-gray-600 border-gray-300';
  if (monitorStatus.value.last_status === 'ERRO') return 'bg-red-50 text-red-700 border-red-200';
  return 'bg-emerald-50 text-emerald-700 border-emerald-200';
});

const monitorDotClass = computed(() => {
  if (!monitorStatus.value?.polling_ativo) return 'bg-gray-400';
  if (monitorStatus.value.last_status === 'ERRO') return 'bg-red-500 animate-pulse';
  return 'bg-emerald-500 animate-pulse';
});

const monitorLabel = computed(() => {
  if (!monitorStatus.value?.polling_ativo) return 'Polling CSH Pausado';
  if (monitorStatus.value.last_status === 'ERRO') return 'CSH: Erro na Varredura';
  return `CSH Ativo (${monitorStatus.value.intervalo_segundos}s)`;
});

const monitorTooltip = computed(() => {
  if (!monitorStatus.value) return '';
  const last = monitorStatus.value.last_check_at
    ? new Date(monitorStatus.value.last_check_at).toLocaleTimeString('pt-BR')
    : 'aguardando primeiro ciclo';
  const err = monitorStatus.value.last_error ? ` | Erro: ${monitorStatus.value.last_error}` : '';
  return `Última checagem: ${last}${err}`;
});

watch(() => authStore.isAuthenticated, (loggedIn) => {
  if (loggedIn) carregarStatusMonitoramento();
  else monitorStatus.value = null;
});

onMounted(() => {
  if (authStore.isAuthenticated) carregarStatusMonitoramento();
  monitorTimer = setInterval(carregarStatusMonitoramento, 30000);
});

onUnmounted(() => {
  if (monitorTimer) clearInterval(monitorTimer);
});
</script>