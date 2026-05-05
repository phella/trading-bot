#!/usr/bin/env python3
"""
THNDR LIVE DATA FETCHER
=======================

Real-time price monitoring with signal generation and email alerts.
- Fetches London & Cairo prices every hour (Cairo trading hours)
- Checks for 1.25% signal threshold
- Sends email alerts when signal detected
- Cloud-ready (Google Cloud Run, Heroku, Railway, etc)

Environment Variables Required:
  GMAIL_USER: Your Gmail address
  GMAIL_PASSWORD: Gmail app-specific password (not regular password)
  ALERT_EMAIL: Email to send alerts to (can be same as GMAIL_USER)
"""

import os
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, time
import pytz
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LiveDataFetcher:
    """Fetch live data and generate trading signals"""
    
    def __init__(self, cairo_ticker="COMI.CA", london_ticker="CBKD.L"):
        self.cairo_ticker = cairo_ticker
        self.london_ticker = london_ticker
        self.signal_threshold = 1.25  # 1.25% as per tested strategy
        
        # Timezones
        self.cairo_tz = pytz.timezone('Africa/Cairo')
        self.london_tz = pytz.timezone('Europe/London')
    
    def is_cairo_trading_hours(self):
        """Check if we're in Cairo trading hours (Sun-Thu, 9:00-16:00 Cairo time)"""
        now = datetime.now(self.cairo_tz)
        
        # Cairo: Sun=6, Mon=0, Tue=1, Wed=2, Thu=3
        trading_days = [6, 0, 1, 2, 3]  # Sun-Thu
        
        if now.weekday() not in trading_days:
            return False
        
        # Trading hours: 9:00 to 16:00 Cairo time
        if time(9, 0) <= now.time() <= time(16, 0):
            return True
        
        return False
    
    def get_london_daily_move(self):
        """Get London's daily move percentage"""
        try:
            london = yf.download(self.london_ticker, period='5d', progress=False)
            
            if london.empty:
                logger.error("No London data available")
                return None, None
            
            today = london.iloc[-1]
            london_open = today['Open']
            london_close = today['Close']
            
            daily_move = ((london_close - london_open) / london_open) * 100
            
            logger.info(f"London {self.london_ticker}: Open={london_open:.2f}, Close={london_close:.2f}, Move={daily_move:+.2f}%")
            
            return daily_move, {
                'open': london_open,
                'close': london_close,
                'high': today['High'],
                'low': today['Low'],
                'volume': today['Volume']
            }
        
        except Exception as e:
            logger.error(f"Error fetching London data: {e}")
            return None, None
    
    def get_cairo_current_price(self):
        """Get Cairo's current price"""
        try:
            cairo = yf.download(self.cairo_ticker, period='5d', progress=False)
            
            if cairo.empty:
                logger.error("No Cairo data available")
                return None
            
            current = cairo.iloc[-1]
            
            logger.info(f"Cairo {self.cairo_ticker}: Price={current['Close']:.2f} EGP")
            
            return {
                'price': current['Close'],
                'open': current['Open'],
                'high': current['High'],
                'low': current['Low'],
                'volume': current['Volume']
            }
        
        except Exception as e:
            logger.error(f"Error fetching Cairo data: {e}")
            return None
    
    def check_signal(self):
        """Check if trading signal exists"""
        london_move, london_data = self.get_london_daily_move()
        cairo_price = self.get_cairo_current_price()
        
        if london_move is None or cairo_price is None:
            return None
        
        has_signal = abs(london_move) > self.signal_threshold
        
        signal = {
            'timestamp': datetime.now(self.cairo_tz).isoformat(),
            'has_signal': has_signal,
            'london_move': london_move,
            'london_data': london_data,
            'cairo_price': cairo_price,
            'signal_type': 'BUY' if london_move > 0 else 'SELL',
            'threshold': self.signal_threshold
        }
        
        return signal

