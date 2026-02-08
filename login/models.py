from sqlalchemy import Column, Integer, String, Float
from database import Base

class User(Base):
    __tablename__ = "logins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=True)
    address = Column(String, nullable=True)
