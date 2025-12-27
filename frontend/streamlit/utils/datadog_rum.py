"""Datadog RUM initialization for Streamlit."""

import os
import streamlit.components.v1 as components


def init_datadog_rum():
    """
    Initialize Datadog RUM for the current page.
    Call this at the top of each Streamlit page to ensure RUM is enabled.
    """
    # Get RUM configuration from environment
    DD_RUM_CLIENT_TOKEN = os.getenv("DD_RUM_CLIENT_TOKEN", "")
    DD_RUM_APPLICATION_ID = os.getenv("DD_RUM_APPLICATION_ID", "")
    DD_SITE = os.getenv("DD_SITE", "datadoghq.com")
    DD_SERVICE = os.getenv("DD_SERVICE", "genai-streamlit-frontend")
    DD_ENV = os.getenv("DD_ENV", "development")
    DD_VERSION = os.getenv("DD_VERSION", "0.1.0")
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

    # Only inject if both client token and app ID are set
    if not (DD_RUM_CLIENT_TOKEN and DD_RUM_APPLICATION_ID):
        return False

    # Inject Datadog RUM script
    datadog_rum_script = f"""
    <script>
      (function(h,o,u,n,d) {{
        h=h[d]=h[d]||{{q:[],onReady:function(c){{h.q.push(c)}}}}
        d=o.createElement(u);d.async=1;d.src=n
        n=o.getElementsByTagName(u)[0];n.parentNode.insertBefore(d,n)
      }})(window,document,'script','https://www.datadoghq-browser-agent.com/us1/v6/datadog-rum.js','DD_RUM')

      window.DD_RUM.onReady(function() {{
        // Check if already initialized
        if (window.DD_RUM_INITIALIZED) {{
          return;
        }}

        window.DD_RUM.init({{
          clientToken: '{DD_RUM_CLIENT_TOKEN}',
          applicationId: '{DD_RUM_APPLICATION_ID}',
          site: '{DD_SITE}',
          service: '{DD_SERVICE}',
          env: '{DD_ENV}',
          version: '{DD_VERSION}',
          sessionSampleRate: 100,
          sessionReplaySampleRate: 100,
          allowedTracingUrls: [
            (url) => url.startsWith("http://localhost"),
            /^https:\\/\\/[^\\/]+\\.run\\.app/,
            {{
              match: (url) => url.startsWith("{API_BASE_URL}"),
              propagatorTypes: ["datadog"]
            }}
          ],
          trackBfcacheViews: true,
          trackResources: true,
          trackLongTasks: true,
          trackUserInteractions: true,
          defaultPrivacyLevel: 'allow',
        }});

        window.DD_RUM_INITIALIZED = true;
        console.log('[Datadog RUM] Initialized for service:', '{DD_SERVICE}');
      }})
    </script>
    """

    components.html(datadog_rum_script, height=0)
    return True
