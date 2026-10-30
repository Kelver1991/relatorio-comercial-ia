from datetime import date

from pydantic import BaseModel, Field


class Consultor(BaseModel):
    nome: str = Field(min_length=1)
    vendas_dia: int = Field(ge=0, description="Quantidade de vendas fechadas no dia")
    valor_dia: float = Field(ge=0, description="Valor vendido no dia (R$)")
    valor_mes: float = Field(ge=0, description="Valor acumulado no mês (R$)")
    meta_mes: float = Field(gt=0, description="Meta individual do mês (R$)")
    orcamentos_dia: int = Field(ge=0, default=0, description="Orçamentos enviados no dia")


class PedidoRelatorio(BaseModel):
    data: date
    dias_uteis_restantes: int = Field(ge=0, description="Dias úteis que faltam para fechar o mês")
    consultores: list[Consultor] = Field(min_length=1)


class MetricaConsultor(BaseModel):
    nome: str
    valor_mes: float
    meta_mes: float
    percentual_meta: float
    falta_para_meta: float
    necessario_por_dia: float
    conversao_dia: float | None
    posicao: int


class MetricasEquipe(BaseModel):
    valor_dia: float
    valor_mes: float
    meta_mes: float
    percentual_meta: float
    consultores: list[MetricaConsultor]


class RespostaRelatorio(BaseModel):
    modo: str  # "ia" ou "demo"
    metricas: MetricasEquipe
    texto_whatsapp: str
