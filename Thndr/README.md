# THNDR Trading Strategies

**⭐ TESTED & RECOMMENDED: 1.25% threshold + 0.1% buy limit + 0.5% sell target (limit order)**  
**Result: 100% win rate | $2,482 total P&L | $23.87 avg/trade**

Organized THNDR trading system with multiple strategies and analysis tools.

## Folder Structure

```
Thndr/
├── strategies/          # Trading strategy backtests
│   └── limit_order_backtest.py     # Compare old (4-hour) vs new (limit order) strategies
│
├── analysis/            # Performance analysis & cost analysis
│   ├── sensitivity_analysis.py     # Test different thresholds & parameters
│   ├── win_rate_explained.py       # Understand win rate calculations
│   ├── egyptian_broker_costs.py    # Broker fees breakdown
│   └── thndr_actual_costs.py       # Real THNDR costs analysis
│
├── alerts/              # Alert system
│   └── thndr_alerts.py             # Real-time trading alerts
│
└── config/              # Configuration files
    └── thndr_config.toml           # THNDR API & strategy settings
```

## Quick Start

### Run Strategy Backtest (Comparison)
```bash
python strategies/limit_order_backtest.py
```

This compares:
- ⏱️ **Old Strategy**: 4-hour time-based exit
- 💰 **New Strategies**: Limit order exits (multiple variations)

Results table shows: Signals, Winners, Losers, Win %, Total P&L, Avg P&L

### Run Sensitivity Analysis
```bash
python analysis/sensitivity_analysis.py
```

Test different signal thresholds (0.5%-1.5%) and see how they affect performance.

### Check Broker Costs
```bash
python analysis/thndr_actual_costs.py
```

See exact commission structure and impact on trades.

## Adding New Strategies

To add a new strategy to the comparison table in `strategies/limit_order_backtest.py`:

1. Open the file
2. Find the `scenarios` list (around line 182)
3. Add your strategy:

```python
{
    'name': '💰 NEW STRATEGY: Your Strategy Name',
    'buy_offset': 0.1,           # % below market to buy
    'sell_target': 0.5,          # % profit target
    'sell_strategy': 'limit_order'  # or 'time_based'
}
```

4. Run and see it in the comparison table automatically!

## Key Files

| File | Purpose | Updated |
|------|---------|---------|
| `strategies/limit_order_backtest.py` | Main strategy comparison | ✓ New |
| `analysis/sensitivity_analysis.py` | Parameter testing | ✓ |
| `analysis/thndr_actual_costs.py` | Cost breakdown | ✓ |

## Current Results

From `limit_order_backtest.py`:

| Strategy | Signals | Win % | Total P&L |
|----------|---------|-------|-----------|
| 4-Hour Exit | 104 | 42.3% | $1,538 |
| Limit 0.1%/0.5% | 104 | 100.0% | $2,482 |
| Limit 0.05%/0.6% | 104 | 100.0% | $3,522 |

➡️ **New limit order strategies outperform 4-hour exit by 1.6x - 2.3x**
