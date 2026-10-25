from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from uuid import UUID
from datetime import date
from typing import Optional

class LoanType(Enum):
    SAC = "SAC"
    PRICE = "PRICE"


class AmortizationGoal(Enum):
    REDUCE_TERM = "REDUCE_TERM"
    REDUCE_INSTALLMENT = "REDUCE_INSTALLMENT"


@dataclass(frozen=True)
class Installment:
    month_number: int
    #prestação
    installment_amount: Decimal
    #amortização
    amortization_amount: Decimal
    #juros
    interest_amount: Decimal
    #saldo a amortizar
    starting_balance: Decimal
    #saldo remanescente
    final_balance: Decimal
    #valor total
    total_payment: Decimal
    #pagamento extraordinário
    extra_payment: Decimal = Decimal('0.00')
    #data
    payment_date: Optional[date] = None

@dataclass(frozen=True)
class LoanParameters:
    principal: Decimal
    annual_interest_rate: Decimal
    term_months: int
    system: LoanType
    payment_day: int = 5
    start_date: date = field(default_factory=date.today)


@dataclass(frozen=True)
class ExtraPayment:
    month_number: int
    amount: Decimal
    goal: AmortizationGoal

    
@dataclass(frozen=True)
class SimulationResult:
    #parcelas
    installments: list[Installment]
    #juros pagos totais
    total_interest_paid: Decimal
    #valor total pago
    total_amount_paid: Decimal


@dataclass(frozen=True)
class LoanContract:
    id: UUID
    name: str
    start_date: date
    parameters: LoanParameters

