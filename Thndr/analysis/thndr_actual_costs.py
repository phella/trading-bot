#!/usr/bin/env python3
"""
THNDR ACTUAL COSTS CALCULATOR (EGP-based)
=========================================

Thndr Fee Structure (Cairo/EGX Trading):
- 2 EGP fixed per transaction (buy AND sell)
- 0.1% variable commission on trade amount
- 0.03% third-party fee on trade amount

All calculations in EGP (Egyptian Pound)
"""

import pandas as pd

# Thndr fee structure
THNDR_FIXED_FEE_PER_TX = 2.0           # EGP per transaction
THNDR_VARIABLE_COMMISSION = 0.1        # % of trade amount
THNDR_THIRD_PARTY = 0.03               # % of trade amount

# Exchange rate reference (for translating back to USD equivalent)
EGP_USD_RATE = 31.0  # 1 USD = 31 EGP (approximate April 2026)

def calculate_thndr_costs(trade_amount_egp):
    """
    Calculate total Thndr fees for a buy+sell round trip
    
    Args:
        trade_amount_egp: Trade size in EGP
        
    Returns:
        dict with cost breakdown
    """
    
    # Per transaction costs
    fixed_per_tx = THNDR_FIXED_FEE_PER_TX  # 2 EGP
    variable_per_tx = trade_amount_egp * (THNDR_VARIABLE_COMMISSION / 100)
    third_party_per_tx = trade_amount_egp * (THNDR_THIRD_PARTY / 100)
    
    total_per_tx = fixed_per_tx + variable_per_tx + third_party_per_tx
    
    # For round trip (buy + sell)
    total_round_trip = total_per_tx * 2
    
    # As percentage of trade amount
    cost_pct = (total_round_trip / trade_amount_egp) * 100
    
    return {
        "trade_amount_egp": trade_amount_egp,
        "cost_per_buy_egp": total_per_tx,
        "cost_per_sell_egp": total_per_tx,
        "total_round_trip_egp": total_round_trip,
        "cost_percentage": cost_pct,
        "cost_per_tx_breakdown": {
            "fixed": fixed_per_tx * 2,
            "variable": variable_per_tx * 2,
            "third_party": third_party_per_tx * 2,
        }
    }

# ============================================================================
# ANALYSIS
# ============================================================================

print("\n" + "█"*80)
print("THNDR ACTUAL COSTS (EGP-based)")
print("█"*80)

print(f"\nFee Structure:")
print(f"  Fixed per transaction: {THNDR_FIXED_FEE_PER_TX} EGP")
print(f"  Variable commission: {THNDR_VARIABLE_COMMISSION}%")
print(f"  Third-party fee: {THNDR_THIRD_PARTY}%")
print(f"  Rate: 1 USD = {EGP_USD_RATE} EGP")

print("\n" + "─"*80)
print("COST EXAMPLES FOR DIFFERENT TRADE SIZES")
print("─"*80)

trade_sizes_usd = [100, 500, 1000, 5000, 10000, 50000, 100000]

results = []
for usd_amount in trade_sizes_usd:
    egp_amount = usd_amount * EGP_USD_RATE
    costs = calculate_thndr_costs(egp_amount)
    
    results.append({
        "Trade Size (USD)": f"${usd_amount:,}",
        "Trade Size (EGP)": f"EGP {egp_amount:,.0f}",
        "Round Trip Cost (EGP)": f"EGP {costs['total_round_trip_egp']:.2f}",
        "Cost as %": f"{costs['cost_percentage']:.4f}%",
        "Cost (USD equiv)": f"${costs['total_round_trip_egp'] / EGP_USD_RATE:.2f}",
    })

df = pd.DataFrame(results)
print("\n" + df.to_string(index=False))

# ============================================================================
# DETAILED BREAKDOWN FOR $10,000 TRADE (BASE CASE)
# ============================================================================

print("\n" + "─"*80)
print("DETAILED BREAKDOWN: $10,000 TRADE")
print("─"*80)

base_trade_usd = 10000
base_trade_egp = base_trade_usd * EGP_USD_RATE
costs = calculate_thndr_costs(base_trade_egp)

print(f"\nTrade Amount: ${base_trade_usd:,} (EGP {base_trade_egp:,.0f})")
print(f"\nBUY Transaction:")
print(f"  Fixed fee:        {THNDR_FIXED_FEE_PER_TX:.2f} EGP")
print(f"  Variable (0.1%):  {base_trade_egp * (THNDR_VARIABLE_COMMISSION / 100):.2f} EGP")
print(f"  Third-party:      {base_trade_egp * (THNDR_THIRD_PARTY / 100):.2f} EGP")
print(f"  ───────────────────────────")
print(f"  Per buy:          {costs['cost_per_buy_egp']:.2f} EGP (${costs['cost_per_buy_egp'] / EGP_USD_RATE:.4f})")

