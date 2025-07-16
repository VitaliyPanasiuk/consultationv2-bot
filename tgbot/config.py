from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    db_uri: str


@dataclass
class TgBot:
    token: str
    chat: str
    admin_ids: list[int]
    use_redis: bool


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token="5257942822:AAFqBBqGZs6UJZsF3fJ6fY-f8pCFQelxXRw",
            chat = "-1002403424723",
            admin_ids=[],
            use_redis=False,
        ),
        db=DbConfig(
            host='localhost',
            password='2545',
            user='postgres',
            database='consultant-bot',
            db_uri=''
        ),
        misc=Miscellaneous()
    )