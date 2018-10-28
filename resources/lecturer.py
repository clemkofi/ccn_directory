from resources_classes.db import DatabaseReq
from flask import request, jsonify
from flask_restful import Resource, reqparse
from apiapp import pass_generator, get_timestamp, get_current_timestamp, get_date_from_timestamp, get_token_for_user
from notification_service.notification_mail import password_notification
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from decorators import token_required
# from werkzeug.security import generate_password_hash, check_password_hash

class LecturerResource(Resource):
    '''
    Request for creating, updating, deleting and getting all information for the lecturers in the system
    '''
    @token_required
    def post(self, currentUser, typeAuth):
        ok_pass_go_on = 0
        #check from the token authentication to ensure that the user is a lecturer and is allowed to perform this task
        if typeAuth == "staff":
            if currentUser[0]['privilege'] == "HR":
                ok_pass_go_on = 1
        elif typeAuth ==  "admin":
            ok_pass_go_on = 1
        else:
            return jsonify({'Statuscode' : '200', 'message' : 'You are not allowed to add lecturer'})
            
        if ok_pass_go_on == 0:
            return jsonify({'Statuscode' : '200', 'message' : 'You are not allowed to add lecturer'})

        try:
            #parse the arguments for the post request
            parser = reqparse.RequestParser()
            parser.add_argument('surname', type=str, help='surname of the lecturer')
            parser.add_argument('other_names', type=str, help='other names of the lecturer')
            parser.add_argument('dob', type=str, help='date of birth of the lecturer')
            parser.add_argument('phone', type=str, help='active phone number')
            parser.add_argument('email', type=str, help='active email address')
            parser.add_argument('Group_id', type=str, help='id for the group the lecturer has been added to')
            parser.add_argument('department_id', type=str, help='id for the department the lecturer has been assigned to')
            args = parser.parse_args()

            #convert the dob to timestamp
            args['dob'] = get_timestamp(date=args['dob'])

            #generate password for the Lecturer
            new_password = pass_generator()
            args['vcode'] = new_password

            #then hash the password to be stored in the db
            hashed_password = generate_password_hash(new_password, method='sha256')

            #give the last update time of the Data
            args['last_update_time'] = get_current_timestamp()

            #get the public id from the uuid
            args['public_id'] = str(uuid.uuid4())

            #adding the arguemnts to a list
            args_to_pass = []
            args_to_pass.append(args['surname'])
            args_to_pass.append(args['other_names'])
            args_to_pass.append(args['dob'])
            args_to_pass.append(args['phone'])
            args_to_pass.append(args['email'])
            args_to_pass.append(args['Group_id'])
            args_to_pass.append(args['department_id'])
            args_to_pass.append(hashed_password)
            args_to_pass.append(args['last_update_time'])
            args_to_pass.append(args['public_id'])

            #creating a cursor from the db class
            arg_data = DatabaseReq().get_cursor(proc_name='spInsertNewLecturer', mode='post', args=args_to_pass)

            if arg_data=="success":
                password_notification(args)
                return jsonify({'Statuscode':'200', 'Message':'Lecturer creation successful'})
            else: 
                return jsonify({'Statuscode':'600', 'Message':arg_data})

        except Exception as e:
            return{'error' : str(e)}

    #/lecturer/ = all lecturers
    #/lecturer/?p_id=public_id = one lecturer with public id
    @token_required
    def get(self, currentUser, typeAuth):
        ok_pass_go_on = 0
        #check from the token authentication to ensure that the user is a lecturer and is allowed to perform this task
        if typeAuth == "staff":
            ok_pass_go_on = 1
        elif typeAuth ==  "admin":
            ok_pass_go_on = 1
        else:
            return jsonify({'Statuscode' : '200', 'message' : 'You are not allowed to add lecturer'})
            
        if ok_pass_go_on == 0:
            return jsonify({'Statuscode' : '200', 'message' : 'You are not allowed to add lecturer'})

        try:
            public_id = request.args.get('p_id')

            if public_id is None:
                #creating a cursor from the db class to get all lecturers
                data_all_lecturers = DatabaseReq().get_cursor(proc_name='spGetAllLecturers', mode='get')
            else:
                #create cursor to get just one lecturer based on his public id
                data_all_lecturers = DatabaseReq().get_cursor(proc_name='spGetOneLecturer', mode='get', args=[public_id])

            if (len(data_all_lecturers)>0):
                lecturerList = []

                #use a for loop to iterate through the result
                for item in data_all_lecturers:
                    if item[6] is 1:
                        continue
                    i = {
                        'surname':item[1],
                        'other_names':item[2],
                        'dob':item[3],
                        'phone':item[4],
                        'email':item[5],
                        'account_setup':item[7],
                        'public_id':item[8],
                        'vcode':item[9],
                        'Group_id':item[11],
                        'Department_id':item[12]
                    }
                    
                    #change date of birth to readable format
                    i['dob'] = get_date_from_timestamp(timestamp=i['dob']) 
                    lecturerList.append(i)

                print len(lecturerList)

                return jsonify({'Statuscode':'200','Lecturers':lecturerList})
            else: 
                return jsonify({'Statuscode':'600', 'Message':'No result found'})

        except Exception as e:
            return{'error' : str(e)}


    def delete(self):
        try:
            #parse the arguments for the delete request
            parser = reqparse.RequestParser()
            parser.add_argument('p_id', type=str, help='public_id of the lecturer')

            args = parser.parse_args()

            public_id = args['p_id']

            #create cursor to get just one lecturer based on his public id
            data_lecturer_check = DatabaseReq().get_cursor(proc_name='spGetOneLecturer', mode='get', args=[public_id])

            if (len(data_lecturer_check)>0):
                #create a cursor to delete the user based on his public_id
                data_lecturer_delete = DatabaseReq().get_cursor(proc_name='spDeleteOneLecturer', mode='del', args=[public_id])

                if data_lecturer_delete=="success":
                    return jsonify({'Statuscode':'200', 'Message':'Lecturer successfully deleted'})
                else: 
                    return jsonify({'Statuscode':'700', 'Message':data_lecturer_delete})
            else:
                return jsonify({'Statuscode':'600', 'Message':'No such user found'})

        except Exception as e:
            return{'error': str(e)}


