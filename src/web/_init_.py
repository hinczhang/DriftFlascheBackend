from flask import Flask, request, redirect, url_for
from flask_restful import Api
from flask_cors import CORS

#start import block; free edit
from web.resource.login import Login
from web.resource.bottle import ManageBottle

#end import block

app = Flask(__name__)
CORS(app, supports_credentials=True) # CORS handle

'''add api resource'''
api = Api(app)

#start mode-use block; free edit
api.add_resource(Login, '/api/login')
api.add_resource(ManageBottle, '/api/bottle')

#end mode-use block
