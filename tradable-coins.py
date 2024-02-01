from coinbase.rest import RESTClient

# Set your API key and secret
api_key = "organizations/a767d337-1e91-45cb-95fa-75b701dd6edb/apiKeys/039c4bdc-33a2-4f66-bd02-cc83018624d3"
api_secret = "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIKOsU+N4V/YsTAe9FSHD9WEMMQk8pBLDeKI3muBKrlVboAoGCCqGSM49\nAwEHoUQDQgAEHe9LjhybIea2ZKVre0XdSvKrJ/VCqEJ4qVOFS3qmK961PBKbSlD7\n/QYQYcRny2KvFUIfSOHE8q3GkWLFAPeO/Q==\n-----END EC PRIVATE KEY-----\n"


# Create a RestClient instance
client = RESTClient(api_key=api_key, api_secret=api_secret, timeout=5)

# Get the list of tradable products
products = client.get_products()

# Print the list of tradable products
for product in products:
    print(product['id'])