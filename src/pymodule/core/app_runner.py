# app_runner.py

from importlib.metadata import version as pkg_version

import pymodule
from pymodule.core.config import Config
from pymodule.logger import get_app_logger

logger = get_app_logger(__name__)

# CLI application main function with collected options & configuration
def run_app(cfg:Config) -> None:
    try:
        # Add real application code here.
        logger.info("Running run_app")
        logger.info("config = %s",str(cfg.config))
        pymodule.hello_from_core_module_a()
        pymodule.goodbye_from_core_module_a()
        pymodule.hello_from_core_module_b()
        pymodule.goodbye_from_core_module_b()
        pymodule.hello_from_utils()
        pymodule.hello_from_ina236()
        pymodule.hello_from_ina236()

    except ValueError as e:
        raise e
    except Exception as e:
        raise e
    finally:
        logger.info("Exiting run_app")

