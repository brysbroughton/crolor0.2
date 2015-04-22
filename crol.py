from bs4 import BeautifulSoup as bs
from urlparse import urlparse
import re
import os
import sys
from datetime import datetime

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
            'actions' : []
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
            'page_reports' : [],
            'url_reports' : []#not sure if use
        }
    
        super(CrawlReport, self).__init__(**kwargs)
        
        if self.props['page_reports']:
            setattr(self, 'page_reports', [PageReport(r) for r in self.props['page_reports']])

        if self.props['url_reports']:
            setattr(self, 'url_reports', [UrlReport(r) for r in self.props['url_reports']])
            
            
            
class PageReport(GenericType):
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
        
        super(PageReport, self).__init__(**kwargs)
        
        if self.props['url_reports']:
            setattr(self, 'url_reports', [UrlReport(r) for r in self.props['url_reports']])

            
class UrlReport(GenericType):
    """
    Object for handling url and the response received when it is requested.
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'url_report',
            'url' : None,
            'linked_from' : None
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
            'urlparse' : None,
            'status' : None,
            'links' : [],
            'parent': None,
            'children' : []
        }
        
        super(Node, self).__init__(**kwargs)
        
        if not self.url:
            raise Exception("Node object must be created with a url")
        
        self.setprop('url', self.normalize(self.getprop('url')))#first step is to normalize all urls
        self.setprop('urlparse', urlparse(self.getprop('url')))
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
        urlparse = self.listprops['urlparse']
        conn = httplib.HTTPConnection(urlparse.netloc)
        conn.request('GET',urlparse.path)
        response = conn.getresponse()
        bytes_received = response.read()
        self.setprop('status', response.status)
        self.setprop('links', self.scrape(bytes_received))
    
    def scrape(self, data):
        """
        Use beautiful soup to get all the links off of the page.
        Return scraped links in set form.
        """
        links = set()
        soup = bs(data)
        tags = []
        attrs = ['background', 'cite', 'codebase', 'href', 'longdesc', 'src']
        
        for a in attrs:
            tags.extend([tag[a] for tag in soup.find_all({a:True})])
        
        # Extract urls from URI type attributes
        for t in tags:
            for a in attrs:
                for url in re.findall(a+'=".*"', t):
                    if not url.startswith('mailto:'):
                        url = normalize(url.split('\"')[1])
                        links.add(url)
        
        return links


class Log(GenericType):
    

    def __init__(self, kwargs={}):
        self.props = {
                'type' : 'log',
                'path' : './',
                'filename' : 'croler',
                'endfilename' : '.log.txt',
                'head_text' : 'header\n',
                'foot_text' : 'footer',
                'filePointer' : None,
                "row_before" : '',
                "row_after" : '',
                "col_before" : '',
                "col_after" : '',
                "heading_row" : []
            }
        super(Log, self).__init__(**kwargs)
        
    def openfile(self):
        date = datetime.now()
        date = date.strftime('%m%d%y%I%M%S')
        self.setprop('filePointer', open(self.path+self.filename+date+self.endfilename, 'a'))
        self.writefile(self.head_text)
        self.headingrow(self.heading_row)
        
    def writefile(self, new_val):
        self.filePointer.write(new_val)
        self.filePointer.flush()
        os.fsync(self.filePointer)

    def closefile(self):
        self.writefile(self.foot_text)
        self.filePointer.close

    def writerow(self, cols):
        self.writefile(self.row_before)
        for item in cols:
            self.writefile(self.col_before + item + self.col_after)
        self.writefile(self.row_after)
    
    def headingrow(self, headings=None):
        if headings:
            self.writefile(self.row_before)
            for header in  headings:
                self.writefile(self.col_before)
                self.writefile(header)
                self.writefile(self.col_after)
        else:
            self.writefile(self.heading_row)
        self.writefile(self.row_after)

class WebLog(Log):
    def __init__(self, kwargs={}):
        self.props = {
                'type' : 'weblog',
                'path' : './',
                'filename' : 'webLog',
                'endfilename' : '.log.html',
                'head_text' : '<html><head></head><body><table>',
                'foot_text' : '</table></body></html>',
                'filePointer' : None,
                "row_before" : '<tr>',
                "row_after" : '</tr>',
                "col_before" : '<td>',
                "col_after" : '</td>',
                "heading_row" : ['Column 1', 'Column 2','Column 3','Column 4']
            }
        #super(WebLog, self).__init__(**kwargs)
        super(WebLog, self).__init__(self.props)



def webTest():
    rows = [["Much Longer item than the rest of these items", "another", "still more", "last one"],["Line2", "A little longer than most others", "Row 2", "End of Row"],["Line3", "Third Row ", "Row 3", "longest one in the third row"]]
    w=WebLog()
    #w=WebLog({'heading_row':['ONE', 'TWO','THREE','FOUR'],'endfilename':'.log.html','filename':'htmlLog','head_text':'<html><head></head><body><table>', 'foot_text':'</table></body></html>','row_before':'<tr>','row_after':'</tr>','col_before':'<td>','col_after':'</td>'})
    w.listprops()
    w.openfile()
    for row in rows:
        w.writerow(row)
    w.closefile()
def test():
    l=Log({'heading_row':['Column 1', 'Column 2','Column 3','Column 4'],'filename':'textformat','endfilename':'.log.txt','row_before':'','row_after':'\n','col_before':'','col_after':','})
    l.openfile()
    l.writerow(["Much Longer item than the rest of these items", "another", "still more", "last one"])
    l.writerow(["Line2", "A little longer than most others", "Row 2", "End of Row"])
    l.writerow(["Line3", "Third Row ", "Row 3", "longest one in the third row"])
    l.closefile()


