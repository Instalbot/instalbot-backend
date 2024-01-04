from flask import Flask, jsonify

app = Flask(__name__)


@app.errorhandler(404)
def not_found(_):
    return jsonify({
        "message": "Requested resource was not found",
        "status": 404
    })


@app.route("/")
def index():
    return jsonify({
        "message": "Hello, backend is working",
        "status": 200
    })
