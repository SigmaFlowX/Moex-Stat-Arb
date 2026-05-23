import requests
from datetime import datetime, timezone

def authorize(refresh_token):
    url = "https://be.broker.ru/trade-api-keycloak/realms/tradeapi/protocol/openid-connect/token"

    payload = {
        "client_id": "trade-api-write",
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        tokens = response.json()
        token = tokens["access_token"]
        return token
    else:
        print("Error while trying  to authorize:", response.status_code, response.text)
        return None

def get_candles(token, ticker, start_date, end_date, class_code="TQBR", timeframe = "M1"):
    url = "https://be.broker.ru/trade-api-market-data-connector/api/v1/candles-chart"

    start_date = datetime.fromisoformat(start_date).astimezone(timezone.utc)
    start_date = start_date.isoformat(timespec="milliseconds")

    end_date = datetime.fromisoformat(end_date).astimezone(timezone.utc)
    end_date = end_date.isoformat(timespec="milliseconds")

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "classCode": class_code,
        "ticker": ticker,
        "startDate": start_date,
        "endDate": end_date,
        "timeFrame": timeframe
    }

    response = requests.get(url, headers=headers, params=payload)

    return response.json()['bars']
