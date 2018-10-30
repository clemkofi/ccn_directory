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
    #/admin/ = all Admins
    #/admin/?a_id=public_id = one Admin with public id
    @token_required
    def get(self, currentUser, typeAuth):
        try:
            admin_id = request.args.get('a_id')

            if admin_id is None:
                # creating a cursor from the db class to get all Admins
                data_all_Admins = DatabaseReq().get_cursor(
                    proc_name='spGetAllAdmins', mode='get')
            else:
                # create cursor to get just one Admin based on his public id
                data_all_Admins = DatabaseReq().get_cursor(
                    proc_name='spGetOneAdmin', mode='get', args=[admin_id])

            if (len(data_all_Admins)>0):
                AdminList = []

                #use a for loop to iterate through the result
                for item in data_all_Admins:
                    i = {
                        'id':item[0],
                        'name':item[1],
                        'number':item[2],
                        'position':item[3],
                        'username':item[5],
                        'is_active':item[6],
                        'public_id':item[8]
                    }

                    AdminList.append(i)

                return {'Statuscode':'200','Admins':AdminList}
            else: 
                return {'Statuscode':'600', 'Message':'No result found'}

        except Exception as e:
            return{'error' : str(e)}

    # /admin/ => with post parameters 
    # => username, password, name, position, number
    @token_required
    def post(self, currentUser, typeAuth):
        # print typeAuth
        # check from the token authentication to ensure that the user is a lecturer and is allowed to perform this task
        # if typeAuth != "admin":
        #     return jsonify({'Statuscode' : '200', 'message' : 'You are not allowed to perform this action!'})

        # parse the arguments for the post request
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='username of the Admin')
        parser.add_argument('password', type=str, help='password of the Admin')
        parser.add_argument('name', type=str, help='name of the Admin')
        parser.add_argument('position', type=str, help='position of the Admin')
        parser.add_argument('number', type=str, help='number of the Admin')
        args = parser.parse_args()

        # give the last update time of the Data
        args['last_update_time'] = get_current_timestamp()

        # hash the password and then save it
        args['v_code'] = generate_password_hash(
            args['password'], method='sha256')

        # get the public id from the uuid
        args['public_id'] = str(uuid.uuid4())

        # adding the arguemnts to a list
        args_to_pass = []
        args_to_pass.append(args['name'])
        args_to_pass.append(args['number'])
        args_to_pass.append(args['position'])
        args_to_pass.append(args['v_code'])
        args_to_pass.append(args['username'])
        args_to_pass.append(args['public_id'])
        args_to_pass.append(args['last_update_time'])

        # creating a cursor from the db class
        arg_data = DatabaseReq().get_cursor(
            proc_name='spInsertNewAdmin', mode='post', args=args_to_pass)

        if arg_data == "success":
            return {'Statuscode': '200', 'Message': 'Admin creation successful'}
        else:
            return {'Statuscode': '600', 'Message': arg_data}

    # /admin/?a_id=public_id
    # with form data to update the current admin details
    @token_required
    def put(self, currentUser, typeAuth):
        try:
            #parse the arguments for the delete request
            parser = reqparse.RequestParser()
            parser.add_argument('a_id', type=str, help='public id of the Admin')
            parser.add_argument('username', type=str, help='username of the Admin')
            parser.add_argument('name', type=str, help='name of the Admin')
            parser.add_argument('position', type=str, help='position of the Admin')
            parser.add_argument('number', type=str, help='number of the Admin')
            parser.add_argument('active', type=int, help='admin active or not')

            args = parser.parse_args()

            # give the last update time of the Data
            args['last_update_time'] = get_current_timestamp()

            admin_public_id = args['a_id']

            #create cursor to get just one Admin based on his public id
            data_Admin_check = DatabaseReq().get_cursor(proc_name='spGetOneAdmin', mode='get', args=[admin_public_id])

            if (len(data_Admin_check)==1):
                # adding the arguemnts to a list
                args_to_pass = []
                args_to_pass.append(admin_public_id)
                args_to_pass.append(args['username'])
                args_to_pass.append(args['name'])
                args_to_pass.append(args['position'])
                args_to_pass.append(args['number'])
                args_to_pass.append(args['active'])
                args_to_pass.append(args['last_update_time'])

                # creating a cursor from the db class
                arg_data = DatabaseReq().get_cursor(
                    proc_name='spUpdateAdmin', mode='post', args=args_to_pass)

                if arg_data == "success":
                    return {'Statuscode': '200', 'Message': 'Admin update successful'}
                else:
                    return {'Statuscode': '700', 'Message': arg_data}
            else:
                return {'Statuscode':'600', 'Message':'No such user found'}

        except Exception as e:
            return{'error': str(e)}


    # /admin/?a_id=public_id 
    # to delete particular admin
    @token_required
    def delete(self, currentUser, typeAuth):
        try:
            #parse the arguments for the delete request
            parser = reqparse.RequestParser()
            parser.add_argument('a_id', type=str, help='public id of the Admin')

            args = parser.parse_args()

            admin_public_id = args['a_id']

            #create cursor to get just one Admin based on his public id
            data_Admin_check = DatabaseReq().get_cursor(proc_name='spGetOneAdmin', mode='get', args=[admin_public_id])

            if (len(data_Admin_check)>0):
                #create a cursor to delete the user based on his public_id
                data_Admin_delete = DatabaseReq().get_cursor(proc_name='spDeleteOneAdmin', mode='del', args=[admin_public_id])

                if data_Admin_delete=="success":
                    return {'Statuscode':'200', 'Message':'Admin successfully deleted'}
                else: 
                    return {'Statuscode':'700', 'Message':data_Admin_delete}
            else:
                return {'Statuscode':'600', 'Message':'No such user found'}

        except Exception as e:
            return{'error': str(e)}

class AdminLoginResource(Resource):
    '''
    Request for authenticating and authorization of an admin
    '''

    def post(self):
        # this function performs token authentication for the admin

        #parse the arguments for the delete request
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='username of the Admin')
        parser.add_argument('password', type=str, help='password of the Admin')
        auth = parser.parse_args()

        if not auth or not auth['username'] or not auth['password']:
            return jsonify({"message": "Could not verify! Login required!", "Statuscode": "401"})

        # login info admin
        args_login = auth['username']

        # cursor to get admin details from the database
        data_one_admin = DatabaseReq().get_cursor(
            proc_name='spGetAdminLogin', mode='postget', args=[args_login])

        if len(data_one_admin) > 0:
            admininfo = []
            hashed_vcode = ""

            # use a for loop to iterate through the result
            for item in data_one_admin:
                if item[6] is 0:
                    continue
                i = {
                    'admin_name': item[1],
                    'public_id': item[8]
                }

                admininfo.append(i)
                hashed_vcode = item[4]

            if check_password_hash(hashed_vcode, auth['password']):
                token_to_give = get_token_for_user(
                    public_id=admininfo[0]['public_id'], admin_name=admininfo[0]['admin_name'], typeAuth='admin')

                return jsonify({"Statuscode": "200", "tokenObtained": token_to_give})

        return jsonify({"message": "Could not verify! Login required!", "Statuscode": "401"})
