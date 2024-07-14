from datetime import datetime

from sqlalchemy import Integer, Column, VARCHAR, BigInteger, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    connection_date = Column(DateTime, default=datetime.now, nullable=False)
    tg_id = Column(BigInteger, nullable=False)
    api_pub = Column(VARCHAR(255), nullable=True)
    api_secret = Column(VARCHAR(255), nullable=True)

    def __repr__(self):
        return self.tg_id
