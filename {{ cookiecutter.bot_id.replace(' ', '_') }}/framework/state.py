from dataclasses import dataclass, asdict, field
from botcity.maestro import BotMaestroSDK, AutomationTaskFinishStatus, AutomationTask
import logging
from .exceptions import *
from dotenv import load_dotenv
import os
from botcity.web import WebBot  # Import for Web Bot
from botcity.core import DesktopBot  # Import for Desktop Bot


logger = logging.getLogger(__name__)

'''
state.py
    Implements a state management system that works seamlessly with BotCity Orchestrator features.
    The State class maintains the execution state of automation tasks, providing features such as:
        - Count successful and failed items
        - Check for interruption request
        - Stores WebBot(), DesktopBot() instances
        - And more
'''


@dataclass
class State:
    maestro: BotMaestroSDK = None
    task_id: str = ""
    item: dict = field(default_factory=dict)
    success_count: int = 0
    error_count: int = 0
    has_error: bool = False
    has_success: bool = False
    webbot: WebBot = None
    desktopbot: DesktopBot = None

    @property
    def total_items(self):
        """
        Sums success and error items.
        Returns: Total items.
        """
        return self.success_count + self.error_count

    def register_success(self):
        """
        Registers item success.
        """
        self.has_success = True
        self.success_count += 1

    def register_error(self):
        """
        Registers item error.
        """
        self.has_error = True
        self.error_count += 1

    def compute_finish_status(self) -> AutomationTaskFinishStatus:
        """
        Calculates the finish status of a task.
        Returns: AutomationTaskFinishStatus
        """
        if self.has_success and self.has_error:
            return AutomationTaskFinishStatus.PARTIALLY_COMPLETED
        elif self.has_error:
            return AutomationTaskFinishStatus.FAILED
        else:
            return AutomationTaskFinishStatus.SUCCESS

    def raise_for_interrupt_requested(self) -> bool:
        """
        Checks whether or not this task received an interrupt request.
        Returns: bool
        """
        task_info = self.maestro.get_task(self.task_id)
        if task_info.is_interrupted():
            raise InterruptException("Interrupt requested via BotCity.")
        return False

    def task_info(self) -> AutomationTask:
        """
        Returns details about a given task.
        Returns: AutomationTask
        """
        return self.maestro.get_task(self.task_id)

    def as_dict(self):
        """
        Returns:
            Dictionary representation of this object.
        """
        return asdict(self)


load_dotenv()
SERVER = os.getenv('SERVER')
LOGIN = os.getenv('LOGIN')
KEY = os.getenv('KEY')
TASK_ID = os.getenv('TASK_ID')


def init_state() -> State:
    """
    Detects how the bot is running and builds STATE accordingly - fully automatic:
      1. Started from the BotCity Runner   -> use the args it passed in
      2. .env filled in                    -> try logging in with those credentials
      3. Neither (or .env login fails)     -> local test mode, no auth
    Returns: STATE
    """
    state = State()

    runner_args = BotMaestroSDK.from_sys_args()

    if runner_args.server:
        state.maestro = runner_args
        state.task_id = state.maestro.task_id
        state.execution = state.maestro.get_execution(state.task_id)
        print("\n ######### Bot is running in a BotCity Runner environment. \n")
        return state

    if all((SERVER, LOGIN, KEY, TASK_ID)):
        # Set your credentials in the .env file order to run your bot locally
        # with connection to the Orchestrator.
        state.maestro = BotMaestroSDK()
        try:
            state.maestro.login(server=SERVER, login=LOGIN, key=KEY)
            state.task_id = TASK_ID
            state.execution = state.maestro.get_execution(state.task_id)
            print("\n ######### Bot is running locally with connection to the Orchestrator. \n")
            return state
        except Exception as ex:
            print(f"Error: {ex}")

    # No Runner args, no usable .env -> local test mode, no auth
    state.maestro = BotMaestroSDK()
    # Disable errors if we are not connected to the Orchestrator
    state.maestro.RAISE_NOT_CONNECTED = False
    # Opt-in to receive mock objects when not connected to the Orchestrator
    state.maestro.MOCK_OBJECT_WHEN_DISCONNECTED = True
    state.execution = state.maestro.get_execution(state.task_id)
    print("\n ######### Bot is running in test mode (locally without authentication). \n")
    return state


STATE = init_state()
