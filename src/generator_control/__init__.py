from pydoover.docker import run_app

from .application import GeneratorControlApplication
from .app_config import GeneratorControlConfig

def main():
    """
    Run the application.
    """
    run_app(GeneratorControlApplication(config=GeneratorControlConfig()))
