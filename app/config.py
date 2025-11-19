from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://snore_detection_user:Ry98Slov1TgLQeqJvqNAMYSMPvO2phHT@dpg-d4bqlqeuk2gs73devtv0-a/snore_detection"
    
    # JWT
    JWT_SECRET: str = "Q7mF2tW9xP3rL6vA8jC4nS1bT5hK0gZ"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Raspberry Pi
    RASPI_API_URL: str = "https://flexizantisnore.online"
    RASPI_API_KEY: str = "R7mP4xQ2kH9tF3wB8jT6nY4cV2sL5pA"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: str = "https://anti-snore-front.vercel.app,http://192.168.1.27:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

