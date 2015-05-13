import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import os, sys, smtplib


def create_registry(filename):
    '''
    Open the xml file at the filename passed in
    Create the registry_data dictionary from the xml data
    '''
    
    tree = ET.parse('configuration.xml')
    root = tree.getroot()
    registry_data = {}
    registrations = []
    for registration in root:
        registration_data = {'site':'', 'department':{}, 'actions':[]}
        for reg_data in registration:
                if reg_data.tag == "site":
                    registration_data['site'] = reg_data.text
                elif reg_data.tag == "department":
                    department = {}
                    for data in reg_data:
                        if data.tag == "email_group":
                            email_group = []
                            for email in data:
                                email_group.append(email.text)
                            department["email_group"] = (email_group)
                        else:
                            data_dict = {data.tag : data.text}
                            department.update(data_dict)
                    registration_data['department'] = department
                else:
                    actions = []
                    for action in reg_data.findall('action'):
                        actions.append(action.text)
                    registration_data['actions'] = actions
        registrations.append(registration_data)
    registry_data['registrations'] = registrations
    return registry_data

def create_xml(registry_data, filename):
    '''
    Create new XML file from the passed in dictionary
    Save to the passed in filename
    '''
    
    f = open(filename, 'w')
    registrations = Element('registrations')
    for r in registry_data['registrations']:
        registration = SubElement(registrations, 'registration')
        for key in r:
            #print key, " = ", r[key]
            child = SubElement(registration, key)
            if key == 'site':
                child.text = r[key]
            elif key == 'department':
                for k in r[key]:
                    gchild = SubElement(child, k)
                    if k == 'name' or k == 'main_email':
                        gchild.text = r[key][k]
                    else:
                        for mails in r[key][k]:
                            emails = SubElement(gchild, 'member')
                            emails.text = mails
            elif key == 'actions':
                for action in r[key]:
                    actions = SubElement(child, 'action')
                    actions.text = action
    
    f.write(tostring(registrations))
    f.flush()
    os.fsync(f)
    f.close

#the filename where the xml file is located or where the new file will be stored
filename = 'configuration.xml'
fileexists = os.path.isfile(filename)
if fileexists:
    registry_data = create_registry(filename)
else:
    #Create the default dictionary of registry data
    registry_data = {
        'registrations' : [
            {
                'site' : 'https://www.otc.edu/FORMS/webtesting/emptyLink/',
                'department' : {
                    'name' : 'Crol Testing',
                    'main_email' : 'wrighta@otc.edu',
                    'email_group' : ['wrighta@otc.edu']
                },
                'actions': []
            },
            {
                'site' : 'http://www.otc.edu/webservices',
                'department' : {
                    'name' : 'Web Services',
                    'main_email' : 'wrighta@otc.edu',
                    'email_group' : ['broughtb@otc.edu','lamelzag@otc.edu']
                },
                'actions' : ['email', 'asana']
            },
            {
                'site' : 'http://www.otc.edu/news/',
                'department' : {
                    'name' : 'Public Relations',
                    'main_email' : 'wrighta@otc.edu',
                },
                'actions' : ['crawl','log']
            },
            {
                'site' : 'http://www.otc.edu/it',
                'department' : {
                    'name' : 'Technical Services',
                    'main_email' : 'wrighta@otc.edu'
                }
            }
        ]
    }
    create_xml(registry_data, filename)
    create_registry(filename)
    
    
registrations = registry_data['registrations']

