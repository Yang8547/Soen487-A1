import unittest
import json
from main import app as tested_app
from config import TestConfig
from models import db as tested_db
from models import User

tested_app.config.from_object(TestConfig)


class TestUser(unittest.TestCase):
    def setUp(self):
        # set up the test DB
        self.db = tested_db
        self.db.create_all()
        self.db.session.add(User(id=1, username="Alice"))
        self.db.session.add(User(id=2, username="Bob"))
        self.db.session.commit()

        self.app = tested_app.test_client()

    def tearDown(self):
        # clean up the DB after the tests
        User.query.delete()
        self.db.session.commit()

    def test_get_all_user(self):
        # send the request and check the response status code
        response = self.app.get("/user")
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        person_list = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(person_list), list)
        self.assertDictEqual(person_list[0], {"id": "1", "username": "Alice"})
        self.assertDictEqual(person_list[1], {"id": "2", "username": "Bob"})

    def test_get_user_success(self):
        response = self.app.get("user/1")
        self.assertEqual(response.status_code, 200)
        person = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(person, {"id": "1", "username": "Alice"})

    def test_get_user_fail_invalid_id(self):
        # send the request and check the response status code
        response = self.app.get("/user/1000000")
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot find this person id."})

    def test_create_user_success(self):
        response = self.app.post("/user", data={"username": "Yang"})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 200, "msg": "success"})

        # check if the DB was updated correctly
        user = User.query.filter_by(id=3).first()
        self.assertEqual(user.username, "Yang")

    def test_create_user_fail_username_empty(self):
        response = self.app.post("/user", data={"username": ""})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot insert user. Missing username."})

    def test_create_user_fail_username_duplicate(self):
        response = self.app.post("/user", data={"username": "Bob"})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Username exits."})

    def test_update_user_success(self):
        response = self.app.put("/user/1", data={"username": "Yang"})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 200, "msg": "success"})

        # check if the DB was updated correctly
        user = User.query.filter_by(id=1).first()
        self.assertEqual(user.username, "Yang")

    def test_update_user_fail_invalid_userID(self):
        response = self.app.put("/user/1000", data={"username": "Yang"})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "No such user."})

    def test_update_user_fail_invalid_username_empty(self):
        response = self.app.put("/user/1", data={"username": ""})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot update user. Missing username."})

    def test_update_user_fail_username_duplicate(self):
        response = self.app.put("/user/1", data={"username": "Bob"})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "User name exists."})

    def test_delete_user_success(self):
        initial_count = User.query.count()
        response = self.app.delete("user/1")
        self.assertEqual(response.status_code, 200)
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 200, "msg": "success"})
        # check DB delete correct
        after_delete_count = User.query.count()
        self.assertEqual(after_delete_count, initial_count-1)

    def test_delete_user_fail_invalid_userID(self):
        response = self.app.delete("user/10000")
        self.assertEqual(response.status_code, 403)
        body = json.loads(str(response.data, "utf8"))
        self.assertEqual(body, {"code": 403, "msg": "User doesn't exist."})

    # def test_put_person_without_id(self):
    #     # do we really need to check counts?
    #     initial_count = Person.query.filter_by(name="Amy").count()
    #
    #     # send the request and check the response status code
    #     response = self.app.put("/person", data={"name": "Amy"})
    #     self.assertEqual(response.status_code, 200)
    #
    #     # convert the response data from json and call the asserts
    #     body = json.loads(str(response.data, "utf8"))
    #     self.assertDictEqual(body, {"code": 200, "msg": "success"})
    #
    #     # check if the DB was updated correctly
    #     updated_count = Person.query.filter_by(name="Amy").count()
    #     self.assertEqual(updated_count, initial_count+1)
    #
    # def test_put_person_with_new_id(self):
    #     # send the request and check the response status code
    #     response = self.app.put("/person", data={"id": 3, "name": "Amy"})
    #     self.assertEqual(response.status_code, 200)
    #
    #     # convert the response data from json and call the asserts
    #     body = json.loads(str(response.data, "utf8"))
    #     self.assertDictEqual(body, {"code": 200, "msg": "success"})
    #
    #     # check if the DB was updated correctly
    #     person = Person.query.filter_by(id=3).first()
    #     self.assertEqual(person.name, "Amy")
