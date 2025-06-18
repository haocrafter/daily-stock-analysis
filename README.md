# 🚀 Glowing Vibe: Advanced Stock Analysis & Trading Signals

A comprehensive stock analysis platform that combines **Mean Reversion** and **Momentum-Based** trading strategies to generate intelligent buy/sell signals across the most popular stocks.

## 🎯 Features

### **Multi-Strategy Analysis**
- **Mean Reversion Algorithm**: Identifies oversold/overbought conditions using Bollinger Bands, RSI, Z-Score analysis
- **Momentum Algorithms**: Detects trend-following opportunities using RSI, MACD, Price ROC, and Moving Average signals
- **Combined Strategy Analysis**: Intelligently combines both approaches for consensus, contrarian, and strategy-specific signals

### **Dynamic Stock Selection**
- Automatically fetches top stocks from S&P 500, NASDAQ 100, Dow Jones, and trending stocks
- Ranks stocks by popularity score (market cap, volume, momentum, beta)
- Supports 100+ stocks with intelligent caching

### **Advanced Technical Analysis**
- **15+ Technical Indicators**: RSI, MACD, Bollinger Bands, Z-Score, ROC, Moving Averages, Volume Analysis
- **Signal Confidence Scoring**: Each signal includes confidence levels and strategy type classification
- **Multi-timeframe Analysis**: 5-day, 10-day, 20-day momentum with 252-day lookback

### **Comprehensive Reporting**
- **Professional Visualizations**: 6-panel combined strategy dashboard with buy/sell signals
- **CSV Exports**: Detailed signal data with strategy types and confidence scores
- **Strategy Classification**: CONSENSUS, MOMENTUM, MEAN_REVERSION, CONTRARIAN, WEAK
- **Clean Output**: Individual algorithms run silently, final results only from combined analysis
- **Email Integration**: Automated reports with embedded multi-strategy dashboard

## 📊 Strategy Overview

### **1. Mean Reversion Strategy**
Identifies stocks that have deviated significantly from their average price and are likely to revert:
- **Buy Signals**: Oversold conditions (low RSI, negative Z-score, below Bollinger lower band)
- **Sell Signals**: Overbought conditions (high RSI, positive Z-score, above Bollinger upper band)
- **Best For**: Range-bound markets, high-volatility stocks, contrarian plays

### **2. Momentum Strategy**
Identifies stocks with strong directional movement likely to continue:
- **Buy Signals**: Upward momentum (RSI > 50, MACD crossovers, positive ROC, price above MAs)
- **Sell Signals**: Downward momentum (RSI < 50, bearish MACD, negative ROC, price below MAs)
- **Best For**: Trending markets, breakout plays, trend-following

### **3. Combined Strategy**
Intelligently combines both approaches:
- **Consensus Signals**: Both strategies agree (highest confidence)
- **Momentum-Driven**: Momentum dominates with mean reversion support
- **Mean Reversion-Driven**: Mean reversion dominates with momentum confirmation
- **Contrarian Signals**: Strategies disagree (high risk/reward opportunities)

## 🛠 Installation

```bash
# Clone the repository
git clone <repository-url>
cd glowing-vibe

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional, for email features)
cp .env.example .env
# Edit .env with your Gmail credentials
```

## ⚡ Quick Start

For the best results, run the **Combined Strategy Analysis** which includes both mean reversion and momentum strategies:

```bash
# 1. Run complete analysis (recommended for daily use)
python src/combined_strategy_analysis.py

# 2. Generate email report with charts
python src/email_sender_gmail_embedded.py

# 3. View results in output/ directory
```

This generates comprehensive analysis with strategy consensus, confidence scoring, and professional visualizations.

## 🚀 Detailed Usage

### **1. Mean Reversion Analysis**
```bash
# Run mean reversion analysis with cached stocks
python src/mean_reversion_algorithms.py

# Force refresh stock list from all sources
python src/mean_reversion_algorithms.py --refresh
```

### **2. Momentum Analysis**
```bash
# Run momentum analysis with cached stocks
python src/momentum_algorithms.py

# Force refresh stock list from all sources
python src/momentum_algorithms.py --refresh
```

### **3. Combined Strategy Analysis**
```bash
# Run comprehensive combined analysis
python src/combined_strategy_analysis.py

# Force refresh stock list from all sources
python src/combined_strategy_analysis.py --refresh
```

### **4. Send Email Reports**
```bash
# Generate combined strategy email report (requires combined analysis first)
python src/email_sender_gmail_embedded.py
```



### **Daily Analysis Workflow (Recommended)**
```bash
# Run complete combined analysis (includes both strategies)
python src/combined_strategy_analysis.py

# Generate email report with embedded charts
python src/email_sender_gmail_embedded.py
```

## 📈 Output Files

The analysis generates comprehensive output files in the `output/` directory:

### **Mean Reversion Outputs**
- `top_buy_signals.csv`: Top oversold stocks with mean reversion buy signals
- `top_sell_signals.csv`: Top overbought stocks with mean reversion sell signals
- `dynamic_multi_stock_signals.png`: Visual analysis charts

