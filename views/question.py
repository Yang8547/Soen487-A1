from flask import jsonify, make_response, request
from main import app
from models import db, row2dict, User, Question
import sqlalchemy


# get all questions
@app.route("/question")
def get_all_question():
    question_list = Question.query.all()
    return jsonify([row2dict(question) for question in question_list])


# get question by id
@app.route("/question/<question_id>")
def get_question(question_id):
    question = Question.query.filter_by(id=question_id).first()
    if question:
        return jsonify(row2dict(question))
    else:
        return make_response(jsonify({"code": 404, "msg": "Cannot find this question id."}), 404)


# get questions by user id
@app.route("/question-by-user/<user_id>")
def get_question_by_user(user_id):
    question_list = Question.query.filter_by(user_id=user_id).all()
    if len(question_list) == 0:
        return make_response(jsonify({"code": 404, "msg": "Cannot find questions by this user id."}), 404)
    else:
        return jsonify([row2dict(question) for question in question_list])


# insert new question
@app.route("/question", methods={"POST"})
def create_question():
    title = request.form.get("title")
    content = request.form.get("content")
    user_id = request.form.get("userID")
    if not title:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot insert question. Missing title."}), 403)
    if User.query.filter_by(id=user_id).count() == 0:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot insert question. No such user, please register first."}), 403)
    question = Question(title=title, content=content, user_id=user_id)
    db.session.add(question)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot insert question. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


# update question
@app.route("/question/<question_id>", methods={"PUT"})
def edit_question(question_id):
    title = request.form.get("title")
    content = request.form.get("content")
    if not title:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot update question. Missing question title."}), 403)
    question = Question.query.filter_by(id=question_id).first()
    if not question:
        return make_response(jsonify({"code": 404,
                                      "msg": "No such question."}), 404)
    question.title = title
    question.content = content
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot update question. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


# delete question
@app.route('/question/<question_id>', methods={'DELETE'})
def delete_question(question_id):
    question = Question.query.filter_by(id=question_id).first()
    if not question:
        return make_response(jsonify({"code": 404,
                                     "msg": "Question doesn't exist."}), 404)
    db.session.delete(question)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot delete question. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})
