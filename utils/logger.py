import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import colorlog

_ROOT = Path(__file__).parent.parent
_LOG_DIR = _ROOT / "logs"
_LOG_DIR.mkdir(exist_ok=True)

_LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
_file_handler: TimedRotatingFileHandler = None


def _get_file_handler() -> TimedRotatingFileHandler:
    global _file_handler
    if _file_handler is None:
        log_file = _LOG_DIR / "test.log"
        _file_handler = TimedRotatingFileHandler(
            log_file, when="midnight", backupCount=7, encoding="utf-8"
        )
        _file_handler.setLevel(logging.DEBUG)
        _file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)-8s] %(name)s - %(message)s"
        ))
    return _file_handler


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(_LOG_LEVEL)
    logger.propagate = False

    # 控制台彩色输出（INFO 及以上）
    console = colorlog.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)-8s] %(name)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    ))

    logger.addHandler(console)
    logger.addHandler(_get_file_handler())
    return logger
