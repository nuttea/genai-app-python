# 🌐 Datadog RUM Quick Start

Enable Real User Monitoring for your Streamlit frontend in 3 minutes!

## What is RUM?

Datadog RUM (Real User Monitoring) tracks:
- ✅ User sessions and interactions
- ✅ Page performance (Core Web Vitals)
- ✅ JavaScript errors
- ✅ API call performance
- ✅ Session replay (watch user sessions)

## 3-Minute Setup

### 1. Create RUM Application in Datadog

```bash
# Go to: https://app.datadoghq.com/rum/list
# Click "New Application"
# Select "Web Application"
# Name: genai-streamlit-frontend
# Get your Client Token and Application ID
```

### 2. Configure Environment

```bash
# Add to .env file
cat >> .env <<EOF
DD_RUM_CLIENT_TOKEN=pub73e15e13baeed4c70480231ac22a12b5
DD_RUM_APPLICATION_ID=91c94a57-8f3f-448f-b069-2ddbb795d2a4
EOF
```

**Note**: These are **public tokens** (safe to expose in frontend).

### 3. Restart Frontend

```bash
# Local
docker-compose restart streamlit-frontend

# Cloud Run
cd infra/cloud-run
export DD_RUM_CLIENT_TOKEN=pub73e15e13baeed4c70480231ac22a12b5
export DD_RUM_APPLICATION_ID=91c94a57-8f3f-448f-b069-2ddbb795d2a4
./deploy-frontend.sh
```

### 4. Verify

```bash
# Generate traffic
open http://localhost:8501

# View in Datadog (within 1-2 minutes)
open https://app.datadoghq.com/rum/sessions?query=service:genai-streamlit-frontend
```

## What You Get

### User Sessions
- Track all user visits
- Session duration
- Page views
- User flows

### Performance Metrics
- Page load time
- Core Web Vitals (LCP, FID, CLS)
- Resource loading time
- API call latency

### Error Tracking
- JavaScript errors with stack traces
- Failed API calls
- Console errors
- Link to backend traces

### Session Replay
- Watch user sessions
- See exactly what users did
- Debug issues visually

### Frontend ↔ Backend Correlation
- Click frontend request → see backend trace
- End-to-end visibility
- Full request journey

## View in Datadog

**Sessions**: https://app.datadoghq.com/rum/sessions
**Performance**: https://app.datadoghq.com/rum/performance/overview
**Errors**: https://app.datadoghq.com/rum/error-tracking
**Session Replay**: https://app.datadoghq.com/rum/replay/sessions

## Example Insights

### Find Slow Page Loads

```
@view.loading_time:>5000
service:genai-streamlit-frontend
```

### Find JavaScript Errors

```
@type:error
service:genai-streamlit-frontend
```

### Track Vote Extraction Usage

```
@view.url_path:/1_🗳️_Vote_Extractor
service:genai-streamlit-frontend
```

### Find Failed API Calls

```
@type:resource
@resource.status_code:>=400
service:genai-streamlit-frontend
```

## Cost Optimization

**High Traffic?** Reduce sampling:

```python
# In app.py, modify:
sessionSampleRate: 20,         # Track 20% of sessions
sessionReplaySampleRate: 5,    # Record 5% of replays
```

## Troubleshooting

### No RUM Data

**Check:**
```bash
# Verify env vars are set
docker-compose exec streamlit-frontend env | grep DD_RUM

# Check browser console (F12)
# Should see "Datadog RUM initialized"
```

### Sessions Not Correlating with Backend

**Verify:**
- Backend has Datadog APM enabled
- `allowedTracingUrls` includes backend URL
- Backend CORS allows trace headers

## Complete Guide

See [docs/monitoring/datadog-rum.md](docs/monitoring/datadog-rum.md) for:
- Complete configuration options
- Advanced features
- Privacy settings
- Monitoring best practices

---

**Quick**: Set `DD_RUM_CLIENT_TOKEN` and `DD_RUM_APPLICATION_ID`, restart, and track users! 🎉
