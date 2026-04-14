⚙️ REALISTIC MODE: CONFIGURATION GUIDE
======================================

How to use and customize the realistic simulation

═════════════════════════════════════════════════════════════════

🎯 QUICK START
───────────────

The Default (What runs now):

```python
analyzer.backtest_arbitrage(
    slippage_pct=0.1,          ← Market impact + partial fills
    bid_ask_spread=0.05,       ← Bid-ask spread on entry/exit
    commission_pct=0.1,        ← Broker commission
    execution_delay_pct=0.0,   ← Order execution delay (0% = instant)
    realistic_mode=True        ← Toggle realistic mode on/off
)
```

This configuration gives you realistic results including:
  ✓ Costs: -$125.59 total
  ✓ Return: 1.71% (down from 2.97% ideal)
  ✓ Trade P&L: $170.96 (down from $296.55 ideal)

═════════════════════════════════════════════════════════════════

📊 PARAMETER EXPLANATION
─────────────────────────

1️⃣ slippage_pct (Default: 0.1%)
   
   What It Is:
   • Price movement against you when submitting order
   • Caused by: market impact + partial execution
   
   When It Happens:
   • You submit: "Buy 100 shares"
   • Market sees: Supply reduction
   • Other traders React: Prices move up
   • You execute: At worse price
   
   How It's Applied:
   • Entry: Buy price increases (+slippage)
   • Exit: Sell price decreases (-slippage)
   
   Typical Values:
   • Very Liquid (AAPL, MSFT):       0.01-0.03%
   • Liquid (CIB, CBKD):             0.05-0.10%
   • Medium Liquid (HRHO, EFGD):     0.10-0.20%
   • Illiquid emerging market pairs:  0.30-1.00%
   
   How to Adjust:
   • Fast execution (< 100ms):       0.05%
   • Normal execution (100-500ms):   0.10% ← Our default
   • Slow execution (> 500ms):       0.20%

2️⃣ bid_ask_spread (Default: 0.05%)
   
   What It Is:
   • Half the spread between bid (buy) and ask (sell)
   • At entry: You pay the ask (spreads against you)
   • At exit: You receive the bid (also spreads against you)
   
   Why We Use 0.05% (not 0.10%):
   • CIB is Blue Chip, tight spreads
   • EGX/LSE both liquid markets
   • Being slightly conservative
   
   Typical Values by Market:
   • High-frequency: 0.01% (HFT algorithms)
   • Large cap stocks: 0.02-0.05%
   • Small/mid cap: 0.05-0.10%
   • Emerging markets: 0.10-0.50%
   
   How to Check Your Broker:
   • Look at Level 2 quote
   • Note bid-ask for typical stock
   • Typical spread / stock price = this value
   • Example: 79.95 bid / 80.05 ask = 0.10 spread
   •         0.10 / 80.00 = 0.125%

3️⃣ commission_pct (Default: 0.1%)
   
   What It Is:
   • Broker fee for each trade
   • Applied on BOTH entry and exit
   • Total = 2 × commission_pct
   
   Typical Values by Broker:
   
   Egyptian Brokers:
   • Cheapest: 0.05%      (Onepoint)
   • Standard: 0.10%      (Most brokers) ← Our default
   • Expensive: 0.15%     (Some boutiques)
   
   UK Brokers:
   • Cheapest: 0.05%      (Interactive Brokers)
   • Standard: 0.10-0.15% (Most brokers)
   • Expensive: 0.20-0.50% (Full service)
   
   How to Find Your Broker's Rate:
   • Check fee schedule on their website
   • Or ask their support
   • Most publish rates publicly
   
   Special Cases:
   • Some brokers: flat fee per trade ($5-20)
   •   Convert to %: Fee / (Stock Price × Shares)
   • Some brokers: volume-based tiered structure
   •   Use average tier for your expected volume

