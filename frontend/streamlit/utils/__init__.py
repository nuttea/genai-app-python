"""Utility functions for Streamlit frontend."""

from utils.config import get_config
from utils.datadog_rum import init_datadog_rum

__all__ = ["init_datadog_rum", "get_config"]
