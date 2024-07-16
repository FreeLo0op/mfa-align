import os
import sys
import logging

def configure_logger():
	logger = logging.getLogger('---align---')
	logger.setLevel(logging.DEBUG)

	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setLevel(logging.DEBUG)

	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	console_handler.setFormatter(formatter)

	logger.addHandler(console_handler)

	return logger

logger = configure_logger()