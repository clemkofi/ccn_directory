from resources.HelloWorld import HelloWorld


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
    # {
    #     'class':CollegeResource,
    #     'urls':[
    #         '/colleges/',  # get all the colleges 
    #         '/colleges/<int:college_id>/', #list all the faculties and departments in a college
    #     ], 
    #     'endpoint':'college'
    # },
    # {
    #     'class':FacultyResource,
    #     'urls':[
    #         '/faculty/', # get all the faculties 
    #         '/faculty/<int:faculty_id>/',  #list all the departments that in a faculty
    #     ], 
    #     'endpoint':'faculty'
    # },
    # {
    #     'class':DepartmentResource,
    #     'urls':[
    #         '/department/', # get all the faculties 
    #     ], 
    #     'endpoint':'department'
    # },
    # {
    #     'class':LecturerResource,
    #     'urls':[
    #         '/lecturer/', # use post to create a new lecturer
    #         '/lecturer/',  
    #         #'college_id' : '1' or '' if the focus is not the college level lecturers,
    #         #'faculty_id' : '1' or '' if the focus is not the faculty level lecturers,
    #         #'department_id' : '1' or '' if the focus is not the department level lecturers,
    #     ], 
    #     'endpoint':'lecturer'
    # },
    # {
    #     'class':LecturerLoginResource,
    #     'urls':[
    #         '/lecturerlogin/', # use post to create a new lecturer
    #     ],
    #     'endpoint':'lecturerlogin'
    # },
    # {
    #     'class':StaffResource,
    #     'urls':[
    #         '/staff/', # use post to create a new lecturer
    #     ], 
    #     'endpoint':'staff'
    # },
    # {
    #     'class':StaffLoginResource,
    #     'urls':[
    #         '/stafflogin/', # use post to create a new lecturer
    #     ],
    #     'endpoint':'stafflogin'
    # },
    # {
    #     'class':ClaimRequestResource,
    #     'urls':[
    #         '/claims/', # use post to create a new lecturer ---- use the get request to get the claims that are uncompleted
    #     ],
    #     'endpoint':'claims'
    # },
    # {
    #     'class':ClaimItemsResource,
    #     'urls':[
    #         '/claimitems/', # use post to create a new lecturer ---- use the get request to get the claims that are uncompleted
    #     ],
    #     'endpoint':'claimsitems'
    # },
    # {
    #     'class':AdminResource,
    #     'urls':[
    #         '/admin/', # use post to create a new lecturer
    #     ], 
    #     'endpoint':'admin'
    # },
    # {
    #     'class':AdminLoginResource,
    #     'urls':[
    #         '/adminlogin/', # use post to create a new lecturer
    #     ],
    #     'endpoint':'adminlogin'
    # },
    # {
    #     'class':ClaimCompleteResource,
    #     'urls':[
    #         '/claimcomplete/', # use post to create a new lecturer
    #     ],
    #     'endpoint':'claimcomplete'
    # },
    # {
    #     'class':ApproveRequestResource,
    #     'urls':[
    #         '/approve_request/', # use post to create a new lecturer
    #     ],
    #     'endpoint':'approve_request'
    # },
]