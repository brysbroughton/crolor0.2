
class generic_type(object):
    """
    General template for associating properties to actions.
    To be extended by other crol classes.

    type: generic
    
    """

    def set_prop(self, key, val):
        if self.props.has_key(key):
            self.props[key] = val
            setattr(self, key, val)
        else:
            raise Exception('%s has no property: %s' % (self.props['type'], key))

    def get_prop(self, key):
        if self.props.has_key(key):
            return self.props[key]
        else:
            raise Exception('%s has no property: %s' % (self.props['type'], key))
            
    def list_props(self):
        for key, val in self.props.iteritems():
            print "%s : %s" % (key, val)
            
    def __extend_props__(self, key, val=None):
        self.props[key] = val
        setattr(self, key, val)

    def __init__(self, **kwargs):
        self.props = self.props or {'type' : 'generic'}
        if not self.props.has_key('type'):
            raise Exception('Generic subtype must have a type specified in properties')
        for key, val in self.props.iteritems():
            self.set_prop(key, val)
        self.args = kwargs
        self.__use_args__()

    def __use_args__(self):
        for key, val in self.args.iteritems():
            if self.props.has_key(key):
                self.set_prop(key, val)
            else:
                raise Exception('%s object has no property: %s' % (self.props['type'], key))



class registration(generic_type):
    """
    Object that associates a department to a website and actions.

    department: department object
    site: dep.otc.edu/artment
    actions: list of action objects
    
    """

    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'registration',
            'department' : None,
            'site' : None,
            'actions' : []
        }

        super(registration, self).__init__(**kwargs)

        if self.props['department']:
            setattr(self, 'department', department(self.props['department']))

        

class department(generic_type):
    """
    Object handles information for an orgnaizational entity associated with a crawl

    type : department
    name : department_name
    main_email : department@otc.edu
    email_group : [an@email.com, another@email.edu]
    
    """

    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'department',
            'name' : None,
            'main_email' : None,
            'email_group' : []
        }

        super(department, self).__init__(**kwargs)




class registry(generic_type):
    """
    Object handles the listing of sites to crawl and associates them to departments.
    """

    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'registry',
            'registrations' : []
        }

        super(registry, self).__init__(**kwargs)

        if self.props['registrations']:
            setattr(self, 'registrations', [registration(r) for r in self.props['registrations']])
            
            
            
class crawl_report(generic_type):
    """
    Object instatiated 1-1 with a crawl job.
    
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'crawl_report',
            'seed_url' : None,
            'page_reports' : [],
            'url_reports' : []#not sure if use
        }
    
        super(crawl_report, self).__init__(**kwargs)
        
        if self.props['page_reports']:
            setattr(self, 'page_reports', [page_report(r) for r in self.props['page_reports']])

        if self.props['url_reports']:
            setattr(self, 'url_reports', [url_report(r) for r in self.props['url_reports']])
            
            
            
class page_report(generic_type):
    """
    Object for handling the reports of all links on its page
    """

    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'page_report',
            'page_url' : None,
            'page_status' : None,
            'url_reports' : []
        }
        
        super(page_report, self).__init__(**kwargs)
        
        if self.props['url_reports']:
            setattr(self, 'url_reports', [url_report(r) for r in self.props['url_reports']])

            
class url_report(generic_type):
    """
    Object for handling url and the response received when it is requested.
    """
    
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'url_report',
            'url' : None,
            'linked_from' : None
        }
        
        super(url_report, self).__init__(**kwargs)
        
