import job, crol, otcregistry
import time
def start():
    for r in otcregistry.registrations:
        cj = job.CrawlJob({'registration':r})
        cj.go()

time_start = time.clock()
start()
time_stop = time.clock()
print 'This crawljob took approximately ' + str(round(time_stop - time_start, 2)) + ' seconds to complete.'

