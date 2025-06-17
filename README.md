# 📈 Glowing Vibe - Automated Trading Analysis System

A comprehensive, automated stock trading analysis system that dynamically fetches popular stocks, performs mean reversion analysis, and generates beautiful email reports with embedded charts.

## 🎯 **Project Overview**

This system provides:
- **Dynamic Stock Discovery**: Fetches the 100 most popular stocks from multiple sources
- **Advanced Technical Analysis**: Mean reversion strategy using Bollinger Bands, RSI, and Z-Score
- **Beautiful Visualizations**: Professional charts with buy/sell signals
- **Automated Email Reports**: HTML emails with embedded charts
- **GitHub Actions Automation**: Scheduled execution and historical archiving

## 📊 **Features**

### 🔍 **Dynamic Stock Selection**
- S&P 500 and NASDAQ 100 components
- Most active stocks from Yahoo Finance
- Recent IPOs (past 2 years)
- Popularity scoring based on market cap, volume, momentum, and beta
- Smart caching to avoid unnecessary API calls

### 📈 **Technical Analysis**
- **Mean Reversion Strategy**: Identifies oversold (buy) and overbought (sell) conditions
- **Multiple Indicators**: Bollinger Bands, RSI (14-period), Z-Score
- **Signal Strength Scoring**: Combines multiple factors for robust signals
- **Risk Metrics**: Price volatility, momentum analysis, beta calculations

### 🎨 **Visualizations**
- **Market Overview Chart**: Complete signal analysis across all stocks
- **Buy Signals Chart**: Detailed visualization of oversold opportunities
- **Sell Signals Chart**: Detailed visualization of overbought conditions
- **Interactive Elements**: Color-coded signals, trend lines, annotations

### 📧 **Email Reports**
- **Embedded Charts**: PNG charts embedded directly in HTML (no attachments needed)
- **Professional Design**: Modern, responsive email templates
- **Multiple Formats**: HTML (with embedded charts), plain text, and .eml files
- **Comprehensive Data**: Top signals, trading tips, risk management guidance

## 🏗️ **Project Structure**

```
glowing-vibe/
├── src/                                    # Source code
│   ├── dynamic_stock_fetcher.py           # Dynamic stock discovery
│   ├── multi_stock_mean_reversion_dynamic.py  # Trading analysis
│   └── email_sender_gmail_embedded.py     # Email generation with embedded charts
├── output/                                 # Generated files
│   ├── top_stocks.json                    # Cached stock list
│   ├── top_buy_signals.csv               # Buy signals data
│   ├── top_sell_signals.csv              # Sell signals data
│   ├── *.png                             # Chart visualizations
│   └── gmail_embedded_email.html         # Email with embedded charts
├── .github/workflows/                      # Automation
│   └── daily_trading_analysis.yml        # GitHub Actions workflow
├── historical_analysis/                   # Archived results
└── requirements.txt                       # Python dependencies
```

## ⚡ **Quick Start**

### 1. **Setup Environment**
```bash
# Clone the repository
git clone <your-repo-url>
cd glowing-vibe

# Install dependencies
pip install -r requirements.txt
```

### 2. **Generate Analysis**
```bash
# Fetch dynamic stock list (run twice weekly)
python src/dynamic_stock_fetcher.py

# Run trading analysis (run daily)
python src/multi_stock_mean_reversion_dynamic.py

# Generate email with embedded charts
python src/email_sender_gmail_embedded.py
```

### 3. **View Results**
- Open `output/gmail_embedded_email.html` in your browser
- Check `output/` directory for CSV data and PNG charts
- Review analysis artifacts uploaded to GitHub Actions

## 🕐 **Automation Schedule**

The system runs automatically via GitHub Actions:

