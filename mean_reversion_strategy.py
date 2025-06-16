import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MeanReversionStrategy:
    def __init__(self, symbol, start_date, end_date, initial_capital=10000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.data = None
        self.signals = None
        self.portfolio = None
        
    def fetch_data(self):
        """Fetch stock data from Yahoo Finance"""
        print(f"Fetching data for {self.symbol}...")
        self.data = yf.download(self.symbol, start=self.start_date, end=self.end_date, progress=False)
        # Flatten column names if MultiIndex
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = self.data.columns.droplevel(1)
        return self.data
    
    def calculate_bollinger_bands(self, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        close_prices = self.data['Close']
        self.data['SMA'] = close_prices.rolling(window=window).mean()
        self.data['STD'] = close_prices.rolling(window=window).std()
        self.data['Upper_Band'] = self.data['SMA'] + (self.data['STD'] * num_std)
        self.data['Lower_Band'] = self.data['SMA'] - (self.data['STD'] * num_std)
        self.data['BB_Width'] = self.data['Upper_Band'] - self.data['Lower_Band']
        self.data['BB_Position'] = (close_prices - self.data['Lower_Band']) / self.data['BB_Width']
        
    def calculate_rsi(self, window=14):
        """Calculate Relative Strength Index (RSI)"""
        close_prices = self.data['Close']
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        
    def calculate_z_score(self, window=20):
        """Calculate Z-Score for mean reversion"""
        close_prices = self.data['Close']
        self.data['Price_Mean'] = close_prices.rolling(window=window).mean()
        self.data['Price_Std'] = close_prices.rolling(window=window).std()
        self.data['Z_Score'] = (close_prices - self.data['Price_Mean']) / self.data['Price_Std']
        
    def calculate_volume_indicator(self):
        """Calculate volume-based indicators"""
        self.data['Volume_SMA'] = self.data['Volume'].rolling(window=20).mean()
        self.data['Volume_Ratio'] = self.data['Volume'] / self.data['Volume_SMA']
        
    def generate_signals(self, strategy='combined'):
        """Generate trading signals based on strategy"""
        self.signals = pd.DataFrame(index=self.data.index)
        self.signals['Price'] = self.data['Close']
        
        if strategy == 'bollinger':
            # Bollinger Bands Strategy
            self.signals['Signal'] = 0
            self.signals['Signal'][self.data['Close'] <= self.data['Lower_Band']] = 1  # Buy
            self.signals['Signal'][self.data['Close'] >= self.data['Upper_Band']] = -1  # Sell
            
        elif strategy == 'rsi':
            # RSI Strategy
            self.signals['Signal'] = 0
            self.signals['Signal'][self.data['RSI'] <= 30] = 1  # Buy (oversold)
            self.signals['Signal'][self.data['RSI'] >= 70] = -1  # Sell (overbought)
            
        elif strategy == 'zscore':
            # Z-Score Strategy
            self.signals['Signal'] = 0
            self.signals['Signal'][self.data['Z_Score'] <= -2] = 1  # Buy (undervalued)
            self.signals['Signal'][self.data['Z_Score'] >= 2] = -1  # Sell (overvalued)
            
        elif strategy == 'combined':
            # Combined Strategy
            self.signals['Signal'] = 0
            
            # Buy conditions (all must be true)
            buy_condition = (
                (self.data['Close'] <= self.data['Lower_Band']) &
                (self.data['RSI'] <= 35) &
                (self.data['Z_Score'] <= -1.5) &
                (self.data['Volume_Ratio'] > 1.2)  # Higher volume confirmation
            )
            
            # Sell conditions (any can be true)
            sell_condition = (
                (self.data['Close'] >= self.data['Upper_Band']) |
                (self.data['RSI'] >= 65) |
                (self.data['Z_Score'] >= 1.5)
            )
            
            self.signals['Signal'][buy_condition] = 1
            self.signals['Signal'][sell_condition] = -1
        
        # Generate positions
        self.signals['Position'] = self.signals['Signal'].replace(to_replace=0, method='ffill')
        self.signals['Position'] = self.signals['Position'].fillna(0)
        
        # Clean up positions (avoid flip-flopping)
        self.signals['Position'] = self.signals['Position'].where(
            self.signals['Position'] != self.signals['Position'].shift(1), 0
        ).fillna(method='ffill').fillna(0)
        
        return self.signals
    
    def backtest_strategy(self):
        """Backtest the trading strategy"""
        self.portfolio = pd.DataFrame(index=self.signals.index)
        self.portfolio['Price'] = self.signals['Price']
        self.portfolio['Signal'] = self.signals['Signal']
        self.portfolio['Position'] = self.signals['Position']
        
        # Calculate returns
        self.portfolio['Market_Return'] = self.portfolio['Price'].pct_change()
        self.portfolio['Strategy_Return'] = (
            self.portfolio['Position'].shift(1) * self.portfolio['Market_Return']
        )
        
        # Calculate cumulative returns
        self.portfolio['Cumulative_Market'] = (1 + self.portfolio['Market_Return']).cumprod()
        self.portfolio['Cumulative_Strategy'] = (1 + self.portfolio['Strategy_Return']).cumprod()
        
        # Calculate portfolio value
        self.portfolio['Portfolio_Value'] = (
            self.initial_capital * self.portfolio['Cumulative_Strategy']
        )
        
        return self.portfolio
    
    def calculate_performance_metrics(self):
        """Calculate performance metrics"""
        strategy_returns = self.portfolio['Strategy_Return'].dropna()
        market_returns = self.portfolio['Market_Return'].dropna()
        
        metrics = {}
        
        # Total returns
        metrics['Total_Strategy_Return'] = (
            self.portfolio['Cumulative_Strategy'].iloc[-1] - 1
        ) * 100
        metrics['Total_Market_Return'] = (
            self.portfolio['Cumulative_Market'].iloc[-1] - 1
        ) * 100
        
        # Annualized returns
        days = len(strategy_returns)
        metrics['Annualized_Strategy_Return'] = (
            (1 + metrics['Total_Strategy_Return']/100) ** (252/days) - 1
        ) * 100
        metrics['Annualized_Market_Return'] = (
            (1 + metrics['Total_Market_Return']/100) ** (252/days) - 1
        ) * 100
        
        # Volatility
        metrics['Strategy_Volatility'] = strategy_returns.std() * np.sqrt(252) * 100
        metrics['Market_Volatility'] = market_returns.std() * np.sqrt(252) * 100
        
        # Sharpe Ratio (assuming 0% risk-free rate)
        metrics['Strategy_Sharpe'] = (
            metrics['Annualized_Strategy_Return'] / metrics['Strategy_Volatility']
        )
        metrics['Market_Sharpe'] = (
            metrics['Annualized_Market_Return'] / metrics['Market_Volatility']
        )
        
        # Maximum Drawdown
        cumulative = self.portfolio['Cumulative_Strategy']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        metrics['Max_Drawdown'] = drawdown.min() * 100
        
        # Win Rate
        winning_trades = strategy_returns[strategy_returns > 0]
        metrics['Win_Rate'] = len(winning_trades) / len(strategy_returns) * 100
        
        # Number of trades
        position_changes = self.portfolio['Position'].diff()
        metrics['Number_of_Trades'] = len(position_changes[position_changes != 0])
        
        return metrics
    
    def plot_results(self):
        """Plot strategy results"""
        fig, axes = plt.subplots(4, 1, figsize=(15, 16))
        
        # Plot 1: Price and Bollinger Bands
        axes[0].plot(self.data.index, self.data['Close'], label='Close Price', linewidth=1)
        axes[0].plot(self.data.index, self.data['SMA'], label='SMA(20)', alpha=0.7)
        axes[0].fill_between(self.data.index, self.data['Lower_Band'], 
                           self.data['Upper_Band'], alpha=0.2, label='Bollinger Bands')
        
        # Add buy/sell signals
        buy_signals = self.signals[self.signals['Signal'] == 1]
        sell_signals = self.signals[self.signals['Signal'] == -1]
        
        axes[0].scatter(buy_signals.index, buy_signals['Price'], 
                       color='green', marker='^', s=50, label='Buy Signal')
        axes[0].scatter(sell_signals.index, sell_signals['Price'], 
                       color='red', marker='v', s=50, label='Sell Signal')
        
        axes[0].set_title(f'{self.symbol} - Price and Trading Signals')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: RSI
        axes[1].plot(self.data.index, self.data['RSI'], label='RSI', color='purple')
        axes[1].axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought (70)')
        axes[1].axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold (30)')
        axes[1].set_title('RSI Indicator')
        axes[1].set_ylabel('RSI')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Z-Score
        axes[2].plot(self.data.index, self.data['Z_Score'], label='Z-Score', color='orange')
        axes[2].axhline(y=2, color='r', linestyle='--', alpha=0.7, label='Overvalued (+2)')
        axes[2].axhline(y=-2, color='g', linestyle='--', alpha=0.7, label='Undervalued (-2)')
        axes[2].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        axes[2].set_title('Z-Score (Mean Reversion)')
        axes[2].set_ylabel('Z-Score')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        # Plot 4: Cumulative Returns
        axes[3].plot(self.portfolio.index, 
                    (self.portfolio['Cumulative_Strategy'] - 1) * 100,
                    label='Strategy Returns', linewidth=2)
        axes[3].plot(self.portfolio.index, 
                    (self.portfolio['Cumulative_Market'] - 1) * 100,
                    label='Buy & Hold Returns', linewidth=2)
        axes[3].set_title('Cumulative Returns Comparison')
        axes[3].set_ylabel('Returns (%)')
        axes[3].set_xlabel('Date')
        axes[3].legend()
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('mean_reversion_strategy.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def run_strategy(self, strategy_type='combined'):
        """Run the complete mean reversion strategy"""
        print(f"Running Mean Reversion Strategy for {self.symbol}")
        print("=" * 60)
        
        # Fetch data
        self.fetch_data()
        
        # Calculate indicators
        print("Calculating technical indicators...")
        self.calculate_bollinger_bands()
        self.calculate_rsi()
        self.calculate_z_score()
        self.calculate_volume_indicator()
        
        # Generate signals
        print(f"Generating {strategy_type} signals...")
        self.generate_signals(strategy_type)
        
        # Backtest
        print("Backtesting strategy...")
        self.backtest_strategy()
        
        # Calculate metrics
        metrics = self.calculate_performance_metrics()
        
        # Display results
        print("\nPerformance Metrics:")
        print("-" * 40)
        print(f"Strategy Total Return: {metrics['Total_Strategy_Return']:.2f}%")
        print(f"Buy & Hold Return: {metrics['Total_Market_Return']:.2f}%")
        print(f"Strategy Annualized Return: {metrics['Annualized_Strategy_Return']:.2f}%")
        print(f"Market Annualized Return: {metrics['Annualized_Market_Return']:.2f}%")
        print(f"Strategy Volatility: {metrics['Strategy_Volatility']:.2f}%")
        print(f"Strategy Sharpe Ratio: {metrics['Strategy_Sharpe']:.2f}")
        print(f"Maximum Drawdown: {metrics['Max_Drawdown']:.2f}%")
        print(f"Win Rate: {metrics['Win_Rate']:.2f}%")
        print(f"Number of Trades: {metrics['Number_of_Trades']}")
        
        # Plot results
        self.plot_results()
        
        return metrics

def main():
    """Main function to run the mean reversion strategy"""
    
    # Strategy parameters
    symbol = "AAPL"  # You can change this to any stock
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 2)  # 2 years of data
    initial_capital = 10000
    
    # Initialize strategy
    strategy = MeanReversionStrategy(
        symbol=symbol,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=initial_capital
    )
    
    # Run different strategy types
    strategies = ['bollinger', 'rsi', 'zscore', 'combined']
    
    print("Mean Reversion Trading Strategy Backtester")
    print("=" * 50)
    print(f"Stock: {symbol}")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Initial Capital: ${initial_capital:,}")
    print()
    
    # Ask user which strategy to run
    print("Available strategies:")
    for i, strat in enumerate(strategies, 1):
        print(f"{i}. {strat.capitalize()}")
    
    choice = input("\nEnter strategy number (1-4) or 'all' for all strategies: ")
    
    if choice.lower() == 'all':
        # Run all strategies
        all_metrics = {}
        for strat in strategies:
            print(f"\n{'='*60}")
            print(f"Running {strat.upper()} Strategy")
            print('='*60)
            metrics = strategy.run_strategy(strat)
            all_metrics[strat] = metrics
        
        # Compare all strategies
        print(f"\n{'='*60}")
        print("STRATEGY COMPARISON")
        print('='*60)
        comparison_df = pd.DataFrame(all_metrics).T
        print(comparison_df[['Total_Strategy_Return', 'Strategy_Sharpe', 'Max_Drawdown', 'Win_Rate']].round(2))
        
    else:
        # Run single strategy
        strategy_idx = int(choice) - 1
        selected_strategy = strategies[strategy_idx]
        strategy.run_strategy(selected_strategy)

if __name__ == "__main__":
    main() 