import requests


def all_futures():
    url =  "https://iss.moex.com/iss/statistics/engines/futures/markets/forts/series.json"

    r = requests.get(url)
    print(r.json()['series']['data'])

def main():
    all_futures()

if __name__ == "__main__":
    main()