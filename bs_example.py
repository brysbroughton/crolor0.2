from get_doc_example import *
#an http request is now stored in variable resbytes
from bs4 import BeautifulSoup as bs

soup = bs(resbytes)

anchors = filter(lambda x: not x['href'].startswith('mailto:'), soup.find_all('a', href=True))
images = [img['src'] for img in soup.find_all('img', src=True)]
scripts = [script['src'] for script in soup.find_all('script', src=True)]
#look for style, src as well

print 'a links found: ' + str(len(anchors))
print 'image links found: ' + str(len(images))
print 'script links found: ' + str(len(scripts))








