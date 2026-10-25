from datetime import date
from typing import Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entities import LoanParameters, ExtraPayment
from app.domain.calculators import simular
from app.models.simulation import Simulations, Installments, ExtraPayments
from app.schemas.simulation import SimulationCreateRequest


def save_simulation(db: Session, payload: SimulationCreateRequest) -> Simulations:
    start_date = payload.start_date or date.today()
    params = LoanParameters(
        principal=payload.principal,
        annual_interest_rate=payload.annual_interest_rate,
        term_months=payload.term_months,
        payment_day=payload.payment_day,
        system=payload.system,
        start_date=start_date
    )

    domain_extra_payments = [
        ExtraPayment(
            month_number=ep.month_number,
            amount=ep.amount,
            goal=ep.goal
        )
        for ep in (payload.extra_payments or [])
    ]

    calc_result = simular(params, domain_extra_payments)

    sim_model = Simulations(
        title=payload.title,
        principal=payload.principal,
        annual_interest_rate=payload.annual_interest_rate,
        term_months=payload.term_months,
        payment_day=payload.payment_day,
        system=payload.system,
        start_date=start_date,
        total_amount=calc_result.total_amount_paid,
        total_interest_paid=calc_result.total_interest_paid,
    )

    installments_by_month = {}
    for p in calc_result.installments:
        inst_model = Installments(
            simulation=sim_model,
            month_number=p.month_number,
            initial_balance=p.starting_balance,
            installment_amount=p.installment_amount,
            amortization_amount=p.amortization_amount,
            interest_amount=p.interest_amount,
            final_balance=p.final_balance,
            extra_payment=p.extra_payment,
            payment_date=p.payment_date,
        )
        sim_model.installments.append(inst_model)
        installments_by_month[p.month_number] = inst_model

    if payload.extra_payments:
        for ep in payload.extra_payments:
            ep_model = ExtraPayments(
                simulation=sim_model,
                installment=installments_by_month.get(ep.month_number),
                month_number=ep.month_number,
                amount=ep.amount,
                goal=ep.goal
            )
            sim_model.extra_payments.append(ep_model)

    try:
        db.add(sim_model)
        db.commit()
        db.refresh(sim_model)
        return sim_model
    except SQLAlchemyError as exc:
        db.rollback()
        raise exc


def list_simulations(db: Session, skip: int = 0, limit: int = 100) -> list[Simulations]:
    return (
        db.query(Simulations)
        .order_by(Simulations.created_at.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )


def get_simulation_by_id(db: Session, simulation_id: int) -> Optional[Simulations]:
    return (
        db.query(Simulations)
        .options(
            selectinload(Simulations.installments),
            selectinload(Simulations.extra_payments)
        )
        .filter(Simulations.id == simulation_id)
        .first()
    )


def delete_simulation(db: Session, simulation_id: int) -> bool:
    sim = db.query(Simulations).filter(Simulations.id == simulation_id).first()
    if not sim:
        return False
    try:
        db.delete(sim)
        db.commit()
        return True
    except SQLAlchemyError as exc:
        db.rollback()
        raise exc
