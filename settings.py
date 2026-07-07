from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    aws_region: str
    aws_access_key_id: str
    aws_secret_access_key: str
    sqs_queue_url: str

    resend_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="forbid"
    )


settings = Settings()
