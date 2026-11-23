<template>
  <div class="space-y-6">
    <Card>
      <template #header>
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div class="flex items-center space-x-3">
            <div class="p-2 bg-indigo-50 rounded-lg border border-indigo-200">
              <ClockIcon class="h-7 w-7 text-indigo-700" />
            </div>
            <div>
              <h1 class="text-2xl font-bold text-paper-text">Histórico de Notificações</h1>
              <p class="text-xs text-gray-500 mt-0.5">
                Auditoria de eventos capturados no CSH, testes manuais e status de entrega no Microsoft Teams.
              </p>
            </div>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <Button variant="secondary" size="sm" @click="testarConexaoCsh" :loading="testingCsh">
              <template #icon>
                <ServerStackIcon class="h-4 w-4 text-gray-600" />
              </template>
              Testar Conexão CSH
            </Button>
            <Button variant="primary" size="sm" @click="sincronizarCsh" :loading="syncingCsh">
              <template #icon>
                <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': syncingCsh }" />
              </template>
              Sincronizar CSH Agora
            </Button>
            <Button variant="secondary" size="sm" @click="carregarHistorico">
              <template #icon>
                <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': loading }" />
              </template>
              Atualizar
            </Button>
          </div>
        </div>
      </template>

      <!-- Mensagem de feedback -->
      <div v-if="feedback.message" :class="feedback.type === 'error' ? 'bg-red-50 border-red-200 text-red-800' : 'bg-emerald-50 border-emerald-200 text-emerald-800'" class="mb-5 p-3.5 rounded-xl border flex items-center justify-between text-sm">
        <span>{{ feedback.message }}</span>
        <button @click="feedback.message = ''" class="text-gray-400 hover:text-gray-600">
          <XMarkIcon class="h-4 w-4" />
        </button>
      </div>

      <!-- KPIs -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="p-4 bg-gray-50 border border-gray-200 rounded-xl">
          <p class="text-xs font-semibold text-gray-500 uppercase">Total Exibido</p>
          <p class="text-2xl font-extrabold text-gray-900 mt-1">{{ historicoFiltrado.length }}</p>
        </div>
        <div class="p-4 bg-emerald-50/70 border border-emerald-200 rounded-xl">
          <p class="text-xs font-semibold text-emerald-700 uppercase">Enviados ao Teams</p>
          <p class="text-2xl font-extrabold text-emerald-800 mt-1">{{ countByStatus('ENVIADO') }}</p>
        </div>
        <div class="p-4 bg-indigo-50/70 border border-indigo-200 rounded-xl">
          <p class="text-xs font-semibold text-indigo-700 uppercase">Simulados</p>
          <p class="text-2xl font-extrabold text-indigo-800 mt-1">{{ countByStatus('SIMULADO') }}</p>
        </div>
        <div class="p-4 bg-red-50/70 border border-red-200 rounded-xl">
          <p class="text-xs font-semibold text-red-700 uppercase">Falhas de Envio</p>
          <p class="text-2xl font-extrabold text-red-800 mt-1">{{ countByStatus('FALHA_ENVIO') }}</p>
        </div>
      </div>

      <!-- Filtros -->
      <div class="flex flex-col sm:flex-row gap-3 mb-4">
        <input
          v-model="busca"
          type="text"
          placeholder="Buscar por ID do chamado, setor ou solicitante..."
          class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none"
        />
        <select
          v-model="filtroOrigem"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
        >
          <option value="TODAS">Todas as Origens</option>
          <option value="CSH_MYSQL">CSH (Automático)</option>
          <option value="TESTE">Testes Manuais</option>
          <option value="CONTINGENCIA">Contingência</option>
        </select>
        <select
          v-model="filtroStatus"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
        >
          <option value="TODOS">Todos os Status</option>
          <option value="ENVIADO">ENVIADO</option>
          <option value="SIMULADO">SIMULADO</option>
          <option value="FALHA_ENVIO">FALHA_ENVIO</option>
          <option value="PENDENTE">PENDENTE</option>
        </select>
      </div>

      <!-- Tabela Completa -->
      <div class="overflow-x-auto bg-white border border-gray-200 rounded-xl">
        <table class="w-full text-left text-xs text-gray-600">
          <thead class="bg-gray-50 text-[11px] uppercase font-bold text-gray-500 border-b">
            <tr>
              <th class="py-3 px-4">Data / Hora</th>
              <th class="py-3 px-4">Origem</th>
              <th class="py-3 px-4">ID Evento</th>
              <th class="py-3 px-4">Localização / Setor</th>
              <th class="py-3 px-4">Detalhes</th>
              <th class="py-3 px-4">Mencionados</th>
              <th class="py-3 px-4 text-center">Status</th>
              <th class="py-3 px-4 text-center">Tentativas</th>
              <th class="py-3 px-4 text-right">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="loading && historico.length === 0">
              <td colspan="9" class="py-8 text-center text-gray-400">Carregando histórico...</td>
            </tr>
            <tr v-else-if="historicoFiltrado.length === 0">
              <td colspan="9" class="py-8 text-center text-gray-400">
                Nenhuma notificação encontrada com os filtros aplicados.
              </td>
            </tr>
            <tr v-for="item in historicoFiltrado" :key="item.id" class="hover:bg-gray-50/80 transition-colors">
              <td class="py-3 px-4 whitespace-nowrap text-gray-700">
                {{ formatarData(item.data_envio || item.data_criacao || item.data_hora_obito) }}
              </td>
              <td class="py-3 px-4 whitespace-nowrap">
                <span :class="getOrigemBadgeClass(item.fonte_origem)" class="px-2 py-0.5 rounded font-bold text-[10px]">
                  {{ item.fonte_origem }}
                </span>
              </td>
              <td class="py-3 px-4 font-mono font-bold text-gray-800 whitespace-nowrap">
                #{{ item.id_evento_origem }}
              </td>
              <td class="py-3 px-4 font-medium text-gray-800">
                {{ item.setor_leito || '-' }}
              </td>
              <td class="py-3 px-4 max-w-xs truncate" :title="item.causa_morte || ''">
                {{ item.causa_morte || item.nome_paciente || '-' }}
              </td>
              <td class="py-3 px-4">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="(nome, idx) in parseDestinatarios(item.destinatarios_notificados)"
                    :key="idx"
                    class="px-1.5 py-0.5 bg-gray-100 text-gray-700 rounded text-[10px] font-medium"
                  >
                    @{{ nome }}
                  </span>
                  <span v-if="parseDestinatarios(item.destinatarios_notificados).length === 0" class="text-gray-400">-</span>
                </div>
              </td>
              <td class="py-3 px-4 text-center whitespace-nowrap">
                <span
                  :class="getStatusBadgeClass(item.status_envio)"
                  :title="item.ultimo_erro || ''"
                  class="px-2 py-0.5 rounded font-bold text-[10px]"
                >
                  {{ item.status_envio }}
                </span>
              </td>
              <td class="py-3 px-4 text-center font-bold">{{ item.tentativas_envio }}</td>
              <td class="py-3 px-4 text-right whitespace-nowrap">
                <button
                  v-if="item.status_envio === 'FALHA_ENVIO' || item.status_envio === 'PENDENTE'"
                  @click="reenviarNotificacao(item)"
                  :disabled="resendingId === item.id"
                  class="px-2.5 py-1 text-[11px] font-semibold text-amber-800 bg-amber-50 hover:bg-amber-100 border border-amber-300 rounded-md transition disabled:opacity-50"
                >
                  {{ resendingId === item.id ? 'Reenviando...' : 'Reenviar' }}
                </button>
                <button
                  v-else
                  @click="reenviarNotificacao(item)"
                  :disabled="resendingId === item.id"
                  title="Disparar novamente para o Teams"
                  class="px-2 py-1 text-[11px] font-semibold text-gray-600 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-md transition disabled:opacity-50"
                >
                  {{ resendingId === item.id ? '...' : 'Reenviar' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import api from '../services/api';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import {
  ClockIcon,
  ArrowPathIcon,
  ServerStackIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline';

interface NotificacaoItem {
  id: number;
  fonte_origem: string;
  id_evento_origem: string;
  nome_paciente?: string;
  setor_leito?: string;
  causa_morte?: string;
  modo_apresentacao: string;
  destinatarios_notificados?: string;
  status_envio: string;
  tentativas_envio: number;
  ultimo_erro?: string;
  data_hora_obito?: string;
  data_envio?: string;
  data_criacao?: string;
}

const historico = ref<NotificacaoItem[]>([]);
const loading = ref(false);
const testingCsh = ref(false);
const syncingCsh = ref(false);
const resendingId = ref<number | null>(null);
const busca = ref('');
const filtroOrigem = ref('TODAS');
const filtroStatus = ref('TODOS');
const feedback = ref<{ type: 'success' | 'error'; message: string }>({ type: 'success', message: '' });

const historicoFiltrado = computed(() => {
  return historico.value.filter(item => {
    if (filtroOrigem.value !== 'TODAS' && item.fonte_origem !== filtroOrigem.value) return false;
    if (filtroStatus.value !== 'TODOS' && item.status_envio !== filtroStatus.value) return false;
    if (busca.value.trim()) {
      const q = busca.value.toLowerCase();
      return (
        item.id_evento_origem.toLowerCase().includes(q) ||
        (item.setor_leito || '').toLowerCase().includes(q) ||
        (item.causa_morte || '').toLowerCase().includes(q) ||
        (item.nome_paciente || '').toLowerCase().includes(q)
      );
    }
    return true;
  });
});

const countByStatus = (status: string) => historicoFiltrado.value.filter(i => i.status_envio === status).length;

const carregarHistorico = async () => {
  loading.value = true;
  try {
    const res = await api.get<NotificacaoItem[]>('/api/notificacoes/obitos?limit=100');
    historico.value = res.data;
  } catch (err: any) {
    feedback.value = { type: 'error', message: err.response?.data?.detail || 'Erro ao carregar histórico.' };
  } finally {
    loading.value = false;
  }
};

const testarConexaoCsh = async () => {
  testingCsh.value = true;
  feedback.value.message = '';
  try {
    const res = await api.get('/api/notificacoes/csh/teste-conexao');
    const status = res.data?.diagnostico?.status;
    const amostra = res.data?.total_amostra ?? 0;
    if (status === 'sucesso') {
      feedback.value = {
        type: 'success',
        message: `Conexão com o banco CSH OK! ${amostra} solicitação(ões) recente(s) encontrada(s) na amostra.`,
      };
    } else {
      feedback.value = {
        type: 'error',
        message: `Falha na conexão CSH: ${res.data?.diagnostico?.detalhe || 'Erro desconhecido'}`,
      };
    }
  } catch (err: any) {
    feedback.value = { type: 'error', message: err.response?.data?.detail || 'Erro ao testar conexão CSH.' };
  } finally {
    testingCsh.value = false;
  }
};

const sincronizarCsh = async () => {
  syncingCsh.value = true;
  feedback.value.message = '';
  try {
    const res = await api.post('/api/notificacoes/csh/sincronizar');
    const { total_encontrados, novos_notificados, ignorados_duplicados } = res.data;
    feedback.value = {
      type: 'success',
      message: `Sincronização concluída: ${novos_notificados} nova(s) notificação(ões) disparada(s), ${ignorados_duplicados} já registrada(s) (total consultado: ${total_encontrados}).`,
    };
    await carregarHistorico();
  } catch (err: any) {
    feedback.value = { type: 'error', message: err.response?.data?.detail || 'Erro ao sincronizar chamados do CSH.' };
  } finally {
    syncingCsh.value = false;
  }
};

const reenviarNotificacao = async (item: NotificacaoItem) => {
  resendingId.value = item.id;
  feedback.value.message = '';
  try {
    const res = await api.post(`/api/notificacoes/obitos/${item.id}/reenviar`);
    feedback.value = {
      type: res.data.status_envio === 'FALHA_ENVIO' ? 'error' : 'success',
      message: `Notificação #${item.id_evento_origem} reenviada — Status atual: ${res.data.status_envio}.`,
    };
    await carregarHistorico();
  } catch (err: any) {
    feedback.value = { type: 'error', message: err.response?.data?.detail || 'Erro ao reenviar notificação.' };
  } finally {
    resendingId.value = null;
  }
};

const parseDestinatarios = (raw?: string): string[] => {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) {
      return parsed.map((d: any) => d.nome || d.email_teams || '').filter(Boolean);
    }
  } catch {
    // ignore
  }
  return [];
};

const formatarData = (iso?: string): string => {
  if (!iso) return '-';
  const date = new Date(iso);
  if (isNaN(date.getTime())) return iso;
  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'ENVIADO':
      return 'bg-emerald-100 text-emerald-800';
    case 'SIMULADO':
      return 'bg-indigo-100 text-indigo-800';
    case 'FALHA_ENVIO':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-amber-100 text-amber-800';
  }
};

const getOrigemBadgeClass = (origem: string) => {
  switch (origem) {
    case 'CSH_MYSQL':
      return 'bg-sky-100 text-sky-800';
    case 'TESTE':
      return 'bg-purple-100 text-purple-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

onMounted(() => {
  carregarHistorico();
});
</script>
