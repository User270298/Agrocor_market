from database import Base, engine
from sqlalchemy import Column, Integer, String


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name= Column(String)
    telephon = Column(String)
    telegram_id = Column(Integer)

class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Integer)
    image = Column(String)



