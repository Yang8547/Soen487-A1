from flask import jsonify, make_response, request
from main import app
from models import db, row2dict, User
import sqlalchemy


# get all users
@app.route("/user")
def get_all_user():
    user_list = User.query.all()
    return jsonify([row2dict(user) for user in user_list])


# find user by id
@app.route("/user/<user_id>")
def get_person(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return jsonify(row2dict(user))
    else:
        return make_response(jsonify({"code": 404, "msg": "Cannot find this person id."}), 404)


# insert new user
@app.route("/user", methods={"POST"})
def create_person():
    name = request.form.get("username")
    if not name:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot insert user. Missing username."}), 403)
    p = User(username=name)
    db.session.add(p)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot put user. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


# update username
@app.route("/user/<user_id>", methods={"PUT"})
def update_person(user_id):
    new_name = request.form.get("username")
    if not new_name:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot update user. Missing username."}), 403)
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return make_response(jsonify({"code": 403,
                                      "msg": "No such user."}), 403)
    if User.query.filter(User.id != user_id, User.username == new_name).count() > 0:
        return make_response(jsonify({"code": 403,
                                      "msg": "User name exists."}), 403)
    user.username = new_name
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot update user. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


# delete user
@app.route('/user/<user_id>', methods={'DELETE'})
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return make_response(jsonify({"code": 403,
                                     "msg": "User doesn't exist."}), 403)
    db.session.delete(user)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot delete user. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})
