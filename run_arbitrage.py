#!/usr/bin/env python3
"""
CIB Arbitrage Analysis - Main Entry Point
Analyzes Cairo vs London GDR price movements for arbitrage opportunities
"""

import sys
from cib_arbitrage_test import CIBArbitrageAnalyzer
from datetime import datetime, timedelta

def main():
    """Run CIB arbitrage analysis"""
    print("\n" + "="*70)
    print("CIB ARBITRAGE ANALYSIS TOOL")
    print("Cairo vs London GDR Dual-Market Arbitrage")
    print("="*70)
    
    # Date configuration
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    print(f"\nAnalysis Period: {start_date} to {end_date}")
    print("="*70)
    
    # Primary arbitrage pairs (if available on yfinance)
    # Note: Check yfinance for actual ticker availability
    print("\n📊 CONFIGURATION")
    print("Cairo Market: Sun-Thu trading (Egypt/EGX)")
    print("London Market: Mon-Fri trading (UK/LSE)")
    print("\nTicker Mapping:")
    print("- COMI.CA: CIB Egypt (Cairo Clinic)")
    print("- CBKD.L:  CIB London (London Listing)")
    print("- HRHO.CA: Heliopolis Housing Co (Cairo)")
    print("- EFGD.L:  EFG-Hermes (London GDR)")
    print("- ORAS.CA: Orascom Telecom (Cairo)")
    print("- ORAS.L:  Orascom Telecom (London GDR)")
    
    print("\nAttempting to fetch arbitrage data for all pairs...")
    
    # Test all Egyptian-London arbitrage pairs
    cib_pairs = [
        ('COMI.CA', 'CBKD.L', 'CIB Egyptian vs CIB London'),
        ('HRHO.CA', 'EFGD.L', 'Heliopolis Housing vs EFG-Hermes'),
        ('ORAS.CA', 'ORAS.L', 'Orascom Telecom Cairo vs London'),
        ('AAPL', 'ASML', 'Alternative: AAPL vs ASML'),
    ]
    
    success = False
    results = []
    
    for cairo_tick, london_tick, description in cib_pairs:
        print(f"\n{'='*70}")
        print(f"📈 Testing: {description}")
        print(f"   Cairo ticker: {cairo_tick} | London ticker: {london_tick}")
        print('='*70)
        
        analyzer = CIBArbitrageAnalyzer(
            cairo_ticker=cairo_tick,
            london_ticker=london_tick,
            start_date=str(start_date),
            end_date=str(end_date)
        )
        
        try:
            if analyzer.run():
                success = True
                results.append({
                    'pair': description,
                    'cairo': cairo_tick,
                    'london': london_tick,
                    'status': '✅ SUCCESS',
                    'correlation': analyzer.correlation,
                    'trades': len(analyzer.backtest_results['trades']),
                    'pnl': analyzer.backtest_results['total_pnl'] if analyzer.backtest_results else 0
                })
                print("\n✅ Analysis completed successfully!")
            else:
                results.append({
                    'pair': description,
                    'cairo': cairo_tick,
                    'london': london_tick,
                    'status': '❌ No data',
                    'correlation': None,
                    'trades': 0,
                    'pnl': 0
                })
                print(f"❌ Failed to fetch data for {cairo_tick}/{london_tick}")
        except Exception as e:
            results.append({
                'pair': description,
                'cairo': cairo_tick,
                'london': london_tick,
                'status': f"❌ Error: {str(e)[:50]}",
                'correlation': None,
                'trades': 0,
                'pnl': 0
            })
            print(f"❌ Error analyzing {cairo_tick}/{london_tick}: {str(e)[:80]}")
            continue
    
    # Print summary
    print(f"\n\n{'='*70}")
    print("ANALYSIS SUMMARY - ALL PAIRS TESTED")
    print('='*70)
    
    for result in results:
        print(f"\n{result['pair']}")
        print(f"  Tickers: {result['cairo']} ↔ {result['london']}")
        print(f"  Status: {result['status']}")
        if result['correlation'] is not None:
            print(f"  Correlation: {result['correlation']:.4f}")
        print(f"  Trades: {result['trades']}")
        print(f"  Total P&L: ${result['pnl']:.2f}")
    
    if not success:
        print(f"\n⚠️  No successful analyses completed")
        print("Note: Some tickers may not be available on yfinance")
        print("For real data, verify ticker symbols and connectivity")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
