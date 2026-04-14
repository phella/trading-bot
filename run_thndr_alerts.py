#!/usr/bin/env python3
"""
Run Thndr Trading Alerts - Cairo-London Arbitrage Alert Examples
================================================================

This module shows how to use the ThndrTradingAlerts system with actual
Thndr broker parameters.

IMPORTANT: Before running, update the THNDR_* constants below with
your actual broker costs from the Thndr platform dashboard.
"""

from thndr_alerts import ThndrTradingAlerts
from datetime import datetime

# ============================================================================
# THNDR BROKER PARAMETERS - UPDATE THESE WITH YOUR ACTUAL COSTS
# ============================================================================
# You can find these values in your Thndr account dashboard

THNDR_COMMISSION_PCT = 0.10           # Commission as % of transaction (e.g., 0.10 = 0.10%)
THNDR_BID_ASK_SPREAD = 0.08           # Bid-ask spread as % (typical for CIB on Thndr)
THNDR_SLIPPAGE_PCT = 0.15             # Slippage from execution delay (1-min buy delay = 0.15%)
THNDR_EXECUTION_DELAY_PCT = 0.20      # Additional % loss for buying at 10:31 vs 10:30 ECT

# Market timing constraints (EGX market hours)
MARKET_OPEN_TIME = "10:30 EET"        # Cairo market opens 10:30 Eastern European Time
BUY_EXECUTION_TIME = "10:31 EET"      # You'll execute buy 1 minute after open
MARKET_CLOSE_TIME = "14:30 EET"       # Cairo market closes 14:30 EET

# Note: No premarket trading available on EGX
# All orders must be placed during regular market hours (10:30 - 14:30 EET)


# ============================================================================
# EXAMPLE 1: Real-time Alert for Primary Pair (COMI/CBKD - CIB arbitrage)
# ============================================================================

def example_1_cib_arbitrage():
    """
    Real-time alert system for CIB (Cairo Commercial & Investment Bank):
    - Monitors London CIB daily moves
    - Generates Cairo trade signals when London move > 1%
    - Includes full Thndr execution costs
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: CIB Arbitrage Real-Time Alert")
    print("="*70)
    
    # Initialize alert system with Thndr-specific costs
    alerts = ThndrTradingAlerts(
        cairo_ticker="COMI",           # CIB on Cairo
        london_ticker="CBKD",          # CIB on London LSE
        commission_pct=THNDR_COMMISSION_PCT,
        bid_ask_spread=THNDR_BID_ASK_SPREAD,
        slippage_pct=THNDR_SLIPPAGE_PCT,
        execution_delay_pct=THNDR_EXECUTION_DELAY_PCT
    )
    
    # Check for trading signal
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking CIB signal...")
    london_move = alerts.get_current_london_move()
    
    if london_move > 1.0:
        print(f"✓ SIGNAL FOUND: London CIB moved {london_move:.2f}%")
        alert = alerts.generate_alert()
        alerts.print_alert()
        alerts.save_alert_log()
        return True
    else:
        print(f"✗ No signal yet. London CIB move: {london_move:.2f}% (need > 1.0%)")
        return False


# ============================================================================
# EXAMPLE 2: Paper Trading - Test Signal Generation Without Execution
# ============================================================================

def example_2_test_signal_generation():
    """
    Test the alert system without placing real trades:
    - Simulates what the alert would be if a signal fired
    - Useful for validation and debugging
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Signal Generation Test (No Execution)")
    print("="*70)
    
    print(f"\nConfigured Thndr Parameters:")
    print(f"  Commission:           {THNDR_COMMISSION_PCT}%")
    print(f"  Bid-Ask Spread:       {THNDR_BID_ASK_SPREAD}%")
    print(f"  Execution Slippage:   {THNDR_SLIPPAGE_PCT}%")
    print(f"  Execution Delay:      {THNDR_EXECUTION_DELAY_PCT}%")
    print(f"  ---")
    print(f"  Total Costs Per Trade: {(THNDR_COMMISSION_PCT + THNDR_BID_ASK_SPREAD + THNDR_SLIPPAGE_PCT + THNDR_EXECUTION_DELAY_PCT):.2f}%")
    
    print(f"\nHousing Finance (HRHO/EFGD) - Example Scenario:")
    
    # Initialize for different pair
    alerts = ThndrTradingAlerts(
        cairo_ticker="HRHO",
        london_ticker="EFGD",
        commission_pct=THNDR_COMMISSION_PCT,
        bid_ask_spread=THNDR_BID_ASK_SPREAD,
        slippage_pct=THNDR_SLIPPAGE_PCT,
        execution_delay_pct=THNDR_EXECUTION_DELAY_PCT
    )
    
    print(f"  Cairo current price: Fetching...")
    try:
        cairo_data = alerts.get_cairo_current_prices()
        print(f"  Signal threshold: 1.0% (London move must exceed this)")
        print(f"  If signal fires, alert will show Thndr execution prices with realistic costs")
    except Exception as e:
        print(f"  (Note: Prices require market hours - {e})")
    
    print(f"\nExecution Constraints (EGX Market):")
    print(f"  Market Open:    {MARKET_OPEN_TIME}")
    print(f"  Buy Execution:  {BUY_EXECUTION_TIME} (1 minute after open)")
    print(f"  Market Close:   {MARKET_CLOSE_TIME}")
    print(f"  Position Hold:  ~4 hours (same-day trade)")
    print(f"  Premarket:      NOT AVAILABLE on EGX")


