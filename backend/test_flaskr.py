from http.client import responses
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category



class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://postgres:Jesus@localhost/trivia_test'
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        # create new question
        self.new_question = {
            'question': 'What do you want to do',
            'answer': 'code',
            'difficulty': 4,
            'category': 3,
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # test for successful operation and expected errors: for categories endpoint

    def test_retrieve_categories(self):

        res = self.client().get('/categories') 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])

    # # test for successful operation and expected errors: for questions endpoint
    def test_get_questions(self):

        res = self.client().get('/questions') 
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['totalQuestions'])

    def test_404_sent_requesting_beyond_valid_page(self):

        res = self.client().get("/questions?page=100")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    #delete a different question in each attempt
    def test_delete_question(self):

        res = self.client().delete("/questions/16")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 16)

    def test_422_if_question_does_not_exist(self):

        res = self.client().delete("/questions/100")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    
    # add new question
    def test_add_question(self):

        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(data["totalQuestions"])

    def test_405_if_question_addition_not_allowed(self):

        res = self.client().post("/questions/68", json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    # #test search endpoints
    def test_get_questions_based_on_search_term(self):

        res = self.client().post("/questions/appendages")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertEqual(data["currentCategory"], None)
        self.assertTrue(data["totalQuestions"])

    def test_get_questions_based_on_search_term_not_found(self):

        res = self.client().post("/questions/111")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"],[])
        self.assertEqual(data["currentCategory"], None)
        self.assertEqual(data["totalQuestions"],0)

    #test questions by category
    def test_get_questions_by_category(self):

        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
        self.assertEqual(data["currentCategory"],"Art")

    # test questions by category
    def test_404_get_questions_by_category_not_found(self):

        res = self.client().get('/categories/23/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["questions"],[])
        self.assertTrue(data["totalQuestions"],0)
        self.assertEqual(data["currentCategory"],'')
        


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()