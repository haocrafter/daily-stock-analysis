#!/usr/bin/env python3
"""
🚀 Glowing Vibe Demo Script
Demonstrates all the trading algorithms and their capabilities
"""

import os
import sys
import time
from datetime import datetime

# Add src directory to path for imports
sys.path.append('src')

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f"🎯 {title}")
    print("="*80)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n📊 {title}")
    print("-" * 60)

def main():
    """Main demo function"""
    print_header("GLOWING VIBE TRADING ALGORITHMS DEMO")
    
    print("Welcome to the comprehensive trading analysis platform!")
    print("This demo will show you all available algorithms and their capabilities.")
    
    # Menu options
    while True:
        print_section("AVAILABLE ALGORITHMS")
        print("1. 📈 Mean Reversion Analysis (Oversold/Overbought Detection)")
        print("2. 🚀 Momentum Analysis (Trend Following)")
        print("3. 🎯 Combined Strategy Analysis (Best of Both Worlds)")
        print("4. 📧 Email Report Generation")
        print("5. 🔍 View Latest Analysis Results")
        print("6. ❓ Help & Documentation")
        print("7. 🚪 Exit")
        
        choice = input("\nSelect an option (1-7): ").strip()
        
        if choice == '1':
            run_mean_reversion_demo()
        elif choice == '2':
            run_momentum_demo()
        elif choice == '3':
            run_combined_demo()
        elif choice == '4':
            run_email_demo()
        elif choice == '5':
            view_results()
        elif choice == '6':
            show_help()
        elif choice == '7':
            print("\n👋 Thanks for using Glowing Vibe! Happy trading!")
            break
        else:
            print("❌ Invalid choice. Please select 1-7.")

def run_mean_reversion_demo():
    """Demonstrate mean reversion analysis"""
    print_header("MEAN REVERSION ANALYSIS DEMO")
    
    print("📋 Mean Reversion Strategy Overview:")
    print("• Identifies stocks that have moved significantly away from their average price")
    print("• Buy signals: Oversold conditions (low RSI, below Bollinger bands)")
    print("• Sell signals: Overbought conditions (high RSI, above Bollinger bands)")
    print("• Best for: Range-bound markets, contrarian plays")
    
    refresh = input("\n🔄 Force refresh stock data? (y/N): ").lower().strip() == 'y'
    
    print("\n🚀 Running Mean Reversion Analysis...")
    
    try:
        if refresh:
            os.system("python src/multi_stock_mean_reversion_dynamic.py --refresh")
        else:
            os.system("python src/multi_stock_mean_reversion_dynamic.py")
        
        print("\n✅ Mean Reversion Analysis Complete!")
        print("📁 Results saved to:")
        print("   • output/top_buy_signals.csv")
        print("   • output/top_sell_signals.csv") 
        print("   • output/dynamic_multi_stock_signals.png")
        
    except Exception as e:
        print(f"❌ Error running analysis: {e}")

def run_momentum_demo():
    """Demonstrate momentum analysis"""
    print_header("MOMENTUM ANALYSIS DEMO")
    
    print("📋 Momentum Strategy Overview:")
    print("• Identifies stocks with strong directional movement")
    print("• Buy signals: Upward momentum (RSI > 50, MACD crossovers, positive ROC)")
    print("• Sell signals: Downward momentum (RSI < 50, bearish MACD, negative ROC)")
    print("• Best for: Trending markets, breakout plays")
    
    refresh = input("\n🔄 Force refresh stock data? (y/N): ").lower().strip() == 'y'
    
    print("\n🚀 Running Momentum Analysis...")
    
    try:
        if refresh:
            os.system("python src/momentum_algorithms.py --refresh")
        else:
            os.system("python src/momentum_algorithms.py")
        
        print("\n✅ Momentum Analysis Complete!")
        print("📁 Results saved to:")
        print("   • output/top_momentum_buy_signals.csv")
        print("   • output/top_momentum_sell_signals.csv")
        
    except Exception as e:
        print(f"❌ Error running analysis: {e}")

def run_combined_demo():
    """Demonstrate combined strategy analysis"""
    print_header("COMBINED STRATEGY ANALYSIS DEMO")
    
    print("📋 Combined Strategy Overview:")
    print("• Intelligently combines mean reversion and momentum strategies")
    print("• CONSENSUS: Both strategies agree (highest confidence)")
    print("• MOMENTUM: Trend-following signals dominate")
    print("• MEAN_REVERSION: Contrarian signals dominate")
    print("• CONTRARIAN: Strategies disagree (high risk/reward)")
    
    refresh = input("\n🔄 Force refresh stock data? (y/N): ").lower().strip() == 'y'
    
    print("\n🚀 Running Combined Strategy Analysis...")
    print("⏳ This will run both mean reversion and momentum analysis...")
    
    try:
        if refresh:
            os.system("python src/combined_strategy_analysis.py --refresh")
        else:
            os.system("python src/combined_strategy_analysis.py")
        
        print("\n✅ Combined Strategy Analysis Complete!")
        print("📁 Results saved to:")
        print("   • output/combined_strategy_analysis.csv")
        print("   • output/consensus_signals.csv")
        print("   • output/momentum_dominant_signals.csv")
        print("   • output/mean_reversion_dominant_signals.csv")
        print("   • output/contrarian_signals.csv")
        print("   • output/combined_strategy_analysis.png")
        
    except Exception as e:
        print(f"❌ Error running analysis: {e}")

