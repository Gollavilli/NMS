from Queue import Queue
from threading import Thread
from time import time


def update_(mydict,key,val):
	mydict[key] = val


class ThreadWorker(Thread):
	def __init__(self, queue):
		Thread.__init__(self)
		self.queue = queue

	def run(self):
		while True:
			func, key, val, mydict = self.queue.get()
			func(mydict, key, val)
			self.queue.task_done()

def run_mp():
	start = time()
	queue = Queue()
	response = {}
	for x in range(18):
		worker = ThreadWorker(queue)
		worker.daemon = True
		worker.start()

	for j in range(500):
		queue.put((update_, j, j, response))

	queue.join()
	end = time()
	return end-start

def run_lp():
	start = time()
	response = {}
	for j in range(500):
		response[j] = j
	end = time()
	return end-start



print run_mp()
print run_lp()
