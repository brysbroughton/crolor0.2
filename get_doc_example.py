import httplib

conn = httplib.HTTPConnection('www.otc.edu')
conn.request('GET','/webservices/webservices.php')
response = conn.getresponse()

print response.status
print response.reason
print '\n\n'
print response.read()
