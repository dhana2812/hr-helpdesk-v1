from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openrouter_api_key: str
    openrouter_model: str = "openai/gpt-5.4"

    client_token: str
    client_employee_id: str

    database_path: str = "data/hr_helpdesk.db"
    employee_db_path: str = "data/employees.db"
    log_file: str = "logs/requests.jsonl"

    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
