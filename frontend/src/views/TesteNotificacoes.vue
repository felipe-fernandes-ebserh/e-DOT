<template>
  <div class="space-y-6">
    <!-- Cabeçalho Principal -->
    <Card>
      <template #header>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="flex items-center space-x-3">
            <div class="p-2 bg-amber-50 rounded-lg border border-amber-200">
              <BellAlertIcon class="h-7 w-7 text-amber-600" />
            </div>
            <div>
              <h1 class="text-2xl font-bold text-paper-text">Teste de Notificações - Microsoft Teams</h1>
              <p class="text-xs text-gray-500 mt-0.5">
                Validação de entrega de alertas sonoros e push da Busca Ativa da CIHDOTT / e-DOT.
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Button variant="secondary" size="sm" @click="abrirGerenciarEquipe">
              <template #icon>
                <UserGroupIcon class="h-4 w-4 text-gray-600" />
              </template>
              Gerenciar Equipe Teams
            </Button>
            <span 
              :class="teamsStatusBadge.class" 
              class="px-3 py-1 text-xs font-semibold rounded-full border flex items-center gap-1.5"
            >
              <span class="h-2 w-2 rounded-full" :class="teamsStatusBadge.dot"></span>
              {{ teamsStatusBadge.text }}
            </span>
          </div>
        </div>
      </template>

      <!-- Mensagens de Alerta Globais -->
      <div v-if="alertMessage" :class="alertClasses" class="p-4 rounded-xl border flex items-start gap-3 text-sm">
        <component :is="alertIcon" class="h-5 w-5 shrink-0 mt-0.5" />
        <div class="flex-1">
          <p class="font-bold">{{ alertTitle }}</p>
          <p class="mt-0.5">{{ alertMessage }}</p>
        </div>
        <button @click="alertMessage = ''" class="text-gray-400 hover:text-gray-600">
          <XMarkIcon class="h-4 w-4" />
        </button>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Coluna da Esquerda: Configuração e Formulário (7 colunas) -->
        <div class="lg:col-span-7 space-y-6">

          <!-- 1. Destino do Envio: Simulação vs Envio Real Teams -->
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">
              1. Destino do Envio:
            </label>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- Simulação Local -->
              <div
                @click="form.modo_envio = 'SIMULADO'"
                :class="[
                  form.modo_envio === 'SIMULADO' 
                    ? 'border-indigo-600 bg-indigo-50/40 ring-2 ring-indigo-500/20 shadow-sm' 
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                ]"
                class="p-4 border rounded-xl cursor-pointer transition-all flex flex-col justify-between"
              >
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <span class="flex items-center gap-2 font-bold text-sm text-gray-900">
                      <ShieldCheckIcon class="h-5 w-5 text-indigo-600" />
                      Simulação Local
                    </span>
                    <input 
                      type="radio" 
                      name="modo_envio" 
                      value="SIMULADO" 
                      v-model="form.modo_envio" 
                      class="text-indigo-600 focus:ring-indigo-500" 
                    />
                  </div>
                  <p class="text-xs text-gray-600 leading-relaxed">
                    Valida a criação do Adaptive Card e histórico sem enviar mensagens ao canal real nem emitir notificações sonoras.
                  </p>
                </div>
                <div class="mt-3 text-[11px] font-semibold text-indigo-700 bg-indigo-100/70 px-2 py-0.5 rounded w-fit">
                  Recomendado para Testes
                </div>
              </div>

              <!-- Disparo Real Teams -->
              <div
                @click="form.modo_envio = 'REAL'"
                :class="[
                  form.modo_envio === 'REAL' 
                    ? 'border-emerald-600 bg-emerald-50/40 ring-2 ring-emerald-500/20 shadow-sm' 
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                ]"
                class="p-4 border rounded-xl cursor-pointer transition-all flex flex-col justify-between"
              >
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <span class="flex items-center gap-2 font-bold text-sm text-gray-900">
                      <SignalIcon class="h-5 w-5 text-emerald-600" />
                      Disparo Real no Teams
                    </span>
                    <input 
                      type="radio" 
                      name="modo_envio" 
                      value="REAL" 
                      v-model="form.modo_envio" 
                      class="text-emerald-600 focus:ring-emerald-500" 
                    />
                  </div>
                  <p class="text-xs text-gray-600 leading-relaxed">
                    Despacha efetivamente o cartão para o Webhook do Teams, gerando menção e notificação móvel no celular da equipe.
                  </p>
                </div>
                <div class="mt-3 text-[11px] font-semibold text-emerald-800 bg-emerald-100/70 px-2 py-0.5 rounded w-fit">
                  Canal Hospitalar Real
                </div>
              </div>
            </div>
          </div>

          <!-- 2. Formato do Alerta: Completo vs Simples -->
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">
              2. Formato do Alerta:
            </label>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- Modo Completo -->
              <div
                @click="form.modo = 'COMPLETO'"
                :class="[
                  form.modo === 'COMPLETO' 
                    ? 'border-primary-600 bg-primary-50/40 ring-2 ring-primary-500/20 shadow-sm' 
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                ]"
                class="p-4 border rounded-xl cursor-pointer transition-all flex flex-col justify-between"
              >
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <span class="flex items-center gap-2 font-bold text-sm text-gray-900">
                      <DocumentTextIcon class="h-5 w-5 text-primary-600" />
                      Modo Completo
                    </span>
                    <input 
                      type="radio" 
                      name="modo" 
                      value="COMPLETO" 
                      v-model="form.modo" 
                      class="text-primary-600 focus:ring-primary-500" 
                    />
                  </div>
                  <p class="text-xs text-gray-600 leading-relaxed">
                    Exibe a identificação nominal do paciente, prontuário, causa da morte e protocolo de Morte Encefálica.
                  </p>
                </div>
                <div class="mt-3 text-[11px] font-semibold text-primary-700 bg-primary-100/60 px-2 py-0.5 rounded w-fit">
                  Padrão CIHDOTT
                </div>
              </div>

              <!-- Modo Alerta Simples -->
              <div
                @click="form.modo = 'ALERTA_SIMPLES'"
                :class="[
                  form.modo === 'ALERTA_SIMPLES' 
                    ? 'border-amber-600 bg-amber-50/40 ring-2 ring-amber-500/20 shadow-sm' 
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                ]"
                class="p-4 border rounded-xl cursor-pointer transition-all flex flex-col justify-between"
              >
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <span class="flex items-center gap-2 font-bold text-sm text-gray-900">
                      <ExclamationTriangleIcon class="h-5 w-5 text-amber-600" />
                      Modo Alerta Simples
                    </span>
                    <input 
                      type="radio" 
                      name="modo" 
                      value="ALERTA_SIMPLES" 
                      v-model="form.modo" 
                      class="text-amber-600 focus:ring-amber-500" 
                    />
                  </div>
                  <p class="text-xs text-gray-600 leading-relaxed">
                    Omite os dados de identificação do paciente, notificando apenas o setor, leito e horário para busca imediata.
                  </p>
                </div>
                <div class="mt-3 text-[11px] font-semibold text-amber-800 bg-amber-100/60 px-2 py-0.5 rounded w-fit">
                  Proteção de Dados / LGPD
                </div>
              </div>
            </div>
          </div>

          <!-- 3. Destinatários Notificados (@menções) -->
          <div class="bg-blue-50/50 p-4 rounded-xl border border-blue-200 space-y-3">
            <div class="flex items-center justify-between">
              <label class="block text-sm font-bold text-gray-800 flex items-center gap-2">
                <UserCircleIcon class="h-5 w-5 text-blue-600" />
                3. Quem Deve Ser Marcado no Cartão (@mention):
              </label>
              <button 
                type="button" 
                @click="abrirGerenciarEquipe" 
                class="text-xs text-blue-700 hover:underline font-semibold"
              >
                Configurar Equipe
              </button>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <label class="flex items-center gap-2 p-2.5 bg-white border rounded-lg cursor-pointer hover:bg-gray-50 transition" :class="{'ring-2 ring-blue-500 border-blue-500': form.tipo_mencao === 'OPERADOR'}">
                <input type="radio" value="OPERADOR" v-model="form.tipo_mencao" class="text-blue-600" />
                <div>
                  <p class="font-bold text-gray-900">Apenas Meu Usuário (Você)</p>
                  <p class="text-[11px] text-gray-500">Menciona @{{ currentUserName }}</p>
                </div>
              </label>

              <label class="flex items-center gap-2 p-2.5 bg-white border rounded-lg cursor-pointer hover:bg-gray-50 transition" :class="{'ring-2 ring-blue-500 border-blue-500': form.tipo_mencao === 'SELECIONADOS'}">
                <input type="radio" value="SELECIONADOS" v-model="form.tipo_mencao" class="text-blue-600" />
                <div>
                  <p class="font-bold text-gray-900">Selecionar Profissionais</p>
                  <p class="text-[11px] text-gray-500">Escolha quem da equipe marcar</p>
                </div>
              </label>

              <label class="flex items-center gap-2 p-2.5 bg-white border rounded-lg cursor-pointer hover:bg-gray-50 transition" :class="{'ring-2 ring-blue-500 border-blue-500': form.tipo_mencao === 'TODOS'}">
                <input type="radio" value="TODOS" v-model="form.tipo_mencao" class="text-blue-600" />
                <div>
                  <p class="font-bold text-gray-900">Toda a Equipe Ativa</p>
                  <p class="text-[11px] text-gray-500">Menciona todos os {{ activeDestinatarios.length }} ativos</p>
                </div>
              </label>

              <label class="flex items-center gap-2 p-2.5 bg-white border rounded-lg cursor-pointer hover:bg-gray-50 transition" :class="{'ring-2 ring-blue-500 border-blue-500': form.tipo_mencao === 'NENHUM'}">
                <input type="radio" value="NENHUM" v-model="form.tipo_mencao" class="text-blue-600" />
                <div>
                  <p class="font-bold text-gray-900">Sem Menções Nominais</p>
                  <p class="text-[11px] text-gray-500">Alerta Geral da CIHDOTT</p>
                </div>
              </label>
            </div>

            <!-- Lista de seleção específica se tipo_mencao === 'SELECIONADOS' -->
            <div v-if="form.tipo_mencao === 'SELECIONADOS'" class="pt-2 border-t border-blue-100">
              <p class="text-xs font-bold text-gray-700 mb-2">Marque os profissionais que devem receber @menção:</p>
              <div v-if="activeDestinatarios.length === 0" class="text-xs text-gray-500 italic p-2 bg-white rounded border">
                Nenhum profissional com status ATIVO cadastrado no momento.
              </div>
              <div v-else class="max-h-36 overflow-y-auto space-y-1 pr-1">
                <label 
                  v-for="dest in activeDestinatarios" 
                  :key="dest.id" 
                  class="flex items-center justify-between p-2 bg-white border rounded text-xs cursor-pointer hover:bg-gray-50"
                >
                  <div class="flex items-center gap-2">
                    <input 
                      type="checkbox" 
                      :value="dest.id" 
                      v-model="selectedDestinatariosIds" 
                      class="rounded text-blue-600 focus:ring-blue-500" 
                    />
                    <span class="font-semibold text-gray-800">{{ dest.nome }}</span>
                  </div>
                  <span class="text-[11px] text-gray-500">{{ dest.email_teams }}</span>
                </label>
              </div>
            </div>
          </div>

          <!-- 4. Formulário de Parâmetros -->
          <form @submit.prevent="dispararEnvio" class="space-y-4 bg-gray-50/70 p-5 rounded-xl border border-gray-200">
            <div class="flex items-center justify-between border-b pb-2">
              <h3 class="text-sm font-bold text-gray-800 flex items-center gap-2">
                <PencilSquareIcon class="h-4 w-4 text-gray-500" />
                4. Dados do Óbito / Parâmetros do Teste
              </h3>
              <button 
                type="button" 
                @click="restaurarPadroes" 
                class="text-xs text-primary-600 hover:text-primary-800 hover:underline"
              >
                Restaurar Padrões de Teste
              </button>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <!-- Setor / Leito -->
              <div class="sm:col-span-2">
                <label class="block text-xs font-semibold text-gray-700 uppercase mb-1">
                  Setor / Leito Hospitalar <span class="text-red-500">*</span>
                </label>
                <input 
                  v-model="form.setor_leito" 
                  type="text" 
                  required 
                  placeholder="Ex: UTI Coronariana - Leito 03"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                />
              </div>

              <!-- Data / Hora do Óbito -->
              <div class="sm:col-span-2">
                <label class="block text-xs font-semibold text-gray-700 uppercase mb-1">
                  Data e Hora do Óbito
                </label>
                <input 
                  v-model="form.data_hora_obito" 
                  type="datetime-local" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                />
              </div>

              <!-- Campos específicos do Modo Completo -->
              <template v-if="form.modo === 'COMPLETO'">
                <div class="sm:col-span-2">
                  <label class="block text-xs font-semibold text-gray-700 uppercase mb-1">
                    Nome Completo do Paciente
                  </label>
                  <input 
                    v-model="form.nome_paciente" 
                    type="text" 
                    placeholder="Ex: Paciente Simulado de Teste (CIHDOTT)"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label class="block text-xs font-semibold text-gray-700 uppercase mb-1">
                    Prontuário
                  </label>
                  <input 
                    v-model="form.prontuario" 
                    type="text" 
                    placeholder="Ex: TESTE-12345"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label class="block text-xs font-semibold text-gray-700 uppercase mb-1">
                    Idade (Anos)
                  </label>
                  <input 
                    v-model.number="form.idade" 
                    type="number" 
                    min="0" 
                    max="125"
                    placeholder="Ex: 52"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label class="block text-xs font-semibold text-gray-700 uppercase mb-1">
                    Sexo
                  </label>
                  <select 
                    v-model="form.sexo" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  >
                    <option value="M">Masculino (M)</option>
                    <option value="F">Feminino (F)</option>
                    <option value="O">Outro / Não informado</option>
                  </select>
                </div>

                <div>
                  <label class="block text-xs font-semibold text-gray-700 uppercase mb-1">
                    Causa do Óbito
                  </label>
                  <input 
                    v-model="form.causa_morte" 
                    type="text" 
                    placeholder="Ex: Choque Cardiogênico"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  />
                </div>

                <div class="sm:col-span-2 pt-1">
                  <label class="inline-flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      v-model="form.protocolo_me" 
                      class="rounded text-primary-600 focus:ring-primary-500 h-4 w-4"
                    />
                    <span class="text-xs font-bold text-gray-800">
                      Sinalizar Protocolo de Morte Encefálica (ME) Aberto
                    </span>
                  </label>
                </div>
              </template>
            </div>

            <!-- Botão de Ação -->
            <div class="pt-4 border-t flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <span class="text-xs text-gray-500">
                <template v-if="form.modo_envio === 'SIMULADO'">
                  <span class="font-bold text-indigo-700">Modo Simulação:</span> Registro interno seguro sem envio ao Teams.
                </template>
                <template v-else>
                  <span class="font-bold text-emerald-700">Modo Real:</span> O alerta será enviado ao canal Teams com as menções selecionadas.
                </template>
              </span>
              <Button 
                type="submit" 
                :variant="form.modo_envio === 'SIMULADO' ? 'secondary' : 'primary'"
                :loading="isSending"
                :disabled="isSending || !form.setor_leito.trim()"
              >
                <template #icon>
                  <PaperAirplaneIcon class="h-5 w-5" />
                </template>
                {{ isSending ? 'Processando...' : (form.modo_envio === 'SIMULADO' ? 'Simular Disparo Local' : 'Enviar Alerta ao Teams') }}
              </Button>
            </div>
          </form>
        </div>

        <!-- Coluna da Direita: Card Preview do Teams e Destinatários (5 colunas) -->
        <div class="lg:col-span-5 space-y-6">
          <!-- Prévia Visual do Adaptive Card (Teams) -->
          <div class="border border-gray-200 rounded-xl overflow-hidden shadow-sm bg-white">
            <div class="bg-gray-100 px-4 py-3 border-b flex items-center justify-between">
              <span class="text-xs font-bold text-gray-700 flex items-center gap-1.5 uppercase tracking-wider">
                <EyeIcon class="h-4 w-4 text-gray-500" />
                Prévia Interativa (Microsoft Teams)
              </span>
              <span class="text-[10px] bg-gray-200 text-gray-700 font-semibold px-2 py-0.5 rounded">
                Adaptive Card v1.5
              </span>
            </div>

            <!-- Moldura do Teams -->
            <div class="p-4 bg-[#F5F5F5]">
              <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 space-y-3">
                <!-- Cabeçalho do Card Teams -->
                <div class="border-l-4 border-[#C41C1C] pl-3 py-0.5">
                  <div class="flex items-center gap-1 text-[#C41C1C] font-extrabold text-sm uppercase">
                    <span>🚨</span>
                    <span>NOTIFICAÇÃO DE ÓBITO - BUSCA ATIVA CIHDOTT</span>
                  </div>
                  <p class="text-xs text-gray-500 mt-0.5">
                    Hospital das Clínicas da UFPE / EBSERH &bull; e-DOT Alerta
                  </p>
                </div>

                <!-- Destaque de Protocolo ME se marcado -->
                <div v-if="form.modo === 'COMPLETO' && form.protocolo_me" class="p-2 bg-red-50 border border-red-200 text-red-800 rounded text-xs font-bold flex items-center gap-1.5">
                  <span>⚠️</span>
                  <span>PROTOCOLO DE MORTE ENCEFÁLICA (ME) SINALIZADO</span>
                </div>

                <!-- Tabela de Propriedades do Card -->
                <div class="text-xs space-y-1.5 pt-1">
                  <div class="flex border-b border-gray-100 pb-1">
                    <span class="w-28 font-bold text-gray-500">Setor / Leito:</span>
                    <span class="flex-1 font-semibold text-gray-900">{{ form.setor_leito || 'Não informado' }}</span>
                  </div>
                  <div class="flex border-b border-gray-100 pb-1">
                    <span class="w-28 font-bold text-gray-500">Data / Horário:</span>
                    <span class="flex-1 text-gray-800">{{ formatarDataPreview(form.data_hora_obito) }}</span>
                  </div>

                  <template v-if="form.modo === 'COMPLETO'">
                    <div class="flex border-b border-gray-100 pb-1">
                      <span class="w-28 font-bold text-gray-500">Paciente:</span>
                      <span class="flex-1 font-semibold text-gray-900">{{ form.nome_paciente || 'Paciente Simulado' }}</span>
                    </div>
                    <div class="flex border-b border-gray-100 pb-1">
                      <span class="w-28 font-bold text-gray-500">Prontuário:</span>
                      <span class="flex-1 text-gray-800">{{ form.prontuario || 'Não informado' }}</span>
                    </div>
                    <div class="flex border-b border-gray-100 pb-1">
                      <span class="w-28 font-bold text-gray-500">Idade / Sexo:</span>
                      <span class="flex-1 text-gray-800">{{ form.idade ? `${form.idade} anos` : 'Não informado' }} ({{ form.sexo || 'N/I' }})</span>
                    </div>
                    <div class="flex border-b border-gray-100 pb-1">
                      <span class="w-28 font-bold text-gray-500">Causa Morte:</span>
                      <span class="flex-1 text-gray-800">{{ form.causa_morte || 'Não informada' }}</span>
                    </div>
                  </template>
                  <template v-else>
                    <div class="p-2 bg-amber-50 rounded text-[11px] text-amber-800 italic">
                      Identificação do paciente ocultada neste modo para segurança operacional e conformidade com a LGPD.
                    </div>
                  </template>
                </div>

                <!-- Menções @ no Rodapé do Card -->
                <div class="pt-2 border-t border-gray-200">
                  <p class="text-[11px] text-gray-500 font-bold mb-1">Destinatários Mencionados Neste Envio:</p>
                  <div class="flex flex-wrap gap-1">
                    <span 
                      v-for="nome in mencoesPreview" 
                      :key="nome" 
                      class="text-[11px] text-blue-700 bg-blue-50 border border-blue-200 px-1.5 py-0.5 rounded font-medium"
                    >
                      @{{ nome }}
                    </span>
                    <span v-if="mencoesPreview.length === 0" class="text-[11px] text-gray-400 italic">
                      Nenhum profissional mencionado nominalmente (Alerta Geral CIHDOTT)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Destinatários Ativos da Equipe -->
          <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-3">
            <div class="flex items-center justify-between border-b pb-2">
              <h3 class="text-sm font-bold text-gray-800 flex items-center gap-1.5">
                <UserGroupIcon class="h-4 w-4 text-gray-600" />
                Equipe Teams Cadastrada ({{ activeDestinatarios.length }} ativos)
              </h3>
              <button 
                type="button"
                @click="abrirGerenciarEquipe" 
                class="text-xs text-primary-600 hover:underline font-semibold"
              >
                Gerenciar Equipe
              </button>
            </div>

            <div v-if="loadingDestinatarios" class="text-xs text-gray-500 py-2 text-center">
              Carregando lista de profissionais...
            </div>
            <div v-else-if="activeDestinatarios.length === 0" class="text-xs text-amber-700 bg-amber-50 p-3 rounded-lg border border-amber-200">
              Nenhum profissional com status ATIVO encontrado. Clique em "Gerenciar Equipe" para adicionar ou ativar membros.
            </div>
            <ul v-else class="divide-y divide-gray-100 text-xs max-h-48 overflow-y-auto pr-1">
              <li v-for="dest in activeDestinatarios" :key="dest.id" class="py-1.5 flex items-center justify-between">
                <div>
                  <p class="font-bold text-gray-800">{{ dest.nome }}</p>
                  <p class="text-[11px] text-gray-500">{{ dest.email_teams }} &bull; {{ dest.cargo_setor || 'CIHDOTT' }}</p>
                </div>
                <span class="text-[10px] bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded">
                  Ativo
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Histórico de Disparos da Sessão -->
      <div class="mt-8 border-t pt-6 space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="text-base font-bold text-paper-text flex items-center gap-2">
            <ClockIcon class="h-5 w-5 text-gray-500" />
            Histórico Recente de Notificações
          </h2>
          <button 
            @click="carregarHistorico" 
            class="text-xs text-primary-600 hover:text-primary-800 font-semibold flex items-center gap-1"
          >
            <ArrowPathIcon class="h-3.5 w-3.5" :class="{ 'animate-spin': loadingHistorico }" />
            Atualizar Lista
          </button>
        </div>

        <div class="overflow-x-auto bg-white border border-gray-200 rounded-xl">
          <table class="w-full text-left text-xs text-gray-600">
            <thead class="bg-gray-50 text-[11px] uppercase font-bold text-gray-500 border-b">
              <tr>
                <th class="py-2.5 px-3">ID Evento</th>
                <th class="py-2.5 px-3">Modo</th>
                <th class="py-2.5 px-3">Setor / Leito</th>
                <th class="py-2.5 px-3">Paciente</th>
                <th class="py-2.5 px-3 text-center">Status</th>
                <th class="py-2.5 px-3 text-center">Tentativas</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="item in historico" :key="item.id" class="hover:bg-gray-50">
                <td class="py-2.5 px-3 font-mono font-bold text-gray-800">{{ item.id_evento_origem }}</td>
                <td class="py-2.5 px-3">
                  <span 
                    :class="item.modo_apresentacao === 'COMPLETO' ? 'bg-primary-100 text-primary-800' : 'bg-amber-100 text-amber-800'"
                    class="px-2 py-0.5 rounded font-bold text-[10px]"
                  >
                    {{ item.modo_apresentacao }}
                  </span>
                </td>
                <td class="py-2.5 px-3 font-medium">{{ item.setor_leito || '-' }}</td>
                <td class="py-2.5 px-3">{{ item.nome_paciente || 'Ocultado / Simples' }}</td>
                <td class="py-2.5 px-3 text-center">
                  <span :class="getStatusBadgeClass(item.status_envio)" class="px-2 py-0.5 rounded font-bold text-[10px]">
                    {{ item.status_envio }}
                  </span>
                </td>
                <td class="py-2.5 px-3 text-center font-bold">{{ item.tentativas_envio }}</td>
              </tr>
              <tr v-if="historico.length === 0">
                <td colspan="6" class="py-6 text-center text-gray-400">
                  Nenhum envio registrado até o momento.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </Card>

    <!-- Modal: Gerenciar Equipe de Destinatários do Teams -->
    <Modal :show="showGerenciarModal" @close="showGerenciarModal = false">
      <template #header>
        <span class="flex items-center gap-2">
          <UserGroupIcon class="h-6 w-6 text-primary-600" />
          Equipe de Destinatários do Teams (CIHDOTT)
        </span>
      </template>

      <div class="space-y-4">
        <p class="text-xs text-gray-500">
          Gerencie os profissionais que recebem os alertas hospitalares no Microsoft Teams. Usuários inativados não receberão notificações.
        </p>

        <!-- Formulário para Incluir Novo Profissional -->
        <div class="p-3 bg-gray-50 border rounded-xl space-y-3">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-bold text-gray-800 uppercase flex items-center gap-1">
              <UserPlusIcon class="h-4 w-4 text-primary-600" />
              Adicionar Novo Destinatário
            </h4>
            <button 
              type="button" 
              @click="preencherComMeuUsuario" 
              class="text-[11px] text-primary-600 hover:underline font-semibold"
            >
              Usar Meus Dados
            </button>
          </div>

          <form @submit.prevent="salvarNovoDestinatario" class="space-y-2">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <div>
                <label class="block text-[11px] font-semibold text-gray-600 mb-0.5">Nome Completo *</label>
                <input 
                  v-model="novoDest.nome" 
                  type="text" 
                  required 
                  placeholder="Ex: Dra. Ana Paula"
                  class="w-full px-2.5 py-1.5 border rounded text-xs focus:ring-1 focus:ring-primary-500 focus:outline-none"
                />
              </div>
              <div>
                <label class="block text-[11px] font-semibold text-gray-600 mb-0.5">E-mail Teams (UPN) *</label>
                <input 
                  v-model="novoDest.email_teams" 
                  type="email" 
                  required 
                  placeholder="Ex: ana.paula@ebserh.gov.br"
                  class="w-full px-2.5 py-1.5 border rounded text-xs focus:ring-1 focus:ring-primary-500 focus:outline-none"
                />
              </div>
              <div class="sm:col-span-2">
                <label class="block text-[11px] font-semibold text-gray-600 mb-0.5">Cargo / Setor</label>
                <input 
                  v-model="novoDest.cargo_setor" 
                  type="text" 
                  placeholder="Ex: Médico Plantonista CIHDOTT"
                  class="w-full px-2.5 py-1.5 border rounded text-xs focus:ring-1 focus:ring-primary-500 focus:outline-none"
                />
              </div>
            </div>

            <div class="flex justify-end pt-1">
              <Button type="submit" variant="primary" size="sm" :loading="isSavingDest">
                Adicionar Profissional
              </Button>
            </div>
          </form>
        </div>

        <!-- Lista de Todos os Profissionais Cadastrados -->
        <div>
          <h4 class="text-xs font-bold text-gray-800 uppercase mb-2">Profissionais Cadastrados ({{ allDestinatarios.length }})</h4>
          <div v-if="loadingAllDest" class="text-center py-4 text-xs text-gray-400">
            Carregando lista completa...
          </div>
          <div v-else-if="allDestinatarios.length === 0" class="text-center py-4 text-xs text-gray-400">
            Nenhum profissional cadastrado.
          </div>
          <ul v-else class="divide-y divide-gray-200 border rounded-xl overflow-hidden max-h-56 overflow-y-auto">
            <li 
              v-for="d in allDestinatarios" 
              :key="d.id" 
              class="p-2.5 flex items-center justify-between text-xs hover:bg-gray-50"
            >
              <div>
                <div class="flex items-center gap-1.5">
                  <span class="font-bold text-gray-900">{{ d.nome }}</span>
                  <span 
                    :class="d.ativo ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-600'" 
                    class="text-[10px] px-1.5 py-0.2 rounded font-semibold"
                  >
                    {{ d.ativo ? 'Ativo' : 'Inativo' }}
                  </span>
                </div>
                <p class="text-[11px] text-gray-500">{{ d.email_teams }} &bull; {{ d.cargo_setor || 'CIHDOTT' }}</p>
              </div>
              <div class="flex items-center gap-1.5">
                <button 
                  @click="alternarStatusDestinatario(d)" 
                  :class="d.ativo ? 'text-amber-600 hover:bg-amber-50 border-amber-200' : 'text-emerald-600 hover:bg-emerald-50 border-emerald-200'"
                  class="px-2 py-1 text-[11px] font-semibold border rounded"
                >
                  {{ d.ativo ? 'Inativar' : 'Ativar' }}
                </button>
                <button 
                  @click="excluirDestinatario(d.id)" 
                  class="px-2 py-1 text-[11px] font-semibold text-red-600 hover:bg-red-50 border border-red-200 rounded"
                >
                  Excluir
                </button>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <template #footer>
        <Button variant="secondary" @click="showGerenciarModal = false">Fechar</Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import Modal from '../components/Modal.vue';
