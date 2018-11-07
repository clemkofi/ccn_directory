from resources.db import DatabaseReq
from flask import request, jsonify
from flask_restful import Resource, reqparse
from apiapp import get_timestamp, get_current_timestamp, get_date_from_timestamp
import calendar
import uuid
from decorators import token_required
from werkzeug.utils import secure_filename
import os

class FirstTimersResource(Resource):
    '''
    Request for adding (one or bulk people), updating info of first timers
    '''
    # /first_timers/ => all first timers with no order
    # /first_timers/?most_recent=1 => 20 most recent first timers
    # /first_timers/?month_added=10&year=2018 => list all first timers in a particular month 
    # /first_timers/?date_added=2211225536 => list all first timers on a particular date
    # /first_timers/?ft_id=ft_id&stu=1 = one first timer with the id given
    @token_required
    def get(self, currentUser, typeAuth):
        try:
            data_first_timers = []
            # print request.args.keys()
            # print int(request.args.values()[0])

            # this check the param used in the request and makes a decision based on that
            if request.args.keys() != []:
                param_used = ''
                key_index = 0

                if len(request.args.keys()) == 1:
                    param_used = request.args.keys()[0]

                if len(request.args.keys()) >= 1:
                    key_index = len(request.args.keys()) - 1
                    param_used = request.args.keys()[key_index]
                
                print request.args.keys()

                if param_used == 'most_recent':
                    if int(request.args.values()[0]) == 1:
                        data_first_timers = DatabaseReq().get_cursor(proc_name='spGet20FirstTimers', mode='get')
                    else:
                        return {'Statuscode' : '400', 'Message' : 'No Names found!'}

                if param_used == 'month_added':
                    month = int(request.args.values()[0])
                    year = int(request.args.values()[1])

                    if not month or not year:
                        return {'Statuscode' : '400', 'Message' : 'Month/Year not specified!'}
                    
                    # gets the timestamp for the start of the month => first day of the month
                    start_month_timestamp = get_timestamp(str(year) + "-" + str(month) + "-01")

                    # gets the timestamp for the end of the month => last day of the month 
                    # using the calendar module with month range and then using the second 
                    # in the tuple 
                    end_month_timestamp = get_timestamp(str(year) + "-" + str(month) + "-" + str(calendar.monthrange(year, month)[1]))
                    print start_month_timestamp, end_month_timestamp
                        
                    data_first_timers = DatabaseReq().get_cursor(proc_name='spGetFirstTimersForMonth', mode='get', args=[start_month_timestamp, end_month_timestamp])

                if param_used == 'date_added':
                    date_added = int(request.args.values()[0])

                    if not date_added:
                        return {'Statuscode' : '400', 'Message' : 'Date not specified!'}

                    data_first_timers = DatabaseReq().get_cursor(proc_name='spGetFirstTimersForDay', mode='get', args=[date_added])

                if param_used == 'ft_id':
                    print 'ok'
                    first_timer_id = int(request.args.values()[key_index])
                    data_first_timer = []
                    print first_timer_id

                    # data_first_timer = DatabaseReq().get_cursor(proc_name='spGetOneFirstTimer', mode='get', args=[first_timer_id])

                    # get the residential address if the person is a student or not
                    if int(request.args.values()[key_index - 1]) == 1:
                        data_first_timer = DatabaseReq().get_cursor(proc_name='spGetOneStudentInfo', mode='get', args=[first_timer_id])
                        if (len(data_first_timer)>0):
                            First_Timer_info = []

                            #use a for loop to iterate through the result
                            for item in data_first_timer:
                                i = {
                                    'id':item[0],
                                    'name':item[1],
                                    'tel_number':item[2],
                                    'email':item[3],
                                    'dob':item[4],
                                    'attendance_date':item[5],
                                    'occupation':item[6],
                                    'work_place':item[7],
                                    'inviter':item[8],
                                    'member':item[9],
                                    'student':item[10],
                                    'school':item[11],
                                    'programme':item[12],
                                    'hall_hostel':item[13],
                                    'room_no':item[14],
                                    'area':item[15],
                                }

                                First_Timer_info.append(i)

                            return {'Statuscode':'200','First_timers':First_Timer_info}

                    if int(request.args.values()[1]) == 0:
                        data_first_timer = DatabaseReq().get_cursor(proc_name='spGetOneNonStudentInfo', mode='get', args=[first_timer_id])
                        if (len(data_first_timer)>0):
                            First_Timer_info = []

                            #use a for loop to iterate through the result
                            for item in data_first_timer:
                                i = {
                                    'id':item[0],
                                    'name':item[1],
                                    'tel_number':item[2],
                                    'email':item[3],
                                    'dob':item[4],
                                    'attendance_date':item[5],
                                    'occupation':item[6],
                                    'work_place':item[7],
                                    'inviter':item[8],
                                    'member':item[9],
                                    'student':item[10],
                                    'residence':item[11],
                                    'house_no':item[12],
                                    'landmark':item[13]
                                }

                                First_Timer_info.append(i)

                            return {'Statuscode':'200','First_timers':First_Timer_info}

            else:
                # create a cursor to get all the first timers in no particular order
                data_first_timers = DatabaseReq().get_cursor(proc_name='spGetAllFirstTimers', mode='get')

            print data_first_timers
            if (len(data_first_timers)>0):
                First_Timers_list = []

                #use a for loop to iterate through the result
                for item in data_first_timers:
                    i = {
                        'id':item[0],
                        'name':item[1],
                        'tel_number':item[2],
                        'email':item[3],
                        'dob':item[4],
                        'attendance_date':item[5],
                        'occupation':item[6],
                        'work_place':item[7],
                        'inviter':item[8],
                        'member':item[9],
                        'student':item[10]
                    }

                    First_Timers_list.append(i)

                return {'Statuscode':'200','First_timers':First_Timers_list}

            return {'Statuscode' : '400', 'Message' : 'No result found!'}

        except Exception as e:
            return{'error' : str(e)}


    # /first_timers/ => with post parameters
    # => id, name, tel_number, email, dob, 
    # => attendance_date, occupation, work_place,
    # => inviter, member, student, 
    # => **student == school, programme, hall_hostel, room_no, area
    # => **non_student == residence, house_no, landmark
    @token_required
    def post(self, currentUser, typeAuth):
        try:
            # parse all arguments from the post request
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, help='name of the person')
            parser.add_argument('tel_number', type=str, help='number of the person')
            parser.add_argument('email', type=str, help='email of the person')
            parser.add_argument('dob', type=str, help='dob of the person')
            parser.add_argument('attendance_date', type=str, help='date of attendance')
            parser.add_argument('occupation', type=str, help='occupation of the person')
            parser.add_argument('work_place', type=str, help='work place of the person')
            parser.add_argument('inviter', type=str, help='inviter of the person')
            parser.add_argument('member', type=int, help='member or not')
            parser.add_argument('student', type=int, help='student or not')
            parser.add_argument('school', type=str, help='school of the person')
            parser.add_argument('programme', type=str, help='programme of the person')
            parser.add_argument('hall_hostel', type=str, help='hall_hostel of the person')
            parser.add_argument('room_no', type=str, help='room_no of the person')
            parser.add_argument('area', type=str, help='area of the person')
            parser.add_argument('residence', type=str, help='residence of the person if not student')
            parser.add_argument('house_no', type=str, help='house_no of the person if not student')
            parser.add_argument('landmark', type=str, help='landmark of the person if not student')
            
            args = parser.parse_args()

            # adding the arguemnts to a list
            args_to_pass = []
            args_to_pass.append(args['name'])
            args_to_pass.append(args['tel_number'])
            args_to_pass.append(args['email'])
            args_to_pass.append(args['occupation'])
            args_to_pass.append(args['work_place'])
            args_to_pass.append(args['inviter'])
            args_to_pass.append(args['member'])
            args_to_pass.append(args['student'])
            args_to_pass.append(get_timestamp(args['dob']))
            args_to_pass.append(get_timestamp(args['attendance_date']))
            
            # creating a cursor from the db class
            arg_data = DatabaseReq().get_cursor(
                proc_name='spInsertNewFirstTimer', mode='post', args=args_to_pass)

            if arg_data == "success":
                # get the id of the new entry
                data_get_for_entry = DatabaseReq().get_cursor(proc_name='spGetOneFirstTimer', mode='get', args=[args['tel_number']])
                entry_id = 0
                print data_get_for_entry
                for item in data_get_for_entry:
                    entry_id = int(item[0])

                if int(args['student']) == 1:
                    args_for_students = []
                    args_for_students.append(entry_id)
                    args_for_students.append(args['school'])
                    args_for_students.append(args['programme'])
                    args_for_students.append(args['hall_hostel'])
                    args_for_students.append(args['room_no'])
                    args_for_students.append(args['area'])

                    student_info_data = DatabaseReq().get_cursor(proc_name='spInsertNewStudentFirstTimer', mode='post', args=args_for_students)

                    if student_info_data == "success":
                        return {'Statuscode': '200', 'Message': 'First Timer Successfully added!'}
                    else:
                        return {'Statuscode': '600', 'Message': student_info_data}

                if int(args['student']) == 0:
                    args_for_ns = []
                    args_for_ns.append(entry_id)
                    args_for_ns.append(args['residence'])
                    args_for_ns.append(args['house_no'])
                    args_for_ns.append(args['landmark'])

                    nstudent_info_data = DatabaseReq().get_cursor(proc_name='spInsertNewNonStudentFirstTimer', mode='post', args=args_for_ns)

                    if nstudent_info_data == "success":
                        return {'Statuscode': '200', 'Message': 'First Timer Successfully added!'}
                    else:
                        return {'Statuscode': '600', 'Message': nstudent_info_data}

            else:
                return {'Statuscode': '600', 'Message': 'First Timer details not successfully added!'}
                
        except Exception as e:
            return{'error' : str(e)}

    # /admin/?a_id=public_id
    # with form data to update the current admin details
    @token_required
    def put(self, currentUser, typeAuth):
        try:
            # parse all arguments from the post request
            parser = reqparse.RequestParser()
            parser.add_argument('ft_id', type=str, help='id of the person')
            parser.add_argument('name', type=str, help='name of the person')
            parser.add_argument('tel_number', type=str, help='number of the person')
            parser.add_argument('email', type=str, help='email of the person')
            parser.add_argument('dob', type=str, help='dob of the person')
            parser.add_argument('attendance_date', type=str, help='date of attendance')
            parser.add_argument('occupation', type=str, help='occupation of the person')
            parser.add_argument('work_place', type=str, help='work place of the person')
            parser.add_argument('inviter', type=str, help='inviter of the person')
            parser.add_argument('member', type=int, help='member or not')
            parser.add_argument('student', type=int, help='student or not')
            parser.add_argument('school', type=str, help='school of the person')
            parser.add_argument('programme', type=str, help='programme of the person')
            parser.add_argument('hall_hostel', type=str, help='hall_hostel of the person')
            parser.add_argument('room_no', type=str, help='room_no of the person')
            parser.add_argument('area', type=str, help='area of the person')
            parser.add_argument('residence', type=str, help='residence of the person if not student')
            parser.add_argument('house_no', type=str, help='house_no of the person if not student')
            parser.add_argument('landmark', type=str, help='landmark of the person if not student')
            
            args = parser.parse_args()

            # first_timer id
            first_timer_id = args['ft_id']

            #create cursor to get just one first timer based on his/her id
            data_ft_check = DatabaseReq().get_cursor(proc_name='spGetOneFirstTimerID', mode='get', args=[first_timer_id])

            if (len(data_ft_check)==1):
                # adding the arguemnts to a list
                args_to_pass = []
                args_to_pass.append(args['ft_id'])
                args_to_pass.append(args['name'])
                args_to_pass.append(args['tel_number'])
                args_to_pass.append(args['email'])
                args_to_pass.append(args['occupation'])
                args_to_pass.append(args['work_place'])
                args_to_pass.append(args['inviter'])
                args_to_pass.append(args['member'])
                args_to_pass.append(args['student'])
                args_to_pass.append(args['dob'])
                args_to_pass.append(args['attendance_date'])

                # creating a cursor from the db class
                arg_data = DatabaseReq().get_cursor(
                    proc_name='spUpdateFirstTimer', mode='post', args=args_to_pass)

                if arg_data == "success":
                    if int(args['student']) == 1:
                        args_for_students = []
                        args_for_students.append(args['ft_id'])
                        args_for_students.append(args['school'])
                        args_for_students.append(args['programme'])
                        args_for_students.append(args['hall_hostel'])
                        args_for_students.append(args['room_no'])
                        args_for_students.append(args['area'])

                        student_info_data = DatabaseReq().get_cursor(proc_name='spUpdateStudentFirstTimer', mode='post', args=args_for_students)

                        if student_info_data == "success":
                            return {'Statuscode': '200', 'Message': 'First Timer update Successful!'}
                        else:
                            return {'Statuscode': '600', 'Message': student_info_data}

                    if int(args['student']) == 0:
                        args_for_ns = []
                        args_for_ns.append(args['ft_id'])
                        args_for_ns.append(args['residence'])
                        args_for_ns.append(args['house_no'])
                        args_for_ns.append(args['landmark'])

                        nstudent_info_data = DatabaseReq().get_cursor(proc_name='spUpdateNonStudentFirstTimer', mode='post', args=args_for_ns)

                        if nstudent_info_data == "success":
                            return {'Statuscode': '200', 'Message': 'First Timer update Successfully!'}
                        else:
                            return {'Statuscode': '600', 'Message': nstudent_info_data}
                else:
                    return {'Statuscode': '700', 'Message': arg_data}
            else:
                return {'Statuscode':'600', 'Message':'Update unsuccessful!'}

        except Exception as e:
            return{'error': str(e)}

    # /first_timers/?ft_id=ft_id 
    # to delete particular first timer
    @token_required
    def delete(self, currentUser, typeAuth):
        try:
            #parse the arguments for the delete request
            parser = reqparse.RequestParser()
            parser.add_argument('ft_id', type=str, help='id of the first timer')

            args = parser.parse_args()

            first_timer_id = args['ft_id']

            #create cursor to get just one First timer based on his/her id
            data_ft_check = DatabaseReq().get_cursor(proc_name='spGetOneFirstTimerID', mode='get', args=[first_timer_id])

            if (len(data_ft_check)>0):
                #create a cursor to delete the user based on his/her id
                data_ft_delete = DatabaseReq().get_cursor(proc_name='spDeleteOneFirstTimer', mode='del', args=[first_timer_id])

                if data_ft_delete=="success":
                    return {'Statuscode':'200', 'Message':'Entry successfully deleted'}
                else: 
                    return {'Statuscode':'700', 'Message':data_ft_delete}
            else:
                return {'Statuscode':'600', 'Message':'No result found'}

        except Exception as e:
            return{'error': str(e)}




class FirstTimersCSVUpload(Resource):
    '''
    Importing a CSV of first timers to be inserted into the db
    '''
    # /first_timers/dataset/
    @token_required
    def post(self, currentUser, typeAuth):
        try:
            # data_csv = request.files['file'].read()
            # get the file uploaded
            data_csv = request.files['file']

            if data_csv:
                filename = secure_filename(data_csv.filename)
                print filename
                file_path = os.path.join('./uploads',filename)
                print file_path
                data_csv.save(os.path.join('./uploads',filename))
                print "ok"

                # TODO
                # carter for student and nonstudents

                # use the cursor to upload file to db
                data_upload = DatabaseReq().load_data(file_path, 'first_timers')

                if data_upload == "success":
                    return {'Statuscode': '200', 'Message' : 'Data successfully uploaded!'}
                else:
                    return {'Statuscode' : '700', 'Message' : 'Upload failed ... Try Again!'}

            # return {'Statuscode': '200', 'Message' : 'Read Succesfully'}
            return {'Statuscode': '600', 'Message' : 'No File Uploaded ... Try again!'}
        except Exception as e:
            return{'error' : str(e)}
