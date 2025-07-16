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
            token="6709760095:AAEFW1mipXRWWU8k7hiXCWGsZufyTYG_4Oc",
            chat = "-1002328598165",
            admin_ids=[],
            use_redis=False,
        ),
        db=DbConfig(
            host='',
            password='',
            user='',
            database='',
            db_uri=''
        ),
        misc=Miscellaneous()
    )