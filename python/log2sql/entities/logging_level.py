from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..orm import ORM


class LoggingLevel(ORM.BASE):
    __tablename__ = "logging_levels"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    num = Column("num", Integer)
    name = Column("name", String(20))
    
    logging_events = relationship("LoggingEvent", uselist=True, back_populates="logging_level")