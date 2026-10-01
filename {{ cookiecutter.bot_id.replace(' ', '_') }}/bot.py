"""BeaPro Automation Outline

This is the main automation file that orchestrates the bot execution flow.
It handles initialization, item processing, exception handling, and finalization.

To customize your automation:
- Adjust initialization settings in framework/initialize.py
- Add your automation steps in the process_item() function located in framework/process.py
- Configure your data source in framework/datasources.py

The BeaPro framework automatically handles:
- System exceptions (technical failures with restart capability)
- Interruption requests from BotCity Orchestrator
- Success/error reporting and alerting
- Logging, and more. Check the README.md for more information.
"""

import logging

from framework.datasources import data_source
from framework.exceptions import BusinessException, InterruptException
from framework.finalize import cleanup, finalize
from framework.initialize import initialize
from framework.process import process_item
from framework.status_handling import (
    handle_business_exception,
    handle_interrupt_requested,
    handle_system_exception,
    register_success,
)

logger = logging.getLogger(__name__)


def action():
    try:
        initialize()

        for item in data_source:

            try:
                result_message = process_item(item)
            except InterruptException as ex:
                handle_interrupt_requested(ex)
            except BusinessException as ex:
                handle_business_exception(ex)
            except Exception as ex:
                handle_system_exception(ex)
                initialize(restart=True)
            else:
                register_success(
                    f"Item processed successfully: {result_message}")

    except Exception as ex:
        logger.error(f"Error: {ex}")

    finally:
        cleanup()
        finalize()


if __name__ == "__main__":
    action()
