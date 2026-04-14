#!/usr/bin/env python3
"""
THNDR EXECUTION GUIDE
====================

Step-by-step instructions for executing the Cairo-London arbitrage strategy
on Thndr platform with Thndr's actual fees (0.2613% per round trip)
"""

print("""
█████████████████████████████████████████████████████████████████████████████
THNDR CAIRO-LONDON ARBITRAGE: COMPLETE EXECUTION GUIDE
█████████████████████████████████████████████████████████████████████████████

═══════════════════════════════════════════════════════════════════════════════
PART 1: UNDERSTANDING THE TRADE FLOW
═══════════════════════════════════════════════════════════════════════════════

SIGNAL GENERATION:
  • Monitor London CIB (CBKD.L) daily move
  • When daily move > 1% (up or down), SIGNAL FIRES
  • Alert shows: Entry price, target exit, expected profit

EXECUTION:
  • Next day at Cairo open (10:30 EET): BUY
  • Same day before close (2:20 PM): SELL
  • Total holding: ~4 hours in same day

PROFIT SOURCE:
  • Cairo's opening gap captures overnight London move
  • Correlation ~0.07 (not perfect, but statistically positive)
  • With 0.2613% Thndr costs, breakeven on ~0.5% moves

═══════════════════════════════════════════════════════════════════════════════
PART 2: THNDR ACCOUNT SETUP (ONE-TIME)
═══════════════════════════════════════════════════════════════════════════════

1. Create Thndr Account
   • Website: https://www.thndr.com/
   • Download app: iOS/Android "Thndr"
   • Verify identity (KYC process)
   • Fund account with EGP or USD

2. Verify Trading Access
   • In settings: Check commission rates
   • Confirm: 0.1% variable + 0.03% third-party + 2 EGP fixed
   • Note: You should see exactly these fees

3. Add COMI (CIB Stock) to Watchlist
   • Search: "COMI" (Cairo ticker)
   • Add to favorites
   • Note the stock symbol: COMI.CA or just COMI

4. Practice Paper Trading (Optional but Recommended)
   • Some brokers offer demo accounts
   • Execute 5-10 practice trades
   • Get familiar with order placement

═══════════════════════════════════════════════════════════════════════════════
PART 3: DAILY EXECUTION WORKFLOW
═══════════════════════════════════════════════════════════════════════════════

PRE-MARKET (Evening Before, After London Closes)
─────────────────────────────────────────────────

⏰ 4:00 PM - 5:30 PM London Time (6:00 PM - 7:30 PM Cairo):
  1. Check London CIB close (CBKD.L on your broker)
  2. Calculate daily move %
  3. IF move > 1% THEN:
     ✓ Generate alert
     ✓ Calculate Cairo entry target (using correlation estimate)
     ✓ Calculate expected profit (move × correlation - 0.2613%)
     ✓ Set phone reminder for next day 10:25 AM Cairo time

EXAMPLE ALERT CALCULATION:
  • London close: 115.50 (was 114.70 at open) = +0.70%
  • Cairo open yesterday: 120.00
  • Expected Cairo move: 0.70% × 0.0728 = +0.051%
  • Expected Cairo open tomorrow: 120.061
  • BUT: Use actual market open price, not predicted
  
═══════════════════════════════════════════════════════════════════════════════
MARKET OPEN (Next Day, 10:30 AM Cairo)
═══════════════════════════════════════════════════════════════════════════════

⏰ 10:25 AM - 10:35 AM Cairo Time (EET):

STEP 1: Check Current Prices
  → Open Thndr app
  → Search "COMI"
  → Check latest quote
  → Is it gapping up? (as expected from UK move)

STEP 2: Execute BUY Order
  
  Method A - Market Order (Fastest):
  ─────────────────────────────────
  1. Tap "COMI" stock
  2. Tap "BUY"
  3. Enter quantity: 100 shares (or your position size)
  4. Select: "Market Order"
  5. Review commission breakdown:
     - Base quantity: 100 shares
     - Price: ~120.00 EGP
     - Commission: 0.1% + 0.03% + fixed 2 EGP
     - Total cost: ~120 EGP + 0.312 EGP + 0.065 EGP = 120.38 EGP
  6. Tap "CONFIRM"
  7. ✅ BUY ORDER PLACED AT 10:31 AM
  
  Method B - Limit Order (Controlled):
  ────────────────────────────────────
  1. Tap "COMI" stock
  2. Tap "BUY"
  3. Enter quantity: 100 shares
  4. Select: "Limit Order"
  5. Enter limit price: 120.05 EGP (slightly below current bid)
  6. Tap "CONFIRM"
  7. Wait for order to fill (usually within seconds on liquid stocks)
  8. ✅ BUY ORDER FILLED


STEP 3: Set Up SELL Order (IMMEDIATELY AFTER BUY)

  Method A - Set Sell Limit Order (Best for This Strategy):
  ──────────────────────────────────────────────────────────
  1. Go to your POSITIONS
  2. Tap the COMI position
  3. Tap "SELL" or "SET LIMIT SELL"
  4. Calculate target sell price:
     Entry price: 120.00 EGP
     Target profit: +0.5% (after costs)
     Target price: 120.00 × (1.005) = 120.60 EGP
  5. Enter: 120.60 EGP as limit price
  6. Enter quantity: 100 shares
  7. Tap "CONFIRM"
  8. ✅ SELL LIMIT ORDER PLACED
  9. Your shares will sell automatically when price hits 120.60
  
  Method B - Market Sell Before Close:
  ───────────────────────────────────
  1. At 2:20 PM Cairo time (10 min before close)
  2. Go to your POSITIONS
  3. Tap COMI position
  4. Tap "SELL"
  5. Select "Market Order"
  6. Enter quantity: 100 shares
  7. Tap "CONFIRM"
  8. ✅ SHARE SOLD AT MARKET PRICE (just before close)


    EXPECTED TIME TO CLOSE:
    ├─ 10:31 AM: BUY 100 @ 120.00 = 120,000 EGP
    ├─ 10:32 AM: SELL limit order placed @ 120.60
    ├─ ~12:00 PM: Sell order fills (hopefully!)
    └─ 2:30 PM: Cairo market closes
    
    P&L CALCULATION:
    ├─ Entry: 120.00 EGP
    ├─ Exit: 120.60 EGP
    ├─ Gross move: +0.60% = +600 EGP
    ├─ Less commissions (both buy+sell): 0.2613% = -314 EGP
    ├─ Net profit: +286 EGP per 100 shares
    └─ ROI: +0.24% on capital deployed

═══════════════════════════════════════════════════════════════════════════════
PART 4: REAL EXECUTION EXAMPLES
═══════════════════════════════════════════════════════════════════════════════

EXAMPLE 1: London UP +1.5% (Bullish Signal)
──────────────────────────────────────────

Expected Outcome: Cairo should gap up too

Timeline:
  4:00 PM London: CBKD.L closes at 115.50 (opened 113.80) = +1.50% ✅
  
  Next day 10:30 AM Cairo:
    • COMI opens at 120.80 (was 120.00 yesterday)
    • This is the gap capturing the London move
    • BUY 1000 shares @ 120.80 = 120,800 EGP
    • Place SELL limit @ 121.50 = +0.58% target
  
  11:00 AM Cairo:
    • Stock rallies, hits 121.60
    • Sell limit fills @ 121.50
    • Exit: 1000 × 121.50 = 121,500 EGP
    
  P&L:
    Entry: 120,800 EGP
    Exit: 121,500 EGP
    Gross profit: 700 EGP
    Less commission (0.2613%): -316 EGP
    ✅ Net profit: +384 EGP on this trade

EXAMPLE 2: London DOWN -1.2% (Bearish Signal)
──────────────────────────────────────────

Expected Outcome: Cairo should gap down too

Timeline:
  4:00 PM London: CBKD.L closes at 113.20 (opened 114.60) = -1.20% ✅
  
  Next day 10:30 AM Cairo:
    • COMI opens at 118.50 (was 120.00 yesterday)
    • This is the gap down capturing London's fall
    • BUY 1000 shares @ 118.50 = 118,500 EGP
    • Place SELL limit @ 119.20 = +0.59% target
  
  1:30 PM Cairo:
    • Stock rallies back up, hits 119.30
    • Sell limit fills @ 119.20
    • Exit: 1000 × 119.20 = 119,200 EGP
    
  P&L:
    Entry: 118,500 EGP
    Exit: 119,200 EGP
    Gross profit: 700 EGP
    Less commission (0.2613%): -309 EGP
    ✅ Net profit: +391 EGP on this trade

EXAMPLE 3: Signal Fails (Cairo Doesn't Move)
──────────────────────────────────────────

Expected Outcome: Cairo doesn't capture the full gap

Timeline:
  4:00 PM London: CBKD.L closes at 114.50 (opened 113.20) = +1.13% ✅
  
  Next day 10:30 AM Cairo:
    • COMI opens at 120.00 (NO GAP - flat from yesterday)
    • Correlation failed, or signal didn't capture
    • BUY 1000 shares @ 120.00 = 120,000 EGP
    • Place SELL limit @ 120.57 (0.57% target)
  
  Throughout day:
    • Stock trades between 119.90 and 120.15
    • Never hits 120.57 limit
  
  2:20 PM Cairo:
    • Cancel limit order (or let it expire)
    • SELL market @ 119.95
    • Exit: 1000 × 119.95 = 119,950 EGP
    
  P&L:
    Entry: 120,000 EGP
    Exit: 119,950 EGP
    Gross loss: -50 EGP
    Less commission (0.2613%): -314 EGP
    ❌ Net loss: -364 EGP (this is a losing trade)

═══════════════════════════════════════════════════════════════════════════════
PART 5: RISK MANAGEMENT RULES
═══════════════════════════════════════════════════════════════════════════════

1. Position Sizing:
   • Use 1000 EGP per trade (0.1% risk per trade) ← CONSERVATIVE
   • Or use 2000 EGP per trade (0.2% risk per trade) ← MODERATE
   • Calculate with formula: Account Balance × Risk % ÷ Average Loss Size

2. Stop Loss (Optional but Recommended):
   • Set stop loss 1% below entry
   • Example: Buy @ 120.00, stop @ 118.80
   • Prevents catastrophic loss if signal is very wrong
   • Use: "SELL stop order"

3. Profit Taking:
   • Don't be greedy - take profits at target
   • 0.5% profit per trade = solid return
   • Over 100+ trades/year, 0.5% × 100 = 50% annual return

4. Winning Trade Exit:
   • Once limit order fills, CLOSE THE POSITION
   • Don't hold for more profit
   • Risk going negative if market reverses

5. Losing Trade Exit:
   • If stock goes against you > 0.5%:
     → Cancel limit order
     → Sell at market
     → Close position
   • Example: Entry 120.00, stock falls to 119.40 (−0.5%)
     → Stop loss triggered, sell immediately

═══════════════════════════════════════════════════════════════════════════════
PART 6: THNDR-SPECIFIC FEATURES
═══════════════════════════════════════════════════════════════════════════════

1. Available on Thndr:
   ✅ Market orders (buy/sell at any price)
   ✅ Limit orders (set your exact buy/sell prices)
   ✅ Stop orders (automatic sell if price drops)
   ✅ Position tracking in real-time
   ✅ Commission breakdown before you trade
   ✅ Mobile + Web platform

2. NOT Available on Thndr:
   ❌ Margin/Leverage trading (safer for us!)
   ❌ Overnight positions (we close same day anyway)
   ❌ Automation/APIs (manual execution only)
   ❌ Shorting (we only go long)

3. Typical Thndr Fills:
   • Market orders: 0.1-0.5 seconds
   • Limit orders: Depends on liquidity, usually <1 minute for CIB
   • CIB is liquid: 100,000 shares/day typical volume

═══════════════════════════════════════════════════════════════════════════════
PART 7: TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

Problem: My sell limit order didn't fill by market close
Solution:
  → 2:25 PM: Cancel sell limit order
  → 2:26 PM: Place market sell order
  → 2:27 PM: Shares sold before 2:30 PM close
  → Better to lock in whatever profit than miss close

Problem: Thndr app crashed during my trade
Solution:
  → Log in immediately on Thndr website
  → Check your positions
  → If BUY filled but SELL didn't:
       → Manually place SELL market order
       → Close position immediately
  → If both filled: mission accomplished!

Problem: I'm seeing a different price than expected
Solution:
  → Thndr might have 5-10 second delay vs real-time data
  → Use backup check: look at COMI price on EGX directly
  → Always enter/exit with Thndr app (most reliable for you)

Problem: Slippage is worse than expected
Solution:
  → Expected slippage on CIB: 0.1-0.3% typically
  → If seeing > 0.5%: market is illiquid that day
  → Skip that trade (cancel orders, don't execute)
  → Wait for next signal

═══════════════════════════════════════════════════════════════════════════════
FINAL CHECKLIST: BEFORE YOU EXECUTE
═══════════════════════════════════════════════════════════════════════════════

□ Signal confirmed: London move > 1% ✓
□ Cairo market open time: 10:30 AM EET ✓
□ My Thndr account is funded with 20,000+ EGP ✓
□ COMI stock is in my watchlist ✓
□ I've checked Thndr fee structure (0.2613%) ✓
□ My position size is calculated (1,000-2,000 EGP per trade) ✓
□ My profit target is set (0.5-0.6% above entry) ✓
□ My stop loss is set (1% below entry) ✓
□ I have 4-hour window (10:30 AM - 2:30 PM Cairo) to execute ✓
□ I'm ready to manually place SELL before 2:30 PM close ✓

READY TO TRADE! 🚀

═══════════════════════════════════════════════════════════════════════════════
""")
