from collections.abc import MutableMapping, Iterable
from .entities import LoggingEvent, LoggingLevel, User
import sqlalchemy

def convert_to_dict_recursive(input, _result={}):
    if isinstance(input, list):
        converted_iterable = input
        for val in input:
            if isinstance(val, dict):
                converted_iterable[input.index(val)] = convert_to_dict_recursive(val, _result)
        return converted_iterable
    elif isinstance(input, dict):     
        for key, val in input.items():
            if isinstance(val, dict):
                _result.update({key: convert_to_dict_recursive(val, _result)})
            elif isinstance(val, LoggingEvent) or isinstance(val, LoggingLevel) or isinstance(val, User) or isinstance(val, sqlalchemy.orm.state.InstanceState):
                _result.update({key: convert_to_dict_recursive(val.__dict__, _result)})
            else:
                _result.update({key: val})
    return _result