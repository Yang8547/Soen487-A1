from flask import jsonify, make_response, request, Blueprint
from models import db, row2dict, User, Question, Answer
import sqlalchemy

answer_view = Blueprint("answer_view", __name__)


# get all answers DOES NOT MAKE SENSE HAVING THIS METHOD
# @answer_view.route("/answer")
# def get_all_answer():
#     answer_list = Answer.query.all()
#     return jsonify([row2dict(answer) for answer in answer_list])


# get answer by id
@answer_view.route("/answer/<answer_id>")
def get_answer(answer_id):
    answer = Answer.query.filter_by(id=answer_id).first()
    # success
    if answer:
        return jsonify(row2dict(answer))
    # invalid answer id
    else:
        return make_response(jsonify({"code": 404, "msg": "Cannot find this answer id."}), 404)


# get answers by question id
@answer_view.route("/answer-by-question/<question_id>")
def get_answer_by_question(question_id):
    question = Question.query.filter_by(id=question_id).first()
    # invalid question id
    if not question:
        return make_response(jsonify({"code": 404, "msg": "Cannot find this question id."}), 404)
    answer_list = question.answers
    # no answer yet
    if len(answer_list) == 0:
        return make_response(jsonify({"code": 200, "msg": "No answer for this question yet."}), 200)
    else:
        return jsonify([row2dict(answer) for answer in answer_list])


# insert new answer
@answer_view.route("/answer", methods={"POST"})
def create_answer():
    content = request.form.get("content")
    user_id = request.form.get("userID")
    question_id = request.form.get("questionID")
    # content empty
    if not content:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot insert answer. Missing content."}), 403)
    # no such user
    if User.query.filter_by(id=user_id).count() == 0:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot insert answer. No such user, please register first."}), 403)
    # invalid question id
    if Question.query.filter_by(id=question_id).count() == 0:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot insert answer. No such Question."}), 403)
    # success
    answer = Answer(content=content, user_id=user_id, question_id=question_id)
    db.session.add(answer)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot insert answer. "
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


# update answer
@answer_view.route("/answer/<answer_id>", methods={"PUT"})
def edit_answer(answer_id):
    content = request.form.get("content")
    user = request.form.get("userID")
    # content empty
    if not content:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot update answer. Missing answer content."}), 403)
    answer = Answer.query.filter_by(id=answer_id).first()
    # invalid answer id
    if not answer:
        return make_response(jsonify({"code": 404,
                                      "msg": "No such answer."}), 404)
    # change other one's answer
    current_user_id = int(user)
    if answer.user_id != current_user_id:
        return make_response(jsonify({"code": 403,
                                      "msg": "Can't edit other user's answer."}), 403)
    # success
    answer.content = content
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot update answer. "
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


# delete answer
@answer_view.route('/answer/<answer_id>', methods={'DELETE'})
def delete_answer(answer_id):
    answer = Answer.query.filter_by(id=answer_id).first()
    # invalid answer id
    if not answer:
        return make_response(jsonify({"code": 404,
                                     "msg": "answer doesn't exist."}), 404)
    # success
    db.session.delete(answer)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot delete answer. "
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})
