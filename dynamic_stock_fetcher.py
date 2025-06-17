import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DynamicStockFetcher:
    def __init__(self):
        self.all_stocks = []
        self.stock_metrics = {}
        
    def get_sp500_stocks(self):
        """Fetch S&P 500 stocks from Wikipedia"""
        print("Fetching S&P 500 stocks...")
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            sp500_df = tables[0]
            symbols = sp500_df['Symbol'].tolist()
            return [(symbol, 'SP500') for symbol in symbols]
        except Exception as e:
            print(f"Error fetching S&P 500: {e}")
            return []
    
    def get_nasdaq100_stocks(self):
        """Fetch NASDAQ 100 stocks"""
        print("Fetching NASDAQ 100 stocks...")
        try:
            url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
            tables = pd.read_html(url)
            nasdaq_df = tables[4]  # The main table is usually the 5th table
            symbols = nasdaq_df['Ticker'].tolist()
            return [(symbol, 'NASDAQ100') for symbol in symbols]
        except Exception as e:
            print(f"Error fetching NASDAQ 100: {e}")
            return []
    
    def get_dow_jones_stocks(self):
        """Fetch Dow Jones Industrial Average stocks"""
        print("Fetching Dow Jones stocks...")
        try:
            url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
            tables = pd.read_html(url)
            dow_df = tables[1]  # Companies table
            symbols = dow_df['Symbol'].tolist()
            return [(symbol, 'DOW') for symbol in symbols]
        except Exception as e:
            print(f"Error fetching Dow Jones: {e}")
            return []
    
    def get_most_active_stocks_yahoo(self):
        """Fetch most active stocks from Yahoo Finance"""
        print("Fetching most active stocks from Yahoo Finance...")
        try:
            # Get most active stocks
            url = "https://finance.yahoo.com/most-active"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for stock symbols in the page
            symbols = []
            
            # Try to find table with stock data
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if cells and len(cells) > 0:
                        # First cell usually contains the symbol
                        symbol_text = cells[0].get_text().strip()
                        if symbol_text and len(symbol_text) <= 5 and symbol_text.isalpha():
                            symbols.append(symbol_text)
            
            return [(symbol, 'MOST_ACTIVE') for symbol in symbols[:25]]
            
        except Exception as e:
            print(f"Error fetching Yahoo most active: {e}")
            return []
    
    def get_recent_ipos(self):
        """Fetch recent IPO stocks"""
        print("Fetching recent IPO stocks...")
        try:
            # Get IPOs from the last 2 years
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)  # 2 years
            
            # Use a list of known recent IPOs (this could be expanded with API calls)
            recent_ipos = [
                'RIVN', 'LCID', 'COIN', 'RBLX', 'ABNB', 'DASH', 'SNOW', 'PLTR',
                'U', 'DDOG', 'CRWD', 'ZM', 'PTON', 'BYND', 'UBER', 'LYFT',
                'PINS', 'ZS', 'OKTA', 'DOCU', 'TWLO', 'SHOP', 'SQ', 'PYPL',
                'ROKU', 'SPOT', 'SNAP', 'TWTR', 'NFLX', 'TSLA', 'NVTA', 'EDIT',
                'BEAM', 'CRSP', 'NTLA', 'PACB', 'ILMN', 'VRTX', 'GILD', 'BIIB'
            ]
            
            return [(symbol, 'RECENT_IPO') for symbol in recent_ipos]
            
        except Exception as e:
            print(f"Error fetching recent IPOs: {e}")
            return []
    
    def get_etf_holdings(self):
        """Get top holdings from popular ETFs"""
        print("Fetching top holdings from popular ETFs...")
        try:
            etf_symbols = ['SPY', 'QQQ', 'IWM', 'VTI', 'ARKK', 'XLF', 'XLK', 'XLE']
            all_holdings = []
            
            for etf in etf_symbols:
                try:
                    # Get ETF info
                    etf_ticker = yf.Ticker(etf)
                    
                    # Try to get holdings (this might not work for all ETFs)
                    # For now, we'll skip this and rely on other sources
                    pass
                    
                except Exception:
                    continue
            
            return all_holdings
            
        except Exception as e:
            print(f"Error fetching ETF holdings: {e}")
            return []
    
    def get_trending_stocks(self):
        """Get trending stocks from various sources"""
        print("Fetching trending stocks...")
        try:
            # Popular growth and tech stocks that are often trending
            trending_stocks = [
                # Mega-cap tech
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA',
                
                # Popular growth stocks
                'AMD', 'CRM', 'ADBE', 'NOW', 'SNOW', 'PLTR', 'RBLX',
                
                # Meme stocks / retail favorites
                'GME', 'AMC', 'BB', 'WISH', 'CLOV', 'SPCE', 'PLUG',
                
                # EV stocks
                'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'FISV', 'QS',
                
                # Biotech/Healthcare
                'MRNA', 'PFE', 'JNJ', 'GILD', 'BIIB', 'REGN', 'VRTX',
                
                # Fintech
                'SQ', 'PYPL', 'COIN', 'HOOD', 'SOFI', 'AFRM', 'UPST',
                
                # Cloud/Software
                'CRWD', 'ZS', 'OKTA', 'DDOG', 'NET', 'TWLO', 'DOCU'
            ]
            
            return [(symbol, 'TRENDING') for symbol in trending_stocks]
            
        except Exception as e:
            print(f"Error fetching trending stocks: {e}")
            return []
    
    def calculate_popularity_score(self, symbol):
        """Calculate popularity score based on multiple factors"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get recent data
            hist = stock.history(period="30d")
            if hist.empty:
                return 0
            
            score = 0
            
            # Market cap factor (normalized)
            market_cap = info.get('marketCap', 0)
            if market_cap > 1e12:  # > $1T
                score += 10
            elif market_cap > 1e11:  # > $100B
                score += 8
            elif market_cap > 1e10:  # > $10B
                score += 6
            elif market_cap > 1e9:   # > $1B
                score += 4
            else:
                score += 2
            
            # Volume factor (average daily volume)
            avg_volume = hist['Volume'].mean()
            if avg_volume > 50e6:    # > 50M
                score += 8
            elif avg_volume > 10e6:  # > 10M
                score += 6
            elif avg_volume > 5e6:   # > 5M
                score += 4
            elif avg_volume > 1e6:   # > 1M
                score += 2
            else:
                score += 1
            
            # Price momentum (30-day return)
            if len(hist) > 1:
                price_change = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
                if abs(price_change) > 20:  # High volatility
                    score += 3
                elif abs(price_change) > 10:
                    score += 2
                else:
                    score += 1
            
            # Beta (volatility relative to market)
            beta = info.get('beta', 1)
            if beta and beta > 1.5:  # High beta stocks are often popular
                score += 2
            elif beta and beta > 1.2:
                score += 1
            
            return score
            
        except Exception as e:
            print(f"Error calculating score for {symbol}: {e}")
            return 0
    
    def deduplicate_and_rank(self, stock_list):
        """Remove duplicates and rank stocks by popularity"""
        print("Ranking stocks by popularity...")
        
        # Deduplicate
        unique_stocks = {}
        for symbol, source in stock_list:
            if symbol not in unique_stocks:
                unique_stocks[symbol] = [source]
            else:
                unique_stocks[symbol].append(source)
        
        # Calculate scores
        scored_stocks = []
        total_stocks = len(unique_stocks)
        
        for i, (symbol, sources) in enumerate(unique_stocks.items()):
            print(f"Scoring {symbol}... ({i+1}/{total_stocks})", end='\r')
            
            try:
                score = self.calculate_popularity_score(symbol)
                
                # Bonus for being in multiple indices
                source_bonus = len(set(sources)) * 2
                
                # Bonus for specific sources
                if 'SP500' in sources:
                    source_bonus += 5
                if 'NASDAQ100' in sources:
                    source_bonus += 4
                if 'DOW' in sources:
                    source_bonus += 3
                if 'MOST_ACTIVE' in sources:
                    source_bonus += 3
                if 'RECENT_IPO' in sources:
                    source_bonus += 2
                
                total_score = score + source_bonus
                
                scored_stocks.append({
                    'symbol': symbol,
                    'score': total_score,
                    'sources': sources,
                    'source_count': len(set(sources))
                })
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"Error scoring {symbol}: {e}")
                continue
        
        print(f"\nCompleted scoring {len(scored_stocks)} stocks")
        
        # Sort by score
        scored_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_stocks
    
    def fetch_top_stocks(self, limit=100):
        """Main method to fetch top stocks from all sources"""
        print("Dynamic Stock Fetcher - Getting Top 100 Most Popular Stocks")
        print("=" * 70)
        
        all_stocks = []
        
        # Fetch from all sources
        all_stocks.extend(self.get_sp500_stocks())
        all_stocks.extend(self.get_nasdaq100_stocks())
        all_stocks.extend(self.get_dow_jones_stocks())
        all_stocks.extend(self.get_most_active_stocks_yahoo())
        all_stocks.extend(self.get_recent_ipos())
        all_stocks.extend(self.get_trending_stocks())
        # all_stocks.extend(self.get_etf_holdings())  # Skip for now
        
        print(f"\nCollected {len(all_stocks)} stocks from all sources")
        
        if not all_stocks:
            print("No stocks found! Using fallback list...")
            # Fallback to a curated list
            fallback_stocks = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
                'JPM', 'BAC', 'WFC', 'GS', 'V', 'MA', 'PYPL', 'SQ',
                'JNJ', 'PFE', 'UNH', 'ABBV', 'WMT', 'HD', 'PG', 'KO'
            ]
            return [{'symbol': s, 'score': 10, 'sources': ['FALLBACK'], 'source_count': 1} 
                    for s in fallback_stocks]
        
        # Deduplicate and rank
        ranked_stocks = self.deduplicate_and_rank(all_stocks)
        
        # Return top N stocks
        top_stocks = ranked_stocks[:limit]
        
        print(f"\nTop {len(top_stocks)} Most Popular Stocks:")
        print("-" * 50)
        for i, stock in enumerate(top_stocks[:20], 1):  # Show top 20
            print(f"{i:2d}. {stock['symbol']:<6} Score: {stock['score']:<3} "
                  f"Sources: {', '.join(stock['sources'])}")
        
        if len(top_stocks) > 20:
            print(f"... and {len(top_stocks) - 20} more stocks")
        
        return top_stocks
    
    def save_to_file(self, stocks, filename='top_stocks.json'):
        """Save the stock list to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(stocks, f, indent=2, default=str)
        print(f"\nSaved top stocks to {filename}")
    
    def get_stock_symbols_only(self, stocks):
        """Extract just the symbols from the stock data"""
        return [stock['symbol'] for stock in stocks]

def main():
    """Main function to demonstrate the fetcher"""
    fetcher = DynamicStockFetcher()
    
    # Fetch top 100 stocks
    top_stocks = fetcher.fetch_top_stocks(100)
    
    # Save to file
    fetcher.save_to_file(top_stocks)
    
    # Get just the symbols
    symbols = fetcher.get_stock_symbols_only(top_stocks)
    
    print(f"\nStock symbols for use in trading strategies:")
    print(symbols)
    
    return symbols

if __name__ == "__main__":
    symbols = main() 