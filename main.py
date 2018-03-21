import db
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/user/<username>', methods=['GET', 'POST', 'DELETE'])
def user(username):
    if request.method == 'POST':
        resp_body, status_code = db.user.create(username)
    elif request.method == 'GET':
        resp_body, status_code = db.user.get(username)
    elif request.method == 'DELETE':
        resp_body, status_code = db.user.delete(username)
    return jsonify(resp_body), status_code


@app.route("/user/<username>/bitbucket/<profile>", methods=['POST', 'DELETE'])
def bitbucket_profile(username, profile):
    if request.method == 'POST':
        response, status_code = db.bitbucket.add(username, profile)
    elif request.method == 'DELETE':
        response, status_code = db.bitbucket.delete(username, profile)
    return jsonify(response), status_code


@app.route("/user/<username>/github/<profile>", methods=['POST', 'DELETE'])
def github_profile(username, profile):
    if request.method == 'POST':
        response, status_code = db.github.add(username, profile)
    elif request.method == 'DELETE':
        response, status_code = db.github.delete(username, profile)
    return jsonify(response), status_code


if __name__ == "__main__":
    app.run()
