from urlparse import urlparse
import httplib

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
        
        new_link = ''
        
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
    
    def scrape_links(self):
        """
        Use beautiful soup to get all the links off of the page.
        Return as list
        """
        pass
    
    def follow(self, link):
        """
        create new crawl object on the input link
        """
        pass
