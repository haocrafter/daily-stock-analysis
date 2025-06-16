import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime, timedelta
import time
import requests

def get_last_trading_day():
    """
    Get the last trading day (excluding weekends)
    """
    today = datetime.now()
    # If today is Monday, last trading day was Friday
    if today.weekday() == 0:  # Monday
        last_trading_day = today - timedelta(days=3)
    # If today is Sunday, last trading day was Friday
    elif today.weekday() == 6:  # Sunday
        last_trading_day = today - timedelta(days=2)
    # Otherwise, yesterday was a trading day
    else:
        last_trading_day = today - timedelta(days=1)
    
    return last_trading_day.strftime('%Y-%m-%d')

def get_most_active_stocks_finnhub(limit=20):
    """
    Try to get most active stocks from Finnhub API (free tier)
    """
    try:
        # Finnhub free API - no key required for some endpoints
        url = "https://finnhub.io/api/v1/stock/market-status?exchange=US&token=demo"
        response = requests.get(url, timeout=5)
        
        # If that doesn't work, try alternative approach
        # Get S&P 500 companies and check their volumes
        url = "https://api.twelvedata.com/stocks?source=docs&exchange=NASDAQ"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                symbols = [stock['symbol'] for stock in data['data'][:50]]
                return get_volume_sorted_stocks(symbols, limit)
        
    except Exception as e:
        print(f"Finnhub API error: {e}")
    
    return None

def get_most_active_stocks_polygon(limit=20):
    """
    Try to get most active stocks from Polygon.io (free tier)
    """
    try:
        last_trading_day = get_last_trading_day()
        # Polygon free API
        url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{last_trading_day}?adjusted=true&apikey=demo"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                # Sort by volume
                sorted_stocks = sorted(data['results'], key=lambda x: x.get('v', 0), reverse=True)
                symbols = [stock['T'] for stock in sorted_stocks[:limit]]
                return symbols
                
    except Exception as e:
        print(f"Polygon API error: {e}")
    
    return None

def get_volume_sorted_stocks(symbols, limit=20):
    """
    Get volume data for given symbols and sort by volume
    """
    print(f"Checking volume for {len(symbols)} stocks...")
    active_stocks = []
    
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            volume = info.get('regularMarketVolume', 0) or info.get('volume', 0)
            if volume > 0:
                active_stocks.append({
                    'symbol': symbol,
                    'volume': volume
                })
            
            time.sleep(0.02)  # Small delay to avoid rate limiting
            
        except Exception:
            continue
    
    # Sort by volume and return top symbols
    active_stocks.sort(key=lambda x: x['volume'], reverse=True)
    return [stock['symbol'] for stock in active_stocks[:limit]]

def get_most_active_stocks(limit=20):
    """
    Get the most actively traded stocks from the last trading day
    """
    print("Fetching most actively traded stocks from the last trading day...")
    last_trading_day = get_last_trading_day()
    print(f"Last trading day: {last_trading_day}")
    
    # Try multiple APIs in order of preference
    print("Trying Polygon.io API...")
    active_stocks = get_most_active_stocks_polygon(limit)
    
    if not active_stocks:
        print("Trying Finnhub API...")
        active_stocks = get_most_active_stocks_finnhub(limit)
    
    if not active_stocks:
        print("APIs unavailable, using popular stocks with volume check...")
        # Get popular stocks that are typically most active
        popular_stocks = [
            'SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'GOOGL', 'META',
            'AMD', 'NFLX', 'BAC', 'JPM', 'WMT', 'JNJ', 'V', 'PG', 'HD', 'UNH',
            'MA', 'DIS', 'ADBE', 'CRM', 'KO', 'PFE', 'MRK', 'ABBV', 'PEP', 'COST',
            'XOM', 'CVX', 'LLY', 'AVGO', 'ORCL', 'ACN', 'DHR', 'VZ', 'ABT', 'QCOM',
            'TXN', 'MDT', 'IBM', 'INTC', 'COP', 'NEE', 'PM', 'UPS', 'RTX', 'HON'
        ]
        active_stocks = get_volume_sorted_stocks(popular_stocks, limit)
    
    return active_stocks or []

def plot_price_changes(symbols, months=3):
    """
    Plot price changes for multiple symbols over the specified period
    """
    plt.figure(figsize=(16, 10))
    end_date = datetime.now()
    start_date = end_date - pd.DateOffset(months=months)
    
    print(f"\nFetching historical data for {len(symbols)} stocks over the past {months} months...")
    successful_plots = 0
    
    for symbol in symbols:
        try:
            df = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'), 
                           end=end_date.strftime('%Y-%m-%d'), progress=False)
            if not df.empty:
                first_price = df['Close'].iloc[0]
                df['price_change'] = (df['Close'] - first_price) / first_price * 100
                plt.plot(df.index, df['price_change'], label=symbol, linewidth=2)
                print(f"✓ Added {symbol} to plot")
                successful_plots += 1
            else:
                print(f"✗ No data for {symbol}")
        except Exception as e:
            print(f"✗ Error plotting {symbol}: {e}")
    
    if successful_plots == 0:
        print("No data could be plotted")
        return
    
    plt.title(f'Price Changes of Most Active Stocks Over Past {months} Months\n(Based on Last Trading Day Volume)', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price Change (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('price_changes.png', dpi=300, bbox_inches='tight')
    print(f"\n📈 Plot with {successful_plots} stocks saved as 'price_changes.png'")
    
    # Show the plot
    plt.show()

def main():
    print("Most Active Stocks Price Change Plotter")
    print("=" * 55)
    
    # Get top 20 most active stocks from last trading day
    active_stocks = get_most_active_stocks(20)
    
    if active_stocks:
        print(f"\n📊 Top {len(active_stocks)} Most Active Stocks (Last Trading Day):")
        print("-" * 50)
        for i, symbol in enumerate(active_stocks, 1):
            print(f"{i:2d}. {symbol}")
        
        # Plot price changes
        plot_price_changes(active_stocks, months=3)
    else:
        print("❌ Could not fetch active stocks data.")

if __name__ == "__main__":
    main() 