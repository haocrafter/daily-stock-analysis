# Automated Daily Trading Analysis Setup

This guide explains how to set up automated daily trading analysis using GitHub Actions.

## 🤖 GitHub Actions Automation

### What It Does

The automated workflow will:
- ✅ Run **daily** at 6:30 AM UTC (Monday-Friday)
- 📊 Analyze top 100 most popular stocks
- 🔍 Generate buy/sell signals using mean reversion
- 📈 Create visualizations and reports
- 💾 Save results and commit back to repository
- 📁 Archive historical data for tracking performance

### Setup Instructions

#### 1. Enable GitHub Actions
1. Go to your repository on GitHub
2. Click on the **"Actions"** tab
3. If prompted, click **"I understand my workflows"**

#### 2. Repository Permissions
1. Go to **Settings** → **Actions** → **General**
2. Under **"Workflow permissions"**, select:
   - ✅ **"Read and write permissions"**
   - ✅ **"Allow GitHub Actions to create and approve pull requests"**

#### 3. Push the Workflow File
The workflow file is already created at `.github/workflows/daily_trading_analysis.yml`

#### 4. Manual Test Run
1. Go to **Actions** tab in your GitHub repository
2. Click on **"Daily Trading Analysis"** workflow
3. Click **"Run workflow"** → **"Run workflow"** to test manually

### 📅 Schedule Details

- **Frequency**: Monday to Friday (market days only)
- **Time**: 6:30 AM UTC (after US market close)
- **Stock List Refresh**: Every Monday (fresh data weekly)
- **Data Sources**: S&P 500, NASDAQ 100, Most Active, Recent IPOs

### 📊 Generated Output

Each run creates:
1. **`top_buy_signals.csv`** - Top oversold opportunities
2. **`top_sell_signals.csv`** - Top overbought signals  
3. **`dynamic_multi_stock_signals.png`** - Visual analysis charts
4. **`daily_report.md`** - Formatted markdown summary
5. **`historical_analysis/YYYYMMDD_HHMMSS/`** - Archived results

### 🔧 Customization Options

#### Change Schedule
Edit the cron schedule in `.github/workflows/daily_trading_analysis.yml`:
```yaml
schedule:
  - cron: '30 6 * * 1-5'  # Current: 6:30 AM UTC, Mon-Fri
  # Examples:
  # - cron: '0 14 * * 1-5'   # 2:00 PM UTC (after market open)
  # - cron: '0 21 * * *'     # 9:00 PM UTC daily (after US close)
```

#### Change Number of Stocks
Modify `multi_stock_mean_reversion_dynamic.py`:
```python
analyzer = DynamicMultiStockMeanReversion(lookback_days=252, num_stocks=200)  # Analyze 200 instead of 100
```

#### Notification Setup (Optional)
Add email/Slack notifications by adding steps to the workflow:
```yaml
- name: Send Results to Slack
  if: success()
  uses: 8398a7/action-slack@v3
  with:
    status: success
    text: "Daily trading analysis complete! Check repository for results."
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 📈 Monitoring Performance

#### View Historical Results
- Browse `historical_analysis/` folder for past runs
- Each timestamped folder contains complete analysis
- Track signal performance over time

#### GitHub Actions Logs
- Go to **Actions** tab to see run history
- Click on any run to see detailed logs
- Download artifacts (CSV files, charts) from completed runs

### 💡 Pro Tips

1. **Market Hours Awareness**: The schedule runs after US market close to ensure latest data
2. **Weekend Handling**: Automatically skips weekends (no point analyzing when markets are closed)
3. **Cost**: GitHub Actions provides 2,000 free minutes/month for public repos, unlimited for public repos
4. **Rate Limiting**: Built-in delays prevent hitting API rate limits
5. **Caching**: Stock list refreshes weekly (Mondays) to balance freshness vs efficiency

### 🚨 Troubleshooting

#### Common Issues:

**"Permission denied" errors:**
- Check repository permissions under Settings → Actions → General

**"Workflow not running on schedule":**
- GitHub Actions may have up to 15-minute delays
- Low activity repos may experience longer delays
- Manual trigger works immediately

**"Python package errors":**
- Check `requirements.txt` has all needed packages
- Workflow automatically installs dependencies

**"No data found" errors:**
- Usually due to API rate limits or weekend runs
- Check if running during market hours/days

### 📧 Getting Notifications

To receive daily reports via email/Slack, you can:
1. **Watch the repository** for all commits (gets email on each analysis)
2. **Set up GitHub notifications** for Actions
3. **Add custom notification steps** to the workflow
4. **Use GitHub Pages** to create a live dashboard

### 🔒 Security Notes

- Workflow uses built-in `GITHUB_TOKEN` (no setup required)
- No sensitive API keys needed (uses free yfinance)
- All data is public market data
- Results are committed to public repository

## Next Steps

1. Push this setup to your repository
2. Enable Actions and run a test
3. Wait for your first scheduled run
4. Check the `historical_analysis/` folder for results
5. Customize schedule/parameters as needed

Happy automated trading analysis! 🚀📈 