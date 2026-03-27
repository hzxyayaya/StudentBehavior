"""Student behavior analytics database package."""

from .cli import main
from .config import AnalyticsDBPaths, build_default_paths

__all__ = ["AnalyticsDBPaths", "build_default_paths", "main"]
