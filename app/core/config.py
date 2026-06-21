
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
        )
    
    PROJECT_NAME: str = Field(default="StudyRAG API")
    VERSION: str = Field(default="1.0.0")
    API_V1_STR: str = Field(default="/api/v1")
    ENVIRONMENT: str = Field(default="development")


    POSTGRES_USER: str = Field(default = "localhost")
    POSTGRES_PASSWORD: str = Field(default = "password")
    POSTGRES_DB: str = Field(default = "studyrag_db")
    POSTGRES_PORT: int = Field(default = 5432)


    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    

    GEMINI_API_KEY: str = Field(default="")

settings = Settings()