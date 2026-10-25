from app.domain.entities import LoanType, LoanParameters
from app.domain.calculators import simular
from app.schemas.comparison import ComparisonRequest, ComparisonResponse
from app.schemas.simulation import SimulationResponse, InstallmentResponse


def to_simulation_response(result) -> SimulationResponse:
    installments_response = [InstallmentResponse.model_validate(p) for p in result.installments]
    return SimulationResponse(
        total_amount = result.total_amount_paid,
        total_interest_paid = result.total_interest_paid,
        total_installments = len(result.installments),
        first_installment = result.installments[0].installment_amount,
        last_installment = result.installments[-1].installment_amount,
        installments=installments_response
    )

def diferenca_sistemas(payload: ComparisonRequest)-> ComparisonResponse:
    price_params = LoanParameters(
        principal=payload.principal,
        annual_interest_rate=payload.annual_interest_rate,
        term_months=payload.term_months,
        payment_day=payload.payment_day,
        system=LoanType.PRICE
    )

    sac_params = LoanParameters(
        principal=payload.principal,
        annual_interest_rate=payload.annual_interest_rate,
        term_months=payload.term_months,
        payment_day=payload.payment_day,
        system=LoanType.SAC
    )

    price_result = to_simulation_response(simular(price_params))
    sac_result = to_simulation_response(simular(sac_params))

    return ComparisonResponse(
        sac = sac_result,
        price = price_result,
        interest_difference = abs(sac_result.total_interest_paid - price_result.total_interest_paid),
        total_amount_difference = abs(sac_result.total_amount - price_result.total_amount),
        first_installment_difference = abs(sac_result.first_installment - price_result.first_installment),
        last_installment_difference = abs(sac_result.last_installment - price_result.last_installment)
    )