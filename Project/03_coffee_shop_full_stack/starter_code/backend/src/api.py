import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_drinks():

    try:
        all_drinks = Drink.query.all()

        drinks = [drink.short() for drink in all_drinks]

        return jsonify({
            "success": True, 
            "drinks": drinks
        })

    except:
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    try:
        all_drinks = Drink.query.all()

        drinks = [drink.long() for drink in all_drinks]

        return jsonify({

            "success": True, 
            "drinks": drinks
        })
    except:
        abort(404)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''



@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drinks(payload):

    drink_data = request.get_json()

    try:
        title = drink_data.get('title', None)
        recipe = json.dumps(drink_data.get('recipe', None))

        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()

        formatted_drink = new_drink.long()

        return jsonify({
            "success": True, 
            "drinks": [formatted_drink]
        })

    except:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, id):

    try:
        drink_data = request.get_json()

        if ('title' in drink_data and 'recipe' in drink_data):

            edited_title = drink_data.get('title', None)
            edited_recipes = json.dumps(drink_data.get('recipe', None))

            drink_to_edit = Drink.query.filter(Drink.id == id)

            drink_to_edit.title = edited_title
            drink_to_edit.recipe = edited_recipes
            drink_to_edit.update()

            drink_representation = drink_to_edit.long()

            return jsonify({
                "success": True, 
                "drinks": [drink_representation]
            })
        else:
            abort(404)
    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            "success": True, 
            "delete": id
        })
    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(400)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Invalid Header"
    }), 400

@app.errorhandler(401)
def unauthorised(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden access"
    }), 403


@app.errorhandler(404)
def unauthorised(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(405)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500



'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def handle_auth_error(error):
    """
    Receive the raised authorization error and propagates it as response
    """
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response





