"""Geração do texto do relatório para WhatsApp."""
import json

from . import llm
from .metricas import moeda, percentual
from .schemas import MetricasEquipe, PedidoRelatorio

PROMPT_SISTEMA = """Você é um analista de performance comercial de uma loja.
Escreva um relatório diário curto para o grupo de WhatsApp da equipe de vendas.

Regras:
- Use SOMENTE os números do JSON recebido. Nunca recalcule nem invente valores.
- Português do Brasil, tom profissional e motivador, sem exageros.
- Nomes dos consultores em negrito do WhatsApp (*Nome*).
- No máximo 2 emojis no texto inteiro. Não use travessão (—).
- Estrutura: resultado da equipe, ranking, destaque do dia, quem precisa de atenção
  (quanto falta e quanto precisa vender por dia) e uma frase final de direcionamento.
- Texto puro pronto para copiar e colar, sem Markdown de títulos (#) e sem citações (>).
"""


def _texto_demo(pedido: PedidoRelatorio, m: MetricasEquipe) -> str:
    """Modelo fixo usado quando não há chave de API (modo demo)."""
    linhas = [
        f"*Relatório comercial {pedido.data.strftime('%d/%m/%Y')}*",
        "",
        f"Equipe no dia: {moeda(m.valor_dia)}",
        f"Acumulado no mês: {moeda(m.valor_mes)} de {moeda(m.meta_mes)} ({percentual(m.percentual_meta)} da meta)",
        "",
        "Ranking (% da meta):",
    ]
    for c in m.consultores:
        linhas.append(f"{c.posicao}. *{c.nome}*: {percentual(c.percentual_meta)} ({moeda(c.valor_mes)})")
    atencao = [c for c in m.consultores if c.falta_para_meta > 0]
    if atencao:
        linhas += ["", "Para bater a meta:"]
        for c in atencao:
            linhas.append(
                f"*{c.nome}*: faltam {moeda(c.falta_para_meta)}, "
                f"média de {moeda(c.necessario_por_dia)} por dia útil"
            )
    linhas += ["", f"Faltam {pedido.dias_uteis_restantes} dias úteis. Bora fechar o mês forte!"]
    return "\n".join(linhas)


def gerar(pedido: PedidoRelatorio, metricas: MetricasEquipe) -> tuple[str, str]:
    """Devolve (modo, texto)."""
    if not llm.ia_disponivel():
        return "demo", _texto_demo(pedido, metricas)

    dados = {
        "data": pedido.data.strftime("%d/%m/%Y"),
        "dias_uteis_restantes": pedido.dias_uteis_restantes,
        "equipe": metricas.model_dump(),
    }
    texto = llm.gerar_texto(PROMPT_SISTEMA, json.dumps(dados, ensure_ascii=False))
    return "ia", texto.replace("—", ",")  # garantia extra da regra de estilo
