import logging
import os
from dotenv import load_dotenv

from yarl import URL


load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
    handlers=[logging.StreamHandler()],
)


class Config:
    """
    Base configuration class.
    """
    DEBUG = True
    TESTING = True
    KEY_DIR = "keys"
    PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "embedded-example-private-key.pem")
    PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "embedded-example-public-key.pem")


class LocalConfig(Config):
    """
    Development configuration.
    """
    API_TOKEN = os.environ.get("LOCAL_API_TOKEN")
    API_SECRET = os.environ.get("LOCAL_API_SECRET")
    KEY_ID = os.environ.get("LOCAL_KEY_ID")
    PRESET_BASE_URL = URL(os.environ.get("LOCAL_PRESET_BASE_URL"))
    PRESET_TEAM_ID = os.environ.get("LOCAL_PRESET_TEAM_ID")
    WORKSPACE_SLUG = os.environ.get('LOCAL_WORKSPACE_SLUG')
    SUPERSET_DOMAIN = URL(os.environ.get('LOCAL_SUPERSET_DOMAIN'))
    DASHBOARD_ID = os.environ.get('LOCAL_DASHBOARD_ID')


class SdxConfig(Config):
    """
    Sandbox configuration.
    """
    API_TOKEN = os.environ.get("SDX_API_TOKEN")
    API_SECRET = os.environ.get("SDX_API_SECRET")
    KEY_ID = os.environ.get("SDX_KEY_ID")
    PRESET_BASE_URL = URL(os.environ.get("SDX_PRESET_BASE_URL"))
    PRESET_TEAM_ID = os.environ.get("SDX_PRESET_TEAM_ID")
    WORKSPACE_SLUG = os.environ.get('SDX_WORKSPACE_SLUG')
    SUPERSET_DOMAIN = URL(os.environ.get('SDX_SUPERSET_DOMAIN'))
    DASHBOARD_ID = os.environ.get('SDX_DASHBOARD_ID')


class StgConfig(Config):
    """
    Staging configuration.
    """
    API_TOKEN = os.environ.get("STG_API_TOKEN")
    API_SECRET = os.environ.get("STG_API_SECRET")
    KEY_ID = os.environ.get("STG_KEY_ID")
    PRESET_BASE_URL = URL(os.environ.get("STG_PRESET_BASE_URL"))
    PRESET_TEAM_ID = os.environ.get("STG_PRESET_TEAM_ID")
    WORKSPACE_SLUG = os.environ.get('STG_WORKSPACE_SLUG')
    SUPERSET_DOMAIN = URL(os.environ.get('STG_SUPERSET_DOMAIN'))
    DASHBOARD_ID = os.environ.get('STG_DASHBOARD_ID')


class ProdConfig(Config):
    """
    Production configuration.
    """
    API_TOKEN = os.environ.get("API_TOKEN")
    API_SECRET = os.environ.get("API_SECRET")
    KEY_ID = os.environ.get("KEY_ID")
    PRESET_BASE_URL = URL(os.environ.get("PRESET_BASE_URL"))
    PRESET_TEAM_ID = os.environ.get("PRESET_TEAM_ID")
    WORKSPACE_SLUG = os.environ.get('WORKSPACE_SLUG')
    SUPERSET_DOMAIN = URL(os.environ.get('SUPERSET_DOMAIN'))
    DASHBOARD_ID = os.environ.get('DASHBOARD_ID')

# Configuration mapping
config = {
    "development": LocalConfig,
    "sandbox": SdxConfig,
    "staging": StgConfig,
    "production": ProdConfig,
}
