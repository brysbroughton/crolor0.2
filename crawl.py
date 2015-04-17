from urlparse import urlparse, urljoin
from bs4 import BeautifulSoup as bs
import httplib
import re

class crawl(object):

    link_in = None
    seed = None # replace by parsed link_in
    skip_pattern = None
    visited_links = set([])#ensure links are normalized before getting added here

    def __init__(self, seed_link):
        parsed = urlparse(seed_link)
        if not (parsed.netloc and parsed.scheme):
            raise Exception("Can't crawl malformed url: %s" % seed_link)
        self.seed = parsed
        
    



class node(object):

    link_in = None
    link_parsed = None
    skip_pattern = None
    links = []
    bytes_received = None
    parent_node = None
    seed = None

    def __init__(self, link_in):
        self.link_in = self.normalize_link(link_in)
        self.link_parsed = parse_link_in = urlparse(self.link_in)
        if not parse_link_in.netloc:
            raise Exception("Can't follow link with invalid host %s" % link_in)

    def normalize_link(self, link):
        """
        Take a string link similar to /admissions
        Return a valid url like http://otc.edu/admissions
        Use urlparse to get the pieces of the link.
        If essential components (scheme, netloc) are missing, use those from self.link_in
        """
        new_parsed = urlparse(link)
        #relative paths are tricky
        new_path = new_parsed.path
        if new_path.startswith('/'):
            pass
        else:
            if self.link_parsed:
                new_path = (self.link_parsed.path + '/' + new_parsed.path).replace('//','/')
        new_link = [
            (new_parsed.scheme or self.link_parsed.scheme) + '://',
            new_parsed.netloc or self.link_parsed.netloc,
            new_path,
            new_parsed.query
        ]
        
        return ''.join(new_link)
    
    def request_page(self):
        """
        Request the url provided to the constructor
        """
        valid_link = self.normalize_link(self.link_in)
        link_parts = urlparse(self.link_in)
        conn = httplib.HTTPConnection(link_parts.netloc)
        conn.request('GET',link_parts.path)
        response = conn.getresponse()
        self.bytes_received = response.read()
        
        print response.status
        print response.reason
    
    def scrape_links(self):
        """
        Use beautiful soup to get all the links off of the page.
        Return as list
        """
        soup = bs(self.bytes_received)
        anchors = filter(lambda x: not x['href'].startswith('mailto:'), soup.find_all('a', href=True))

        for a in anchors:
            href = re.search('href="(.+?)"', str(a))

            if href:
                url = href.group(1)

                if url.startswith('/'):
                    url = self.normalize_link(url)

                if '#' not in url:
                    self.links.append((url, None))
                    
        return self.links

    def compile_statuses(self, links):
        """
        Compile status codes of links into the links list.
        """
        
        for l in self.links:
            status = l[1]
            str_link = urlparse(l[0])
            conn = httplib.HTTPConnection(str_link.hostname)
            conn.request('GET', str_link.path)
            res = conn.getresponse()

            if not status:
                status = res.status
                l = list(l)
                l[1] = status
                l = tuple(l)
    
    def follow(self, link):
        """
        Create new crawl object on the input link
        """
        pass
