<script setup lang="ts">
    import { useSimulation } from '../composables/useSimulation'
    import { useComparison } from '../composables/useComparison'
    import { ref, watch, onMounted, onUnmounted } from 'vue'
    import type { SimulationRequest, ComparisonRequest } from '../types/simulation'
    import { formatCurrency, formatDate } from '../adapters/formatters'

    // Composable para simulação única
    const { runSimulation, result, error, isLoading } = useSimulation();
    
    // Composable para comparação dupla (SAC x Price)
    const { runComparison, result: compareResult, error: compareError, isLoading: isComparing } = useComparison();

    const principal = ref<number>(0);
    const system = ref<'SAC' | 'PRICE'>('PRICE');
    const annual_interest_rate = ref<number>(0);
    const term_months = ref<number>(0);
    const payment_day = ref<number>(5);
    const start_date = ref<string | null>(null);

    // Controle de abertura dos modais
    const isModalOpen = ref(false);
    const isCompareModalOpen = ref(false);

    // Aba de tabela selecionada no resultado da comparação (SAC ou PRICE)
    const activeCompareTab = ref<'SAC' | 'PRICE'>('SAC');

    function openModal() {
        isModalOpen.value = true;
    }

    function closeModal() {
        isModalOpen.value = false;
    }

    function openCompareModal() {
        isCompareModalOpen.value = true;
    }

    function closeCompareModal() {
        isCompareModalOpen.value = false;
    }

    // Fecha qualquer modal aberto com a tecla Esc
    function onKeydown(event: KeyboardEvent) {
        if (event.key === 'Escape') {
            if (isModalOpen.value) closeModal();
            if (isCompareModalOpen.value) closeCompareModal();
        }
    }

    onMounted(() => window.addEventListener('keydown', onKeydown));
    onUnmounted(() => window.removeEventListener('keydown', onKeydown));

    // Bloqueia o scroll da página enquanto qualquer modal estiver aberto
    watch([isModalOpen, isCompareModalOpen], ([open1, open2]) => {
        document.body.style.overflow = (open1 || open2) ? 'hidden' : '';
    });
    
    // Submissão da simulação individual
    async function onSubmit() {
        const request: SimulationRequest = {
            principal: principal.value,
            system: system.value,
            annual_interest_rate: annual_interest_rate.value / 100,
            term_months: term_months.value,
            payment_day: payment_day.value,
            start_date: start_date.value || null,
        }
        await runSimulation(request)
        if (!error.value) {
            closeModal();
        }
    }

    // Submissão da comparação SAC x Price
    async function onCompareSubmit() {
        const request: ComparisonRequest = {
            principal: principal.value,
            annual_interest_rate: annual_interest_rate.value / 100,
            term_months: term_months.value,
            payment_day: payment_day.value,
            start_date: start_date.value || null,
        }
        await runComparison(request)
        if (!compareError.value) {
            closeCompareModal();
        }
    }
</script>

