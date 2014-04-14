"""
	Test for Logger
"""

import logger

l = logger.Logger(filename="test", write_delay=5)
print l.load()

