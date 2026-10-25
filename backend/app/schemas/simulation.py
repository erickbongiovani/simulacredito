from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal
from app.domain.entities import LoanType, AmortizationGoal
from datetime import date, datetime


class ExtraPaymentRequest(BaseModel):    
    month_number: int = Field(..., gt=0, description='Mês em que o aporte será realizado')
    amount: Decimal = Field(..., gt=0, description='Valor do aporte financeiro')
    goal: AmortizationGoal = Field(..., description='Objetivo: REDUCE_TERM ou REDUCE_INSTALLMENT')


class SimulationRequest(BaseModel):
    principal: Decimal = Field(..., gt=0, description='Valor financiado / do empréstimo')
    annual_interest_rate: Decimal = Field(..., ge=0, description='Taxa de juros anual (ex: 0.10 para 10% a.a.)')
    term_months: int = Field(..., gt=0, description='Prazo total em meses')
    payment_day: int = Field(default=5, ge=1, le=28, description='Dia do vencimento da parcela')
    system: LoanType = Field(..., description='Sistema de amortização: SAC ou PRICE')
    extra_payments: list[ExtraPaymentRequest] | None = Field(default=None, description='Lista opcional de aportes extraordinários')
    start_date: Optional[date] = Field(default=None, description='Data do inicio do emprestimo')


class InstallmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month_number: int = Field(..., description='Número da parcela')
    starting_balance: Decimal = Field(..., description='Saldo devedor inicial do período')
    installment_amount: Decimal = Field(..., description='Valor da prestação contratual')
    amortization_amount: Decimal = Field(..., description='Valor da amortização da dívida')
    interest_amount: Decimal = Field(..., description='Valor dos juros do mês')
    final_balance: Decimal = Field(..., description='Saldo devedor residual final')
    extra_payment: Decimal = Field(default=Decimal('0.00'), description='Aporte extraordinário aplicado')
    total_payment: Decimal = Field(..., description='Total desembolsado no mês (prestação + aporte)')
    payment_date: Optional[date] = Field(default=None, description='Data de vencimento da parcela')

class SimulationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_amount: Decimal = Field(..., description='Valor total pago no financiamento')
    total_interest_paid: Decimal = Field(..., description='Total de juros pagos acumulados')
    total_installments: int = Field(..., description='Número total de parcelas geradas até a quitação')
    first_installment: Decimal = Field(..., description='Valor da primeira prestação')
    last_installment: Decimal = Field(..., description='Valor da última prestação')
    installments: list[InstallmentResponse] = Field(..., description='Lista completa das parcelas mês a mês')


class ExtraPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    month_number: int = Field(..., description='Mês do aporte')
    amount: Decimal = Field(..., description='Valor do aporte')
    goal: AmortizationGoal = Field(..., description='Objetivo do aporte')


class SimulationCreateRequest(SimulationRequest):
    title: str = Field(..., min_length=1, max_length=255, description='Título para salvar a simulação')


class SimulationSummaryDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    principal: Decimal
    annual_interest_rate: Decimal
    term_months: int
    payment_day: int
    system: LoanType
    start_date: Optional[date] = None
    created_at: Optional[datetime] = None
    total_amount: Decimal
    total_interest_paid: Decimal


class SimulationDetailDB(SimulationSummaryDB):
    total_installments: int
    first_installment: Decimal
    last_installment: Decimal
    installments: list[InstallmentResponse] = []
    extra_payments: list[ExtraPaymentResponse] = []
