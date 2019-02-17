from flask import jsonify, make_response, request, Blueprint
from models import db, row2dict, User, Question
import sqlalchemy

question_view = Blueprint("question_view", __name__)


# get all questions
@question_view.route("/question")
def get_all_question():
    question_list = Question.query.all()
    return jsonify([row2dict(question) for question in question_list])


# get question by id
@question_view.route("/question/<question_id>")
def get_question(question_id):
    question = Question.query.filter_by(id=question_id).first()
    # success
    if question:
        return jsonify(row2dict(question))
    # invalid id
    else:
        return make_response(jsonify({"code": 404, "msg": "Cannot find this question id."}), 404)


# get questions by user id
@question_view.route("/question-by-user/<user_id>")
def get_question_by_user(user_id):
    question_list = Question.query.filter_by(user_id=user_id).all()
    # no question under this user id
    if len(question_list) == 0:
        return make_response(jsonify({"code": 404, "msg": "Cannot find questions by this user id."}), 404)
    # success
    else:
        return jsonify([row2dict(question) for question in question_list])


# insert new question
@question_view.route("/question", methods={"POST"})
def create_question():
    title = request.form.get("title")
    content = request.form.get("content")
    user_id = request.form.get("userID")
    # title empty
    if not title:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot insert question. Missing title."}), 403)
    # invalid user ID or not login
    if User.query.filter_by(id=user_id).count() == 0:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot insert question. No such user, please register first."}), 403)
    # success
    question = Question(title=title, content=content, user_id=user_id)
    db.session.add(question)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot insert question. "
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


# update question
@question_view.route("/question/<question_id>", methods={"PUT"})
def edit_question(question_id):
    title = request.form.get("title")
    content = request.form.get("content")
    # title empty
    if not title:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot update question. Missing question title."}), 403)
    question = Question.query.filter_by(id=question_id).first()
    # invalid question id
    if not question:
        return make_response(jsonify({"code": 404,
                                      "msg": "No such question."}), 404)
    # success
    question.title = title
    question.content = content
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot update question. "
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


# delete question
@question_view.route('/question/<question_id>', methods={'DELETE'})
def delete_question(question_id):
    question = Question.query.filter_by(id=question_id).first()
    # invalid question id
    if not question:
        return make_response(jsonify({"code": 404,
                                     "msg": "Question doesn't exist."}), 404)
    # success
    db.session.delete(question)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot delete question. "
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})
