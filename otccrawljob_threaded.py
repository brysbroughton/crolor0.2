import job, crol, otcregistry
import threading
import time
from timeit import default_timer
import multiprocessing

class Crawl_Job(threading.Thread):
    def __init__(self, reg):
        threading.Thread.__init__(self)
        self.registration = reg
        
    def run(self):
        cj = job.CrawlJob({'registration':self.registration})
        cj.go()

if __name__ == '__main__':
    start_time = default_timer()

    thread_list = []
    for r in otcregistry.registrations:
        tcj = Crawl_Job(reg=r)
        thread_list.append(tcj)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()
    duration = default_timer() - start_time
    print "This job took: ",duration, " seconds"
