"""
Examples and test cases for CIB Arbitrage Analysis Tool
"""

# Example 1: Basic Usage
# =====================

from cib_arbitrage_test import CIBArbitrageAnalyzer
from datetime import datetime, timedelta

# Setup
end_date = datetime.now().date()
start_date = end_date - timedelta(days=365)

# Create analyzer
analyzer = CIBArbitrageAnalyzer(
    cairo_ticker='COMI.CA',
    london_ticker='CBKD.L',
    start_date=str(start_date),
    end_date=str(end_date)
)

# Run complete analysis
success = analyzer.run()

if success:
    print(f"✓ Analysis completed!")
    print(f"  Sunday Correlation: {analyzer.correlation}")


# Example 2: Testing Multiple Ticker Pairs
# =========================================

pairs_to_test = [
    ('COMI.CA', 'CBKD.L', 'CIB Egypt vs London'),
    ('AAPL', 'ASML', 'Tech Pair Fallback'),
]

for cairo_tick, london_tick, description in pairs_to_test:
    print(f"\nTesting: {description}")
    
    analyzer = CIBArbitrageAnalyzer(
        cairo_ticker=cairo_tick,
        london_ticker=london_tick,
        start_date=str(start_date),
        end_date=str(end_date)
    )
    
    try:
        if analyzer.run():
            print(f"✓ {description}: SUCCESS")
            break
    except Exception as e:
        print(f"✗ {description}: {str(e)[:80]}")


# Example 3: Custom Date Range
# ===========================

# Last 2 years
start_date = datetime.now().date() - timedelta(days=730)
end_date = datetime.now().date()

analyzer = CIBArbitrageAnalyzer(
    cairo_ticker='COMI.CA',
    london_ticker='CBKD.L',
    start_date=str(start_date),
    end_date=str(end_date)
)

analyzer.run()


# Example 4: Accessing Backtest Results
# =====================================

analyzer = CIBArbitrageAnalyzer(
    cairo_ticker='COMI.CA',
    london_ticker='CBKD.L',
    start_date='2025-04-14',
    end_date='2026-04-14'
)

analyzer.fetch_data()
analyzer.create_unified_calendar()
analyzer.smart_forward_fill()
analyzer.calculate_weekend_lead()
analyzer.calculate_sunday_open_gap()
analyzer.calculate_correlation()
analyzer.generate_trading_signals(london_move_threshold=1.0)
analyzer.backtest_arbitrage(initial_capital=10000)

# Access results
if analyzer.backtest_results['trades']:
    import pandas as pd
    trades_df = pd.DataFrame(analyzer.backtest_results['trades'])
    
    print("Trade Analysis:")
    print(f"Total Trades: {len(trades_df)}")
    print(f"Win Rate: {(analyzer.backtest_results['winning_trades']/len(trades_df))*100:.1f}%")
    print(f"Avg PnL: ${trades_df['PnL$'].mean():.2f}")
    print(f"Total PnL: ${analyzer.backtest_results['total_pnl']:.2f}")
    
    # Show best 3 trades
    print("\nTop 3 Trades:")
    for idx, row in trades_df.nlargest(3, 'PnL$').iterrows():
        print(f"  {row['Date']}: +{row['PnL%']:.2f}% (${row['PnL$']:.2f})")


# Example 5: Different Signal Thresholds
# =====================================

for threshold in [0.5, 1.0, 1.5, 2.0]:
    print(f"\nTesting threshold: {threshold}%")
    
    analyzer = CIBArbitrageAnalyzer(
        cairo_ticker='COMI.CA',
        london_ticker='CBKD.L',
        start_date='2025-04-14',
        end_date='2026-04-14'
    )
    
    analyzer.fetch_data()
    analyzer.create_unified_calendar()
    analyzer.smart_forward_fill()
    analyzer.calculate_weekend_lead()
    analyzer.calculate_sunday_open_gap()
    analyzer.generate_trading_signals(london_move_threshold=threshold)
    analyzer.backtest_arbitrage()
    
    if analyzer.backtest_results['trades']:
        num_trades = len(analyzer.backtest_results['trades'])
        pnl = analyzer.backtest_results['total_pnl']
        print(f"  Trades: {num_trades}, Total PnL: ${pnl:.2f}")


# Example 6: Accessing Unified DataFrame
# ======================================

analyzer = CIBArbitrageAnalyzer(
    cairo_ticker='COMI.CA',
    london_ticker='CBKD.L',
    start_date='2025-04-14',
    end_date='2026-04-14'
)

analyzer.run()

