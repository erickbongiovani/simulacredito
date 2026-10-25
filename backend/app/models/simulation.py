from app.core.database import Base
from enum import Enum
from sqlalchemy import Column, Integer, Enum, String, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from decimal import Decimal
from sqlalchemy import DECIMAL
from app.domain.entities import LoanType, AmortizationGoal
from sqlalchemy.orm import relationship


class Simulations(Base):
    __tablename__ = 'simulations'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    principal = Column(DECIMAL(15, 2), nullable=False)
    annual_interest_rate = Column(DECIMAL(15, 2), nullable=False)
    term_months = Column(Integer, nullable=False)
    payment_day = Column(Integer, nullable=False)
    system = Column(Enum(LoanType))
    start_date = Column(Date)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship('User', back_populates='simulations')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    total_amount = Column(DECIMAL(15, 2), nullable=False)
    total_interest_paid = Column(DECIMAL(15, 2), nullable=False)
    extra_payments = relationship('ExtraPayments', back_populates='simulation', cascade='all, delete-orphan')
    installments = relationship('Installments', back_populates='simulation', cascade='all, delete-orphan')

    @property
    def total_installments(self) -> int:
        return len(self.installments) if self.installments else self.term_months

    @property
    def first_installment(self):
        return self.installments[0].installment_amount if self.installments else Decimal('0.00')

    @property
    def last_installment(self):
        return self.installments[-1].installment_amount if self.installments else Decimal('0.00')
    

class ExtraPayments(Base):
    __tablename__ = 'extra_payments'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    simulation_id = Column(Integer, ForeignKey('simulations.id'))
    installment_id = Column(Integer, ForeignKey('installments.id'))
    month_number = Column(Integer, nullable=False)
    amount = Column(DECIMAL(15, 2), nullable=False)
    goal = Column(Enum(AmortizationGoal), nullable=False)
    simulation = relationship('Simulations', back_populates='extra_payments')
    installment = relationship('Installments', back_populates='extra_payments')

class Installments(Base):
    __tablename__ = 'installments'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    simulation_id = Column(Integer, ForeignKey('simulations.id'))
    month_number = Column(Integer, nullable=False)
    initial_balance = Column(DECIMAL(15, 2), nullable=False)
    installment_amount = Column(DECIMAL(15, 2), nullable=False)
    amortization_amount = Column(DECIMAL(15, 2), nullable=False)
    interest_amount = Column(DECIMAL(15, 2), nullable=False)
    final_balance = Column(DECIMAL(15, 2), nullable=False)
    extra_payment = Column(DECIMAL(15, 2), nullable=False)
    payment_date = Column(Date)
    simulation = relationship('Simulations', back_populates='installments')
    extra_payments = relationship('ExtraPayments', back_populates='installment')

    @property
    def starting_balance(self):
        return self.initial_balance

    @property
    def total_payment(self):
        return self.installment_amount + (self.extra_payment or Decimal('0.00'))

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    simulations = relationship('Simulations', back_populates='user')


