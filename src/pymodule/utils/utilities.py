# utils/utilities.py

from pymodule.logger import get_app_logger

logger = get_app_logger(__name__)

def hello_from_utils() ->  None:
    logger.info("Hello from utils")

# this function is used to demonstrate unittest and pytest styles of unit testing
def sumator(a:int, b:int, c:int) -> int:
    return a + b + c
