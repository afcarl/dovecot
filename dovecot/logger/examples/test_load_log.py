"""
	Test for Logger
"""

import logger

l = logger.Logger(file_name="test", write_delay=5)
print l.load()

