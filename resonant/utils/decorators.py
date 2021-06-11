import logging
import time
import datetime

def log_execution(logging_help = None):
    def decorator(func):
        nonlocal logging_help
        
        identifier = ""
        if logging_help is None:
            identifier += f"Function {func.__name__}"
        else:
            identifier += f"{logging_help} ({func.__name__})"

        def wrapper(*args, **kwargs):
            start = time.time()
            time_str = datetime.datetime.fromtimestamp(start).strftime("%H:%M:%S:%f")
            logging.debug(f"{identifier} was called at {time_str}")
            result = func(*args, **kwargs)
            end = time.time()
            logging.debug(f"{identifier} execution time: {end-start}")
            
            return result
        return wrapper
    return decorator

