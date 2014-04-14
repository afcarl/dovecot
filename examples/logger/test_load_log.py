"""
	Test for Logger
"""
import sys

from dovecot.logger import logger

f_name = sys.argv[1]

l = logger.Logger(filename=f_name, write_delay=5)
print l.load()

