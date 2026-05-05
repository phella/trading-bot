"""
Thndr Trading Alerts: Real-time signal generation with manual execution instructions
Generates alerts for Cairo-London arbitrage opportunities
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, time
import warnings
warnings.filterwarnings('ignore')


class ThndrTradingAlerts:
    """Generate real-time trading signals and alerts for manual Thndr execution"""
    
    def __init__(self, cairo_ticker, london_ticker, 
                 commission_pct=0.10, bid_ask_spread=0.08, 
                 slippage_pct=0.15, execution_delay_pct=0.20):
        """
        Initialize alert system with Thndr-specific parameters
        
        Args:
            cairo_ticker: Cairo stock ticker (e.g., 'COMI.CA')
            london_ticker: London GDR ticker (e.g., 'CBKD.L')
            commission_pct: Thndr commission rate (default 0.10%)
            bid_ask_spread: Thndr bid-ask spread (default 0.08%)
            slippage_pct: Slippage from 1-min delay (default 0.15%)
            execution_delay_pct: Execution delay impact (default 0.20%)
        """
        self.cairo_ticker = cairo_ticker
        self.london_ticker = london_ticker
        self.london_daily_return = None
        self.cairo_prices = None
        
        # Thndr-specific costs
        self.commission_pct = commission_pct
        self.bid_ask_spread = bid_ask_spread
        self.slippage_pct = slippage_pct
        self.execution_delay_pct = execution_delay_pct
        
    def get_current_london_move(self):
        """Get today's London market move (% change from open to current close)"""
        try:
            # Download latest London data
            london = yf.download(self.london_ticker, period='5d', progress=False)
            
            if london.empty:
                return None, None
            
            # Today's data
            today = london.iloc[-1]
            yesterday = london.iloc[-2] if len(london) > 1 else None
            
            london_open = today['Open']
            london_close = today['Close']
            london_move_pct = ((london_close - london_open) / london_open) * 100
            
            return london_move_pct, {
                'open': london_open,
                'close': london_close,
                'high': today['High'],
                'low': today['Low']
            }
            
        except Exception as e:
            print(f"Error fetching London data: {e}")
            return None, None
    
    def get_cairo_current_prices(self):
        """Get current Cairo market prices"""
        try:
            cairo = yf.download(self.cairo_ticker, period='1d', progress=False)
            
            if cairo.empty:
                return None
            
            today = cairo.iloc[-1]
            
            return {
                'open': today['Open'],
                'close': today['Close'],
                'high': today['High'],
                'low': today['Low'],
                'time': datetime.now()
            }
            
        except Exception as e:
            print(f"Error fetching Cairo data: {e}")
            return None
    
    def check_signal(self, london_move_threshold=1.0):
        """Check if trading signal exists"""
        london_move, london_data = self.get_current_london_move()
        cairo_prices = self.get_cairo_current_prices()
        
        if london_move is None or cairo_prices is None:
            return None, None, None
        
        signal = {
            'has_signal': london_move > london_move_threshold,
            'london_move': london_move,
            'london_data': london_data,
            'cairo_prices': cairo_prices,
            'timestamp': datetime.now()
        }
        
        return signal, london_move, cairo_prices
    
    def generate_alert(self, signal, realistic_costs=True):
        """Generate beautifully formatted alert with execution instructions"""
        
        if not signal or not signal['has_signal']:
            return None
        
        london_move = signal['london_move']
        london_data = signal['london_data']
        cairo_prices = signal['cairo_prices']
        
        # Calculate P&L estimates
        cairo_open = cairo_prices['open']
        cairo_close = cairo_prices['close']
        
        # Ideal scenario
        ideal_pnl_pct = ((cairo_close - cairo_open) / cairo_open) * 100
        ideal_pnl_dollars = 10000 * (ideal_pnl_pct / 100)
        
        # Realistic scenario with Thndr costs
        if realistic_costs:
            # Entry costs (buying)
            bid_ask_entry = (cairo_open * self.bid_ask_spread / 100) / 2
            slippage_entry = cairo_open * self.slippage_pct / 100
            delay_entry = cairo_open * self.execution_delay_pct / 100
            commission_entry = cairo_open * self.commission_pct / 100
            
            entry_price = cairo_open + bid_ask_entry + slippage_entry + delay_entry + commission_entry
            
            # Exit costs (selling)
            bid_ask_exit = (cairo_close * self.bid_ask_spread / 100) / 2
            slippage_exit = cairo_close * self.slippage_pct / 100
            delay_exit = cairo_close * self.execution_delay_pct / 100
            commission_exit = cairo_close * self.commission_pct / 100
            
            exit_price = cairo_close - bid_ask_exit - slippage_exit - delay_exit - commission_exit
            
            realistic_pnl_pct = ((exit_price - entry_price) / entry_price) * 100
            realistic_pnl_dollars = 10000 * (realistic_pnl_pct / 100)
        else:
            entry_price = cairo_open
            exit_price = cairo_close
            realistic_pnl_pct = ideal_pnl_pct
            realistic_pnl_dollars = ideal_pnl_dollars
        
        # Build alert message
        alert = {
            'timestamp': signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'signal_type': '🟢 BUY' if realistic_pnl_pct > 0 else '🔴 SELL',
            'london_move': london_move,
            'cairo_ticker': self.cairo_ticker,
            'london_ticker': self.london_ticker,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'ideal_pnl_pct': ideal_pnl_pct,
            'realistic_pnl_pct': realistic_pnl_pct,
            'ideal_pnl_dollars': ideal_pnl_dollars,
            'realistic_pnl_dollars': realistic_pnl_dollars,
            'cairo_open': cairo_open,
            'cairo_close': cairo_close,
            'london_data': london_data,
            'costs': {
                'commission_pct': self.commission_pct,
                'bid_ask_spread': self.bid_ask_spread,
                'slippage_pct': self.slippage_pct,
                'execution_delay_pct': self.execution_delay_pct
            }
        }
        
        return alert
    
    def format_alert_message(self, alert):
        """Format alert as human-readable message for manual execution"""
        
        if not alert:
            return None
        
        msg = f"""
{'='*70}
🚨 TRADING ALERT - {alert['timestamp']}
{'='*70}

SIGNAL: {alert['signal_type']}
London Daily Move: {alert['london_move']:+.2f}% (threshold: 1%)

PAIR INFORMATION:
  Cairo Ticker: {alert['cairo_ticker']}
  London Ticker: {alert['london_ticker']}

CURRENT CAIRO PRICES:
  Open:  {alert['cairo_open']:.2f} EGP
  Close: {alert['cairo_close']:.2f} EGP
  Daily Move: {((alert['cairo_close'] - alert['cairo_open']) / alert['cairo_open'] * 100):+.2f}%

EXECUTION INSTRUCTIONS (Manual on Thndr):
──────────────────────────────────────────

STEP 1: PLACE BUY ORDER (Cairo Open)
  └─ Open Thndr.com
  └─ Search for: {alert['cairo_ticker']}
  └─ Click BUY
  └─ Entry Price Target: {alert['entry_price']:.2f} EGP
  └─ OR Market Order (accept {alert['entry_price']:.2f} ± market spread)
  └─ Quantity: 100 shares
  └─ Submit Order

STEP 2: HOLD (Sun-Thu only, ~4 hours)
  └─ Entry confirmed ✓
  └─ Wait for Cairo market close
  └─ Monitor for unexpected price movements

STEP 3: PLACE SELL ORDER (Cairo Close)
  └─ Open Thndr.com
  └─ Search for: {alert['cairo_ticker']}
  └─ Click SELL
  └─ Exit Price Target: {alert['exit_price']:.2f} EGP
  └─ Quantity: 100 shares (same as buy)
  └─ Submit Order

EXPECTED OUTCOMES:
──────────────────

IDEAL (No Costs):
  Entry: {alert['cairo_open']:.2f} → Exit: {alert['cairo_close']:.2f}
  Return: {alert['ideal_pnl_pct']:+.2f}%
  P&L: ${alert['ideal_pnl_dollars']:+.2f}

REALISTIC (With Costs):
  Entry: {alert['entry_price']:.2f} → Exit: {alert['exit_price']:.2f}
  Return: {alert['realistic_pnl_pct']:+.2f}%
  P&L: ${alert['realistic_pnl_dollars']:+.2f}

THNDR ACTUAL COSTS TO DEDUCT:
  └─ Bid-Ask Spread: {alert['costs']['bid_ask_spread']:.2f}%
  └─ Slippage (1-min delay): {alert['costs']['slippage_pct']:.2f}%
  └─ Execution Delay: {alert['costs']['execution_delay_pct']:.2f}%
  └─ Commission: {alert['costs']['commission_pct']:.2f}%
  └─ TOTAL COST: {(alert['costs']['bid_ask_spread'] + alert['costs']['slippage_pct'] + alert['costs']['execution_delay_pct'] + alert['costs']['commission_pct']):.2f}%

RISK REMINDERS:
───────────────
⚠️  This is NOT financial advice
⚠️  Past performance ≠ future results
⚠️  You could lose money
⚠️  Start with small positions
⚠️  Use stop losses if available
⚠️  Never risk more than you can afford to lose

TRACKING:
─────────
□ Signal Generated: {alert['timestamp']}
□ Order 1 Placed: ________ @ ________ EGP
□ Order 1 Confirmed: ________ EGP
□ Order 2 Placed: ________ @ ________ EGP
□ Order 2 Confirmed: ________ EGP
□ Actual P&L: ________ EGP
□ Actual Return: ________ %

{'='*70}
"""
        return msg
    
    def print_alert(self, signal):
        """Print formatted alert to console"""
        alert = self.generate_alert(signal)
        if alert:
            message = self.format_alert_message(alert)
            print(message)
            return alert
        return None
    
    def save_alert_log(self, alert, filename='thndr_alerts.log'):
        """Save alert to log file for tracking"""
        if not alert:
            return
        
        message = self.format_alert_message(alert)
        
        try:
            with open(filename, 'a') as f:
                f.write(message)
                f.write("\n\n")
            print(f"✓ Alert logged to {filename}")
        except Exception as e:
            print(f"Error saving alert: {e}")


