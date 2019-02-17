import unittest
import json
from main import app as tested_app
from config import TestConfig
from models import db as tested_db
from models import Answer, User, Question

tested_app.config.from_object(TestConfig)


class TestAnswer(unittest.TestCase):
    def setUp(self):
        # set up the test DB
        self.db = tested_db
        self.db.create_all()
        self.db.session.add(User(id=1, username="Alice"))
        self.db.session.add(Question(id=1, title="When is the A1 due?", content="Is it due this Sunday?", user_id=1))
        self.db.session.add(Question(id=2, title="When is the A2 due?", content="Is it due this Monday?", user_id=1))
        self.db.session.add(Answer(id=1, content="Yes, It is.", user_id=1, question_id=1))
        self.db.session.commit()

        self.app = tested_app.test_client()

    def tearDown(self):
        # clean up the DB after the tests
        User.query.delete()
        Question.query.delete()
        Answer.query.delete()
        self.db.session.commit()

    def test_get_answer_success(self):
        response = self.app.get("answer/1")
        self.assertEqual(response.status_code, 200)
        answer = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(answer, {"id": "1", "content": "Yes, It is.",
                                      "user_id": "1", "question_id": "1"})

    def test_get_answer_fail_invalid_id(self):
        response = self.app.get("/answer/1000000")
        self.assertEqual(response.status_code, 404)
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot find this answer id."})

    def test_get_answer_by_question_success(self):
        response = self.app.get("answer-by-question/1")
        self.assertEqual(response.status_code, 200)
        answer_list = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(answer_list), list)
        self.assertDictEqual(answer_list[0], {"id": "1", "content": "Yes, It is.",
                                              "user_id": "1", "question_id": "1"})

    def test_get_answer_by_question_success_no_answer(self):
        response = self.app.get("answer-by-question/2")
        self.assertEqual(response.status_code, 200)
        body = json.loads(str(response.data, "utf8"))
        self.assertEqual(body, {"code": 200, "msg": "No answer for this question yet."})

    def test_get_answer_by_question_fail_invalid_questionID(self):
        response = self.app.get("answer-by-question/100")
        self.assertEqual(response.status_code, 404)
        body = json.loads(str(response.data, "utf8"))
        self.assertEqual(body, {"code": 404, "msg": "Cannot find this question id."})

    def test_create_answer_success(self):
        response = self.app.post("/answer", data={"content": "test content",
                                                  "userID": 1, "questionID": 1})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 200, "msg": "success"})

        # check if the DB was insert correctly
        answer = Answer.query.filter_by(id=2).first()
        self.assertEqual(answer.content, "test content")
        self.assertEqual(answer.query.count(), 2)

    def test_create_answer_fail_content_empty(self):
        response = self.app.post("/answer", data={"content": "",
                                                  "userID": 1, "questionID": 1})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot insert answer. Missing content."})

    def test_create_answer_fail_invalid_userID(self):
        response = self.app.post("/answer", data={"content": "test content",
                                                  "userID": "20", "questionID": 1})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403,
                                    "msg": "Cannot insert answer. No such user, please register first."})

    def test_create_answer_fail_invalid_questionID(self):
        response = self.app.post("/answer", data={"content": "test content",
                                                  "userID": "1", "questionID": 100})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403,
                                    "msg": "Cannot insert answer. No such Question."})

    def test_edit_answer_success(self):
        response = self.app.put("/answer/1", data={"content": "edit test", "userID": 1})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 200, "msg": "success"})

        # check if the DB was updated correctly
        answer = Answer.query.filter_by(id=1).first()
        self.assertEqual(answer.content, "edit test")

    def test_edit_answer_fail_content_empty(self):
        response = self.app.put("/answer/1", data={"content": "", "userID": 1})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot update answer. Missing answer content."})

    def test_edit_answer_fail_invalid_answerID(self):
        response = self.app.put("/answer/1000", data={"content": "test content", "userID": 1})
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "No such answer."})

    def test_edit_answer_fail_change_other_one_answer(self):
        response = self.app.put("/answer/1", data={"content": "test content", "userID": 2})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Can't edit other user's answer."})

    def test_delete_answer_success(self):
        initial_count = Answer.query.count()
        response = self.app.delete("answer/1")
        self.assertEqual(response.status_code, 200)
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 200, "msg": "success"})
        # check DB delete correct
        after_delete_count = Answer.query.count()
        self.assertEqual(after_delete_count, initial_count-1)

    def test_delete_answer_fail_invalid_answerID(self):
        response = self.app.delete("answer/10000")
        self.assertEqual(response.status_code, 404)
        body = json.loads(str(response.data, "utf8"))
        self.assertEqual(body, {"code": 404, "msg": "answer doesn't exist."})


