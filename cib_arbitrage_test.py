"""
CIB Arbitrage Script: Cairo vs London GDR Arbitrage
Quick test version without plotting
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class CIBArbitrageAnalyzer:
    """Dual-market arbitrage analyzer for CIB GDR pairs."""
    
    def __init__(self, cairo_ticker, london_ticker, start_date, end_date):
        self.cairo_ticker = cairo_ticker
        self.london_ticker = london_ticker
        self.start_date = start_date
        self.end_date = end_date
        
        self.cairo_data = None
        self.london_data = None
        self.unified_df = None
        self.backtest_results = None
        self.correlation = None
        
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
        date_range = pd.date_range(
            start=self.start_date,
            end=self.end_date,
            freq='D'
        )
        
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
        print(f"Total days: {len(self.unified_df)}")
    
    def smart_forward_fill(self):
        """
        Fill missing prices using smart forward fill:
        - Friday's London price carries to Sat-Sun (limit=2)
        - Thursday's Cairo price carries to Friday (limit=1)
        """
        print("\nApplying smart forward fill logic...")
        
        # Forward fill London prices (Mon-Fri market) for weekend
        self.unified_df['London_Close'] = self.unified_df['London_Close'].ffill(limit=2)
        self.unified_df['London_Open'] = self.unified_df['London_Open'].ffill(limit=2)
        
        # Forward fill Cairo prices (Sun-Thu market) for Friday
        self.unified_df['Cairo_Close'] = self.unified_df['Cairo_Close'].ffill(limit=1)
        self.unified_df['Cairo_Open'] = self.unified_df['Cairo_Open'].ffill(limit=1)
        
        print("✓ Smart forward fill completed")
    
    def calculate_weekend_lead(self):
        """Calculate daily London moves for all trading days"""
        # Calculate daily percentage change for London close
        self.unified_df['London_DailyReturn'] = (
            self.unified_df['London_Close'].pct_change() * 100
        )
        
        # Mark day of week
        self.unified_df['Is_Monday'] = self.unified_df['DayOfWeek'] == 'Monday'
        self.unified_df['Is_Tuesday'] = self.unified_df['DayOfWeek'] == 'Tuesday'
        self.unified_df['Is_Wednesday'] = self.unified_df['DayOfWeek'] == 'Wednesday'
        self.unified_df['Is_Thursday'] = self.unified_df['DayOfWeek'] == 'Thursday'
        self.unified_df['Is_Friday'] = self.unified_df['DayOfWeek'] == 'Friday'
        
        print("✓ Daily London returns calculated")
    
    def calculate_sunday_open_gap(self):
        """Calculate Cairo opening gaps for all trading days after London signal"""
        # Tuesday gap: Monday London close → Tuesday Cairo open
        self.unified_df['Monday_Close_for_Tuesday'] = np.nan
        self.unified_df['Tuesday_Open_Gap'] = np.nan
        
        for i in range(len(self.unified_df)):
            if self.unified_df.iloc[i]['DayOfWeek'] == 'Tuesday' and i >= 1:
                monday_idx = i - 1
                if self.unified_df.iloc[monday_idx]['DayOfWeek'] == 'Monday':
                    self.unified_df.loc[self.unified_df.index[i], 'Monday_Close_for_Tuesday'] = (
                        self.unified_df.iloc[monday_idx]['Cairo_Close']
                    )
                    self.unified_df.loc[self.unified_df.index[i], 'Tuesday_Open_Gap'] = (
                        (self.unified_df.iloc[i]['Cairo_Open'] - self.unified_df.iloc[monday_idx]['Cairo_Close']) /
                        self.unified_df.iloc[monday_idx]['Cairo_Close'] * 100
                    )
        
        # Wednesday gap: Tuesday London close → Wednesday Cairo open
        self.unified_df['Tuesday_Close_for_Wednesday'] = np.nan
        self.unified_df['Wednesday_Open_Gap'] = np.nan
        
        for i in range(len(self.unified_df)):
            if self.unified_df.iloc[i]['DayOfWeek'] == 'Wednesday' and i >= 1:
                tuesday_idx = i - 1
                if self.unified_df.iloc[tuesday_idx]['DayOfWeek'] == 'Tuesday':
                    self.unified_df.loc[self.unified_df.index[i], 'Tuesday_Close_for_Wednesday'] = (
                        self.unified_df.iloc[tuesday_idx]['Cairo_Close']
                    )
                    self.unified_df.loc[self.unified_df.index[i], 'Wednesday_Open_Gap'] = (
                        (self.unified_df.iloc[i]['Cairo_Open'] - self.unified_df.iloc[tuesday_idx]['Cairo_Close']) /
                        self.unified_df.iloc[tuesday_idx]['Cairo_Close'] * 100
                    )
        
        # Thursday gap: Wednesday London close → Thursday Cairo open
        self.unified_df['Wednesday_Close_for_Thursday'] = np.nan
        self.unified_df['Thursday_Open_Gap'] = np.nan
        
        for i in range(len(self.unified_df)):
            if self.unified_df.iloc[i]['DayOfWeek'] == 'Thursday' and i >= 1:
                wednesday_idx = i - 1
                if self.unified_df.iloc[wednesday_idx]['DayOfWeek'] == 'Wednesday':
                    self.unified_df.loc[self.unified_df.index[i], 'Wednesday_Close_for_Thursday'] = (
                        self.unified_df.iloc[wednesday_idx]['Cairo_Close']
                    )
                    self.unified_df.loc[self.unified_df.index[i], 'Thursday_Open_Gap'] = (
                        (self.unified_df.iloc[i]['Cairo_Open'] - self.unified_df.iloc[wednesday_idx]['Cairo_Close']) /
                        self.unified_df.iloc[wednesday_idx]['Cairo_Close'] * 100
                    )
        
        # Sunday gap: Friday London close → Sunday Cairo open (existing)
        self.unified_df['Thursday_Close'] = np.nan
        self.unified_df['Sunday_Open_Gap'] = np.nan
        
        for i in range(len(self.unified_df)):
            if self.unified_df.iloc[i]['DayOfWeek'] == 'Sunday' and i >= 3:
                thursday_idx = i - 3
                if thursday_idx >= 0 and self.unified_df.iloc[thursday_idx]['DayOfWeek'] == 'Thursday':
                    self.unified_df.loc[self.unified_df.index[i], 'Thursday_Close'] = (
                        self.unified_df.iloc[thursday_idx]['Cairo_Close']
                    )
                    self.unified_df.loc[self.unified_df.index[i], 'Sunday_Open_Gap'] = (
                        (self.unified_df.iloc[i]['Cairo_Open'] - self.unified_df.iloc[thursday_idx]['Cairo_Close']) / 
                        self.unified_df.iloc[thursday_idx]['Cairo_Close'] * 100
                    )
        
        self.unified_df['Is_Sunday'] = self.unified_df['DayOfWeek'] == 'Sunday'
        
        print("✓ All Cairo opening gaps calculated (Tue, Wed, Thu, Sun)")
    
    def calculate_correlation(self):
        """Calculate correlations between London moves and Cairo gaps for each day"""
        print("\n" + "="*60)
        print("CORRELATION ANALYSIS - ALL TRADING DAYS")
        print("="*60)
        
        correlations = {}
        
        # Tuesday: Monday London → Tuesday Cairo gap
        mon_valid_mask = (
            self.unified_df['Is_Tuesday'] & 
            self.unified_df['London_DailyReturn'].notna() & 
            self.unified_df['Tuesday_Open_Gap'].notna()
        )
        if mon_valid_mask.sum() >= 2:
            mon_data = self.unified_df[mon_valid_mask]
            mon_corr = mon_data['London_DailyReturn'].corr(mon_data['Tuesday_Open_Gap'])
            correlations['Monday→Tuesday'] = mon_corr
            print(f"\n📊 Monday → Tuesday Trade")
            print(f"   London Daily Return vs Cairo Tuesday Gap")
            print(f"   Correlation: {mon_corr:.4f} (n={len(mon_data)})")
        
        # Wednesday: Tuesday London → Wednesday Cairo gap
        tue_valid_mask = (
            self.unified_df['Is_Wednesday'] & 
            self.unified_df['London_DailyReturn'].notna() & 
            self.unified_df['Wednesday_Open_Gap'].notna()
        )
        if tue_valid_mask.sum() >= 2:
            tue_data = self.unified_df[tue_valid_mask]
            tue_corr = tue_data['London_DailyReturn'].corr(tue_data['Wednesday_Open_Gap'])
            correlations['Tuesday→Wednesday'] = tue_corr
            print(f"\n📊 Tuesday → Wednesday Trade")
            print(f"   London Daily Return vs Cairo Wednesday Gap")
            print(f"   Correlation: {tue_corr:.4f} (n={len(tue_data)})")
        
        # Thursday: Wednesday London → Thursday Cairo gap
        wed_valid_mask = (
            self.unified_df['Is_Thursday'] & 
            self.unified_df['London_DailyReturn'].notna() & 
            self.unified_df['Thursday_Open_Gap'].notna()
        )
        if wed_valid_mask.sum() >= 2:
            wed_data = self.unified_df[wed_valid_mask]
            wed_corr = wed_data['London_DailyReturn'].corr(wed_data['Thursday_Open_Gap'])
            correlations['Wednesday→Thursday'] = wed_corr
            print(f"\n📊 Wednesday → Thursday Trade")
            print(f"   London Daily Return vs Cairo Thursday Gap")
            print(f"   Correlation: {wed_corr:.4f} (n={len(wed_data)})")
        
        # Sunday: Friday London → Sunday Cairo gap
        fri_valid_mask = (
            self.unified_df['Is_Sunday'] & 
            self.unified_df['London_DailyReturn'].notna() & 
            self.unified_df['Sunday_Open_Gap'].notna()
        )
        if fri_valid_mask.sum() >= 2:
            fri_data = self.unified_df[fri_valid_mask]
            fri_corr = fri_data['London_DailyReturn'].corr(fri_data['Sunday_Open_Gap'])
            correlations['Friday→Sunday'] = fri_corr
            print(f"\n📊 Friday → Sunday Trade")
            print(f"   London Daily Return vs Cairo Sunday Gap")
            print(f"   Correlation: {fri_corr:.4f} (n={len(fri_data)})")
        
        # Average correlation
        if correlations:
            avg_corr = np.mean(list(correlations.values()))
            print(f"\n📈 AVERAGE CORRELATION: {avg_corr:.4f}")
        
        self.correlation = correlations
        print("="*60)
        
        return self.correlation
    
    def generate_trading_signals(self, london_move_threshold=1.0):
        """
        Generate trading signals for all overlapping days:
        "If Monday London Move > threshold%, Buy Cairo at Tuesday Open and Sell at Tuesday Close"
        "If Tuesday London Move > threshold%, Buy Cairo at Wednesday Open and Sell at Wednesday Close"
        "If Wednesday London Move > threshold%, Buy Cairo at Thursday Open and Sell at Thursday Close"
        "If Friday London Move > threshold%, Buy Cairo at Sunday Open and Sell at Sunday Close"
        """
        self.unified_df['Signal'] = 0
        self.unified_df['Trade_Type'] = 'None'
        self.unified_df['Signal_Source'] = ''
        
        for i in range(len(self.unified_df)):
            current_day = self.unified_df.iloc[i]['DayOfWeek']
            
            # Tuesday trades (from Monday signal)
            if current_day == 'Tuesday' and i >= 1:
                monday_idx = i - 1
                if self.unified_df.iloc[monday_idx]['DayOfWeek'] == 'Monday':
                    monday_move = self.unified_df.iloc[monday_idx]['London_DailyReturn']
                    if pd.notna(monday_move) and monday_move > london_move_threshold:
                        self.unified_df.loc[self.unified_df.index[i], 'Signal'] = 1
                        self.unified_df.loc[self.unified_df.index[i], 'Trade_Type'] = 'BUY'
                        self.unified_df.loc[self.unified_df.index[i], 'Signal_Source'] = 'Monday'
            
            # Wednesday trades (from Tuesday signal)
            elif current_day == 'Wednesday' and i >= 1:
                tuesday_idx = i - 1
                if self.unified_df.iloc[tuesday_idx]['DayOfWeek'] == 'Tuesday':
                    tuesday_move = self.unified_df.iloc[tuesday_idx]['London_DailyReturn']
                    if pd.notna(tuesday_move) and tuesday_move > london_move_threshold:
                        self.unified_df.loc[self.unified_df.index[i], 'Signal'] = 1
                        self.unified_df.loc[self.unified_df.index[i], 'Trade_Type'] = 'BUY'
                        self.unified_df.loc[self.unified_df.index[i], 'Signal_Source'] = 'Tuesday'
            
            # Thursday trades (from Wednesday signal)
            elif current_day == 'Thursday' and i >= 1:
                wednesday_idx = i - 1
                if self.unified_df.iloc[wednesday_idx]['DayOfWeek'] == 'Wednesday':
                    wednesday_move = self.unified_df.iloc[wednesday_idx]['London_DailyReturn']
                    if pd.notna(wednesday_move) and wednesday_move > london_move_threshold:
                        self.unified_df.loc[self.unified_df.index[i], 'Signal'] = 1
                        self.unified_df.loc[self.unified_df.index[i], 'Trade_Type'] = 'BUY'
                        self.unified_df.loc[self.unified_df.index[i], 'Signal_Source'] = 'Wednesday'
            
            # Sunday trades (from Friday signal)
            elif current_day == 'Sunday' and i >= 2:
                friday_idx = i - 2
                if friday_idx >= 0 and self.unified_df.iloc[friday_idx]['DayOfWeek'] == 'Friday':
                    friday_move = self.unified_df.iloc[friday_idx]['London_DailyReturn']
                    if pd.notna(friday_move) and friday_move > london_move_threshold:
                        self.unified_df.loc[self.unified_df.index[i], 'Signal'] = 1
                        self.unified_df.loc[self.unified_df.index[i], 'Trade_Type'] = 'BUY'
                        self.unified_df.loc[self.unified_df.index[i], 'Signal_Source'] = 'Friday'
        
        signal_count = (self.unified_df['Signal'] == 1).sum()
        print(f"\n✓ Trading signals generated (threshold: {london_move_threshold}%)")
        print(f"  Total signals: {signal_count} trades")
    
    def backtest_arbitrage(self, initial_capital=10000, 
                          slippage_pct=0.1, bid_ask_spread=0.05, 
                          commission_pct=0.1, execution_delay_pct=0.0,
                          realistic_mode=True):
        """
        Run backtest: Buy Cairo at Open (Tue, Wed, Thu, or Sun), Sell at Close
        
        Args:
            initial_capital: Capital per trade
            slippage_pct: Slippage cost as % (default 0.1%)
            bid_ask_spread: Bid-ask spread as % (default 0.05%)
            commission_pct: Commission on buy+sell as % (default 0.1%)
            execution_delay_pct: Price movement while order fills (default 0%)
            realistic_mode: If True, apply all costs; if False, perfect execution
        """
        self.backtest_results = {
            'trades': [],
            'total_pnl': 0,
            'total_pnl_ideal': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_costs': 0,
            'simulation_params': {
                'slippage_pct': slippage_pct,
                'bid_ask_spread': bid_ask_spread,
                'commission_pct': commission_pct,
                'execution_delay_pct': execution_delay_pct,
                'realistic_mode': realistic_mode
            }
        }
        
        for i in range(len(self.unified_df)):
            if self.unified_df.iloc[i]['Signal'] == 1:
                cairo_open_ideal = self.unified_df.iloc[i]['Cairo_Open']
                cairo_close_ideal = self.unified_df.iloc[i]['Cairo_Close']
                signal_source = self.unified_df.iloc[i]['Signal_Source']
                
                if pd.notna(cairo_open_ideal) and pd.notna(cairo_close_ideal):
                    trade_date = self.unified_df.index[i].strftime('%Y-%m-%d')
                    
                    if realistic_mode:
                        # ENTRY COSTS
                        bid_ask_entry = (cairo_open_ideal * bid_ask_spread / 100) / 2
                        delay_entry = cairo_open_ideal * execution_delay_pct / 100
                        slippage_entry = cairo_open_ideal * slippage_pct / 100
                        
                        # Actual entry price (worse for us)
                        cairo_buy_price = cairo_open_ideal + bid_ask_entry + delay_entry + slippage_entry
                        
                        # EXIT COSTS
                        bid_ask_exit = (cairo_close_ideal * bid_ask_spread / 100) / 2
                        delay_exit = cairo_close_ideal * execution_delay_pct / 100
                        slippage_exit = cairo_close_ideal * slippage_pct / 100
                        
                        # Actual exit price (worse for us on sell)
                        cairo_sell_price = cairo_close_ideal - bid_ask_exit - delay_exit - slippage_exit
                        
                        # COMMISSIONS
                        buy_commission = cairo_buy_price * commission_pct / 100
                        sell_commission = cairo_sell_price * commission_pct / 100
                        
                        # Total actual cost
                        total_costs = bid_ask_entry + delay_entry + slippage_entry + \
                                     bid_ask_exit + delay_exit + slippage_exit + \
                                     buy_commission + sell_commission
                        
                    else:
                        # Perfect execution (ideal scenario)
                        cairo_buy_price = cairo_open_ideal
                        cairo_sell_price = cairo_close_ideal
                        total_costs = 0
                    
                    # Calculate P&L
                    pnl_ideal = ((cairo_close_ideal - cairo_open_ideal) / cairo_open_ideal) * 100
                    pnl_realistic = ((cairo_sell_price - cairo_buy_price) / cairo_buy_price) * 100
                    
                    pnl_dollars_ideal = initial_capital * (pnl_ideal / 100)
                    pnl_dollars_realistic = initial_capital * (pnl_realistic / 100)
                    
                    self.backtest_results['trades'].append({
                        'Date': trade_date,
                        'Signal_Day': signal_source,
                        'Cairo_Open': cairo_open_ideal,
                        'Cairo_Close': cairo_close_ideal,
                        'Entry_Price': cairo_buy_price,
                        'Exit_Price': cairo_sell_price,
                        'PnL%_Ideal': pnl_ideal,
                        'PnL%': pnl_realistic,
                        'PnL$_Ideal': pnl_dollars_ideal,
                        'PnL$': pnl_dollars_realistic,
                        'Costs': total_costs,
                        'Realistic': realistic_mode
                    })
                    
                    self.backtest_results['total_pnl_ideal'] += pnl_dollars_ideal
                    self.backtest_results['total_pnl'] += pnl_dollars_realistic
                    self.backtest_results['total_costs'] += total_costs
                    
                    if pnl_realistic > 0:
                        self.backtest_results['winning_trades'] += 1
                    else:
                        self.backtest_results['losing_trades'] += 1
    
    def print_backtest_results(self):
        """Print comprehensive backtest results with daily breakdown"""
        if not self.backtest_results or not self.backtest_results['trades']:
            print("\n⚠ No trades executed during backtest period")
            return
        
        trades_df = pd.DataFrame(self.backtest_results['trades'])
        realistic = self.backtest_results['simulation_params']['realistic_mode']
        
        print("\n" + "="*70)
        print("DAILY ARBITRAGE BACKTEST RESULTS - ALL TRADING DAYS")
        print("="*70)
        print(f"Strategy: Buy Cairo Open, Sell Cairo Close (Tue, Wed, Thu, Sun)")
        print(f"Trigger: London Daily Move > 1%")
        print(f"Execution Mode: {'THNDR REALISTIC' if realistic else 'PERFECT (Ideal)'}")
        
        if realistic:
            print(f"\n🏦 THNDR ACTUAL BROKER COSTS (EGP-based):")
            params = self.backtest_results['simulation_params']
            print(f"  • Fixed per transaction: 2.00 EGP")
            print(f"  • Variable commission: 0.10%")
            print(f"  • Third-party fee: 0.03%")
            print(f"  ───────────────────────────────")
            total_cost = params['commission_pct']  # This is 0.2613% total
            print(f"  • TOTAL COST PER TRADE (Buy+Sell): {total_cost:.4f}%")
            print(f"  • Cost per $10,000 trade: $26.13")
        
        print(f"\n{'='*70}")
        print(f"SUMMARY STATISTICS")
        print(f"{'='*70}")
        print(f"Total Trades: {len(trades_df)}")
        print(f"Winning Trades: {self.backtest_results['winning_trades']}")
        print(f"Losing Trades: {self.backtest_results['losing_trades']}")
        
        if len(trades_df) > 0:
            win_rate = (self.backtest_results['winning_trades'] / len(trades_df)) * 100
            print(f"Win Rate: {win_rate:.2f}%")
            
            # Breakdown by signal source
            if 'Signal_Day' in trades_df.columns:
                print(f"\nTrades by Signal Source:")
                for source in ['Monday', 'Tuesday', 'Wednesday', 'Friday']:
                    count = (trades_df['Signal_Day'] == source).sum()
                    if count > 0:
                        source_trades = trades_df[trades_df['Signal_Day'] == source]
                        source_pnl = source_trades['PnL$'].sum()
                        source_return = (source_pnl / (10000 * count)) * 100
                        wins = (source_trades['PnL$'] > 0).sum()
                        print(f"  {source:10s}: {count:2d} trades | ${source_pnl:8.2f} P&L | {source_return:6.2f}% avg | {wins}/{count} wins")
            
            if realistic and 'PnL%' in trades_df.columns:
                print(f"\n{'─'*70}")
                print(f"--- REALISTIC RESULTS (With Costs) ---")
                print(f"Average PnL per Trade: ${trades_df['PnL$'].mean():.2f}")
                print(f"Best Trade: ${trades_df['PnL$'].max():.2f}")
                print(f"Worst Trade: ${trades_df['PnL$'].min():.2f}")
                
                print(f"\nTotal P&L (Realistic): ${self.backtest_results['total_pnl']:.2f}")
                print(f"Total Costs: ${self.backtest_results['total_costs']:.2f}")
                print(f"Initial Capital per Trade: $10,000")
                
                realistic_return = (self.backtest_results['total_pnl']/(10000*len(trades_df)))*100
                print(f"Average Realistic Return: {realistic_return:.2f}%")
                
                # Show ideal comparison
                print(f"\n--- IDEAL RESULTS (Perfect Execution) ---")
                print(f"Total P&L (Ideal): ${self.backtest_results['total_pnl_ideal']:.2f}")
                ideal_return = (self.backtest_results['total_pnl_ideal']/(10000*len(trades_df)))*100
                print(f"Average Ideal Return: {ideal_return:.2f}%")
                
                print(f"\n--- IMPACT ANALYSIS ---")
                impact = self.backtest_results['total_pnl_ideal'] - self.backtest_results['total_pnl']
                impact_pct = (impact / abs(self.backtest_results['total_pnl_ideal'])) * 100 if self.backtest_results['total_pnl_ideal'] != 0 else 0
                print(f"Cost Impact: -${impact:.2f} ({-impact_pct:.2f}%)")
                print(f"Average Cost per Trade: ${self.backtest_results['total_costs']/len(trades_df):.2f}")
                
            else:
                win_rate = (self.backtest_results['winning_trades'] / len(trades_df)) * 100
                print(f"Win Rate: {win_rate:.2f}%")
                print(f"\nAverage PnL per Trade: ${trades_df['PnL$'].mean():.2f}")
                print(f"Total P&L: ${self.backtest_results['total_pnl']:.2f}")
                print(f"Return: {(self.backtest_results['total_pnl']/(10000*len(trades_df)))*100:.2f}%")
            
            print(f"\n{'='*70}")
            print("DETAILED TRADE LOG:")
            print(f"{'='*70}")
            
            for idx, row in trades_df.iterrows():
                if realistic and 'PnL%' in trades_df.columns:
                    ideal_pnl = row['PnL%_Ideal']
                    realistic_pnl = row['PnL%']
                    source = row.get('Signal_Day', '')
                    print(f"{row['Date']} ({source:3s}) | Entry: {row['Entry_Price']:.2f} | Exit: {row['Exit_Price']:.2f}")
                    print(f"           Ideal: {ideal_pnl:+.2f}% | Realistic: {realistic_pnl:+.2f}% | Cost: ${row['Costs']:.2f}")
                else:
                    source = row.get('Signal_Day', '')
                    print(f"{row['Date']} ({source:3s}) | Open: {row['Cairo_Open']:.2f} | Close: {row['Cairo_Close']:.2f} | "
                          f"PnL: {row['PnL%']:.2f}% (${row['PnL$']:.2f})")
        
        print("="*70)
    
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
        # Run backtest with THNDR ACTUAL COSTS
        # Real fee structure: 2 EGP per tx + 0.1% variable + 0.03% third-party = 0.2613% total
        self.backtest_arbitrage(
            initial_capital=10000,
            slippage_pct=0.0,           # 0% (included in fixed fees)
            bid_ask_spread=0.0,         # 0% (included in commission)
            commission_pct=0.2613,      # 0.2613% actual Thndr fee (2 EGP + 0.1% + 0.03%)
            execution_delay_pct=0.0,    # 0% (no significant delay cost)
            realistic_mode=True         # THNDR ACTUAL simulation
        )
        self.print_backtest_results()
        
        return True


def main():
    """Main execution - CIB Arbitrage Analysis"""
    print("\n" + "="*60)
    print("CIB ARBITRAGE ANALYSIS: CAIRO vs LONDON")
    print("="*60)
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    # Alternative ticker pairs to try
    alt_pairs = [
        ('AAPL', 'MSFT'),   # Tech pair (Mon-Fri vs Mon-Fri)
        ('AAPL', 'ASML'),   # Mixed pair
    ]
    
    for attempt, (ticker1, ticker2) in enumerate(alt_pairs):
        print(f"\nAttempt {attempt + 1}: Testing {ticker1} vs {ticker2}")
        print(f"Date range: {start_date} to {end_date}\n")
        
        analyzer = CIBArbitrageAnalyzer(
            cairo_ticker=ticker1,
            london_ticker=ticker2,
            start_date=str(start_date),
            end_date=str(end_date)
        )
        
        try:
            if analyzer.run():
                print(f"\n✓ Successfully completed analysis for {ticker1} vs {ticker2}")
                break
        except Exception as e:
            print(f"\nError with {ticker1} vs {ticker2}: {e}")
            print("Trying next pair...\n")


if __name__ == "__main__":
    main()
