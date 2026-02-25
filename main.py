import os
import datetime
import requests
from data.market_data import get_stock_data
from analysis.scoring import value_score

# Lista inicial (depois automatizamos índice completo)
tickers = [
    "PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3",
    "WEGE3", "MGLU3", "SUZB3", "ELET3", "RENT3",
    "LREN3", "PRIO3", "GGBR4", "CSNA3", "EMBR3",
    "JBSS3", "RADL3", "HAPV3", "EQTL3", "RAIL3"
]

# Coleta dados
df = get_stock_data(tickers)

df["Score"] = df.apply(value_score, axis=1)
df = df.sort_values("Score", ascending=False)

top20 = df.head(20)

# Salvar CSV
hoje = datetime.date.today()
arquivo = f"ranking_value_{hoje}.csv"
top20.to_csv(arquivo, index=False)

# Criar resumo
mensagem = f"📊 Ranking Value Diário - {hoje}\n\n"

for i, row in top20.head(5).iterrows():
    mensagem += (
        f"{row['Ticker']} | Score: {row['Score']} "
        f"| PVP: {round(row['PVP'],2)} "
        f"| PL: {round(row['PL'],2)}\n"
    )

# Enviar Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if TOKEN and CHAT_ID:

    # Enviar mensagem texto
    url_msg = f"https://api.telegram.org/bot8714485092:AAEBTxwIFbwoE62tcBWtNSdXa-i5ePTAXvY/sendMessage"
    requests.post(url_msg, data={
        "chat_id": id": 146536864,
        "text": mensagem
    })

    # Enviar CSV
    url_doc = f"https://api.telegram.org/bot8714485092:AAEBTxwIFbwoE62tcBWtNSdXa-i5ePTAXvY/sendDocument"
    with open(arquivo, "rb") as file:
        requests.post(url_doc, data={
            "chat_id": id": 146536864
        }, files={
            "document": file
        })