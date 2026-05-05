#!/usr/bin/env python3
"""
THNDR POSITION TRACKER
======================

Manages concurrent buy/sell positions:
- Track open positions waiting for sell
- Enforce position limits (single vs concurrent)
- Calculate aggregate P&L across all positions
- Alert when it's time to sell each position
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import yfinance as yf

class PositionTracker:
    """Track open positions and manage concurrent trades"""
    
    def __init__(self, max_concurrent_positions=1, positions_file='positions.json'):
        """
        Initialize position tracker
        
        Args:
            max_concurrent_positions: Max open buys at same time (1 = no concurrent)
            positions_file: JSON file to persist positions
        """
        self.max_concurrent_positions = max_concurrent_positions
        self.positions_file = positions_file
        self.positions = self._load_positions()
    
    def _load_positions(self):
        """Load positions from JSON file"""
        if Path(self.positions_file).exists():
            try:
                with open(self.positions_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_positions(self):
        """Save positions to JSON file"""
        with open(self.positions_file, 'w') as f:
            json.dump(self.positions, f, indent=2)
    
    def can_buy(self):
        """Check if we can place a new buy order"""
        open_buys = [p for p in self.positions if p['status'] == 'OPEN']
        return len(open_buys) < self.max_concurrent_positions
    
    def add_position(self, ticker, entry_price, entry_date, shares=100, 
                   sell_strategy='time', sell_target=None):
        """
        Record a new BUY position
        
        Args:
            ticker: Stock ticker (e.g., 'COMI.CA')
            entry_price: Actual price paid
            entry_date: Date/time of entry
            shares: Number of shares
            sell_strategy: 'time' (4-hour) or 'limit' (price-based)
            sell_target: Target sell price (if limited)
        
        Returns: Position ID
        """
        if not self.can_buy():
            return None, f"Cannot buy: {len([p for p in self.positions if p['status'] == 'OPEN'])} positions already open"
        
        position = {
            'id': len(self.positions) + 1,
            'ticker': ticker,
            'entry_price': entry_price,
            'entry_date': entry_date,
            'shares': shares,
            'status': 'OPEN',  # OPEN, SOLD, CLOSED
            'sell_strategy': sell_strategy,
            'sell_target': sell_target,
            'exit_price': None,
            'exit_date': None,
            'pnl_dollar': None,
            'pnl_percent': None
        }
        
        self.positions.append(position)
        self._save_positions()
        
        return position['id'], "✓ Position recorded"
    
    def sell_position(self, position_id, exit_price, exit_date):
        """
        Record a SELL for an open position
        
        Args:
            position_id: ID of position to sell
            exit_price: Actual price received
            exit_date: Date/time of exit
        """
        for pos in self.positions:
            if pos['id'] == position_id and pos['status'] == 'OPEN':
                pos['exit_price'] = exit_price
                pos['exit_date'] = exit_date
                pos['status'] = 'SOLD'
                
                # Calculate P&L
                pnl_dollar = (exit_price - pos['entry_price']) * pos['shares']
                pnl_percent = ((exit_price - pos['entry_price']) / pos['entry_price']) * 100
                
                pos['pnl_dollar'] = pnl_dollar
                pos['pnl_percent'] = pnl_percent
                
                self._save_positions()
                return pos
        
        return None
    
    def get_open_positions(self):
        """Get all open (not yet sold) positions"""
        return [p for p in self.positions if p['status'] == 'OPEN']
    
    def get_positions_to_sell(self, strategy='time'):
        """
        Get positions that should be sold now
        
        Args:
            strategy: 'time' = held 4+ hours, 'limit' = price target reached
        """
        open_pos = self.get_open_positions()
        to_sell = []
        
        if strategy == 'time':
            # Check which positions held 4+ hours
            for pos in open_pos:
                entry = datetime.fromisoformat(pos['entry_date'])
                elapsed = datetime.now() - entry
                if elapsed >= timedelta(hours=4):
                    to_sell.append(pos)
        
        elif strategy == 'limit':
            # Check price targets (would need live price data)
            for pos in open_pos:
                if pos['sell_strategy'] == 'limit' and pos['sell_target']:
                    # Get current price
                    try:
                        curr = yf.download(pos['ticker'], period='1d', progress=False)
                        current_price = curr.iloc[-1]['Close']
                        if current_price >= pos['sell_target']:
                            to_sell.append(pos)
                    except:
                        pass
        
        return to_sell
    
    def get_aggregate_stats(self):
        """Calculate aggregate stats across all positions"""
        sold = [p for p in self.positions if p['status'] == 'SOLD']
        
        if not sold:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl_dollar': 0,
                'total_pnl_percent': 0,
                'avg_pnl_dollar': 0,
                'best_trade': 0,
                'worst_trade': 0
            }
        
        pnls = [p['pnl_dollar'] for p in sold]
        winners = sum(1 for p in sold if p['pnl_dollar'] > 0)
        
        return {
            'total_trades': len(sold),
            'winning_trades': winners,
            'losing_trades': len(sold) - winners,
            'win_rate': (winners / len(sold) * 100) if sold else 0,
            'total_pnl_dollar': sum(pnls),
            'avg_pnl_dollar': sum(pnls) / len(sold) if sold else 0,
            'best_trade': max(pnls),
            'worst_trade': min(pnls)
        }
    
    def print_status(self):
        """Print current position status"""
        open_pos = self.get_open_positions()
        sold = [p for p in self.positions if p['status'] == 'SOLD']
        stats = self.get_aggregate_stats()
        
        print("\n" + "="*80)
        print("POSITION TRACKER STATUS")
        print("="*80)
        
        print(f"\nOPEN POSITIONS: {len(open_pos)} / {self.max_concurrent_positions}")
        for pos in open_pos:
            entry = datetime.fromisoformat(pos['entry_date'])
            elapsed = datetime.now() - entry
            hours = elapsed.total_seconds() / 3600
            
            print(f"\n  ID#{pos['id']}: {pos['ticker']}")
            print(f"    Entry: ${pos['entry_price']:.2f} ({pos['shares']} shares)")
            print(f"    Entry Date: {pos['entry_date']}")
            print(f"    Held: {hours:.1f} hours")
            print(f"    Strategy: {pos['sell_strategy']}" + 
                  (f" @ ${pos['sell_target']:.2f}" if pos['sell_target'] else ""))
        
        print(f"\n\nCLOSED POSITIONS: {len(sold)}")
        if stats['total_trades'] > 0:
            print(f"  Total Trades: {stats['total_trades']}")
            print(f"  Winning: {stats['winning_trades']} | Losing: {stats['losing_trades']}")
            print(f"  Win Rate: {stats['win_rate']:.1f}%")
            print(f"  Total P&L: ${stats['total_pnl_dollar']:.2f}")
            print(f"  Avg P&L: ${stats['avg_pnl_dollar']:.2f}")
            print(f"  Best Trade: ${stats['best_trade']:.2f}")
            print(f"  Worst Trade: ${stats['worst_trade']:.2f}")
        
        print("\n" + "="*80)
    
    def get_positions_table(self):
        """Return positions as DataFrame for analysis"""
        return pd.DataFrame(self.positions)


def main():
    """Example usage"""
    tracker = PositionTracker(max_concurrent_positions=3)  # Allow up to 3 concurrent buys
    
    print("POSITION TRACKER EXAMPLE")
    print("="*80)
    
    # Check if we can buy
    if tracker.can_buy():
        print("✓ Can place a new BUY order\n")
        
        # Record a buy
        pos_id, msg = tracker.add_position(
            ticker='COMI.CA',
            entry_price=24.50,
            entry_date=datetime.now().isoformat(),
            shares=100,
            sell_strategy='time'
        )
        print(f"{msg}: Position ID#{pos_id}\n")
    
    # Print status
    tracker.print_status()
    
    print("\n\nUsage in your code:")
    print("-" * 80)
    print("""
from position_tracker import PositionTracker

# Create tracker (max 1 concurrent = no overlapping trades)
tracker = PositionTracker(max_concurrent_positions=1)

# Can we buy?
if tracker.can_buy():
    pos_id, msg = tracker.add_position(
        ticker='COMI.CA',
        entry_price=24.50,
        entry_date=datetime.now().isoformat(),
        sell_strategy='time'
    )
    print(f"New position: {pos_id}")

# Later: Check if we should sell (4+ hours held)
to_sell = tracker.get_positions_to_sell(strategy='time')
for pos in to_sell:
    print(f"Time to sell position #{pos['id']}")

# When sold
tracker.sell_position(pos_id, exit_price=24.75, exit_date=datetime.now().isoformat())

# See overall performance
stats = tracker.get_aggregate_stats()
print(f"Win rate: {stats['win_rate']:.1f}%")
print(f"Total P&L: ${stats['total_pnl_dollar']:.2f}")
    """)


if __name__ == '__main__':
    main()
