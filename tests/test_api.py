from fastapi.testclient import TestClient

from app import relatorio
from app.main import app
from app.metricas import moeda

cliente = TestClient(app)

PEDIDO = {
    "data": "2026-10-30",
    "dias_uteis_restantes": 4,
    "consultores": [
        {"nome": "Ana", "vendas_dia": 1, "valor_dia": 18000, "valor_mes": 90000, "meta_mes": 100000, "orcamentos_dia": 4},
        {"nome": "Bruno", "vendas_dia": 0, "valor_dia": 0, "valor_mes": 40000, "meta_mes": 80000, "orcamentos_dia": 2},
        {"nome": "Carla", "vendas_dia": 2, "valor_dia": 25000, "valor_mes": 85000, "meta_mes": 80000},
    ],
}


def test_saude_em_modo_demo(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert cliente.get("/saude").json() == {"status": "ok", "modo": "demo"}


def test_metricas_e_ranking(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    corpo = cliente.post("/relatorios", json=PEDIDO).json()
    m = corpo["metricas"]
    assert corpo["modo"] == "demo"
    assert m["valor_mes"] == 215000
    assert m["percentual_meta"] == 82.7
    assert [c["nome"] for c in m["consultores"]] == ["Carla", "Ana", "Bruno"]
    bruno = m["consultores"][2]
    assert bruno["falta_para_meta"] == 40000
    assert bruno["necessario_por_dia"] == 10000
    assert bruno["conversao_dia"] == 0.0
    assert m["consultores"][0]["conversao_dia"] is None  # Carla não informou orçamentos


def test_texto_demo_tem_negrito_e_sem_travessao(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    texto = cliente.post("/relatorios", json=PEDIDO).json()["texto_whatsapp"]
    assert "*Ana*" in texto and "—" not in texto
    assert "82,7% da meta" in texto


def test_modo_ia_usa_numeros_calculados(monkeypatch):
    """Simula a IA para conferir que ela recebe os números já calculados."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "teste")
    recebido = {}

    def falso(sistema, mensagem, max_tokens=1024):
        recebido["mensagem"] = mensagem
        return "Relatório — gerado"

    monkeypatch.setattr(relatorio.llm, "gerar_texto", falso)
    corpo = cliente.post("/relatorios", json=PEDIDO).json()
    assert corpo["modo"] == "ia"
    assert '"percentual_meta": 82.7' in recebido["mensagem"]
    assert "—" not in corpo["texto_whatsapp"]


def test_falha_da_ia_vira_502(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "teste")

    def quebra(*a, **k):
        raise TimeoutError

    monkeypatch.setattr(relatorio.llm, "gerar_texto", quebra)
    assert cliente.post("/relatorios", json=PEDIDO).status_code == 502


def test_nome_repetido_e_meta_zero_sao_recusados():
    repetido = {**PEDIDO, "consultores": [PEDIDO["consultores"][0]] * 2}
    assert cliente.post("/relatorios", json=repetido).status_code == 422
    meta_zero = {**PEDIDO, "consultores": [{**PEDIDO["consultores"][0], "meta_mes": 0}]}
    assert cliente.post("/relatorios", json=meta_zero).status_code == 422


def test_moeda_padrao_brasileiro():
    assert moeda(1234567.8) == "R$ 1.234.567,80"
