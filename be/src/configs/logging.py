import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "colored",
        },
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "mysql.connector": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "httpx": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
        "httpcore": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name=None):
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals["__name__"]

    logger = logging.getLogger(name)
    return logger
