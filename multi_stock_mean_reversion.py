import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
import time
warnings.filterwarnings('ignore')

class MultiStockMeanReversion:
    def __init__(self, lookback_days=252):
        self.lookback_days = lookback_days
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=lookback_days + 50)  # Extra days for indicators
        self.stock_data = {}
        self.signals_df = None
        
        # Top 100 popular stocks
        self.popular_stocks = [
            # Technology
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'ADBE', 'CRM',
            'ORCL', 'IBM', 'INTC', 'AMD', 'AVGO', 'QCOM', 'TXN', 'NOW', 'SNOW', 'PLTR',
            
            # Financial
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'COF', 'AXP',
            'BRK-B', 'BLK', 'SPGI', 'ICE', 'CME', 'MCO', 'NDAQ', 'SCHW', 'TROW', 'BEN',
            
            # Healthcare
            'JNJ', 'PFE', 'UNH', 'ABBV', 'BMY', 'MRK', 'TMO', 'ABT', 'DHR', 'SYK',
            'MDT', 'GILD', 'AMGN', 'REGN', 'ISRG', 'ZTS', 'BSX', 'EW', 'IDXX', 'IQV',
            
            # Consumer
            'WMT', 'HD', 'PG', 'KO', 'PEP', 'COST', 'TGT', 'LOW', 'SBUX', 'MCD',
            'NKE', 'DIS', 'NFLX', 'PYPL', 'V', 'MA', 'AMZN', 'EBAY', 'ETSY', 'SHOP',
            
            # Industrial & Energy
            'XOM', 'CVX', 'COP', 'EOG', 'OXY', 'SLB', 'MPC', 'VLO', 'PSX', 'KMI',
            'CAT', 'DE', 'BA', 'GE', 'HON', 'MMM', 'RTX', 'LMT', 'NOC', 'GD',
            
            # Others
            'BRK-A', 'TSM', 'ASML', 'UNP', 'NEE', 'SO', 'DUK', 'AEP', 'EXC', 'XEL'
        ]
    
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
        
        return data
    
    def calculate_signal_strength(self, data):
        """Calculate signal strength for mean reversion"""
        if data is None or len(data) < 50:
            return None, None
        
        latest = data.iloc[-1]
        
        # Buy signal components (oversold conditions)
        buy_signals = []
        
        # Bollinger Bands: Price below lower band
        if latest['Close'] <= latest['Lower_Band']:
            buy_signals.append(1.0)
        elif latest['BB_Position'] < 0.2:
            buy_signals.append(0.5)
        else:
            buy_signals.append(0.0)
        
        # RSI: Oversold
        if latest['RSI'] <= 25:
            buy_signals.append(1.0)
        elif latest['RSI'] <= 35:
            buy_signals.append(0.7)
        elif latest['RSI'] <= 45:
            buy_signals.append(0.3)
        else:
            buy_signals.append(0.0)
        
        # Z-Score: Significantly undervalued
        if latest['Z_Score'] <= -2.5:
            buy_signals.append(1.0)
        elif latest['Z_Score'] <= -1.5:
            buy_signals.append(0.7)
        elif latest['Z_Score'] <= -1.0:
            buy_signals.append(0.3)
        else:
            buy_signals.append(0.0)
        
        # Volume confirmation
        if latest['Volume_Ratio'] > 1.5:
            buy_signals.append(0.5)
        elif latest['Volume_Ratio'] > 1.2:
            buy_signals.append(0.3)
        else:
            buy_signals.append(0.0)
        
        # Recent decline (momentum)
        if latest['Price_Change_5d'] < -0.05:  # 5% decline
            buy_signals.append(0.5)
        elif latest['Price_Change_5d'] < -0.02:
            buy_signals.append(0.3)
        else:
            buy_signals.append(0.0)
        
        # Sell signal components (overbought conditions)
        sell_signals = []
        
        # Bollinger Bands: Price above upper band
        if latest['Close'] >= latest['Upper_Band']:
            sell_signals.append(1.0)
        elif latest['BB_Position'] > 0.8:
            sell_signals.append(0.5)
        else:
            sell_signals.append(0.0)
        
        # RSI: Overbought
        if latest['RSI'] >= 75:
            sell_signals.append(1.0)
        elif latest['RSI'] >= 65:
            sell_signals.append(0.7)
        elif latest['RSI'] >= 55:
            sell_signals.append(0.3)
        else:
            sell_signals.append(0.0)
        
        # Z-Score: Significantly overvalued
        if latest['Z_Score'] >= 2.5:
            sell_signals.append(1.0)
        elif latest['Z_Score'] >= 1.5:
            sell_signals.append(0.7)
        elif latest['Z_Score'] >= 1.0:
            sell_signals.append(0.3)
        else:
            sell_signals.append(0.0)
        
        # Volume confirmation
        if latest['Volume_Ratio'] > 1.5:
            sell_signals.append(0.5)
        elif latest['Volume_Ratio'] > 1.2:
            sell_signals.append(0.3)
        else:
            sell_signals.append(0.0)
        
        # Recent gain (momentum)
        if latest['Price_Change_5d'] > 0.05:  # 5% gain
            sell_signals.append(0.5)
        elif latest['Price_Change_5d'] > 0.02:
            sell_signals.append(0.3)
        else:
            sell_signals.append(0.0)
        
        # Calculate weighted signal strength
        buy_strength = np.mean(buy_signals)
        sell_strength = np.mean(sell_signals)
        
        return buy_strength, sell_strength
    
    def analyze_all_stocks(self):
        """Analyze all stocks and generate signals"""
        print("Analyzing 100 popular stocks for mean reversion signals...")
        print("=" * 60)
        
        results = []
        processed = 0
        
        for symbol in self.popular_stocks:
            print(f"Processing {symbol}... ({processed + 1}/100)", end='\r')
            
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
                'Price_Change_20d': latest['Price_Change_20d'] * 100
            })
            
            processed += 1
            time.sleep(0.01)  # Small delay to avoid rate limiting
        
        print(f"\nCompleted analysis of {processed} stocks")
        
        # Create DataFrame with results
        self.signals_df = pd.DataFrame(results)
        return self.signals_df
    
    def get_top_signals(self):
        """Get top 10 buy and sell signals"""
        if self.signals_df is None:
            return None, None
        
        # Sort by signal strength
        top_buys = self.signals_df.nlargest(10, 'Buy_Signal_Strength')
        top_sells = self.signals_df.nlargest(10, 'Sell_Signal_Strength')
        
        return top_buys, top_sells
    
    def plot_signals(self, top_buys, top_sells):
        """Plot the top buy and sell signals"""
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        
        # Plot 1: Top 10 Buy Signals - Price Charts
        ax1 = axes[0, 0]
        for symbol in top_buys['Symbol'].head(10):
            if symbol in self.stock_data:
                data = self.stock_data[symbol].tail(60)  # Last 60 days
                normalized_price = (data['Close'] / data['Close'].iloc[0] - 1) * 100
                ax1.plot(data.index, normalized_price, label=symbol, alpha=0.7)
        
        ax1.set_title('Top 10 Buy Signals - Price Performance (Last 60 Days)', fontsize=14)
        ax1.set_ylabel('Price Change (%)')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Top 10 Sell Signals - Price Charts
        ax2 = axes[0, 1]
        for symbol in top_sells['Symbol'].head(10):
            if symbol in self.stock_data:
                data = self.stock_data[symbol].tail(60)
                normalized_price = (data['Close'] / data['Close'].iloc[0] - 1) * 100
                ax2.plot(data.index, normalized_price, label=symbol, alpha=0.7)
        
        ax2.set_title('Top 10 Sell Signals - Price Performance (Last 60 Days)', fontsize=14)
        ax2.set_ylabel('Price Change (%)')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Signal Strength Distribution
        ax3 = axes[1, 0]
        ax3.bar(range(len(top_buys)), top_buys['Buy_Signal_Strength'], 
                color='green', alpha=0.7, label='Buy Signal Strength')
        ax3.set_title('Top 10 Buy Signal Strengths', fontsize=14)
        ax3.set_ylabel('Signal Strength')
        ax3.set_xticks(range(len(top_buys)))
        ax3.set_xticklabels(top_buys['Symbol'], rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Sell Signal Strength Distribution
        ax4 = axes[1, 1]
        ax4.bar(range(len(top_sells)), top_sells['Sell_Signal_Strength'], 
                color='red', alpha=0.7, label='Sell Signal Strength')
        ax4.set_title('Top 10 Sell Signal Strengths', fontsize=14)
        ax4.set_ylabel('Signal Strength')
        ax4.set_xticks(range(len(top_sells)))
        ax4.set_xticklabels(top_sells['Symbol'], rotation=45)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('multi_stock_mean_reversion_signals.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_detailed_analysis(self, symbols, signal_type='buy'):
        """Plot detailed technical analysis for specific stocks"""
        n_stocks = len(symbols)
        fig, axes = plt.subplots(n_stocks, 4, figsize=(20, 5 * n_stocks))
        
        if n_stocks == 1:
            axes = axes.reshape(1, -1)
        
        for i, symbol in enumerate(symbols):
            if symbol not in self.stock_data:
                continue
                
            data = self.stock_data[symbol].tail(120)  # Last 120 days
            
            # Price and Bollinger Bands
            ax1 = axes[i, 0]
            ax1.plot(data.index, data['Close'], label='Close Price', linewidth=2)
            ax1.plot(data.index, data['SMA_20'], label='SMA(20)', alpha=0.7)
            ax1.fill_between(data.index, data['Lower_Band'], data['Upper_Band'], 
                           alpha=0.2, label='Bollinger Bands')
            ax1.set_title(f'{symbol} - Price & Bollinger Bands')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # RSI
            ax2 = axes[i, 1]
            ax2.plot(data.index, data['RSI'], color='purple', linewidth=2)
            ax2.axhline(y=70, color='r', linestyle='--', alpha=0.7)
            ax2.axhline(y=30, color='g', linestyle='--', alpha=0.7)
            ax2.set_title(f'{symbol} - RSI')
            ax2.set_ylabel('RSI')
            ax2.grid(True, alpha=0.3)
            
            # Z-Score
            ax3 = axes[i, 2]
            ax3.plot(data.index, data['Z_Score'], color='orange', linewidth=2)
            ax3.axhline(y=2, color='r', linestyle='--', alpha=0.7)
            ax3.axhline(y=-2, color='g', linestyle='--', alpha=0.7)
            ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            ax3.set_title(f'{symbol} - Z-Score')
            ax3.set_ylabel('Z-Score')
            ax3.grid(True, alpha=0.3)
            
            # Volume
            ax4 = axes[i, 3]
            ax4.bar(data.index, data['Volume'], alpha=0.6)
            ax4.plot(data.index, data['Volume_SMA'], color='red', linewidth=2, label='Volume SMA')
            ax4.set_title(f'{symbol} - Volume')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'detailed_{signal_type}_signals.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def run_analysis(self):
        """Run the complete multi-stock analysis"""
        print("Multi-Stock Mean Reversion Analysis")
        print("=" * 60)
        
        # Analyze all stocks
        signals_df = self.analyze_all_stocks()
        
        if signals_df is None or len(signals_df) == 0:
            print("No valid signals found!")
            return
        
        # Get top signals
        top_buys, top_sells = self.get_top_signals()
        
        # Display results
        print("\nTOP 10 BUY SIGNALS (Strong Mean Reversion - Oversold)")
        print("=" * 80)
        print(top_buys[['Symbol', 'Current_Price', 'Buy_Signal_Strength', 'RSI', 
                       'Z_Score', 'Price_Change_5d']].to_string(index=False))
        
        print("\nTOP 10 SELL SIGNALS (Strong Mean Reversion - Overbought)")
        print("=" * 80)
        print(top_sells[['Symbol', 'Current_Price', 'Sell_Signal_Strength', 'RSI', 
                        'Z_Score', 'Price_Change_5d']].to_string(index=False))
        
        # Plot overview
        self.plot_signals(top_buys, top_sells)
        
        # Plot detailed analysis for top 5 of each
        print("\nGenerating detailed analysis for top 5 buy signals...")
        self.plot_detailed_analysis(top_buys['Symbol'].head(5).tolist(), 'buy')
        
        print("Generating detailed analysis for top 5 sell signals...")
        self.plot_detailed_analysis(top_sells['Symbol'].head(5).tolist(), 'sell')
        
        return top_buys, top_sells

def main():
    """Main function"""
    analyzer = MultiStockMeanReversion(lookback_days=252)
    top_buys, top_sells = analyzer.run_analysis()
    
    print("\nAnalysis complete! Check the generated plots:")
    print("1. multi_stock_mean_reversion_signals.png - Overview of top signals")
    print("2. detailed_buy_signals.png - Detailed analysis of top buy signals")
    print("3. detailed_sell_signals.png - Detailed analysis of top sell signals")

if __name__ == "__main__":
    main() 