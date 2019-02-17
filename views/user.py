from flask import jsonify, make_response, request, Blueprint
from models import db, row2dict, User
import sqlalchemy

user_view = Blueprint("user_view", __name__)


# get all users
@user_view.route("/user")
def get_all_user():
    user_list = User.query.all()
    return jsonify([row2dict(user) for user in user_list])


# find user by id
@user_view.route("/user/<user_id>")
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return jsonify(row2dict(user))
    else:
        return make_response(jsonify({"code": 404, "msg": "Cannot find this person id."}), 404)


# insert new user
@user_view.route("/user", methods={"POST"})
def create_user():
    name = request.form.get("username")
    # username is empty
    if not name:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot insert user. Missing username."}), 403)
    # username duplicate
    if User.query.filter_by(username=name).count() > 0:
        return make_response(jsonify({"code": 403,
                                      "msg": "Username exits."}), 403)
    # success
    p = User(username=name)
    db.session.add(p)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot put user. "
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


# update username
@user_view.route("/user/<user_id>", methods={"PUT"})
def update_user(user_id):
    new_name = request.form.get("username")
    # username empty
    if not new_name:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot update user. Missing username."}), 403)
    # invalid user id
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return make_response(jsonify({"code": 403,
                                      "msg": "No such user."}), 403)
    # username exist
    if User.query.filter(User.id != user_id, User.username == new_name).count() > 0:
        return make_response(jsonify({"code": 403,
                                      "msg": "User name exists."}), 403)
    # success
    user.username = new_name
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot update user. "
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


# delete user
@user_view.route('/user/<user_id>', methods={'DELETE'})
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    # invalid user id
    if not user:
        return make_response(jsonify({"code": 403,
                                     "msg": "User doesn't exist."}), 403)
    # success
    db.session.delete(user)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot delete user. "
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})
