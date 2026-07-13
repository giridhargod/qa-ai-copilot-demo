import importlib

import pytest

from .. import config


def test_float_env_parses_valid_value(monkeypatch):
    monkeypatch.setenv("STSG_TEST_FLOAT", "0.75")
    assert config._float_env("STSG_TEST_FLOAT", "0.6") == 0.75


def test_float_env_falls_back_to_default_when_unset(monkeypatch):
    monkeypatch.delenv("STSG_TEST_FLOAT", raising=False)
    assert config._float_env("STSG_TEST_FLOAT", "0.6") == 0.6


def test_float_env_raises_clear_error_on_non_numeric_value(monkeypatch):
    monkeypatch.setenv("STSG_TEST_FLOAT", "0.6a")
    with pytest.raises(ValueError, match="STSG_TEST_FLOAT.*is not a number"):
        config._float_env("STSG_TEST_FLOAT", "0.6")


def test_module_level_thresholds_raise_clear_error_on_malformed_env(monkeypatch):
    # Regression: these are computed at import time -- a typo'd env var
    # used to surface as a bare "could not convert string to float"
    # traceback with no indication of which setting or file was at fault.
    monkeypatch.setenv("STSG_LOW_CONFIDENCE_THRESHOLD", "not-a-number")
    with pytest.raises(ValueError, match="STSG_LOW_CONFIDENCE_THRESHOLD"):
        importlib.reload(config)
    monkeypatch.delenv("STSG_LOW_CONFIDENCE_THRESHOLD", raising=False)
    importlib.reload(config)  # restore clean module state for other tests
