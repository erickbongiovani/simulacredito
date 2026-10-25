from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import date
from app.domain.entities import LoanType
from app.schemas.simulation import SimulationResponse, ExtraPaymentRequest, InstallmentResponse

class ComparisonRequest(BaseModel):
    principal: Decimal = Field(..., gt=0, description='Valor financiado / do empréstimo')
    annual_interest_rate: Decimal = Field(..., ge=0, description='Taxa de juros anual (ex: 0.10 para 10% a.a.)')
    term_months: int = Field(..., gt=0, description='Prazo total em meses')
    payment_day: int = Field(default=5, ge=1, le=28, description='Dia do vencimento da parcela')
    extra_payments: list[ExtraPaymentRequest] | None = Field(default=None, description='Lista opcional de aportes extraordinários')
    start_date: Optional[date] = Field(default=None, description='Data do inicio do emprestimo')


class ComparisonResponse(BaseModel):
    sac: SimulationResponse = Field(..., description='Simulação completa pelo sistema SAC')
    price: SimulationResponse = Field(..., description='Simulação completa pelo sistema PRICE')
    interest_difference: Decimal = Field(..., description='Diferença total de juros entre os sistemas')
    total_amount_difference: Decimal = Field(..., description='Diferença total pagos entre sistemas')
    first_installment_difference: Decimal = Field(..., description='Diferença na primeira parcela')
    last_installment_difference: Decimal = Field(..., description='Diferença na última parcela')
