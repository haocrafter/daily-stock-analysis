#!/usr/bin/env python3
"""
Gmail Email Content Generator with Embedded Charts

Generates email content with PNG charts embedded directly in HTML as base64 images.
No separate PNG attachments needed - everything is self-contained in the HTML file.

Usage: python src/email_sender_gmail_embedded.py
"""

import os
import base64
import pandas as pd
from datetime import datetime
import json
from dotenv import load_dotenv

class GmailEmailSender:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Email configuration
        self.to_email = os.getenv('TO_EMAIL', 'haowang228@gmail.com')
        
        # File paths
        self.output_dir = 'output'
        self.buy_signals_file = os.path.join(self.output_dir, 'top_buy_signals.csv')
        self.sell_signals_file = os.path.join(self.output_dir, 'top_sell_signals.csv')
        self.stocks_metadata_file = os.path.join(self.output_dir, 'top_stocks.json')
        
        # PNG chart files
        self.buy_chart = os.path.join(self.output_dir, 'detailed_buy_signals.png')
        self.sell_chart = os.path.join(self.output_dir, 'detailed_sell_signals.png')
        self.overview_chart = os.path.join(self.output_dir, 'dynamic_multi_stock_signals.png')
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        issues = []
        
        if not os.path.exists(self.buy_signals_file):
            issues.append(f"Buy signals file not found: {self.buy_signals_file}")
        
        if not os.path.exists(self.sell_signals_file):
            issues.append(f"Sell signals file not found: {self.sell_signals_file}")
        
        return issues
    
    def load_analysis_data(self):
        """Load the latest analysis results"""
        try:
            # Load buy signals
            buy_signals = pd.read_csv(self.buy_signals_file) if os.path.exists(self.buy_signals_file) else pd.DataFrame()
            
            # Load sell signals  
            sell_signals = pd.read_csv(self.sell_signals_file) if os.path.exists(self.sell_signals_file) else pd.DataFrame()
            
            # Load stock metadata
            stock_metadata = []
            if os.path.exists(self.stocks_metadata_file):
                with open(self.stocks_metadata_file, 'r') as f:
                    stock_metadata = json.load(f)
            
            return buy_signals, sell_signals, stock_metadata
            
        except Exception as e:
            print(f"❌ Error loading analysis data: {e}")
            return pd.DataFrame(), pd.DataFrame(), []

    def image_to_base64(self, image_path):
        """Convert image to base64 string for HTML embedding"""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            print(f"⚠️ Error converting {image_path} to base64: {e}")
            return None

    def generate_html_email(self, buy_signals, sell_signals, stock_metadata):
        """Generate HTML email content with embedded charts"""
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        
        # Convert charts to base64 for embedding
        print("🖼️ Converting PNG charts to base64...")
        buy_chart_b64 = self.image_to_base64(self.buy_chart) if os.path.exists(self.buy_chart) else None
        sell_chart_b64 = self.image_to_base64(self.sell_chart) if os.path.exists(self.sell_chart) else None
        overview_chart_b64 = self.image_to_base64(self.overview_chart) if os.path.exists(self.overview_chart) else None
        
        # Start building HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
            background-color: #f8f9fa;
        }}
        .container {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 30px 20px; 
            text-align: center; 
        }}
        .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
        .header p {{ margin: 10px 0 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .summary {{ 
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 30px; 
        }}
        .summary h2 {{ margin-top: 0; color: #495057; }}
        .metrics {{ display: flex; flex-wrap: wrap; gap: 15px; margin-top: 15px; }}
        .metric {{ 
            background: white; 
            padding: 12px 16px; 
            border-radius: 6px; 
            border-left: 4px solid #007bff; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex: 1;
            min-width: 200px;
        }}
        .metric-label {{ font-size: 12px; color: #6c757d; text-transform: uppercase; font-weight: 600; }}
        .metric-value {{ font-size: 20px; font-weight: 700; color: #212529; }}
        .chart-container {{ text-align: center; margin: 30px 0; }}
        .chart-container h3 {{ color: #495057; margin-bottom: 15px; }}
        .chart-container img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        .signals-section {{ margin-bottom: 40px; }}
        .section-header {{ 
            display: flex; 
            align-items: center; 
            margin-bottom: 20px; 
            padding-bottom: 10px; 
            border-bottom: 2px solid #e9ecef; 
        }}
        .buy-signals .section-header {{ border-bottom-color: #28a745; }}
        .sell-signals .section-header {{ border-bottom-color: #dc3545; }}
        .section-header h2 {{ margin: 0; font-size: 22px; }}
        .signal-table {{ 
            width: 100%; 
            border-collapse: collapse; 
            background: white; 
            border-radius: 8px; 
            overflow: hidden; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
        }}
        .signal-table th {{ 
            background: #f8f9fa; 
            padding: 15px 12px; 
            text-align: left; 
            font-weight: 600; 
            color: #495057; 
            border-bottom: 2px solid #dee2e6; 
        }}
        .signal-table td {{ 
            padding: 12px; 
            border-bottom: 1px solid #dee2e6; 
        }}
        .buy-row {{ background: rgba(40, 167, 69, 0.05); }}
        .sell-row {{ background: rgba(220, 53, 69, 0.05); }}
        .symbol {{ font-weight: 700; color: #212529; }}
        .price {{ font-weight: 600; color: #007bff; }}
        .signal-strength {{ font-weight: 600; }}
        .rsi {{ font-family: monospace; }}
        .change-positive {{ color: #28a745; font-weight: 600; }}
        .change-negative {{ color: #dc3545; font-weight: 600; }}
        .tips {{ 
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
            padding: 25px; 
            border-radius: 8px; 
            margin-top: 30px; 
        }}
        .tips h3 {{ margin-top: 0; color: #1565c0; }}
        .tips ul {{ margin: 0; }}
        .tips li {{ margin-bottom: 8px; }}
        .footer {{ 
            text-align: center; 
            padding: 20px; 
            background: #f8f9fa; 
            color: #6c757d; 
            font-size: 13px; 
            border-top: 1px solid #dee2e6; 
        }}
        .embedded-note {{
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 6px;
            padding: 15px;
            margin-top: 20px;
        }}
        .embedded-note h4 {{ margin-top: 0; color: #0c5460; }}
        @media (max-width: 600px) {{
            .metrics {{ flex-direction: column; }}
            .signal-table {{ font-size: 14px; }}
            .signal-table th, .signal-table td {{ padding: 8px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Daily Trading Analysis Report</h1>
            <p>{current_date}</p>
        </div>
        
        <div class="content">
            <div class="summary">
                <h2>📊 Market Analysis Summary</h2>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-label">Stocks Analyzed</div>
                        <div class="metric-value">{len(stock_metadata)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Buy Signals</div>
                        <div class="metric-value" style="color: #28a745;">{len(buy_signals)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Sell Signals</div>
                        <div class="metric-value" style="color: #dc3545;">{len(sell_signals)}</div>
                    </div>
                </div>
                <p style="margin-top: 20px; color: #6c757d;">
                    <strong>Strategy:</strong> Mean Reversion &nbsp;•&nbsp; 
                    <strong>Sources:</strong> S&P 500, NASDAQ 100, Most Active, Recent IPOs
                </p>
            </div>"""

        # Market Overview Chart
        if overview_chart_b64:
            html_content += f"""
            <div class="chart-container">
                <h3>📊 Market Overview</h3>
                <img src="data:image/png;base64,{overview_chart_b64}" alt="Market Overview Chart" />
            </div>"""

        # Buy Signals Section
        if not buy_signals.empty:
            html_content += """
            <div class="signals-section buy-signals">
                <div class="section-header">
                    <h2>🟢 Top Buy Signals (Oversold Opportunities)</h2>
                </div>
                <table class="signal-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Price</th>
                            <th>Signal Strength</th>
                            <th>RSI</th>
                            <th>5-Day Change</th>
                        </tr>
                    </thead>
                    <tbody>"""
            
            for _, row in buy_signals.head(5).iterrows():
                change_class = "change-negative" if row['Price_Change_5d'] < 0 else "change-positive"
                html_content += f"""
                        <tr class="buy-row">
                            <td class="symbol">{row['Symbol']}</td>
                            <td class="price">${row['Current_Price']:.2f}</td>
                            <td class="signal-strength">{row['Buy_Signal_Strength']:.2f}</td>
                            <td class="rsi">{row['RSI']:.1f}</td>
                            <td class="{change_class}">{row['Price_Change_5d']:+.1f}%</td>
                        </tr>"""
            
            html_content += """
                    </tbody>
                </table>"""
            
            # Buy Signals Chart
            if buy_chart_b64:
                html_content += f"""
                <div class="chart-container">
                    <img src="data:image/png;base64,{buy_chart_b64}" alt="Buy Signals Chart" />
                </div>"""
            
            html_content += """
            </div>"""

        # Sell Signals Section
        if not sell_signals.empty:
            html_content += """
            <div class="signals-section sell-signals">
                <div class="section-header">
                    <h2>🔴 Top Sell Signals (Overbought Conditions)</h2>
                </div>
                <table class="signal-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Price</th>
                            <th>Signal Strength</th>
                            <th>RSI</th>
                            <th>5-Day Change</th>
                        </tr>
                    </thead>
                    <tbody>"""
            
            for _, row in sell_signals.head(5).iterrows():
                change_class = "change-positive" if row['Price_Change_5d'] > 0 else "change-negative"
                html_content += f"""
                        <tr class="sell-row">
                            <td class="symbol">{row['Symbol']}</td>
                            <td class="price">${row['Current_Price']:.2f}</td>
                            <td class="signal-strength">{row['Sell_Signal_Strength']:.2f}</td>
                            <td class="rsi">{row['RSI']:.1f}</td>
                            <td class="{change_class}">{row['Price_Change_5d']:+.1f}%</td>
                        </tr>"""
            
            html_content += """
                    </tbody>
                </table>"""
            
            # Sell Signals Chart
            if sell_chart_b64:
                html_content += f"""
                <div class="chart-container">
                    <img src="data:image/png;base64,{sell_chart_b64}" alt="Sell Signals Chart" />
                </div>"""
            
            html_content += """
            </div>"""

        # Tips and Footer
        html_content += """
            <div class="tips">
                <h3>💡 Trading Tips & Risk Management</h3>
                <ul>
                    <li><strong>Buy Signals:</strong> Look for RSI &lt; 30, negative Z-scores, recent declines</li>
                    <li><strong>Sell Signals:</strong> Look for RSI &gt; 70, positive Z-scores, recent gains</li>
                    <li><strong>Risk Management:</strong> Always use stop-losses and proper position sizing</li>
                    <li><strong>Confirmation:</strong> Consider volume patterns, market conditions, and fundamentals</li>
                    <li><strong>Timing:</strong> Mean reversion works best in ranging markets</li>
                </ul>
            </div>
            
            <div class="embedded-note">
                <h4>📊 Embedded Visualizations</h4>
                <p>This email contains embedded PNG charts for better compatibility:</p>
                <ul>
                    <li><strong>Market Overview:</strong> Complete analysis of all signals</li>
                    <li><strong>Buy Signals Chart:</strong> Detailed buy opportunities visualization</li>
                    <li><strong>Sell Signals Chart:</strong> Detailed sell opportunities visualization</li>
                </ul>
                <p><em>Charts are embedded as base64 images - no external files needed!</em></p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>📧 Automated Trading Analysis</strong> | Embedded Charts Version</p>
            <p>⚠️ <em>This analysis is for educational purposes only. Not financial advice.</em></p>
            <p>📊 Data sources: Yahoo Finance via yfinance library</p>
        </div>
    </div>
</body>
</html>"""
        
        return html_content

    def save_email_content(self):
        """Generate and save email content with embedded charts"""
        
        try:
            # Load analysis data
            print("📊 Loading analysis data...")
            buy_signals, sell_signals, stock_metadata = self.load_analysis_data()
            
            if buy_signals.empty and sell_signals.empty:
                print("❌ No analysis data found")
                return False
            
            # Generate HTML content with embedded charts
            print("📝 Generating HTML email with embedded charts...")
            html_content = self.generate_html_email(buy_signals, sell_signals, stock_metadata)
            
            # Save HTML content
            html_file = os.path.join(self.output_dir, 'gmail_embedded_email.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ HTML email with embedded charts saved to {html_file}")
            
            # Generate plain text summary
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
            text_content = f"""📈 DAILY TRADING ANALYSIS REPORT - {current_date}
{'='*60}

📊 MARKET ANALYSIS SUMMARY:
• Total Stocks Analyzed: {len(stock_metadata)}
• Buy Signals Found: {len(buy_signals)}
• Sell Signals Found: {len(sell_signals)}
• Data Sources: S&P 500, NASDAQ 100, Most Active, Recent IPOs
• Strategy: Mean Reversion (Bollinger Bands, RSI, Z-Score)

🟢 TOP 5 BUY SIGNALS (Oversold Opportunities):
{'-'*50}
"""
            
            if not buy_signals.empty:
                for i, (_, row) in enumerate(buy_signals.head(5).iterrows(), 1):
                    text_content += f"{i}. {row['Symbol']} - ${row['Current_Price']:.2f} | Signal: {row['Buy_Signal_Strength']:.2f} | RSI: {row['RSI']:.1f} | Change: {row['Price_Change_5d']:+.1f}%\n"
            
            text_content += f"""
🔴 TOP 5 SELL SIGNALS (Overbought Conditions):
{'-'*50}
"""
            
            if not sell_signals.empty:
                for i, (_, row) in enumerate(sell_signals.head(5).iterrows(), 1):
                    text_content += f"{i}. {row['Symbol']} - ${row['Current_Price']:.2f} | Signal: {row['Sell_Signal_Strength']:.2f} | RSI: {row['RSI']:.1f} | Change: {row['Price_Change_5d']:+.1f}%\n"
            
            text_content += f"""
💡 TRADING TIPS:
• Buy Signals: Look for RSI < 30, negative Z-scores, recent declines
• Sell Signals: Look for RSI > 70, positive Z-scores, recent gains  
• Risk Management: Always use stop-losses and position sizing
• Confirmation: Consider volume, market conditions, fundamentals

🖼️ EMBEDDED VISUALIZATIONS:
• Market overview chart showing all signals
• Buy signals detailed chart  
• Sell signals detailed chart
• All charts embedded in HTML - no separate files needed!

📧 Automated Trading Analysis | Embedded Charts Version
⚠️  This is for educational purposes only. Not financial advice.
📊 Data sources: Yahoo Finance via yfinance library
"""
            
            # Save text content
            text_file = os.path.join(self.output_dir, 'gmail_embedded_email.txt')
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"✅ Text email content saved to {text_file}")
            
            # Create email subject
            subject = f"📈 Daily Trading Analysis - {datetime.now().strftime('%Y-%m-%d')} (Embedded Charts)"
            subject_file = os.path.join(self.output_dir, 'gmail_embedded_subject.txt')
            with open(subject_file, 'w', encoding='utf-8') as f:
                f.write(subject)
            print(f"✅ Email subject saved to {subject_file}")
            
            # Show file summary
            print(f"\n📋 Email Content Summary:")
            print(f"   📧 Subject: {subject}")
            print(f"   📄 Recipients: {self.to_email}")
            print(f"   📊 Buy signals: {len(buy_signals)}, Sell signals: {len(sell_signals)}")
            print(f"   🖼️ Embedded charts: Market overview, buy signals, sell signals")
            
            # Show file sizes
            if os.path.exists(html_file):
                size_mb = os.path.getsize(html_file) / (1024 * 1024)
                print(f"\n📊 Generated File:")
                print(f"   📁 {os.path.basename(html_file)}: {size_mb:.1f} MB (includes embedded charts)")
            
            print(f"\n🎉 Email content with embedded charts generated successfully!")
            print(f"💡 All charts are embedded in the HTML - no separate attachments needed!")
            return True
            
        except Exception as e:
            print(f"❌ Error generating email content: {e}")
            return False

def main():
    """Main function"""
    print("📧 Gmail Email Content Generator (Embedded Charts)")
    print("=" * 55)
    print("🖼️ Embeds PNG charts directly in HTML - no attachments needed")
    print()
    
    sender = GmailEmailSender()
    
    # Check prerequisites
    issues = sender.check_prerequisites()
    
    if issues:
        print("❌ Prerequisites not met:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 Setup Instructions:")
        print("   📊 Generate analysis data first:")
        print("      python src/multi_stock_mean_reversion_dynamic.py")
        
        return
    
    # All prerequisites met, generate email content
    success = sender.save_email_content()
    
    if success:
        print("\n💡 Next Steps:")
        print("   🌐 Open output/gmail_embedded_email.html in browser to preview")
        print("   📧 Email is self-contained with embedded charts")
        print("   📄 Use output/gmail_embedded_email.txt for plain text version")
        print("   🚀 Use HTML file with any email service or automation")
    else:
        print("\n💔 Email content generation failed")

if __name__ == "__main__":
    main() 