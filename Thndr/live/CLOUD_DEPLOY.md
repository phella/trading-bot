# THNDR Live Data Fetcher - Cloud Run Setup

## Deployment to Google Cloud Run (FREE TIER)

### Quick Start (5 minutes)

1. **Setup Gmail App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select: Mail + Windows Computer
   - Copy the 16-character password

2. **Set Environment Variables**
   ```bash
   export PROJECT_ID="your-gcp-project"
   export GMAIL_USER="your-email@gmail.com"
   export GMAIL_PASSWORD="xxxx xxxx xxxx xxxx"  # 16-char app password
   export ALERT_EMAIL="alert-recipient@gmail.com"
   ```

3. **Deploy**
   ```bash
   chmod +x deploy-gcp.sh
   ./deploy-gcp.sh
   ```

   OR manually:
   ```bash
   # Build Docker image
   gcloud builds submit --tag gcr.io/$PROJECT_ID/thndr-fetcher

   # Deploy to Cloud Run
   gcloud run deploy thndr-fetcher \
     --image gcr.io/$PROJECT_ID/thndr-fetcher \
     --platform managed \
     --region us-central1 \
     --memory 512Mi \
     --set-env-vars GMAIL_USER=$GMAIL_USER,GMAIL_PASSWORD=$GMAIL_PASSWORD,ALERT_EMAIL=$ALERT_EMAIL
   ```

4. **Setup Scheduler (Optional but Recommended)**
   ```bash
   # Run every hour during trading hours
   gcloud scheduler jobs create http thndr-check \
     --schedule="0 9-16 * * 0-4" \
     --http-method=GET \
     --uri="https://your-cloud-run-url.a.run.app" \
     --time-zone="Africa/Cairo"
   ```

---

## Free Tier Limits (Google Cloud Run)

| Resource | Free Tier | Your Usage |
|----------|-----------|-----------|
| Requests | 2M/month | ~720/month (hourly check) ✅ |
| CPU-seconds | 180,000/month | ~2.5 hours ✅ |
| Memory (GB-seconds) | 360,000/month | ~3 GB ✅ |
| Outbound data | 1 GB/month | ~50 MB ✅ |
| **Estimated Cost** | **FREE** | **$0.00** |

✅ You stay well within free tier!

---

## Alternative Cloud Providers

### Heroku (Easier Setup)
```bash
# Create app
heroku create thndr-live

# Set config vars
heroku config:set GMAIL_USER=your@gmail.com
heroku config:set GMAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
heroku config:set ALERT_EMAIL=recipient@gmail.com

# Push code
git push heroku main

# Add scheduler
heroku addons:create scheduler:standard
```

### Railway.app (Modern Alternative)
- Deploy from GitHub
- Auto-deploys on push
- $5 free credit/month (enough for many deployments)
- Simple environment variables UI

### Replit (Browser-Based)
- Import GitHub repo
- Click "Run"
- Setup env vars in Secrets
- Deploy with "Deploy" button
- Completely free, always-on

---

## Local Testing

```bash
# Test fetcher locally
python live_fetcher.py

# Test with environment variables
GMAIL_USER="your@gmail.com" \
GMAIL_PASSWORD="xxxx xxxx xxxx xxxx" \
ALERT_EMAIL="recipient@gmail.com" \
python live_fetcher.py

# Run every hour (for testing, Ctrl+C to stop)
while true; do
  python live_fetcher.py
  sleep 3600
done
```

---

## Getting Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication (if not already done)
3. Go to "App passwords"
4. Select: Mail + Windows Computer (or generic)
5. Google gives you 16-character password
6. Use this (not your regular Gmail password)

**⚠️ IMPORTANT:**
- Never commit env vars to GitHub
- Use Cloud secrets manager for production
- Rotate passwords regularly

---

## Monitoring & Logs

### Google Cloud Run
```bash
# View logs
gcloud run services describe thndr-fetcher --region us-central1

# Tail live logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 50 \
  --format json
```

### Heroku
```bash
heroku logs --tail
```

### Local
Just run the script and watch console output

---

## Troubleshooting

### "No module named 'yfinance'"
```bash
pip install -r requirements.txt
```

### "Gmail authentication failed"
- Check you're using app password (not regular password)
- Verify 2FA is enabled on your Google account
- Try creating a new app password

### "Outside Cairo trading hours"
- Script only runs during Cairo trading hours (Sun-Thu, 9-16 Cairo time)
- This is by design to save costs and reduce unnecessary alerts

### No signals detected
- This is normal! Signals only trigger when London move > 1.25%
- This happens maybe once every few days
- Check your email spam folder

---

## Production Checklist

- [ ] Gmail app password generated
- [ ] Environment variables stored securely (not in code)
- [ ] Cloud Run deployed successfully
- [ ] Cloud Scheduler configured (optional)
- [ ] Test alert received in email
- [ ] Logs checked and clean
- [ ] Cost monitoring setup
- [ ] Backup plan (switch to alternative provider)

---

## Cost Estimate (Monthly)

| Service | Cost | Notes |
|---------|------|-------|
| Google Cloud Run | FREE | ~720 requests/month, well under limits |
| Gmail API | FREE | Built into Gmail account |
| Cloud Scheduler | FREE | 3 free jobs (you need 1) |
| **Total** | **$0** | **Completely free** |

Alternatively with Heroku free tier: Also $0 (but has some restrictions)

---

## Next Steps

1. Deploy to cloud (5 minutes)
2. Verify emails work (check spam folder!)
3. Monitor for first week (check logs)
4. Adjust if needed (more/fewer notifications)
5. Integrate with position tracker when trade triggered

---

## Questions?

- Email alerts not working: Check email spam folder, verify credentials
- Wrong timezone: Adjust THNDR_TIMEZONE env var
- Too many alerts: Increase signal threshold from 1.25% to 1.5%
- Too few alerts: Decrease threshold to 1.0%
