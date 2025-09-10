from pathlib import Path

from pydoover import config


class GeneratorControlConfig(config.Schema):
    def __init__(self):

        self.display_name = config.String(
            "Display Name",
            description="The display name for the small motor control application.",
            default="Engine",
        )
        self.run_command_pin = config.Integer(
            "Run Command Pin",
            description="The output pin is used to control the generator",
            default=0,
            minimum=0,
        )
        self.run_sense_pins = config.Array(
            "Run Sense Pins",
            description="If any of these pins are high, the generator is running",
            element=config.Integer("Input Pin", description="Input Pin"),
        )
        self.warmup_time = config.Integer(
            "Warmup Time",
            description="The time in seconds to warm up the generator",
            default=60,
            minimum=0,
        )
        self.cooldown_time = config.Integer(
            "Cooldown Time",
            description="The time in seconds to cool down the generator",
            default=30,
            minimum=0,
        )
        self.error_timeout = config.Integer(
            "Error Timeout",
            description="If there is a problem, the fault will be cleared after this many hours",
            default=24,
            minimum=0,
        )
        self.send_error_notifications = config.Boolean(
            "Send Error Notifications",
            description="Whether to send error notifications",
            default=True,
        )

        self.position = config.Integer(
            "Position",
            default=119,  # fairly low
            minimum=0,
            maximum=999,
            description="The position of the generator control app in the UI. Smaller is higher, larger is lower. 100 is the default position of most apps.",
        )

    @property
    def error_timeout_seconds(self):
        return self.error_timeout.value * 60 * 60


def export():
    GeneratorControlConfig().export(Path(__file__).parents[2] / "doover_config.json", "generator_control")

if __name__ == "__main__":
    export()
