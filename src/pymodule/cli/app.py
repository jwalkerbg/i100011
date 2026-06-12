# src/cli/app.py

from importlib.metadata import version as pkg_version

import pymodule
from pymodule.core.config import get_app_configuration
from pymodule.logger import get_app_logger, setup_logging
from pymodule.core.app_runner import run_app

logger = get_app_logger(__name__)

def main() -> None:
    """Main entry point of the CLI."""

    try:
        # Step 1: Collect configuration from defaults, configuration file, and environment variables and CLI options
        cfg = get_app_configuration()
        # Step 2: Setup logging according to collected configuration
        setup_logging(cfg.config['logging']['verbose'], cfg.config['logging']['log_prefix'], cfg.config['logging']['use_color'], cfg.config['logging']['use_string_handler'])

        # Step 3: Show version info or run the application with collected configuration
        if cfg.config['logging']['version_option']:
            # Step 3a: Show version information
            logger.info("Version information requested")
            app_version = pkg_version("pymodule")
            print(f"pymodule {app_version}")
        else:
            # Step 3b: Run the application with the collected configuration
            run_app(cfg)
    except Exception as e:
        logger.error("Application terminated: %s", str(e), exc_info=False)

if __name__ == "__main__":
    main()
