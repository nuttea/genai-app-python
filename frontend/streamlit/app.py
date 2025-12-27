"""Main Streamlit application with multi-page support."""

import streamlit as st
from dotenv import load_dotenv
import os
from utils.datadog_rum import init_datadog_rum

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="GenAI Application Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Datadog RUM (will be available across all pages)
rum_enabled = init_datadog_rum()

# Show RUM initialization status in development
DD_ENV = os.getenv("DD_ENV", "development")
if DD_ENV == "development" and rum_enabled:
    st.success("🌐 Datadog RUM initialized successfully")

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .upload-text {
        font-size: 14px;
        color: #666;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar configuration
with st.sidebar:
    st.title("🤖 GenAI Platform")
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📑 Navigation")
    
    # Debug info (development only)
    DD_ENV = os.getenv("DD_ENV", "development")
    if DD_ENV == "development":
        st.markdown("---")
        with st.expander("🔧 Debug Info", expanded=False):
            DD_RUM_CLIENT_TOKEN = os.getenv("DD_RUM_CLIENT_TOKEN", "")
            DD_RUM_APPLICATION_ID = os.getenv("DD_RUM_APPLICATION_ID", "")
            API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
            DD_SERVICE = os.getenv("DD_SERVICE", "genai-streamlit-frontend")
            DD_VERSION = os.getenv("DD_VERSION", "0.1.0")
            
            st.text(f"Backend: {API_BASE_URL}")
            st.text(f"Service: {DD_SERVICE}")
            st.text(f"Environment: {DD_ENV}")
            st.text(f"Version: {DD_VERSION}")
            st.text(f"RUM Enabled: {rum_enabled}")
            if DD_RUM_CLIENT_TOKEN:
                st.text(f"RUM Token: {DD_RUM_CLIENT_TOKEN[:10]}...")
            if DD_RUM_APPLICATION_ID:
                st.text(f"RUM App ID: {DD_RUM_APPLICATION_ID[:8]}...")
    
# Main page content
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
    
    ### 📝 About
    
    This platform is powered by:
    - FastAPI backend with Google Vertex AI
    - Streamlit for interactive UI
    - Docker for easy deployment
    """
)

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px;'>
        GenAI Application Platform | Built with ❤️ using FastAPI & Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)

