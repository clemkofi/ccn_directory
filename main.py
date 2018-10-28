from flask_restful import Api
from urls import url_register
from apiapp import create_app
from flask_cors import CORS

#get the name of the app
app = create_app()

api = Api(app)

# go to the urls and then add them to the resources of the api
url_register(api)

# @app.after_request
# def after_request(response):
#     '''
#     Called after every request, when returning the response.
#     We add extra fields to the response header.
#     :param response(flask_restful.Response): The response returned for the current request
#     '''
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Methods',
#                          'POST, GET, OPTIONS, DELETE')
#     response.headers.add('Access-Control-Allow-Headers',
#                          'Content-Type')
#     return response
   
CORS(app)

# starting the app
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')