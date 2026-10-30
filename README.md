# Relatório Comercial com IA

API em **FastAPI** que recebe os números diários de uma equipe de vendas e usa um **LLM (Claude)** para escrever o relatório de desempenho pronto para o grupo de WhatsApp.

## O problema

Na rotina de gestão comercial, montar o relatório diário da equipe é manual: somar vendas, calcular % da meta, montar ranking, ver quanto cada consultor precisa vender por dia e escrever a mensagem. Leva tempo todo dia e está sujeito a erro de conta.

## Como funciona

```
JSON com os números  ──►  metricas.py (Python faz TODAS as contas)
                                   │
                                   ▼
                        relatorio.py ──► Claude escreve o texto
                                   │        (só usa os números recebidos)
                                   ▼
                  resposta: métricas + texto pronto para o WhatsApp
```

**Decisão técnica principal:** a IA não faz conta. LLMs erram aritmética com frequência, então o Python calcula tudo (percentuais, ranking, quanto falta, média por dia útil) e o modelo recebe os números prontos com a instrução de não recalcular. O LLM fica só com o que ele faz bem: escrever.

Outras decisões:
- **Modo demo:** sem `ANTHROPIC_API_KEY`, a API gera o texto por um modelo fixo. Qualquer pessoa testa sem chave.
- **Falha da IA não derruba o serviço:** erro na API externa vira HTTP 502 com mensagem clara.
- **Ranking por % da meta**, e não por valor, para ser justo quando as metas são diferentes.
- **Regras de estilo no prompt** (negrito nos nomes, no máximo 2 emojis, sem travessão) e uma garantia extra no código.

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# opcional: ativar a IA
export ANTHROPIC_API_KEY=sua_chave   # Windows: set ANTHROPIC_API_KEY=sua_chave

uvicorn app.main:app --reload
```

Abra http://127.0.0.1:8000/docs para testar pela documentação interativa.

```bash
curl -X POST http://127.0.0.1:8000/relatorios \
  -H "Content-Type: application/json" -d @exemplo.json
```

Exemplo de saída (modo demo):

```
*Relatório comercial 30/10/2026*

Equipe no dia: R$ 43.000,00
Acumulado no mês: R$ 215.000,00 de R$ 260.000,00 (82,7% da meta)

Ranking (% da meta):
1. *Carla*: 106,2% (R$ 85.000,00)
2. *Ana*: 90,0% (R$ 90.000,00)
3. *Bruno*: 50,0% (R$ 40.000,00)
...
```

## Testes

```bash
pytest -q
```

Os testes cobrem cálculo das métricas, ranking, validação de entrada, modo demo e o modo IA com o modelo simulado (sem gastar chamadas de API).

## Estrutura

```
app/
  main.py       # rotas FastAPI
  schemas.py    # validação de entrada/saída com Pydantic
  metricas.py   # cálculos comerciais
  relatorio.py  # prompt e geração do texto
  llm.py        # cliente do Claude + detecção do modo demo
tests/
```

## Próximos passos

- Ler os dados direto de uma planilha ou do CRM.
- Enviar o relatório automaticamente no horário de fechamento.
- Comparar com o dia/semana anterior para mostrar tendência.

> Projeto de portfólio com dados fictícios. Inspirado na minha rotina real como gestor comercial.