# ============================================================================
# EXAMPLE 3: Continuous Monitoring Loop (for live deployment on VPS)
# ============================================================================

def example_3_continuous_monitoring():
    """
    Continuous monitoring loop suitable for VPS deployment:
    - Checks for signals on a schedule
    - Logs all activity to file
    - Can be run 24/7 or scheduled for market hours only
    
    NOTE: For production, consider running only 10:00-14:45 EET
    to ensure sufficient margin for order placement before market close
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Continuous Monitoring Setup (Production Ready)")
    print("="*70)
    
    print(f"\nConfiguration for Thndr Alert Service:")
    print(f"  Primary Pair:        COMI/CBKD (CIB)")
    print(f"  Backup Pair:         HRHO/EFGD (Housing)")
    print(f"  Commission Rate:     {THNDR_COMMISSION_PCT}%")
    print(f"  Spread (CIB):        {THNDR_BID_ASK_SPREAD}%")
    print(f"  Slippage (1-min):    {THNDR_SLIPPAGE_PCT}%")
    print(f"  Delay Cost:          {THNDR_EXECUTION_DELAY_PCT}%")
    
    print(f"\nFor deployment, instantiate alerts with config:")
    print(f"""
    alerts = ThndrTradingAlerts(
        cairo_ticker="COMI",
        london_ticker="CBKD",
        commission_pct={THNDR_COMMISSION_PCT},
        bid_ask_spread={THNDR_BID_ASK_SPREAD},
        slippage_pct={THNDR_SLIPPAGE_PCT},
        execution_delay_pct={THNDR_EXECUTION_DELAY_PCT}
    )
    
    # Then call in loop:
    # - alerts.check_signal() → returns True if London > 1%
    # - alerts.generate_alert() → calculates Thndr execution prices
    # - alerts.print_alert() → displays step-by-step instructions
    # - alerts.save_alert_log() → logs to thndr_alerts.log
    """)
    
    print(f"\nPython Scheduling Example (using schedule library):")
    print(f"""
    import schedule
    
    def check_cib_signal():
        alerts = ThndrTradingAlerts(
            'COMI', 'CBKD',
            commission_pct={THNDR_COMMISSION_PCT},
            bid_ask_spread={THNDR_BID_ASK_SPREAD},
            slippage_pct={THNDR_SLIPPAGE_PCT},
            execution_delay_pct={THNDR_EXECUTION_DELAY_PCT}
        )
        if alerts.check_signal():
            alerts.generate_alert()
            alerts.print_alert()
            alerts.save_alert_log()
    
    # Check every 5 minutes during market hours
    schedule.every(5).minutes.do(check_cib_signal)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
    """)


# ============================================================================
# MAIN - Run the examples
# ============================================================================

if __name__ == "__main__":
    print("\n" + "█"*70)
    print("THNDR TRADING ALERTS - Examples & Configuration")
    print("█"*70)
    
    print(f"\nCurrent Thndr Parameters (from config):")
    print(f"  Commission:      {THNDR_COMMISSION_PCT}%")
    print(f"  Bid-Ask Spread:  {THNDR_BID_ASK_SPREAD}%")
    print(f"  Slippage:        {THNDR_SLIPPAGE_PCT}%")
    print(f"  Execution Delay: {THNDR_EXECUTION_DELAY_PCT}%")
    print(f"  Total Cost/Trade: {(THNDR_COMMISSION_PCT + THNDR_BID_ASK_SPREAD + THNDR_SLIPPAGE_PCT + THNDR_EXECUTION_DELAY_PCT):.2f}%")
    
    print(f"\n⚠️  BEFORE RUNNING:")
    print(f"  1. Update THNDR_* constants above with your actual broker costs")
    print(f"  2. Run during Cairo market hours (10:30-14:30 EET)")
    print(f"  3. Current time zones: EET is UTC+2 (winter) or UTC+3 (summer)")
    print(f"  4. Default values shown are reasonable estimates - confirm with Thndr dashboard")
    
    # Run examples
    print("\n" + "─"*70)
    example_1_cib_arbitrage()
    
    print("\n" + "─"*70)
    example_2_test_signal_generation()
    
    print("\n" + "─"*70)
    example_3_continuous_monitoring()
    
    print("\n" + "█"*70)
    print("For full documentation, see: docs/THNDR_INTEGRATION.md")
    print("Configuration template: thndr_config.toml")
    print("█"*70 + "\n")
