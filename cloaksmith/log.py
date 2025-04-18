# log.py
import logging


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[41m",  # Red background
        "GREY": "\033[90m",      # Grau
        "RESET": "\033[0m"
    }

    def format(self, record):
        # Pad uncolored level name
        raw_level = record.levelname
        padded = f"{raw_level:<8}"

        # Add color after padding
        color = self.COLORS.get(raw_level, "")
        reset = self.COLORS["RESET"]
        record.levelname = f"{color}{padded}{reset}"
        record.name = f"{self.COLORS.get('GREY')}{record.name}{reset}"
        return super().format(record)


_logger = None

def setup_logging(level="INFO"):
    global _logger
    if _logger:
        return _logger

    logger = logging.getLogger("keycloak-scripts")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter("%(asctime)s [ %(levelname)s | %(name)s ] %(message)s"))
        logger.addHandler(handler)

    _logger = logger
    return logger

def get_logger():
    return _logger or setup_logging()