"""Cálculo das métricas comerciais.

Decisão importante do projeto: TODA conta é feita aqui, em Python.
A IA só recebe os números prontos e escreve o texto. Assim ela não
inventa nem erra valores (LLMs costumam errar contas).
"""
from .schemas import MetricaConsultor, MetricasEquipe, PedidoRelatorio


def _pct(parte: float, total: float) -> float:
    return round(parte / total * 100, 1) if total else 0.0


def calcular(pedido: PedidoRelatorio) -> MetricasEquipe:
    linhas = []
    for c in pedido.consultores:
        falta = max(c.meta_mes - c.valor_mes, 0)
        por_dia = falta / pedido.dias_uteis_restantes if pedido.dias_uteis_restantes else falta
        conversao = _pct(c.vendas_dia, c.orcamentos_dia) if c.orcamentos_dia else None
        linhas.append(
            MetricaConsultor(
                nome=c.nome,
                valor_mes=round(c.valor_mes, 2),
                meta_mes=round(c.meta_mes, 2),
                percentual_meta=_pct(c.valor_mes, c.meta_mes),
                falta_para_meta=round(falta, 2),
                necessario_por_dia=round(por_dia, 2),
                conversao_dia=conversao,
                posicao=0,
            )
        )

    # Ranking pelo percentual da meta (mais justo que valor absoluto quando as metas são diferentes)
    linhas.sort(key=lambda m: m.percentual_meta, reverse=True)
    for i, linha in enumerate(linhas, start=1):
        linha.posicao = i

    valor_mes = sum(c.valor_mes for c in pedido.consultores)
    meta_mes = sum(c.meta_mes for c in pedido.consultores)
    return MetricasEquipe(
        valor_dia=round(sum(c.valor_dia for c in pedido.consultores), 2),
        valor_mes=round(valor_mes, 2),
        meta_mes=round(meta_mes, 2),
        percentual_meta=_pct(valor_mes, meta_mes),
        consultores=linhas,
    )


def percentual(valor: float) -> str:
    """82.7 -> '82,7%'"""
    return f"{valor:.1f}%".replace(".", ",")


def moeda(valor: float) -> str:
    """Formata no padrão brasileiro: R$ 12.345,67"""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"
