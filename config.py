"""
config.py
Centralized configuration management for the Banking Assistant.
Loads settings from environment variables and .env file.
"""

import os
from pathlib import Path
from typing import Any, Optional

try:
    import streamlit as st
except Exception:  # pragma: no cover - streamlit is optional in local scripts
    st = None

# Load .env file if present
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, fall back to environment variables only


def _get_setting(name: str, default: Any = None) -> Any:
    """Read from environment variables or Streamlit secrets when deployed on Streamlit Cloud."""
    value = os.getenv(name)
    if value not in (None, ""):
        return value

    if st is not None and hasattr(st, "secrets"):
        try:
            secrets = st.secrets
            for candidate in (name, name.lower(), name.upper()):
                if candidate in secrets:
                    value = secrets[candidate]
                    if value not in (None, ""):
                        return value
        except Exception:
            pass

    return default


class Config:
    """
    Central configuration management.
    All settings are loaded from environment variables or defaults.
    """

    # ========================================================================
    # LLM Configuration - Groq
    # ========================================================================

    # Groq API settings
    LLM_API_KEY = _get_setting("GROQ_API_KEY", "")
    LLM_MODEL = _get_setting("GROQ_MODEL", "groq/openai/gpt-oss-120b")
    LLM_TEMPERATURE = float(_get_setting("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(_get_setting("LLM_MAX_TOKENS", "4000"))
    LLM_TIMEOUT = int(_get_setting("LLM_TIMEOUT", "30"))

    # ========================================================================
    # Rate Limiting Configuration
    # ========================================================================

    # Qwen model: 1000 RPM limit
    MAX_RPM = int(os.getenv("MAX_RPM", "900"))  # 10% safety buffer
    MIN_REQUEST_INTERVAL = float(os.getenv("MIN_REQUEST_INTERVAL", "0.1"))  # seconds
    RETRY_MAX_ATTEMPTS = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
    RETRY_MIN_WAIT = int(os.getenv("RETRY_MIN_WAIT", "1"))  # seconds
    RETRY_MAX_WAIT = int(os.getenv("RETRY_MAX_WAIT", "10"))  # seconds

    # ========================================================================
    # Database Configuration
    # ========================================================================

    DATABASE_PATH = Path(_get_setting("DATABASE_PATH", "bank_data.db"))
    DATABASE_TYPE = _get_setting("DATABASE_TYPE", "sqlite")

    # ========================================================================
    # Application Configuration
    # ========================================================================

    # Demo account for testing (no authentication)
    DEMO_ACCOUNT_ID = _get_setting("DEMO_ACCOUNT_ID", "ACC001")

    # Streamlit settings
    STREAMLIT_THEME = _get_setting("STREAMLIT_THEME", "light")
    STREAMLIT_PAGE_WIDTH = _get_setting("STREAMLIT_PAGE_WIDTH", "wide")

    # ========================================================================
    # Logging Configuration
    # ========================================================================

    LOG_LEVEL = _get_setting("LOG_LEVEL", "INFO")
    VERBOSE_AGENT_OUTPUT = str(_get_setting("VERBOSE_AGENT_OUTPUT", "true")).lower() == "true"
    LOG_FILE = _get_setting("LOG_FILE", "banking_assistant.log")

    # ========================================================================
    # Validation Methods
    # ========================================================================

    @classmethod
    def validate_llm_config(cls) -> bool:
        """
        Validate that LLM configuration is properly set.

        Returns:
            True if configuration is valid, False otherwise
        """
        if not cls.LLM_API_KEY:
            print("⚠ Warning: GROQ_API_KEY not set in environment")
            return False
        if not cls.LLM_MODEL:
            print("⚠ Warning: GROQ_MODEL not set in environment")
            return False
        return True

    @classmethod
    def validate_database_config(cls) -> bool:
        """
        Validate that database configuration is properly set.

        Returns:
            True if database file exists or can be created, False otherwise
        """
        if cls.DATABASE_TYPE != "sqlite":
            print(f"✗ Error: Unsupported database type: {cls.DATABASE_TYPE}")
            return False

        if not cls.DATABASE_PATH.parent.exists():
            cls.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

        return True

    @classmethod
    def print_config(cls, show_secrets: bool = False) -> None:
        """
        Print current configuration (useful for debugging).

        Args:
            show_secrets: If True, show API keys (use with caution!)
        """
        print("\n" + "=" * 60)
        print("Banking Assistant Configuration")
        print("=" * 60)

        print("\n[LLM]")
        print(f"  Model: {cls.LLM_MODEL}")
        if show_secrets and cls.LLM_API_KEY:
            print(f"  API Key: {cls.LLM_API_KEY[:10]}...")
        else:
            print(f"  API Key: {'SET' if cls.LLM_API_KEY else 'NOT SET'}")
        print(f"  Model route: {cls.LLM_MODEL}")
        print(f"  Temperature: {cls.LLM_TEMPERATURE}")
        print(f"  Max Tokens: {cls.LLM_MAX_TOKENS}")
        print(f"  Timeout: {cls.LLM_TIMEOUT}s")

        print("\n[Rate Limiting]")
        print(f"  Max RPM: {cls.MAX_RPM}")
        print(f"  Min Request Interval: {cls.MIN_REQUEST_INTERVAL}s")
        print(f"  Retry Max Attempts: {cls.RETRY_MAX_ATTEMPTS}")
        print(f"  Retry Backoff: {cls.RETRY_MIN_WAIT}s - {cls.RETRY_MAX_WAIT}s")

        print("\n[Database]")
        print(f"  Type: {cls.DATABASE_TYPE}")
        print(f"  Path: {cls.DATABASE_PATH}")
        print(f"  Exists: {cls.DATABASE_PATH.exists()}")

        print("\n[Application]")
        print(f"  Demo Account: {cls.DEMO_ACCOUNT_ID}")
        print(f"  Verbose Output: {cls.VERBOSE_AGENT_OUTPUT}")
        print(f"  Log Level: {cls.LOG_LEVEL}")

        print("\n" + "=" * 60 + "\n")


# ============================================================================
# Environment Variable Documentation
# ============================================================================

ENVIRONMENT_VARIABLES_DOCUMENTATION = """
Banking Assistant - Environment Variables Reference
=====================================================

LLM Configuration:
  GROQ_API_KEY          - Your Groq API key (REQUIRED)
  GROQ_MODEL            - Groq model name (default: groq/openai/gpt-oss-120b)
  LLM_TEMPERATURE       - Model temperature 0-1 (default: 0.7)
  LLM_MAX_TOKENS        - Max tokens per request (default: 4000)
  LLM_TIMEOUT           - Request timeout in seconds (default: 30)

Rate Limiting:
  MAX_RPM               - Max requests per minute (default: 900)
  MIN_REQUEST_INTERVAL  - Min seconds between requests (default: 0.1)
  RETRY_MAX_ATTEMPTS    - Max retry attempts (default: 3)
  RETRY_MIN_WAIT        - Min wait between retries (default: 1)
  RETRY_MAX_WAIT        - Max wait between retries (default: 10)

Database:
  DATABASE_TYPE         - Database system (default: sqlite)
  DATABASE_PATH         - Database file location (default: bank_data.db)

Application:
  DEMO_ACCOUNT_ID       - Default account for testing (default: ACC001)
  VERBOSE_AGENT_OUTPUT  - Enable verbose output (default: true)
  LOG_LEVEL             - Logging level (default: INFO)
  LOG_FILE              - Log file path (default: banking_assistant.log)

Streamlit:
  STREAMLIT_THEME       - Theme (default: light)
  STREAMLIT_PAGE_WIDTH  - Page width (default: wide)

Example .env file:
  OPENAI_API_KEY=sk-xxx...
  OPENAI_API_BASE=https://api.provider.com/v1
  MAX_RPM=900
  LOG_LEVEL=INFO
"""


if __name__ == "__main__":
    # Print documentation
    print(ENVIRONMENT_VARIABLES_DOCUMENTATION)

    # Validate and print current configuration
    print("\nCurrent Configuration:")
    Config.print_config(show_secrets=False)

    # Validate configuration
    print("Configuration Validation:")
    llm_valid = Config.validate_llm_config()
    db_valid = Config.validate_database_config()

    if llm_valid and db_valid:
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration has issues (see warnings above)")
