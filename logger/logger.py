from datetime import datetime
from functools import wraps

from config.config import Config_


class DictLog:
    def __init__(self, name, args=None, kwargs=None, result=None):
        self.date_time = datetime.now()
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.result = result

    def __str__(self):
        dt = self.date_time.strftime("%Y-%m-%d %H:%M:%S")
        return f'[{dt}] функция: {self.name} - args = {self.args}, {self.kwargs} - функция возвращает {self.result} \n'


def write_file(path, log: DictLog):
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(str(log))
    except Exception as e:
        print(f'Не возможно записать файл {path}: error - {e}')


def logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        dict_log = DictLog(func.__name__, args, kwargs)
        result = func(*args, **kwargs)
        dict_log.result = result
        write_file(Config_.get_path_file_log(), dict_log)
        return result
    return wrapper

def logger_func(path):
    def logger(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            dict_log = DictLog(func.__name__, args, kwargs)
            result = func(*args, **kwargs)
            dict_log.result = result
            write_file(path, dict_log)
            return result
        return wrapper
    return logger

def logger_func_flag(path, flag_args=True):
    def logger(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if flag_args:
                dict_log = DictLog(func.__name__, args, kwargs)
            else:
                dict_log = DictLog(func.__name__)
            result = func(*args, **kwargs)
            dict_log.result = result
            write_file(path, dict_log)
            return result
        return wrapper
    return logger