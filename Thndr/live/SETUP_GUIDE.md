# THNDR Live System - Complete Setup Guide

## 🎯 What You're Getting

A **production-ready, free, always-on trading alert system** that:
- ✅ Monitors Cairo-London market prices hourly
- ✅ Detects 1.25% signal threshold (your tested best strategy)
- ✅ Sends email alerts instantly when signal triggers
- ✅ Runs 24/7 in the cloud for FREE
- ✅ Takes < 5 minutes to deploy

---

## 📋 Files Overview

| File | Purpose |
|------|---------|
| `live_fetcher.py` | Main signal detection & email alert engine |
| `scheduler_local.py` | Local hourly scheduler (for testing) |
| `Dockerfile` | Container for cloud deployment |
| `deploy-gcp.sh` | One-click Google Cloud deployment |
| `CLOUD_DEPLOY.md` | Detailed cloud setup instructions |
| `requirements.txt` | Python dependencies |
| `README.md` | Quick reference guide |

---

## 🚀 Quickest Start (< 5 minutes)

### Step 1: Get Gmail App Password (2 min)
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" + "Windows Computer"
3. Copy the 16-character password
4. Save it somewhere safe

### Step 2: Deploy to Cloud (3 min)
```bash
cd Thndr/live

# Set your credentials
export PROJECT_ID="your-gcp-project"
export GMAIL_USER="your-email@gmail.com"
export GMAIL_PASSWORD="xxxx xxxx xxxx xxxx"  # The 16-char password from step 1
export ALERT_EMAIL="your-email@gmail.com"   # Where to send alerts

# Deploy (one command!)
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

**Done!** Your system is now live. 🎉

---

## 🧪 Test Locally First (Recommended)

Want to test before deploying to cloud?

```bash
cd Thndr/live
pip install -r requirements.txt

# Set credentials
export GMAIL_USER="your-email@gmail.com"
export GMAIL_PASSWORD="xxxx xxxx xxxx xxxx"
export ALERT_EMAIL="your-email@gmail.com"

# Test once
python live_fetcher.py

# Or run hourly scheduler locally
python scheduler_local.py
```

Expected output:
```
2026-05-05 21:07:48 - INFO - ✓ Currently in Cairo trading hours
2026-05-05 21:07:50 - INFO - London CBKD.L: Move=+1.45%
2026-05-05 21:07:50 - INFO - Cairo COMI.CA: Price=24.50 EGP
2026-05-05 21:07:50 - INFO - 🚨 SIGNAL DETECTED: BUY (+1.45%)
2026-05-05 21:07:52 - INFO - ✅ Alert email sent
```

---

## 📊 How Signal Detection Works

```
EVERY HOUR (during Cairo trading hours):
  ↓
Get London closing price
  ↓
Calculate move = (Close - Open) / Open * 100
  ↓
Is |move| > 1.25%?
  │
  ├─ YES ──→ SEND EMAIL ALERT
  │         Subject: "🚨 THNDR TRADING ALERT: BUY Signal"
  │         Content: Complete trading instructions
  │
  └─ NO ──→ Wait for next hour
```

---

## 📧 Alert Example

**Email Subject:**
```
🚨 THNDR TRADING ALERT: BUY Signal Detected
```

**Email Body:**
```
TRADING SIGNAL DETECTED
=======================

Type: BUY
Time: 2026-05-05T09:30:00+02:00

LONDON MOVE:
  Move: +1.45% (Threshold: 1.25%)
  Status: ✅ SIGNAL TRIGGERED

CAIRO PRICE:
  Current: 24.50 EGP

RECOMMENDED ACTION:
1. Login to Thndr.com
2. Search for COMI.CA
3. Place BUY limit order at 0.1% below market
4. Set SELL target at 0.5% profit
5. Monitor position

Expected P&L: ~$23.87 per trade

⚠️ Past performance ≠ future results
```

When you receive this, you manually execute on Thndr.

---

## 💰 Cost Analysis

**TOTALLY FREE** ✅

| Component | Cost | Why Free |
|-----------|------|----------|
| Google Cloud Run | $0 | ~720 checks/month << 2M free limit |
| Gmail SMTP | $0 | Built into Gmail |
| Cloud Scheduler | $0 | Free tier includes 3 jobs |
| **TOTAL** | **$0/month** | ✅ No credit card charges |

**Equivalent paid alternatives:**
- Heroku: $7/month (cheap but slower)
- AWS Lambda: $0.20/million (you'd pay almost nothing)
- Firebase: Free tier plenty

---

## 🛠️ Deployment Options

### Option 1: Google Cloud Run (RECOMMENDED)
- **Setup time:** 5 minutes
- **Cost:** FREE
- **Reliability:** 99.95% uptime
- **Auto-scaling:** Handles spikes automatically
- **Command:**
  ```bash
  ./deploy-gcp.sh
  ```

### Option 2: Local Testing
- **Setup time:** 2 minutes
- **Cost:** FREE (uses your computer)
- **Reliability:** Depends on your machine running
- **Command:**
  ```bash
  python scheduler_local.py
  ```
- **Note:** Requires your computer running 24/7

### Option 3: Heroku
- **Setup time:** 10 minutes  
- **Cost:** FREE (with git-based deployment)
- **Reliability:** Good
- **Commands:** (See CLOUD_DEPLOY.md)

### Option 4: Railway / Render / Replit
- Similar to Heroku
- See CLOUD_DEPLOY.md for instructions

---

## ⚙️ Configuration

### Change Signal Threshold
If you want stricter/looser signals:

```python
# In live_fetcher.py, line 31
self.signal_threshold = 1.25  # Change to your preferred threshold