import api from '../services/api';
import { useAuthStore } from '../stores/auth';
import {
  BellAlertIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  PencilSquareIcon,
  PaperAirplaneIcon,
  UserGroupIcon,
  ClockIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XMarkIcon,
  UserCircleIcon,
  ShieldCheckIcon,
  SignalIcon,
  UserPlusIcon
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();

interface Destinatario {
  id: number;
  nome: string;
  email_teams: string;
  cargo_setor?: string;
  ativo: boolean;
}

interface NotificacaoItem {
  id: number;
  id_evento_origem: string;
  fonte_origem: string;
  nome_paciente?: string;
  prontuario?: string;
  setor_leito?: string;
  modo_apresentacao: string;
  status_envio: string;
  tentativas_envio: number;
}

const form = ref({
  modo_envio: 'SIMULADO' as 'SIMULADO' | 'REAL',
  modo: 'COMPLETO' as 'COMPLETO' | 'ALERTA_SIMPLES',
  tipo_mencao: 'OPERADOR' as 'OPERADOR' | 'SELECIONADOS' | 'TODOS' | 'NENHUM',
  setor_leito: 'UTI Geral - Leito 04 (Simulação)',
  data_hora_obito: new Date().toISOString().slice(0, 16),
  nome_paciente: 'Paciente Simulado de Teste (CIHDOTT)',
  prontuario: 'TESTE-12345',
  idade: 52,
  sexo: 'M',
  causa_morte: 'Choque Cardiogênico (Simulação)',
  protocolo_me: false,
});

const isSending = ref(false);
const activeDestinatarios = ref<Destinatario[]>([]);
const allDestinatarios = ref<Destinatario[]>([]);
const selectedDestinatariosIds = ref<number[]>([]);
const loadingDestinatarios = ref(false);
const loadingAllDest = ref(false);
const historico = ref<NotificacaoItem[]>([]);
const loadingHistorico = ref(false);

// Modal de Gerenciamento
const showGerenciarModal = ref(false);
const isSavingDest = ref(false);
const novoDest = ref({
  nome: '',
  email_teams: '',
  cargo_setor: 'CIHDOTT / HC-UFPE'
});

const alertMessage = ref('');
const alertTitle = ref('');
const alertType = ref<'success' | 'error' | 'info'>('info');

const currentUserName = computed(() => {
  return authStore.user?.displayName?.[0] || authStore.user?.username || 'Usuário Atual';
});

const currentUserEmail = computed(() => {
  return authStore.user?.email?.[0] || `${authStore.user?.username || 'usuario'}@ebserh.gov.br`;
});

const currentUserDept = computed(() => {
  return authStore.user?.department?.[0] || 'CIHDOTT / HC-UFPE';
});

const mencoesPreview = computed(() => {
  if (form.value.tipo_mencao === 'OPERADOR') {
    return [currentUserName.value];
  }
  if (form.value.tipo_mencao === 'NENHUM') {
    return [];
  }
  if (form.value.tipo_mencao === 'SELECIONADOS') {
    return activeDestinatarios.value
      .filter(d => selectedDestinatariosIds.value.includes(d.id))
      .map(d => d.nome);
  }
  // 'TODOS'
  return activeDestinatarios.value.map(d => d.nome);
});

const teamsStatusBadge = computed(() => {
  if (form.value.modo_envio === 'SIMULADO') {
    return {
      text: 'Modo Seguro: Simulação Local Ativa',
      class: 'bg-indigo-50 text-indigo-800 border-indigo-200',
      dot: 'bg-indigo-500'
    };
  }
  return {
    text: 'Disparo Real Conectado ao Teams',
    class: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    dot: 'bg-emerald-500'
  };
});

const alertClasses = computed(() => {
  switch (alertType.value) {
    case 'success':
      return 'bg-emerald-50 border-emerald-200 text-emerald-800';
    case 'error':
      return 'bg-red-50 border-red-200 text-red-800';
    default:
      return 'bg-blue-50 border-blue-200 text-blue-800';
  }
});

const alertIcon = computed(() => {
  switch (alertType.value) {
    case 'success':
      return CheckCircleIcon;
    case 'error':
      return ExclamationTriangleIcon;
    default:
      return BellAlertIcon;
  }
});

const formatarDataPreview = (isoString?: string) => {
  if (!isoString) return new Date().toLocaleString('pt-BR');
  try {
    const d = new Date(isoString);
    return isNaN(d.getTime()) ? isoString : d.toLocaleString('pt-BR');
  } catch {
    return isoString;
  }
};

const restaurarPadroes = () => {
  form.value = {
    modo_envio: form.value.modo_envio,
    tipo_mencao: 'OPERADOR',
    modo: form.value.modo,
    setor_leito: 'UTI Coronariana - Leito 02 (Simulação)',
    data_hora_obito: new Date().toISOString().slice(0, 16),
    nome_paciente: 'Paciente Simulado de Teste (CIHDOTT)',
    prontuario: 'TESTE-12345',
    idade: 52,
    sexo: 'M',
    causa_morte: 'Choque Cardiogênico (Teste de Notificação)',
    protocolo_me: false,
  };
};

const carregarDestinatarios = async () => {
  loadingDestinatarios.value = true;
  try {
    const res = await api.get<Destinatario[]>('/api/notificacoes/destinatarios?apenas_ativos=true');
    activeDestinatarios.value = res.data;
    // Seleciona todos os ativos por padrão para o caso de o usuário alternar para SELECIONADOS
    selectedDestinatariosIds.value = res.data.map(d => d.id);
  } catch (error) {
    console.error('Erro ao carregar destinatários ativos:', error);
  } finally {
    loadingDestinatarios.value = false;
  }
};

const carregarTodosDestinatarios = async () => {
  loadingAllDest.value = true;
  try {
    const res = await api.get<Destinatario[]>('/api/notificacoes/destinatarios?apenas_ativos=false');
    allDestinatarios.value = res.data;
  } catch (error) {
    console.error('Erro ao carregar lista geral de destinatários:', error);
  } finally {
    loadingAllDest.value = false;
  }
};

const abrirGerenciarEquipe = async () => {
  showGerenciarModal.value = true;
  await carregarTodosDestinatarios();
};

const preencherComMeuUsuario = () => {
  novoDest.value = {
    nome: currentUserName.value,
    email_teams: currentUserEmail.value,
    cargo_setor: currentUserDept.value
  };
};

const salvarNovoDestinatario = async () => {
  if (!novoDest.value.nome.trim() || !novoDest.value.email_teams.trim()) return;
  isSavingDest.value = true;
  try {
    await api.post('/api/notificacoes/destinatarios', novoDest.value);
    novoDest.value = { nome: '', email_teams: '', cargo_setor: 'CIHDOTT / HC-UFPE' };
    await carregarTodosDestinatarios();
    await carregarDestinatarios();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Erro ao cadastrar destinatário.');
  } finally {
    isSavingDest.value = false;
  }
};

const alternarStatusDestinatario = async (dest: Destinatario) => {
  try {
    await api.put(`/api/notificacoes/destinatarios/${dest.id}`, { ativo: !dest.ativo });
    await carregarTodosDestinatarios();
    await carregarDestinatarios();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Erro ao alterar status.');
  }
};

const excluirDestinatario = async (id: number) => {
  if (!confirm('Deseja realmente remover este destinatário da equipe de alertas?')) return;
  try {
    await api.delete(`/api/notificacoes/destinatarios/${id}`);
    await carregarTodosDestinatarios();
    await carregarDestinatarios();
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Erro ao excluir destinatário.');
  }
};

const carregarHistorico = async () => {
  loadingHistorico.value = true;
  try {
    const res = await api.get<NotificacaoItem[]>('/api/notificacoes/obitos?limit=20');
    historico.value = res.data;
  } catch (error) {
    console.error('Erro ao carregar histórico:', error);
  } finally {
    loadingHistorico.value = false;
  }
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

const dispararEnvio = async () => {
  if (!form.value.setor_leito.trim()) return;

  isSending.value = true;
  alertMessage.value = '';

  try {
    const isSimulacao = form.value.modo_envio === 'SIMULADO';

    let destinatariosIdsParam: number[] | null = null;
    let notificarOperadorParam = false;

    if (form.value.tipo_mencao === 'OPERADOR') {
      notificarOperadorParam = true;
    } else if (form.value.tipo_mencao === 'NENHUM') {
      destinatariosIdsParam = [];
    } else if (form.value.tipo_mencao === 'SELECIONADOS') {
      destinatariosIdsParam = selectedDestinatariosIds.value;
    } else {
      // 'TODOS'
      destinatariosIdsParam = null;
    }

    const payload = {
      modo: form.value.modo,
      apenas_simular: isSimulacao,
      notificar_apenas_operador: notificarOperadorParam,
      destinatarios_ids: destinatariosIdsParam,
      dados_obito: {
        setor_leito: form.value.setor_leito,
        data_hora_obito: form.value.data_hora_obito,
        nome_paciente: form.value.modo === 'COMPLETO' ? form.value.nome_paciente : null,
        prontuario: form.value.modo === 'COMPLETO' ? form.value.prontuario : null,
        idade: form.value.modo === 'COMPLETO' ? form.value.idade : null,
        sexo: form.value.modo === 'COMPLETO' ? form.value.sexo : null,
        causa_morte: form.value.modo === 'COMPLETO' ? form.value.causa_morte : null,
        protocolo_me: form.value.modo === 'COMPLETO' ? form.value.protocolo_me : false,
      }
    };

    const res = await api.post('/api/notificacoes/teste-teams', payload);
    const data = res.data;

    alertType.value = 'success';
    if (data.status_envio === 'SIMULADO') {
      alertTitle.value = 'Simulação Concluída com Sucesso!';
      alertMessage.value = `Cartão em ${data.modo_apresentacao} gerado e validado internamente (ID: ${data.id_evento_origem}). Nenhuma mensagem disparada no Teams.`;
    } else {
      alertTitle.value = 'Notificação Despachada com Sucesso!';
      alertMessage.value = `Alerta em ${data.modo_apresentacao} despachado com sucesso ao Microsoft Teams (Status: ${data.status_envio}).`;
    }

    // Atualiza a tabela de histórico
    await carregarHistorico();
  } catch (err: any) {
    console.error('Falha no despacho da notificação:', err);
    alertType.value = 'error';
    alertTitle.value = 'Falha no Despacho da Notificação';
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') {
      alertMessage.value = detail;
    } else if (Array.isArray(detail)) {
      alertMessage.value = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
    } else if (err.message) {
      alertMessage.value = `Erro de comunicação: ${err.message} (${err.response?.status || 'Sem status'})`;
    } else {
      alertMessage.value = 'Ocorreu um erro ao comunicar com a API do e-DOT.';
    }
  } finally {
    isSending.value = false;
  }
};

onMounted(() => {
  carregarDestinatarios();
  carregarHistorico();
});
</script>
