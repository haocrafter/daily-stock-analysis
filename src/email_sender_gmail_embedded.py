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
        # Updated to use combined strategy analysis files
        self.combined_analysis_file = os.path.join(self.output_dir, 'combined_strategy_analysis.csv')
        self.consensus_signals_file = os.path.join(self.output_dir, 'consensus_signals.csv')
        self.momentum_signals_file = os.path.join(self.output_dir, 'momentum_dominant_signals.csv')
        self.mean_reversion_signals_file = os.path.join(self.output_dir, 'mean_reversion_dominant_signals.csv')
        self.contrarian_signals_file = os.path.join(self.output_dir, 'contrarian_signals.csv')
        self.stocks_metadata_file = os.path.join(self.output_dir, 'top_stocks.json')
        
        # PNG chart files - updated to use combined strategy analysis
        self.combined_chart = os.path.join(self.output_dir, 'combined_strategy_analysis.png')
        # Keep fallback to old charts if available
        self.buy_chart = os.path.join(self.output_dir, 'detailed_buy_signals.png')
        self.sell_chart = os.path.join(self.output_dir, 'detailed_sell_signals.png')
        self.overview_chart = os.path.join(self.output_dir, 'dynamic_multi_stock_signals.png')
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        issues = []
        
        if not os.path.exists(self.combined_analysis_file):
            issues.append(f"Combined analysis file not found: {self.combined_analysis_file}")
        
        if not os.path.exists(self.combined_chart):
            issues.append(f"Combined strategy chart not found: {self.combined_chart}")
        
        return issues
    
    def load_analysis_data(self):
        """Load the latest combined strategy analysis results"""
        try:
            # Load combined analysis data
            combined_data = pd.read_csv(self.combined_analysis_file) if os.path.exists(self.combined_analysis_file) else pd.DataFrame()
            
            # Load individual strategy files (if available)
            consensus_signals = pd.read_csv(self.consensus_signals_file) if os.path.exists(self.consensus_signals_file) else pd.DataFrame()
            momentum_signals = pd.read_csv(self.momentum_signals_file) if os.path.exists(self.momentum_signals_file) else pd.DataFrame()
            mean_reversion_signals = pd.read_csv(self.mean_reversion_signals_file) if os.path.exists(self.mean_reversion_signals_file) else pd.DataFrame()
            contrarian_signals = pd.read_csv(self.contrarian_signals_file) if os.path.exists(self.contrarian_signals_file) else pd.DataFrame()
            
            # Load stock metadata
            stock_metadata = []
            if os.path.exists(self.stocks_metadata_file):
                with open(self.stocks_metadata_file, 'r') as f:
                    stock_metadata = json.load(f)
            
            return {
                'combined': combined_data,
                'consensus': consensus_signals,
                'momentum': momentum_signals,
                'mean_reversion': mean_reversion_signals,
                'contrarian': contrarian_signals,
                'metadata': stock_metadata
            }
            
        except Exception as e:
            print(f"❌ Error loading analysis data: {e}")
            return {
                'combined': pd.DataFrame(),
                'consensus': pd.DataFrame(),
                'momentum': pd.DataFrame(),
                'mean_reversion': pd.DataFrame(),
                'contrarian': pd.DataFrame(),
                'metadata': []
            }

    def image_to_base64(self, image_path):
        """Convert image to base64 string for HTML embedding"""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            print(f"⚠️ Error converting {image_path} to base64: {e}")
            return None

    def generate_html_email(self, analysis_data):
        """Generate HTML email content with embedded charts"""
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        
        # Extract data from analysis_data
        combined_data = analysis_data['combined']
        consensus_signals = analysis_data['consensus']
        momentum_signals = analysis_data['momentum']
        mean_reversion_signals = analysis_data['mean_reversion']
        contrarian_signals = analysis_data['contrarian']
        stock_metadata = analysis_data['metadata']
        
        # Get top buy and sell signals from combined data
        top_buy_signals = combined_data.nlargest(10, 'Combined_Buy_Signal') if not combined_data.empty else pd.DataFrame()
        top_sell_signals = combined_data.nlargest(10, 'Combined_Sell_Signal') if not combined_data.empty else pd.DataFrame()
        
        # Convert charts to base64 for embedding
        print("🖼️ Converting PNG charts to base64...")
        combined_chart_b64 = self.image_to_base64(self.combined_chart) if os.path.exists(self.combined_chart) else None
        # Fallback to old charts if combined chart not available
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
                <h2>📊 Combined Strategy Analysis Summary</h2>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-label">Stocks Analyzed</div>
                        <div class="metric-value">{len(combined_data)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Strong Buy Signals</div>
                        <div class="metric-value" style="color: #28a745;">{len(top_buy_signals)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Strong Sell Signals</div>
                        <div class="metric-value" style="color: #dc3545;">{len(top_sell_signals)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Consensus Signals</div>
                        <div class="metric-value" style="color: #6f42c1;">{len(consensus_signals)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Momentum Signals</div>
                        <div class="metric-value" style="color: #fd7e14;">{len(momentum_signals)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Mean Reversion</div>
                        <div class="metric-value" style="color: #20c997;">{len(mean_reversion_signals)}</div>
                    </div>
                </div>
                <p style="margin-top: 20px; color: #6c757d;">
                    <strong>Strategies:</strong> Mean Reversion + Momentum Analysis &nbsp;•&nbsp; 
                    <strong>Sources:</strong> S&P 500, NASDAQ 100, Most Active, Recent IPOs &nbsp;•&nbsp;
                    <strong>Confidence Scoring:</strong> Multi-strategy validation
                </p>
            </div>"""

        # Combined Strategy Chart
        if combined_chart_b64:
            html_content += f"""
            <div class="chart-container">
                <h3>📊 Combined Strategy Analysis Dashboard</h3>
                <img src="data:image/png;base64,{combined_chart_b64}" alt="Combined Strategy Analysis Chart" />
            </div>"""
        elif overview_chart_b64:
            html_content += f"""
            <div class="chart-container">
                <h3>📊 Market Overview</h3>
                <img src="data:image/png;base64,{overview_chart_b64}" alt="Market Overview Chart" />
            </div>"""

        # Buy Signals Section
        if not top_buy_signals.empty:
            html_content += """
            <div class="signals-section buy-signals">
                <div class="section-header">
                    <h2>🟢 Top Combined Buy Signals</h2>
                </div>
                <table class="signal-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Price</th>
                            <th>Buy Signal</th>
                            <th>Strategy Type</th>
                            <th>Confidence</th>
                            <th>RSI</th>
                        </tr>
                    </thead>
                    <tbody>"""
            
            for _, row in top_buy_signals.head(8).iterrows():
                # Determine strategy type color
                strategy_color = {
                    'CONSENSUS': '#6f42c1',
                    'MOMENTUM': '#fd7e14', 
                    'MEAN_REVERSION': '#20c997',
                    'CONTRARIAN': '#ffc107',
                    'WEAK': '#6c757d'
                }.get(row['Strategy_Type'], '#6c757d')
                
                html_content += f"""
                        <tr class="buy-row">
                            <td class="symbol">{row['Symbol']}</td>
                            <td class="price">${row['Current_Price']:.2f}</td>
                            <td class="signal-strength">{row['Combined_Buy_Signal']:.3f}</td>
                            <td style="color: {strategy_color}; font-weight: 600;">{row['Strategy_Type']}</td>
                            <td class="signal-strength">{row['Confidence_Score']:.2f}</td>
                            <td class="rsi">{row['RSI']:.1f}</td>
                        </tr>"""
            
            html_content += """
                    </tbody>
                </table>
            </div>"""

        # Sell Signals Section
        if not top_sell_signals.empty:
            html_content += """
            <div class="signals-section sell-signals">
                <div class="section-header">
                    <h2>🔴 Top Combined Sell Signals</h2>
                </div>
                <table class="signal-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Price</th>
                            <th>Sell Signal</th>
                            <th>Strategy Type</th>
                            <th>Confidence</th>
                            <th>RSI</th>
                        </tr>
                    </thead>
                    <tbody>"""
            
            for _, row in top_sell_signals.head(8).iterrows():
                # Determine strategy type color
                strategy_color = {
                    'CONSENSUS': '#6f42c1',
                    'MOMENTUM': '#fd7e14', 
                    'MEAN_REVERSION': '#20c997',
                    'CONTRARIAN': '#ffc107',
                    'WEAK': '#6c757d'
                }.get(row['Strategy_Type'], '#6c757d')
                
                html_content += f"""
                        <tr class="sell-row">
                            <td class="symbol">{row['Symbol']}</td>
                            <td class="price">${row['Current_Price']:.2f}</td>
                            <td class="signal-strength">{row['Combined_Sell_Signal']:.3f}</td>
                            <td style="color: {strategy_color}; font-weight: 600;">{row['Strategy_Type']}</td>
                            <td class="signal-strength">{row['Confidence_Score']:.2f}</td>
                            <td class="rsi">{row['RSI']:.1f}</td>
                        </tr>"""
            
            html_content += """
                    </tbody>
                </table>
            </div>"""

        # Tips and Footer
        html_content += """
            <div class="tips">
                <h3>💡 Combined Strategy Trading Tips</h3>
                <ul>
                    <li><strong>Consensus Signals:</strong> Both mean reversion and momentum agree - highest confidence</li>
                    <li><strong>Momentum Signals:</strong> Trend-following opportunities with strong directional bias</li>
                    <li><strong>Mean Reversion:</strong> Contrarian plays expecting price normalization</li>
                    <li><strong>Contrarian Signals:</strong> Strategies disagree - high risk but potential high reward</li>
                    <li><strong>Risk Management:</strong> Always use stop-losses and proper position sizing</li>
                    <li><strong>Confidence Scores:</strong> Higher scores indicate stronger signal validation</li>
                </ul>
            </div>
            
            <div class="embedded-note">
                <h4>📊 Combined Strategy Dashboard</h4>
                <p>This email contains the comprehensive combined strategy analysis dashboard:</p>
                <ul>
                    <li><strong>Buy/Sell Signal Charts:</strong> Top opportunities from both strategies</li>
                    <li><strong>Strategy Distribution:</strong> Breakdown of signal types</li>
                    <li><strong>Signal Strength Analysis:</strong> Confidence-weighted recommendations</li>
                    <li><strong>Multi-Strategy Validation:</strong> Enhanced accuracy through strategy combination</li>
                </ul>
                <p><em>All charts embedded as base64 images - no external files needed!</em></p>
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
            print("📊 Loading combined strategy analysis data...")
            analysis_data = self.load_analysis_data()
            
            if analysis_data['combined'].empty:
                print("❌ No combined analysis data found")
                return False
            
            # Generate HTML content with embedded charts
            print("📝 Generating HTML email with embedded charts...")
            html_content = self.generate_html_email(analysis_data)
            
            # Save HTML content
            html_file = os.path.join(self.output_dir, 'gmail_embedded_email.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ HTML email with embedded charts saved to {html_file}")
            
            # Extract data for text summary
            combined_data = analysis_data['combined']
            top_buy_signals = combined_data.nlargest(5, 'Combined_Buy_Signal')
            top_sell_signals = combined_data.nlargest(5, 'Combined_Sell_Signal')
            strategy_counts = combined_data['Strategy_Type'].value_counts()
            
            # Generate plain text summary
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
            text_content = f"""📈 COMBINED STRATEGY ANALYSIS REPORT - {current_date}
{'='*60}

📊 COMBINED STRATEGY SUMMARY:
• Total Stocks Analyzed: {len(combined_data)}
• Strong Buy Signals: {len(top_buy_signals)}
• Strong Sell Signals: {len(top_sell_signals)}
• Consensus Signals: {len(analysis_data['consensus'])}
• Momentum Signals: {len(analysis_data['momentum'])}
• Mean Reversion Signals: {len(analysis_data['mean_reversion'])}
• Data Sources: S&P 500, NASDAQ 100, Most Active, Recent IPOs
• Strategies: Mean Reversion + Momentum Analysis

🎯 STRATEGY BREAKDOWN:
{'-'*50}
"""
            
            for strategy, count in strategy_counts.items():
                percentage = (count / len(combined_data)) * 100
                text_content += f"• {strategy.replace('_', ' ')}: {count} stocks ({percentage:.1f}%)\n"
            
            text_content += f"""
🟢 TOP 5 COMBINED BUY SIGNALS:
{'-'*50}
"""
            
            if not top_buy_signals.empty:
                for i, (_, row) in enumerate(top_buy_signals.iterrows(), 1):
                    text_content += f"{i}. {row['Symbol']} - ${row['Current_Price']:.2f} | Signal: {row['Combined_Buy_Signal']:.3f} | Strategy: {row['Strategy_Type']} | Confidence: {row['Confidence_Score']:.2f} | RSI: {row['RSI']:.1f}\n"
            
            text_content += f"""
🔴 TOP 5 COMBINED SELL SIGNALS:
{'-'*50}
"""
            
            if not top_sell_signals.empty:
                for i, (_, row) in enumerate(top_sell_signals.iterrows(), 1):
                    text_content += f"{i}. {row['Symbol']} - ${row['Current_Price']:.2f} | Signal: {row['Combined_Sell_Signal']:.3f} | Strategy: {row['Strategy_Type']} | Confidence: {row['Confidence_Score']:.2f} | RSI: {row['RSI']:.1f}\n"
            
            text_content += f"""
💡 COMBINED STRATEGY TIPS:
• Consensus Signals: Both strategies agree - highest confidence
• Momentum Signals: Trend-following opportunities with directional bias
• Mean Reversion: Contrarian plays expecting price normalization
• Contrarian Signals: Strategies disagree - high risk/reward potential
• Risk Management: Always use stop-losses and position sizing
• Confidence Scores: Higher scores indicate stronger signal validation

🖼️ COMBINED STRATEGY DASHBOARD:
• Buy/Sell signal charts with strategy breakdown
• Strategy distribution and signal strength analysis
• Multi-strategy validation for enhanced accuracy
• All charts embedded in HTML - no separate files needed!

📧 Combined Strategy Analysis | Embedded Charts Version
⚠️  This is for educational purposes only. Not financial advice.
📊 Data sources: Yahoo Finance via yfinance library
"""
            
            # Save text content
            text_file = os.path.join(self.output_dir, 'gmail_embedded_email.txt')
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"✅ Text email content saved to {text_file}")
            
            # Create email subject
            subject = f"📈 Combined Strategy Analysis - {datetime.now().strftime('%Y-%m-%d')} (Multi-Strategy Dashboard)"
            subject_file = os.path.join(self.output_dir, 'gmail_embedded_subject.txt')
            with open(subject_file, 'w', encoding='utf-8') as f:
                f.write(subject)
            print(f"✅ Email subject saved to {subject_file}")
            
            # Show file summary
            print(f"\n📋 Email Content Summary:")
            print(f"   📧 Subject: {subject}")
            print(f"   📄 Recipients: {self.to_email}")
            print(f"   📊 Combined signals: {len(combined_data)} stocks analyzed")
            print(f"   🎯 Strategy breakdown: {len(analysis_data['consensus'])} consensus, {len(analysis_data['momentum'])} momentum, {len(analysis_data['mean_reversion'])} mean reversion")
            print(f"   🖼️ Embedded charts: Combined strategy dashboard with buy/sell signals")
            
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
        print("   📊 Generate combined strategy analysis first:")
        print("      python src/combined_strategy_analysis.py")
        
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