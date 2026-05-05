#!/usr/bin/env python3
"""
Local scheduler for THNDR Live Fetcher
Run this locally to test signal detection every hour during trading hours
"""

import schedule
import time
from live_fetcher import check_and_notify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def job():
    """Scheduled job"""
    logger.info("\n" + "="*80)
    logger.info("🕐 SCHEDULED CHECK")
    logger.info("="*80)
    check_and_notify()

if __name__ == '__main__':
    print("\n" + "█"*80)
    print("THNDR LIVE FETCHER - LOCAL SCHEDULER")
    print("█"*80)
    print("\nChecking for signals every hour during trading hours")
    print("Cairo trading: Sun-Thu, 9:00-16:00 Cairo time")
    print("\nPress Ctrl+C to stop\n")
    
    # Schedule job
    schedule.every().hour.do(job)
    
    # Run first check
    check_and_notify()
    
    # Keep scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute if a job is due
    except KeyboardInterrupt:
        print("\n\n✅ Scheduler stopped")
