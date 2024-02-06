import requests
import csv

def get_tradeable_crypto_coins():
    url = "https://api.exchange.coinbase.com/products"
    tradeable_coins = set()

    try:
        response = requests.get(url)
        response.raise_for_status()
        products = response.json()

        for product in products:
            base_currency = product['base_currency']
            quote_currency = product['quote_currency']
            tradeable_coins.add(base_currency)
            tradeable_coins.add(quote_currency)
            
    except requests.RequestException as e:
        print(f"Failed to fetch tradeable crypto coins: {e}")
        return []

    return sorted(list(tradeable_coins))

def write_coins_to_csv(coins, filename="tradeable_crypto_coins.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Tradeable Crypto Coins"])
        for coin in coins:
            writer.writerow([coin])
    print(f"Tradeable crypto coins have been written to {filename}")

if __name__ == "__main__":
    tradeable_coins = get_tradeable_crypto_coins()
    if tradeable_coins:
        write_coins_to_csv(tradeable_coins)
    else:
        print("No tradeable coins fetched to write to CSV.")
