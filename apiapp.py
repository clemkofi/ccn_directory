from flask import Flask
import global_config as G
import random
import string
from datetime import datetime, timedelta
import time
import jwt

DEFAULT_APP_NAME = 'ccn_directory'


def create_app(app_name=None):
    if app_name is None:
        app_name = DEFAULT_APP_NAME
    
    app = Flask(app_name)

    configure_db(app)

    configure_mail_for_notification(app)

    return app

def configure_db(app):
    #MySQL configurations
    app.config['MYSQL_DATABASE_USER'] = G.MYSQL_DATABASE_USER
    app.config['MYSQL_DATABASE_PASSWORD'] = G.MYSQL_DATABASE_PASSWORD
    app.config['MYSQL_DATABASE_DB'] = G.MYSQL_DATABASE_DB
    app.config['MYSQL_DATABASE_HOST'] = G.MYSQL_DATABASE_HOST

def configure_mail_for_notification(app):
    # Mail Server Configurations
    app.config['MAIL_SERVER']=G.MAIL_SERVER
    app.config['MAIL_PORT'] = G.MAIL_PORT
    app.config['MAIL_USERNAME'] = G.MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = G.MAIL_PASSWORD
    app.config['MAIL_USE_TLS'] = G.MAIL_USE_TLS
    app.config['MAIL_USE_SSL'] = G.MAIL_USE_SSL

def pass_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_timestamp(date):
    '''
    function to convert any date to timestamp
    '''
    #convert string date to datetime tuple format
    datetuple = datetime.strptime(date, '%Y-%m-%d')
    return int(time.mktime(datetuple.timetuple()))

def get_timestamp_from_time(time):
    '''
    function to get the time to timestamp
    '''
    #convert string time to datetime tuple format and then to timestamp
    string_date_time_to_use = "2017-10-10" + time
    time_tuple = time.strptime(string_date_time_to_use, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(time_tuple))

def get_current_timestamp():
    '''
    function to convert current date and time to timestamp
    '''
    #convert current time and date to timestamp    
    return int(time.mktime(datetime.now().timetuple()))

def get_duration_from_timestamps(start_time, end_time):
    return int((end_time - start_time)/3600)

def get_date_from_timestamp(timestamp):
    '''
    function to get the date from the timestamp
    '''
    #convert the timestamp to date without the time
    return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d")


def get_date_for_today():
    '''
    function to get the date for today well formated
    '''
    return datetime.today()

def add_days_to_date_get_timestamp(add_days):
    '''
    function to add a number of days to a date and then convert to a timestamp
    '''
    return int(time.mktime((datetime.now().date() + timedelta(days=add_days)).timetuple()))

def get_token_for_user(public_id=None, admin_name="", typeAuth=None):
    '''
    function that is used to get a token for a user when they login
    '''
    # an app variable is created
    app = create_app()
    app.config['SECRET'] = "OurSecret"
    token = jwt.encode({'public_id' : public_id, 'admin_name' : admin_name, 'typeAuth' : typeAuth, 'exp' : datetime.utcnow() + timedelta(weeks=12)}, app.config['SECRET'], algorithm='HS256')

    return token.decode('UTF-8')

def parse_token(token):
    '''
    function that parses the token to get the values out 
    '''
    # an app variable is created
    app = create_app()
    app.config['SECRET'] = "OurSecret"
    return jwt.decode(token, app.config['SECRET'], algorithms='HS256')