from monolog.config import MonologConfig, Node, Connection
from pydantic import BaseModel


class Monolog(MonologConfig):
    connection: Connection = Connection(
        serv="localhost",
        port=27017,
        username="USERNAME",
        auth_source="AUTH_SOURCE",
        auth_mechanism="SCRAM-SHA-1",
        password="PASSWORD",
        database="DATABASE",
    )
    current_level: str = "debug"
    mongo_logger_duplicate: bool = False
    std_logger_duplicate: bool = True
    node: Node = Node(
        host="myService",
        ip="127.0.0.1",
    )

class PostgresCore(BaseModel):
    USER: str = 'login'
    PASSWORD: str = 'pass'
    DB: str = 'core'
    HOST: str = 'pgslave.generic.deac'
    PORT: int = 5432

    def build_url(self) -> str:
        return f'postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}'  # noqa: WPS221, E501

class PostgresStats(BaseModel):
    USER: str = 'login'
    PASSWORD: str = 'pass'
    DB: str = 'stats'
    HOST: str = 'pg01.generic.deac'
    PORT: int = 5432

    def build_url(self) -> str:
        return f'postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}'  # noqa: WPS221, E501

class Settings(BaseModel):
    WEB_APP_HOST: str = "0.0.0.0"
    WEB_APP_PORT: int = 8080
    POSTGRES_STATS: PostgresStats = PostgresStats()
    POSTGRES_CORE: PostgresCore = PostgresCore()
    LOGGER: Monolog = Monolog()
    PROJECT_NAME: str = "kowalski"



settings = Settings()
