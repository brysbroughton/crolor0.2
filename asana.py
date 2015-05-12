# Created with help from Pandemics https://github.com/pandemicsyn/asana/blob/master/asana/asana.py 
import json, requests

asana = {
    'apikey' : '5QV5zJFw.M3sUT3ja9v8ySDMA3SUjGqY',
    'url' : 'https://app.asana.com/api/1.0/tasks/',
    'host' : 'app.asana.com',
    'scheme' : 'https',
    'path': '/api/1.0/tasks/'
}

links_task_template = {
    #'assignee' : '20613987251546',#broughtb
    'followers[0]' : '20613987251546',
    'name' : 'Broken Link Report', #add department name to this
    'notes' : 'Created by Crolor automatic link checker',
    'projects' : '32910344974978', #links project
    'workspace' : '20613813963070' #Web Services workspace
}

def pushlogtotask(task_details, file_name):
    data = {'data':task_details}
    r = requests.post(asana['url'], auth=(asana['apikey'], ''), data=json.dumps(data))
    task = json.loads(r._content)
    return uploadattachment(task['data']['id'], file_name)

def uploadattachment(task_id, file_name):
    """
    Takes an asana task id, and the name of a file. Uploads file to asana task.
    It is assumed that the file is in the current directory.
    """
    attpath = asana['url'] + str(task_id) + '/attachments'
    stream = open(file_name, 'rb')
    files = {'file':(file_name, stream)}
    r = requests.post(attpath, auth=(asana['apikey'], ''), files=files)
    return r
