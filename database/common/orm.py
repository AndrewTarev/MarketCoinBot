from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from database.common.models import Base, User
from settings import settings


engine = create_engine(
    url=settings.DATABASE_URL_psycopg, echo=False
)  # создаем движок для подключения к БД
Base.metadata.create_all(engine)  # создает таблицы
session_factory: sessionmaker[Session] = sessionmaker(
    bind=engine
)  # "фабрика сессий" используем для транзакции к бд


class OrmFunc:
    @staticmethod
    def add_user(tg_id):
        with session_factory() as session:
            user = session.query(User).filter(User.tg_id == tg_id).first()
            if user is None:
                new_user = User(tg_id=tg_id)
                session.add(new_user)  # Добавляем объект
                session.commit()

    @staticmethod
    def add_api_pub_DB(tg_id, api_pub):
        with session_factory() as session:
            user = session.query(User).filter(User.tg_id == tg_id).first()
            user.api_pub = api_pub
            session.commit()

    @staticmethod
    def add_api_secret_DB(tg_id, api_secret):
        with session_factory() as session:
            user = session.query(User).filter(User.tg_id == tg_id).first()
            user.api_secret = api_secret
            session.commit()

    @staticmethod
    def remove_api_keys(tg_id):
        with session_factory() as session:
            session.query(User).filter(User.tg_id == tg_id).update({User.api_pub: None})
            session.query(User).filter(User.tg_id == tg_id).update(
                {User.api_secret: None}
            )
            session.commit()

    @staticmethod
    def get_api_keys(tg_id):
        with session_factory() as session:
            user = session.query(User).filter(User.tg_id == tg_id).one_or_none()
            return user.api_pub, user.api_secret
