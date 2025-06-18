import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
import time
import json
import os
from mean_reversion_algorithms import MeanReversionAlgorithms
from momentum_algorithms import MomentumAlgorithms
warnings.filterwarnings('ignore')

class CombinedStrategyAnalysis:
    def __init__(self, lookback_days=252, num_stocks=100):
        self.lookback_days = lookback_days
        self.num_stocks = num_stocks
        self.output_dir = 'output'
        
        # Initialize both analyzers
        self.mean_reversion_analyzer = MeanReversionAlgorithms(lookback_days, num_stocks)
        self.momentum_analyzer = MomentumAlgorithms(lookback_days, num_stocks)
        
        # Results storage
        self.combined_signals_df = None
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def run_combined_analysis(self, force_refresh_stocks=False):
        """Run both mean reversion and momentum analysis"""
        print("🚀 COMBINED STRATEGY ANALYSIS: Mean Reversion + Momentum")
        print("=" * 80)
        
        # Run mean reversion analysis (silently to avoid duplicate output)
        print("\n📈 Running Mean Reversion Analysis...")
        mr_buy_signals, mr_sell_signals = self.mean_reversion_analyzer.run_analysis(force_refresh_stocks, silent=True)
        
        # Run momentum analysis (silently to avoid duplicate output)
        print("\n📊 Running Momentum Analysis...")
        mom_buy_signals, mom_sell_signals = self.momentum_analyzer.run_momentum_analysis(force_refresh_stocks, silent=True)
        
        # Combine the results
        print("\n🔄 Combining Strategy Results...")
        self.combine_strategies(mr_buy_signals, mr_sell_signals, mom_buy_signals, mom_sell_signals)
        
        return self.combined_signals_df
    
    def combine_strategies(self, mr_buy, mr_sell, mom_buy, mom_sell):
        """Combine mean reversion and momentum signals"""
        
        # Get all unique symbols
        all_symbols = set()
        all_symbols.update(mr_buy['Symbol'].tolist())
        all_symbols.update(mr_sell['Symbol'].tolist())
        all_symbols.update(mom_buy['Symbol'].tolist())
        all_symbols.update(mom_sell['Symbol'].tolist())
        
        combined_results = []
        
        for symbol in all_symbols:
            # Get mean reversion signals
            mr_buy_row = mr_buy[mr_buy['Symbol'] == symbol]
            mr_sell_row = mr_sell[mr_sell['Symbol'] == symbol]
            
            mr_buy_strength = mr_buy_row['Buy_Signal_Strength'].iloc[0] if len(mr_buy_row) > 0 else 0
            mr_sell_strength = mr_sell_row['Sell_Signal_Strength'].iloc[0] if len(mr_sell_row) > 0 else 0
            
            # Get momentum signals
            mom_buy_row = mom_buy[mom_buy['Symbol'] == symbol]
            mom_sell_row = mom_sell[mom_sell['Symbol'] == symbol]
            
            mom_buy_strength = mom_buy_row['Momentum_Buy_Signal'].iloc[0] if len(mom_buy_row) > 0 else 0
            mom_sell_strength = mom_sell_row['Momentum_Sell_Signal'].iloc[0] if len(mom_sell_row) > 0 else 0
            
            # Get current price (from either dataset)
            current_price = 0
            rsi = 0
            if len(mr_buy_row) > 0:
                current_price = mr_buy_row['Current_Price'].iloc[0]
                rsi = mr_buy_row['RSI'].iloc[0]
            elif len(mr_sell_row) > 0:
                current_price = mr_sell_row['Current_Price'].iloc[0]
                rsi = mr_sell_row['RSI'].iloc[0]
            elif len(mom_buy_row) > 0:
                current_price = mom_buy_row['Current_Price'].iloc[0]
                rsi = mom_buy_row['RSI'].iloc[0]
            elif len(mom_sell_row) > 0:
                current_price = mom_sell_row['Current_Price'].iloc[0]
                rsi = mom_sell_row['RSI'].iloc[0]
            
            # Calculate combined signals
            combined_buy_signal = self.calculate_combined_buy_signal(mr_buy_strength, mom_buy_strength)
            combined_sell_signal = self.calculate_combined_sell_signal(mr_sell_strength, mom_sell_strength)
            
            # Determine strategy recommendation
            strategy_type = self.determine_strategy_type(mr_buy_strength, mr_sell_strength, 
                                                       mom_buy_strength, mom_sell_strength)
            
            # Calculate confidence score
            confidence = self.calculate_confidence_score(mr_buy_strength, mr_sell_strength,
                                                       mom_buy_strength, mom_sell_strength)
            
            combined_results.append({
                'Symbol': symbol,
                'Current_Price': current_price,
                'RSI': rsi,
                'MR_Buy_Signal': mr_buy_strength,
                'MR_Sell_Signal': mr_sell_strength,
                'Mom_Buy_Signal': mom_buy_strength,
                'Mom_Sell_Signal': mom_sell_strength,
                'Combined_Buy_Signal': combined_buy_signal,
                'Combined_Sell_Signal': combined_sell_signal,
                'Strategy_Type': strategy_type,
                'Confidence_Score': confidence,
                'Signal_Strength': max(combined_buy_signal, combined_sell_signal)
            })
        
        self.combined_signals_df = pd.DataFrame(combined_results)
        
        # Generate comprehensive report
        self.generate_combined_report()
        
        return self.combined_signals_df
    
    def calculate_combined_buy_signal(self, mr_buy, mom_buy):
        """Calculate combined buy signal strength"""
        # Strategy 1: Both strategies agree (strongest signal)
        if mr_buy > 0.5 and mom_buy > 0.5:
            return (mr_buy + mom_buy) / 2 * 1.2  # Boost when both agree
        
        # Strategy 2: Momentum breakout with mean reversion support
        elif mom_buy > 0.7 and mr_buy > 0.2:
            return mom_buy * 0.8 + mr_buy * 0.2
        
        # Strategy 3: Strong mean reversion with some momentum
        elif mr_buy > 0.7 and mom_buy > 0.1:
            return mr_buy * 0.8 + mom_buy * 0.2
        
        # Strategy 4: Individual strong signals
        elif mr_buy > 0.6 or mom_buy > 0.6:
            return max(mr_buy, mom_buy) * 0.8
        
        # Weak signals
        else:
            return (mr_buy + mom_buy) / 2 * 0.6
    
    def calculate_combined_sell_signal(self, mr_sell, mom_sell):
        """Calculate combined sell signal strength"""
        # Strategy 1: Both strategies agree (strongest signal)
        if mr_sell > 0.5 and mom_sell > 0.5:
            return (mr_sell + mom_sell) / 2 * 1.2  # Boost when both agree
        
        # Strategy 2: Momentum breakdown with mean reversion resistance
        elif mom_sell > 0.7 and mr_sell > 0.2:
            return mom_sell * 0.8 + mr_sell * 0.2
        
        # Strategy 3: Strong mean reversion with some momentum
        elif mr_sell > 0.7 and mom_sell > 0.1:
            return mr_sell * 0.8 + mom_sell * 0.2
        
        # Strategy 4: Individual strong signals
        elif mr_sell > 0.6 or mom_sell > 0.6:
            return max(mr_sell, mom_sell) * 0.8
        
        # Weak signals
        else:
            return (mr_sell + mom_sell) / 2 * 0.6
    
    def determine_strategy_type(self, mr_buy, mr_sell, mom_buy, mom_sell):
        """Determine the primary strategy type for the signal"""
        
        # Both strategies strongly agree
        if (mr_buy > 0.5 and mom_buy > 0.5) or (mr_sell > 0.5 and mom_sell > 0.5):
            return "CONSENSUS"
        
        # Momentum dominant
        elif max(mom_buy, mom_sell) > max(mr_buy, mr_sell) and max(mom_buy, mom_sell) > 0.5:
            return "MOMENTUM"
        
        # Mean reversion dominant
        elif max(mr_buy, mr_sell) > max(mom_buy, mom_sell) and max(mr_buy, mr_sell) > 0.5:
            return "MEAN_REVERSION"
        
        # Contrarian (momentum and mean reversion disagree)
        elif (mr_buy > 0.4 and mom_sell > 0.4) or (mr_sell > 0.4 and mom_buy > 0.4):
            return "CONTRARIAN"
        
        # Weak signals
        else:
            return "WEAK"
    
    def calculate_confidence_score(self, mr_buy, mr_sell, mom_buy, mom_sell):
        """Calculate confidence score for the combined signal"""
        
        # High confidence when both strategies agree
        if (mr_buy > 0.5 and mom_buy > 0.5) or (mr_sell > 0.5 and mom_sell > 0.5):
            return 0.9
        
        # Medium-high confidence for strong individual signals
        elif max(mr_buy, mr_sell, mom_buy, mom_sell) > 0.7:
            return 0.75
        
        # Medium confidence for moderate signals
        elif max(mr_buy, mr_sell, mom_buy, mom_sell) > 0.5:
            return 0.6
        
        # Lower confidence for contrarian signals
        elif (mr_buy > 0.3 and mom_sell > 0.3) or (mr_sell > 0.3 and mom_buy > 0.3):
            return 0.4
        
        # Low confidence for weak signals
        else:
            return 0.3
    
    def generate_combined_report(self):
        """Generate comprehensive combined strategy report"""
        
        if self.combined_signals_df is None or len(self.combined_signals_df) == 0:
            print("No combined signals to report!")
            return
        
        # Sort by signal strength
        sorted_df = self.combined_signals_df.sort_values('Signal_Strength', ascending=False)
        
        # Get top signals by strategy type
        consensus_signals = sorted_df[sorted_df['Strategy_Type'] == 'CONSENSUS'].head(10)
        momentum_signals = sorted_df[sorted_df['Strategy_Type'] == 'MOMENTUM'].head(10)
        mean_reversion_signals = sorted_df[sorted_df['Strategy_Type'] == 'MEAN_REVERSION'].head(10)
        contrarian_signals = sorted_df[sorted_df['Strategy_Type'] == 'CONTRARIAN'].head(5)
        
        # Display results
        print("\n" + "="*100)
        print("🎯 COMBINED STRATEGY ANALYSIS RESULTS")
        print("="*100)
        
        if len(consensus_signals) > 0:
            print("\n🔥 TOP 10 CONSENSUS SIGNALS (Both Strategies Agree)")
            print("-" * 80)
            print(consensus_signals[['Symbol', 'Current_Price', 'Combined_Buy_Signal', 'Combined_Sell_Signal', 
                                   'Strategy_Type', 'Confidence_Score']].round(3).to_string(index=False))
        
        if len(momentum_signals) > 0:
            print("\n📈 TOP 10 MOMENTUM-DRIVEN SIGNALS")
            print("-" * 80)
            print(momentum_signals[['Symbol', 'Current_Price', 'Mom_Buy_Signal', 'Mom_Sell_Signal', 
                                  'Confidence_Score']].round(3).to_string(index=False))
        
        if len(mean_reversion_signals) > 0:
            print("\n🔄 TOP 10 MEAN REVERSION SIGNALS")
            print("-" * 80)
            print(mean_reversion_signals[['Symbol', 'Current_Price', 'MR_Buy_Signal', 'MR_Sell_Signal', 
                                        'Confidence_Score']].round(3).to_string(index=False))
        
        if len(contrarian_signals) > 0:
            print("\n⚡ TOP 5 CONTRARIAN SIGNALS (Strategies Disagree - High Risk/Reward)")
            print("-" * 80)
            print(contrarian_signals[['Symbol', 'Current_Price', 'MR_Buy_Signal', 'MR_Sell_Signal',
                                    'Mom_Buy_Signal', 'Mom_Sell_Signal', 'Confidence_Score']].round(3).to_string(index=False))
        
        # Strategy distribution
        strategy_counts = self.combined_signals_df['Strategy_Type'].value_counts()
        print(f"\n📊 STRATEGY DISTRIBUTION:")
        print("-" * 40)
        for strategy, count in strategy_counts.items():
            percentage = (count / len(self.combined_signals_df)) * 100
            print(f"{strategy}: {count} stocks ({percentage:.1f}%)")
        
        # Save results
        self.save_combined_results(consensus_signals, momentum_signals, mean_reversion_signals, contrarian_signals)
    
    def save_combined_results(self, consensus, momentum, mean_reversion, contrarian):
        """Save combined analysis results to files"""
        
        # Save individual strategy results
        consensus.to_csv(os.path.join(self.output_dir, 'consensus_signals.csv'), index=False)
        momentum.to_csv(os.path.join(self.output_dir, 'momentum_dominant_signals.csv'), index=False)
        mean_reversion.to_csv(os.path.join(self.output_dir, 'mean_reversion_dominant_signals.csv'), index=False)
        contrarian.to_csv(os.path.join(self.output_dir, 'contrarian_signals.csv'), index=False)
        
        # Save complete combined results
        self.combined_signals_df.to_csv(os.path.join(self.output_dir, 'combined_strategy_analysis.csv'), index=False)
        
        print(f"\n💾 RESULTS SAVED:")
        print(f"- Consensus signals: consensus_signals.csv")
        print(f"- Momentum dominant: momentum_dominant_signals.csv") 
        print(f"- Mean reversion dominant: mean_reversion_dominant_signals.csv")
        print(f"- Contrarian signals: contrarian_signals.csv")
        print(f"- Complete analysis: combined_strategy_analysis.csv")
    
    def plot_combined_analysis(self):
        """Create comprehensive visualization of combined analysis results with clear buy/sell signals"""
        if self.combined_signals_df is None:
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(24, 16))
        
        # Get top buy and sell signals
        top_buy_signals = self.combined_signals_df.nlargest(15, 'Combined_Buy_Signal')
        top_sell_signals = self.combined_signals_df.nlargest(15, 'Combined_Sell_Signal')
        
        # Plot 1: Top Buy Signals
        ax1 = axes[0, 0]
        if len(top_buy_signals) > 0:
            buy_bars = ax1.barh(range(len(top_buy_signals[:10])), 
                               top_buy_signals['Combined_Buy_Signal'][:10], 
                               color='green', alpha=0.8)
            ax1.set_yticks(range(len(top_buy_signals[:10])))
            ax1.set_yticklabels(top_buy_signals['Symbol'][:10])
            ax1.set_xlabel('Combined Buy Signal Strength')
            ax1.set_title('🟢 TOP 10 BUY SIGNALS', fontsize=14, fontweight='bold', color='green')
            ax1.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(buy_bars, top_buy_signals['Combined_Buy_Signal'][:10])):
                ax1.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                        f'{value:.2f}', ha='left', va='center', fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'No Strong Buy Signals', ha='center', va='center', 
                    transform=ax1.transAxes, fontsize=12)
            ax1.set_title('🟢 TOP 10 BUY SIGNALS', fontsize=14, fontweight='bold')
        
        # Plot 2: Top Sell Signals
        ax2 = axes[0, 1]
        if len(top_sell_signals) > 0:
            sell_bars = ax2.barh(range(len(top_sell_signals[:10])), 
                                top_sell_signals['Combined_Sell_Signal'][:10], 
                                color='red', alpha=0.8)
            ax2.set_yticks(range(len(top_sell_signals[:10])))
            ax2.set_yticklabels(top_sell_signals['Symbol'][:10])
            ax2.set_xlabel('Combined Sell Signal Strength')
            ax2.set_title('🔴 TOP 10 SELL SIGNALS', fontsize=14, fontweight='bold', color='red')
            ax2.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(sell_bars, top_sell_signals['Combined_Sell_Signal'][:10])):
                ax2.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                        f'{value:.2f}', ha='left', va='center', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No Strong Sell Signals', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=12)
            ax2.set_title('🔴 TOP 10 SELL SIGNALS', fontsize=14, fontweight='bold')
        
        # Plot 3: Strategy Type Distribution
        ax3 = axes[0, 2]
        strategy_counts = self.combined_signals_df['Strategy_Type'].value_counts()
        colors = ['#2E8B57', '#FF6347', '#4169E1', '#FFD700', '#8A2BE2']
        wedges, texts, autotexts = ax3.pie(strategy_counts.values, labels=strategy_counts.index, 
                                          autopct='%1.1f%%', colors=colors[:len(strategy_counts)])
        ax3.set_title('📊 Strategy Type Distribution', fontsize=14, fontweight='bold')
        
        # Plot 4: Buy vs Sell Signal Strength Scatter
        ax4 = axes[1, 0]
        scatter = ax4.scatter(self.combined_signals_df['Combined_Buy_Signal'], 
                             self.combined_signals_df['Combined_Sell_Signal'],
                             c=self.combined_signals_df['Confidence_Score'],
                             alpha=0.7, s=80, cmap='RdYlGn', edgecolors='black', linewidth=0.5)
        ax4.set_xlabel('Combined Buy Signal Strength')
        ax4.set_ylabel('Combined Sell Signal Strength')
        ax4.set_title('📈 Buy vs Sell Signal Strength', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # Add quadrant labels
        ax4.text(0.8, 0.8, 'HIGH SELL\nLOW BUY', transform=ax4.transAxes, 
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="red", alpha=0.3))
        ax4.text(0.8, 0.2, 'HIGH BUY\nLOW SELL', transform=ax4.transAxes, 
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="green", alpha=0.3))
        
        plt.colorbar(scatter, ax=ax4, label='Confidence Score')
        
        # Plot 5: Mean Reversion vs Momentum Signals
        ax5 = axes[1, 1]
        mr_signals = self.combined_signals_df['MR_Buy_Signal'] - self.combined_signals_df['MR_Sell_Signal']
        mom_signals = self.combined_signals_df['Mom_Buy_Signal'] - self.combined_signals_df['Mom_Sell_Signal']
        
        scatter = ax5.scatter(mr_signals, mom_signals, 
                             c=self.combined_signals_df['Signal_Strength'],
                             alpha=0.7, s=80, cmap='viridis', edgecolors='black', linewidth=0.5)
        ax5.set_xlabel('Mean Reversion Signal (Buy - Sell)')
        ax5.set_ylabel('Momentum Signal (Buy - Sell)')
        ax5.set_title('🔄 Mean Reversion vs Momentum', fontsize=14, fontweight='bold')
        ax5.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax5.axvline(x=0, color='k', linestyle='--', alpha=0.5)
        ax5.grid(True, alpha=0.3)
        
        # Add quadrant labels
        ax5.text(0.8, 0.8, 'MOMENTUM\nBUY', transform=ax5.transAxes, 
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
        ax5.text(0.2, 0.8, 'CONTRARIAN\nSIGNALS', transform=ax5.transAxes, 
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        ax5.text(0.8, 0.2, 'CONTRARIAN\nSIGNALS', transform=ax5.transAxes, 
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        ax5.text(0.2, 0.2, 'MEAN REV\nBUY', transform=ax5.transAxes, 
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
        
        plt.colorbar(scatter, ax=ax5, label='Overall Signal Strength')
        
        # Plot 6: Top Consensus Signals (if any)
        ax6 = axes[1, 2]
        consensus_signals = self.combined_signals_df[self.combined_signals_df['Strategy_Type'] == 'CONSENSUS']
        if len(consensus_signals) > 0:
            top_consensus = consensus_signals.nlargest(10, 'Signal_Strength')
            bars = ax6.barh(range(len(top_consensus)), top_consensus['Signal_Strength'], 
                           color='purple', alpha=0.8)
            ax6.set_yticks(range(len(top_consensus)))
            ax6.set_yticklabels(top_consensus['Symbol'])
            ax6.set_xlabel('Combined Signal Strength')
            ax6.set_title('🎯 TOP CONSENSUS SIGNALS', fontsize=14, fontweight='bold', color='purple')
            ax6.grid(True, alpha=0.3)
            
            # Add value labels
            for i, (bar, value) in enumerate(zip(bars, top_consensus['Signal_Strength'])):
                ax6.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                        f'{value:.2f}', ha='left', va='center', fontweight='bold')
        else:
            # Show top momentum signals instead
            momentum_signals = self.combined_signals_df[self.combined_signals_df['Strategy_Type'] == 'MOMENTUM']
            if len(momentum_signals) > 0:
                top_momentum = momentum_signals.nlargest(8, 'Signal_Strength')
                bars = ax6.barh(range(len(top_momentum)), top_momentum['Signal_Strength'], 
                               color='orange', alpha=0.8)
                ax6.set_yticks(range(len(top_momentum)))
                ax6.set_yticklabels(top_momentum['Symbol'])
                ax6.set_xlabel('Signal Strength')
                ax6.set_title('🚀 TOP MOMENTUM SIGNALS', fontsize=14, fontweight='bold', color='orange')
                ax6.grid(True, alpha=0.3)
                
                # Add value labels
                for i, (bar, value) in enumerate(zip(bars, top_momentum['Signal_Strength'])):
                    ax6.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                            f'{value:.2f}', ha='left', va='center', fontweight='bold')
            else:
                ax6.text(0.5, 0.5, 'No Strong Signals Found', ha='center', va='center', 
                        transform=ax6.transAxes, fontsize=12)
                ax6.set_title('🎯 TOP SIGNALS', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'combined_strategy_analysis.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\n📊 Visualization saved: {output_path}")
        
        # Print summary of top signals
        print(f"\n📈 TOP BUY SIGNALS SUMMARY:")
        print("-" * 50)
        if len(top_buy_signals) > 0:
            for i, row in top_buy_signals.head(5).iterrows():
                print(f"  {row['Symbol']}: ${row['Current_Price']:.2f} | Signal: {row['Combined_Buy_Signal']:.3f} | {row['Strategy_Type']}")
        else:
            print("  No strong buy signals found")
        
        print(f"\n📉 TOP SELL SIGNALS SUMMARY:")
        print("-" * 50)
        if len(top_sell_signals) > 0:
            for i, row in top_sell_signals.head(5).iterrows():
                print(f"  {row['Symbol']}: ${row['Current_Price']:.2f} | Signal: {row['Combined_Sell_Signal']:.3f} | {row['Strategy_Type']}")
        else:
            print("  No strong sell signals found")

def main():
    """Main function for combined strategy analysis"""
    import sys
    
    force_refresh = '--refresh' in sys.argv
    
    if force_refresh:
        print("🔄 Force refresh mode: Will fetch fresh stock list from all sources")
    else:
        print("📂 Cache mode: Will use existing top_stocks.json if available")
    
    # Initialize combined analyzer
    combined_analyzer = CombinedStrategyAnalysis(lookback_days=252, num_stocks=100)
    
    # Run combined analysis
    combined_results = combined_analyzer.run_combined_analysis(force_refresh_stocks=force_refresh)
    
    # Generate visualizations
    combined_analyzer.plot_combined_analysis()
    
    print("\n" + "="*80)
    print("🎉 COMBINED STRATEGY ANALYSIS COMPLETE!")
    print("="*80)
    print("✅ Mean reversion analysis completed")
    print("✅ Momentum analysis completed") 
    print("✅ Strategies combined and analyzed")
    print("✅ Comprehensive reports generated")
    print("✅ Results saved to CSV files")
    print("✅ Visualizations created")
    
    print(f"\n📈 Total stocks analyzed: {len(combined_results)}")
    print(f"🎯 Strategy recommendations generated for all stocks")
    
    print("\n💡 Tip: Use 'python combined_strategy_analysis.py --refresh' to force fetch fresh stocks")

if __name__ == "__main__":
    main() 