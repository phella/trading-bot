# THNDR Live Data Fetcher

Real-time signal detection and email alerts for THNDR trading strategy.

**Status:** ✅ Ready to deploy  
**Notification:** Email (Gmail)  
**Cloud:** Google Cloud Run (free tier)  
**Cost:** $0/month  

---

## What it Does

- ✅ Checks London market daily move every hour
- ✅ Detects when move > 1.25% (your tested threshold)
- ✅ Sends email alert immediately when signal triggers
- ✅ Runs only during Cairo trading hours (Sun-Thu, 9-16 local)
- ✅ Saves costs by not checking outside trading hours
- ✅ Completely free to run and deploy

---

## Quick Start (Local Testing)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Gmail Credentials
```bash
export GMAIL_USER="your-email@gmail.com"
export GMAIL_PASSWORD="xxxx xxxx xxxx xxxx"  # Gmail app password (16 chars)
export ALERT_EMAIL="where@to@send@alerts.com"
```

**Get Gmail app password:**
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Copy the 16-character password
4. Use it as GMAIL_PASSWORD (not your regular Gmail password!)

### 3. Test Once
```bash
python live_fetcher.py
```

Output:
```
════════════════════════════════════════════════════════════════════════════════
🤖 THNDR LIVE DATA FETCHER - Checking for signals...
════════════════════════════════════════════════════════════════════════════════
✓ Currently in Cairo trading hours
London CBKD.L: Open=123.45, Close=124.50, Move=+0.85%
Cairo COMI.CA: Price=24.50 EGP
✓ No signal (move +0.85% < threshold 1.25%)
```

### 4. Local Scheduler (Hourly)
```bash
pip install schedule
python scheduler_local.py

# Runs every hour during trading hours
# Press Ctrl+C to stop
```

---

## Deploy to Cloud (Google Cloud Run)

**Recommended for always-on monitoring**

### Option 1: Automated
```bash
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

### Option 2: Manual
```bash
# 1. Build Docker image
gcloud builds submit --tag gcr.io/YOUR_PROJECT/thndr-fetcher

# 2. Deploy to Cloud Run
gcloud run deploy thndr-fetcher \
  --image gcr.io/YOUR_PROJECT/thndr-fetcher \
  --region us-central1 \
  --set-env-vars GMAIL_USER=$GMAIL_USER,GMAIL_PASSWORD=$GMAIL_PASSWORD

# 3. Setup scheduled checks (optional)
gcloud scheduler jobs create http thndr-check \
  --schedule="0 9-16 * * 0-4" \
  --http-method=GET \
  --uri="YOUR_CLOUD_RUN_URL"
```

### Cost
- **FREE** for your usage (well under Google Cloud Run free tier)
- ~720 checks/month = minimal CPU/memory usage

See [CLOUD_DEPLOY.md](CLOUD_DEPLOY.md) for detailed instructions.

---

## File Structure

```
live/
├── live_fetcher.py          # Main fetcher & alert logic
├── scheduler_local.py       # Local hourly scheduler (testing)
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container for cloud deployment
├── deploy-gcp.sh          # Google Cloud Run deployment script
├── CLOUD_DEPLOY.md        # Detailed cloud setup guide
└── README.md              # This file
```

---

## How Alerts Work

### 1. Signal Detection
```
Every hour (during trading hours):
  ↓
Get London daily move %
  ↓
Is |move| > 1.25%?
  ├─ YES → SEND ALERT EMAIL
  └─ NO  → Silently continue
```

### 2. Email Alert
When signal detected, you receive:
- **Subject:** 🚨 THNDR TRADING ALERT: BUY Signal Detected
- **Content:**
  - Exact London move %
  - Cairo current price
  - Recommended action (manual Thndr execution)
  - Trade parameters (buy 0.1%, sell 0.5%)

### 3. Example Alert

```
TRADING SIGNAL DETECTED
=======================

Type: BUY
Time: 2026-05-05T09:30:00+02:00

