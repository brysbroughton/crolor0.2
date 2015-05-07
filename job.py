import crol, logs, actions
from otcregistry import registry_data as rd

rg = crol.Registry(rd)

class Job:
    """
    Class description.
    """
    
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
        
        if not isinstance(self.log, logs.WebLog):
            self.setprop('log', logs.WebLog(self.log or {}))
            self.registration.setprop('log', self.log)
    
    def go(self):
        """
        Starts the CrawlJob().
        Opens the appropriate file.
        Creates and starts Crawl() with reportnode().
        Sends the built crawl_report to log.
        Closes opened file.
        Calls applyactions() is the crawl_report had broken links.
        """
        
        self.log.filename = self.registration.department.name
        self.log.openfile()
        self.setprop('crawl', crol.Crawl({'seed_url':self.registration.site, 'log':self.log}))
        self.crawl.start(self.reportnode)#need to pass logging function here
        self.log.readreport(self.crawl.crawl_report)
        self.log.closefile()
        #if self.has_broken_links:
            #self.applyactions()
    
    def reportnode(self, node):
        """
        Collects data from the given node.
        Adds appropriate statistics to crawl_report.
        Adds UrlReport to crawl_report.
        """
        
        #collect and report url statistics
        self.crawl.crawl_report.statistics['total_count'] += 1
        if str(node.status).startswith('2'): self.crawl.crawl_report.statistics['ok_count'] += 1
        if str(node.status).startswith('3'): self.crawl.crawl_report.statistics['redirected_count'] += 1
        if str(node.status) == '404':
            self.crawl.crawl_report.statistics['broken_count'] += 1
            self.has_broken_links = True
        
        #report node url_data
        if node.parent == 'HEAD': parent = node.parent
        else: parent = node.parent.url
        self.crawl.crawl_report.addreport(crol.UrlReport({
            'url' : node.url,
            'mimetype' : node.mimetype,
            'status' : node.status,
            'reason' : node.reason,
            'parent_url' : parent
        }))
    
    def applyactions(self):
        """
        Calls actions.apply() for each action in registration.actions.
        """
        
        for a in self.registration.actions:
            actions.apply(a, self.registration)

##this is how the CrawlJob is used
#cj = CrawlJob({'registration':rg.registrations[0]})
#cj.go()

