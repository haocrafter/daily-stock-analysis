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

class DynamicMultiStockMeanReversion:
    def __init__(self, lookback_days=252, num_stocks=100):
        self.lookback_days = lookback_days
        self.num_stocks = num_stocks
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=lookback_days + 50)  # Extra days for indicators
        self.stock_data = {}
        self.signals_df = None
        self.stock_fetcher = DynamicStockFetcher()
        self.popular_stocks = []
        self.output_dir = 'output'
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_stocks_from_file(self, filename='top_stocks.json'):
        """Load stocks from existing JSON file"""
        try:
            filepath = os.path.join(self.output_dir, filename)
            if os.path.exists(filepath):
                print(f"Loading existing stock list from {filepath}...")
                with open(filepath, 'r') as f:
                    stocks_data = json.load(f)
                
                # Extract symbols from the loaded data
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
        
        # First try to load from existing file unless force refresh
        if not force_refresh:
            cached_stocks = self.load_stocks_from_file()
            if cached_stocks:
                self.popular_stocks = cached_stocks
                return self.popular_stocks
        
        print("Fetching fresh dynamic list of most popular stocks...")
        print("=" * 60)
        
        # Get top stocks from dynamic fetcher
        top_stocks_data = self.stock_fetcher.fetch_top_stocks(self.num_stocks)
        
        # Extract just the symbols
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
            
            if len(data) > 50:  # Ensure we have enough data
                return data
            return None
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def calculate_indicators(self, data):
        """Calculate technical indicators for a stock"""
        if data is None or len(data) < 50:
            return None
        
        # Bollinger Bands
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['STD_20'] = data['Close'].rolling(window=20).std()
        data['Upper_Band'] = data['SMA_20'] + (data['STD_20'] * 2)
        data['Lower_Band'] = data['SMA_20'] - (data['STD_20'] * 2)
        data['BB_Position'] = (data['Close'] - data['Lower_Band']) / (data['Upper_Band'] - data['Lower_Band'])
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # Z-Score
        data['Price_Mean'] = data['Close'].rolling(window=20).mean()
        data['Price_Std'] = data['Close'].rolling(window=20).std()
        data['Z_Score'] = (data['Close'] - data['Price_Mean']) / data['Price_Std']
        
        # Volume indicators
        data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
        data['Volume_Ratio'] = data['Volume'] / data['Volume_SMA']
        
        # Price momentum
        data['Price_Change_5d'] = data['Close'].pct_change(5)
        data['Price_Change_20d'] = data['Close'].pct_change(20)
        
        # Additional indicators for enhanced scoring
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        data['Price_vs_SMA50'] = (data['Close'] / data['SMA_50'] - 1) * 100
        data['Price_vs_SMA200'] = (data['Close'] / data['SMA_200'] - 1) * 100
        
        return data
    
    def calculate_signal_strength(self, data):
        """Calculate signal strength for mean reversion with enhanced scoring"""
        if data is None or len(data) < 50:
            return None, None
        
        latest = data.iloc[-1]
        
        # Buy signal components (oversold conditions)
        buy_signals = []
        
        # Bollinger Bands: Price below lower band
        if latest['Close'] <= latest['Lower_Band']:
            buy_signals.append(1.0)
        elif latest['BB_Position'] < 0.2:
            buy_signals.append(0.6)
        elif latest['BB_Position'] < 0.3:
            buy_signals.append(0.3)
        else:
            buy_signals.append(0.0)
        
        # RSI: Oversold
        if latest['RSI'] <= 20:
            buy_signals.append(1.0)
        elif latest['RSI'] <= 30:
            buy_signals.append(0.8)
        elif latest['RSI'] <= 40:
            buy_signals.append(0.4)
        else:
            buy_signals.append(0.0)
        
        # Z-Score: Significantly undervalued
        if latest['Z_Score'] <= -2.5:
            buy_signals.append(1.0)
        elif latest['Z_Score'] <= -2.0:
            buy_signals.append(0.8)
        elif latest['Z_Score'] <= -1.5:
            buy_signals.append(0.6)
        elif latest['Z_Score'] <= -1.0:
            buy_signals.append(0.3)
        else:
            buy_signals.append(0.0)
        
        # Volume confirmation
        if latest['Volume_Ratio'] > 2.0:
            buy_signals.append(0.6)
        elif latest['Volume_Ratio'] > 1.5:
            buy_signals.append(0.4)
        elif latest['Volume_Ratio'] > 1.2:
            buy_signals.append(0.2)
        else:
            buy_signals.append(0.0)
        
        # Recent decline (momentum)
        if latest['Price_Change_5d'] < -0.10:  # 10% decline
            buy_signals.append(0.8)
        elif latest['Price_Change_5d'] < -0.05:  # 5% decline
            buy_signals.append(0.5)
        elif latest['Price_Change_5d'] < -0.02:
            buy_signals.append(0.3)
        else:
            buy_signals.append(0.0)
        
        # Long-term trend support
        if latest['Price_vs_SMA200'] > -10 and latest['Price_vs_SMA50'] < -5:
            buy_signals.append(0.3)  # Near long-term support but short-term oversold
        else:
            buy_signals.append(0.0)
        
        # Sell signal components (overbought conditions)
        sell_signals = []
        
        # Bollinger Bands: Price above upper band
        if latest['Close'] >= latest['Upper_Band']:
            sell_signals.append(1.0)
        elif latest['BB_Position'] > 0.8:
            sell_signals.append(0.6)
        elif latest['BB_Position'] > 0.7:
            sell_signals.append(0.3)
        else:
            sell_signals.append(0.0)
        
        # RSI: Overbought
        if latest['RSI'] >= 80:
            sell_signals.append(1.0)
        elif latest['RSI'] >= 70:
            sell_signals.append(0.8)
        elif latest['RSI'] >= 60:
            sell_signals.append(0.4)
        else:
            sell_signals.append(0.0)
        
        # Z-Score: Significantly overvalued
        if latest['Z_Score'] >= 2.5:
            sell_signals.append(1.0)
        elif latest['Z_Score'] >= 2.0:
            sell_signals.append(0.8)
        elif latest['Z_Score'] >= 1.5:
            sell_signals.append(0.6)
        elif latest['Z_Score'] >= 1.0:
            sell_signals.append(0.3)
        else:
            sell_signals.append(0.0)
        
        # Volume confirmation
        if latest['Volume_Ratio'] > 2.0:
            sell_signals.append(0.6)
        elif latest['Volume_Ratio'] > 1.5:
            sell_signals.append(0.4)
        elif latest['Volume_Ratio'] > 1.2:
            sell_signals.append(0.2)
        else:
            sell_signals.append(0.0)
        
        # Recent gain (momentum)
        if latest['Price_Change_5d'] > 0.10:  # 10% gain
            sell_signals.append(0.8)
        elif latest['Price_Change_5d'] > 0.05:  # 5% gain
            sell_signals.append(0.5)
        elif latest['Price_Change_5d'] > 0.02:
            sell_signals.append(0.3)
        else:
            sell_signals.append(0.0)
        
        # Long-term trend resistance
        if latest['Price_vs_SMA200'] < 10 and latest['Price_vs_SMA50'] > 5:
            sell_signals.append(0.3)  # Near long-term resistance but short-term overbought
        else:
            sell_signals.append(0.0)
        
        # Calculate weighted signal strength
        buy_strength = np.mean(buy_signals)
        sell_strength = np.mean(sell_signals)
        
        return buy_strength, sell_strength
    
    def analyze_all_stocks(self):
        """Analyze all stocks and generate signals"""
        if not self.popular_stocks:
            self.fetch_dynamic_stock_list()
        
        print(f"\nAnalyzing {len(self.popular_stocks)} dynamically fetched stocks for mean reversion signals...")
        print("=" * 80)
        
        results = []
        processed = 0
        
        for symbol in self.popular_stocks:
            print(f"Processing {symbol}... ({processed + 1}/{len(self.popular_stocks)})", end='\r')
            
            # Fetch data
            data = self.fetch_stock_data(symbol)
            if data is None:
                continue
            
            # Calculate indicators
            data = self.calculate_indicators(data)
            if data is None:
                continue
            
            # Calculate signal strength
            buy_strength, sell_strength = self.calculate_signal_strength(data)
            if buy_strength is None:
                continue
            
            # Store data for later plotting
            self.stock_data[symbol] = data
            
            # Get latest metrics
            latest = data.iloc[-1]
            
            results.append({
                'Symbol': symbol,
                'Current_Price': latest['Close'],
                'Buy_Signal_Strength': buy_strength,
                'Sell_Signal_Strength': sell_strength,
                'RSI': latest['RSI'],
                'Z_Score': latest['Z_Score'],
                'BB_Position': latest['BB_Position'],
                'Volume_Ratio': latest['Volume_Ratio'],
                'Price_Change_5d': latest['Price_Change_5d'] * 100,
                'Price_Change_20d': latest['Price_Change_20d'] * 100,
                'Price_vs_SMA50': latest['Price_vs_SMA50'],
                'Price_vs_SMA200': latest['Price_vs_SMA200']
            })
            
            processed += 1
            time.sleep(0.02)  # Small delay to avoid rate limiting
        
        print(f"\nCompleted analysis of {processed} stocks")
        
        # Create DataFrame with results
        self.signals_df = pd.DataFrame(results)
        return self.signals_df
    
    def get_top_signals(self, top_n=15):
        """Get top N buy and sell signals"""
        if self.signals_df is None:
            return None, None
        
        # Sort by signal strength
        top_buys = self.signals_df.nlargest(top_n, 'Buy_Signal_Strength')
        top_sells = self.signals_df.nlargest(top_n, 'Sell_Signal_Strength')
        
        return top_buys, top_sells
    
    def plot_signals(self, top_buys, top_sells):
        """Plot the top buy and sell signals"""
        fig, axes = plt.subplots(2, 3, figsize=(24, 16))
        
        # Plot 1: Top Buy Signals - Price Charts
        ax1 = axes[0, 0]
        for symbol in top_buys['Symbol'].head(10):
            if symbol in self.stock_data:
                data = self.stock_data[symbol].tail(60)  # Last 60 days
                normalized_price = (data['Close'] / data['Close'].iloc[0] - 1) * 100
                ax1.plot(data.index, normalized_price, label=symbol, alpha=0.7, linewidth=2)
        
        ax1.set_title('Top 10 Buy Signals - Price Performance (Last 60 Days)', fontsize=14)
        ax1.set_ylabel('Price Change (%)')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Top Sell Signals - Price Charts
        ax2 = axes[0, 1]
        for symbol in top_sells['Symbol'].head(10):
            if symbol in self.stock_data:
                data = self.stock_data[symbol].tail(60)
                normalized_price = (data['Close'] / data['Close'].iloc[0] - 1) * 100
                ax2.plot(data.index, normalized_price, label=symbol, alpha=0.7, linewidth=2)
        
        ax2.set_title('Top 10 Sell Signals - Price Performance (Last 60 Days)', fontsize=14)
        ax2.set_ylabel('Price Change (%)')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Buy Signal Strength Distribution
        ax3 = axes[0, 2]
        bars = ax3.bar(range(len(top_buys.head(10))), top_buys['Buy_Signal_Strength'].head(10), 
                      color='green', alpha=0.7)
        ax3.set_title('Top 10 Buy Signal Strengths', fontsize=14)
        ax3.set_ylabel('Signal Strength')
        ax3.set_xticks(range(len(top_buys.head(10))))
        ax3.set_xticklabels(top_buys['Symbol'].head(10), rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, top_buys['Buy_Signal_Strength'].head(10)):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{value:.2f}', ha='center', va='bottom', fontsize=10)
        
        # Plot 4: Sell Signal Strength Distribution
        ax4 = axes[1, 0]
        bars = ax4.bar(range(len(top_sells.head(10))), top_sells['Sell_Signal_Strength'].head(10), 
                      color='red', alpha=0.7)
        ax4.set_title('Top 10 Sell Signal Strengths', fontsize=14)
        ax4.set_ylabel('Signal Strength')
        ax4.set_xticks(range(len(top_sells.head(10))))
        ax4.set_xticklabels(top_sells['Symbol'].head(10), rotation=45)
        ax4.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, top_sells['Sell_Signal_Strength'].head(10)):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{value:.2f}', ha='center', va='bottom', fontsize=10)
        
        # Plot 5: RSI vs Z-Score scatter for Buy signals
        ax5 = axes[1, 1]
        scatter = ax5.scatter(top_buys['RSI'].head(15), top_buys['Z_Score'].head(15), 
                             c=top_buys['Buy_Signal_Strength'].head(15), 
                             s=100, alpha=0.7, cmap='RdYlGn_r')
        ax5.set_title('Buy Signals: RSI vs Z-Score', fontsize=14)
        ax5.set_xlabel('RSI')
        ax5.set_ylabel('Z-Score')
        ax5.axhline(y=-2, color='g', linestyle='--', alpha=0.5, label='Z-Score -2')
        ax5.axvline(x=30, color='g', linestyle='--', alpha=0.5, label='RSI 30')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax5, label='Buy Signal Strength')
        
        # Plot 6: RSI vs Z-Score scatter for Sell signals
        ax6 = axes[1, 2]
        scatter = ax6.scatter(top_sells['RSI'].head(15), top_sells['Z_Score'].head(15), 
                             c=top_sells['Sell_Signal_Strength'].head(15), 
                             s=100, alpha=0.7, cmap='RdYlGn')
        ax6.set_title('Sell Signals: RSI vs Z-Score', fontsize=14)
        ax6.set_xlabel('RSI')
        ax6.set_ylabel('Z-Score')
        ax6.axhline(y=2, color='r', linestyle='--', alpha=0.5, label='Z-Score +2')
        ax6.axvline(x=70, color='r', linestyle='--', alpha=0.5, label='RSI 70')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax6, label='Sell Signal Strength')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'dynamic_multi_stock_signals.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def run_analysis(self, force_refresh_stocks=False):
        """Run the complete dynamic multi-stock analysis"""
        print("Dynamic Multi-Stock Mean Reversion Analysis")
        print("=" * 60)
        
        # Fetch dynamic stock list first (will use cache if available)
        self.fetch_dynamic_stock_list(force_refresh=force_refresh_stocks)
        
        # Analyze all stocks
        signals_df = self.analyze_all_stocks()
        
        if signals_df is None or len(signals_df) == 0:
            print("No valid signals found!")
            return
        
        # Get top signals
        top_buys, top_sells = self.get_top_signals(15)
        
        # Display results
        print("\nTOP 15 BUY SIGNALS (Strong Mean Reversion - Oversold)")
        print("=" * 90)
        print(top_buys[['Symbol', 'Current_Price', 'Buy_Signal_Strength', 'RSI', 
                       'Z_Score', 'Price_Change_5d', 'Price_vs_SMA50']].round(2).to_string(index=False))
        
        print("\nTOP 15 SELL SIGNALS (Strong Mean Reversion - Overbought)")
        print("=" * 90)
        print(top_sells[['Symbol', 'Current_Price', 'Sell_Signal_Strength', 'RSI', 
                        'Z_Score', 'Price_Change_5d', 'Price_vs_SMA50']].round(2).to_string(index=False))
        
        # Plot overview
        self.plot_signals(top_buys, top_sells)
        
        # Save results to CSV
        buy_signals_path = os.path.join(self.output_dir, 'top_buy_signals.csv')
        sell_signals_path = os.path.join(self.output_dir, 'top_sell_signals.csv')
        charts_path = os.path.join(self.output_dir, 'dynamic_multi_stock_signals.png')
        
        top_buys.to_csv(buy_signals_path, index=False)
        top_sells.to_csv(sell_signals_path, index=False)
        
        print("\nResults saved to output files:")
        print(f"- {buy_signals_path}")
        print(f"- {sell_signals_path}")
        print(f"- {charts_path}")
        
        return top_buys, top_sells

def main():
    """Main function"""
    import sys
    
    # Check command line argument for force refresh
    force_refresh = '--refresh' in sys.argv
    
    if force_refresh:
        print("🔄 Force refresh mode: Will fetch fresh stock list from all sources")
    else:
        print("📂 Cache mode: Will use existing top_stocks.json if available")
    
    analyzer = DynamicMultiStockMeanReversion(lookback_days=252, num_stocks=100)
    top_buys, top_sells = analyzer.run_analysis(force_refresh_stocks=force_refresh)
    
    print("\nDynamic analysis complete!")
    if force_refresh:
        print("✅ Fetched fresh stock list from multiple sources")
    else:
        print("✅ Used cached/dynamic stock list efficiently")
    print("✅ Analyzed mean reversion signals")
    print("✅ Generated comprehensive visualizations")
    print("✅ Saved results to files")
    
    print("\n💡 Tip: Use 'python multi_stock_mean_reversion_dynamic.py --refresh' to force fetch fresh stocks")

if __name__ == "__main__":
    main() 