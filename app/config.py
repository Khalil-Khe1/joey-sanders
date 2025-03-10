from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LOCALHOST : str
    PORT : str
    HTTP_PROTOCOL : str
    UPLOADS : str
    SQL_URI : str

    class Config:
        env_file = ".env"

settings = Settings()
