from resources.db import DatabaseReq
from flask import request, jsonify
from flask_restful import Resource, reqparse
from apiapp import pass_generator, get_timestamp, get_current_timestamp, get_date_from_timestamp, get_token_for_user
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from decorators import token_required

class AdminResource(Resource):
    '''
    Request for creating, updating, deleting and getting all information for the Admins in the system
    '''
    def post(self):
        # print typeAuth
        #check from the token authentication to ensure that the user is a lecturer and is allowed to perform this task
        # if typeAuth != "admin":
        #     return jsonify({'Statuscode' : '200', 'message' : 'You are not allowed to perform this action!'})

        #parse the arguments for the post request
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='username of the Admin')
        parser.add_argument('password', type=str, help='password of the Admin')
        parser.add_argument('name', type=str, help='name of the Admin')
        parser.add_argument('position', type=str, help='position of the Admin')
        parser.add_argument('number', type=str, help='number of the Admin')
        args = parser.parse_args()

        #give the last update time of the Data
        args['last_update_time'] = get_current_timestamp()

        # hash the password and then save it 
        args['v_code'] = generate_password_hash(args['password'], method='sha256')

        #get the public id from the uuid
        args['public_id'] = str(uuid.uuid4())

        #adding the arguemnts to a list
        args_to_pass = []
        args_to_pass.append(args['name'])
        args_to_pass.append(args['number'])
        args_to_pass.append(args['position'])
        args_to_pass.append(args['v_code'])
        args_to_pass.append(args['username'])
        args_to_pass.append(args['public_id'])
        args_to_pass.append(args['last_update_time'])
        

        #creating a cursor from the db class
        arg_data = DatabaseReq().get_cursor(proc_name='spInsertNewAdmin', mode='post', args=args_to_pass)

        if arg_data=="success":
            return {'Statuscode':'200', 'Message':'Admin creation successful'}
        else: 
            return {'Statuscode':'600', 'Message':arg_data}


class AdminLoginResource(Resource):
    '''
    Request for authenticating and authorization of an admin
    '''

    def get(self):
        # this function performs token authentication for the admin

        # getting the variables
        auth = request.authentication

        if not auth or not auth.username or not auth.password:
            return jsonify({"message" : "Could not verify! Login required!", "Statuscode" : "401"})

        # login info admin
        args_login = auth.username

        # cursor to get admin details from the database 
        data_one_admin = DatabaseReq().get_cursor(proc_name='spGetAdminLogin', mode='postget', args=[args_login])

        if len(data_one_admin) > 0:
            admininfo = []
            hashed_vcode = ""

            #use a for loop to iterate through the result
            for item in data_one_admin:
                if item[6] is 0:
                    continue
                i = {
                        'admin_name' : item[1],
                        'public_id' : item[7]
                }

                admininfo.append(i)
                hashed_vcode = item[4]

            if check_password_hash(hashed_vcode, auth.password):
                token_to_give = get_token_for_user(public_id=admininfo[0]['public_id'], admin_name=admininfo[0]['admin_name'], typeAuth='admin')

                return jsonify({"Statuscode" : "200", "tokenObtained" : token_to_give})
        
        return jsonify({"message" : "Could not verify! Login required!", "Statuscode" : "401"})