# Examples:
# 1.0 = More sensitive (more alerts)
# 1.25 = Your tested optimal (recommended)
# 1.5 = Less sensitive (fewer alerts)
# 2.0 = Very strict (only strong moves)
```

### Change Check Frequency
If you want more/fewer checks:

```bash
# In deploy-gcp.sh, line 26
--schedule="0 9-16 * * 0-4"  # Cron format

# Examples:
# Every hour: "0 9-16 * * 0-4"
# Every 15 min: "*/15 9-16 * * 0-4"
# Twice daily (10am, 3pm): "0 10,15 * * 0-4"
# Only once at 10am: "0 10 * * 0-4"
```

---

## 📈 Monitoring

### Google Cloud Run Console
```
https://console.cloud.google.com/run
```
- View all deployments
- Check logs in real-time
- Monitor resource usage
- See invocation count

### Command Line
```bash
# View recent logs
gcloud logging read --limit 50

# Tail live logs
gcloud run services describe thndr-fetcher --region us-central1

# Check deployment status
gcloud run services list
```

---

## 🐛 Troubleshooting

### Problem: "Gmail credentials not provided"
**Solution:** Set environment variables before running
```bash
export GMAIL_USER="your@gmail.com"
export GMAIL_PASSWORD="xxxx xxxx xxxx xxxx"
export ALERT_EMAIL="your@gmail.com"
python live_fetcher.py
```

### Problem: Gmail authentication fails
**Solution:** Use app password, not regular Gmail password
1. Go to https://myaccount.google.com/apppasswords
2. Generate new app password
3. Use that 16-character password (not your Gmail login password)

### Problem: No alerts received
**Solution:** Check 3 things
1. Email in spam folder ✓
2. ALERT_EMAIL env var correct ✓
3. Try sending test email:
   ```python
   from live_fetcher import EmailNotifier
   notifier = EmailNotifier()
   notifier.send_status("Test email - if you see this, emails work!")
   ```

### Problem: "Outside Cairo trading hours"
**Solution:** This is normal!
- Script only runs Sun-Thu, 9 AM - 4 PM Cairo time
- This saves costs and reduces unnecessary alerts
- If you want to test outside hours, edit line 44 of `live_fetcher.py`:
  ```python
  return True  # Always return True to bypass time check
  ```

### Problem: Docker build fails
**Solution:** 
- Ensure Docker installed: `docker --version`
- Check internet connection
- Try: `docker pull python:3.11-slim` first

### Problem: Cloud Run deployment fails
**Solution:**
- Check project ID is correct
- Verify gcloud authenticated: `gcloud auth list`
- Try: `gcloud auth application-default login`

---

## 📱 Next Steps After Deployment

### 1. Verify It Works (Day 1)
- Manually trigger a test during trading hours
- Check that email alert arrives
- Reply to alert to confirm email works

### 2. Monitor for a Week
- Watch for real signals (should get ~1 per week)
- Check Cloud Run logs weekly
- Verify alerts arrive in time

### 3. When Alert Arrives
- Read full alert email
- Login to Thndr
- Execute trade manually:
  1. Search for COMI.CA
  2. BUY with 0.1% limit order
  3. Set SELL at 0.5% target
  4. Wait for fill

### 4. Track Performance
- Log each trade in `position_tracker.py`
- Compare actual results vs backtest ($23.87 target)
- Adjust if needed (threshold, limits, etc)

---

## 🔐 Security Notes

⚠️ Important:
- Never commit env vars to GitHub
- Never share your Gmail app password
- Use Cloud Secrets Manager for production (free tier)
- Rotate passwords every 3-6 months
- Gmail passwords: Delete and regenerate periodically
- Cloud credentials: Use service accounts, not personal keys

### Setup Secrets Properly
```bash
# For Cloud Run, use Secret Manager (free):
gcloud secrets create GMAIL_PASSWORD --data-file=-
# Type your password, Ctrl+D to save

# Reference in Cloud Run:
gcloud run deploy ... --update-secrets GMAIL_PASSWORD=GMAIL_PASSWORD:latest
```

---

## 📞 Support Checklist

If something doesn't work:
1. ✅ Check all env vars set: `echo $GMAIL_USER`
2. ✅ Verify Gmail app password (not regular password)
3. ✅ Test locally first: `python live_fetcher.py`
4. ✅ Check email spam folder
5. ✅ Review logs: `gcloud logging read`
6. ✅ Try test email before depending on alerts

---

## 🎓 What You've Built

A **production-grade real-time trading system** that:
- ✅ Runs 24/7 in the cloud
- ✅ Costs exactly $0/month
- ✅ Scales automatically
- ✅ Notifies you instantly
- ✅ Integrates with your tested strategy
- ✅ Can be deployed anywhere

**This is the foundation for:**
- Automated trading (if API available)
- Discord/Telegram notifications
- Mobile app alerts
- Multi-strategy monitoring
- Portfolio tracking

---

## 🚀 You're Ready!

Your complete live trading system is set up. Next:
1. Deploy to Google Cloud Run (`./deploy-gcp.sh`)
2. Wait for first signal
3. Execute manually on Thndr
4. Track results vs backtest
5. Refine based on real data

**Questions?** Start with local testing:
```bash
python live_fetcher.py
```

Good luck! 📈
