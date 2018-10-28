from flaskext.mysql import MySQL
from apiapp import create_app
import logging as log

app = create_app()


class DatabaseReq(object):
    def __init__(self):
        try:
            # creating my sql instance
            mysql = MySQL()

            # initialize the MySQL
            mysql.init_app(app)

            # connection to mysql
            self._conn = mysql.connect()

            # cursor to interact with the database
            self._cursor = self._conn.cursor()

        except Exception as e:
            log.error(
                'Error in class %s :--- %s', self.__class__.__name__, e
            )
            raise e

    def get_cursor(self, proc_name, mode, args=[]):
        try:
            # arguments for he procedure
            proc_args = ()

            # temporary list to hold the args to be later converted to the proc_args tuple
            proc_list_temp = []

            if(len(args) > 0):
                for arg in args:
                    proc_list_temp.append(arg)

                # convert args in list to the tuple
                proc_args = tuple(proc_list_temp)

                print proc_name
                print proc_args

                # using the cursor with the stored procedure passed into the function
                self._cursor.callproc(proc_name, proc_args)

                # get the current cursor being used
                data = self._cursor.fetchall()

                if (mode=='post') or (mode=='del'):
                    if len(data) is 0:
                        self._conn.commit()
                        return "success"
                    
                    self._conn.commit()
                    return data
                else:
                    return data

            else:
                print proc_name
                print proc_args

                # using the cursor with the stored procedure passed into the function
                self._cursor.callproc(proc_name, proc_args)

                # get the current cursor being used
                return self._cursor.fetchall()
        except Exception as e:
            return{'error':'function error'}

