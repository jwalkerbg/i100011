# drivers/ina236.py

from pymodule.logger import get_app_logger

logger = get_app_logger(__name__)

def hello_from_ina236() -> None:
    logger.info("Hello from ina236")
