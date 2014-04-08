"""
	Test for Logger
"""

import time
import sys

from dovecot.logger import logger

f_name = sys.argv[1]

l = logger.Logger(file_name=f_name, write_delay=60)
#l.start()
l.log({'a' : 1})
l.save()
l.log({'b' : 2})
l.log({'c' : 3})
l.log({'d' : 4})
l.print_datas()
l.save()
