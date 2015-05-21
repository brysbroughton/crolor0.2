import job, crol, otcregistry
from timeit import default_timer

def run():
    for r in otcregistry.registrations:
        cj = job.CrawlJob({'registration':r})
        cj.go()
        
start_time = default_timer()
run()
duration = default_timer() - start_time
print "This job took: ",duration," seconds"
 
