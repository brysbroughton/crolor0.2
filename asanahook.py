import urllib, urllib2, httplib, json, base64, string, six, requests

asana = {
    'apikey' : '5QV5zJFw.M3sUT3ja9v8ySDMA3SUjGqY',
    'url' : 'https://app.asana.com/api/1.0/tasks/',
    'host' : 'app.asana.com',
    'scheme' : 'https',
    'path': '/api/1.0/tasks/'
}

links_project = {
    'assignee' : '20613987251546',#broughtb
    'followers[0]' : '20613987251546',
    'name' : 'Broken Link Report', #add department name to this
    'notes' : '',
    'projects' : '32910344974978', #links project
    'workspace' : '20613813963070' #Web Services workspace
}


def pushtask(data=None, files=None):
    data = {'data':links_project}
    r = requests.post(asana['url'], auth=(asana['apikey'], ''), data=json.dumps(data), files=files)
    print r.status_code
    return r

def posttask(data=None, files=None):
    data = {'data':links_project}
    r = requests.post(asana['url'], auth=(asana['apikey'], ''), data=json.dumps(data), files=files)
    print r.status_code
    return r

def getinfo():
    #auth = get_basic_auth()
    r = requests.get(asana['url']+'?project=31595995443650', auth=(asana['apikey'], ''))
    print r.status_code
    return r
    
def get_basic_auth():
    s = six.b(asana['apikey']+':')
    return base64.b64encode(s).rstrip()


