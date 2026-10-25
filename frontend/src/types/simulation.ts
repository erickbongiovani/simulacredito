// ============================================================
// Espelho exato dos schemas Pydantic do backend (simulation.py)
// Qualquer alteração no backend DEVE ser refletida aqui.
// ============================================================


export type LoanType = 'SAC' | 'PRICE'

export type AmortizationGoal = 'REDUCE_TERM' | 'REDUCE_INSTALLMENT'

// ---------- Inputs (Request) ----------

export interface ExtraPaymentRequest {
  month_number: number
  amount: number
  goal: AmortizationGoal
}

export interface SimulationRequest {
  principal: number
  annual_interest_rate: number   // Decimal unitário: 0.17 = 17% a.a.
  term_months: number
  payment_day: number            // Dia do mês (1–28)
  system: LoanType
  start_date?: string | null     // ISO 8601: "YYYY-MM-DD". Se omitido, sem datas de vencimento
  extra_payments?: ExtraPaymentRequest[] | null
}

// ---------- Outputs (Response) ----------

export interface InstallmentResponse {
  month_number: number
  starting_balance: number
  installment_amount: number
  amortization_amount: number
  interest_amount: number
  final_balance: number
  extra_payment: number
  total_payment: number
  payment_date: string | null    // ISO 8601: "YYYY-MM-DD"
}

export interface SimulationResponse {
  total_amount: number
  total_interest_paid: number
  total_installments: number
  first_installment: number
  last_installment: number
  installments: InstallmentResponse[]
}

export interface ComparisonRequest {
  principal: number
  annual_interest_rate: number
  term_months: number
  payment_day: number
  extra_payments?: ExtraPaymentRequest[] | null
  start_date?: string | null
}

export interface ComparisonResponse {
  sac: SimulationResponse
  price: SimulationResponse
  interest_difference: number
  total_amount_difference: number
  first_installment_difference: number
  last_installment_difference: number
}