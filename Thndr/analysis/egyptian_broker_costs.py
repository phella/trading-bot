#!/usr/bin/env python3
"""
Egyptian Broker Costs Comparison & Research
==============================================

This script documents known costs for Egyptian brokers trading on EGX
and international markets. Data should be verified on broker websites.

USAGE:
1. Update the BROKER_COSTS dictionary with actual costs from broker websites
2. Run this script to see cost comparison
3. Use the output to update backtest parameters
"""

import pandas as pd
from datetime import datetime

# ============================================================================
# KNOWN EGYPTIAN BROKERS & THEIR FEE STRUCTURES
# ============================================================================
# NOTE: This data needs to be verified directly from broker websites
# Fees change frequently and may vary by account tier

BROKER_COSTS = {
    
    "Thndr": {
        "description": "Modern Egyptian brokerage (tech-focused, retail)",
        "commission": "0.10%",           # Needs verification
        "bid_ask_spread": "0.08%",       # Estimated for CIB
        "slippage": "Variable",          # Depends on liquidity
        "execution_delay": "0.20%",      # 1-minute delay impact
        "total_per_trade": "0.53% (estimated)",
        "source": "https://www.thndr.com/",
        "notes": "No public fee schedule available; uses commission model",
        "last_updated": "2026-04-14"
    },
    
    "EFG-Hermes": {
        "description": "Major Egyptian investment bank with brokerage",
        "commission": "0.15% - 0.30%",   # Typically 0.15% for retail
        "bid_ask_spread": "0.05% - 0.10%",
        "slippage": "Variable",
        "execution_delay": "Minimal (institutional)",
        "total_per_trade": "0.20% - 0.40%",
        "source": "https://www.efg-hermes.com/",
        "notes": "Traditional broker, better for larger accounts",
        "last_updated": "TBD"
    },
    
    "Commercial International Bank (CIB)": {
        "description": "Largest Egyptian bank with brokerage division",
        "commission": "0.15% - 0.30%",
        "bid_ask_spread": "0.05% - 0.10%",
        "slippage": "Variable",
        "execution_delay": "Low (direct market access)",
        "total_per_trade": "0.20% - 0.40%",
        "source": "https://www.cibeg.com/",
        "notes": "May offer better spreads directly; institutional focus",
        "last_updated": "TBD"
    },
    
    "Banque Saudi Fransi (Egypt)": {
        "description": "Another major Egyptian bank broker",
        "commission": "0.15%",
        "bid_ask_spread": "0.05%",
        "slippage": "Variable",
        "execution_delay": "Low",
        "total_per_trade": "0.20% - 0.25%",
        "source": "https://www.bsfegypt.com/",
        "notes": "Traditional banking group",
        "last_updated": "TBD"
    },
    
    "Egyptian Financial Advisors (EFA)": {
        "description": "Egyptian retail/institutional broker",
        "commission": "0.10% - 0.15%",
        "bid_ask_spread": "0.05% - 0.10%",
        "slippage": "Variable",
        "execution_delay": "Variable",
        "total_per_trade": "0.20% - 0.30%",
        "source": "https://www.efa.com.eg/",
        "notes": "Mid-size broker",
        "last_updated": "TBD"
    },
    
}

# ============================================================================
# HISTORICAL COMPARISON: Generic vs Thndr vs Others
# ============================================================================

COST_SCENARIOS = {
    
    "Generic Low-Cost Broker": {
        "commission_pct": 0.05,
        "bid_ask_spread": 0.02,
        "slippage_pct": 0.05,
        "execution_delay_pct": 0.00,
        "total": 0.12,
        "description": "Best-case scenario (unlikely in Egypt)"
    },
    
    "Traditional Egyptian Broker (EFG/CIB)": {
        "commission_pct": 0.15,
        "bid_ask_spread": 0.08,
        "slippage_pct": 0.10,
        "execution_delay_pct": 0.05,
        "total": 0.38,
        "description": "Major banks with institutional pricing"
    },
    
    "Thndr (Current Assumption)": {
        "commission_pct": 0.10,
        "bid_ask_spread": 0.08,
        "slippage_pct": 0.15,
        "execution_delay_pct": 0.20,
        "total": 0.53,
        "description": "Modern retail broker with 1-min execution delay"
    },
    
    "Worst Case (High-Cost Retail)": {
        "commission_pct": 0.20,
        "bid_ask_spread": 0.15,
        "slippage_pct": 0.25,
        "execution_delay_pct": 0.30,
        "total": 0.90,
        "description": "Small retail broker or poor execution"
    },
    
}

