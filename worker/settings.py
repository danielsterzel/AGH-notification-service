from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    aws_region: str
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    sqs_queue_url: str = Field(
        validation_alias=AliasChoices("SQS_QUEUE_URL", "QUEUE_URL")
    )

    smtp_email: str
    smtp_app_password: str
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
