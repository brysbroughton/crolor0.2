import crol
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

    def go(self):
        self.log.filename = self.registration.department.name
        self.log.openfile()
        self.setprop('crawl', crol.Crawl({'seed_url':self.registration.site, 'log':self.log}))
        self.crawl.start(self.lognode)#need to pass logging function here
        self.log.closefile()
        if self.has_broken_links:
            self.sendemail()
            
    def lognode(self, node):
        if str(node.status) == '404':
            self.has_broken_links = True
        if node.parent == "HEAD":
            self.log.writerow([node.status, node.reason, node.mimetype, node.url, node.parent])
        else:
            self.log.writerow([node.status, node.reason, node.mimetype, node.url, node.parent.url])
            
    def sendemail(self):
        report_location = self.log.path+self.log.filename+self.log.endfilename
        msg = '<h1>Link Report</h1><p>You can review the report at: <a href="' + report_location + '">this link</a></p>'
        subject = 'Crawl Completed'
        to_address = self.registration.department.main_email
        cc_address = ''
        files = [report_location]
        from_address = 'web@otc.edu'
        file_name = self.log.filename + self.log.endfilename
        email_props = {'files':files, 'filename':file_name, 'cc_address':cc_address, 'to_address':to_address, 'from_address':from_address, 'subject':subject, 'msg_body':msg}
        e = crol.Email(email_props)
        e.send()


##this is how the CrawlJob is used
#cj = CrawlJob({'registration':rg.registrations[0]})
#cj.go()


