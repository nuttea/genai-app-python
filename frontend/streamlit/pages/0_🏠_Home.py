"""Home page (duplicate of main app for multi-page navigation)."""

import os
import sys

import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.datadog_rum import init_datadog_rum

st.set_page_config(
    page_title="Home - GenAI Platform",
    page_icon="🏠",
    layout="wide",
)

# Initialize Datadog RUM
rum_enabled = init_datadog_rum()

# Page content
st.title("Welcome to GenAI Application Platform")
st.markdown(
    """
    ### 👋 Getting Started

    Use the sidebar menu to navigate between different tools:

    - **🗳️ Vote Extractor** - Extract data from Thai election forms (Form S.S. 5/18)
    - More tools coming soon...

    ### 🚀 Features

    - **Multi-page Document Processing** - Upload multiple pages and get consolidated results
    - **Structured Data Extraction** - Get JSON-formatted data ready for analysis
    - **Real-time Processing** - See results as they're extracted
    - **Data Export** - Download as CSV or JSON
    - **Multi-report Support** - Process multiple reports in one batch

    ### 🔐 Security

    - API key authentication for secure access
    - Google Cloud Secret Manager integration
    - Application Default Credentials for GCP

    ### 📊 Monitoring

    - **Backend APM** - Full request tracing with Datadog
    - **LLM Observability** - Track all AI model calls
    - **Frontend RUM** - Real user monitoring
    - **Session Replay** - Watch user sessions
    - **Distributed Tracing** - End-to-end visibility

    ### 📝 About

    This platform is powered by:
    - **FastAPI** backend with Google Vertex AI (Gemini 2.5 Flash)
    - **Streamlit** for interactive UI
    - **Poetry** for dependency management
    - **Docker** for easy deployment
    - **Datadog** for complete observability

    ### 🔗 Quick Links

    - **API Documentation**: http://localhost:8000/docs
    - **Backend Health**: http://localhost:8000/health
    - **GitHub**: [Project Repository](#)
    """
)

# Show RUM status in development
DD_ENV = os.getenv("DD_ENV", "development")
if DD_ENV == "development" and rum_enabled:
    st.info("🌐 Datadog RUM is enabled - User sessions are being monitored")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px;'>
        GenAI Application Platform | Built with ❤️ using FastAPI, Streamlit & Google Vertex AI
    </div>
    """,
    unsafe_allow_html=True,
)
