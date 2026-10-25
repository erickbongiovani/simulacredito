try:
    from app.domain.entities import *
except (ImportError, ModuleNotFoundError):
    from entities import *

from decimal import Decimal, ROUND_HALF_UP
#PADRÃO BRASILEIRO BACEN DE ARREDONDAMENTO
from datetime import date
import calendar


def moeda(value: Decimal) -> Decimal:
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def taxa_juros_mensal(annual_interest_rate: Decimal) -> Decimal:
    rate_float = float(annual_interest_rate)
    monthly_interest_rate = Decimal(str((1 + rate_float) ** (1/12) - 1))
    return monthly_interest_rate


def fator_sistema_price(taxa_mensal: Decimal, prazo: int) -> Decimal:
    numerador = (taxa_mensal * (1+taxa_mensal) ** prazo)
    denominador = ((1+taxa_mensal) ** prazo - 1)
    return Decimal(str(numerador/denominador))

def calcular_parcelas_sac(
    params: LoanParameters, extra_payments: list[ExtraPayment] | None = None
) -> list[Installment]:
    amortizacao_fixa = moeda(params.principal / params.term_months)
    taxa_mensal = taxa_juros_mensal(params.annual_interest_rate)
    saldo_atual = moeda(params.principal)

    mapa_aportes = {ep.month_number: ep for ep in (extra_payments or [])}
    installments: list[Installment] = []

    ano_base = params.start_date.year
    mes_base = params.start_date.month
    for mes in range(1, params.term_months + 1):
        if saldo_atual <= Decimal('0.00'):
            break

        mes_alvo = mes_base + mes
        ano_alvo = ano_base + (mes_alvo - 1) // 12
        mes_alvo = ((mes_alvo - 1) % 12) + 1

        ultimo_dia = calendar.monthrange(ano_alvo, mes_alvo)[1]
        dia_vencimento = min(params.payment_day, ultimo_dia)
        payment_date = date(ano_alvo, mes_alvo, dia_vencimento)

        juros_mes = moeda(saldo_atual * taxa_mensal)

        # Ajuste de última parcela se amortização for maior que o saldo restante
        if amortizacao_fixa >= saldo_atual or mes == params.term_months:
            amortizacao_mes = moeda(saldo_atual)
            prestacao_ajustada = moeda(amortizacao_mes + juros_mes)
        else:
            amortizacao_mes = moeda(amortizacao_fixa)
            prestacao_ajustada = moeda(amortizacao_mes + juros_mes)

        saldo_residual = moeda(saldo_atual - amortizacao_mes)

        aporte_do_mes = mapa_aportes.get(mes)
        valor_extra = moeda(aporte_do_mes.amount if aporte_do_mes else Decimal('0.00'))

        if valor_extra > saldo_residual:
            valor_extra_efetivo = moeda(saldo_residual)
            novo_saldo = Decimal('0.00')
        else:
            valor_extra_efetivo = valor_extra
            novo_saldo = moeda(saldo_residual - valor_extra_efetivo)

        prestacao_final = moeda(prestacao_ajustada + valor_extra_efetivo)

        parcela = Installment(
            month_number=mes,
            installment_amount=prestacao_ajustada,
            amortization_amount=amortizacao_mes,
            interest_amount=juros_mes,
            starting_balance=saldo_atual,
            final_balance=novo_saldo,
            total_payment=prestacao_final,
            extra_payment=valor_extra_efetivo,
            payment_date=payment_date
        )

        installments.append(parcela)

        if novo_saldo <= Decimal('0.00'):
            break

        meses_restantes = params.term_months - mes
        # REDUZIR VALOR DA PARCELA
        if aporte_do_mes and aporte_do_mes.goal == AmortizationGoal.REDUCE_INSTALLMENT and meses_restantes > 0:
            amortizacao_fixa = moeda(novo_saldo / meses_restantes)

        saldo_atual = novo_saldo

    return installments