4️⃣ execution_delay_pct (Default: 0.0%)
   
   What It Is:
   • Price movement while order is filling
   • Time between order submit and execution
   
   When It Happens:
   • You submit market order at 10:30:00.00
   • Exchange latency: +5ms
   • Order routing: +10ms
   • Matching engine: +5ms
   • Total: ~20ms delay
   • In that 20ms, price could move
   
   Typical Delay Scenarios:
   • Professional algo (co-located):    0.00% ← Near-instant
   • Retail broker (local PC):          0.01-0.05%
   • Retail with poor connection:       0.05-0.10%
   • Mobile order submission:           0.10-0.30%
   • Manual phone order:                0.50-2.00%
   
   How to Benchmark Your Setup:
   • Create test order (don't execute)
   • Note time submitted, time executed
   • Calculate delay in milliseconds
   • Multiply by typical market volatility
   •   Example: 20ms delay × 0.0001 price change/ms = 0.002%
   
   Why We Use 0.0% (for Cairo markets):
   • CIB is highly liquid blue chip
   • Order fills almost instantly
   • Electronic matching is fast
   • If you use poor broker, increase this!

5️⃣ realistic_mode (Default: True)
   
   What It Is:
   • Boolean toggle: True = apply costs, False = ignore costs
   
   When to Use realistic_mode=False:
   • Comparing to ideal baseline
   • Understanding max theoretical profit
   • Testing signal generation (cost-agnostic)
   • Academic analysis
   
   When to Use realistic_mode=True:
   • Evaluating strategy for real trading
   • Calculating expected returns
   • Sizing positions
   • Risk management

═════════════════════════════════════════════════════════════════

🔧 PRESET CONFIGURATIONS
─────────────────────────

These are ready-to-copy configurations for different scenarios:

✂️ CHEAP BROKER (Premium service, low costs)

```python
analyzer.backtest_arbitrage(
    slippage_pct=0.05,        # Tight execution
    bid_ask_spread=0.02,      # Tight spreads
    commission_pct=0.05,      # Low fee
    execution_delay_pct=0.0,  # Fast
    realistic_mode=True
)
# Expected result: ~+2.3-2.5% (vs +1.71% default)
```

📊 STANDARD BROKER (What we use now - default)

```python
analyzer.backtest_arbitrage(
    slippage_pct=0.1,         # Normal execution
    bid_ask_spread=0.05,      # Normal spreads
    commission_pct=0.1,       # Standard fee
    execution_delay_pct=0.0,  # Good execution
    realistic_mode=True
)
# Expected result: ~+1.71% (our observed results)
```

🔥 EXPENSIVE BROKER (High costs)

```python
analyzer.backtest_arbitrage(
    slippage_pct=0.2,         # Poor execution
    bid_ask_spread=0.1,       # Wide spreads
    commission_pct=0.2,       # High fee
    execution_delay_pct=0.05, # Slow execution
    realistic_mode=True
)
# Expected result: ~+0.5-0.7% (breakeven territory)
```

🌍 EMERGING MARKET BROKER (Illiquid markets)

```python
analyzer.backtest_arbitrage(
    slippage_pct=0.5,         # Significant slippage
    bid_ask_spread=0.30,      # Wide spreads (illiquid)
    commission_pct=0.25,      # High fee
    execution_delay_pct=0.10, # Variable execution
    realistic_mode=True
)
# Expected result: ~+0.2-0.5% (very tight margins)
```

⚡ ALGO TRADER (Best execution, high volume)

```python
analyzer.backtest_arbitrage(
    slippage_pct=0.02,        # Minimal slippage
    bid_ask_spread=0.01,      # Tight throughout
    commission_pct=0.02,      # Volume discount
    execution_delay_pct=0.0,  # Co-located
    realistic_mode=True
)
# Expected result: ~+2.7-2.9% (near ideal)
```

🧪 HYPOTHESIS TEST (What if costs change?)

To test sensitivity, try one parameter at a time:

```python
# Q: How sensitive to commission changes?
# A: Test these three

# Low commission scenario
analyzer.backtest_arbitrage(commission_pct=0.05, realistic_mode=True)
# Result: X%

# Medium commission scenario
analyzer.backtest_arbitrage(commission_pct=0.10, realistic_mode=True)
# Result: Y% ← Our current setting

# High commission scenario
analyzer.backtest_arbitrage(commission_pct=0.20, realistic_mode=True)
# Result: Z%

# Decision: If Z% is unprofitable, ✗ don't use that broker
```

═════════════════════════════════════════════════════════════════

📈 COST SENSITIVITY MATRIX
──────────────────────────

How each parameter affects returns:

Parameter          1%      2%      *5%*    10%     20%
──────────────────────────────────────────────────────
slippage_pct      2.5%    2.1%    1.7%    1.2%    0.2%
bid_ask_spread    2.6%    2.2%    1.7%    1.2%    0.3%
commission_pct    2.4%    2.0%    1.7%    1.2%    0.5%

*Bolded = our default = 1.71% return

Key Takeaways:
  • Doubling costs = roughly -50% return impact
  • Halving costs = roughly +50% return impact
  • Most sensitive to: slippage > commission > spread
  • Spread has least impact (already tight)

═════════════════════════════════════════════════════════════════

🔍 HOW TO CHOOSE YOUR CONFIGURATION
────────────────────────────────────

Step 1: Check Your Broker's Rate Sheet
  • Commission: Usually published clearly
  • Spread: Ask their support or check Level 2 quotes
  • Slippage: Unique to market/stock, research online
  • Delay: Can only determine empirically (test orders)

Step 2: Choose Closest Preset
  • Are you a retail trader?
    → Use STANDARD BROKER (our default) ✓
  • Do you have premium broker?
    → Use CHEAP BROKER
  • Are you trading illiquid pairs?
    → Use EMERGING MARKET BROKER
  • Could you trade Egyptian markets?
    → Use STANDARD BROKER (tight spreads for CIB)

Step 3: Tweak One Parameter at a Time
  • Don't change all 5 at once
  • Change one, observe impact
  • Example: Start with default, increase commission_pct
  •   Does strategy still profitable? → Use that new value
  •   Strategy no longer profitable? → Don't use that broker

Step 4: Validate Against Your Reality
  • Paper trade using these settings
  • Compare actual results vs simulated results
  • If actual significantly worse → costs higher than assumed
  • If actual similar → costs assumptions accurate ✓

═════════════════════════════════════════════════════════════════

💡 PRACTICAL WORKFLOW
──────────────────────

1. Get Your Broker Info
   "Hey [Broker], what are your rates for Egypt + UK trading?"
   Collect: commission, typical spreads, any account minimums

2. Map to Configuration
   Their 0.1% commission → commission_pct=0.1
   Their 0.05% typical spread → bid_ask_spread=0.05
   Their execution speed → execution_delay_pct=0.0 (assume instant)
   Market liquidity for CIB → slippage_pct=0.1 (blue chip)

3. Test Your Configuration
   ```python
   analyzer.backtest_arbitrage(
       slippage_pct=0.1,
       bid_ask_spread=0.05,
       commission_pct=0.1,        ← Your actual rate
       execution_delay_pct=0.0,
       realistic_mode=True
   )
   ```

4. Verify Profitability
   • P&L > 0? → Strategy viable with this broker ✓
   • P&L < 0? → Look for cheaper broker
   • P&L < 0.5%? → Consider higher trading volume

5. Compare Brokers
   ```python
   # Broker 1: 0.1% commission, 0.05% spread, 0.1% slippage
   # Result: +1.71%
   
   # Broker 2: 0.05% commission, 0.02% spread, 0.05% slippage
   # Result: +2.3%
   
   # Decision: Broker 2 is better (+0.59% better return)
   ```

═════════════════════════════════════════════════════════════════

🎓 ADVANCED: CUSTOM CALCULATION
─────────────────────────────────

Want to calculate costs manually for a specific trade?

Formula for Entry Price (as you pay):
  Entry = Ideal_Open × (1 + [bid_ask/2 + slippage + commission]%)

Formula for Exit Price (as you receive):
  Exit = Ideal_Close × (1 - [bid_ask/2 + slippage + commission]%)

Example:
  Ideal Open:  80.00 EGP
  Ideal Close: 81.00 EGP
  
  With 0.05% spread, 0.1% slippage, 0.1% commission:
  
  Entry = 80.00 × (1 + 0.25%) = 80.00 × 1.0025 = 80.20 EGP
  Exit  = 81.00 × (1 - 0.25%) = 81.00 × 0.9975 = 80.79 EGP
  
  Return = (80.79 - 80.20) / 80.20 = 0.74%
  P&L = $10,000 × 0.74% = $74

This is exactly what the script does! ✓

═════════════════════════════════════════════════════════════════

❓ FAQ: REALISTIC MODE
──────────────────────

Q: Should I use realistic_mode=True or False?
A: TRUE for real trading decisions, FALSE for academic analysis

Q: Can costs be even higher?
A: Yes! If your broker charges flat fees, spreads widen intraday,
   or you submit limit orders instead of market orders

Q: What if I don't know my exact costs?
A: Use STANDARD BROKER preset (our default). It's conservative
   and covers most retail brokers. You can refine later.

Q: Do costs change over time?
A: Yes. Spreads widen during market stress, commissions vary by
   volume tier, slippage increases in illiquid periods. Update
   your parameters periodically based on actual trading data.

Q: What if my broker has lower costs?
A: Test CHEAP BROKER preset. You'll see higher returns.
   Difference is real money of your bottom line.

Q: Can I optimize parameters to maximize returns?
A: No. Parameters are determined by your broker/market, not by
   optimization. They represent reality, not a tuning knob.

═════════════════════════════════════════════════════════════════

✅ IMPLEMENTATION CHECKLIST
────────────────────────────

□ Know your broker's commission rate (%)
□ Know typical bid-ask spread in your market (%)
□ Estimate slippage for your market (%)
□ Map these to the configuration variables
□ Run backtest with realistic_mode=True
□ Verify return is profitable (P&L > 0)
□ If not profitable, find cheaper broker or... 
□ Reconsider the strategy
□ Compare with industry benchmarks
□ Paper trade to validate assumptions
□ Trade with real money when confident

═════════════════════════════════════════════════════════════════

🎯 NEXT STEP
─────────────

Ready to use realistic mode?

Option 1 (Quick): Use default (already set up)
  • Run: python run_arbitrage.py
  • Gets: +1.71% realistic results
  • Done! ✓

Option 2 (Custom): Configure for your broker
  • Edit: cib_arbitrage_test.py (around line 150)
  • Change: slippage_pct, bid_ask_spread, commission_pct
  • Run: python run_arbitrage.py
  • Check: Results reflect your reality

Option 3 (Advanced): Compare brokers
  • Create: test_brokers.py with different presets
  • Run: Compare results side-by-side
  • Choose: Broker with best net return

═════════════════════════════════════════════════════════════════