def run_alert_service(cairo_ticker, london_ticker, check_interval=300, threshold=1.0,
                      commission_pct=0.10, bid_ask_spread=0.08, slippage_pct=0.15, 
                      execution_delay_pct=0.20):
    """
    Run continuous monitoring service with Thndr-specific costs
    
    Args:
        cairo_ticker: Cairo stock ticker (e.g., 'COMI.CA')
        london_ticker: London GDR ticker (e.g., 'CBKD.L')
        check_interval: Check interval in seconds (300 = 5 min)
        threshold: Signal threshold in % (default 1%)
        commission_pct: Thndr commission rate
        bid_ask_spread: Thndr bid-ask spread
        slippage_pct: Slippage from execution delay
        execution_delay_pct: Impact of 1-min delay
    """
    import time
    
    alerts = ThndrTradingAlerts(
        cairo_ticker, london_ticker,
        commission_pct=commission_pct,
        bid_ask_spread=bid_ask_spread,
        slippage_pct=slippage_pct,
        execution_delay_pct=execution_delay_pct
    )
    
    print(f"\n{'='*70}")
    print(f"🤖 THNDR TRADING ALERT SERVICE STARTED")
    print(f"{'='*70}")
    print(f"Monitoring: {cairo_ticker} (Cairo) vs {london_ticker} (London)")
    print(f"Signal Threshold: {threshold}%")
    print(f"Check Interval: {check_interval}s")
    print(f"\nThndr Cost Structure:")
    print(f"  Commission: {commission_pct}%")
    print(f"  Bid-Ask Spread: {bid_ask_spread}%")
    print(f"  Slippage (1-min delay): {slippage_pct}%")
    print(f"  Execution Delay: {execution_delay_pct}%")
    print(f"  Total Drag: {commission_pct + bid_ask_spread + slippage_pct + execution_delay_pct}%")
    print(f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Press Ctrl+C to stop\n")
    
    signal_count = 0
    
    try:
        while True:
            signal, london_move, cairo_prices = alerts.check_signal(threshold)
            
            if signal and signal['has_signal']:
                signal_count += 1
                print(f"\n[Signal #{signal_count}] 🚨 ALERT GENERATED: {datetime.now().strftime('%H:%M:%S')}")
                print(f"London Move: {london_move:+.2f}%")
                
                alert = alerts.print_alert(signal)
                alerts.save_alert_log(alert)
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print(f"\n\n{'='*70}")
        print(f"🛑 ALERT SERVICE STOPPED")
        print(f"Total Signals Generated: {signal_count}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")


if __name__ == "__main__":
    # Example usage
    print("\n🔧 Thndr Trading Alerts Module")
    print("Use in your code:\n")
    print("  from thndr_alerts import ThndrTradingAlerts, run_alert_service")
    print("\n  # Check for signal once")
    print("  alerts = ThndrTradingAlerts('COMI.CA', 'CBKD.L')")
    print("  signal, _, _ = alerts.check_signal(threshold=1.0)")
    print("  alerts.print_alert(signal)")
    print("\n  # Or run continuous monitoring")
    print("  run_alert_service('COMI.CA', 'CBKD.L', check_interval=300)")
