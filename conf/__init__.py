import os
import logging
from biicode.common.conf.configure_environment import get_env

BII_LOGGING_LEVEL = get_env('BII_LOGGING_LEVEL', logging.CRITICAL)
BII_LOGGING_FILE = get_env('BII_LOGGING_FILE', None)  # None is stdout
BII_TRACE_ERRORS = get_env('BII_TRACE_ERRORS', False)

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MEGABYTE = 1048576

# Max file size
BII_FILE_SIZE_LIMIT = get_env('BII_FILE_SIZE_LIMIT', 5 * MEGABYTE)
# Block max files
BII_BLOCK_NUMFILES_LIMIT = get_env('BII_BLOCK_NUMFILES_LIMIT', 2000)
# Hive max files
BII_MAX_BLOCK_SIZE = get_env('BII_MAX_BLOCK_SIZE', 12 * MEGABYTE)  # Max size of each block
