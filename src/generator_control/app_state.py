import logging

from pydoover.state import StateMachine

log = logging.getLogger(__name__)

STATE_NAME_LOOKUP = {
    "off": "Off",
    "error": "Problem",
    "running_manual": "Running",
    "starting_user": "Starting",
    "running_user": "Running",
    "stopping_user": "Stopping",
    "starting_auto": "Starting",
    "warmup_auto": "Warming Up",
    "running_auto": "Running",
    "cooldown_auto": "Cooling Down",
    "stopping_auto": "Stopping",
}

class GeneratorControlState:
    state: str

    def __init__(self, app):
        self.app = app

        self.states = [
            {"name": "off"},
            {"name": "error", "timeout": self.app.config.error_timeout_seconds, "on_timeout": "reset_error", "on_enter": "on_error", "on_exit": "clear_error"},
            {"name": "running_manual"},
            ## These states are used when the user has pressed the start button
            {"name": "starting_user", "timeout": 30, "on_timeout": "trigger_error"},
            {"name": "running_user"},
            {"name": "stopping_user", "timeout": 30, "on_timeout": "trigger_error"},
            ## These states are used when another system has requested the motor to run
            {"name": "starting_auto", "timeout": 45, "on_timeout": "trigger_error"},
            {"name": "warmup_auto", "timeout": self.app.config.warmup_time.value, "on_timeout": "warmup_auto_complete"},
            {"name": "running_auto"},
            {"name": "cooldown_auto", "timeout": self.app.config.cooldown_time.value, "on_timeout": "auto_stop"},
            {"name": "stopping_auto", "timeout": 30, "on_timeout": "trigger_error"},
        ]

        self.transitions = [
            {"trigger": "manual_start", "source": "off", "dest": "running_manual"},
            {"trigger": "user_start", "source": ["off", "error"], "dest": "starting_user"},
            {"trigger": "user_has_started", "source": "starting_user", "dest": "running_user"},
            {"trigger": "user_stop", "source": "running_user", "dest": "stopping_user"},
            {"trigger": "auto_run_start", "source": "off", "dest": "starting_auto"},
            {"trigger": "auto_has_started", "source": "starting_auto", "dest": "warmup_auto"},
            {"trigger": "warmup_auto_complete", "source": ["warmup_auto", "cooldown_auto"], "dest": "running_auto"},
            {"trigger": "cooling_down_auto", "source": "running_auto", "dest": "cooldown_auto"},
            {"trigger": "auto_stop", "source": ["warmup_auto", "cooldown_auto"], "dest": "stopping_auto"},
            {"trigger": "generator_stopped", "source": ["running_manual", "starting_user", "running_user", "stopping_user", "starting_auto", "warmup_auto", "running_auto", "cooldown_auto", "stopping_auto"], "dest": "off"},
            {"trigger": "set_error", "source": "*", "dest": "error"},
            {"trigger": "unset_error", "source": "error", "dest": "off"},
        ]

        self.state_machine = StateMachine(
            states=self.states,
            transitions=self.transitions,
            model=self,
            initial="off",
            queued=True,
        )

    def get_state_string(self):
        """
        Returns the display string of the current state.
        """
        ## Iterate through the states to find the one with "name" matching the current state
        for state in self.states:
            if state["name"] == self.state:
                return STATE_NAME_LOOKUP.get(state["name"], "...")
        return "..."

    async def spin_state(self): 
        last_state = None
        ## keep spinning until state has stabilised
        while last_state != self.state:
            last_state = self.state
            await self.evaluate_state()
            # log.info(f"State spin complete for {self.name} - {self.state}")

        log.info(f"State is: {self.state}")
        return self.state

    async def evaluate_state(self):
        s = self.state

        if s == "off":
            if self.app.get_is_running():
                await self.manual_start()
            elif self.app.check_start_command():
                await self.user_start()
            elif self.app.has_run_request():
                await self.auto_run_start()

        elif s == "error":
            if self.app.check_clear_error_command():
                await self.reset_error()
            elif self.app.check_start_command():
                await self.user_start()

        elif s == "running_manual":
            if not self.app.get_is_running(stable_time=2, stable_value=True):
                await self.generator_stopped()

        elif s == "starting_user":
            if self.app.get_is_running():
                await self.user_has_started()
            elif self.app.check_stop_command():
                await self.user_stop()

        elif s == "running_user":
            if self.app.check_stop_command():
                await self.user_stop()
            elif not self.app.get_is_running(stable_time=2, stable_value=True):
                await self.trigger_error()

        elif s == "stopping_user":
            if not self.app.get_is_running(stable_time=2, stable_value=True):
                await self.generator_stopped()

        elif s == "starting_auto":
            if self.app.get_is_running():
                await self.auto_has_started()
            elif not self.app.has_run_request():
                await self.generator_stopped()

        elif s == "warmup_auto":
            if not self.app.has_run_request():
                await self.auto_stop()
            elif not self.app.get_is_running(stable_time=2, stable_value=True):
                await self.trigger_error()

        elif s == "running_auto":
            if not self.app.has_run_request():
                await self.cooling_down_auto()
            elif not self.app.get_is_running(stable_time=2, stable_value=True):
                await self.trigger_error()

        elif s == "cooldown_auto":
            if self.app.has_run_request():
                await self.warmup_auto_complete()
            elif not self.app.get_is_running(stable_time=2, stable_value=True):
                await self.generator_stopped()    

        elif s == "stopping_auto":
            if not self.app.get_is_running(stable_time=2, stable_value=True):
                await self.generator_stopped()

    async def trigger_error(self, error: str = "Problem running generator"):
        """
        Set the state to error.
        """
        log.error("Setting state to error : " + error)
        if self.state != "error":
            await self.set_error()
        self.app.last_error = error

    async def on_error(self):
        """
        Called when the state is set to error.
        """
        ## Send a notification to the user
        if self.app.config.send_error_notifications.value:
            await self.app.ui_manager.send_notification_async("Problem running generator. Most likely out of fuel")

    async def reset_error(self):
        """
        Reset the error state.
        """
        log.info("Resetting error state")
        if self.state == "error":
            await self.unset_error()
        self.clear_error()

    def clear_error(self):
        self.app.last_error = None