
class generic_type(object):
    """
    General template for associating properties to actions. To be extended by other crol classes.

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

    def __extend_props__(self, key, value):
        self.props[key] = value

    def __init__(self, **kwargs):
        self.props = {'type' : 'generic'}
        self.args = kwargs

    def __use_args__(self):
        for key, val in self.args.iteritems():
            if self.props.has_key(key):
                self.props[key] = val
            else:
                raise Exception('%s object has no property: %s' % self.props['type'], key)



class registration(generic_type):
    """
    Object that associates a department to a website and actions.

    department: department object
    site: dep.otc.edu/artment
    actions: list of action objects
    
    """

    def __init__(self, **kwargs):
        super(registration, self).__init__(**kwargs)
        self.set_property('type', 'registration')
        self.__extend_props__('department', None)
        self.__extend_props__('site', '')
        self.__extend_props__('actions', [])
        self.__use_args__()

        

class department(generic_type):
    """
    Object handles information for an orgnaizational entity associated with a crawl

    type : department
    name : department_name
    main_email : department@otc.edu
    email_group : [an@email.com, another@email.edu]
    
    """

    def __init__(self, **kwargs):
        super(department, self).__init__(**kwargs)
        self.set_property('type', 'department')
        self.__extend_props__('name', 'unnamed department')
        self.__extend_props__('main_email', 'web@otc.edu')
        self.__extend_props__('email_group', [])
        self.__use_args__()




class registry(generic_type):
    """
    Object handles the listing of sites to crawl and associates them to departments.
    """


    def __init__(self, *args):
        self.__extend_props__('registrations', [])



