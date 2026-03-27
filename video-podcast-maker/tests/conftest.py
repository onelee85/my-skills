"""Shared test fixtures for video-podcast-maker tests."""
import importlib.util
import os
import sys
from unittest.mock import patch


def _load_module(name, script_path, fake_argv=None, fake_env=None):
    """Load a Python script as a module with mocked sys.argv and env vars."""
    argv = fake_argv or [script_path, "--help"]
    env = {**os.environ, **(fake_env or {})}

    spec = importlib.util.spec_from_file_location(name, script_path)
    module = importlib.util.module_from_spec(spec)

    with patch.object(sys, "argv", argv), \
         patch.dict(os.environ, env, clear=False), \
         patch("sys.exit") as mock_exit:
        try:
            spec.loader.exec_module(module)
        except (SystemExit, Exception):
            pass  # Script may fail on missing API keys — we only need the functions

    return module


# Pre-load modules once for all tests
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# generate_tts.py needs mocked argv + env to avoid API key checks
tts_module = _load_module(
    "generate_tts",
    os.path.join(_project_root, "generate_tts.py"),
    fake_argv=["generate_tts.py", "--input", "/dev/null", "--dry-run"],
    fake_env={"TTS_BACKEND": "edge"},  # edge needs no API key
)

# generate_shorts.py
shorts_module = _load_module(
    "generate_shorts",
    os.path.join(_project_root, "generate_shorts.py"),
    fake_argv=["generate_shorts.py", "--input-dir", "/dev/null"],
)

# learn_design.py
learn_module = _load_module(
    "learn_design",
    os.path.join(_project_root, "learn_design.py"),
    fake_argv=["learn_design.py", "--help"],
)
