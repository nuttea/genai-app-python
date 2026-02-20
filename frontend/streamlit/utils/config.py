"""Shared configuration utilities."""

import os

import streamlit as st


def get_config(key: str, default: str = "") -> str:
    """
    Get configuration from environment or secrets, with graceful fallback.

    Priority:
    1. Environment variable (Cloud Run, Docker Compose)
    2. Streamlit secrets.toml (local development, optional)
    3. Default value

    Args:
        key: Configuration key name
        default: Default value if not found

    Returns:
        Configuration value
    """
    # First try environment variable (preferred)
    env_value = os.getenv(key)
    if env_value:
        return env_value

    # Then try secrets.toml (for local development only)
    if hasattr(st, "secrets") and st.secrets:
        try:
            secrets_dict = dict(st.secrets)
            if key in secrets_dict:
                return secrets_dict[key]
        except Exception:
            pass

    return default
