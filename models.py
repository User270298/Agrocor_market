from database import Base, engine
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    telephon = Column(String)
    telegram_id = Column(BigInteger)

    products_buy = relationship('ProductBuy', back_populates='user')
    products_sell = relationship('ProductSell', back_populates='user')

class ProductBuy(Base):
    __tablename__ = 'product_buy'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(String)
    date_at = Column(DateTime)
    price_up = Column(Integer)
    price_down = Column(Integer)
    price_middle = Column(Integer)
    status = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('Users', back_populates='products_buy')

class ProductSell(Base):
    __tablename__ = 'product_sell'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(String)
    date_at = Column(DateTime)
    price_up = Column(Integer)
    price_down = Column(Integer)
    price_middle = Column(Integer)
    status = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('Users', back_populates='products_sell')