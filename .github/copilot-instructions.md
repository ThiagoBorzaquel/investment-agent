# Investment Agent - Instruções para AI Agents

## Visão Geral do Projeto

Agente de análise de investimentos em ações brasileiras (B3 - Bolsa de Valores). O projeto coleta dados fundamentalistas de cerca de 20 ações de blue-chips do mercado brasileiro e, futuramente, realizará análise, ranking e distribuição via Telegram.

### Arquitetura

```
investment_agent/
├── main.py              # Orquestrador principal - executa pipeline completo
├── data/
│   └── market_data.py   # Camada de dados - busca de informações via yfinance
├── analysis/            # [PLANEJADO] Cálculos e análises fundamentalistas
├── ranking/             # [PLANEJADO] Geração de rankings e scores
└── telegram/            # [PLANEJADO] Bot de distribuição de resultados
```

## Padrões de Dados e Convenções

### 1. Estrutura de Tickers
- **Formato**: Tickers brasileiros terminam com `.SA` (São Paulo Stock Exchange)
- **Exemplo**: `PETR4.SA`, `VALE3.SA` (convenção yfinance)
- **Ar armazenamento**: Listas simples de strings sem sufixo `.SA` em `main.py`; adicionado em tempo de execução

### 2. Estrutura de Dados Retornada
Função `get_stock_data()` retorna pandas DataFrame com colunas:
- `Ticker`, `Empresa`, `PVP` (Preço/Valor Patrimonial)
- `PL` (P/L ratio), `ROE`, `DivYield`, `DebtToEquity`, `MarketCap`
- Use `.get()` ao acessar campos de API (retorna None se não disponível)

### 3. Tratamento de Erros
- Exceções durante coleta de dados são capturadas **por ticker** (não falha o pipeline)
- Registra erro com `print()` mantendo a execução
- Dados inválidos retornam `None` e filtram naturalmente no DataFrame

## Fluxo de Dados Crítico

```
main.py (lista de tickers)
    ↓
get_stock_data(tickers) [data/market_data.py]
    ↓
yfinance.Ticker().info (API externa)
    ↓
pandas.DataFrame (saída esperada)
```

**Ponto crítico**: Yfinance faz requisições HTTP por ticker. Falhas em tickers individuais não devem interromper o pipeline.

## Dependências Principais

- **yfinance**: Busca dados de ações (sem auth necessária)
- **pandas**: Manipulação de dados tabulares
- **Python 3.8+**: Sem pinning explícito de versões (verificar venv/)

## Configurações Específicas

### Tickers Monitorados
Atualmente 20 blue-chips (definidos em `main.py`):
- Energia: PETR4, ELET3
- Mineração: VALE3, GGBR4
- Financeiro: ITUB4, BBDC4, BBAS3
- Retail: MGLU3, LREN3
- Etc.

**Pattern**: Adicionar novos tickers = editar lista `tickers` em `main.py`

## próximas Etapas (Planejadas)

- `analysis/`: Implementar cálculos fundamentalistas, scores de atratividade
- `ranking/`: Ordenar ações por critério (PL, ROE, etc.)
- `telegram/`: Integração com bot para alertas automatizados

## Checklist para Novos Recursos

- [ ] Imports seguem `from data.market_data import ...`
- [ ] Retorno de dados em pandas DataFrame quando aplicável
- [ ] Tickers brasileiros seguem nomenclatura `.SA`
- [ ] Exceções capturadas individualmente, não globalmente
- [ ] Código em inglês, comentários/strings em português
