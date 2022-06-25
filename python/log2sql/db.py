from .orm import ORM
from .enums import OperationType
from .entities import User, LoggingEvent, LoggingLevel

from pprint import pprint

class DB(ORM):
    
    __operation_callables__ = [
        "create",
        "read",
        "update",
        "delete"
    ]
    def batch(self, instructions):
        results = []
        for instruction in instructions:
            operation_enum_value = instruction["operation"]
            entity = instruction["entity"]
            data = instruction["data"]

            operation_callable = self.__operation_callables__[operation_enum_value]
            results.append(operation_callable(entity, data))
        return results
    
    def submit_new_logging_event(self, log_record, username):
        self.LOGGER.info("Submitting new logging event...")
        # create or retreive existing `User`-record
        user_query = self.query(User,
            {
                "alias": username
            }
        )
        user_record = user_query.first()
        if user_record:
            self.LOGGER.info("User '{user_record.alias}' already exists, skipping creation.")
        else:
            user_record = self.create(User,
                {
                    "alias": username
                }
            )
            self.LOGGER.info("Creating user: {user_record.alias}".format(user_record=user_record))
            self.LOGGER.debug(user_record.__dict__)

        # retrieve `LoggingEvent`-record
        logging_level_record = self.query(LoggingLevel, num=log_record["levelno"]).first()
        if not logging_level_record:
            self.LOGGER.warning("No database-model for `LoggingLevel` with `levelno`: {levelno}".format(levelno=log_record["levelno"]))
            self.LOGGER.warning("Creating `LoggingLevel` record: {levelname} ({levelno})".format(levelname=log_record["levelname"], levelno=log_record["levelno"]))
            logging_level_record = self.create(LoggingLevel,
                {
                    "name":log_record["levelname"],
                    "num": log_record["levelno"]
                }
            )

        # generate an instruction-dict for new `LoggingEvent` record
        logging_event_data = log_record
        if "levelno" in logging_event_data:
            del logging_event_data["levelno"]
        if "levelname" in logging_event_data:
            del logging_event_data["levelname"]
        logging_event_data["user_id"] = user_record.id
        logging_event_data["logging_level_id"] = logging_level_record.id
        self.create(LoggingEvent, logging_event_data)
