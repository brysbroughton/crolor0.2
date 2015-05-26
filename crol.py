from bs4 import BeautifulSoup as bs
from urlparse import urlparse
from datetime import datetime
import re, httplib
from pprint import pprint


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
            'actions' : [],
            'nofollow_patterns' : [],
            'ignore_patterns' : []
        }
        
        super(Registration, self).__init__(**kwargs)
        
        if self.props['department']:
            setattr(self, 'department', Department(self.props['department']))


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
        """
        Adds the given url_report to url_reports list.
        """
        
        self.url_reports.append(report)
    
    def reportnode(self, node):
        """
        Collects data from the given node.
        Adds appropriate statistics to crawl_report.
        Adds UrlReport to crawl_report.
        """
        
        #collect and report url statistics
        self.statistics['total_count'] += 1
        if str(node.status).startswith('2'): self.statistics['ok_count'] += 1
        if str(node.status).startswith('3'): self.statistics['redirected_count'] += 1
        if str(node.status) == '404': self.statistics['broken_count'] += 1
        
        #report node url_data
        if node.parent == 'HEAD': parent = node.parent
        else: parent = node.parent.url
        self.addreport(UrlReport({
            'url' : node.url,
            'mimetype' : node.mimetype,
            'status' : node.status,
            'reason' : node.reason,
            'parent_url' : parent
        }))


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
            'response' : None,
            'urlparse' : None,
            'headers' : None,
            'mimetype' : None,
            'status' : None,
            'reason' : None,
            'links' : [],
            'parent': None,
            'children' : []
        }
        
        super(Node, self).__init__(**kwargs)
        
        #if not self.url:
        #    raise Exception("Node object must be created with a url")
        print 'link:', self.url #to show progess in console
        
        self.setprop('url', self.normalize(self.getprop('url')))#first step is to normalize all urls
        print self.url #to show progess in console
        self.setprop('urlparse', urlparse(self.getprop('url')))
        if self.urlparse.scheme in ['http', 'https']:
            self.request()
        elif self.urlparse.scheme == 'mailto':
            self.checkemail()
        elif not self.url == '':
            self.setprop('reason', 'Unsupported URI Scheme')
    
    def normalize(self, link):
        """
        Take a relative link and turn it into an absolute link, based on the current node.
        Follows browser behavior, not necessarily up to speecification (http://www.ietf.org/rfc/rfc2396.txt)
        """
        
        #empty link
        if link is None or len(link) == 0:
            return ''
            
        new_parsed = urlparse(link)
        generated_path = False #replace by a generated path, when relative link is evaluated

        #if the link has a scheme, treat as absolute url
        if new_parsed.scheme != '':
            return link
            
        else:
            
            if new_parsed.path == '' or new_parsed.path == '/':
                pass
            else:#evaluating path for relative links
                current_path_stack = re.split('/', self.urlparse.path)
                current_path_stack.pop()#last path string will either be empty string or filename
                new_path_stack = re.split('/', new_parsed.path)
                generated_path_stack = [] if new_parsed.path.startswith('/') else current_path_stack
                
                for new_path_bit in new_path_stack:
                    try:
                        if new_path_bit == '.': #or new_path_bit == '':
                            pass
                        elif new_path_bit == '..':
                            generated_path_stack.pop()
                        else:
                            generated_path_stack.append(new_path_bit)
                    except IndexError:
                        pass#popping from empty stack is ok
                
                generated_path = '/'.join(generated_path_stack).replace('//', '/')
                if not generated_path.startswith('/'): generated_path = '/' + generated_path
            
            try:
                normal_bits = [
                    self.urlparse.scheme + '://',
                    self.urlparse.netloc,
                    generated_path if generated_path is not False else new_parsed.path,
                    #';'+new_parsed.params,
                    '?'+new_parsed.query if new_parsed.query else '',
                    #'#'+new_parsed.fragment
                ]
            except AttributeError as AEX:
                raise Exception("Could not normalize url. Url is mal-formed, or a relative url without a parent node. ORIGINAL ERROR: "+AEX.message)
            
            return ''.join(normal_bits)
    
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
                    
        # Checking for a query string in the url
        # If present, add query string to url before checking status
        if self.urlparse.query != '':
            conn.request('GET',self.urlparse.path+"?"+self.urlparse.query)
        else:
            conn.request('GET',self.urlparse.path)
        #try up to five times in case server closes connection too early
        #Avoids getting a blank status line that throws an exception
        for attempt in range(5):
            try:
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
            except:
                continue
            else:
                break

        
    
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
        self.setprop('reason', 'Address Correctly Formatted' if valid else 'Invalid Email Address')


class Crawl(GenericType):
    """
    Executes site crawl by creating and maintaining Node tree.
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'crawler',
            'seed_url' : None,
            'node_tree' : None,
            'visited_urls' : set([]),
            'url_nodes' : {},
            'crawl_report' : None,
            'logs' : {
                'excellog' : None,
                'weblog' : None
            },
            'nofollow_patterns' : [],
            'ignore_patterns' : []
        }
        
        super(Crawl, self).__init__(**kwargs)
    
    def start(self, funcin=None):
        """
        Begin the crawl process from url seed
        """
        
        head = Node({'url':self.seed_url, 'parent':'HEAD'})
        self.setprop('node_tree', head)
        if funcin: funcin(head)
        self.reccrawl(head, funcin)
    
    def reccrawl(self, node, funcin=None):
        """
        Creates a node for each link found on the given node.
        Adds each new_node as children to the given node.
        Calls itself for each new crawlable child.
        """
        
        self.visited_urls.add(node.url)
        
        for l in node.links:
            new_url = None
            
            #try to normalize url
            try: new_url = node.normalize(l)
            except IOError: print 'Could not normalize url: ', l

            if new_url:
                if self.shouldignore(new_url):
                    continue
            
            if not new_url and self.url_nodes.has_key(''):
                new_node = self.url_nodes['']
            elif self.url_nodes.has_key(new_url):
                new_node = self.url_nodes[new_url]
            elif new_url:
                new_node = Node({'url':new_url})
                new_node.setprop('parent', node)
            else:
                new_node = Node({'url':'', 'status':404, 'reason':'Empty URL'})
                new_node.setprop('parent', node)
            
            node.children.append(new_node)
            if funcin: funcin(new_node)
            
            if not self.url_nodes.has_key(new_node.url):
                if new_url not in self.visited_urls and self.shouldfollow(new_node):
                    self.reccrawl(new_node, funcin)
    
    def shouldfollow(self, node):
        """
        Take node object, return boolean
        #don't crawl the same url 2x
        #only crawl urls within a subsite of the input seed
        """
        
        for p in self.nofollow_patterns:
            match = re.search(p, node.url)
            if match:
                self.url_nodes[node.url] = node
                return False
        
        if node.url not in self.getprop('visited_urls'):
            url = urlparse(node.url)
            seed = urlparse(self.getprop('seed_url'))
            if url.netloc == seed.netloc and url.path[:len(seed.path)] == seed.path:
                self.url_nodes[node.url] = node
                return True
            else:
                self.url_nodes[node.url] = node
                return False
        else:
            self.url_nodes[node.url] = node
            return False

    def shouldignore(self, url):
        for p in self.ignore_patterns:
            match = re.search(p, url)
            if match:
                return True
            else:
                return False

