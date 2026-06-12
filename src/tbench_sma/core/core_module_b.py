# core/core_module_b.py

from pymodule.logger import get_app_logger

logger = get_app_logger(__name__)

def hello_from_core_module_b() -> int:
    logger.info("Hello from core_module_b")
    return 2

def goodbye_from_core_module_b() -> int:
    logger.info("Goodbye from core_module_b")
    return -2
