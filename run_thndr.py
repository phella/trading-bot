#!/usr/bin/env python3
"""
THNDR TRADING MASTER RUNNER
============================

Orchestrate all THNDR strategies, analysis, and alerts from one place.
Keeps all results organized and comparable.
"""

import subprocess
import sys
from pathlib import Path

def run_strategy_backtest():
    """Run main strategy comparison backtest"""
    print("\n" + "█"*80)
    print("RUNNING: Strategy Backtest (Old vs New Limit Orders)")
    print("█"*80 + "\n")
    
    script_path = Path(__file__).parent / 'Thndr' / 'strategies' / 'limit_order_backtest.py'
    result = subprocess.run(['python3', str(script_path)], cwd=str(script_path.parent))
    return result.returncode == 0

def run_sensitivity_analysis():
    """Run sensitivity analysis"""
    print("\n" + "█"*80)
    print("RUNNING: Sensitivity Analysis (Different Thresholds)")
    print("█"*80 + "\n")
    
    script_path = Path(__file__).parent / 'Thndr' / 'analysis' / 'sensitivity_analysis.py'
    result = subprocess.run(['python3', str(script_path)], cwd=str(script_path.parent))
    return result.returncode == 0

def run_cost_analysis():
    """Run broker cost analysis"""
    print("\n" + "█"*80)
    print("RUNNING: Cost Analysis")
    print("█"*80 + "\n")
    
    script_path = Path(__file__).parent / 'Thndr' / 'analysis' / 'thndr_actual_costs.py'
    result = subprocess.run(['python3', str(script_path)], cwd=str(script_path.parent))
    return result.returncode == 0

def main():
    """Run selected analysis"""
    if len(sys.argv) < 2:
        print("""
THNDR Trading Master Runner
============================

Usage: python run_thndr.py [command]

Commands:
  backtest        Run strategy comparison backtest
  sensitivity     Run sensitivity analysis
  costs          Run broker cost analysis
  all            Run all analyses
  
Example:
  python run_thndr.py backtest    # Compare old vs new strategies
  python run_thndr.py all         # Run everything
        """)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'backtest':
        success = run_strategy_backtest()
    elif command == 'sensitivity':
        success = run_sensitivity_analysis()
    elif command == 'costs':
        success = run_cost_analysis()
    elif command == 'all':
        results = [
            run_strategy_backtest(),
            run_sensitivity_analysis(),
            run_cost_analysis()
        ]
        success = all(results)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
