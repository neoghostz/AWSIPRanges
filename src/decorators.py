import logging
import os

logging.basicConfig(format='%(asctime)s [%(levelname)s] (%(funcName)s) %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger('Builder.decorator')
logger.setLevel(int(os.environ.get('Logging', logging.DEBUG)))

def func_call_logger(func):
    def logger_wrapper(*args, **kwargs):
        logger.info(f'Calling {str(func)}')
        return_value = func(*args, **kwargs)
        logger.info(f'Finished {str(func)}')

        return return_value

    return logger_wrapper
