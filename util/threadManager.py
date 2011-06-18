from threading import Thread
import config

def runThreads(function,task_generator,storage,wait=True):
	def startThread(function,args):
		thread = Thread(target=function,args=args)
		thread.daemon = True
		thread.start()
		return thread
	
	threads = []
	for task in task_generator():
		threads.append(startThread(function,(task,storage)))
		if len(threads) > config.THREADLIMIT:
			break
	
	if wait:
		for thread in threads:
			thread.join()