from ast import Str
from multiprocessing import current_process
import os
from unicodedata import category
from unittest import result

from sqlalchemy import true
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request

    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])

    def retrieve_categories():
        
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = { category.id: category.type for category in categories}

        return jsonify({
            'success': True,
            'categories': formatted_categories,
            "total_categories": len(Category.query.all()),

        })

        
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions" , methods=["GET"])

    def get_questions():

        selections = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selections)

        categories = Category.query.order_by(Category.id).all()
        formatted_categories = { category.id: category.type for category in categories}

        if len(current_questions) == 0:
            abort(404)
            

        return jsonify({
            'success': True,
            'questions': current_questions,
            'categories': formatted_categories,
            'totalQuestions': len(Question.query.all()),
            'currentCategory': None,
        })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:q_id>" , methods=["DELETE"])
    def delete_question_by_id(q_id):

        try:
            question = Question.query.filter(Question.id == q_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                "success": True,
                "deleted": q_id,
            })

        except:
            abort(422)



    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def add_question():
        body = request.get_json()
        question = body.get("question", None)
        answer = body.get("answer", None)
        difficulty = body.get("difficulty", None)
        category = body.get("category", None)

        if not question:
            abort(422)

        if not answer:
            abort(422)

        if not difficulty:
            abort(422)

        if not category:
            abort(422)        

        try:

            question = Question(question=question, answer=answer, difficulty=difficulty, category=category)

            question.insert()

            return jsonify(
                {
                    'success': True ,
                    'created': question.id,
                    'totalQuestions': len(Question.query.all())
                }
            )

        except:
            abort(422)
    """     
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/<string:searchTerm>", methods=["POST"])

    def get_questions_based_on_search_term(searchTerm):
        

        if searchTerm is None:
            abort(404)

        try:
                search_results = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(searchTerm))).all()

                if search_results is not None:

                    show_questions = paginate_questions(request, search_results)

                    return jsonify({
                        "success": True,
                        "questions": show_questions,
                        "currentCategory": None,
                        "totalQuestions": len(show_questions)
                    })

        except:
            abort(422)
        





    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:question_category>/questions", methods=["GET"])

    def get_questions_by_category(question_category):

        categories = Category.query.filter(Category.id == question_category).one_or_none()

        if categories is None:
            abort(404)

        try:
            questions = Question.query.filter(Question.category == question_category).all()

            formatted_questions = [question.format() for question in questions]    

            return jsonify({
                "success": True,
                "questions": formatted_questions,
                "totalQuestions": len(questions),
                "current_category": categories.type

            })

        except:
          abort(422)    

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])

    def get_question_to_play():

        body = request.get_json()
        quiz_category = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions', None)
        
        if quiz_category['id'] == 0:
            questions = Question.query.order_by(Question.id).all()
        
        elif (int(quiz_category['id']) in range(7)) and (int(quiz_category['id']) != 0):
            questions = Question.query.order_by(Question.id).filter(Question.id.in_(previous_questions)).all()
            

        questions_to_play = [question.format() for question in questions]
        
        if len(questions_to_play) == 0: 
            
            return jsonify({
                'success': False,
                'question': False
                })
        
        return jsonify({
                'success':True,
                'question': random.choice(questions_to_play)
            })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    return app
