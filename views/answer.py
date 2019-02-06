from flask import jsonify, make_response, request
from main import app
from models import db, row2dict, User, Question, Answer
import sqlalchemy


# get all answers
@app.route("/answer")
def get_all_answer():
    answer_list = Answer.query.all()
    return jsonify([row2dict(answer) for answer in answer_list])


# get answer by id
@app.route("/answer/<answer_id>")
def get_answer(answer_id):
    answer = Answer.query.filter_by(id=answer_id).first()
    if answer:
        return jsonify(row2dict(answer))
    else:
        return make_response(jsonify({"code": 404, "msg": "Cannot find this answer id."}), 404)


# get answers by question id
@app.route("/answer-by-question/<question_id>")
def get_answer_by_question(question_id):
    question = Question.query.filter_by(id=question_id)
    if not question:
        return make_response(jsonify({"code": 404, "msg": "Cannot find this question id."}), 404)
    answer_list = question.answers
    if len(answer_list) == 0:
        return make_response(jsonify({"code": 404, "msg": "No answer for this question yet."}), 404)
    else:
        return jsonify([row2dict(answer) for answer in answer_list])


# insert new answer
@app.route("/answer", methods={"POST"})
def create_answer():
    content = request.form.get("content")
    user_id = request.form.get("userID")
    question_id = request.form.get("questionID")
    if not content:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot insert answer. Missing content."}), 403)
    if User.query.filter_by(id=user_id).count() == 0:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot insert answer. No such user, please register first."}), 403)
    if Question.query.filter_by(id=question_id).count() == 0:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot insert answer. No such Question."}), 403)
    answer = Answer(content=content, user_id=user_id, question_id=question_id)
    db.session.add(answer)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot insert answer. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


# update answer
@app.route("/answer/<answer_id>", methods={"PUT"})
def edit_answer(answer_id):
    content = request.form.get("content")
    if not content:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot update answer. Missing answer content."}), 403)
    answer = Answer.query.filter_by(id=answer_id).first()
    if not answer:
        return make_response(jsonify({"code": 404,
                                      "msg": "No such answer."}), 404)
    answer.content = content
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot update answer. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


# delete answer
@app.route('/answer/<answer_id>', methods={'DELETE'})
def delete_answer(answer_id):
    answer = Answer.query.filter_by(id=answer_id).first()
    if not answer:
        return make_response(jsonify({"code": 404,
                                     "msg": "answer doesn't exist."}), 404)
    db.session.delete(answer)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot delete answer. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})
