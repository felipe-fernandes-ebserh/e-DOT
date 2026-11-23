<template>
  <div class="space-y-6">
    <Card>
      <template #header>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="flex items-center space-x-3">
            <div class="p-2 bg-primary-50 rounded-lg border border-primary-200">
              <UserGroupIcon class="h-7 w-7 text-primary-700" />
            </div>
            <div>
              <h1 class="text-2xl font-bold text-paper-text">Equipe de Notificações (Teams)</h1>
              <p class="text-xs text-gray-500 mt-0.5">
                Configure os profissionais da CIHDOTT / Busca Ativa que serão mencionados (@mention) nos alertas do Microsoft Teams.
              </p>
            </div>
          </div>
          <Button variant="secondary" size="sm" @click="carregarDestinatarios">
            <template #icon>
              <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': loading }" />
            </template>
            Atualizar
          </Button>
        </div>
      </template>

      <!-- Mensagem de feedback -->
      <div v-if="feedback.message" :class="feedback.type === 'error' ? 'bg-red-50 border-red-200 text-red-800' : 'bg-emerald-50 border-emerald-200 text-emerald-800'" class="mb-5 p-3.5 rounded-xl border flex items-center justify-between text-sm">
        <span>{{ feedback.message }}</span>
        <button @click="feedback.message = ''" class="text-gray-400 hover:text-gray-600">
          <XMarkIcon class="h-4 w-4" />
        </button>
      </div>

      <!-- Cards de Resumo -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="p-4 bg-gray-50 border border-gray-200 rounded-xl">
          <p class="text-xs font-semibold text-gray-500 uppercase">Total Cadastrados</p>
          <p class="text-2xl font-extrabold text-gray-900 mt-1">{{ destinatarios.length }}</p>
        </div>
        <div class="p-4 bg-emerald-50/70 border border-emerald-200 rounded-xl">
          <p class="text-xs font-semibold text-emerald-700 uppercase">Ativos (Recebendo Alertas)</p>
          <p class="text-2xl font-extrabold text-emerald-800 mt-1">{{ totalAtivos }}</p>
        </div>
        <div class="p-4 bg-amber-50/60 border border-amber-200 rounded-xl">
          <p class="text-xs font-semibold text-amber-700 uppercase">Inativos (Pausados)</p>
          <p class="text-2xl font-extrabold text-amber-800 mt-1">{{ destinatarios.length - totalAtivos }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Formulário de Adição -->
        <div class="lg:col-span-5">
          <div class="p-5 bg-gray-50 border border-gray-200 rounded-xl space-y-4">
            <div class="flex items-center justify-between border-b pb-3">
              <h2 class="text-sm font-bold text-gray-800 uppercase flex items-center gap-2">
                <UserPlusIcon class="h-5 w-5 text-primary-600" />
                Adicionar Profissional
              </h2>
              <button
                type="button"
                @click="preencherComMeuUsuario"
                class="text-xs text-primary-600 hover:underline font-semibold"
              >
                Usar Meus Dados
              </button>
            </div>

            <form @submit.prevent="salvarNovoDestinatario" class="space-y-3 text-sm">
              <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Nome Completo *</label>
                <input
                  v-model="novoDest.nome"
                  type="text"
                  required
                  placeholder="Ex: Dra. Ana Paula"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none bg-white"
                />
              </div>

              <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">E-mail Teams (UPN Ebserh) *</label>
                <input
                  v-model="novoDest.email_teams"
                  type="email"
                  required
                  placeholder="Ex: ana.paula@ebserh.gov.br"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none bg-white"
                />
                <p class="text-[11px] text-gray-500 mt-1">
                  O e-mail deve corresponder exatamente à conta do Microsoft Teams para a menção @ funcionar.
                </p>
              </div>

              <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Cargo / Setor</label>
                <input
                  v-model="novoDest.cargo_setor"
                  type="text"
                  placeholder="Ex: Médico Plantonista CIHDOTT"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none bg-white"
                />
              </div>

              <div class="pt-2">
                <Button type="submit" variant="primary" class="w-full justify-center" :loading="isSaving">
                  <template #icon>
                    <UserPlusIcon class="h-4 w-4" />
                  </template>
                  Incluir na Equipe
                </Button>
              </div>
            </form>
          </div>
        </div>

        <!-- Lista de Profissionais -->
        <div class="lg:col-span-7 space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <input
              v-model="busca"
              type="text"
              placeholder="Buscar por nome, e-mail ou setor..."
              class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none"
            />
            <select
              v-model="filtroStatus"
              class="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
            >
              <option value="TODOS">Todos ({{ destinatarios.length }})</option>
              <option value="ATIVOS">Somente Ativos ({{ totalAtivos }})</option>
              <option value="INATIVOS">Somente Inativos ({{ destinatarios.length - totalAtivos }})</option>
            </select>
          </div>

          <div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <div v-if="loading" class="p-8 text-center text-sm text-gray-500">
              Carregando equipe...
            </div>
            <div v-else-if="destinatariosFiltrados.length === 0" class="p-8 text-center text-sm text-gray-500">
              Nenhum profissional encontrado com os filtros atuais.
            </div>
            <ul v-else class="divide-y divide-gray-100">
              <li
                v-for="d in destinatariosFiltrados"
                :key="d.id"
                class="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-gray-50/70 transition-colors"
              >
                <div class="min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="font-bold text-gray-900 truncate">{{ d.nome }}</span>
                    <span
                      :class="d.ativo ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-600'"
                      class="text-[11px] px-2 py-0.5 rounded-full font-bold shrink-0"
                    >
                      {{ d.ativo ? 'ATIVO' : 'INATIVO' }}
                    </span>
                  </div>
                  <p class="text-xs text-gray-600 truncate mt-0.5">{{ d.email_teams }}</p>
                  <p class="text-[11px] text-gray-400 truncate">{{ d.cargo_setor || 'CIHDOTT / HC-UFPE' }}</p>
                </div>

                <div class="flex items-center gap-2 shrink-0">
                  <button
                    @click="alternarStatus(d)"
                    :class="d.ativo ? 'text-amber-700 bg-amber-50 hover:bg-amber-100 border-amber-200' : 'text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border-emerald-200'"
                    class="px-3 py-1.5 text-xs font-semibold border rounded-lg transition"
                  >
                    {{ d.ativo ? 'Pausar / Inativar' : 'Ativar' }}
                  </button>
                  <button
                    @click="excluirDestinatario(d)"
                    title="Remover da equipe"
                    class="px-2.5 py-1.5 text-xs font-semibold text-red-600 bg-red-50 hover:bg-red-100 border border-red-200 rounded-lg transition"
                  >
                    Remover
                  </button>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import api from '../services/api';
import { useAuthStore } from '../stores/auth';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import {
  UserGroupIcon,
  UserPlusIcon,
  ArrowPathIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline';

interface Destinatario {
  id: number;
  nome: string;
  email_teams: string;
  cargo_setor?: string;
  ativo: boolean;
}

const authStore = useAuthStore();
const destinatarios = ref<Destinatario[]>([]);
const loading = ref(false);
const isSaving = ref(false);
const busca = ref('');
const filtroStatus = ref<'TODOS' | 'ATIVOS' | 'INATIVOS'>('TODOS');
const feedback = ref<{ type: 'success' | 'error'; message: string }>({ type: 'success', message: '' });

const novoDest = ref({
  nome: '',
  email_teams: '',
  cargo_setor: 'CIHDOTT / HC-UFPE',
});

const totalAtivos = computed(() => destinatarios.value.filter(d => d.ativo).length);

const destinatariosFiltrados = computed(() => {
  return destinatarios.value.filter(d => {
    if (filtroStatus.value === 'ATIVOS' && !d.ativo) return false;
    if (filtroStatus.value === 'INATIVOS' && d.ativo) return false;
    if (busca.value.trim()) {
      const q = busca.value.toLowerCase();
      return (
        d.nome.toLowerCase().includes(q) ||
        d.email_teams.toLowerCase().includes(q) ||
        (d.cargo_setor || '').toLowerCase().includes(q)
      );
    }
    return true;
  });
});

const carregarDestinatarios = async () => {
  loading.value = true;
  try {
    const res = await api.get<Destinatario[]>('/api/notificacoes/destinatarios?apenas_ativos=false');
    destinatarios.value = res.data;
  } catch (err: any) {
    feedback.value = { type: 'error', message: err.response?.data?.detail || 'Erro ao carregar destinatários.' };
  } finally {
    loading.value = false;
  }
};

const preencherComMeuUsuario = () => {
  const user = authStore.user;
  const nome = Array.isArray(user?.displayName) ? user.displayName[0] : (user?.displayName || user?.username || '');
  const email = Array.isArray(user?.email) ? user.email[0] : (user?.email || `${user?.username || 'usuario'}@ebserh.gov.br`);
  const dept = Array.isArray(user?.department) ? user.department[0] : (user?.department || 'CIHDOTT / HC-UFPE');
  novoDest.value = { nome, email_teams: email, cargo_setor: dept };
};

const salvarNovoDestinatario = async () => {
  if (!novoDest.value.nome.trim() || !novoDest.value.email_teams.trim()) return;
  isSaving.value = true;
  feedback.value.message = '';
  try {
    await api.post('/api/notificacoes/destinatarios', novoDest.value);
    novoDest.value = { nome: '', email_teams: '', cargo_setor: 'CIHDOTT / HC-UFPE' };
    feedback.value = { type: 'success', message: 'Profissional adicionado à equipe com sucesso!' };
    await carregarDestinatarios();
  } catch (err: any) {
    feedback.value = { type: 'error', message: err.response?.data?.detail || 'Erro ao cadastrar destinatário (verifique permissões).' };
  } finally {
    isSaving.value = false;
  }
};

const alternarStatus = async (dest: Destinatario) => {
  try {
    await api.put(`/api/notificacoes/destinatarios/${dest.id}`, { ativo: !dest.ativo });
    feedback.value = {
      type: 'success',
      message: `${dest.nome} agora está ${!dest.ativo ? 'ATIVO' : 'INATIVO'}.`,
    };
    await carregarDestinatarios();
  } catch (err: any) {
    feedback.value = { type: 'error', message: err.response?.data?.detail || 'Erro ao atualizar status.' };
  }
};

const excluirDestinatario = async (dest: Destinatario) => {
  if (!confirm(`Deseja realmente remover "${dest.nome}" da equipe de alertas?`)) return;
  try {
    await api.delete(`/api/notificacoes/destinatarios/${dest.id}`);
    feedback.value = { type: 'success', message: `${dest.nome} removido(a) da equipe.` };
    await carregarDestinatarios();
  } catch (err: any) {
    feedback.value = { type: 'error', message: err.response?.data?.detail || 'Erro ao remover destinatário.' };
  }
};

onMounted(() => {
  carregarDestinatarios();
});
</script>
