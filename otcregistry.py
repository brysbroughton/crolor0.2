
registry_data = {
    'registrations' : [
        {
            'site' : 'http://www.otc.edu/webservices',
            'department' : {
                'name' : 'Web Services',
                'email_group' : ['wrighta@otc.edu']
            },
            'actions' : ['email'],
            'nofollow_patterns' : ['^.*disclaimer.*$','^.*reddot.*$'],
            'ignore_patterns' : ['^.*jpg.*$','^.*png.*$']
        },
        {
            'site' : 'http://www.otc.edu/news/',
            'department' : {
                'name' : 'Public Relations',
                'email_group' : ['wrighta@otc.edu'],
            },
            'actions' : ['crawl','log']
        },
        {
            'site' : 'http://www.otc.edu/it',
            'department' : {
                'name' : 'Technical Services',
                'email_group' : ['wrighta@otc.edu']
            },
            'actions' : ['email']
        }
    ]
}

registrations = registry_data['registrations']
