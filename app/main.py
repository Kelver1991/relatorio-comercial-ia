from fastapi import FastAPI, HTTPException

from . import llm, metricas, relatorio
from .schemas import PedidoRelatorio, RespostaRelatorio

app = FastAPI(
    title="Relatório Comercial com IA",
    description="Recebe os números da equipe de vendas e devolve um relatório pronto para o WhatsApp.",
    version="1.0.0",
)


@app.get("/saude")
def saude():
    return {"status": "ok", "modo": "ia" if llm.ia_disponivel() else "demo"}


@app.post("/relatorios", response_model=RespostaRelatorio)
def criar_relatorio(pedido: PedidoRelatorio):
    nomes = [c.nome.strip().lower() for c in pedido.consultores]
    if len(nomes) != len(set(nomes)):
        raise HTTPException(status_code=422, detail="Há consultores com nome repetido.")

    calculadas = metricas.calcular(pedido)
    try:
        modo, texto = relatorio.gerar(pedido, calculadas)
    except Exception as erro:  # falha na API externa não pode derrubar o serviço
        raise HTTPException(status_code=502, detail=f"Falha ao gerar texto com IA: {type(erro).__name__}")
    return RespostaRelatorio(modo=modo, metricas=calculadas, texto_whatsapp=texto)
