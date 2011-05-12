from threading import Thread
from util import *

def runThreads(function,task_generator,storages):
	try:
		def startThread(function,*args):
			thread = Thread(target=function,args=args)
			thread.start()
			return thread
		
		threads = []
		for task in task_generator():
			threads.append(startThread(function,task,storages))
			if len(threads) > config.THREADLIMIT:
				break
		
		for thread in threads:
			thread.join()
	except:
		logError(__name__)