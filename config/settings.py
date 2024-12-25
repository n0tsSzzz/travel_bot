from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    BOT_WEBHOOK_URL: str

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    RABBIT_HOST: str
    RABBIT_PORT: int
    RABBIT_USER: str
    RABBIT_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: str

    USER_ITEMS_QUEUE_TEMPLATE: str = "user_items.{user_id}"
    USER_TRIPS_QUEUE_TEMPLATE: str = "user_trips.{user_id}"
    USER_MESSAGES_QUEUE: str = "user_messages"
    USER_EXCHANGE: str = "user_items"

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def rabbit_url(self) -> str:
        return f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASSWORD}@{self.RABBIT_HOST}:{self.RABBIT_PORT}/"

    class Config:
        env_file = "config/.env"


settings = Settings()
