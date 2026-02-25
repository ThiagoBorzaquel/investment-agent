import os
import datetime
import requests
from data.market_data import get_stock_data
from analysis.scoring import value_score

# Lista inicial
tickers = [
    "PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3",
    "WEGE3", "MGLU3", "SUZB3", "ELET3", "RENT3",
    "LREN3", "PRIO3", "GGBR4", "CSNA3", "EMBR3",
    "JBSS3", "RADL3", "HAPV3", "EQTL3", "RAIL3"
]

# =========================
# COLETA E RANKING
# =========================

df = get_stock_data(tickers)
df["Score"] = df.apply(value_score, axis=1)
df = df.sort_values("Score", ascending=False)

top20 = df.head(20)

hoje = datetime.date.today()
arquivo = f"ranking_value_{hoje}.csv"
top20.to_csv(arquivo, index=False)

# =========================
# MENSAGEM
# =========================

mensagem = f"📊 Ranking Value Diário - {hoje}\n\n"

for _, row in top20.head(5).iterrows():
    mensagem += (
        f"{row['Ticker']} | "
        f"Score: {row['Score']} | "
        f"PVP: {round(row['PVP'], 2)} | "
        f"PL: {round(row['PL'], 2)}\n"
    )

# =========================
# TELEGRAM
# =========================


TOKEN = os.getenv("8714485092:AAEBTxwIFbwoE62tcBWtNSdXa-i5ePTAXvY")
CHAT_ID = os.getenv('id": 8714485092')

print("TOKEN carregado:", bool(TOKEN))
print("CHAT_ID carregado:", bool(CHAT_ID))

if TOKEN and CHAT_ID:

    url_msg = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r1 = requests.post(
        url_msg,
        data={
            "chat_id": CHAT_ID,
            "text": mensagem
        }
    )
    print("Mensagem status:", r1.status_code, r1.text)

    url_doc = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(arquivo, "rb") as file:
        r2 = requests.post(
            url_doc,
            data={"chat_id": CHAT_ID},
            files={"document": file}
        )
    print("Documento status:", r2.status_code, r2.text)

else:
    print("Secrets não encontrados")