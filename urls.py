from resources.HelloWorld import HelloWorld
from resources.admin import AdminLoginResource, AdminResource
from resources.first_timers import FirstTimersResource, FirstTimersCSVUpload

def add_api_url_rule(api, resource_class, urls, endpoint=None):
    ''' 
    Add a url rule via flask_restful.Api().add_resource() function

    :param api(flask_restul.Api): The flask_restful.Api instance to attach the url rule to

    :param resource_class(flask_restful.Resource): The resource class that contains the request handlers functions

    :param urls(list): A list of the urls that are handled by the :resource_class:. Each entry(url) in the list is a string

    :param endpoint(str): The name of the url rule. Deafults to the name of the :resource_class:
    '''
    api.add_resource(
        resource_class,
        *urls,
        endpoint=endpoint
    )


def url_register(api):
    # add the api url rules
    for url_info in URLS_FOR_API:
        add_api_url_rule(
            api, resource_class=url_info['class'],
            urls=url_info['urls'], endpoint=url_info['endpoint']
        )

URLS_FOR_API = [
    {
        # for testing responsiveness of the api
        'class':HelloWorld,
        'urls':[
            '/',
        ], 
        'endpoint':'hello'
    },
    {
        # the endpoint for admin creation, deletion and updating
        'class':AdminResource,
        'urls':[
            '/admin/', # post with parameters to add new admin
        ], 
        'endpoint':'admin'
    },
    {
        # endpoint to login for admin
        'class':AdminLoginResource,
        'urls':[
            '/adminlogin/', # use get to login
        ],
        'endpoint':'adminlogin'
    },
    {
        # endpoint for getting and adding new first timers
        'class':FirstTimersResource,
        'urls':[
            '/first_timers/', # use get to obtain first timers and post to add new ones
        ],
        'endpoint':'first_timers'
    },
    {
        # endpoint for adding new first timers from csv file
        'class':FirstTimersCSVUpload,
        'urls':[
            '/dataset/', # use post to upload/import the csv file
        ],
        'endpoint':'dataset'
    },
]