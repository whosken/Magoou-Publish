import logging
import os

def configLogging(name):
	formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')

	filename = os.path.join(os.getcwd(),'log')
	file = logging.FileHandler(filename)
	file.setLevel(logging.DEBUG)
	file.setFormatter(formatter)

	console = logging.StreamHandler()
	console.setLevel(logging.ERROR)
	console.setFormatter(formatter)

	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)
	# logger.addHandler(file)
	logger.addHandler(console)
	return logger

logger = configLogging('')

def debug(msg, *args, **kwargs):
	logger.debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
	logger.info(msg, *args, **kwargs)
	
def warning(msg, *args, **kwargs):
	logger.warning(msg, *args, **kwargs)
	
def error(msg, *args, **kwargs):
	logger.error(msg, *args, **kwargs)
	
def critical(msg, *args, **kwargs):
	logger.critical(msg, *args, **kwargs)
