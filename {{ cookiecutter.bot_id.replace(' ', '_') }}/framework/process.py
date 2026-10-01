"""
process.py
    Add the steps to your automation process here.
"""

import logging

from .exceptions import BusinessException, InterruptException, SystemException
from .state import STATE

logger = logging.getLogger(__name__)


def process_item(item):
    """
    Runs the steps of the automation process for each item and checks if the process has received an interruption request from the BotCity Orchestrator.
    """
    STATE.raise_for_interrupt_requested()

    logger.info(f"Item processing has started: {item}.")
    bot = STATE.webbot

    # Your code here
    ...

    result_message = f"Processing successful for item {item}."
    return result_message
