import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class StockDataFetcher:
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            raise ValueError("Please set ALPHA_VANTAGE_API_KEY in your .env file")
        
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_stock_data(self, symbol):
        """
        Fetch real-time stock data for a given symbol
        """
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'Error Message' in data:
                raise ValueError(f"Error: {data['Error Message']}")
            
            if 'Note' in data:
                print(f"Note: {data['Note']}")  # API limit warning
            
            quote = data.get('Global Quote', {})
            if not quote:
                raise ValueError(f"No data found for symbol {symbol}")
            
            return {
                'symbol': symbol,
                'price': float(quote.get('05. price', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0%'),
                'volume': int(quote.get('06. volume', 0)),
                'latest_trading_day': quote.get('07. latest trading day', ''),
                'previous_close': float(quote.get('08. previous close', 0))
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

def main():
    try:
        fetcher = StockDataFetcher()
        symbol = "AAPL"  # Default to Apple Inc.
        
        print(f"\nFetching data for {symbol}...")
        stock_data = fetcher.get_stock_data(symbol)
        
        if stock_data:
            print("\nStock Data:")
            print(f"Symbol: {stock_data['symbol']}")
            print(f"Current Price: ${stock_data['price']:.2f}")
            print(f"Change: ${stock_data['change']:.2f} ({stock_data['change_percent']})")
            print(f"Volume: {stock_data['volume']:,}")
            print(f"Latest Trading Day: {stock_data['latest_trading_day']}")
            print(f"Previous Close: ${stock_data['previous_close']:.2f}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 