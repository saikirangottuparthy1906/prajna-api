from sqlalchemy import Column, Integer, String, Text
from database import Base

class User(Base):
    __tablename__ = "master_user_entity"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(String(20), index=True)
    pwd = Column(Text)