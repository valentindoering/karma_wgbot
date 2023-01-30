import yaml
import time
import sys
import traceback

class Config():
    def __init__(self, config_file: str):
        self.config = yaml.load(open(config_file), Loader=yaml.FullLoader)

    def get(self, key: str):
        return self.config[key]

class CSVLogger():
    def __init__(self, file_name: str):
        self._file_name = file_name

    def log(self, message: str):
        with open(self._file_name, 'a') as f:
            f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")},{message}')

def on_error_send_traceback(log_func):
    def on_error_send_traceback_decorator(function):
        def wrapper_function(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as err:
                # traceback.print_tb(err.__traceback__)
                etype, value, tb = sys.exc_info()
                max_stack_number = 300
                traceback_string = ''.join(traceback.format_exception(etype, value, tb, max_stack_number))
                log_func('Exception in ' + function.__name__ + '\n' + traceback_string)

        return wrapper_function
    return on_error_send_traceback_decorator