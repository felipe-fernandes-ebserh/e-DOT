<template>
  <div class="space-y-6">
    <Card>
      <template #header>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="flex items-center space-x-3">
            <HomeIcon class="h-7 w-7 text-paper-text" />
            <div>
              <h1 class="text-2xl font-bold text-paper-text">Bem-vindo ao {{ SYSTEM_TITLE }}</h1>
              <p class="text-xs text-gray-500">
                Sistema de Notificação de Solicitações de Declaração de Óbito &bull; CIHDOTT / HC-UFPE
              </p>
            </div>
          </div>
          <span
            v-if="authStore.isAuthenticated && monitorStatus"
            :class="monitorStatus.polling_ativo ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-gray-100 text-gray-600 border-gray-300'"
            class="px-3 py-1 text-xs font-semibold rounded-full border w-fit flex items-center gap-1.5"
          >
            <span class="h-2 w-2 rounded-full" :class="monitorStatus.polling_ativo ? 'bg-emerald-500 animate-pulse' : 'bg-gray-400'"></span>
            {{ monitorStatus.polling_ativo ? `Monitoramento CSH Ativo (${monitorStatus.intervalo_segundos}s)` : 'Monitoramento CSH Pausado' }}
          </span>
        </div>
      </template>

      <div class="space-y-6">
        <p class="text-sm text-gray-700 leading-relaxed">
          O <strong>{{ SYSTEM_TITLE }}</strong> monitora continuamente as solicitações de Declaração de Óbito no sistema CSH e alerta automaticamente a equipe de Busca Ativa pelo Microsoft Teams.
        </p>

        <!-- Métricas Operacionais (quando autenticado) -->
        <div v-if="authStore.isAuthenticated" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="p-4 bg-sky-50/70 border border-sky-200 rounded-xl">
            <p class="text-xs font-semibold text-sky-700 uppercase">Chamados CSH Capturados</p>
            <p class="text-2xl font-extrabold text-sky-900 mt-1">{{ metrics.cshCapturados }}</p>
            <p class="text-[11px] text-sky-700/80 mt-0.5">Nos últimos registros</p>
          </div>
          <div class="p-4 bg-emerald-50/70 border border-emerald-200 rounded-xl">
            <p class="text-xs font-semibold text-emerald-700 uppercase">Enviados ao Teams</p>
            <p class="text-2xl font-extrabold text-emerald-900 mt-1">{{ metrics.enviados }}</p>
            <p class="text-[11px] text-emerald-700/80 mt-0.5">Entregas confirmadas</p>
          </div>
          <div class="p-4 bg-amber-50/70 border border-amber-200 rounded-xl">
            <p class="text-xs font-semibold text-amber-700 uppercase">Falhas Pendentes</p>
            <p class="text-2xl font-extrabold text-amber-900 mt-1">{{ metrics.falhas }}</p>
            <p class="text-[11px] text-amber-700/80 mt-0.5">Disponíveis p/ reenvio</p>
          </div>
          <div class="p-4 bg-indigo-50/70 border border-indigo-200 rounded-xl">
            <p class="text-xs font-semibold text-indigo-700 uppercase">Equipe Ativa (Teams)</p>
            <p class="text-2xl font-extrabold text-indigo-900 mt-1">{{ metrics.equipeAtiva }}</p>
            <p class="text-[11px] text-indigo-700/80 mt-0.5">Profissionais mencionados</p>
          </div>
        </div>

        <!-- Atalhos Rápidos -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-1">
          <router-link to="/historico-notificacoes" class="p-4 bg-gray-50 hover:bg-white border border-gray-200 hover:border-sky-300 rounded-xl space-y-1.5 hover:shadow-md transition-all duration-200 group block">
            <h3 class="font-bold text-gray-800 group-hover:text-sky-700 flex items-center gap-2">
              <ClockIcon class="h-5 w-5 text-sky-600" />
              Histórico
            </h3>
            <p class="text-xs text-gray-500">Acompanhe os chamados capturados do CSH, reenvie falhas e sincronize manualmente.</p>
          </router-link>

          <router-link to="/equipe-teams" class="p-4 bg-gray-50 hover:bg-white border border-gray-200 hover:border-emerald-300 rounded-xl space-y-1.5 hover:shadow-md transition-all duration-200 group block">
            <h3 class="font-bold text-gray-800 group-hover:text-emerald-700 flex items-center gap-2">
              <UserGroupIcon class="h-5 w-5 text-emerald-600" />
              Equipe Teams
            </h3>
            <p class="text-xs text-gray-500">Adicione, pause ou remova profissionais que recebem @menções nos alertas.</p>
          </router-link>

          <router-link to="/teste-notificacoes" class="p-4 bg-gray-50 hover:bg-white border border-gray-200 hover:border-amber-300 rounded-xl space-y-1.5 hover:shadow-md transition-all duration-200 group block">
            <h3 class="font-bold text-gray-800 group-hover:text-amber-700 flex items-center gap-2">
              <BellAlertIcon class="h-5 w-5 text-amber-600" />
              Teste Teams
            </h3>
            <p class="text-xs text-gray-500">Dispare alertas simulados ou reais para validar notificações nos celulares da equipe.</p>
          </router-link>

          <router-link to="/configuracoes" class="p-4 bg-gray-50 hover:bg-white border border-gray-200 hover:border-gray-400 rounded-xl space-y-1.5 hover:shadow-md transition-all duration-200 group block">
            <h3 class="font-bold text-gray-800 group-hover:text-paper-text flex items-center gap-2">
              <Cog6ToothIcon class="h-5 w-5 text-gray-600" />
              Configurações
            </h3>
            <p class="text-xs text-gray-500">Gerencie usuários autorizados e perfis de acesso (RBAC) do sistema.</p>
          </router-link>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../services/api';
import Card from '../components/Card.vue';
import { useAuthStore } from '../stores/auth';
import { SYSTEM_TITLE } from '../config/version';
import {
  HomeIcon,
  ClockIcon,
  UserGroupIcon,
  BellAlertIcon,
  Cog6ToothIcon,
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();

const monitorStatus = ref<{ polling_ativo: boolean; intervalo_segundos: number } | null>(null);
const metrics = ref({
  cshCapturados: 0,
  enviados: 0,
  falhas: 0,
  equipeAtiva: 0,
});

const carregarResumo = async () => {
  if (!authStore.isAuthenticated) return;
  try {
    const [resMonitor, resObitos, resEquipe] = await Promise.all([
      api.get('/api/notificacoes/csh/status-monitoramento'),
      api.get('/api/notificacoes/obitos?limit=100'),
      api.get('/api/notificacoes/destinatarios?apenas_ativos=true'),
    ]);
    monitorStatus.value = resMonitor.data;
    const lista = resObitos.data || [];
    metrics.value = {
      cshCapturados: lista.filter((i: any) => i.fonte_origem === 'CSH_MYSQL').length,
      enviados: lista.filter((i: any) => i.status_envio === 'ENVIADO').length,
      falhas: lista.filter((i: any) => i.status_envio === 'FALHA_ENVIO').length,
      equipeAtiva: (resEquipe.data || []).length,
    };
  } catch {
    // Mantém valores padrão caso haja falha pontual
  }
};

onMounted(() => {
  carregarResumo();
});
</script>