class LecturerLoginResource(Resource):
    '''
    Request for creating, updating, deleting and getting all information for the lecturers in the system
    '''
    def post(self):
        #parse the arguments for the post request
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, help='active email address')
        parser.add_argument('vcode', type=str, help='active vcode to use')
        args = parser.parse_args()

        #login info for the Lecturer
        args_login = []
        args_login.append(args['email'])
        args_login.append(args['vcode'])

        #create cursor to get just one lecturer based on his public id
        data_all_lecturers = DatabaseReq().get_cursor(proc_name='spGetLecturerLogin', mode='postget', args=args_login)

        if (len(data_all_lecturers)>0):
            lecturerinfo = []

            #use a for loop to iterate through the result
            for item in data_all_lecturers:
                if item[6] is 1:
                    continue
                i = {
                        'surname':item[1],
                        'other_names':item[2],
                        'dob':item[3],
                        'phone':item[4],
                        'email':item[5],
                        'account_setup':item[7],
                        'public_id':item[8],
                        'vcode':item[9],
                        'Group_id':item[11],
                        'Department_name':item[14],
                }
                    
                #change date of birth to readable format
                i['dob'] = get_date_from_timestamp(timestamp=i['dob']) 
                lecturerinfo.append(i)

            return jsonify({'Statuscode':'200','Lecturer':lecturerinfo})
        else: 
            return jsonify({'Statuscode':'600', 'Message':'Authentication Failed ... No such user'})

    def get(self):
        #this is a function that implements the token authentication when a user logs in

        # this gets the auth variables from the request .... 
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return jsonify({"message" : "Could not verify! Login required!", "Statuscode" : "401"})
        
        #login info for the Lecturer
        args_login = auth.username

        #create cursor to get just one lecturer based on his public id
        data_one_lecturer = DatabaseReq().get_cursor(proc_name='spGetLecturerLogin2', mode='postget', args=[args_login])

        if len(data_one_lecturer) > 0:
            lecturerinfo = []
            hashed_vcode = ""

            #use a for loop to iterate through the result
            for item in data_one_lecturer:
                if item[6] is 1:
                    continue
                i = {
                        'public_id':item[8],
                        'Group_id':item[11],
                        'Department_id':item[13],
                }

                lecturerinfo.append(i)
                hashed_vcode = item[9]

            if check_password_hash(hashed_vcode, auth.password):
                token_to_give = get_token_for_user(lecturerinfo[0]['public_id'], lecturerinfo[0]['Department_id'], typeAuth='lecturer')

                return jsonify({"Statuscode" : "200", "tokenObtained" : token_to_give})
        
        return jsonify({"message" : "Could not verify! Login required!", "Statuscode" : "401"})

