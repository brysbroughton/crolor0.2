import job, crol, otcregistry

def start():
    for r in otcregistry.registrations:
        cj = job.CrawlJob({'registration':r})
        cj.go()

start()