### **Momentum Outputs**
- `top_momentum_buy_signals.csv`: Top stocks with strong upward momentum
- `top_momentum_sell_signals.csv`: Top stocks with strong downward momentum

### **Combined Strategy Outputs**
- `combined_strategy_analysis.csv`: Complete analysis with all signals and strategy types
- `consensus_signals.csv`: Stocks where both strategies agree (highest confidence)
- `momentum_dominant_signals.csv`: Momentum-driven recommendations
- `mean_reversion_dominant_signals.csv`: Mean reversion-driven recommendations
- `contrarian_signals.csv`: High risk/reward contrarian plays
- `combined_strategy_analysis.png`: Comprehensive visualization dashboard

### **Email Integration**
- `gmail_embedded_email.html`: HTML email with embedded combined strategy dashboard
- `gmail_embedded_email.txt`: Plain text summary of combined analysis
- `gmail_embedded_subject.txt`: Email subject line

## 🔧 Technical Architecture

### **Core Components**

1. **`dynamic_stock_fetcher.py`**: Dynamic stock selection and ranking
   - Fetches from multiple sources (S&P 500, NASDAQ, Dow Jones, trending)
   - Calculates popularity scores based on market cap, volume, momentum, beta
   - Intelligent caching system

2. **`mean_reversion_algorithms.py`**: Mean reversion analysis engine
   - Bollinger Bands, RSI, Z-Score calculations
   - Volume-weighted signals
   - Oversold/overbought detection

3. **`momentum_algorithms.py`**: Momentum analysis engine
   - RSI momentum, MACD crossovers
   - Price rate of change (ROC) analysis
   - Moving average trend detection
   - Volume confirmation

4. **`combined_strategy_analysis.py`**: Strategy integration engine
   - Signal combination algorithms
   - Strategy type classification
   - Confidence scoring system
   - Comprehensive reporting

5. **`email_sender_gmail_embedded.py`**: Automated reporting system
   - Combined strategy email reports with embedded dashboard
   - HTML email generation with multi-strategy analysis
   - Strategy breakdown and confidence scoring in emails

### **Key Algorithms**

#### **Mean Reversion Signal Calculation**
```python
def calculate_buy_signal_strength(data):
    # Combine multiple mean reversion indicators
    bollinger_signal = (close < bollinger_lower) * 0.3
    rsi_signal = (rsi < 30) * 0.25
    zscore_signal = (zscore < -2) * 0.25
    volume_signal = (volume > avg_volume * 1.5) * 0.2
    
    return min(sum(signals), 1.0)
```

#### **Momentum Signal Calculation**
```python
def calculate_momentum_signal_strength(data):
    # Combine multiple momentum indicators
    rsi_momentum = (rsi > 60 and rsi_prev <= 60) * 0.3
    macd_crossover = (macd > signal and macd_prev <= signal_prev) * 0.4
    price_momentum = (roc_5 > 5) * 0.2
    ma_alignment = (price_above_ma_count >= 3) * 0.1
    
    return min(sum(signals), 1.0)
```

#### **Combined Strategy Logic**
```python
def calculate_combined_signal(mr_signal, mom_signal):
    # Boost when both strategies agree
    if mr_signal > 0.5 and mom_signal > 0.5:
        return (mr_signal + mom_signal) / 2 * 1.2
    
    # Momentum breakout with mean reversion support
    elif mom_signal > 0.7 and mr_signal > 0.2:
        return mom_signal * 0.8 + mr_signal * 0.2
    
    # Individual strong signals
    elif max(mr_signal, mom_signal) > 0.6:
        return max(mr_signal, mom_signal) * 0.8
    
    return (mr_signal + mom_signal) / 2 * 0.6
```

## 📊 Signal Interpretation Guide

### **Signal Strength Scale**
- **0.8 - 1.0**: Very Strong Signal (High Probability)
- **0.6 - 0.8**: Strong Signal (Good Probability)
- **0.4 - 0.6**: Moderate Signal (Medium Probability)
- **0.2 - 0.4**: Weak Signal (Low Probability)
- **0.0 - 0.2**: Very Weak Signal (Very Low Probability)

### **Strategy Types**
- **CONSENSUS**: Both mean reversion and momentum agree (Highest Confidence)
- **MOMENTUM**: Trend-following signals dominate (Good for trending markets)
- **MEAN_REVERSION**: Contrarian signals dominate (Good for range-bound markets)
- **CONTRARIAN**: Strategies disagree (High risk/reward, requires careful analysis)
- **WEAK**: Low signal strength across all strategies

### **Confidence Scores**
- **0.9**: High confidence (Both strategies agree)
- **0.75**: Medium-high confidence (Strong individual signals)
- **0.6**: Medium confidence (Moderate signals)
- **0.4**: Lower confidence (Contrarian signals)
- **0.3**: Low confidence (Weak signals)

## ⚠️ Risk Disclaimer

This software is for educational and research purposes only. It is not financial advice. Always:
- Conduct your own research
- Consider your risk tolerance
- Diversify your investments
- Consult with financial professionals
- Never invest more than you can afford to lose

Past performance does not guarantee future results. All trading involves risk of loss.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- New technical indicators
- Additional data sources
- Performance optimizations
- Bug fixes
- Documentation improvements

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ for the trading community** 