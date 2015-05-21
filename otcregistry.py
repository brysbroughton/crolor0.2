
registry_data = {
    'registrations' : [
        {
            'site' : 'http://www.otc.edu/webservices',
            'department' : {
                'name' : 'Web Services',
                'email_group' : ['wrighta@otc.edu']
            },
            'actions' : [('excellog', 'email'), ('weblog', 'email')],
            'nofollow_patterns' : ['^.*disclaimer.*$','^.*reddot.*$'],
            'ignore_patterns' : ['^.*jpg.*$','^.*png.*$']
        },
        {
            'site' : 'http://www.otc.edu/news/',
            'department' : {
                'name' : 'Public Relations',
                'email_group' : ['wrighta@otc.edu'],
            },
            'actions' : [('excellog', 'email'), ('weblog', 'asana', 'email')]
        },
        {
            'site' : 'http://www.otc.edu/it',
            'department' : {
                'name' : 'Technical Services',
                'email_group' : ['wrighta@otc.edu']
            },
            'actions' : [('excellog', 'email'), ('weblog', 'email')]
        }
    ]
}

registrations = registry_data['registrations']
