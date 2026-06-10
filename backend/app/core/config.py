from typing import Optional
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
    # dsn: str = f"postgresql+psycopg2://postgres:postgres@postgres/difimages" #TODO get from env not working
    dsn: str = "postgresql://user:password@host:port/dbname"


class S3Config(BaseModel):
    bucket_name: str = None
    region_name: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None
    endpoint_url: Optional[str] = None
    default_acl: str = "private"
    expiration: int = 3600


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
    model_path: str = "models/resnet50_embedding.onnx"
    database: DatabaseConfig = DatabaseConfig()
    s3_enable: bool = False
    s3_confif: S3Config = S3Config()


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "MYAPI_"
        env_nested_delimiter = "__"
        case_sensitive = False
        extra = 'ignore'


config = Config()
# setup_root_logger()

# Get logger for module
# logger = logging.getLogger(__name__)
