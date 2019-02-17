import unittest
import json
from main import app as tested_app
from config import TestConfig
from models import db as tested_db
from models import Question, User

tested_app.config.from_object(TestConfig)


class TestQuestion(unittest.TestCase):
    def setUp(self):
        # set up the test DB
        self.db = tested_db
        self.db.create_all()
        self.db.session.add(User(id=1, username="Alice"))
        self.db.session.add(Question(id=1, title="When is the A1 due?", content="It is due this Sunday?", user_id=1))
        self.db.session.add(Question(id=2, title="When is the A2 due?", content="It is due this Monday?", user_id=1))
        self.db.session.commit()

        self.app = tested_app.test_client()

    def tearDown(self):
        # clean up the DB after the tests
        User.query.delete()
        Question.query.delete()
        self.db.session.commit()

    def test_get_all_question(self):
        # send the request and check the response status code
        response = self.app.get("/question")
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        question_list = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(question_list), list)
        self.assertDictEqual(question_list[0], {"id": "1", "title": "When is the A1 due?",
                                                "content": "It is due this Sunday?", "user_id": "1"})
        self.assertDictEqual(question_list[1], {"id": "2", "title": "When is the A2 due?",
                                                "content": "It is due this Monday?", "user_id": "1"})

    def test_get_question_success(self):
        response = self.app.get("question/1")
        self.assertEqual(response.status_code, 200)
        question = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(question, {"id": "1", "title": "When is the A1 due?",
                                        "content": "It is due this Sunday?", "user_id": "1"})

    def test_get_question_fail_invalid_id(self):
        # send the request and check the response status code
        response = self.app.get("/question/1000000")
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot find this question id."})

    def test_get_question_by_user_success(self):
        response = self.app.get("question-by-user/1")
        self.assertEqual(response.status_code, 200)
        question_list = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(question_list), list)
        self.assertDictEqual(question_list[0], {"id": "1", "title": "When is the A1 due?",
                                                "content": "It is due this Sunday?", "user_id": "1"})
        self.assertDictEqual(question_list[1], {"id": "2", "title": "When is the A2 due?",
                                                "content": "It is due this Monday?", "user_id": "1"})

    def test_get_question_by_user_fail_invalid_userID(self):
        response = self.app.get("question-by-user/22")
        self.assertEqual(response.status_code, 404)
        body = json.loads(str(response.data, "utf8"))
        self.assertEqual(body, {"code": 404, "msg": "Cannot find questions by this user id."})

    def test_create_question_success(self):
        response = self.app.post("/question", data={"title": "Test", "content": "test content",
                                                    "userID": 1})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 200, "msg": "success"})

        # check if the DB was insert correctly
        question = Question.query.filter_by(id=3).first()
        self.assertEqual(question.title, "Test")
        self.assertEqual(question.query.count(), 3)

    def test_create_question_fail_title_empty(self):
        response = self.app.post("/question", data={"title": "", "content": "test content",
                                                "userID": 1})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot insert question. Missing title."})

    def test_create_question_fail_invalid_userID(self):
        response = self.app.post("/question", data={"title": "test", "content": "test content",
                                                "userID":"20"})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403,
                                    "msg": "Cannot insert question. No such user, please register first."})

    def test_edit_question_success(self):
        response = self.app.put("/question/1", data={"title": "edit test", "content": "test test"})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 200, "msg": "success"})

        # check if the DB was updated correctly
        question = Question.query.filter_by(id=1).first()
        self.assertEqual(question.title, "edit test")
        self.assertEqual(question.content, "test test")

    def test_edit_question_fail_title_empty(self):
        response = self.app.put("/question/1", data={"title": "", "content": "test content"})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot update question. Missing question title."})

    def test_edit_question_fail_invalid_questionID(self):
        response = self.app.put("/question/1000", data={"title": "test", "content": "test content"})
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "No such question."})

    def test_delete_question_success(self):
        initial_count = Question.query.count()
        response = self.app.delete("question/1")
        self.assertEqual(response.status_code, 200)
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 200, "msg": "success"})
        # check DB delete correct
        after_delete_count = Question.query.count()
        self.assertEqual(after_delete_count, initial_count-1)

    def test_delete_question_fail_invalid_userID(self):
        response = self.app.delete("question/10000")
        self.assertEqual(response.status_code, 404)
        body = json.loads(str(response.data, "utf8"))
        self.assertEqual(body, {"code": 404, "msg": "Question doesn't exist."})


