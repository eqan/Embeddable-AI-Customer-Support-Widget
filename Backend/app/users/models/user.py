from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime
from .enums import UserType
from base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False, default=UserType.REGULAR_USER.value)
    blackListed = Column(Boolean, nullable=False, default=False)
    profile_url = Column(String, nullable=True, default=None)   
    last_time_service_used = Column(DateTime, nullable=True, default=None)
    notes = Column(Text, nullable=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
