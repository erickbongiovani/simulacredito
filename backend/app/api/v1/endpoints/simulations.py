from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.calculators import simular
from app.domain.entities import (
    AmortizationGoal,
    ExtraPayment,
    LoanParameters,
    LoanType,
)
from app.schemas.comparison import ComparisonRequest, ComparisonResponse
from app.schemas.simulation import (
    ExtraPaymentRequest,
    InstallmentResponse,
    SimulationCreateRequest,
    SimulationDetailDB,
    SimulationRequest,
    SimulationResponse,
    SimulationSummaryDB,
)
from app.services.comparison import diferenca_sistemas
from app.services.simulation_service import (
    delete_simulation,
    get_simulation_by_id,
    list_simulations,
    save_simulation,
)

router = APIRouter()


@router.post(
    "/calculate",
    response_model=SimulationResponse,
    status_code=status.HTTP_200_OK,
    summary="Realizar cálculo instantâneo em memória (sem salvar no banco)",
)
def calculate_simulation(payload: SimulationRequest) -> SimulationResponse:
    start_date = payload.start_date or date.today()
    params = LoanParameters(
        principal=payload.principal,
        annual_interest_rate=payload.annual_interest_rate,
        term_months=payload.term_months,
        payment_day=payload.payment_day,
        system=payload.system,
        start_date=start_date,
    )

    extra_payments = [
        ExtraPayment(
            month_number=ep.month_number,
            amount=ep.amount,
            goal=ep.goal,
        )
        for ep in (payload.extra_payments or [])
    ]

    result = simular(params, extra_payments)

    installments_response = [
        InstallmentResponse.model_validate(p) for p in result.installments
    ]

    return SimulationResponse(
        total_amount=result.total_amount_paid,
        total_interest_paid=result.total_interest_paid,
        total_installments=len(result.installments),
        first_installment=result.installments[0].installment_amount,
        last_installment=result.installments[-1].installment_amount,
        installments=installments_response,
    )


@router.post(
    "/compare",
    response_model=ComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Comparar sistemas de amortização SAC vs PRICE",
)
def comparar_sistemas(payload: ComparisonRequest) -> ComparisonResponse:
    return diferenca_sistemas(payload)


@router.post(
    "",
    response_model=SimulationDetailDB,
    status_code=status.HTTP_201_CREATED,
    summary="Calcular e persistir uma nova simulação no PostgreSQL",
)
def create_saved_simulation(
    payload: SimulationCreateRequest,
    db: Session = Depends(get_db),
) -> SimulationDetailDB:
    sim = save_simulation(db, payload)
    return sim


@router.get(
    "",
    response_model=list[SimulationSummaryDB],
    status_code=status.HTTP_200_OK,
    summary="Listar histórico de simulações salvas",
)
def get_all_simulations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[SimulationSummaryDB]:
    return list_simulations(db, skip=skip, limit=limit)


@router.get(
    "/{simulation_id}",
    response_model=SimulationDetailDB,
    status_code=status.HTTP_200_OK,
    summary="Obter detalhes e parcelas de uma simulação salva por ID",
)
def get_saved_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
) -> SimulationDetailDB:
    sim = get_simulation_by_id(db, simulation_id)
    if not sim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulação com ID {simulation_id} não encontrada.",
        )
    return sim


@router.delete(
    "/{simulation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir uma simulação salva e suas parcelas em cascata",
)
def remove_saved_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_simulation(db, simulation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulação com ID {simulation_id} não encontrada.",
        )
    return None
