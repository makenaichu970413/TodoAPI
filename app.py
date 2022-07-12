
###################################
# Module
###################################
import os
import json
from flask import Flask, jsonify, request, session, make_response
from flask_swagger_ui import get_swaggerui_blueprint
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import bson.json_util as json_util
from functools import wraps
from bson.objectid import ObjectId
from db import DB
import jwt
import re
import bcrypt
from decouple import config
from dotenv import load_dotenv
###################################


###################################
# Flask Setup
###################################
app = Flask(__name__)
try:
    load_dotenv()
except Exception as error:
    print(f"Production: {True}; WARNING: {error}")

# Send Mail
mail_domain = os.environ.get('MAIL_USERNAME').split('@')[-1].strip()
app.config["MAIL_SERVER"] = f'smtp.{mail_domain}'
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT")) # 405
app.config["MAIL_USERNAME"] = os.environ.get('MAIL_USERNAME')
app.config["MAIL_PASSWORD"] = os.environ.get('MAIL_PASSWORD')
app.config["MAIL_USE_TLS"] = True
# app.config["MAIL_USE_SSL"] = False
mail = Mail(app)

# Token Secret
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')

domain = os.environ.get('DOMAIN')
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

# API Documentation URL
# https://cognixus-todo-api.herokuapp.com/swagger/

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
    result = None
    if data:
        data["_id"] = str(ObjectId(data["_id"]))
        result = data
    return result


def dumpObjectIDs(list):
    result = []
    for item in list:
        item["_id"] = str(ObjectId(item["_id"]))
        result.append(item)
    return result


def checkEmail(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    valid = re.fullmatch(regex, email)
    return valid


def hashPassword(password):
    bPassword =password.encode('utf-8')
    hashed = bcrypt.hashpw(bPassword, bcrypt.gensalt())
    hashed = hashed.decode("utf-8")
    # print(f"hashed: {hashed}")
    return hashed


def verifyPassword(password, hashed):
    bPassword = password.encode('utf-8')
    bHashed = hashed.encode('utf-8')
    match = bcrypt.checkpw(bPassword, bHashed)
    # print(f"match: {match}")
    return match


def date_conversion(str):
    # str = "2022-07-02 05:31:52.603664"
    date = datetime.strptime(str, '%Y-%m-%d %H:%M:%S.%f')
    return date


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            response = {"Status": 200, "Message": "Token is missing!"}
            return jsonify(response), 200

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=['HS256'])
            # print(f"payload: {payload}")
            expiration = date_conversion(payload["expiration"])
            if expiration > datetime.utcnow():
                return func(payload, *args, **kwargs)
            else:
                response = {"Status": 200, "Message": f"Your token have expired!"}
                return jsonify(response), 200

        except Exception as error:
            response = {"Status": 200, "Message": f"Invalid token! Error:{error}."}
            return jsonify(response), 401

    return decorated


def JWT(userID, expired):
    token = jwt.encode({
        "userID": userID,
        "expiration": str(datetime.utcnow() + timedelta(seconds=expired))
    }, app.config["SECRET_KEY"])
    # token = token.decode("utf-8")
    data = {"token": token}
    return data


def authenticated(userID):
    hour = 12
    expired_period = hour * 60 * 60
    # expired_period = 30
    session["logged_in"] = True
    data = JWT(userID, expired_period)
    return data


def send_mail(email, title, content):
    sender = "noreply@demo.com"
    msg = Message(title, sender=sender, recipients=[email])
    msg.body = content
    mail.send(msg)

###################################


###################################
# REST API
###################################

@app.route('/')
def home():
    if not session.get("logged_in"):
        status = 401
        response = {"Status": 200, "Message": "Please login your account"}
    else:
        token = ""
        status = 200
        response = {"Status": 200, "Message": "You have logged in!", "Token": token}

    return jsonify(response), status

# User Authentication
@app.route('/signup', methods=["POST"])
def signup():
    try:
        req = request.json

        if not req["email"] or not req["password"] or not req["confirm_password"]:
            response = {"Status": 200, "Message": "Please filled in all required value."}
            return jsonify(response), 200

        email = req["email"].strip()
        valid = checkEmail(email)
        if not valid:
            response = {"Status": 200, "Message": "Your email was not valid."}
            return jsonify(response), 200

        password = req["password"].strip()
        repassword = req["confirm_password"].strip()
        if password != repassword:
            response = {"Status": 200, "Message": "Your password and confirm password are unmatched."}
            return jsonify(response), 200

        if len(password) < 7:
            response = {"Status": 200, "Message": "Your password should be at least 7 characters long."}
            return jsonify(response), 200

        where = {"email": email}
        existingUser = users.find_one(where)
        if existingUser:
            response = {"Status": 200, "Message": "The email has been signed up, please change to another email."}
            return jsonify(response), 200

        hashed = hashPassword(password)
        data = {"email": email, "password": hashed, "verified": False}
        result = users.insert_one(data)
        userID = str(ObjectId(result.inserted_id))
        auth = authenticated(userID)
        response = {"Status": 200, "Message": "You have signed up an new account!", "Auth": auth}
        return jsonify(response), 200

    except Exception as error:
        response = {"Status": 401, "Error": f"{error}"}
        return jsonify(response), 401


