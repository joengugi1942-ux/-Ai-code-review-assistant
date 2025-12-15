import logging

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    logging.basicConfig(level=settings.log_level.upper())
    logger.remove()
    logger.add(
        sink=lambda msg: logging.getLogger("app").info(msg),
        level=settings.log_level.upper(),
    )


setup_logging()



