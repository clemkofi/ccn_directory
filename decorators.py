from threading import Thread
from flask import request, jsonify
from apiapp import parse_token, get_date_from_timestamp
from resources_classes.db import DatabaseReq


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

            if typeAuth == "lecturer":
                #create cursor to get just one lecturer based on his public id
                data_one_lecturer_staff_admin = DatabaseReq().get_cursor(proc_name='spGetOneLecturer', mode='get', args=[data_from_token['public_id']])

                if (len(data_one_lecturer_staff_admin)>0):
                    currentUser = []
                        
                    #use a for loop to iterate through the result
                    for item in data_one_lecturer_staff_admin:
                        if item[6] is 1:
                            return jsonify({'Statuscode' : '401', 'message' : 'User does not exist. User not authenticated!!'}) 
                        i = {
                            'use_lect' : item[0],
                            'surname': item[1],
                            'other_names': item[2],
                            'dob': item[3],
                            'phone': item[4],
                            'email': item[5],
                            'account_setup': item[7],
                            'public_id': item[8],
                            'vcode': item[9],
                            'Group_id': item[11],
                            'Department_id': item[12],
                        }

                        #change date of birth to readable format
                        i['dob'] = get_date_from_timestamp(timestamp=i['dob'])
                        currentUser.append(i)

                    return f(f, currentUser, typeAuth)
                
                
            if typeAuth == "staff":
                print "into"
                #create cursor to get just one lecturer based on his public id
                data_one_lecturer_staff_admin = DatabaseReq().get_cursor(proc_name='spGetOneStaff', mode='get', args=[data_from_token['public_id']])

                if (len(data_one_lecturer_staff_admin)>0):
                    currentUser = []
                        
                    #use a for loop to iterate through the result
                    for item in data_one_lecturer_staff_admin:
                        if item[6] is 1:
                            return jsonify({'Statuscode' : '401', 'message' : 'User does not exist. User not authenticated!!'}) 
                        i = {
                            'staff_id' : item[0],
                            'employee_id' : item[1],
                            'surname' : item[2],
                            'other_names': item[3],
                            'phone': item[4],
                            'email': item[5],
                            'public_id': item[7],
                            'vcode': item[8],
                            'privilege': item[9],
                            'department_id': item[11],
                            'faculty_id': item[12]
                        }

                        currentUser.append(i)

                    return f(f, currentUser, typeAuth)

            if typeAuth == "admin":
                #create cursor to get just one lecturer based on his public id
                data_one_admin = DatabaseReq().get_cursor(proc_name='spGetOneAdmin', mode='get', args=[data_from_token['public_id']])

                if len(data_one_admin) > 0:
                    currentUser = []

                    #use a for loop to iterate through the result
                    for item in data_one_admin:
                        if item[5] is 0:
                            continue
                        i = {
                                'public_id':item[4],
                        }

                        currentUser.append(i)

                    return f(f, currentUser, typeAuth)

            return jsonify({'Statuscode' : '401', 'message' : 'Token is missing!'})

        except:
            return jsonify({'Statuscode' : '401', 'message' : 'Token Expired. User not authenticated!!'})
    
    return decorated_token_checker