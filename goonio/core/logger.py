import sys
import logging
from loguru import logger

# Intercept standard logging messages to redirect them through Loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logger(level: str = "INFO"):
    """
    Configures the Loguru logger with custom levels and formatting.
    """
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    logger.level("GOONIO", no=50, icon="🌶️", color="<fg #ff4500>")
    logger.level("API", no=45, icon="🌐", color="<fg #006989>")
    logger.level("SCRAPER", no=40, icon="🔍", color="<fg #d6bb71>")
    logger.level("STREAM", no=35, icon="🎬", color="<fg #d171d6>")

    log_format = (
        "<white>{time:YYYY-MM-DD HH:mm:ss}</white> | "
        "<level>{level.icon}</level> <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    logger.configure(
        handlers=[
            {
                "sink": sys.stderr,
                "level": level.upper(),
                "format": log_format,
                "backtrace": False,
                "diagnose": False,
                "enqueue": True,
            }
        ]
    )

# Initialize the logger with a default level
setup_logger()