LONDON MOVE:
  Move: +1.45%
  Threshold: 1.25%
  Status: ✅ SIGNAL TRIGGERED

CAIRO PRICE:
  Current: 24.50 EGP

RECOMMENDED ACTION:
  1. Login to Thndr.com
  2. Search for COMI.CA
  3. Place BUY limit order at 0.1% below market
  4. Set SELL target at 0.5% profit
  5. Monitor position

Expected P&L: ~$23.87
```

---

## Configuration

### Change Signal Threshold
```python
# In live_fetcher.py, line 31
self.signal_threshold = 1.25  # Change to 1.0, 1.5, etc
```

### Change Check Frequency
```bash
# In deploy-gcp.sh, line 26
--schedule="0 9-16 * * 0-4"  # Cron format (hourly 9am-4pm)

# Other examples:
# Every 30 minutes: "*/30 9-16 * * 0-4"
# Every hour: "0 9-16 * * 0-4"
# Every 2 hours: "0 9,11,13,15 * * 0-4"
# Only at 10am: "0 10 * * 0-4"
```

### Change Alert Email
```bash
export ALERT_EMAIL="different-email@gmail.com"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Gmail auth fails | Use app password, not regular password. Enable 2FA first. |
| No emails received | Check spam folder. Verify ALERT_EMAIL is correct. |
| "Outside trading hours" | Normal! Script only runs Sun-Thu, 9-16 Cairo time |
| Docker build fails | Ensure Docker installed. Check internet connection. |
| Cloud Run fails | Verify env vars set. Check project ID correct. |

---

## Cost Breakdown

| Service | Monthly Cost | Why Free |
|---------|-------------|----------|
| Google Cloud Run | $0 | ~720 requests << 2M free limit |
| Gmail API | $0 | Built into Gmail |
| Cloud Scheduler | $0 | Free tier includes 3 jobs |
| **TOTAL** | **$0** | ✅ Completely free |

---

## Next Steps

1. **Test locally first**
   ```bash
   python live_fetcher.py
   ```

2. **Verify emails work**
   - Check Gmail spam folder
   - Reply to alert to confirm email works

3. **Deploy to cloud**
   ```bash
   ./deploy-gcp.sh
   ```

4. **Monitor for a week**
   - Check logs in Cloud Run console
   - Verify alerts arrive when signals trigger

5. **Integrate with position tracker**
   - When alert arrives, execute on Thndr
   - Log trade in position_tracker.py
   - Track actual vs backtest results

---

## Architecture

```
┌─────────────────────────────────┐
│  Live Data Fetcher (hourly)     │
│  - Check Cairo & London prices  │
│  - Detect 1.25% threshold       │
└────────────┬────────────────────┘
             │
             ├─Signal Detected?
             │ └─YES→ SEND EMAIL ALERT
             │         ↓
             │    Gmail SMTP
             │         ↓
             │    Your Inbox
             │
             └─NO→ Continue waiting

┌─────────────────────────────────┐
│  Cloud Run (Always-On)          │
│  Runs hourly during trading hrs │
└─────────────────────────────────┘

OR

┌─────────────────────────────────┐
│  Local Scheduler (Dev/Testing)  │
│  Runs on your machine           │
└─────────────────────────────────┘
```

---

## Future Enhancements

- [ ] Multiple notification channels (Discord, Telegram)
- [ ] Webhook integration (if trading bot available)
- [ ] Position tracking integration
- [ ] Real-time (minute-by-minute) monitoring
- [ ] SMS alerts (Twilio, ~$0.0075/alert)
- [ ] Slack integration
- [ ] Google Sheets logging

---

## Support

For issues:
1. Check [CLOUD_DEPLOY.md](CLOUD_DEPLOY.md) for cloud-specific help
2. Review logs: `gcloud logging read ...`
3. Test locally first to isolate issues
4. Verify all env vars set correctly

---

**Questions?** Start with:
- `python live_fetcher.py` (test locally)
- Check your spam folder (alerts might be there!)
- Verify env vars: `echo $GMAIL_USER`
