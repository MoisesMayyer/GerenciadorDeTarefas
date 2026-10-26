from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Origens autorizadas a chamar a API (separadas por vírgula).
    # O padrão é apenas o frontend publicado no GitHub Pages.
    # Para desenvolvimento local, adicione as origens em backend/.env.
    CORS_ORIGINS: str = "https://moisesmayyer.github.io"

    @property
    def cors_origins(self) -> list[str]:
        return [
            origem.strip()
            for origem in self.CORS_ORIGINS.split(",")
            if origem.strip()
        ]


settings = Settings()  # noqa
