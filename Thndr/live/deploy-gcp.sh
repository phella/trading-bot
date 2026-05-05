#!/bin/bash
# Google Cloud Run Deployment Script
# Run this to deploy live fetcher to Google Cloud Run

PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="thndr-live-fetcher"
REGION="us-central1"  # Or your preferred region
SCHEDULE_NAME="thndr-hourly-check"
TIMEZONE="Africa/Cairo"

echo "🚀 Deploying THNDR Live Fetcher to Google Cloud Run"
echo "=================================================="

# 1. Build and push Docker image
echo "Step 1: Building and pushing Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --project=$PROJECT_ID

# 2. Deploy to Cloud Run
echo "Step 2: Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --memory 512Mi \
  --timeout 300 \
  --set-env-vars GMAIL_USER=$GMAIL_USER,GMAIL_PASSWORD=$GMAIL_PASSWORD,ALERT_EMAIL=$ALERT_EMAIL \
  --project=$PROJECT_ID

# 3. Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format 'value(status.url)' \
  --project=$PROJECT_ID)

echo "Step 3: Setting up Cloud Scheduler..."
echo "Service deployed at: $SERVICE_URL"

# 4. Create Cloud Scheduler job (if using Cloud Scheduler)
# Schedule it to run every hour during trading hours
gcloud scheduler jobs create http $SCHEDULE_NAME \
  --schedule="0 9-16 * * 0-4" \
  --http-method=GET \
  --uri="$SERVICE_URL" \
  --time-zone=$TIMEZONE \
  --location=$REGION \
  --project=$PROJECT_ID || echo "Scheduler job already exists or failed"

echo ""
echo "✅ Deployment complete!"
echo "📊 Service URL: $SERVICE_URL"
echo "⏰ Scheduler: Every hour, 9 AM - 4 PM Cairo time"
echo ""
echo "Next steps:"
echo "1. Set environment variables in Cloud Run:"
echo "   - GMAIL_USER: your-email@gmail.com"
echo "   - GMAIL_PASSWORD: your-app-password"
echo "   - ALERT_EMAIL: recipient@email.com"