| **Component** | **Schedule** | **Time (ET)** | **Time (UTC)** | **Frequency** |
|---------------|--------------|---------------|----------------|---------------|
| **Stock Fetcher** | Mon, Thu | 4:30 AM | 9:30 AM | Twice weekly |
| **Trading Analysis** | Mon-Fri | 5:00 AM | 10:00 AM | Daily |
| **Email Generation** | Mon-Fri | 5:30 AM | 10:30 AM | Daily |

### **Why This Schedule?**
- **4:30 AM ET**: Stock data refresh before market analysis
- **5:00 AM ET**: Analysis runs after overnight market movement data is available
- **5:30 AM ET**: Email ready for morning review before market open (9:30 AM ET)

## 📈 **Current Performance**

### **Latest Analysis Results**
- **Stocks Analyzed**: 100 dynamically selected popular stocks
- **Buy Signals**: 15 oversold opportunities identified
- **Sell Signals**: 15 overbought conditions detected

### **Top Current Signals**
**🟢 Buy Signals (Oversold)**:
- ADBE: $391.68, RSI 36.9, Signal Strength 0.58
- TMUS: $228.00, RSI 29.2, Signal Strength 0.57
- ADP: $306.82, RSI 27.3, Signal Strength 0.55

**🔴 Sell Signals (Overbought)**:
- FANG: $154.91, RSI 75.3, Signal Strength 0.75
- ORCL: $215.22, RSI 95.3, Signal Strength 0.73 ⚠️ (Extremely overbought)
- KLAC: $867.67, RSI 79.2, Signal Strength 0.48

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Optional: Email configuration
TO_EMAIL=your-email@gmail.com

# For actual email sending (not required for content generation)
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
SENDGRID_API_KEY=your-sendgrid-key
```

### **GitHub Secrets**
Set up these secrets in your GitHub repository for automation:
- `GITHUB_TOKEN`: Automatically provided
- `EMAIL_APP_PASSWORD`: Gmail app password (optional)
- `SENDER_EMAIL`: Your email address (optional)
- `RECIPIENT_EMAIL`: Recipient email address (optional)

## 📊 **Technical Details**

### **Stock Selection Algorithm**
1. **Data Sources**: S&P 500, NASDAQ 100, Yahoo Finance most active, recent IPOs
2. **Popularity Scoring**: 
   - Market Cap Weight: 30%
   - Volume Weight: 25%
   - Momentum Weight: 25%
   - Beta (Volatility) Weight: 20%
3. **Top 100 Selection**: Highest scoring stocks across all sources

### **Mean Reversion Strategy**
```python
# Buy Signal Criteria (Oversold)
RSI < 30 AND Price < Lower Bollinger Band AND Z-Score < -1

# Sell Signal Criteria (Overbought)  
RSI > 70 AND Price > Upper Bollinger Band AND Z-Score > 1

# Signal Strength = Combined score of all indicators
```

### **Chart Generation**
- **Libraries**: matplotlib, seaborn for professional visualizations
- **Embedding**: Charts converted to base64 and embedded in HTML
- **Size Optimization**: Compressed PNG format, responsive design
- **Compatibility**: Works with all major email clients

## 📧 **Email Features**

### **Embedded Charts Version**
- **File**: `gmail_embedded_email.html` (~8.4 MB with charts)
- **Benefits**: Self-contained, no external dependencies
- **Charts Included**: Market overview, buy signals, sell signals
- **Format**: Professional HTML with responsive design

### **Content Types Generated**
1. **HTML Email**: `gmail_embedded_email.html` - Full email with embedded charts
2. **Plain Text**: `gmail_embedded_email.txt` - Text-only version
3. **Subject Line**: `gmail_embedded_subject.txt` - Email subject
4. **Charts**: Individual PNG files for manual use

## 🚀 **Advanced Usage**

### **Manual Execution**
```bash
# Force refresh stock list
python src/dynamic_stock_fetcher.py

# Run analysis with specific parameters
python src/multi_stock_mean_reversion_dynamic.py --refresh