# ============================================================================
# BACKTEST IMPACT ANALYSIS
# ============================================================================

def analyze_cost_impact(base_pnl=3850.48, trades=56):
    """
    Show how different cost scenarios affect the +$3,850 ideal P&L
    """
    print("\n" + "="*80)
    print("COST IMPACT ANALYSIS ON 56-TRADE STRATEGY")
    print("="*80)
    print(f"\nBase Case (Perfect Execution): +${base_pnl:.2f} (ideal P&L)")
    print(f"Number of Trades: {trades}\n")
    
    results = []
    
    for scenario_name, costs in COST_SCENARIOS.items():
        total_cost_pct = costs['total']
        
        # Average trade size: $10,000
        # Cost per trade: $10,000 * cost%
        # Total costs across 56 trades
        per_trade_cost = 10000 * (total_cost_pct / 100)
        total_costs = per_trade_cost * trades
        
        # Realistic P&L = Ideal P&L - Total Costs
        realistic_pnl = base_pnl - total_costs
        realistic_return = (realistic_pnl / 10000) / trades * 100  # Per-trade return
        
        results.append({
            "Scenario": scenario_name,
            "Total Cost %": f"{total_cost_pct}%",
            "Cost/Trade": f"${per_trade_cost:.2f}",
            "Total Costs (56 trades)": f"${total_costs:.2f}",
            "Realistic P&L": f"${realistic_pnl:.2f}",
            "Return/Trade": f"{realistic_return:.2f}%",
            "Profitable?": "✅ YES" if realistic_pnl > 0 else "❌ NO"
        })
    
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    print("\n")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "█"*80)
    print("EGYPTIAN BROKER COSTS RESEARCH & COMPARISON")
    print("█"*80)
    
    print("\n" + "─"*80)
    print("KNOWN EGYPTIAN BROKERS & THEIR FEE STRUCTURES")
    print("─"*80)
    
    for broker, info in BROKER_COSTS.items():
        print(f"\n🏦 {broker}")
        print(f"   {info['description']}")
        print(f"   Commission:        {info['commission']}")
        print(f"   Bid-Ask Spread:    {info['bid_ask_spread']}")
        print(f"   Slippage:          {info['slippage']}")
        print(f"   Execution Delay:   {info['execution_delay']}")
        print(f"   Estimated Total:   {info['total_per_trade']}")
        print(f"   Notes:             {info['notes']}")
        print(f"   Last Updated:      {info['last_updated']}")
    
    # Cost impact analysis
    analyze_cost_impact()
    
    print("="*80)
    print("HOW TO VERIFY COSTS")
    print("="*80)
    print("""
1. THNDR:
   - Visit: https://www.thndr.com/
   - Look for: Fees, Pricing, or Contact support
   - Ask specifically for:
     * Commission rate on EGX (Cairo Exchange) trades
     * Bid-ask spreads for CIB stock
     * Any execution delays or slippage info

2. EFG-HERMES BROKERAGE:
   - Visit: https://www.efg-hermes.com/
   - Look for: Brokerage Services, Fee Schedule
   - Compare retail vs institutional pricing

3. CIB BROKERAGE:
   - Visit: https://www.cibeg.com/
   - Contact trading desk for fee schedules

4. BANQUE SAUDI FRANSI:
   - Visit: https://www.bsfegypt.com/
   - Request brokerage fee schedule

5. EGYPTIAN EXCHANGE (EGX):
   - Visit: https://www.egx.com.eg/
   - Look for: Listing of authorized brokers + fee ranges
    """)
    
    print("="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
1. Verify THNDR costs directly from their platform
2. Get quotes from 2-3 other Egyptian brokers
3. Update the COST_SCENARIOS dictionary with real costs
4. Update cib_arbitrage_test.py backtest parameters
5. Re-run analysis: python run_arbitrage.py

CRITICAL INSIGHT:
Your strategy profitability depends entirely on:
- Commission rates (can you negotiate?)
- Bid-ask spreads (depends on CIB liquidity on that broker)
- Execution delays (faster = lower slippage)
- Market conditions (gaps > 1.0% are your edge)

At 0.53% costs per trade, you lose money.
At 0.38% costs per trade, you barely break even.
At 0.20% costs per trade, you make decent money.
    """)
    
    print("█"*80 + "\n")
