from pydantic import BaseModel
from pydantic_settings import BaseSettings
import logging
# from app.core.logging_setup import setup_root_logger

class DatabaseConfig(BaseModel):
    """Backend database configuration parameters.

    Attributes:
        dsn:
            DSN for target database.
    """
    dsn: str = f"postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/postgres" #TODO get from env not working
    # dsn: str = "postgresql://user:password@host:port/dbname"


class CeleryConfig(BaseModel):
    REDIS_HOST: str = ""
    REDIS_PORT: str = ""
    REDIS_DB: str = "0"
    CELERY_BROKER_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    CELERY_RESULT_BACKEND: str = ""
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_EVENT_SERIALIZER: str = "json"
    CELERY_VISIBILITY_TIMEOUT:int = 1209600

class MailBoxConfig(BaseModel):
    login: str = ""
    password: str = ""


class Config(BaseSettings):
    """API configuration parameters.

    Automatically read modifications to the configuration parameters
    from environment variables and ``.env`` file.

    Attributes:
        database:
            Database configuration settings.
            Instance of :class:`app.backend.config.DatabaseConfig`.
        token_key:
            Random secret key used to sign JWT tokens.
    """

    debug: bool = True
    database: DatabaseConfig = DatabaseConfig()
    mail: MailBoxConfig = MailBoxConfig()
    token_key: str = ""
    backend_url: str = ""
    qr_time:int = 300
    qr_delivery:int = 86400
    celery: CeleryConfig = CeleryConfig()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "MYAPI_"
        env_nested_delimiter = "__"
        case_sensitive = False


config = Config()
# setup_root_logger()

# Get logger for module
# logger = logging.getLogger(__name__)