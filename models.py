from database import Base, engine
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    telephon = Column(String)
    telegram_id = Column(BigInteger, unique=True, index=True)
    subscribe = Column(String, default='No')

    __table_args__ = (Index('idx_users_subscribe', 'subscribe'),)
    products_buy = relationship('ProductBuy', back_populates='user')
    products_sell = relationship('ProductSell', back_populates='user')


class ProductBuy(Base):
    __tablename__ = 'product_buy'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    location = Column(String, index=True)
    basis = Column(String, index=True)
    date_at = Column(DateTime, index=True)
    price = Column(Integer)
    status = Column(String, index=True)

    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    user = relationship('Users', back_populates='products_buy')


class ProductSell(Base):
    __tablename__ = 'product_sell'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    location = Column(String, index=True)
    basis = Column(String, index=True)
    date_at = Column(DateTime, index=True)
    price = Column(Integer)
    status = Column(String, index=True)

    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    user = relationship('Users', back_populates='products_sell')