# Generate email content only
python src/email_sender_gmail_embedded.py
```

### **Data Export**
```bash
# View top buy signals
cat output/top_buy_signals.csv

# View top sell signals  
cat output/top_sell_signals.csv

# Check stock metadata
cat output/top_stocks.json
```

### **Historical Analysis**
All results are automatically archived in `historical_analysis/` with timestamps:
```
historical_analysis/
└── 20250616_140000/
    ├── top_buy_signals.csv
    ├── top_sell_signals.csv
    ├── dynamic_multi_stock_signals.png
    └── daily_report.md
```

## 🔬 **Strategy Performance**

### **Mean Reversion Effectiveness**
- **Best Markets**: Range-bound, low volatility environments
- **Signal Accuracy**: Higher accuracy during market consolidation periods
- **Risk Management**: Always use stop-losses and position sizing
- **Confirmation**: Consider volume, fundamentals, and market conditions

### **Key Metrics Tracked**
- Signal strength distribution
- RSI effectiveness at extremes
- Bollinger Band bounce rate
- Z-Score reversion probability

## ⚠️ **Important Disclaimers**

### **Educational Purpose Only**
- This system is for **educational and research purposes only**
- **Not financial advice** - do your own research
- Past performance does not guarantee future results
- Always consult with a financial advisor before making investment decisions

### **Risk Management**
- **Use Stop Losses**: Limit downside risk on all positions
- **Position Sizing**: Never risk more than 1-2% per trade
- **Diversification**: Don't put all capital in one signal
- **Market Conditions**: Strategy works best in ranging markets

## 🛠️ **Dependencies**

### **Core Libraries**
```
pandas>=2.0.0          # Data manipulation
numpy>=1.24.0           # Numerical computing
matplotlib>=3.7.0       # Chart generation
yfinance>=0.2.22        # Stock data
requests>=2.31.0        # HTTP requests
beautifulsoup4>=4.12.0  # Web scraping
python-dotenv==1.0.0    # Environment variables
lxml                    # XML parsing
sendgrid>=6.10.0        # Email sending (optional)
```

### **System Requirements**
- Python 3.11+
- Internet connection for data fetching
- 50MB+ disk space for historical data
- GitHub repository for automation

## 📚 **Documentation**

### **Key Files**
- `README.md`: This comprehensive guide
- `requirements.txt`: Python dependencies
- `.github/workflows/daily_trading_analysis.yml`: Automation configuration

### **Generated Reports**
- `output/daily_report.md`: Daily analysis summary (GitHub)
- `output/gmail_embedded_email.html`: Email report with charts
- `historical_analysis/*/`: Archived analysis results

## 🤝 **Contributing**

This is a personal trading analysis project. Feel free to fork and modify for your own use.

### **Customization Ideas**
- Add more technical indicators (MACD, Stochastic, etc.)
- Implement different trading strategies (momentum, breakout, etc.)
- Add fundamental analysis filters
- Integrate with broker APIs for automated execution
- Add Slack/Discord notifications

## 📝 **License**

This project is for educational purposes. Use at your own risk.

---

## 🎉 **Latest Updates**

### **Version 2.0 Features** (Current)
- ✅ Dynamic stock discovery from multiple sources  
- ✅ Enhanced technical analysis with multiple indicators
- ✅ Professional chart visualizations with embedded PNG support
- ✅ Automated GitHub Actions workflow with proper scheduling
- ✅ Beautiful HTML email reports with embedded charts
- ✅ Historical data archiving and artifact management
- ✅ Comprehensive error handling and logging

### **Future Enhancements**
- 🔄 Real-time signal monitoring
- 📱 Mobile-responsive dashboard
- 🔔 Instant notifications for high-confidence signals
- 🤖 AI-powered signal confidence scoring
- 📊 Backtesting framework with performance metrics

---

**Generated by Glowing Vibe Trading Analysis System** | **Last Updated**: 2025-06-16 