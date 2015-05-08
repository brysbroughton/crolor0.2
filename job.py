import crol, logs, actions


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
            'crawl' : None
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
        
        self.setprop('crawl', crol.Crawl({
            'seed_url' : self.registration.site,
            'crawl_report' : crol.CrawlReport({'seed_url':self.registration.site}),
            'log' : self.log,
        }))
        self.log.filename = self.registration.department.name
        self.crawl.start(self.crawl.crawl_report.reportnode)
        self.log.reporttofile(self.crawl.crawl_report)
        if self.crawl.crawl_report.statistics['broken_count'] > 0: self.applyactions()
    
    def applyactions(self):
        """
        Calls actions.apply() for each action in registration.actions.
        """
        
        for a in self.registration.actions:
            actions.apply(a, self.registration)

