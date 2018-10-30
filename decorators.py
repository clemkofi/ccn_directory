from threading import Thread
from flask import request, jsonify
from apiapp import parse_token, get_date_from_timestamp
from resources.db import DatabaseReq


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

def token_required(f):
    def decorated_token_checker(*args, **kwags):
        token = None

        #check the header for token header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'Statuscode' : '401', 'message' : 'Token is missing. User not authenticated!!'})

        try:
            data_from_token = parse_token(token)
            typeAuth = data_from_token['typeAuth']

            print typeAuth

            if typeAuth == "admin":
                #create cursor to get just one lecturer based on his public id
                data_one_admin = DatabaseReq().get_cursor(proc_name='spGetOneAdmin', mode='get', args=[data_from_token['public_id']])

                if len(data_one_admin) > 0:
                    currentUser = []

                    #use a for loop to iterate through the result
                    for item in data_one_admin:
                        if item[6] is 0:
                            continue
                        i = {
                                'public_id':item[8],
                        }

                        currentUser.append(i)

                    return f(f, currentUser, typeAuth)

            return jsonify({'Statuscode' : '401', 'message' : 'Token is missing!'})

        except:
            return jsonify({'Statuscode' : '401', 'message' : 'Token Expired. User not authenticated!!'})
    
    return decorated_token_checker