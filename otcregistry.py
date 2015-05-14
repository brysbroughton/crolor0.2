
registry_data = {
    'registrations' : [
        {
            'site' : 'http://www.otc.edu/webservices',
            'department' : {
                'name' : 'Web Services',
                'main_email' : 'wrighta@otc.edu',
                'email_group' : ['broughtb@otc.edu','lamelzag@otc.edu']
            },
            'actions' : ['email'],
            'nofollow_patterns' : ['^.*disclaimer.*$','^.*reddot.*$']
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
            },
            'actions' : ['email']
        }
    ]
}

registrations = registry_data['registrations']
