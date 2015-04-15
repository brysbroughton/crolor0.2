
class generic_type(object):
    """
    General template for associating properties to actions.
    To be extended by other crol classes.

    type: generic
    
    """

    def set_property(self, key, value):
        if self.props.has_key(key):
            self.props[key] = value
        else:
            raise Exception('Department has no property: %s' % key)

    def list_properties(self):
        for key, val in self.props.iteritems():
            print "%s : %s" % (key, val)

    def __extend_props__(self, key, value=None):
        self.props[key] = value

    def __init__(self, **kwargs):
        self.props = self.props or {'type' : 'generic'}
        self.args = kwargs
        self.__use_args__()

    def __use_args__(self):
        for key, val in self.args.iteritems():
            if self.props.has_key(key):
                self.props[key] = val
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
            self.props['department'] = department(self.props['department'])

        

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
            self.props['registrations'] = [registration(r) for r in self.props['registrations']]



