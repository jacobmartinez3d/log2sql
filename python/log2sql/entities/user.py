from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..orm import ORM


class User(ORM.BASE):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    alias = Column(String(16))
    first_name = Column(String(16))
    last_name = Column(String(32))

    logging_events = relationship("LoggingEvent")