print(f"\nSELL Transaction:")
print(f"  Fixed fee:        {THNDR_FIXED_FEE_PER_TX:.2f} EGP")
print(f"  Variable (0.1%):  {base_trade_egp * (THNDR_VARIABLE_COMMISSION / 100):.2f} EGP")
print(f"  Third-party:      {base_trade_egp * (THNDR_THIRD_PARTY / 100):.2f} EGP")
print(f"  ───────────────────────────")
print(f"  Per sell:         {costs['cost_per_sell_egp']:.2f} EGP (${costs['cost_per_sell_egp'] / EGP_USD_RATE:.4f})")

print(f"\nROUND TRIP COSTS:")
print(f"  Total (EGP):      {costs['total_round_trip_egp']:.2f} EGP")
print(f"  Total (USD):      ${costs['total_round_trip_egp'] / EGP_USD_RATE:.4f}")
print(f"  Cost as %:        {costs['cost_percentage']:.4f}%")

print(f"\nCost Breakdown:")
print(f"  Fixed (2x):       {costs['cost_per_tx_breakdown']['fixed']:.2f} EGP ({(costs['cost_per_tx_breakdown']['fixed'] / costs['total_round_trip_egp'] * 100):.1f}%)")
print(f"  Variable (2x):    {costs['cost_per_tx_breakdown']['variable']:.2f} EGP ({(costs['cost_per_tx_breakdown']['variable'] / costs['total_round_trip_egp'] * 100):.1f}%)")
print(f"  Third-party (2x): {costs['cost_per_tx_breakdown']['third_party']:.2f} EGP ({(costs['cost_per_tx_breakdown']['third_party'] / costs['total_round_trip_egp'] * 100):.1f}%)")

# ============================================================================
# COMPARISON: THNDR vs ORIGINAL ASSUMPTIONS
# ============================================================================

print("\n" + "─"*80)
print("COMPARISON: ACTUAL THNDR vs ORIGINAL ASSUMPTIONS")
print("─"*80)

actual_thndr_pct = costs['cost_percentage']
original_assumption_pct = 0.53  # What we assumed before

print(f"\nOriginal assumption: 0.53% per trade")
print(f"Actual Thndr costs:  {actual_thndr_pct:.4f}% per trade")
print(f"Difference:          {original_assumption_pct - actual_thndr_pct:.4f}% (YOU'RE BETTER OFF!)")

# ============================================================================
# BACKTEST IMPACT
# ============================================================================

print("\n" + "─"*80)
print("IMPACT ON 56-TRADE BACKTEST")
print("─"*80)

ideal_pnl = 3850.48
trades = 56

cost_per_trade_original = 10000 * (original_assumption_pct / 100)
cost_per_trade_actual = 10000 * (actual_thndr_pct / 100)

total_costs_original = cost_per_trade_original * trades
total_costs_actual = cost_per_trade_actual * trades

pnl_original = ideal_pnl - total_costs_original
pnl_actual = ideal_pnl - total_costs_actual

print(f"\nBased on ideal P&L: ${ideal_pnl:.2f}")
print(f"Across 56 trades of $10,000 each\n")

print(f"Using ORIGINAL assumption (0.53%):")
print(f"  Cost per trade:  ${cost_per_trade_original:.2f}")
print(f"  Total costs:     ${total_costs_original:.2f}")
print(f"  Realistic P&L:   ${pnl_original:.2f}")
print(f"  Return per trade: {(pnl_original / 560000) * 100:.3f}%")

print(f"\nUsing ACTUAL Thndr costs ({actual_thndr_pct:.4f}%):")
print(f"  Cost per trade:  ${cost_per_trade_actual:.2f}")
print(f"  Total costs:     ${total_costs_actual:.2f}")
print(f"  Realistic P&L:   ${pnl_actual:.2f}")
print(f"  Return per trade: {(pnl_actual / 560000) * 100:.3f}%")

print(f"\n💰 YOU SAVE: ${total_costs_original - total_costs_actual:.2f}")
print(f"📈 EXTRA PROFIT: ${pnl_actual - pnl_original:.2f}")

if pnl_actual > 0:
    print(f"\n✅ STRATEGY IS PROFITABLE WITH ACTUAL THNDR COSTS!")
else:
    print(f"\n⚠️  Strategy still unprofitable at actual Thndr costs")

print("\n" + "█"*80 + "\n")
