from flask import Flask, jsonify, make_response, request

# need an app before we import models because models need it
app = Flask(__name__)

from models import db
db.create_all()

import views.user
import views.question
import views.answer


@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({"code": 404, "msg": "404: Not Found"}), 404)

@app.route('/')
def soen487_a1():
    return "index page"

if __name__ == '__main__':
    app.run()
