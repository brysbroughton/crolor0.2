import job
import crol

rg = job.rg
for r in rg.registrations:
    cj = job.CrawlJob({'registration':r})
    cj.go()
