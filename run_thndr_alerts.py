#!/usr/bin/env python3
"""
Quick Start: Using Thndr Trading Alerts
Generates real-time trading signals with manual execution instructions
"""

from thndr_alerts import ThndrTradingAlerts, run_alert_service

# Example 1: Check for signals once
print("\n" + "="*70)
print("EXAMPLE 1: Check Current Signal (One-time)")
print("="*70)

alerts = ThndrTradingAlerts('COMI.CA', 'CBKD.L')
signal, london_move, cairo_prices = alerts.check_signal(threshold=1.0)

if signal and signal['has_signal']:
    print(f"\n✅ Signal Found!")
    print(f"London Move: {london_move:+.2f}%")
    alerts.print_alert(signal)
    alerts.save_alert_log(alerts.generate_alert(signal), 'thndr_alerts.log')
else:
    print(f"\n❌ No signal at this time")
    if london_move:
        print(f"Current London Move: {london_move:+.2f}% (need > 1% to trigger)")

print("\n")

# Example 2: Continuous monitoring (uncomment to run)
# Runs indefinitely, checks every 5 minutes
# Press Ctrl+C to stop
"""
print("\n" + "="*70)
print("EXAMPLE 2: Continuous Monitoring")
print("="*70)
print("This will check for signals every 5 minutes")
print("Alerts will be printed and logged to thndr_alerts.log\n")

run_alert_service(
    cairo_ticker='COMI.CA',
    london_ticker='CBKD.L',
    check_interval=300,  # 5 minutes
    threshold=1.0  # 1% move threshold
)
"""

# Example 3: Custom check with multiple pairs
print("\n" + "="*70)
print("EXAMPLE 3: Check Multiple Pairs")
print("="*70)

pairs = [
    ('COMI.CA', 'CBKD.L'),   # CIB
    ('HRHO.CA', 'EFGD.L'),   # Heliopolis Housing
]

for cairo_ticker, london_ticker in pairs:
    print(f"\nChecking {cairo_ticker} vs {london_ticker}...")
    
    try:
        alerts = ThndrTradingAlerts(cairo_ticker, london_ticker)
        signal, london_move, cairo_prices = alerts.check_signal(threshold=1.0)
        
        if signal and signal['has_signal']:
            print(f"  ✅ SIGNAL FOUND! London move: {london_move:+.2f}%")
        else:
            if london_move:
                print(f"  ❌ No signal. London move: {london_move:+.2f}% (need > 1%)")
            else:
                print(f"  ⚠️  Could not fetch data")
    except Exception as e:
        print(f"  ⚠️  Error: {e}")

print("\n" + "="*70)
print("✨ Alert system ready!")
print("="*70)
print("\nTo use in production:")
print("  python thndr_alerts.py  # Check current signals once")
print("\nOr modify this file to uncomment Example 2 for continuous monitoring")
print("="*70 + "\n")