class EmailNotifier:
    """Send email notifications"""
    
    def __init__(self, gmail_user=None, gmail_password=None, alert_email=None):
        self.gmail_user = gmail_user or os.getenv('GMAIL_USER')
        self.gmail_password = gmail_password or os.getenv('GMAIL_PASSWORD')
        self.alert_email = alert_email or os.getenv('ALERT_EMAIL', self.gmail_user)
        
        if not self.gmail_user or not self.gmail_password:
            raise ValueError("Gmail credentials not provided. Set GMAIL_USER and GMAIL_PASSWORD env vars")
        
        logger.info(f"Email notifier initialized for {self.alert_email}")
    
    def send_alert(self, signal):
        """Send email alert for signal"""
        if not signal or not signal['has_signal']:
            return False
        
        try:
            # Build email message
            subject = f"🚨 THNDR TRADING ALERT: {signal['signal_type']} Signal Detected"
            
            body = f"""
TRADING SIGNAL DETECTED
=======================

Type: {signal['signal_type']}
Time: {signal['timestamp']}

LONDON MOVE:
  Move: {signal['london_move']:+.2f}%
  Threshold: {signal['threshold']}%
  Status: ✅ SIGNAL TRIGGERED (>threshold)

CAIRO PRICE:
  Current: {signal['cairo_price']['price']:.2f} EGP
  Open: {signal['cairo_price']['open']:.2f} EGP
  High: {signal['cairo_price']['high']:.2f} EGP
  Low: {signal['cairo_price']['low']:.2f} EGP

RECOMMENDED ACTION:
  1. Login to Thndr.com
  2. Search for COMI.CA
  3. Place BUY limit order at 0.1% below market
  4. Set SELL target at 0.5% profit
  5. Monitor position

Expected P&L: ~$23.87 per trade (based on backtest)

⚠️ This is NOT financial advice. Past performance ≠ future returns.
Start with small positions. Trade at your own risk.

---
THNDR Live Data Fetcher
"""
            
            # Send email
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = self.alert_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Alert email sent to {self.alert_email}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False
    
    def send_status(self, status_msg):
        """Send status update email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = self.alert_email
            msg['Subject'] = "📊 THNDR Status Update"
            
            msg.attach(MIMEText(status_msg, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            
            logger.info("✅ Status email sent")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to send status: {e}")
            return False

def check_and_notify():
    """Main function: Check for signals and notify"""
    logger.info("="*80)
    logger.info("🤖 THNDR LIVE DATA FETCHER - Checking for signals...")
    logger.info("="*80)
    
    try:
        # Initialize
        fetcher = LiveDataFetcher()
        notifier = EmailNotifier()
        
        # Check if we're in trading hours
        if not fetcher.is_cairo_trading_hours():
            logger.info("⏰ Outside Cairo trading hours. Skipping check.")
            logger.info("   Trading hours: Sun-Thu, 9:00-16:00 Cairo time")
            return False
        
        logger.info("✓ Currently in Cairo trading hours")
        
        # Check for signal
        signal = fetcher.check_signal()
        
        if signal is None:
            logger.warning("⚠️ Could not fetch market data")
            return False
        
        logger.info(f"Signal check: {signal['london_move']:+.2f}% move (threshold: {signal['threshold']}%)")
        
        # If signal detected, send alert
        if signal['has_signal']:
            logger.info(f"🚨 SIGNAL DETECTED: {signal['signal_type']} ({signal['london_move']:+.2f}%)")
            notifier.send_alert(signal)
            return True
        else:
            logger.info(f"✓ No signal (move {signal['london_move']:+.2f}% < threshold {signal['threshold']}%)")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error in check_and_notify: {e}")
        return False

def main():
    """Entry point for direct execution"""
    print("\n" + "█"*80)
    print("THNDR LIVE DATA FETCHER")
    print("█"*80)
    print("\nUsage:")
    print("  python live_fetcher.py                    # Check once")
    print("  python live_fetcher.py --loop             # Run continuously (for local testing)")
    print("  docker build -t thndr-fetcher .           # Build Docker image")
    print("  gcloud run deploy thndr-fetcher ...       # Deploy to Google Cloud Run")
    print("\nEnvironment Variables Required:")
    print("  GMAIL_USER: Your Gmail address")
    print("  GMAIL_PASSWORD: Gmail app-specific password")
    print("  ALERT_EMAIL: Email to send alerts to (optional)")
    print("\n" + "█"*80 + "\n")
    
    # Check once
    check_and_notify()

if __name__ == '__main__':
    main()
