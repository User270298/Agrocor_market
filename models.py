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
    region = Column(String, index=True)  # область
    district = Column(String, index=True)  # район
    city = Column(String, index=True)  # населенный пункт
    date_at = Column(DateTime, index=True)
    volume = Column(Integer, index=True)
    price = Column(Integer)
    status = Column(String, index=True)
    vat_required = Column(String, default='No', index=True)  # работа с НДС
    other_quality = Column(String, nullable=True)  # другие показатели

    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    user = relationship('Users', back_populates='products_buy')


class ProductSell(Base):
    __tablename__ = 'product_sell'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    region = Column(String, index=True)  # область
    district = Column(String, index=True)  # район
    city = Column(String, index=True)  # населенный пункт
    date_at = Column(DateTime, index=True)
    volume = Column(Integer, index=True)
    price = Column(Integer)
    status = Column(String, index=True)
    vat_required = Column(String, default='No', index=True)  # работа с НДС
    other_quality = Column(String, nullable=True)  # другие показатели в свободной форме

    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    user = relationship('Users', back_populates='products_sell')


# from sqlalchemy import create_engine, text

# # Подключение к базе данных
# engine = create_engine('sqlite:///agrocor.db')

# # Добавление столбца
# with engine.connect() as conn:
#     conn.execute(text("ALTER TABLE product_buy ADD COLUMN volume INTEGER"))
#     conn.execute(text("ALTER TABLE product_sell ADD COLUMN volume INTEGER"))
#     conn.commit()