@app.route('/login', methods=["POST"])
def login():

    try:
        req = request.json

        if not req["email"] or not req["password"]:
            response = {"Status": 200, "Message": "Please filled in all required value."}
            return jsonify(response), 200

        email = req["email"].strip()
        valid = checkEmail(email)
        if not valid:
            response = {"Status": 200, "Message": "Your email was not valid."}
            return jsonify(response), 200

        where = {"email": email}
        result = users.find_one(where)
        data = dumpObjectID(result)
        if not data:
            response = {"Status": 200, "Message": "User does not exists!"}
            return jsonify(response), 200

        password = req["password"].strip()
        hashed = data["password"]
        match = verifyPassword(password, hashed)
        if match:
            auth = authenticated(data["_id"])
            response = {"Status": 200, "Message": "Your have logged in.", "Auth": auth}
            return jsonify(response), 200
        else:
            response = {"Status": 200, "Message": "Authentication failed!"}
            return jsonify(response), 200

    except Exception as error:
        status = 401
        response = {"Status": status, "Error": f"{error}"}
        return jsonify(response), status


@app.route('/verify_email', methods=["GET"])
@token_required
def verify_email(payload):
    try:
        userID = payload["userID"]
        where = {'_id': ObjectId(userID)}
        user = users.find_one(where)
        data = dumpObjectID(user)

        if data["verified"]:
            response = {"Status": 200, "Message": f"The email has '{data['email']}' has verified."}
            return jsonify(response), 200

        hour = 12
        expired_period = hour * 60 * 60
        # expired_period = 30
        jwt = JWT(userID, expired_period)
        link = f"http://{domain}/verified_email?token={jwt['token']}"

        email = data['email']
        title = "TodoAPI Email Verification"
        content = f'Hi please verified your email by clicking on the below link and thanks. \n\n Link: {link}'
        send_mail(email, title, content)

        response = {"Status": 200, "Message": f"The mail has sent to '{data['email']}'. Please check your mail."}
        return jsonify(response), 200

    except Exception as error:
        status = 401
        response = {"Status": status, "Error": f"{error}"}
        return jsonify(response), status


@app.route('/verified_email', methods=["GET"])
@token_required
def verified_email(payload):
    try:
        userID = payload["userID"]
        where = {'_id': ObjectId(userID)}
        set = {"$set": {'verified': True}}
        result = users.update_one(where, set)
        status = 200
        response = {"Status": status, "Message": "The user email was verified!"}

    except Exception as error:
        status = 401
        response = {"Status": status, "Error": f"{error}"}

    return jsonify(response), status


@app.route('/forget_password', methods=["POST"])
def forget_password():
    try:
        req = request.json
        email = req["email"].strip()

        if not email:
            response = {"Status": 200, "Message": "Please filled in the required value."}
            return jsonify(response), 200

        valid = checkEmail(email)
        if not valid:
            response = {"Status": 200, "Message": "Your email format was invalid."}
            return jsonify(response), 200

        where = {"email": email}
        existingUser = users.find_one(where)
        data = dumpObjectID(existingUser)
        if not data:
            response = {"Status": 200, "Message": "The email was not sign-up yet."}
            return jsonify(response), 200

        userID = data["_id"]
        hour = 12
        expired_period = hour * 60 * 60
        # expired_period = 30
        jwt = JWT(userID, expired_period)
        link = f"http://{domain}/reset_password?token={jwt['token']}"

        email = data['email']
        title = "TodoAPI Reset Password"
        content = f'Hi please reset your password by clicking on the below link and thanks. \n\n Link: {link}'
        send_mail(email, title, content)

        response = {"Status": 200, "Message": f"The mail has sent to '{data['email']}'. Please check your mail."}
        return jsonify(response), 200

    except Exception as error:
        status = 401
        response = {"Status": status, "Error": f"{error}"}
        return jsonify(response), status


@app.route('/reset_password', methods=["POST"])
@token_required
def reset_password(payload):

    try:
        req = request.json
        password = req["password"].strip()
        repassword = req["confirm_password"].strip()

        if not password or not repassword:
            response = {"Status": 200, "Message": "Please filled in all required value."}
            return jsonify(response), 200

        if password != repassword:
            response = {"Status": 200, "Message": "Your password and confirm password are unmatched."}
            return jsonify(response), 200

        if len(password) < 7:
            response = {"Status": 200, "Message": "Your password should be at least 7 characters long."}
            return jsonify(response), 200

        userID = payload["userID"]
        where = {'_id': ObjectId(userID)}
        hashed = hashPassword(password)
        set = {"$set": {'password': hashed}}
        result = users.update_one(where, set)
        response = {"Status": 200, "Message": "The new password has been updated."}
        return jsonify(response), 200

    except Exception as error:
        response = {"Status": 401, "Error": f"{error}"}
        return jsonify(response), 401


# Get todo list
@app.route("/todolist", methods=["GET"])
@token_required
def get_todos(payload):
    try:
        userID = payload["userID"]
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
@token_required
def get_todo(payload, id):
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
@token_required
def add_todo(payload):
    try:
        req = request.json
        userID = payload["userID"]

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
@token_required
def update_todo(payload, id):
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
@token_required
def delete_todo(payload, id):
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
    # print(f"SECRET: {os.environ.get('SECRET_KEY')}")
    app.run(host=host, port=port, debug=True)

###################################

# https://jwt.io/
# https://cognixus-todo-api.herokuapp.com
# docker build -t 970413/cognixus_todo_api .
