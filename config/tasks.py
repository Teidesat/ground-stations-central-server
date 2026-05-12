# config/tasks.py
"""Legacy tasks module - DEPRECATED. Use core.tasks instead."""

import warnings

from core.tasks import *  # noqa: F401, F403

warnings.warn(
    "Importing from config.tasks is deprecated. Use core.tasks instead.",
    DeprecationWarning,
    stacklevel=2
)