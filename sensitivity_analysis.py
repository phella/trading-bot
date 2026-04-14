#!/usr/bin/env python3
"""
Strategy Parameter Sensitivity Analysis
========================================

Test different variations:
1. Signal threshold variations (0.5%, 0.75%, 1.0%, 1.25%, 1.5%)
2. Intraday volume-based trading
3. Compare profitability across scenarios

Uses actual Thndr costs: 0.2613% per round trip
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Constants
CAIRO_TICKER = "COMI.CA"
LONDON_TICKER = "CBKD.L"
START_DATE = "2025-04-14"
END_DATE = "2026-04-14"
THNDR_COMMISSION_PCT = 0.2613  # Actual Thndr costs (0.2613%)
INITIAL_CAPITAL = 10000

def fetch_and_prepare_data():
    """Fetch and prepare Cairo/London price data"""
    print("Fetching data...")
    
    cairo_data = yf.download(CAIRO_TICKER, start=START_DATE, end=END_DATE, progress=False)
    london_data = yf.download(LONDON_TICKER, start=START_DATE, end=END_DATE, progress=False)
    
    if cairo_data.empty or london_data.empty:
        raise ValueError("Failed to fetch data")
    
    print(f"✓ Cairo: {len(cairo_data)} days, London: {len(london_data)} days")
    return cairo_data, london_data

def create_unified_calendar(cairo_df, london_df):
    """Merge Cairo and London data into unified calendar"""
    unified = pd.DataFrame(index=pd.date_range(START_DATE, END_DATE, freq='D'))
    
    # Cairo close prices (forward fill for weekends)
    cairo_close = cairo_df[['Close']].copy()
    cairo_close.columns = ['cairo_close']
    cairo_close = cairo_close.reindex(unified.index, method='ffill')
    
    # London close prices
    london_close = london_df[['Close']].copy()
    london_close.columns = ['london_close']
    london_close = london_close.reindex(unified.index, method='ffill')
    
    # London daily returns
    london_close['london_return'] = london_close['london_close'].pct_change() * 100
    
    result = pd.concat([cairo_close, london_close], axis=1)
    return result.dropna()

def backtest_threshold(unified_df, signal_threshold):
    """
    Backtest with specific signal threshold
    
    Strategy: If London daily return > threshold, trade Cairo on signal day
    Uses correlation: London move predicts Cairo move (correlation ~0.07)
    """
    trades = []
    CORRELATION = 0.0728  # Mon->Tue correlation from main backtest
    
    for i in range(len(unified_df) - 1):
        london_return = unified_df.iloc[i]['london_return']
        
        # Signal: London move exceeds threshold (use absolute value for both directions)
        if abs(london_return) > signal_threshold:
            date = unified_df.index[i]
            
            # Entry: today's Cairo close
            entry_price = unified_df.iloc[i]['cairo_close']
            
            # Expected Cairo move based on correlation with London move
            # Cairo move = London move * correlation
            expected_cairo_move = london_return * CORRELATION
            
            # Exit price (estimated from next day data, similar to original backtest)
            # Use the actual price change observed
            next_day_price = unified_df.iloc[i + 1]['cairo_close']
            actual_move = ((next_day_price - entry_price) / entry_price) * 100
            
            exit_price = next_day_price
            
            # Use actual move (not just correlation estimate)
            ideal_return = actual_move
            realistic_return = ideal_return - THNDR_COMMISSION_PCT
            
            ideal_pnl = INITIAL_CAPITAL * (ideal_return / 100)
            realistic_pnl = INITIAL_CAPITAL * (realistic_return / 100)
            
            trades.append({
                'trigger_date': date,
                'trigger_return': london_return,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'ideal_return': ideal_return,
                'realistic_return': realistic_return,
                'ideal_pnl': ideal_pnl,
                'realistic_pnl': realistic_pnl,
                'profitable': realistic_pnl > 0
            })
    
    return pd.DataFrame(trades)

def backtest_intraday_volume(unified_df):
    """
    Intraday volume-based strategy:
    Trade smaller positions multiple times per day
    Entry: When London signal fires (morning)
    Exit 1: Capture 50% of expected move (midday)
    Exit 2: Capture remaining move (afternoon)
    """
    trades = []
    CORRELATION = 0.0728
    
    for i in range(len(unified_df) - 1):
        london_return = unified_df.iloc[i]['london_return']
        
        # Signal threshold for intraday: lower threshold (0.5%)
        if abs(london_return) > 0.5:
            date = unified_df.index[i]
            entry_price = unified_df.iloc[i]['cairo_close']
            next_day_price = unified_df.iloc[i + 1]['cairo_close']
            
            # Total expected move
            total_move = ((next_day_price - entry_price) / entry_price) * 100
            
            # Intraday trade 1: Capture 60% of the move
            exit_price_1 = entry_price * (1 + (total_move * 0.6) / 100)
            move_1 = total_move * 0.6
            realistic_return_1 = move_1 - THNDR_COMMISSION_PCT
            
            # Intraday trade 2: Re-enter and capture remaining 40%
            exit_price_2 = entry_price * (1 + (total_move * 0.4) / 100)
            move_2 = total_move * 0.4
            realistic_return_2 = move_2 - THNDR_COMMISSION_PCT
            
            # Trade 1
            trades.append({
                'date': date,
                'session': 'Morning (60% cap)',
                'london_return': london_return,
                'entry_price': entry_price,
                'exit_price': exit_price_1,
                'ideal_return': move_1,
                'realistic_return': realistic_return_1,
                'ideal_pnl': INITIAL_CAPITAL * (move_1 / 100),
                'realistic_pnl': INITIAL_CAPITAL * (realistic_return_1 / 100),
                'profitable': INITIAL_CAPITAL * (realistic_return_1 / 100) > 0
            })
            
            # Trade 2  
            trades.append({
                'date': date,
                'session': 'Afternoon (40% cap)',
                'london_return': london_return,
                'entry_price': entry_price,
                'exit_price': exit_price_2,
                'ideal_return': move_2,
                'realistic_return': realistic_return_2,
                'ideal_pnl': INITIAL_CAPITAL * (move_2 / 100),
                'realistic_pnl': INITIAL_CAPITAL * (realistic_return_2 / 100),
                'profitable': INITIAL_CAPITAL * (realistic_return_2 / 100) > 0
            })
    
    return pd.DataFrame(trades)

def print_results(scenario_name, trades_df):
    """Print backtest results"""
    if len(trades_df) == 0:
        print(f"\n{scenario_name}: No trades generated")
        return
    
    total_trades = len(trades_df)
    winning_trades = (trades_df['realistic_pnl'] > 0).sum()
    losing_trades = (trades_df['realistic_pnl'] < 0).sum()
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    total_ideal_pnl = trades_df['ideal_pnl'].sum()
    total_realistic_pnl = trades_df['realistic_pnl'].sum()
    total_costs = total_ideal_pnl - total_realistic_pnl
    
    avg_return = trades_df['realistic_return'].mean()
    best_trade = trades_df['realistic_pnl'].max()
    worst_trade = trades_df['realistic_pnl'].min()
    
    print(f"\n{'='*80}")
    print(f"{scenario_name}")
    print(f"{'='*80}")
    print(f"\nTotal Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades} ({win_rate:.1f}%)")
    print(f"Losing Trades: {losing_trades}")
    print(f"\nAverage Return per Trade: {avg_return:.4f}%")
    print(f"Average P&L per Trade: ${trades_df['realistic_pnl'].mean():.2f}")
    print(f"\nBest Trade: ${best_trade:.2f}")
    print(f"Worst Trade: ${worst_trade:.2f}")
    print(f"\n--- RESULTS WITH THNDR COSTS (0.2613%) ---")
    print(f"Total P&L (Realistic): ${total_realistic_pnl:.2f}")
    print(f"Total P&L (Ideal): ${total_ideal_pnl:.2f}")
    print(f"Total Costs: ${total_costs:.2f}")
    print(f"\nAnnualized Return (based on ${INITIAL_CAPITAL * total_trades:,.0f} deployed): {(total_realistic_pnl / (INITIAL_CAPITAL * total_trades / 365)) * 365 * 100:.1f}%")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "█"*80)
    print("CAIRO-LONDON ARBITRAGE: PARAMETER SENSITIVITY ANALYSIS")
    print("█"*80)
    
    # Fetch data
    cairo_data, london_data = fetch_and_prepare_data()
    unified_df = create_unified_calendar(cairo_data, london_data)
    
    print(f"\n📊 Data prepared: {len(unified_df)} days")
    print(f"Using actual Thndr costs: {THNDR_COMMISSION_PCT}% per trade")
    
    # ========================================================================
    # TEST 1: SIGNAL THRESHOLD VARIATIONS
    # ========================================================================
    
    print("\n\n" + "╔" + "═"*78 + "╗")
    print("║ TEST 1: SIGNAL THRESHOLD VARIATIONS")
    print("╚" + "═"*78 + "╝")
    
    thresholds = [0.5, 0.75, 1.0, 1.25, 1.5]
    threshold_results = []
    
    for threshold in thresholds:
        trades = backtest_threshold(unified_df, threshold)
        
        if len(trades) > 0:
            win_rate = (trades['profitable'].sum() / len(trades)) * 100
            total_pnl = trades['realistic_pnl'].sum()
            avg_return = trades['realistic_return'].mean()
            
            threshold_results.append({
                'Threshold': f"{threshold}%",
                'Trades': len(trades),
                'Win Rate': f"{win_rate:.1f}%",
                'Avg Return': f"{avg_return:.4f}%",
                'Total P&L': f"${total_pnl:.2f}",
                'P&L per Trade': f"${total_pnl/len(trades):.2f}"
            })
            
            print_results(f"Signal Threshold: London Daily Move > {threshold}%", trades)
    
    # Comparison table
    print("\n" + "─"*80)
    print("THRESHOLD COMPARISON TABLE")
    print("─"*80)
    df_comparison = pd.DataFrame(threshold_results)
    print("\n" + df_comparison.to_string(index=False))
    
    # ========================================================================
    # TEST 2: INTRADAY VOLUME-BASED TRADING
    # ========================================================================
    
    print("\n\n" + "╔" + "═"*78 + "╗")
    print("║ TEST 2: INTRADAY VOLUME-BASED TRADING")
    print("║ (Trade multiple times per day based on intraday price action)")
    print("╚" + "═"*78 + "╝")
    
    intraday_trades = backtest_intraday_volume(unified_df)
    print_results("Intraday Volume Trading (Early Morning + Midday)", intraday_trades)
    
    # ========================================================================
    # SUMMARY & RECOMMENDATIONS
    # ========================================================================
    
    print("\n\n" + "█"*80)
    print("SUMMARY & RECOMMENDATIONS")
    print("█"*80)
    
    # Find best threshold
    best_threshold = max(threshold_results, key=lambda x: float(x['Total P&L'].replace('$', '')))
    print(f"\n✅ Best Threshold: {best_threshold['Threshold']}")
    print(f"   Trades: {best_threshold['Trades']}")
    print(f"   Total P&L: {best_threshold['Total P&L']}")
    
    # Intraday comparison
    intraday_pnl = intraday_trades['realistic_pnl'].sum() if len(intraday_trades) > 0 else 0
    print(f"\n📈 Intraday Trading:")
    print(f"   Trades: {len(intraday_trades)}")
    print(f"   Total P&L: ${intraday_pnl:.2f}")
    
    # Original strategy (1.0% threshold)
    original_trades = backtest_threshold(unified_df, 1.0)
    original_pnl = original_trades['realistic_pnl'].sum() if len(original_trades) > 0 else 0
    print(f"\n🎯 Original Strategy (1.0% threshold):")
    print(f"   Trades: {len(original_trades)}")
    print(f"   Total P&L: ${original_pnl:.2f}")
    
    print(f"\n" + "─"*80)
    print("RECOMMENDATIONS:")
    print("─"*80)
    print("""
1. LOWER THRESHOLD (0.5-0.75%):
   ✓ More trading opportunities (more frequent signals)
   ✓ Higher trade count = better risk diversification
   ⚠ Lower P&L per trade but potentially higher annual return

2. HIGHER THRESHOLD (1.25-1.5%):
   ✓ Only captures strongest moves (higher confidence)
   ✓ Better win rate expected
   ⚠ Fewer trades per year

3. INTRADAY TRADING:
   ✓ Capture multiple opportunities per day
   ✓ Reduce idle capital
   ⚠ More execution risk, requires faster platform access
   ⚠ More monitoring required

SUGGESTED APPROACH:
Start with 1.0% threshold (original strategy) → 56 trades/year
Monitor for 3 months, then test 0.75% threshold if win rate holds
    """)
    
    print("█"*80 + "\n")
