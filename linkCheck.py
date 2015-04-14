import httplib
from bs4 import BeautifulSoup as bs
conn = httplib.HTTPConnection('www.otc.edu')
urlList = ''
global badList
badList = ''
global allGoodLinks
allGoodLinks = "true"
def newConn(newURL):
    conn = httplib.HTTPConnection('www.otc.edu')
    conn.request('GET',newURL)
    global response
    global resbytes
    response = conn.getresponse()
    resbytes = response.read()

    soup = bs(resbytes)
    global anchors
    global images
    global scripts
    anchors = filter(lambda x: not x['href'].startswith('mailto:'), soup.find_all('a', href=True))
    images = [img['src'] for img in soup.find_all('img', src=True)]
    scripts = [script['src'] for script in soup.find_all('script', src=True)]
    #look for style, src as well

    #print 'a links found: ' + str(len(anchors))
    #print 'image links found: ' + str(len(images))
    #print 'script links found: ' + str(len(scripts))

newConn('/webservices/webservices.php')

def getHREFS():
    a_hrefs = [x['href'] for x in anchors]
    return a_hrefs

def printHREFS():
    hrefs = getHREFS()
    for x in hrefs:
        print x.encode("UTF-8")

def checkLinks():
    a_hrefs = getHREFS()
    for x in a_hrefs:
        global urlList
        global allGoodLinks
        global badList
        list(urlList).append(x)
        if urlList.count(x) < 2:
            newConn(x)
            #print str(x) + ": " + str(response.status)
            if response.status != 200 and response.status != 300 and response.status != 301 and response.status != 302:
                #print str(x) + ": " + str(response.status)
                global allGoodLinks
                allGoodLinks = "false"
                list(badList).append(x)
                
    if allGoodLinks == 'true':
        print "Links all have status codes of 200, 300, 301, or 302"
    else:
        print "Some links have status codes other than 200, 300, 301, or 302"
        print "Those links are: "
        for x in badList:
            print str(x)
    
    
            








