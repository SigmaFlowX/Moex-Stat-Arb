import requests
import pandas as pd
from datetime import date


def get_candles(symbol, start_date, end_date, interval=10, engine="stock", market="shares", board="TQBR"):
    url = f"https://iss.moex.com/iss/engines/{engine}/markets/{market}/boards/{board}/securities/{symbol}/candles.json"

    session = requests.Session()
    all_dfs = []
    start = 0
    while True:

        params = {
            "start": start,
            "from": start_date,
            "till": end_date,
            "interval": interval,
        }

        response = session.get(url, params=params, timeout=30)
        data = response.json()

        candles = data.get("candles", {})
        rows = candles.get("data", [])
        cols = candles.get("columns", [])

        all_dfs.append(pd.DataFrame(rows, columns=cols))

        if len(rows) < 500:
            break
        start += 500

    if not all_dfs:
        return pd.DataFrame()

    df = pd.concat(all_dfs, ignore_index=True)
    df["timestamp"] = pd.to_datetime(df["begin"])
    df.set_index("timestamp", inplace=True)
    df.drop(columns=["begin"], inplace=True)

    return df

def main():
    df = get_candles(
        "BRM6",
        date(2026, 5, 20),
        date(2026, 5, 23),
        interval=60,
        engine="futures",
        market="forts",
        board="RFUD",
    )

    import matplotlib.pyplot as plt
    plt.scatter(df.index, df['close'])
    plt.xticks(rotation=45)
    plt.show()

if __name__ == "__main__":
    main()