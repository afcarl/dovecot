"""
	Test for Logger
"""
import sys

from dovecot.logger import logger

f_name = sys.argv[2]
g_folder = sys.argv[1]

l = logger.Logger(filename=f_name, folder=g_folder, write_delay=5)
print l.load()

