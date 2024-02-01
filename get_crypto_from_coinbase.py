import requests
from requests.auth import HTTPBasicAuth

# Replace these with your actual Coinbase API credentials
API_KEY = '039c4bdc-33a2-4f66-bd02-cc83018624d3'
API_SECRET = 'e89bc15a-294a-58c9-aaf1-e9d73167daa8'

# Coinbase API endpoints
BASE_URL = 'https://api.coinbase.com/v2'
ACCOUNT_ENDPOINT = '/account'
CURRENCY_PAIR = 'BTC-USD'  # Replace with the desired cryptocurrency pair

def get_auth_headers():
    auth = HTTPBasicAuth(API_KEY, API_SECRET)
    headers = {
        'Content-Type': 'application/json',
    }
    return auth, headers

def get_account_data():
    endpoint = BASE_URL + ACCOUNT_ENDPOINT
    auth, headers = get_auth_headers()
    response = requests.get(endpoint, auth=auth, headers=headers)
    return response.json()

def get_currency_pair_data(currency_pair):
    endpoint = BASE_URL + f'/prices/{currency_pair}/spot'
    response = requests.get(endpoint)
    return response.json()

if __name__ == "__main__":
    # Example usage
    account_data = get_account_data()
    print("Account Data:")
    print(account_data)

    currency_pair_data = get_currency_pair_data(CURRENCY_PAIR)
    print(f"\n{CURRENCY_PAIR} Spot Price:")
    print(currency_pair_data)
