import os
import sys

from loguru import logger

logger.remove()  # remove the old handler. Else, the old one will work along with the new one you've added below'
logger.add(sys.stdout, level=os.environ.get("LOG_LEVEL", "INFO").upper())
