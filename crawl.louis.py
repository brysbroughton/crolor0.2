from urlparse import urlparse, urljoin
from bs4 import BeautifulSoup as bs
import httplib
import re

class crawl:

    link_in = None
    skip_pattern = None
    links = []
    bytes_received = None

    def __init__(self, link_in=None):
        if link_in:
            self.link_in = link_in
            parse_link_in = urlparse(link_in)
            if not parse_link_in.netloc:
                raise Exception("Can't follow link with invalid host %s" % link_in)
    
    
    def normalize_link(self, link):
        """
        Take a string link similar to /admissions
        Return a valid url like http://otc.edu/admissions
        Use urlparse to get the pieces of the link.
        If essential components (scheme, netloc) are missing, use those from self.link_in
        """
        host = 'http://www.otc.edu/'
        new_link = urljoin(host, link)
        self.link = new_link
        
        return new_link
        
    
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
    
    def scrape_links(self, links):
        """
        Use beautiful soup to get all the links off of the page.
        Return as list
        """
        self.links = links
        soup = bs(resbytes)
        anchors = filter(lambda x: not x['href'].startswith('mailto:'), soup.find_all('a', href=True))

        for a in anchors:
            href = re.search('href="(.+?)"', str(a))

            if href:
                url = href.group(1)

                if url.startswith('/'):
                    url = normalize_link(url)

                if '#' not in url:
                    self.links.append((url, None))
                    
        return links

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
