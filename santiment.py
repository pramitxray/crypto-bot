import requests
import logging as lg

# Santiment API key (ensure it's correctly loaded from config.json)
API_KEY = 'natyx4ec4dvfudcd_ekin3cxr4da6shgj'

# Setup logger
lg.basicConfig(level=lg.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Santiment API base URL
SANTIMENT_API_BASE = "https://api.santiment.net/graphql"

def fetch_santiment_data(crypto_symbol):
    """
    Fetches on-chain data for the given cryptocurrency symbol using the Santiment API.
    
    :param crypto_symbol: The cryptocurrency symbol (e.g., 'bitcoin', 'ethereum').
    :return: A dictionary containing transaction volume, active addresses, and hash rate.
    """
    # Define GraphQL query (make sure the slug matches Santiment's format)
    query = f"""
    {{
      getMetric(metric: "transaction_volume") {{
        timeseriesData(
          slug: "{crypto_symbol}"
          from: "2023-01-01T00:00:00Z"
          to: "2024-01-01T00:00:00Z"
          interval: "1d"
        ) {{
          datetime
          value
        }}
      }}
      getMetric(metric: "active_addresses_24h") {{
        timeseriesData(
          slug: "{crypto_symbol}"
          from: "2023-01-01T00:00:00Z"
          to: "2024-01-01T00:00:00Z"
          interval: "1d"
        ) {{
          datetime
          value
        }}
      }}
    }}
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(SANTIMENT_API_BASE, json={"query": query}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        lg.info(f"Fetched Santiment data for {crypto_symbol}")
        
        transaction_volume = data['data']['getMetric'][0]['timeseriesData'][-1]['value']
        active_addresses = data['data']['getMetric'][1]['timeseriesData'][-1]['value']

        return {
            'transaction_volume': transaction_volume,
            'active_addresses': active_addresses,
        }
    else:
        lg.error(f"Failed to fetch Santiment data: {response.status_code}")
        return None
