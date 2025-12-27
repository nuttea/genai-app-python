# Datadog RUM (Real User Monitoring) Setup

Complete guide for setting up Datadog RUM to monitor frontend user experience, performance, and errors.

## Overview

Datadog RUM provides real-time visibility into:

✅ **User Sessions** - Track user journeys and interactions  
✅ **Page Performance** - Core Web Vitals, loading times  
✅ **Errors** - JavaScript errors and stack traces  
✅ **Resources** - API calls, images, scripts  
✅ **User Interactions** - Clicks, form submissions  
✅ **Session Replay** - Watch user sessions  

## Prerequisites

- Datadog account
- RUM application created in Datadog
- Client token and application ID

## Setup RUM Application in Datadog

### 1. Create RUM Application

1. Go to [Datadog RUM Applications](https://app.datadoghq.com/rum/list)
2. Click "New Application"
3. Select "Web Application"
4. Enter application name: `genai-streamlit-frontend`
5. Click "Create"

### 2. Get Credentials

After creating the application, you'll receive:
- **Client Token**: `pub...` (public token)
- **Application ID**: UUID format

Save these values - you'll need them for configuration.

## Quick Setup

### Local Development

```bash
# Add to .env file
cat >> .env <<EOF
DD_RUM_CLIENT_TOKEN=pub73e15e13baeed4c70480231ac22a12b5
DD_RUM_APPLICATION_ID=91c94a57-8f3f-448f-b069-2ddbb795d2a4
EOF

# Restart frontend
docker-compose restart streamlit-frontend
```

### Cloud Run Deployment

```bash
# Set environment variables
export DD_RUM_CLIENT_TOKEN=pub73e15e13baeed4c70480231ac22a12b5
export DD_RUM_APPLICATION_ID=91c94a57-8f3f-448f-b069-2ddbb795d2a4

# Deploy
cd infra/cloud-run
./deploy-frontend.sh
```

## Implementation

### How It Works

The RUM script is injected into the Streamlit app in `frontend/streamlit/app.py`:

```python
# Load RUM configuration from environment
DD_RUM_CLIENT_TOKEN = os.getenv("DD_RUM_CLIENT_TOKEN", "")
DD_RUM_APPLICATION_ID = os.getenv("DD_RUM_APPLICATION_ID", "")

if DD_RUM_CLIENT_TOKEN and DD_RUM_APPLICATION_ID:
    # Inject Datadog RUM script
    components.html(datadog_rum_script, height=0)
```

### Configuration

The RUM is configured with:

**Sampling:**
- `sessionSampleRate: 100` - Track 100% of sessions
- `sessionReplaySampleRate: 100` - Record 100% of sessions

**Tracking:**
- `trackResources: true` - Track API calls, images, scripts
- `trackLongTasks: true` - Detect performance issues
- `trackUserInteractions: true` - Track clicks, inputs
- `trackBfcacheViews: true` - Track back/forward cache navigation

**Tracing:**
- `allowedTracingUrls` - Correlate frontend → backend traces
- Includes localhost and Cloud Run URLs
- Propagates trace IDs to backend

**Privacy:**
- `defaultPrivacyLevel: 'allow'` - Record all data (adjust as needed)

## Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `DD_RUM_CLIENT_TOKEN` | Public client token | Yes | `pub123...` |
| `DD_RUM_APPLICATION_ID` | Application UUID | Yes | `91c94a57-...` |
| `DD_SITE` | Datadog site | No | `datadoghq.com` |
| `DD_SERVICE` | Service name | No | `genai-streamlit-frontend` |
| `DD_ENV` | Environment | No | `production` |
| `DD_VERSION` | Version | No | `0.1.0` |

## View RUM Data in Datadog

### Access RUM

**Sessions**: https://app.datadoghq.com/rum/sessions

**Performance**: https://app.datadoghq.com/rum/performance/overview

**Errors**: https://app.datadoghq.com/rum/error-tracking

**Session Replay**: https://app.datadoghq.com/rum/replay/sessions

### Key Metrics

**Performance:**
- Loading Time
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- First Input Delay (FID)
- Cumulative Layout Shift (CLS)

**User Behavior:**
- Page views
- User actions (clicks, inputs)
- Session duration
- User flows

**Errors:**
- JavaScript errors
- Failed API calls
- Console errors
- Network errors

**Resources:**
- API call latency
- Image loading times
- Script execution time

## Distributed Tracing (Frontend → Backend)

RUM automatically correlates frontend requests with backend traces:

**Configuration:**
```javascript
allowedTracingUrls: [
  (url) => url.startsWith("http://localhost"),
  /^https:\/\/[^\/]+\.run\.app/,
  {
    match: (url) => url.startsWith("${API_BASE_URL}"),
    propagatorTypes: ["datadog"]
  }
]
```

**Benefits:**
- ✅ Click frontend error → see backend trace
- ✅ Understand full request flow
- ✅ Identify frontend vs backend issues
- ✅ Track end-to-end latency

## Session Replay

### Enable Session Replay

Already enabled with `sessionReplaySampleRate: 100`.

### View Replays

1. Go to [Session Replay](https://app.datadoghq.com/rum/replay/sessions)
2. Filter by service: `genai-streamlit-frontend`
3. Click any session to watch replay

**What you see:**
- User mouse movements
- Clicks and interactions
- Page navigations
- Console logs
- Network requests
- Errors in context

### Privacy Considerations

Adjust privacy level as needed:

```javascript
defaultPrivacyLevel: 'mask-user-input'  // Mask sensitive inputs
defaultPrivacyLevel: 'mask'              // Mask all text
defaultPrivacyLevel: 'allow'             // Record everything (current)
```

## Sampling

### Adjust Sampling Rates

For high-traffic applications, reduce sampling:

```javascript
sessionSampleRate: 20,         // Track 20% of sessions
sessionReplaySampleRate: 10,   // Record 10% of sessions
```

**Cost optimization:**
- Lower sampling reduces costs
- Keep 100% for development/staging
- Reduce for production based on traffic

## Troubleshooting

### RUM Data Not Appearing

**Check:**
1. ✅ `DD_RUM_CLIENT_TOKEN` and `DD_RUM_APPLICATION_ID` are set
2. ✅ Streamlit app is running
3. ✅ Browser console shows no RUM errors
4. ✅ Application exists in Datadog

**Debug:**
```bash
# Check environment variables
docker-compose exec streamlit-frontend env | grep DD_RUM

# Check browser console
# Open http://localhost:8501
# Press F12 → Console
# Look for "Datadog RUM" messages
```

### Traces Not Correlating

**Check:**
1. ✅ Backend has Datadog APM enabled
2. ✅ `allowedTracingUrls` includes backend URL
3. ✅ CORS allows trace headers

**Fix:**
```javascript
// Ensure backend URL is in allowedTracingUrls
allowedTracingUrls: [
  {
    match: (url) => url.startsWith("${API_BASE_URL}"),
    propagatorTypes: ["datadog"]
  }
]
```

### High Costs

**Optimize:**
```javascript
sessionSampleRate: 20,          // Reduce from 100
sessionReplaySampleRate: 5,     // Reduce from 100
```

## Monitoring Best Practices

### 1. Set Up Alerts

**High Error Rate:**
```
avg(last_5m):sum:rum.error.count{service:genai-streamlit-frontend}.as_count() > 10
```

**Slow Page Load:**
```
avg(last_5m):avg:rum.loading_time{service:genai-streamlit-frontend} > 5s
```

**High Resource Load Time:**
```
avg(last_5m):p95:rum.resource.duration{service:genai-streamlit-frontend} > 2s
```

### 2. Create Dashboards

Create dashboard with widgets for:
- Session count
- Page views
- Error rate
- Loading time
- Core Web Vitals
- Top errors
- Most visited pages

### 3. Monitor Core Web Vitals

Track these Google metrics:
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

### 4. Track Custom Actions

Add custom tracking in your code:

```python
# Not directly supported in Streamlit
# RUM automatically tracks clicks, inputs, page views
```

## Advanced Configuration

### Custom Context

Add custom data to all RUM events:

```javascript
window.DD_RUM.setGlobalContextProperty('user.plan', 'premium');
window.DD_RUM.setGlobalContextProperty('feature.flags', {
  newUI: true,
  betaFeature: false
});
```

### Track Custom Errors

```javascript
window.DD_RUM.addError(
  new Error('Custom error'),
  {
    context: 'vote-extraction',
    user_action: 'upload'
  }
);
```

## Cost Estimates

**RUM Pricing** (approximate):
- 10,000 sessions/month: Free
- 50,000 sessions/month: ~$31/month
- 100,000 sessions/month: ~$62/month

**Session Replay Pricing**:
- 1,000 replays/month: Free
- 10,000 replays/month: ~$27/month

## Security Notes

**Client Token**:
- ✅ **Public token** - Safe to expose in frontend
- ✅ Can only send RUM data
- ✅ Cannot read data or access Datadog account

**Application ID**:
- ✅ **Public UUID** - Safe to expose
- ✅ Identifies your application

**Not sensitive** - No need for Secret Manager (unlike API keys).

## Resources

- [Datadog RUM Documentation](https://docs.datadoghq.com/real_user_monitoring/)
- [Browser Monitoring](https://docs.datadoghq.com/real_user_monitoring/browser/)
- [Session Replay](https://docs.datadoghq.com/real_user_monitoring/session_replay/)

---

**Quick Start**: Set `DD_RUM_CLIENT_TOKEN` and `DD_RUM_APPLICATION_ID`, restart frontend, and view sessions at https://app.datadoghq.com/rum/sessions 🎉

