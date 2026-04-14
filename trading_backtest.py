"""
CIB Arbitrage Script: Cairo (COMI.CA) vs London (CBKD.L) GDR Arbitrage
Handles Sun-Thu vs Mon-Fri market calendar mismatch with smart forward fill.
Calculates Weekend Lead correlation with Sunday Open Gap for trading signals.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class TradingBacktester:
    """
    Dual-market arbitrage analyzer for CIB GDR pairs.
    Cairo: COMI.CA (Sun-Thu trading)
    London: CBKD.L (Mon-Fri trading)
    """
    
    def __init__(self, cairo_ticker, london_ticker, start_date, end_date):
        """
        Initialize the arbitrage analyzer
        
        Args:
            cairo_ticker (str): Cairo stock ticker (e.g., 'COMI.CA')
            london_ticker (str): London GDR ticker (e.g., 'CBKD.L')
            start_date (str): Start date in format 'YYYY-MM-DD'
            end_date (str): End date in format 'YYYY-MM-DD'
        """
        self.cairo_ticker = cairo_ticker
        self.london_ticker = london_ticker
        self.start_date = start_date
        self.end_date = end_date
        
        self.cairo_data = None
        self.london_data = None
        self.unified_df = None
        self.signals = None
        self.backtest_results = None
        
    def fetch_data(self):
        """Fetch historical price data for both markets"""
        print(f"Fetching Cairo data ({self.cairo_ticker})...")
        try:
            self.cairo_data = yf.download(
                self.cairo_ticker,
                start=self.start_date,
                end=self.end_date,
                progress=False
            )
            if self.cairo_data.empty:
                print(f"Warning: No data found for {self.cairo_ticker}")
                return False
            print(f"✓ Fetched {len(self.cairo_data)} days of Cairo data")
        except Exception as e:
            print(f"Error fetching Cairo data: {e}")
            return False
        
        print(f"Fetching London data ({self.london_ticker})...")
        try:
            self.london_data = yf.download(
                self.london_ticker,
                start=self.start_date,
                end=self.end_date,
                progress=False
            )
            if self.london_data.empty:
                print(f"Warning: No data found for {self.london_ticker}")
                return False
            print(f"✓ Fetched {len(self.london_data)} days of London data")
        except Exception as e:
            print(f"Error fetching London data: {e}")
            return False
        
        return True
    
    def create_unified_calendar(self):
        """Create unified calendar spanning entire date range (Mon-Sun)"""
        # Create complete date range
        date_range = pd.date_range(
            start=self.start_date,
            end=self.end_date,
            freq='D'
        )
        
        # Initialize unified dataframe
        self.unified_df = pd.DataFrame(index=date_range)
        self.unified_df.index.name = 'Date'
        
        # Add Cairo data (Sun-Thu trading)
        cairo_close = self.cairo_data[['Close']].copy()
        cairo_close.columns = ['Cairo_Close']
        cairo_open = self.cairo_data[['Open']].copy()
        cairo_open.columns = ['Cairo_Open']
        
        self.unified_df = self.unified_df.join(cairo_close, how='left')
        self.unified_df = self.unified_df.join(cairo_open, how='left')
        
        # Add London data (Mon-Fri trading)
        london_close = self.london_data[['Close']].copy()
        london_close.columns = ['London_Close']
        london_open = self.london_data[['Open']].copy()
        london_open.columns = ['London_Open']
        
        self.unified_df = self.unified_df.join(london_close, how='left')
        self.unified_df = self.unified_df.join(london_open, how='left')
        
        # Add day of week for reference
        self.unified_df['DayOfWeek'] = self.unified_df.index.day_name()
        
        print("\n" + "="*60)
        print("UNIFIED CALENDAR CREATED")
        print("="*60)
        print(f"Date range: {self.start_date} to {self.end_date}")
        print(f"Total trading days: {len(self.unified_df)}")
    
    def smart_forward_fill(self):
        """
        Fill missing prices using smart forward fill:
        - Friday's London price carries to Sat-Sun (limit=2)
        - Thursday's Cairo price carries to Friday (limit=1)
        """
        print("\nApplying smart forward fill logic...")
        
        # Forward fill London prices (Mon-Fri market) for weekend
        # Limit to 2 days to only cover Sat-Sun
        self.unified_df['London_Close'] = self.unified_df['London_Close'].ffill(limit=2)
        self.unified_df['London_Open'] = self.unified_df['London_Open'].ffill(limit=2)
        
        # Forward fill Cairo prices (Sun-Thu market) for Friday
        # Limit to 1 day to only cover Friday
        self.unified_df['Cairo_Close'] = self.unified_df['Cairo_Close'].ffill(limit=1)
        self.unified_df['Cairo_Open'] = self.unified_df['Cairo_Open'].ffill(limit=1)
        
        print("✓ Smart forward fill completed")
    
    def calculate_weekend_lead(self):
        """
        Calculate Weekend_Lead: Friday's London percentage move
        This captures how the London GDR performs on Friday (end of week)
        """
        # Calculate daily percentage change for London close
        self.unified_df['London_DailyReturn'] = (
            self.unified_df['London_Close'].pct_change() * 100
        )
        
        # Weekend Lead is the Friday London move
        # We'll use it to predict Sunday Cairo open gap
        self.unified_df['Weekend_Lead'] = self.unified_df['London_DailyReturn'].copy()
        
        # Mark which rows are Fridays
        self.unified_df['Is_Friday'] = self.unified_df['DayOfWeek'] == 'Friday'
        
        print("✓ Weekend_Lead calculated")
    
    def calculate_sunday_open_gap(self):
        """
        Calculate Sunday_Open_Gap: % difference between Cairo Sunday Open and Thursday Close
        This is the gap we're trying to exploit
        """
        # Get Thursday Close
        self.unified_df['Thursday_Close'] = np.nan
        for i in range(len(self.unified_df)):
            if self.unified_df.iloc[i]['DayOfWeek'] == 'Sunday' and i >= 3:
                # Find the Thursday before this Sunday (3 days back)
                # Sunday is index i, Thursday should be at i-3
                thursday_idx = i - 3
                if thursday_idx >= 0 and self.unified_df.iloc[thursday_idx]['DayOfWeek'] == 'Thursday':
                    self.unified_df.loc[self.unified_df.index[i], 'Thursday_Close'] = (
                        self.unified_df.iloc[thursday_idx]['Cairo_Close']
                    )
        
        # Calculate Sunday Open Gap
        self.unified_df['Sunday_Open_Gap'] = (
            (self.unified_df['Cairo_Open'] - self.unified_df['Thursday_Close']) / 
            self.unified_df['Thursday_Close'] * 100
        )
        
        # Mark which rows are Sundays
        self.unified_df['Is_Sunday'] = self.unified_df['DayOfWeek'] == 'Sunday'
        
        print("✓ Sunday_Open_Gap calculated")
    
    def calculate_correlation(self):
        """Calculate correlation between Weekend_Lead and Sunday_Open_Gap"""
        # Get valid data points (Sundays with both values)
        valid_mask = (
            self.unified_df['Is_Sunday'] & 
            self.unified_df['Weekend_Lead'].notna() & 
            self.unified_df['Sunday_Open_Gap'].notna()
        )
        
        if valid_mask.sum() < 2:
            print("⚠ Insufficient data for correlation")
            return 0
        
        valid_data = self.unified_df[valid_mask]
        
        correlation = valid_data['Weekend_Lead'].corr(valid_data['Sunday_Open_Gap'])
        
        print("\n" + "="*60)
        print("STATISTICAL CORRELATION ANALYSIS")
        print("="*60)
        print(f"Weekend_Lead (Friday London Move) vs Sunday_Open_Gap (Cairo Gap)")
        print(f"Correlation Coefficient: {correlation:.4f}")
        print(f"Sample size: {len(valid_data)} Sundays")
        
        if len(valid_data) > 0:
            print(f"Mean Weekend_Lead: {valid_data['Weekend_Lead'].mean():.4f}%")
            print(f"Mean Sunday_Open_Gap: {valid_data['Sunday_Open_Gap'].mean():.4f}%")
        
        return correlation
    
    def generate_trading_signals(self, london_move_threshold=1.0):
        """
        Generate trading signals:
        "If Friday London Move > threshold%, Buy Cairo at Sunday Open and Sell at Sunday Close"
        
        Args:
            london_move_threshold (float): Percentage threshold for Friday London move
        """
        self.unified_df['Signal'] = 0
        self.unified_df['Trade_Type'] = 'None'
        self.unified_df['Cairo_Sunday_Close'] = np.nan
        
        # Find Sundays with preceding Friday London move > threshold
        for i in range(len(self.unified_df)):
            if self.unified_df.iloc[i]['DayOfWeek'] == 'Sunday' and i >= 3:
                # Friday is 2 days before Sunday
                friday_idx = i - 2
                if (friday_idx >= 0 and 
                    self.unified_df.iloc[friday_idx]['DayOfWeek'] == 'Friday'):
                    
                    friday_move = self.unified_df.iloc[friday_idx]['London_DailyReturn']
                    
                    if pd.notna(friday_move) and friday_move > london_move_threshold:
                        # Buy signal on Sunday
                        self.unified_df.loc[self.unified_df.index[i], 'Signal'] = 1
                        self.unified_df.loc[self.unified_df.index[i], 'Trade_Type'] = 'BUY'
        
        # For each buy signal, find the sell (Sunday Close)
        for i in range(len(self.unified_df)):
            if self.unified_df.iloc[i]['Signal'] == 1:
                # Cairo_Close on Sunday is the exit price
                self.unified_df.loc[self.unified_df.index[i], 'Cairo_Sunday_Close'] = (
                    self.unified_df.iloc[i]['Cairo_Close']
                )
        
        print(f"\n✓ Trading signals generated (threshold: {london_move_threshold}%)")
    
    def backtest_arbitrage(self, initial_capital=10000):
        """
        Run backtest: Buy Cairo at Sunday Open, Sell at Sunday Close
        
        Args:
            initial_capital (float): Starting capital
        """
        self.backtest_results = {
            'trades': [],
            'portfolio_value': initial_capital,
            'total_pnl': 0,
            'winning_trades': 0,
            'losing_trades': 0
        }
        
        for i in range(len(self.unified_df)):
            if self.unified_df.iloc[i]['Signal'] == 1:
                sunday_open = self.unified_df.iloc[i]['Cairo_Open']
                sunday_close = self.unified_df.iloc[i]['Cairo_Close']
                
                if pd.notna(sunday_open) and pd.notna(sunday_close):
                    pnl_pct = ((sunday_close - sunday_open) / sunday_open) * 100
                    pnl_dollars = initial_capital * (pnl_pct / 100)
                    
                    trade_date = self.unified_df.index[i].strftime('%Y-%m-%d')
                    
                    self.backtest_results['trades'].append({
                        'Date': trade_date,
                        'Cairo_Open': sunday_open,
                        'Cairo_Close': sunday_close,
                        'PnL%': pnl_pct,
                        'PnL$': pnl_dollars
                    })
                    
                    self.backtest_results['total_pnl'] += pnl_dollars
                    
                    if pnl_pct > 0:
                        self.backtest_results['winning_trades'] += 1
                    else:
                        self.backtest_results['losing_trades'] += 1
        
        self.backtest_results['portfolio_value'] = initial_capital + self.backtest_results['total_pnl']
    
    def print_backtest_results(self):
        """Print comprehensive backtest results"""
        if not self.backtest_results or not self.backtest_results['trades']:
            print("\n⚠ No trades executed during backtest period")
            return
        
        trades_df = pd.DataFrame(self.backtest_results['trades'])
        
        print("\n" + "="*60)
        print("ARBITRAGE BACKTEST RESULTS")
        print("="*60)
        print(f"Total Trades: {len(trades_df)}")
        print(f"Winning Trades: {self.backtest_results['winning_trades']}")
        print(f"Losing Trades: {self.backtest_results['losing_trades']}")
        
        if len(trades_df) > 0:
            win_rate = (self.backtest_results['winning_trades'] / len(trades_df)) * 100
            print(f"Win Rate: {win_rate:.2f}%")
            print(f"\nAverage PnL per Trade: ${trades_df['PnL$'].mean():.2f}")
            print(f"Max PnL: ${trades_df['PnL$'].max():.2f}")
            print(f"Min PnL: ${trades_df['PnL$'].min():.2f}")
            print(f"\nTotal P&L: ${self.backtest_results['total_pnl']:.2f}")
            print(f"Initial Capital: $10,000")
            print(f"Final Portfolio Value: ${self.backtest_results['portfolio_value']:.2f}")
            print(f"Return: {(self.backtest_results['total_pnl']/10000)*100:.2f}%")
            
            print("\n" + "-"*60)
            print("Individual Trades:")
            print("-"*60)
            for idx, trade in enumerate(self.backtest_results['trades'][:10], 1):
                print(f"{idx}. {trade['Date']} | "
                      f"Open: {trade['Cairo_Open']:.2f} | "
                      f"Close: {trade['Cairo_Close']:.2f} | "
                      f"PnL: {trade['PnL%']:.2f}% (${trade['PnL$']:.2f})")
            
            if len(self.backtest_results['trades']) > 10:
                print(f"... and {len(self.backtest_results['trades']) - 10} more trades")
        
        print("="*60)
    
    def plot_results(self, filename=None):
        """Plot arbitrage analysis results"""
        fig, axes = plt.subplots(3, 1, figsize=(14, 12))
        
        # Plot 1: Both markets aligned
        valid_data = self.unified_df.dropna(subset=['Cairo_Close', 'London_Close'])
        
        ax1 = axes[0]
        ax1_twin = ax1.twinx()
        
        ax1.plot(valid_data.index, valid_data['Cairo_Close'], 
                label='Cairo Close', color='blue', linewidth=2)
        ax1_twin.plot(valid_data.index, valid_data['London_Close'], 
                     label='London Close', color='red', linewidth=2, alpha=0.7)
        
        ax1.set_ylabel('Cairo Price (EGP)', color='blue')
        ax1_twin.set_ylabel('London Price (GBP)', color='red')
        ax1.set_title('CIB: Cairo vs London - Unified Calendar View', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        ax1_twin.legend(loc='upper right')
        
        # Plot 2: Weekend Lead vs Sunday Gap (if data available)
        ax2 = axes[1]
        friday_data = self.unified_df[self.unified_df['Is_Friday']].dropna(subset=['Weekend_Lead'])
        sunday_data = self.unified_df[self.unified_df['Is_Sunday']].dropna(subset=['Sunday_Open_Gap'])
        
        if len(friday_data) > 0:
            ax2.scatter(friday_data.index, friday_data['Weekend_Lead'], 
                       label='Friday London Move', color='green', s=50, alpha=0.6)
        if len(sunday_data) > 0:
            ax2.scatter(sunday_data.index, sunday_data['Sunday_Open_Gap'], 
                       label='Sunday Cairo Gap', color='orange', s=50, alpha=0.6)
        
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.3)
        ax2.set_ylabel('% Change')
        ax2.set_title('Weekend Lead vs Sunday Open Gap', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Trade signals and P&L
        ax3 = axes[2]
        
        if self.backtest_results and self.backtest_results['trades']:
            trades_df = pd.DataFrame(self.backtest_results['trades'])
            trades_df['Date'] = pd.to_datetime(trades_df['Date'])
            
            colors = ['green' if pnl > 0 else 'red' for pnl in trades_df['PnL$']]
            ax3.bar(trades_df['Date'], trades_df['PnL$'], color=colors, alpha=0.7)
            ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax3.set_ylabel('P&L ($)')
            ax3.set_title(f'Trading Signal P&L (Buy Sunday Open, Sell Sunday Close)', fontweight='bold')
            ax3.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=100, bbox_inches='tight')
            print(f"✓ Plot saved to {filename}")
        
        plt.show()
    
    def run(self):
        """Run complete arbitrage analysis"""
        if not self.fetch_data():
            return False
        
        self.create_unified_calendar()
        self.smart_forward_fill()
        self.calculate_weekend_lead()
        self.calculate_sunday_open_gap()
        
        correlation = self.calculate_correlation()
        
        self.generate_trading_signals(london_move_threshold=1.0)
        self.backtest_arbitrage()
        self.print_backtest_results()
        
        return True


def main():
    """Main execution - CIB Arbitrage Analysis"""
    print("\n" + "="*60)
    print("CIB ARBITRAGE ANALYSIS: CAIRO vs LONDON")
    print("="*60)
    
    # Configuration
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)  # 1 year of data
    
    # CIB Tickers - primary pair
    cairo_ticker_primary = 'COMI.CA'    # Cairo Clinic, Cairo Exchange
    london_ticker_primary = 'CBKD.L'    # CIB, London Stock Exchange (GDR)
    
    # Alternative ticker pairs to try if above don't work
    alt_pairs = [
        ('COMI.CA', 'CBKD.L'),
        ('CIB.CA', 'CIB.L'),
        ('AAPL', 'ASML'),  # Fallback for testing
    ]
    
    analyzer = None
    for attempt, (cairo_tick, london_tick) in enumerate(alt_pairs):
        print(f"\nAttempt {attempt + 1}: Testing {cairo_tick} vs {london_tick}")
        print(f"Date range: {start_date} to {end_date}\n")
        
        analyzer = TradingBacktester(
            cairo_ticker=cairo_tick,
            london_ticker=london_tick,
            start_date=str(start_date),
            end_date=str(end_date)
        )
        
        try:
            if analyzer.run():
                # Successfully ran
                analyzer.plot_results(
                    filename=f'cib_arbitrage_{cairo_tick.replace(".","_")}_vs_{london_tick.replace(".","_")}.png'
                )
                break
        except Exception as e:
            print(f"Error with {cairo_tick} vs {london_tick}: {e}\n")
            analyzer = None


if __name__ == "__main__":
    main()
