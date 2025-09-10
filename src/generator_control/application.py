import logging
import time

from pydoover.docker import Application
from pydoover import ui

from .app_config import GeneratorControlConfig
from .app_ui import GeneratorControlUI
from .app_state import GeneratorControlState

log = logging.getLogger()

class GeneratorControlApplication(Application):
    config: GeneratorControlConfig  # not necessary, but helps your IDE provide autocomplete!

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.started: float = time.time()
        self.ui: GeneratorControlUI = None
        self.state: GeneratorControlState = None

        self.loop_target_period = 0.5  # seconds

        self.last_is_running = False
        self.last_is_running_change = time.time()

        self.last_error = None
        self.last_inputs = None
        self.last_run_command = None


    async def setup(self):
        self.ui = GeneratorControlUI()
        self.state = GeneratorControlState(self)

        self.ui_manager.set_display_name(self.config.display_name.value)
        self.ui_manager.add_children(*self.ui.fetch())
        await self.update_inputs()

    async def main_loop(self):
        await self.update_inputs()

        state = await self.state.spin_state()

        ## Clear the UI actions after evaluating the state
        self.ui.start_now.coerce(None)
        self.ui.stop_now.coerce(None)
        self.ui.clear_error.coerce(None)

        await self.update_tags()

        ## Do different things based on the state
        if state in [
                "off",
                "error",
                "running_manual",
                "stopping_user",
                "stopping_auto",
            ]:
            await self.set_run_command(False)

        elif state in ["starting_user", "starting_auto", "warmup_auto", "running_auto", "cooldown_auto"]:
            await self.set_run_command(True)

        ## Update the display string
        self.ui_manager.set_display_name(self.config.display_name.value + " - " + self.state.get_state_string())
        self.ui.update(
            run_request=state in ["starting_user", "running_user", "starting_auto", "warmup_auto", "running_auto", "cooldown_auto"],
            is_running=(self.get_is_running()),
            is_starting=("starting" in state),
            manual_mode=state in ["running_manual"],
            run_request_reason=self.run_request_reason(),
            error=self.last_error,
        )

    async def update_inputs(self):
        # This is where you would read inputs from the device
        run_sense_pins = [pin.value for pin in self.config.run_sense_pins.elements]
        self.last_inputs = await self.platform_iface.get_di_async(run_sense_pins)
        if not isinstance(self.last_inputs, list):
            self.last_inputs = [self.last_inputs]

    async def update_tags(self):
        await self.set_tag("state", self.state.state)

    def has_run_request(self) -> bool:
        return self.run_request_reason() is not None

    def run_request_reason(self) -> str | None:
        return self.get_tag("run_request_reason")

    def check_start_command(self):
        # This is where you would check for a start command, e.g., from a button press
        return self.ui.start_now.current_value
    
    def check_stop_command(self):
        # This is where you would check for a stop command, e.g., from a button press
        return self.ui.stop_now.current_value
    
    def check_clear_error_command(self):
        # This is where you would check for a clear error command, e.g., from a button press
        return self.ui.clear_error.current_value

    def get_is_running(self, stable_time: float = 0.5, stable_value: bool = None) -> bool:
        if self.last_inputs is None or len(self.last_inputs) == 0:
            result = self.last_run_command
        elif any(self.last_inputs):
            result = True
        else:
            result = False
 
        if result != self.last_is_running:
            self.last_is_running = result
            self.last_is_running_change = time.time()
        if stable_value is not None and time.time() - self.last_is_running_change < stable_time:
            return stable_value
        return result
    
    async def set_run_command(self, state: bool):
        await self.platform_iface.set_do_async(self.config.run_command_pin.value, state)
        self.last_run_command = state