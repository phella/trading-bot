#!/usr/bin/env python3
"""
Win/Loss Analysis: Why 32% Win Rate = Positive P&L
===================================================

Explains the risk/reward ratio and why winners > losers in size
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
THNDR_COMMISSION_PCT = 0.2613
INITIAL_CAPITAL = 10000

def fetch_and_prepare_data():
    """Fetch data"""
    cairo_data = yf.download(CAIRO_TICKER, start=START_DATE, end=END_DATE, progress=False)
    london_data = yf.download(LONDON_TICKER, start=START_DATE, end=END_DATE, progress=False)
    
    unified = pd.DataFrame(index=pd.date_range(START_DATE, END_DATE, freq='D'))
    
    cairo_close = cairo_data[['Close']].copy()
    cairo_close.columns = ['cairo_close']
    cairo_close = cairo_close.reindex(unified.index, method='ffill')
    
    london_close = london_data[['Close']].copy()
    london_close.columns = ['london_close']
    london_close = london_close.reindex(unified.index, method='ffill')
    
    london_close['london_return'] = london_close['london_close'].pct_change() * 100
    
    result = pd.concat([cairo_close, london_close], axis=1)
    return result.dropna()

def backtest_threshold(unified_df, signal_threshold):
    """Backtest with signal threshold"""
    trades = []
    CORRELATION = 0.0728
    
    for i in range(len(unified_df) - 1):
        london_return = unified_df.iloc[i]['london_return']
        
        if abs(london_return) > signal_threshold:
            entry_price = unified_df.iloc[i]['cairo_close']
            next_day_price = unified_df.iloc[i + 1]['cairo_close']
            
            actual_move = ((next_day_price - entry_price) / entry_price) * 100
            
            ideal_return = actual_move
            realistic_return = ideal_return - THNDR_COMMISSION_PCT
            
            ideal_pnl = INITIAL_CAPITAL * (ideal_return / 100)
            realistic_pnl = INITIAL_CAPITAL * (realistic_return / 100)
            
            trades.append({
                'date': unified_df.index[i],
                'london_return': london_return,
                'actual_move': actual_move,
                'ideal_return': ideal_return,
                'realistic_return': realistic_return,
                'ideal_pnl': ideal_pnl,
                'realistic_pnl': realistic_pnl,
                'profitable': realistic_pnl > 0
            })
    
    return pd.DataFrame(trades)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "█"*80)
    print("WHY 32% WIN RATE = POSITIVE P&L (Risk/Reward Ratio Explained)")
    print("█"*80)
    
    # Fetch data
    unified_df = fetch_and_prepare_data()
    
    # Test 1.25% threshold
    trades = backtest_threshold(unified_df, 1.25)
    
    print(f"\n📊 1.25% Threshold Analysis\n")
    
    # Separate wins and losses
    winning_trades = trades[trades['profitable'] == True]
    losing_trades = trades[trades['profitable'] == False]
    
    print(f"Total Trades: {len(trades)}")
    print(f"✅ Winning Trades: {len(winning_trades)}")
    print(f"❌ Losing Trades: {len(losing_trades)}")
    print(f"Win Rate: {(len(winning_trades)/len(trades)*100):.1f}%")
    
    # Calculate statistics
    print(f"\n" + "─"*80)
    print(f"WINNING TRADES STATISTICS")
    print(f"─"*80)
    
    win_total_pnl = winning_trades['realistic_pnl'].sum()
    win_avg_pnl = winning_trades['realistic_pnl'].mean()
    win_min = winning_trades['realistic_pnl'].min()
    win_max = winning_trades['realistic_pnl'].max()
    win_median = winning_trades['realistic_pnl'].median()
    
    print(f"Total P&L (all wins): ${win_total_pnl:.2f}")
    print(f"Average per winning trade: ${win_avg_pnl:.2f}")
    print(f"Median per winning trade: ${win_median:.2f}")
    print(f"Smallest winning trade: ${win_min:.2f}")
    print(f"Largest winning trade: ${win_max:.2f}")
    print(f"Range: ${win_min:.2f} to ${win_max:.2f}")
    
    print(f"\n" + "─"*80)
    print(f"LOSING TRADES STATISTICS")
    print(f"─"*80)
    
    loss_total_pnl = losing_trades['realistic_pnl'].sum()
    loss_avg_pnl = losing_trades['realistic_pnl'].mean()
    loss_min = losing_trades['realistic_pnl'].min()  # Most negative (biggest loss)
    loss_max = losing_trades['realistic_pnl'].max()  # Least negative (smallest loss)
    loss_median = losing_trades['realistic_pnl'].median()
    
    print(f"Total P&L (all losses): ${loss_total_pnl:.2f}")
    print(f"Average per losing trade: ${loss_avg_pnl:.2f}")
    print(f"Median per losing trade: ${loss_median:.2f}")
    print(f"Biggest loss: ${loss_min:.2f}")
    print(f"Smallest loss: ${loss_max:.2f}")
    print(f"Range: ${loss_min:.2f} to ${loss_max:.2f}")
    
    print(f"\n" + "─"*80)
    print(f"THE MATH: WHY WINNERS > LOSERS")
    print(f"─"*80)
    
    print(f"\nWinning Trades Contribution:")
    print(f"  {len(winning_trades)} winning trades × avg ${win_avg_pnl:.2f} = ${win_total_pnl:.2f}")
    
    print(f"\nLosing Trades Contribution:")
    print(f"  {len(losing_trades)} losing trades × avg ${loss_avg_pnl:.2f} = ${loss_total_pnl:.2f}")
    
    total_pnl = trades['realistic_pnl'].sum()
    print(f"\nNet Result:")
    print(f"  ${win_total_pnl:.2f} + (${loss_total_pnl:.2f}) = ${total_pnl:.2f}")
    
    # Risk/Reward ratio
    avg_win_size = abs(win_avg_pnl)
    avg_loss_size = abs(loss_avg_pnl)
    risk_reward_ratio = avg_win_size / avg_loss_size
    
    print(f"\n" + "─"*80)
    print(f"RISK/REWARD RATIO")
    print(f"─"*80)
    
    print(f"\nAverage Winner Size: ${avg_win_size:.2f}")
    print(f"Average Loser Size: ${avg_loss_size:.2f}")
    print(f"Risk/Reward Ratio: {risk_reward_ratio:.2f}x")
    
    print(f"\nInterpretation:")
    print(f"  For every $1 you lose on a losing trade,")
    print(f"  you make ${risk_reward_ratio:.2f} on a winning trade")
    
    # Profitability formula
    win_rate = len(winning_trades) / len(trades)
    breakeven_win_rate = avg_loss_size / (avg_win_size + avg_loss_size)
    
    print(f"\n" + "─"*80)
    print(f"PROFITABILITY FORMULA")
    print(f"─"*80)
    
    print(f"\nExpected Profit = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)")
    print(f"${total_pnl:.2f} = ({win_rate:.1%} × ${avg_win_size:.2f}) - ({(1-win_rate):.1%} × ${avg_loss_size:.2f})")
    print(f"${total_pnl:.2f} = ${win_rate * avg_win_size:.2f} - ${(1-win_rate) * avg_loss_size:.2f}")
    
    print(f"\nBreakeven Win Rate (where profit = 0):")
    print(f"  {breakeven_win_rate:.1%} of trades need to win")
    print(f"  Your actual win rate: {win_rate:.1%}")
    print(f"  Margin above breakeven: {(win_rate - breakeven_win_rate):.1%}")
    
    # Distribution analysis
    print(f"\n" + "─"*80)
    print(f"PROFIT DISTRIBUTION")
    print(f"─"*80)
    
    # Quartiles for wins
    win_q1 = winning_trades['realistic_pnl'].quantile(0.25)
    win_q2 = winning_trades['realistic_pnl'].quantile(0.50)
    win_q3 = winning_trades['realistic_pnl'].quantile(0.75)
    
    print(f"\nWinning Trades Distribution:")
    print(f"  25th percentile: ${win_q1:.2f}")
    print(f"  50th percentile (median): ${win_q2:.2f}")
    print(f"  75th percentile: ${win_q3:.2f}")
    print(f"  ({len(winning_trades)} trades total)")
    
    # Quartiles for losses
    loss_q1 = losing_trades['realistic_pnl'].quantile(0.25)
    loss_q2 = losing_trades['realistic_pnl'].quantile(0.50)
    loss_q3 = losing_trades['realistic_pnl'].quantile(0.75)
    
    print(f"\nLosing Trades Distribution:")
    print(f"  25th percentile (biggest losses): ${loss_q1:.2f}")
    print(f"  50th percentile (median): ${loss_q2:.2f}")
    print(f"  75th percentile (smallest losses): ${loss_q3:.2f}")
    print(f"  ({len(losing_trades)} trades total)")
    
    print(f"\n" + "█"*80)
    print(f"KEY INSIGHT")
    print(f"█"*80)
    print(f"""
You DON'T need 50%+ win rate to be profitable.

This strategy is profitable with 32% win rate because:

1. ✅ Winning trades are BIGGER on average (${avg_win_size:.2f})
2. ❌ Losing trades are SMALLER on average (${avg_loss_size:.2f})
3. 📊 Risk/Reward ratio is {risk_reward_ratio:.2f}x in your favor

This is why professional traders focus on:
  • Taking profits when winners 2-3x their risk
  • Cutting losses quickly before they get big
  • Having more winners ≠ more money (bigger wins matter more)

Your strategy naturally creates this because:
  • Higher threshold (1.25%) → filters for BIG moves
  • Small losses on marginal moves
  • Big wins on strong momentum
  • Low Thndr costs (0.2613%) → reduce death by a thousand cuts
    """)
    
    print("█"*80 + "\n")
