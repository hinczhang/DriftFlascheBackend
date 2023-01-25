from flask_restful import Resource
from flask import Response,request
import json
import pymongo
import jwt
import time
from configparser import ConfigParser
import base64
# opt
conn = ConfigParser()
conn.read("./conf.ini")

# mongoDB
# mongoDB
mongo_user = conn.get('mongodb','user')
mongo_passwd = conn.get('mongodb','password')
mongo_url = conn.get('mongodb','url')
mongo_port = conn.get('mongodb','port')
client = pymongo.MongoClient("mongodb://{0}:{1}@{2}:{3}/".format(mongo_user, mongo_passwd, mongo_url, mongo_port))
db = client["mobile"]
col = db["users"]

# token config
headers = {
  "alg": "HS256",
  "typ": "JWT"
}
salt = conn.get('key','token_key')
exp = int(time.time() + 1)

#return useful information
class Login(Resource):
    def get(self):#block get method
        pass
    def post(self):#open post method
        form = request.form.to_dict()
        res = None
        if(form["mode"] == "login"):
            res = self.__login__(form['username'], form['password'], form['keep'])
        elif(form["mode"] == "token"):
            res = self.__token__(form)
        else:
            res = self.__register__(form)
        return res
    
    def __token_encoder__(self, password, username, truename, keep):
        exp_time = int(time.time() + 60*60*24*7) if keep else int(time.time()+ 60*60*24)
        payload = {"username": username, "password": password, "truename": truename, "keep": 1 if keep==True else 0, "exp": exp_time}
        return jwt.encode(payload=payload, key=salt, algorithm='HS256', headers=headers)

    def __token_decoder__(self, token):
        try:
            info = jwt.decode(jwt = token, key = salt, verify=True, algorithms='HS256')
            print(info)
            token = self.__token_encoder__(info["password"], info["username"], info["truename"],info["keep"] == 1)
            return [True, token, info['username'], info["truename"]]
        except Exception as e:
            print(repr(e))
            return False, None, None, None
    
    def __encoder__(self, password):
        return base64.b64encode(password.encode('utf-8'))

    def __decoder__(self, password):
        return base64.b64decode(password)

    def __register__(self, form):
        query = {'username': form['username']}
        doc = list(col.find(query))
        data = None
        if len(doc) == 0:
            col.insert_one({'username': form['username'], 'password': self.__encoder__(form['password']), 'truename': form['truename']})
            data = json.dumps({'status': 0, 'msg': 'Registration success! Please login.'})
        else:
            data = json.dumps({'status': 1, 'msg': 'User already exists!'})
        res = Response(response=data, status=200, mimetype="application/json")#send message to frontend
        return res
    
    def __token__(self, form):
        print(form["token"])
        valid, token, username, truename = self.__token_decoder__(form["token"])
        data = None
        if(valid):
            data = json.dumps({'status': 0, 'msg': 'Token login success!', 'token': token, 'username': username, 'truename': truename})
        else:
            data = json.dumps({'status': 1, 'msg': 'Invalid token!'})
        res = Response(response = data, status = 200, mimetype="application/json")
        return res

    def __login__(self, username, password, keep):
        query = {'username': username}
        doc = list(col.find(query))
        data = None
        if len(doc) == 0:
            data = json.dumps({'status': 1, 'msg': 'User not exists!'})
        else:
            flag = str(self.__decoder__(doc[0]['password']), 'utf-8')==str(password)
            if(flag):
                truename = doc[0]['truename']
                data = json.dumps({'status': 0, 'msg': 'Login success!', 'username': username, 'truename': truename ,'token': self.__token_encoder__(password, username, truename, keep)})
            else:
                data = json.dumps({'status': 2, 'msg': 'Invalid password'})
        res = Response(response=data, status=200, mimetype="application/json")
        return res

