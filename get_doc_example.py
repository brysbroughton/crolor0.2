import httplib

conn = httplib.HTTPConnection('www.otc.edu')
conn.request('GET','/online/online.php')
response = conn.getresponse()
resbytes = response.read()

print response.status
print response.reason
print '\n\n'
print resbytes
