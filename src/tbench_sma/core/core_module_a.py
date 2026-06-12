# core/core_module_a.py

from pymodule.logger import get_app_logger

logger = get_app_logger(__name__)

def hello_from_core_module_a() -> int:
    logger.info(
        "Hello from core_module_a")
    return 1

def goodbye_from_core_module_a() -> int:
    logger.info("Goodbye from core_module_a")
    return -1
