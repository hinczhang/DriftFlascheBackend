from flask_restful import Resource
from flask import Response,request
import json
import pymongo
from configparser import ConfigParser
import jwt
from bson.objectid import ObjectId
from geopy.distance import geodesic
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
col = db["bottles"]
# token config
headers = {
  "alg": "HS256",
  "typ": "JWT"
}
salt = conn.get('key','token_key')

def validate_token(token, username):
    try:
        info = jwt.decode(jwt = token, key = salt, verify=True, algorithms='HS256')
        if username == info["username"]:
            return True
        else:
            return False
    except Exception as e:
        print(repr(e))
        return False



class ManageBottle(Resource):
    def get(self):#block get method
        pass
    def post(self):#open post method
        form = request.form.to_dict()
        res = None
        print(form)
        if validate_token(form["token"], form["username"]):
            if(form["mode"] == "add"):
                res = self.__add_bottle__(form)
            elif(form["mode"] == "search"):
                res = self.__search_bottle_(form)
            elif(form["mode"] == "comment"):
                res = self.__comment_bottle__(form)
            elif(form["mode"] == "delete"):
                return self.__delete_bottle__(form)
            elif(form["mode"] == "mybottle"):
                res = self.__my_bottle__(form)
            else:
                res = Response(response = json.dumps({'status': 1, 'msg': 'Invalid mode! Please contact the developer'}), status = 200, mimetype="application/json")  
        else:
            res = Response(response = json.dumps({'status': 2, 'msg': 'Invalid operations! Will come back to the login page.'}), status = 200, mimetype="application/json")
        return res

    def __add_bottle__(self, form):
        try:
            col.insert_one({"username": form["username"], "content": form["content"], "type": form["type"], "affiliate": [], "position": {"lat": form["lat"], "lng": form["lng"]}})
            return Response(response = json.dumps({'status': 0, 'msg': 'Add successfully!'}), status = 200, mimetype="application/json")
        except Exception as e:
            print(repr(e))
            return Response(response = json.dumps({'status': 3, 'msg': 'Database Error'}), status = 200, mimetype="application/json")

    def __search_bottle_(self, form):
        distance = float(form["distance"])
        if(distance>=100):
            distance = 1145141919
        doc = list(col.find())
        array = []
        flag = True if "types" in form.keys() else False
        choose_type = None
        if flag:
            choose_type = set(form["types"].split(";"))
        for item in doc:
            if(geodesic((float(item["position"]["lat"]), float(item["position"]["lng"])), (float(form["lat"]), float(form["lng"]))).km <= distance):
                if flag:
                    if item["type"] in choose_type:
                        array.append(item)
                        array[-1]["_id"] = str(array[-1]["_id"])
                else:
                    array.append(item)
                    array[-1]["_id"] = str(array[-1]["_id"])
        return Response(response = json.dumps({"data": array, "msg": "Get data successfully!", "status": 0}), status = 200, mimetype="application/json")

    def __my_bottle__(self, form):
        query = {'username': form["username"]}
        doc = list(col.find(query))
        for index in range(len(doc)):
            doc[index]["_id"] = str(doc[index]["_id"])
        return Response(response = json.dumps({"data": doc, "msg": "Get data successfully!", "status": 0}), status = 200, mimetype="application/json")

    def __delete_bottle__(self, form):
        query = {'_id': ObjectId(form["id"])}
        col.delete_one(query)
        return Response(response = json.dumps({"msg": "Delete data successfully!", "status": 0}), status = 200, mimetype="application/json")
    
    def __comment_bottle__(self, form):
        print(form)
        query = {'_id': ObjectId(form["id"])}
        print(query)
        doc = list(col.find(query))[0]["affiliate"]
        print(doc)
        doc.append({"username": form["username"], "content": form["content"]})
        print(doc)
        col.update_one(query, {"$set":{"affiliate": doc}})
        return Response(response = json.dumps({"msg": "Insert data successfully!", "status": 0}), status = 200, mimetype="application/json")


