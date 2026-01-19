"""Logger utility for RESPOND."""

import logging
import sys

from config.settings import settings

_configured_loggers: set[str] = set()


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name (typically module name).
    
    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding duplicate handlers
    if name in _configured_loggers:
        return logger
    
    logger.setLevel(settings.LOG_LEVEL.upper())
    
    # Console handler with formatted output
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(settings.LOG_LEVEL.upper())
    
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    _configured_loggers.add(name)
    return logger


# Default application logger
logger = get_logger("respond")
