import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")
    db_name: str = os.getenv("DB_NAME", "reviews")
    db_host: str = os.getenv("DB_HOST", "db")
    db_port: str = os.getenv("DB_PORT", "5432")
    rabbit_host: str = os.getenv("RABBIT_HOST", "rabbitmq")
    rabbit_port: int = int(os.getenv("RABBIT_PORT", "5672"))
    rabbit_user: str = os.getenv("RABBIT_USER", "guest")
    rabbit_password: str = os.getenv("RABBIT_PASSWORD", "guest")
    rabbit_queue: str = os.getenv("RABBIT_QUEUE", "reviews")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
