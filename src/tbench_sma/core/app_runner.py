# app_runner.py

from importlib.metadata import version as pkg_version

import tbench_sma
from tbench_sma.core.config import Config
from tbench_sma.logger import get_app_logger
from tbench_sma.core.ms_host import MShost

logger = get_app_logger(__name__)

# CLI application main function with collected options & configuration
def run_app(cfg:Config) -> None:
    try:
        # Add real application code here.
        logger.info("Running run_app")
        logger.info("config = %s",str(cfg.config))
        tbench_sma.hello_from_core_module_a()
        tbench_sma.goodbye_from_core_module_a()
        tbench_sma.hello_from_core_module_b()
        tbench_sma.goodbye_from_core_module_b()
        tbench_sma.hello_from_utils()

    except ValueError as e:
        raise e
    except Exception as e:
        raise e
    finally:
        logger.info("Exiting run_app")
