from get_doc_example import *
#an http request is now stored in variable resbytes
from bs4 import BeautifulSoup as bs
from urlparse import urlparse, urljoin
import httplib
import re

soup = bs(resbytes)

anchors = filter(lambda x: not x['href'].startswith('mailto:'), soup.find_all('a', href=True))
images = [img['src'] for img in soup.find_all('img', src=True)]
scripts = [script['src'] for script in soup.find_all('script', src=True)]
#look for style, src as well

print 'a links found: ' + str(len(anchors))
print 'image links found: ' + str(len(images))
print 'script links found: ' + str(len(scripts))

statuses = []

for a in anchors:
    href = re.search('href="(.+?)"', str(a))

    if href:
        url = href.group(1)
        
        if url.startswith('/'):
            host = 'http://www.otc.edu/'
            url = urljoin(host, url)

        if not url == '#':    
            statuses.append((url, None))

        #if '#' not in url:
        #    statuses.append((url, None))
        
def get_status(str_link):
    """
    Normalize input link.
    Do connection stuff.
    Get status code from response abd return it.
    """
    #urlparse to get host
    str_link = urlparse(str_link)
        
    conn = httplib.HTTPConnection(str_link.hostname)
    conn.request('GET', str_link.path)
    res = conn.getresponse()
    return res.status
    

for s in statuses:
    status = s[1]
    print 'URL: ' + str(s[0])
    
    if not status:
        status = get_status(s[0])
        print 'STATUS: ' + str(status) + '\n'
        s = list(s)
        s[1] = status
        s = tuple(s)
    
print 'Statuses found: ' + str(len(statuses))
