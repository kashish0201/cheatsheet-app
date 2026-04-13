from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "CheatSheet API"
    ENV: str = "dev"
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
