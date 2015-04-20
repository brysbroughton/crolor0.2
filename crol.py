from bs4 import BeautifulSoup as bs
from urlparse import urlparse
import re


class generic_type(object):
    """
    General template for associating properties to actions.
    To be extended by other crol classes.

    type: generic
    
    """

    def set_prop(self, key, val):
        if self.props.has_key(key):
            self.props[key] = val
            setattr(self, key, val)
        else:
            raise Exception('%s has no property: %s' % (self.props['type'], key))

    def get_prop(self, key):
        if self.props.has_key(key):
            return self.props[key]
        else:
            raise Exception('%s has no property: %s' % (self.props['type'], key))
            
    def list_props(self):
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
            self.set_prop(key, val)
        self.args = kwargs
        self.__use_args__()

    def __use_args__(self):
        for key, val in self.args.iteritems():
            if self.props.has_key(key):
                self.set_prop(key, val)
            else:
                raise Exception('%s object has no property: %s' % (self.props['type'], key))



class registration(generic_type):
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
            'actions' : []
        }

        super(registration, self).__init__(**kwargs)

        if self.props['department']:
            setattr(self, 'department', department(self.props['department']))

        

class department(generic_type):
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

        super(department, self).__init__(**kwargs)




class registry(generic_type):
    """
    Object handles the listing of sites to crawl and associates them to departments.
    """

    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'registry',
            'registrations' : []
        }

        super(registry, self).__init__(**kwargs)

        if self.props['registrations']:
            setattr(self, 'registrations', [registration(r) for r in self.props['registrations']])
            
            
            
class crawl_report(generic_type):
    """
    Object instatiated 1-1 with a crawl job.
    
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'crawl_report',
            'seed_url' : None,
            'page_reports' : [],
            'url_reports' : []#not sure if use
        }
    
        super(crawl_report, self).__init__(**kwargs)
        
        if self.props['page_reports']:
            setattr(self, 'page_reports', [page_report(r) for r in self.props['page_reports']])

        if self.props['url_reports']:
            setattr(self, 'url_reports', [url_report(r) for r in self.props['url_reports']])
            
            
            
class page_report(generic_type):
    """
    Object for handling the reports of all links on its page
    """

    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'page_report',
            'page_url' : None,
            'page_status' : None,
            'url_reports' : []
        }
        
        super(page_report, self).__init__(**kwargs)
        
        if self.props['url_reports']:
            setattr(self, 'url_reports', [url_report(r) for r in self.props['url_reports']])

            
class url_report(generic_type):
    """
    Object for handling url and the response received when it is requested.
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'url_report',
            'url' : None,
            'linked_from' : None
        }
        
        super(url_report, self).__init__(**kwargs)
        

        
class node(generic_type):
    """
    Handles a url request information.
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'node',
            'url' : None,
            'urlparse' : None,
            'status' : None,
            'links' : [],
            'parent': None,
            'children' : []
        }
        
        super(node, self).__init__(**kwargs)
        
        if not self.url:
            raise Exception("Node object must be created with a url")
        
        self.set_prop('url', self.normalize(self.get_prop('url')))#first step is to normalize all urls
        self.set_prop('urlparse', urlparse(self.get_prop('url')))
        self.request()
    
    def normalize(self, link):
        """
        Take a string link similar to /admissions
        Return a valid url like http://otc.edu/admissions
        Use urlparse to get the pieces of the link.
        If essential components (scheme, netloc) are missing, attempt to use those from parent node
        """
        new_parsed = urlparse(link)
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
                '?'+new_parsed.query,
                #'#'+new_parsed.fragment
            ]
        except AttributeError as AEX:
            raise Exception("Could not normalize url. Url is mal-formed, or a relative url without a parent node. ORIGINAL ERROR: "+AEX.message)
        
        return ''.join(new_link)
    
    def request(self):
        """
        Request the url provided to the constructor.
        Set node url status code.
        Call scape() and set node links list.
        """
        urlparse = self.list_props['urlparse']
        conn = httplib.HTTPConnection(urlparse.netloc)
        conn.request('GET',urlparse.path)
        response = conn.getresponse()
        bytes_received = response.read()
        self.set_prop('status', response.status)
        self.set_prop('links', self.scrape(bytes_received))
    
    def scrape(self, data):
        """
        Use beautiful soup to get all the links off of the page.
        Return scraped links in set form.
        """
        links = set()
        soup = bs(data)
        tags = []
        tags.extend([tag['background'] for tag in soup.find_all(background=True)])
        tags.extend([tag['cite'] for tag in soup.find_all(cite=True)])
        tags.extend([tag['codebase'] for tag in soup.find_all(codebase=True)])
        tags.extend(filter(lambda tag: not tag['href'].startswith('mailto:'), soup.find_all(href=True)))
        tags.extend([tag['longdesc'] for tag in soup.find_all(longdesc=True)])
        tags.extend([tag['src'] for tag in soup.find_all(src=True)])
        
        
        # Extract urls from URI type attributes
        for t in tags:
            for background in re.findall('background=".*"', t):
                t = normalize(t.split('\"')[1])
                links.add(t)
            
            for cite in re.findall('cite=".*"', t):
                t = normalize(t.split('\"')[1])
                links.add(t)
            
            for codebase in re.findall('codebase=".*"', t):
                t = normalize(t.split('\"')[1])
                links.add(t)
            
            for href in re.findall('href=".*"', t):
                t = normalize(t.split('\"')[1])
                links.add(t)
            
            for longdesc in re.findall('longdesc=".*"', t):
                t = normalize(t.split('\"')[1])
                links.add(t)
            
            for src in re.findall('src=".*"', t):
                t = normalize(t.split('\"')[1])
                links.add(t)
        
        return links