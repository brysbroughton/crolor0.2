from bs4 import BeautifulSoup as bs
from urlparse import urlparse
from datetime import datetime
import re, httplib


class GenericType(object):
    """
    General template for associating properties to actions.
    To be extended by other crol classes.
    
    type: generic
    """
    
    def setprop(self, key, val):
        if self.props.has_key(key):
            self.props[key] = val
            setattr(self, key, val)
        else:
            raise Exception('%s has no property: %s' % (self.props['type'], key))
    
    def getprop(self, key):
        if self.props.has_key(key):
            return self.props[key]
        else:
            raise Exception('%s has no property: %s' % (self.props['type'], key))
    
    def listprops(self):
        for key, val in self.props.iteritems():
            print "%s : %s" % (key, val)
    
    def __extend_props__(self, key, val=None):
        self.props[key] = val
        setattr(self, key, val)
    
    def __init__(self, **kwargs):
        self.props = self.props or {'type' : 'generic'}
        if not self.props.has_key('type'):
            raise Exception('Generic subtype must have a type specified in properties')
        for key, val in self.props.iteritems():
            self.setprop(key, val)
        self.args = kwargs
        self.__use_args__()
    
    def __use_args__(self):
        for key, val in self.args.iteritems():
            if self.props.has_key(key):
                self.setprop(key, val)
            else:
                raise Exception('%s object has no property: %s' % (self.props['type'], key))


class Registration(GenericType):
    """
    Object that associates a department to a website and actions.
    
    department: department object
    site: dep.otc.edu/artment
    actions: list of action objects
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'registration',
            'department' : None,
            'site' : None,
            'log' : None,
            'actions' : []
        }
        
        super(Registration, self).__init__(**kwargs)
        
        if self.props['department']:
            self.setprop('department', Department(self.props['department']))
            
        if self.props['log']:
            self.setprop('log', WebLog(self.props[log]))


class Department(GenericType):
    """
    Object handles information for an orgnaizational entity associated with a crawl
    type : department
    name : department_name
    main_email : department@otc.edu
    email_group : [an@email.com, another@email.edu]
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'department',
            'name' : None,
            'main_email' : None,
            'email_group' : []
        }
        
        super(Department, self).__init__(**kwargs)


class Registry(GenericType):
    """
    Object handles the listing of sites to crawl and associates them to departments.
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'registry',
            'registrations' : []
        }
        
        super(Registry, self).__init__(**kwargs)
        
        if self.props['registrations']:
            setattr(self, 'registrations', [Registration(r) for r in self.props['registrations']])


class CrawlReport(GenericType):
    """
    Object instatiated 1-1 with a crawl job.
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'crawl_report',
            'crawl' : None,
            'seed_url' : None,
            'url_reports' : [],
            'statistics' : {
                'total_count' : 0,
                'ok_count' : 0,
                'redirected_count' : 0,
                'broken_count' : 0
            }
        }
        
        super(CrawlReport, self).__init__(**kwargs)
        
        if self.props['url_reports']:
            setattr(self, 'url_reports', [UrlReport(r) for r in self.props['url_reports']])
    
    def addreport(self, report):
        self.url_reports.append(report)


