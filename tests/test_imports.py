"""
Basic tests for an application.

This ensures all modules are importable and that the config is valid.
"""

def test_import_app():
    from generator_control.application import GeneratorControlApplication
    assert GeneratorControlApplication

def test_config():
    from generator_control.app_config import GeneratorControlConfig

    config = GeneratorControlConfig()
    assert isinstance(config.to_dict(), dict)

def test_ui():
    from generator_control.app_ui import GeneratorControlUI
    assert GeneratorControlUI

def test_state():
    from generator_control.app_state import GeneratorControlState
    assert GeneratorControlState