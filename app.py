
###################################
# Module
###################################
import json
from flask import Flask, jsonify, request, make_response
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime
import bson.json_util as json_util
from bson.objectid import ObjectId
from db import DB
###################################


###################################
# Flask Setup
###################################
app = Flask(__name__)

###################################


###################################
# Swagger Setup
###################################
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Todo List API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

###################################


###################################
# DB
###################################
users = DB().collection("users")
todos = DB().collection("todos")
###################################


###################################
# Function
###################################
def dumpObjectID(data):
    data["_id"] = str(ObjectId(data["_id"]))
    return data

def dumpObjectIDs(list):
    result = []
    for item in list:
        item["_id"] = str(ObjectId(item["_id"]))
        result.append(item)
    return result

###################################


###################################
# REST API
###################################

# Get todo list
@app.route("/todolist", methods=["POST"])
def get_todos():
    try:
        req = request.json
        userID = req["userID"]

        where = {'userID': userID}
        result = todos.find(where)
        result = [r for r in result]

        data = dumpObjectIDs(result)
        status = 200
        response = {"Status": status, "Message": "The todo list was retrieved!", "length": len(data), "data": data}
    except Exception as error:
        status = 401
        response = {"Status": status, "Error": f"{error}"}

    return jsonify(response), status


# Get a specific todo
@app.route("/todolist/<string:id>", methods=["GET"])
def get_todo(id):
    try:
        where = {'_id': ObjectId(id)}
        data = todos.find_one(where)
        data = dumpObjectID(data) if data else None
        status = 200
        response = {"Status": status, "Message": "The data was retrieved!", "data": data}

    except Exception as error:
        status = 401
        response = {"Status": status, "Error": f"{error}"}

    return jsonify(response), status


# Add a specific todo
@app.route("/todolist/add", methods=["POST"])
def add_todo():
    try:
        req = request.json
        userID = req["userID"]

        data = {
            "userID": userID,
            "title": req["title"],
            "completed": False,
            "tags": req["tags"],
            "date": str(datetime.utcnow())
        }
        result = todos.insert_one(data)

        status = 200
        response = {"Status": status, "Message": f"The todo was successfully added!", "data": dumpObjectID(data)}
    except Exception as error:
        status = 401
        response = {"Status": status, "Error": f"{error}"}

    return jsonify(response), status


# Update a specific todo
@app.route("/todolist/update/<string:id>", methods=["PUT"])
def update_todo(id):
    try:
        req = request.json

        where = {'_id': ObjectId(id)}
        set = {"$set": {'completed': req["completed"], 'title': req["title"], 'tags': req["tags"]}}
        result = todos.update_one(where, set)

        where = {'_id': ObjectId(id)}
        data = todos.find_one(where)

        status = 200
        response = {"Status": status, "Message": "The todo was updated!", "data": dumpObjectID(data)}

    except Exception as error:
        status = 401
        response = {"Status": status, "Error": f"{error}"}

    return jsonify(response), status


# Delete a specific todo
@app.route("/todolist/remove/<string:id>", methods=["DELETE"])
def delete_todo(id):
    try:
        where = {'_id': ObjectId(id)}
        result = todos.delete_one(where)
        status = 200
        response = {"Status": status, "Message": f"The todo was deleted!"}
    except Exception as error:
        status = 401
        response = {"Status": status, "Error": f"{error}"}

    return jsonify(response), status

###################################


###################################
# Run Flask
###################################
if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5000
    app.run(host=host, port=port, debug=True)

###################################

