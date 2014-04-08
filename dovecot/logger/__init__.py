"""
Typical usage:
	l = logger.Logger(file_name="test_log", write_delay=5)
	l.log({'a' : 1})
	l.end()
    
"""
from .logger import Logger