def calcular_parcelas_price(
    params: LoanParameters, 
    extra_payments: list[ExtraPayment] | None = None
) -> list[Installment]:

    taxa_mensal = taxa_juros_mensal(params.annual_interest_rate)
    fator = fator_sistema_price(taxa_mensal, params.term_months)

    mapa_aportes = {ep.month_number: ep for ep in (extra_payments or [])}
    saldo_atual = moeda(params.principal)

    prestacao_atual = moeda(saldo_atual * fator)

    installments: list[Installment] = []

    ano_base = params.start_date.year
    mes_base = params.start_date.month

    for mes in range(1, params.term_months + 1):
        if saldo_atual <= Decimal('0.00'):
            break
        mes_alvo = mes_base + mes
        ano_alvo = ano_base + (mes_alvo - 1) // 12
        mes_alvo = ((mes_alvo - 1) % 12) + 1

        ultimo_dia = calendar.monthrange(ano_alvo, mes_alvo)[1]
        dia = min(params.payment_day, ultimo_dia)
        payment_date = date(ano_alvo, mes_alvo, dia)

        #AQUI FAZ COM QUE A AMORTIZACAO DIMINUA CASO REDUCE_TERM, POIS O SALDO DIMINUI
        juros_mes = moeda(saldo_atual * taxa_mensal)
        amortizacao_mes = moeda(prestacao_atual - juros_mes)
        

        if amortizacao_mes >= saldo_atual or mes == params.term_months or amortizacao_mes <= 0:
            amortizacao_mes = moeda(saldo_atual)
            prestacao_ajustada = moeda(amortizacao_mes + juros_mes)
        else:
            prestacao_ajustada = moeda(prestacao_atual)
        
        saldo_residual = moeda(saldo_atual - amortizacao_mes)

        aporte_do_mes = mapa_aportes.get(mes)
        valor_extra = aporte_do_mes.amount if aporte_do_mes else Decimal('0.00')
        valor_extra = moeda(valor_extra)

        if valor_extra > saldo_residual:
            valor_extra_efetivo = saldo_residual
            novo_saldo = Decimal('0.00')
        else:
            valor_extra_efetivo = valor_extra
            novo_saldo = moeda(saldo_residual - valor_extra_efetivo)
            
        prestacao_final = moeda(prestacao_ajustada + valor_extra_efetivo)

        parcela = Installment(
            month_number=mes,
            installment_amount=prestacao_ajustada,
            amortization_amount=amortizacao_mes,
            interest_amount=juros_mes,
            starting_balance=saldo_atual,
            final_balance=novo_saldo,
            total_payment=prestacao_final,
            extra_payment=valor_extra_efetivo,
            payment_date=payment_date
        )

        installments.append(parcela)

        if novo_saldo <= Decimal('0.00'):
            break

        if aporte_do_mes:
            if aporte_do_mes.goal == AmortizationGoal.REDUCE_INSTALLMENT:
                meses_restantes = params.term_months - mes
                if meses_restantes > 0:
                    fator = fator_sistema_price(taxa_mensal, meses_restantes)
                    prestacao_atual = moeda(novo_saldo * fator)
            elif aporte_do_mes.goal == AmortizationGoal.REDUCE_TERM:
                #PRESTAÇÃO SE MANTÉM, AMORTIZAÇÃO CRESCE NATURALMENTE
                #SOBRE O SALDO MENOR
                pass
        
        saldo_atual = novo_saldo
    return installments


##MINHA FUNÇÃO ZERO BALA DE SIMULAR FINANCIAMENTO
def simular(
    params: LoanParameters, 
    extra_payments: list[ExtraPayment] | None = None
) -> SimulationResult:
    if params.system == LoanType.SAC:
        installments = calcular_parcelas_sac(params, extra_payments)
    elif params.system == LoanType.PRICE:
        installments = calcular_parcelas_price(params, extra_payments)
    else:
        raise ValueError(f"Sistema de amortização não suportado: {params.system}")

    return SimulationResult(
        installments=installments,
        total_interest_paid=sum(p.interest_amount for p in installments),
        total_amount_paid=sum(p.total_payment for p in installments)
    )
            


        