def run_email_demo():
    """Demonstrate email report generation"""
    print_header("EMAIL REPORT GENERATION DEMO")
    
    print("📋 Email Features:")
    print("• Professional HTML emails with embedded charts")
    print("• No external dependencies - charts embedded as base64")
    print("• Comprehensive analysis summary")
    print("• Trading tips and risk management guidance")
    
    print("\n🚀 Generating Email Report...")
    
    try:
        os.system("python src/email_sender_gmail_embedded.py")
        
        print("\n✅ Email Report Generated!")
        print("📁 Email files created:")
        print("   • output/gmail_embedded_email.html (Open in browser)")
        print("   • output/gmail_embedded_email.txt (Plain text version)")
        print("   • output/complete_email_message.eml (Email file)")
        
        view_email = input("\n👀 Open HTML email in browser? (y/N): ").lower().strip() == 'y'
        if view_email:
            os.system("open output/gmail_embedded_email.html")  # macOS
            # For Linux: os.system("xdg-open output/gmail_embedded_email.html")
            # For Windows: os.system("start output/gmail_embedded_email.html")
        
    except Exception as e:
        print(f"❌ Error generating email: {e}")

def view_results():
    """View latest analysis results"""
    print_header("LATEST ANALYSIS RESULTS")
    
    output_dir = "output"
    if not os.path.exists(output_dir):
        print("❌ No analysis results found. Run an analysis first!")
        return
    
    files = os.listdir(output_dir)
    csv_files = [f for f in files if f.endswith('.csv')]
    png_files = [f for f in files if f.endswith('.png')]
    
    if csv_files:
        print_section("CSV DATA FILES")
        for i, file in enumerate(csv_files, 1):
            file_path = os.path.join(output_dir, file)
            size = os.path.getsize(file_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"{i:2d}. {file:<35} ({size:,} bytes, {mod_time.strftime('%Y-%m-%d %H:%M')})")
    
    if png_files:
        print_section("CHART FILES")
        for i, file in enumerate(png_files, 1):
            file_path = os.path.join(output_dir, file)
            size = os.path.getsize(file_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"{i:2d}. {file:<35} ({size:,} bytes, {mod_time.strftime('%Y-%m-%d %H:%M')})")
    
    if csv_files:
        file_choice = input(f"\n📊 View a CSV file? Enter number (1-{len(csv_files)}) or press Enter to skip: ").strip()
        if file_choice.isdigit() and 1 <= int(file_choice) <= len(csv_files):
            file_to_view = csv_files[int(file_choice) - 1]
            print(f"\n📋 Contents of {file_to_view}:")
            print("-" * 80)
            try:
                with open(os.path.join(output_dir, file_to_view), 'r') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
                        print(f"{i:2d}: {line.rstrip()}")
                    if len(lines) > 20:
                        print(f"... and {len(lines) - 20} more lines")
            except Exception as e:
                print(f"❌ Error reading file: {e}")

def show_help():
    """Show help and documentation"""
    print_header("HELP & DOCUMENTATION")
    
    print_section("SIGNAL INTERPRETATION GUIDE")
    print("Signal Strength Scale:")
    print("• 0.8 - 1.0: Very Strong Signal (High Probability)")
    print("• 0.6 - 0.8: Strong Signal (Good Probability)")
    print("• 0.4 - 0.6: Moderate Signal (Medium Probability)")
    print("• 0.2 - 0.4: Weak Signal (Low Probability)")
    print("• 0.0 - 0.2: Very Weak Signal (Very Low Probability)")
    
    print_section("STRATEGY TYPES")
    print("• CONSENSUS: Both strategies agree (Highest Confidence)")
    print("• MOMENTUM: Trend-following signals dominate")
    print("• MEAN_REVERSION: Contrarian signals dominate")
    print("• CONTRARIAN: Strategies disagree (High risk/reward)")
    print("• WEAK: Low signal strength across all strategies")
    
    print_section("TECHNICAL INDICATORS")
    print("Mean Reversion Indicators:")
    print("• RSI (Relative Strength Index): Measures overbought/oversold")
    print("• Bollinger Bands: Price volatility bands")
    print("• Z-Score: Statistical measure of price deviation")
    print("• Volume Analysis: Confirms price movements")
    
    print("\nMomentum Indicators:")
    print("• MACD: Moving Average Convergence Divergence")
    print("• ROC: Rate of Change (price momentum)")
    print("• Moving Averages: Trend direction indicators")
    print("• Volume Momentum: Volume-based confirmations")
    
    print_section("RISK MANAGEMENT")
    print("⚠️  IMPORTANT DISCLAIMERS:")
    print("• This software is for educational purposes only")
    print("• Not financial advice - do your own research")
    print("• Always use stop-losses and position sizing")
    print("• Never invest more than you can afford to lose")
    print("• Past performance does not guarantee future results")
    
    print_section("COMMAND LINE USAGE")
    print("Individual Components:")
    print("• python src/multi_stock_mean_reversion_dynamic.py [--refresh]")
    print("• python src/momentum_algorithms.py [--refresh]")
    print("• python src/combined_strategy_analysis.py [--refresh]")
    print("• python src/email_sender_gmail_embedded.py")
    
    print("\nFlags:")
    print("• --refresh: Force fetch fresh stock data from all sources")
    print("• (no flag): Use cached stock data if available")

if __name__ == "__main__":
    main() 