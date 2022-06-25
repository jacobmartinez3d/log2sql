from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Float, Boolean
from sqlalchemy.orm import relationship

from ..orm import ORM


class LoggingEvent(ORM.BASE):
    __tablename__ = "logging_events"
    __table_args__ = {'extend_existing': True}

    # log2sql columns
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    logging_level_id = Column(Integer, ForeignKey("logging_levels.id"))
    
    # logging.LogRecord attribute mapping
    args = Column(JSON(String))
    created = Column(Float)
    exc_info = Column(JSON(String))
    exc_text = Column(String)
    filename = Column(String)
    funcName = Column(String)
    lineno = Column(Integer)
    module = Column(String)
    msecs = Column(Float)
    msg = Column(JSON)
    name = Column(String)
    pathname = Column(String)
    process = Column(Integer)
    processName = Column(String)
    relativeCreated = Column(Float)
    stack_info = Column(Boolean)
    thread = Column(Integer)
    threadName = Column(String)
    
    
    # relationships
    logging_level = relationship("LoggingLevel")
    user = relationship("User", uselist=True, back_populates="logging_events")