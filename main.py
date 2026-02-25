from data.market_data import get_stock_data
from analysis.scoring import value_score
import datetime

tickers = [
    "PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3",
    "WEGE3", "MGLU3", "SUZB3", "ELET3", "RENT3",
    "LREN3", "PRIO3", "GGBR4", "CSNA3", "EMBR3",
    "JBSS3", "RADL3", "HAPV3", "EQTL3", "RAIL3"
]

df = get_stock_data(tickers)

df["Score"] = df.apply(value_score, axis=1)

df = df.sort_values("Score", ascending=False)

top20 = df.head(20)

print("\n=== TOP 20 VALUE ===\n")
print(top20[["Ticker", "PVP", "PL", "ROE", "Score"]])

# Exportar CSV
hoje = datetime.date.today()
arquivo = f"ranking_value_{hoje}.csv"
top20.to_csv(arquivo, index=False)

print(f"\nArquivo salvo: {arquivo}")

# Criar resumo texto
mensagem = f"\n📊 Ranking Value Diário - {hoje}\n\n"

for i, row in top20.head(5).iterrows():
    mensagem += f"{row['Ticker']} | Score: {row['Score']} | PVP: {round(row['PVP'],2)} | PL: {round(row['PL'],2)}\n"

print(mensagem)