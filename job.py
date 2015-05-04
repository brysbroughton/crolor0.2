import crol, actions
from otcregistry import registry_data as rd

rg = crol.Registry(rd)

class Job:

    visited_urls = set([])
    
    def __init__(self):
        pass
        
    
    
class CrawlJob(crol.GenericType):
    """
    CrawlJob must be instantiated with valid registration object,
    or valid parameters for registration and log objects
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'crawljob',
            'registration' : None,
            'log' : None,
            'crawl' : None,
            'has_broken_links' : False
        }
        
        super(CrawlJob, self).__init__(**kwargs)

        if not isinstance(self.registration, crol.Registration):
            self.setprop('registration', crol.Registration(self.registration))

        if not isinstance(self.log, crol.WebLog):
            self.setprop('log', crol.WebLog(self.log or {}))
            self.registration.setprop('log', self.log)

    def go(self):
        self.log.filename = self.registration.department.name
        self.log.openfile()
        self.setprop('crawl', crol.Crawl({'seed_url':self.registration.site, 'log':self.log}))
        self.crawl.start(self.lognode)#need to pass logging function here
        self.log.closefile()
        if self.has_broken_links:
            self.applyactions()
            
    def lognode(self, node):
        if str(node.status) == '404':
            self.has_broken_links = True
        if node.parent == "HEAD":
            self.log.writerow([node.status, node.reason, node.mimetype, node.url, node.parent])
        else:
            self.log.writerow([node.status, node.reason, node.mimetype, node.url, node.parent.url])
            
    def applyactions(self):
        for a in self.registration.actions:
            actions.apply(a, self.registration)
            

##this is how the CrawlJob is used
#cj = CrawlJob({'registration':rg.registrations[0]})
#cj.go()

