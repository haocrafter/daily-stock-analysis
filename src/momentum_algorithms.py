import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
import time
import json
import os
from dynamic_stock_fetcher import DynamicStockFetcher
warnings.filterwarnings('ignore')

class MomentumAlgorithms:
    def __init__(self, lookback_days=252, num_stocks=100):
        self.lookback_days = lookback_days
        self.num_stocks = num_stocks
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=lookback_days + 100)
        self.stock_data = {}
        self.signals_df = None
        self.stock_fetcher = DynamicStockFetcher()
        self.popular_stocks = []
        self.output_dir = 'output'
        
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_stocks_from_file(self, filename='top_stocks.json'):
        """Load stocks from existing JSON file"""
        try:
            filepath = os.path.join(self.output_dir, filename)
            if os.path.exists(filepath):
                print(f"Loading existing stock list from {filepath}...")
                with open(filepath, 'r') as f:
                    stocks_data = json.load(f)
                
                symbols = [stock['symbol'] for stock in stocks_data[:self.num_stocks]]
                
                print(f"Loaded {len(symbols)} stocks from existing file")
                print(f"Top 10 stocks: {symbols[:10]}")
                return symbols
            else:
                print(f"No existing {filepath} found")
                return None
                
        except Exception as e:
            print(f"Error loading from {filepath}: {e}")
            return None
    
    def fetch_dynamic_stock_list(self, force_refresh=False):
        """Fetch the most popular stocks dynamically or from cache"""
        
        if not force_refresh:
            cached_stocks = self.load_stocks_from_file()
            if cached_stocks:
                self.popular_stocks = cached_stocks
                return self.popular_stocks
        
        print("Fetching fresh dynamic list of most popular stocks...")
        print("=" * 60)
        
        top_stocks_data = self.stock_fetcher.fetch_top_stocks(self.num_stocks)
        self.popular_stocks = self.stock_fetcher.get_stock_symbols_only(top_stocks_data)
        
        print(f"\nDynamic stock list ready: {len(self.popular_stocks)} stocks")
        return self.popular_stocks
    
    def fetch_stock_data(self, symbol):
        """Fetch data for a single stock"""
        try:
            data = yf.download(symbol, start=self.start_date.strftime('%Y-%m-%d'), 
                             end=self.end_date.strftime('%Y-%m-%d'), progress=False)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            
            if len(data) > 50:
                return data
            return None
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None

    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = prices.ewm(span=fast).mean()
        exp2 = prices.ewm(span=slow).mean()
        macd = exp1 - exp2
        macd_signal = macd.ewm(span=signal).mean()
        macd_histogram = macd - macd_signal
        return macd, macd_signal, macd_histogram
    
    def calculate_momentum_indicators(self, data):
        """Calculate all momentum indicators for a stock"""
        if data is None or len(data) < 50:
            return None
        
        # RSI
        data['RSI'] = self.calculate_rsi(data['Close'])
        
        # MACD
        data['MACD'], data['MACD_Signal'], data['MACD_Histogram'] = self.calculate_macd(data['Close'])
        
        # Price momentum (rate of change)
        data['ROC_5'] = data['Close'].pct_change(5) * 100
        data['ROC_10'] = data['Close'].pct_change(10) * 100
        data['ROC_20'] = data['Close'].pct_change(20) * 100
        
        # Moving averages
        data['SMA_10'] = data['Close'].rolling(window=10).mean()
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        
        # Volume momentum
        data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
        data['Volume_Momentum'] = data['Volume'] / data['Volume_SMA']
        
        # Price position relative to moving averages
        data['Price_vs_SMA10'] = (data['Close'] / data['SMA_10'] - 1) * 100
        data['Price_vs_SMA20'] = (data['Close'] / data['SMA_20'] - 1) * 100
        data['Price_vs_SMA50'] = (data['Close'] / data['SMA_50'] - 1) * 100
        data['Price_vs_SMA200'] = (data['Close'] / data['SMA_200'] - 1) * 100
        
        return data
    
    def calculate_momentum_signal_strength(self, data):
        """Calculate combined momentum signal strength"""
        if data is None or len(data) < 50:
            return None, None
        
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        buy_strength = 0.0
        sell_strength = 0.0
        
        # RSI momentum signals
        if latest['RSI'] > 60 and prev['RSI'] <= 60:
            buy_strength += 0.3
        elif latest['RSI'] > 50 and prev['RSI'] <= 50:
            buy_strength += 0.2
        elif latest['RSI'] > 55:
            buy_strength += 0.1
        
        if latest['RSI'] < 40 and prev['RSI'] >= 40:
            sell_strength += 0.3
        elif latest['RSI'] < 50 and prev['RSI'] >= 50:
            sell_strength += 0.2
        elif latest['RSI'] < 45:
            sell_strength += 0.1
        
        # MACD momentum signals
        if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
            buy_strength += 0.4
        elif latest['MACD'] > latest['MACD_Signal'] and latest['MACD_Histogram'] > 0:
            buy_strength += 0.2
        
        if latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
            sell_strength += 0.4
        elif latest['MACD'] < latest['MACD_Signal'] and latest['MACD_Histogram'] < 0:
            sell_strength += 0.2
        
        # Price momentum
        if latest['ROC_5'] > 5:
            buy_strength += 0.2
        elif latest['ROC_5'] > 2:
            buy_strength += 0.1
        elif latest['ROC_5'] < -5:
            sell_strength += 0.2
        elif latest['ROC_5'] < -2:
            sell_strength += 0.1
        
        # Moving average alignment
        ma_signals = 0
        if latest['Price_vs_SMA10'] > 0:
            ma_signals += 1
        if latest['Price_vs_SMA20'] > 0:
            ma_signals += 1
        if latest['Price_vs_SMA50'] > 0:
            ma_signals += 1
        if latest['Price_vs_SMA200'] > 0:
            ma_signals += 1
        
        if ma_signals >= 3:
            buy_strength += 0.3
        elif ma_signals >= 2:
            buy_strength += 0.1
        
        if ma_signals <= 1:
            sell_strength += 0.3
        elif ma_signals <= 2:
            sell_strength += 0.1
        
        # Volume confirmation
        if latest['Volume_Momentum'] > 1.5:
            if latest['ROC_5'] > 0:
                buy_strength += 0.1
            else:
                sell_strength += 0.1
        
        return min(buy_strength, 1.0), min(sell_strength, 1.0)
    
    def analyze_all_stocks(self):
        """Analyze all stocks and generate momentum signals"""
        if not self.popular_stocks:
            self.fetch_dynamic_stock_list()
        
        print(f"\nAnalyzing {len(self.popular_stocks)} stocks for momentum signals...")
        print("=" * 80)
        
        results = []
        processed = 0
        
        for symbol in self.popular_stocks:
            print(f"Processing {symbol}... ({processed + 1}/{len(self.popular_stocks)})", end='\r')
            
            data = self.fetch_stock_data(symbol)
            if data is None:
                continue
            
            data = self.calculate_momentum_indicators(data)
            if data is None:
                continue
            
            buy_strength, sell_strength = self.calculate_momentum_signal_strength(data)
            if buy_strength is None:
                continue
            
            self.stock_data[symbol] = data
            latest = data.iloc[-1]
            
            results.append({
                'Symbol': symbol,
                'Current_Price': latest['Close'],
                'Momentum_Buy_Signal': buy_strength,
                'Momentum_Sell_Signal': sell_strength,
                'RSI': latest['RSI'],
                'MACD': latest['MACD'],
                'MACD_Signal': latest['MACD_Signal'],
                'MACD_Histogram': latest['MACD_Histogram'],
                'ROC_5': latest['ROC_5'],
                'ROC_20': latest['ROC_20'],
                'Price_vs_SMA10': latest['Price_vs_SMA10'],
                'Price_vs_SMA20': latest['Price_vs_SMA20'],
                'Price_vs_SMA50': latest['Price_vs_SMA50'],
                'Volume_Momentum': latest['Volume_Momentum']
            })
            
            processed += 1
            time.sleep(0.02)
        
        print(f"\nCompleted momentum analysis of {processed} stocks")
        
        self.signals_df = pd.DataFrame(results)
        return self.signals_df
    
    def get_top_momentum_signals(self, top_n=15):
        """Get top N momentum buy and sell signals"""
        if self.signals_df is None:
            return None, None
        
        top_momentum_buys = self.signals_df.nlargest(top_n, 'Momentum_Buy_Signal')
        top_momentum_sells = self.signals_df.nlargest(top_n, 'Momentum_Sell_Signal')
        
        return top_momentum_buys, top_momentum_sells
    
    def run_momentum_analysis(self, force_refresh_stocks=False):
        """Run the complete momentum analysis"""
        print("Momentum-Based Stock Analysis")
        print("=" * 60)
        
        self.fetch_dynamic_stock_list(force_refresh=force_refresh_stocks)
        signals_df = self.analyze_all_stocks()
        
        if signals_df is None or len(signals_df) == 0:
            print("No valid momentum signals found!")
            return
        
        top_momentum_buys, top_momentum_sells = self.get_top_momentum_signals(15)
        
        print("\nTOP 15 MOMENTUM BUY SIGNALS (Strong Upward Momentum)")
        print("=" * 90)
        print(top_momentum_buys[['Symbol', 'Current_Price', 'Momentum_Buy_Signal', 'RSI', 
                                'MACD', 'ROC_5', 'ROC_20', 'Price_vs_SMA20']].round(2).to_string(index=False))
        
        print("\nTOP 15 MOMENTUM SELL SIGNALS (Strong Downward Momentum)")
        print("=" * 90)
        print(top_momentum_sells[['Symbol', 'Current_Price', 'Momentum_Sell_Signal', 'RSI', 
                                 'MACD', 'ROC_5', 'ROC_20', 'Price_vs_SMA20']].round(2).to_string(index=False))
        
        # Save results
        momentum_buy_signals_path = os.path.join(self.output_dir, 'top_momentum_buy_signals.csv')
        momentum_sell_signals_path = os.path.join(self.output_dir, 'top_momentum_sell_signals.csv')
        
        top_momentum_buys.to_csv(momentum_buy_signals_path, index=False)
        top_momentum_sells.to_csv(momentum_sell_signals_path, index=False)
        
        print("\nMomentum analysis results saved to:")
        print(f"- {momentum_buy_signals_path}")
        print(f"- {momentum_sell_signals_path}")
        
        return top_momentum_buys, top_momentum_sells

def main():
    """Main function for momentum analysis"""
    import sys
    
    force_refresh = '--refresh' in sys.argv
    
    if force_refresh:
        print("🔄 Force refresh mode: Will fetch fresh stock list from all sources")
    else:
        print("📂 Cache mode: Will use existing top_stocks.json if available")
    
    analyzer = MomentumAlgorithms(lookback_days=252, num_stocks=100)
    top_momentum_buys, top_momentum_sells = analyzer.run_momentum_analysis(force_refresh_stocks=force_refresh)
    
    print("\nMomentum analysis complete!")
    print("✅ Analyzed momentum signals across multiple strategies")
    print("✅ Saved results to files")
    
    print("\n💡 Tip: Use 'python momentum_algorithms.py --refresh' to force fetch fresh stocks")

if __name__ == "__main__":
    main() 