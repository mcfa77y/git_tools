import sys
from enum import Enum
from typing import Optional, Union

from loguru import logger


class LogLevel(Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    def __init__(self, name: str, level: Union[LogLevel, str] = LogLevel.INFO) -> None:
        """Initialize a logger with a name and level.

        Args:
            name: The name of the logger
            level: The logging level (default: LogLevel.INFO)
        """
        self.name = name
        self.level = level.value if isinstance(
            level, LogLevel) else level.upper()
        logger.remove()
        logger.add(sys.stdout, level=self.level)
        self.logger_jl = logger

    def create_child(
        self, child_name: str, level: Optional[Union[LogLevel, str]] = None
    ) -> "Logger":
        """Create a child logger with an optional different level.

        Args:
            child_name: Name of the child logger
            level: Optional log level for the child logger

        Returns:
            A new Logger instance representing the child logger
        """
        full_name = f"{self.name}.{child_name}"
        return Logger(full_name, level or self.level)
