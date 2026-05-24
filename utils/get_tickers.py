import requests
import pandas as pd


def get_all_asset_codes():
    url = "https://iss.moex.com/iss/statistics/engines/futures/markets/forts/series.json"

    r = requests.get(url, timeout=10)
    r.raise_for_status()

    block = r.json()["series"]
    df = pd.DataFrame(block["data"], columns=block["columns"])
    return df["asset_code"].dropna().unique().tolist()


def get_futures_by_asset(asset_code: str, show_expired: bool=False):
    url = "https://iss.moex.com/iss/statistics/engines/futures/markets/forts/series.json"
    params = {
        "asset_code": asset_code,
        "show_expired": int(show_expired)
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()

    block = r.json()["series"]
    df = pd.DataFrame(block["data"], columns=block["columns"])
    return df

def get_all_futures():
    asset_codes = get_all_asset_codes()

    dfs = []
    for code in asset_codes:
        try:
            df = get_futures_by_asset(code)
            if not df.empty:
                dfs.append(df)
        except Exception as e:
            print(e)

    result = pd.concat(dfs, ignore_index=True)
    return result


if __name__ == "__main__":
    df = get_all_futures()
    print(df)