# Access the unified calendar
df = analyzer.unified_df

# Show sample rows
print("Sample Trading Data:")
print(df[['Cairo_Close', 'London_Close', 'Weekend_Lead', 'Sunday_Open_Gap']].head(10))

# Statistics
print("\nCalendar Statistics:")
print(f"Total days: {len(df)}")
print(f"Cairo data points: {df['Cairo_Close'].notna().sum()}")
print(f"London data points: {df['London_Close'].notna().sum()}")

# Weekend Lead stats
weekend_lead_stats = df['Weekend_Lead'].describe()
print(f"\nWeekend Lead Statistics:")
print(weekend_lead_stats)

# Sunday Open Gap stats  
open_gap_stats = df['Sunday_Open_Gap'].describe()
print(f"\nSunday Open Gap Statistics:")
print(open_gap_stats)


# Example 7: Export Results to CSV
# ================================

import pandas as pd

analyzer = CIBArbitrageAnalyzer(
    cairo_ticker='COMI.CA',
    london_ticker='CBKD.L',
    start_date='2025-04-14',
    end_date='2026-04-14'
)

analyzer.run()

# Export unified calendar
analyzer.unified_df.to_csv('cib_unified_calendar.csv')
print("✓ Exported: cib_unified_calendar.csv")

# Export trades
if analyzer.backtest_results['trades']:
    trades_df = pd.DataFrame(analyzer.backtest_results['trades'])
    trades_df.to_csv('cib_trades.csv', index=False)
    print("✓ Exported: cib_trades.csv")


# Example 8: Error Handling
# =========================

import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    analyzer = CIBArbitrageAnalyzer(
        cairo_ticker='INVALID_TICKER',
        london_ticker='CBKD.L',
        start_date='2025-04-14',
        end_date='2026-04-14'
    )
    
    success = analyzer.run()
    
    if not success:
        logger.warning("Analysis failed - trying fallback tickers")
        
        # Fallback to working tickers
        analyzer = CIBArbitrageAnalyzer(
            cairo_ticker='AAPL',
            london_ticker='ASML',
            start_date='2025-04-14',
            end_date='2026-04-14'
        )
        
        analyzer.run()
        
except Exception as e:
    logger.error(f"Analysis error: {e}")


# Example 9: Performance Metrics Calculation
# ==========================================

def calculate_sharpe_ratio(trades_df, capital=10000):
    """Calculate Sharpe ratio of trades"""
    import numpy as np
    
    if len(trades_df) == 0:
        return 0
    
    returns = trades_df['PnL%'].values / 100
    daily_std = np.std(returns)
    
    if daily_std == 0:
        return 0
    
    risk_free_rate = 0.02 / 252  # ~2% annual
    sharpe = (returns.mean() - risk_free_rate) / daily_std * np.sqrt(252)
    
    return sharpe


analyzer = CIBArbitrageAnalyzer(
    cairo_ticker='COMI.CA',
    london_ticker='CBKD.L',
    start_date='2025-04-14',
    end_date='2026-04-14'
)

analyzer.run()

if analyzer.backtest_results['trades']:
    import pandas as pd
    
    trades_df = pd.DataFrame(analyzer.backtest_results['trades'])
    sharpe = calculate_sharpe_ratio(trades_df)
    
    print(f"Sharpe Ratio: {sharpe:.2f}")


# Example 10: Comparison Against Buy & Hold
# =========================================

def calculate_buyhold_return(prices):
    """Calculate simple buy & hold return"""
    if len(prices) < 2:
        return 0
    return ((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100


analyzer = CIBArbitrageAnalyzer(
    cairo_ticker='COMI.CA',
    london_ticker='CBKD.L',
    start_date='2025-04-14',
    end_date='2026-04-14'
)

analyzer.run()

# Calculator returns
cairo_buyhold = calculate_buyhold_return(
    analyzer.unified_df['Cairo_Close'].dropna()
)

london_buyhold = calculate_buyhold_return(
    analyzer.unified_df['London_Close'].dropna()
)

strategy_return = (analyzer.backtest_results['total_pnl'] / 10000) * 100

print("Return Comparison:")
print(f"Cairo Buy & Hold: {cairo_buyhold:.2f}%")
print(f"London Buy & Hold: {london_buyhold:.2f}%")
print(f"Arbitrage Strategy: {strategy_return:.2f}%")
print(f"Outperformance: {strategy_return - max(cairo_buyhold, london_buyhold):.2f}%")


if __name__ == "__main__":
    print("CIB Arbitrage Analysis - Examples")
    print("Run individual examples to test functionality")