class UrlReport(GenericType):
    """
    Object for handling url and the response received when it is requested.
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'url_report',
            'url' : None,
            'mimetype' : None,
            'status' : None,
            'reason' : None,
            'parent_url' : None
        }
        
        super(UrlReport, self).__init__(**kwargs)


class Node(GenericType):
    """
    Handles a url request information.
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'node',
            'url' : None,
            'response' : None,#replace by response object from httplib
            'urlparse' : None,
            'response' : None,
            'headers' : None,
            'mimetype' : None,
            'status' : None,
            'reason' : None,
            'links' : [],
            'parent': None,#'HEAD'
            'children' : []
        }
        
        super(Node, self).__init__(**kwargs)
        
        #if not self.url:
        #    raise Exception("Node object must be created with a url")
        print 'link:', self.url #to show progess in console
        
        self.setprop('url', self.normalize(self.getprop('url')))#first step is to normalize all urls
        self.setprop('urlparse', urlparse(self.getprop('url')))
        if self.urlparse.scheme in ['http', 'https']:
            self.request()
        elif self.urlparse.scheme == 'mailto':
            self.checkemail()
    
    def normalize(self, link):
        """
        Take a string link similar to /admissions
        Return a valid url like http://otc.edu/admissions
        Use urlparse to get the pieces of the link.
        If essential components (scheme, netloc) are missing, attempt to use those from parent node
        """
        
        if link is None or len(link) == 0:
            return ''
            
        link = link.strip()#remove whitespace from ends
        
        new_parsed = urlparse(link)

        if new_parsed.scheme == 'mailto':
            return link

        #relative paths are tricky
        new_path = new_parsed.path
        new_link = []
        
        try:
            if new_path.startswith('/'):
                pass
            else:#link with no leading slash should be sub-link of current directory
                if self.urlparse:
                    old_path_bits = re.split('/', self.urlparse.path)
                    if '.' in old_path_bits[-1]:#url ends with a filename
                        new_path_bits = old_path_bits[:-1] + [new_path]
                        new_path = '/'.join(new_path_bits)
                    else:
                        new_path = (self.urlparse.path + '/' + new_parsed.path).replace('//','/')
            new_link = [
                (new_parsed.scheme or self.urlparse.scheme) + '://',
                new_parsed.netloc or self.urlparse.netloc,
                new_path,
                #';'+new_parsed.params,
                '?'+new_parsed.query if new_parsed.query else '',
                #'#'+new_parsed.fragment
            ]
        except AttributeError as AEX:
            raise Exception("Could not normalize url. Url is mal-formed, or a relative url without a parent node. ORIGINAL ERROR: "+AEX.message)
        
        return ''.join(new_link)
    
    def request(self):
        """
        Request the url provided to the constructor.
        Set node url status code and reason.
        Call scape() and set node links list.
        """
        
        #connect and collect node.url info
        if self.urlparse.scheme == 'http':
            conn = httplib.HTTPConnection(self.urlparse.netloc)
        elif self.urlparse.scheme == 'https':
            conn = httplib.HTTPSConnection(self.urlparse.netloc)
        else:
            raise Exception("Node attempted to request unsupported protocol: "+self.url)
        
        #get response from HTTPConnnection and set props
        conn.request('GET',self.urlparse.path)
        response = conn.getresponse()
        self.setprop('response', response)
        self.setprop('status', response.status)
        self.setprop('reason', response.reason)
        self.setprop('headers', response.getheaders())
        
        #check for text/html mime type to scrape html
        content_type = response.getheader('content-type')
        if ';' in str(content_type): content_type = content_type.split(';')[0]
        self.setprop('mimetype', content_type)
        if self.mimetype is not None and 'text/html' in self.mimetype:
            if str(self.status) != '404':
                html_response = response.read()
                self.setprop('links', self.scrape(html_response))
    
    def scrape(self, html):
        """
        Use beautiful soup to get all the links off of the page.
        Return scraped links in set form.
        
        If the header includes a redirect, the location will be added to the nodes links,
        the same as a link in the response body. A correctly configured server will return
        the same link in the body as in the header redirect.
        """
        
        links = []
        
        #check headers for redirects
        redirects = filter(lambda x: x[0] == 'location', self.headers)
        links.extend([x[1] for x in redirects])
        
        #scrape response body
        soup = bs(html)
        metalinks = soup.findAll('meta', attrs={'http-equiv':True})
        for m in metalinks:
            index = str(m).find('url=')
            end = str(m).find('"',index, len(str(m)))
            if index != -1:
                link = str(m)[index+4:end]
                links.append(link)
        
        attrs = ['background', 'cite', 'codebase', 'href', 'longdesc', 'src']
            
        for a in attrs:
            links.extend(
                map(lambda x: x[a], soup.findAll(**{a:True}))# **{} unzips dictionary to a=True
            )
        
        return links
    
    def checkemail(self):
        """
        Called on node that contains an email link.
        Evaluates the link for correctness and sets internal properties accordingly
        """
        valid = re.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,4}$', self.urlparse.path)
        self.setprop('status', 200 if valid else 404)
        self.setprop('reason', 'Address correctly formatted' if valid else 'invalid email address')


class Crawl(GenericType):
    """
    Executes site crawl by creating and maintaining Node tree.
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'crawler',
            'seed_url' : None,
            'node_tree' : None,#'HEAD'
            'visited_urls' : set([]),
            'crawl_report' : None,
            'log' : None,
        }
        
        super(Crawl, self).__init__(**kwargs)
    
    def start(self, funcin=None):
        """
        Begin the crawl process from url seed
        """
        
        self.setprop('crawl_report', CrawlReport({'crawl':self, 'seed_url':self.seed_url}))
        head = Node({'url':self.seed_url, 'parent':'HEAD'})
        self.setprop('node_tree', head)
        if funcin: funcin(head)
        self.reccrawl(head, funcin)
        #self.setprop('log', WebLog({'crawl_report':self.crawl_report}))
    
    def reccrawl(self, node, funcin=None):
        self.visited_urls.add(node.url)
        
        for l in node.links:
            new_url = None
            
            #try to normalize url
            try:
                new_url = node.normalize(l)
            except IOError:
                print 'Could not normalize url: ', l
                
            if new_url: new_node = Node({'url':new_url})
            else: new_node = Node({'url':'', 'status':404, 'reason':'Empty link'})
            new_node.setprop('parent', node)
            node.children.append(new_node)
            
            if funcin: funcin(new_node)
            
            if new_url not in self.visited_urls:
                if self.shouldfollow(new_url):
                    self.reccrawl(new_node, funcin)
    
    def shouldfollow(self, url):
        """
        Checks if given url should be crawled.
        Returns boolean.
        """
        
        if url not in self.getprop('visited_urls'):
            url = urlparse(url)
            seed = urlparse(self.getprop('seed_url'))
            if url.netloc == seed.netloc and url.path[:len(seed.path)] == seed.path:
                return True
            else:
                return False
        else:
            return False

