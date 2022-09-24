from flask import Flask, jsonify, request, redirect
import sys
import os 
app = Flask(__name__)


@app.route("/")
def root():
    return redirect("/hello")

@app.route("/hello")
def hello():
    return "<!doctype html><h1>Welcome to the cloud platform team!<h1><h3>Container hostname -> " + os.uname()[1] +"</h3></h1>", 200

@app.route("/healthz")
def healthy():
    return "ok\n", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)