<template>
    <main>
        <!-- ============ HERO ============ -->
        <section class="hero">
            <div class="hero-arc" aria-hidden="true"></div>

            <div class="hero-content">
                <h1>Planeje seu <span class="text-gold">financiamento</span><br />com clareza total</h1>
                <p class="hero-subtitle">
                    Simule SAC e Price, compare custos totais e descubra o melhor caminho para quitar seu imóvel.
                </p>

                <div class="pill-list">
                    <button type="button" class="pill pill--active" id="pill-simulate" @click="openModal">
                        <span class="pill-title">Simular empréstimo</span>
                        <span class="pill-caption">SAC &amp; Price</span>
                    </button>

                    <button type="button" class="pill pill--active" id="pill-compare" @click="openCompareModal">
                        <span class="pill-title">Comparar sistemas</span>
                        <span class="pill-caption">Lado a Lado</span>
                    </button>

                    <button type="button" class="pill" id="pill-extra" disabled>
                        <span class="pill-title">Amortização extra</span>
                        <span class="pill-caption">Em breve</span>
                    </button>
                </div>

                <button type="button" class="btn-cta" id="btn-start" @click="openModal">Começar agora</button>
            </div>
        </section>

        <!-- ============ MODAL 1: SIMULAÇÃO INDIVIDUAL ============ -->
        <Teleport to="body">
            <Transition name="modal">
                <div v-if="isModalOpen" class="modal-overlay" id="simulation-modal" role="dialog" aria-modal="true"
                    aria-labelledby="modal-title" @click.self="closeModal">
                    <div class="modal-box">
                        <h2 id="modal-title">Simular empréstimo</h2>
                        <p class="modal-subtitle">Preencha os dados do financiamento para calcular as parcelas.</p>
                        <form @submit.prevent="onSubmit">
                            <label for="principal">Valor do empréstimo (R$)</label>
                            <input v-model.number="principal" id="principal" type="number" step="0.01" min="0.01" required />

                            <label for="system">Sistema</label>
                            <select v-model="system" id="system">
                                <option value="SAC">SAC</option>
                                <option value="PRICE">PRICE</option>
                            </select>

                            <label for="annual_interest_rate">Taxa de juros anual (%)</label>
                            <input v-model.number="annual_interest_rate" id="annual_interest_rate" type="number" step="any" min="0.01" required />

                            <label for="term_months">Prazo em meses</label>
                            <input v-model.number="term_months" id="term_months" type="number" step="1" min="1" max="420" required />

                            <label for="payment_day">Dia do vencimento</label>
                            <input v-model.number="payment_day" id="payment_day" type="number" step="1" min="1" max="28" required />

                            <label for="start_date">Data de início</label>
                            <input v-model="start_date" id="start_date" type="date" />

                            <div class="modal-actions">
                                <button type="button" class="btn-secondary" @click="closeModal">Fechar</button>
                                <button type="submit" :disabled="isLoading">Calcular</button>
                            </div>
                        </form>
                    </div>
                </div>
            </Transition>
        </Teleport>

        <!-- ============ MODAL 2: COMPARAR SISTEMAS (SAC x PRICE) ============ -->
        <Teleport to="body">
            <Transition name="modal">
                <div v-if="isCompareModalOpen" class="modal-overlay" id="compare-modal" role="dialog" aria-modal="true"
                    aria-labelledby="compare-modal-title" @click.self="closeCompareModal">
                    <div class="modal-box">
                        <h2 id="compare-modal-title">Comparar SAC × Price</h2>
                        <p class="modal-subtitle">Calcularemos ambos os sistemas simultaneamente para você comparar economia e parcelas.</p>
                        <form @submit.prevent="onCompareSubmit">
                            <label for="compare-principal">Valor do empréstimo (R$)</label>
                            <input v-model.number="principal" id="compare-principal" type="number" step="0.01" min="0.01" required />

                            <label for="compare-annual_interest_rate">Taxa de juros anual (%)</label>
                            <input v-model.number="annual_interest_rate" id="compare-annual_interest_rate" type="number" step="any" min="0.01" required />

                            <label for="compare-term_months">Prazo em meses</label>
                            <input v-model.number="term_months" id="compare-term_months" type="number" step="1" min="1" max="420" required />

                            <label for="compare-payment_day">Dia do vencimento</label>
                            <input v-model.number="payment_day" id="compare-payment_day" type="number" step="1" min="1" max="28" required />

                            <label for="compare-start_date">Data de início</label>
                            <input v-model="start_date" id="compare-start_date" type="date" />

                            <div class="modal-actions">
                                <button type="button" class="btn-secondary" @click="closeCompareModal">Fechar</button>
                                <button type="submit" :disabled="isComparing">Comparar Sistemas</button>
                            </div>
                        </form>
                    </div>
                </div>
            </Transition>
        </Teleport>

        <!-- ============ SEÇÃO DE RESULTADOS ============ -->
        <section class="container results">
            <!-- Feedbacks de carregamento e erro -->
            <div v-if="isLoading || isComparing"><span class="spinner"></span> Processando cálculo...</div>
            <div v-if="error" class="alert-error">{{ error }}</div>
            <div v-if="compareError" class="alert-error">{{ compareError }}</div>

            <!-- 1. RESULTADO COMPARATIVO (SAC x PRICE) -->
            <div v-if="compareResult">
                <div class="compare-banner">
                    <h3>🏆 Resumo do Comparativo</h3>
                    <p>
                        <strong>Economia em Juros:</strong> Ao escolher o <strong>SAC</strong>, você economiza
                        <span class="text-gold"><strong>{{ formatCurrency(compareResult.interest_difference) }}</strong></span> em juros acumulados comparado à Tabela Price!
                    </p>
                    <p>
                        <strong>Alívio de Parcela Inicial:</strong> A primeira parcela da <strong>Price</strong> é
                        <span class="text-gold"><strong>{{ formatCurrency(compareResult.first_installment_difference) }}</strong></span> mais baixa que a do SAC.
                    </p>
                </div>

                <div class="compare-grid">
                    <!-- CARD SAC -->
                    <div class="compare-card winner">
                        <span class="badge">Menor Custo Total</span>
                        <h3>Sistema SAC</h3>
                        <p class="text-muted">Amortização constante, parcelas decrescentes ao longo do tempo.</p>
                        
                        <div class="metric-list">
                            <div class="metric-row">
                                <span class="metric-label">Total Pago</span>
                                <span class="metric-value text-gold">{{ formatCurrency(compareResult.sac.total_amount) }}</span>
                            </div>
                            <div class="metric-row">
                                <span class="metric-label">Juros Totais</span>
                                <span class="metric-value">{{ formatCurrency(compareResult.sac.total_interest_paid) }}</span>
                            </div>
                            <div class="metric-row">
                                <span class="metric-label">1ª Parcela</span>
                                <span class="metric-value">{{ formatCurrency(compareResult.sac.first_installment) }}</span>
                            </div>
                            <div class="metric-row">
                                <span class="metric-label">Última Parcela</span>
                                <span class="metric-value">{{ formatCurrency(compareResult.sac.last_installment) }}</span>
                            </div>
                        </div>
                    </div>

                    <!-- CARD PRICE -->
                    <div class="compare-card">
                        <span class="badge badge-blue">Parcela Inicial Menor</span>
                        <h3>Tabela Price</h3>
                        <p class="text-muted">Prestações fixas, ideal para quem precisa de menor desembolso inicial.</p>

                        <div class="metric-list">
                            <div class="metric-row">
                                <span class="metric-label">Total Pago</span>
                                <span class="metric-value">{{ formatCurrency(compareResult.price.total_amount) }}</span>
                            </div>
                            <div class="metric-row">
                                <span class="metric-label">Juros Totais</span>
                                <span class="metric-value">{{ formatCurrency(compareResult.price.total_interest_paid) }}</span>
                            </div>
                            <div class="metric-row">
                                <span class="metric-label">1ª Parcela</span>
                                <span class="metric-value text-gold">{{ formatCurrency(compareResult.price.first_installment) }}</span>
                            </div>
                            <div class="metric-row">
                                <span class="metric-label">Última Parcela</span>
                                <span class="metric-value">{{ formatCurrency(compareResult.price.last_installment) }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tabela de Parcelas com Alternador de Abas (SAC ou PRICE) -->
                <div class="tabs-header">
                    <span style="font-weight: 600; margin-right: 10px;">Ver cronograma detalhado:</span>
                    <button type="button" class="tab-btn" :class="{ active: activeCompareTab === 'SAC' }" @click="activeCompareTab = 'SAC'">
                        Tabela SAC
                    </button>
                    <button type="button" class="tab-btn" :class="{ active: activeCompareTab === 'PRICE' }" @click="activeCompareTab = 'PRICE'">
                        Tabela Price
                    </button>
                </div>

                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Mês</th>
                                <th>Valor da prestação</th>
                                <th>Amortização</th>
                                <th>Juros</th>
                                <th>Saldo devedor</th>
                                <th>Pagamento total</th>
                                <th>Vencimento</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="inst in (activeCompareTab === 'SAC' ? compareResult.sac.installments : compareResult.price.installments)" :key="inst.month_number">
                                <td>{{ inst.month_number }}</td>
                                <td>{{ formatCurrency(inst.installment_amount) }}</td>
                                <td>{{ formatCurrency(inst.amortization_amount) }}</td>
                                <td>{{ formatCurrency(inst.interest_amount) }}</td>
                                <td>{{ formatCurrency(inst.final_balance) }}</td>
                                <td>{{ formatCurrency(inst.total_payment) }}</td>
                                <td>{{ formatDate(inst.payment_date) }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 2. RESULTADO DE SIMULAÇÃO INDIVIDUAL (quando usada) -->
            <div v-if="result && !compareResult">
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Total pago</th>
                                <th>Total de juros</th>
                                <th>Nº de parcelas</th>
                                <th>Primeira parcela</th>
                                <th>Última parcela</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{{ formatCurrency(result.total_amount) }}</td>
                                <td>{{ formatCurrency(result.total_interest_paid) }}</td>
                                <td>{{ result.total_installments }}</td>
                                <td>{{ formatCurrency(result.first_installment) }}</td>
                                <td>{{ formatCurrency(result.last_installment) }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Mês</th>
                                <th>Valor da prestação</th>
                                <th>Amortização</th>
                                <th>Juros</th>
                                <th>Saldo devedor</th>
                                <th>Pagamento extra</th>
                                <th>Pagamento total</th>
                                <th>Data de vencimento</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="installment in result.installments" :key="installment.month_number">
                                <td>{{ installment.month_number }}</td>
                                <td>{{ formatCurrency(installment.installment_amount) }}</td>
                                <td>{{ formatCurrency(installment.amortization_amount) }}</td>
                                <td>{{ formatCurrency(installment.interest_amount) }}</td>
                                <td>{{ formatCurrency(installment.final_balance) }}</td>
                                <td>{{ formatCurrency(installment.extra_payment) }}</td>
                                <td>{{ formatCurrency(installment.total_payment) }}</td>
                                <td>{{ formatDate(installment.payment_date) }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    </main>
</template>