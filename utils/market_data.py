import requests
import pandas as pd
from datetime import datetime, timedelta
from datetime import date

INTERVAL_DELTA = {
    1:   timedelta(hours=8),
    10:  timedelta(days=4),
    60:  timedelta(days=20),
    1440: timedelta(days=365),
}


def get_candles(symbol, start_date, end_date, interval=10, show=False, engine="stock", market="shares", board="TQBR"):
    url = f"https://iss.moex.com/iss/engines/{engine}/markets/{market}/boards/{board}/securities/{symbol}/candles.json"
    cur_date = start_date

    delta = INTERVAL_DELTA[interval]
    df = pd.DataFrame()

    session = requests.Session()

    while cur_date < end_date:
        params = {
            "from": cur_date,
            "till": cur_date + delta,
            "interval": interval,
        }
        response = session.get(url, params=params)
        data = response.json()

        temp_df = pd.DataFrame(data["candles"]["data"], columns=data["candles"]["columns"])
        df = pd.concat([df, temp_df], ignore_index=True)

        cur_date = cur_date + delta
        if show:
            print(cur_date)

    duplicates_count = df.duplicated(subset=["begin"]).sum()
    df.drop_duplicates(subset=["begin"], inplace=True)
    print("Number of deleted duplicates:", duplicates_count)

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
        show=True
    )
    print(df)

if __name__ == "__main__":
    main()