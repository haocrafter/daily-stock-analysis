import smtplib
import os
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TradingAnalysisEmailer:
    def __init__(self):
        # Email configuration - using Gmail SMTP
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('SENDER_EMAIL', 'your_email@gmail.com')  # Set in .env or GitHub secrets
        self.sender_password = os.getenv('EMAIL_APP_PASSWORD')  # Gmail app password
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')  # Can be overridden in .env
        
        # File paths
        self.output_dir = 'output'
        self.buy_signals_file = os.path.join(self.output_dir, 'top_buy_signals.csv')
        self.sell_signals_file = os.path.join(self.output_dir, 'top_sell_signals.csv')
        self.stocks_metadata_file = os.path.join(self.output_dir, 'top_stocks.json')
        self.charts_file = os.path.join(self.output_dir, 'dynamic_multi_stock_signals.png')
        
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
            print(f"Error loading analysis data: {e}")
            return pd.DataFrame(), pd.DataFrame(), []
    
    def create_html_report(self, buy_signals, sell_signals, stock_metadata):
        """Create HTML email content"""
        
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .buy-signals {{ background-color: #d5f4e6; padding: 15px; border-radius: 5px; }}
                .sell-signals {{ background-color: #f8d7da; padding: 15px; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                .strong {{ font-weight: bold; }}
                .positive {{ color: #27ae60; }}
                .negative {{ color: #e74c3c; }}
                .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                .footer {{ background-color: #34495e; color: white; padding: 10px; border-radius: 5px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📈 Daily Trading Analysis Report</h1>
                <p>Generated on: {current_date}</p>
                <p>Analyzed {len(stock_metadata)} popular stocks from multiple sources</p>
            </div>
            
            <div class="section summary">
                <h2>📊 Market Analysis Summary</h2>
                <ul>
                    <li><strong>Total Stocks Analyzed:</strong> {len(stock_metadata)}</li>
                    <li><strong>Buy Signals Found:</strong> {len(buy_signals)}</li>
                    <li><strong>Sell Signals Found:</strong> {len(sell_signals)}</li>
                    <li><strong>Data Sources:</strong> S&P 500, NASDAQ 100, Most Active, Recent IPOs</li>
                    <li><strong>Strategy:</strong> Mean Reversion (Bollinger Bands, RSI, Z-Score)</li>
                </ul>
            </div>
        """
        
        # Add Buy Signals section
        if not buy_signals.empty:
            html_content += """
            <div class="section buy-signals">
                <h2>🟢 Top Buy Signals (Oversold Opportunities)</h2>
                <p>These stocks show strong mean reversion buy signals based on technical indicators:</p>
                <table>
                    <tr>
                        <th>Symbol</th>
                        <th>Price</th>
                        <th>Signal Strength</th>
                        <th>RSI</th>
                        <th>Z-Score</th>
                        <th>5-Day Change</th>
                        <th>vs 50-Day MA</th>
                    </tr>
            """
            
            for _, row in buy_signals.head(10).iterrows():
                price_change_class = "negative" if row['Price_Change_5d'] < 0 else "positive"
                html_content += f"""
                    <tr>
                        <td class="strong">{row['Symbol']}</td>
                        <td>${row['Current_Price']:.2f}</td>
                        <td class="strong">{row['Buy_Signal_Strength']:.2f}</td>
                        <td>{row['RSI']:.1f}</td>
                        <td>{row['Z_Score']:.2f}</td>
                        <td class="{price_change_class}">{row['Price_Change_5d']:.1f}%</td>
                        <td>{row['Price_vs_SMA50']:.1f}%</td>
                    </tr>
                """
            
            html_content += "</table></div>"
        
        # Add Sell Signals section
        if not sell_signals.empty:
            html_content += """
            <div class="section sell-signals">
                <h2>🔴 Top Sell Signals (Overbought Conditions)</h2>
                <p>These stocks show strong mean reversion sell signals based on technical indicators:</p>
                <table>
                    <tr>
                        <th>Symbol</th>
                        <th>Price</th>
                        <th>Signal Strength</th>
                        <th>RSI</th>
                        <th>Z-Score</th>
                        <th>5-Day Change</th>
                        <th>vs 50-Day MA</th>
                    </tr>
            """
            
            for _, row in sell_signals.head(10).iterrows():
                price_change_class = "positive" if row['Price_Change_5d'] > 0 else "negative"
                html_content += f"""
                    <tr>
                        <td class="strong">{row['Symbol']}</td>
                        <td>${row['Current_Price']:.2f}</td>
                        <td class="strong">{row['Sell_Signal_Strength']:.2f}</td>
                        <td>{row['RSI']:.1f}</td>
                        <td>{row['Z_Score']:.2f}</td>
                        <td class="{price_change_class}">{row['Price_Change_5d']:.1f}%</td>
                        <td>{row['Price_vs_SMA50']:.1f}%</td>
                    </tr>
                """
            
            html_content += "</table></div>"
        
        # Add trading tips
        html_content += """
        <div class="section">
            <h2>💡 Trading Tips</h2>
            <ul>
                <li><strong>Buy Signals:</strong> Look for RSI < 30, negative Z-scores, and recent price declines</li>
                <li><strong>Sell Signals:</strong> Look for RSI > 70, positive Z-scores, and recent price gains</li>
                <li><strong>Risk Management:</strong> Always use stop-losses and position sizing</li>
                <li><strong>Confirmation:</strong> Consider volume, market conditions, and fundamental analysis</li>
                <li><strong>Mean Reversion:</strong> These signals work best in range-bound markets</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>📧 Automated Trading Analysis | Generated by GitHub Actions</p>
            <p>⚠️ This is for educational purposes only. Not financial advice. Always do your own research.</p>
            <p>📊 Data sources: Yahoo Finance via yfinance library</p>
        </div>
        
        </body>
        </html>
        """
        
        return html_content
    
    def send_email(self):
        """Send the trading analysis email"""
        try:
            # Load analysis data
            buy_signals, sell_signals, stock_metadata = self.load_analysis_data()
            
            if buy_signals.empty and sell_signals.empty:
                print("No analysis data found to send")
                return False
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"📈 Daily Trading Analysis - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Create HTML content
            html_content = self.create_html_report(buy_signals, sell_signals, stock_metadata)
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Attach CSV files
            attachments = [
                (self.buy_signals_file, 'Top Buy Signals'),
                (self.sell_signals_file, 'Top Sell Signals'),
                (self.charts_file, 'Analysis Charts')
            ]
            
            for filepath, description in attachments:
                if os.path.exists(filepath):
                    try:
                        with open(filepath, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        # Use just the filename, not the full path
                        filename = os.path.basename(filepath)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {filename}',
                        )
                        msg.attach(part)
                        print(f"Attached {filename}")
                    except Exception as e:
                        print(f"Error attaching {filepath}: {e}")
            
            # Send email
            if not self.sender_password:
                print("❌ EMAIL_APP_PASSWORD not set. Cannot send email.")
                print("💡 For GitHub Actions, add EMAIL_APP_PASSWORD to repository secrets")
                return False
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.recipient_email, text)
            server.quit()
            
            print(f"✅ Trading analysis email sent successfully to {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

def main():
    """Main function to send daily trading analysis email"""
    emailer = TradingAnalysisEmailer()
    success = emailer.send_email()
    
    if success:
        print("📧 Daily trading analysis email sent successfully!")
    else:
        print("❌ Failed to send trading analysis email")
        print("💡 Make sure EMAIL_APP_PASSWORD is set as environment variable")

if __name__ == "__main__":
    main() 