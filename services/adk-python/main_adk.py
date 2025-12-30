"""
Main ADK FastAPI application using get_fast_api_app().

Full ADK implementation - use this instead of app/main.py for pure ADK deployment.
"""

import logging
import os
from pathlib import Path

from ddtrace.llmobs import LLMObs
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Datadog LLM Observability
DD_API_KEY = os.getenv("DD_API_KEY")
DD_SITE = os.getenv("DD_SITE", "datadoghq.com")
DD_ENV = os.getenv("DD_ENV", "development")
DD_SERVICE = os.getenv("DD_SERVICE", "adk-python")
DD_VERSION = os.getenv("DD_VERSION", "1.0.0")

if DD_API_KEY:
    try:
        LLMObs.enable(
            ml_app="adk-python-content-creator",
            api_key=DD_API_KEY,
            site=DD_SITE,
            agentless_enabled=True,
            env=DD_ENV,
            service=DD_SERVICE,
        )
        logger.info(f"Datadog LLM Observability enabled: ml_app=adk-python-content-creator")
    except Exception as e:
        logger.warning(f"Failed to enable Datadog LLM Observability: {e}")

# ADK Configuration
# Point to parent directory (this file's directory) which contains 'agents' subdirectory
BASE_DIR = Path(__file__).parent
AGENTS_DIR = str(BASE_DIR)  # Parent directory containing agents/
# For session storage, use SQLite URI format
SESSION_SERVICE_URI = os.getenv("SESSION_SERVICE_URI", f"sqlite:///{BASE_DIR}/sessions.db")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8501").split(
    ","
)
SERVE_WEB_INTERFACE = os.getenv("SERVE_WEB_INTERFACE", "true").lower() == "true"

logger.info(f"ADK Agents directory: {AGENTS_DIR}")
logger.info(f"ADK Session service URI: {SESSION_SERVICE_URI}")
logger.info(f"ADK Web interface: {SERVE_WEB_INTERFACE}")

# Create FastAPI app using ADK's get_fast_api_app
# Per https://dev.to/timtech4u/building-ai-agents-with-google-adk-fastapi-and-mcp-26h7
# and https://github.com/google/adk-python/issues/1025
# agents_dir should point to parent directory containing agent subdirectories
app: FastAPI = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

logger.info("ADK Python Service started with get_fast_api_app()")

# Verify agent loading
try:
    from content_creator_agent.agent import root_agent

    logger.info(f"✅ Agent loaded: {root_agent.name} with {len(root_agent.tools)} tools")
except Exception as e:
    logger.error(f"❌ Failed to load agent: {e}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Used by Cloud Run, GKE, and load balancers to verify service health.
    """
    return {
        "status": "healthy",
        "service": DD_SERVICE,
        "version": DD_VERSION,
        "adk": "enabled",
    }


# Register shutdown handler for LLMObs flush
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down ADK Python Service")

    if DD_API_KEY:
        try:
            LLMObs.flush()
            logger.info("Flushed Datadog LLM Observability data")
        except Exception as e:
            logger.warning(f"Failed to flush LLM Observability data: {e}")


if __name__ == "__main__":
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = [f"0.0.0.0:{os.getenv('PORT', '8002')}"]
    config.worker_class = "asyncio"

    asyncio.run(serve(app, config))
