def value_score(row):
    score = 0

    # Valuation (peso forte)
    if row["PVP"] > 0:
        if row["PVP"] < 0.8:
            score += 20
        elif row["PVP"] < 1:
            score += 15
        elif row["PVP"] < 1.5:
            score += 8

    if row["PL"] > 0:
        if row["PL"] < 8:
            score += 15
        elif row["PL"] < 12:
            score += 10

    # Qualidade mínima
    if row["ROE"] > 0.15:
        score += 10

    # Endividamento
    if 0 < row["DebtToEquity"] < 150:
        score += 10

    # Dividend Yield
    if row["DivYield"] and row["DivYield"] > 0.04:
        score += 10

    return score