"""
	Test for Logger
"""

import logger
import time

l = logger.Logger(filename="test", write_delay=5)
l.start()
l.log({'a' : 1})
l.log({'b' : 2})
l.log({'c' : 3})
l.log({'d' : 4})
l.print_datas()
