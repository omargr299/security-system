
import json
import flask
from connections import DatabaseConn
import hashlib
from os import getenv
from dotenv import load_dotenv

load_dotenv()

app = flask.Flask(__name__)
db = DatabaseConn(getenv("ADMIN_NAME"), getenv("ADMIN_PASSWORD"))
hasher = hashlib.sha256()


@app.route('/users', methods=['GET', 'POST'])
def users():
    auth = flask.request.authorization
    if not auth:
        return flask.Response(status=401)
    if db.isAdminAuthorized(auth.get("username"), auth.get("password")) is False:
        return flask.Response(status=401)

    if flask.request.method == 'POST':
        request = flask.request.get_json()
        if not request:
            request = flask.request.form
        if not request:
            return flask.Response(status=400)
        try:
            res = db.createUser(
                **request)
        except Exception as e:
            return flask.Response(status=400)
        return flask.Response(status=200, response=json.dumps(res))
    elif flask.request.method == 'GET':
        res = db.getAllUsers()
        resp = flask.Response(status=200, response=json.dumps(res))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    return flask.Response(status=400)


@app.route('/user/<registerNumber>', methods=['GET', 'PUT', 'DELETE'])
def user(registerNumber):
    if type(registerNumber) is not str:
        return flask.Response(status=400)

    auth = flask.request.authorization
    if not auth:
        return flask.Response(status=401)
    if db.isAdminAuthorized(auth.get("username"), auth.get("password")) is False:
        return flask.Response(status=401)

    if flask.request.method == 'GET':
        res = db.getUser(registerNumber)
        if res is None:
            return flask.Response(status=404)
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp
    elif flask.request.method == 'PUT':
        try:
            res = db.updateUser(registerNumber, **flask.request.get_json())
        except Exception as e:
            return flask.Response(status=400)
        if res is None:
            return flask.Response(status=404)
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp
    elif flask.request.method == 'DELETE':
        try:
            res = db.deleteUser(registerNumber)
        except Exception as e:
            return flask.Response(status=400)
        if res is None:
            return flask.Response(status=404)
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp


@app.route('/vehicles', methods=['GET', 'POST'])
def vehicles():
    auth = flask.request.authorization
    if not auth:
        return flask.Response(status=401)
    if db.isAdminAuthorized(auth.get("username"), auth.get("password")) is False:
        return flask.Response(status=401)
    if flask.request.method == 'GET':
        res = db.getAllVehicles()
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp
    if flask.request.method == 'POST':
        try:
            res = db.createVehicle(**flask.request.get_json())
        except Exception as e:
            return flask.Response(status=400)
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp

    return flask.Response(status=400)


@app.route('/vehicle/<plate>', methods=['GET', 'PUT', 'DELETE'])
def vehicle(plate):
    if type(plate) is not str:
        return flask.Response(status=400)

    auth = flask.request.authorization
    if not auth:
        return flask.Response(status=401)
    if db.isAdminAuthorized(auth.get("username"), auth.get("password")) is False:
        return flask.Response(status=401)

    if flask.request.method == 'GET':
        res = db.getVehicle(plate)
        if res is None:
            return flask.Response(status=404)
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp
    elif flask.request.method == 'PUT':
        try:
            res = db.updateVehicle(plate, **flask.request.get_json())
        except Exception as e:
            return flask.Response(status=400)
        if res is None:
            return flask.Response(status=404)
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp
    elif flask.request.method == 'DELETE':
        try:
            res = db.deleteVehicle(plate)
        except Exception as e:
            return flask.Response(status=400)
        if res is None:
            return flask.Response(status=404)
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp

    return flask.Response(status=400)


@app.route('/employes', methods=['GET', 'POST'])
def employes():
    auth = flask.request.authorization
    if not auth:
        return flask.Response(status=401)
    if db.isAdminAuthorized(auth.get("username"), auth.get("password")) is False:
        return flask.Response(status=401)

    if flask.request.method == 'GET':
        res = db.getAllEmployes()
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp
    if flask.request.method == 'POST':
        try:
            res = db.createEmploye(**flask.request.get_json())
        except Exception as e:

            return flask.Response(status=400)
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp

    return flask.Response(status=400)


@app.route('/employe/<registerNumber>', methods=['GET', 'PUT', 'DELETE'])
def employe(registerNumber):
    if type(registerNumber) is not str:
        return flask.Response(status=400)

    auth = flask.request.authorization
    if not auth:
        return flask.Response(status=401)
    if db.isAdminAuthorized(auth.get("username"), auth.get("password")) is False:
        return flask.Response(status=401)

    if flask.request.method == 'GET':
        try:
            res = db.getEmploye(registerNumber, auth.get("username"))
        except PermissionError as e:

            return flask.Response(status=401)
        except Exception as e:

            return flask.Response(status=400)

        if res is None:
            return flask.Response(status=404)
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp
    elif flask.request.method == 'PUT':
        try:
            res = db.updateEmploye(registerNumber, auth.get(
                "username"), **flask.request.get_json())
        except Exception as e:

            return flask.Response(status=400)
        if not res:
            return flask.Response(status=404)
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp
    elif flask.request.method == 'DELETE':
        try:
            res = db.deleteEmploye(registerNumber, auth.get("username"))
        except PermissionError as e:

            return flask.Response(status=401)
        except Exception as e:

            return flask.Response(status=400)
        if res is None:
            return flask.Response(status=404)
        resp = flask.Response(status=200, response=json.dumps(res))
        return resp


@app.route('/admin/login', methods=['POST'])
def adminLogin():

    if flask.request.method == 'POST':
        auth = flask.request.authorization
        if not auth:
            return flask.Response(status=401)
        if db.isAdminAuthorized(auth.get("username"), auth.get("password")) is False:
            return flask.Response(status=401)

        return flask.Response(status=200)

    return flask.Response(status=400)


@app.route('/operator/login', methods=['POST'])
def operatorLogin():

    if flask.request.method == 'POST':
        auth = flask.request.authorization
        if not auth:
            return flask.Response(status=401)
        auth = db.isAuthorized(auth.get("username"), auth.get("password"))

        if auth is False:
            return flask.Response(status=401)
        return flask.Response(status=200)

    return flask.Response(status=400)


@app.route('/operator/qr/<hashCode>', methods=['GET'])
def existsQR(hashCode):
    if flask.request.method == 'GET':
        auth = flask.request.authorization
        if not auth:
            return flask.Response(status=401)
        auth = db.isAuthorized(auth.get("username"), auth.get("password"))

        if auth is False:
            return flask.Response(status=401)
        qr = db.getQR(hashCode)
        if qr is None:
            return flask.Response(status=404)
        return flask.Response(status=200)


@app.route('/operator/vehicle/<plate>', methods=['GET'])
def existVehicle(plate):
    if flask.request.method == 'GET':
        auth = flask.request.authorization
        if not auth:
            return flask.Response(status=401)
        auth = db.isAuthorized(auth.get("username"), auth.get("password"))

        if auth is False:
            return flask.Response(status=401)
        vehicle = db.getVehicle(plate)
        if vehicle is None:
            return flask.Response(status=404)
        if len(vehicle.users) == 0:
            return flask.Response(status=404)
        return flask.Response(status=200)


app.run(host=getenv("HOST_HTTP"), port=getenv(
    "PORT_HTTP"), debug=True, threaded=True)
