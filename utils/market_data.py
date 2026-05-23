import requests
import pandas as pd
from datetime import datetime, timedelta

def get_candles(symbol, start_date, end_date, interval=10, show=False):
    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{symbol}/candles.json"
    cur_date = start_date

    if interval == 10:
        delta = 3
    else:
        delta = 0.5
    df = pd.DataFrame()

    session = requests.Session()

    while cur_date < end_date:
        params = {
            "from": cur_date,
            "till": cur_date + timedelta(days=delta),
            "interval": interval
        }
        response = session.get(url, params=params)
        data = response.json()

        temp_df = pd.DataFrame(data["candles"]["data"], columns=data["candles"]["columns"])
        df = pd.concat([df, temp_df], ignore_index=True)


        cur_date = cur_date + timedelta(days=delta)
        if show:
            print(cur_date)

    duplicates_count = df.duplicated(subset=["begin"]).sum()
    df.drop_duplicates(subset=["begin"], inplace=True)
    print("Number of deleted duplicates:", duplicates_count)

    df['timestamp'] = pd.to_datetime(df['begin'])
    df.set_index('timestamp', inplace=True)
    df.drop(columns=['begin'], inplace=True)

    return df