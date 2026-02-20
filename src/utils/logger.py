from monolog import MongoLogger

from src.core.config import settings

logger = MongoLogger(config=settings.LOGGER)
