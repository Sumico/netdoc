#!/usr/bin/env python3
""" App init """
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20170430'

""" API
    Methods:
    - GET /api/objects - Retrieves a list of objects
    - GET /api/objects/1 - Retrieves a specific objects
    - POST /api/objects - Creates a new object
    - PUT /api/objects/1 - Edits a specific object
    - DELETE /api/objects/1 - Deletes a specific object
    Return codes:
    - 200 success - Request ok
    - 201 success - New objects has been created
    - 400 bad request - Input request not valid
    - 401 unauthorized - User not authenticated
    - 403 forbidden - User authenticated but not authorized
    - 404 fail - Url or object not found
    - 405 fail - Method not allowed
    - 406 fail - Not acceptable
    - 409 fail - Object already exists, cannot create another one
    - 500 error - Server error, maybe a bug/exception or a backend/database error
"""
#import hashlib, memcache, os, sh, shutil, socket, sys
import logging
from flask import Flask
#from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_script import Command, Manager, Server
import werkzeug.exceptions
from netdoc.config import *

# Creating the Flask app
app = Flask(__name__)
app_root = os.path.dirname(os.path.abspath(__file__))
config = loadConfig(app_root)
app.config.update(
    BUNDLE_ERRORS = True,
    SQLALCHEMY_DATABASE_URI = config['app']['database_uri'],
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    TRAP_HTTP_EXCEPTIONS = True
)
manager = Manager(app)
db = SQLAlchemy(app)
api = Api(app)

# Postpone to avoid circular import
from netdoc.catalog.resources import *
from netdoc.catalog.models import *

# Creating database structure
try:
    db.create_all()
except Exception as err:
    # Cannot add tables
    logging.error('cannot update database "{}"'.format(config['app']['database_uri']))
    logging.error(err)
    sys.exit(1)

# Managing HTTP errors (~/Library/Python/3.6//lib/python/site-packages/werkzeug/__pycache__/exceptions.cpython-36.pyc)
@app.errorhandler(werkzeug.exceptions.BadRequest)
def http_400(err):
    response = {
        'code': 400,
        'status': 'fail',
        'message': 'Bad Request',
        'description': 'The browser (or proxy) sent a request that this server could not understand.'
    }
    return json.dumps(response, indent = 4, sort_keys = True) + '\n', 400

@app.errorhandler(werkzeug.exceptions.Unauthorized)
def http_401(err):
    response = {
        'code': 401,
        'status': 'fail',
        'message': 'Unauthorized',
        'description': 'The browser (or proxy) sent a request that this server could not understand.'
    }
    return json.dumps(response, indent = 4, sort_keys = True) + '\n', 401

@app.errorhandler(werkzeug.exceptions.Forbidden)
def http_403(err):
    response = {
        'code': 403,
        'status': 'fail',
        'message': 'Forbidden',
        'description': 'You don\'t have the permission to access the requested resource. It is either read-protected or not readable by the server.'
    }
    return json.dumps(response, indent = 4, sort_keys = True) + '\n', 403

@app.errorhandler(werkzeug.exceptions.NotFound)
def http_404(err):
    response = {
        'code': 404,
        'status': 'fail',
        'message': 'Not Found',
        'description': 'The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.'
    }
    return json.dumps(response, indent = 4, sort_keys = True) + '\n', 404

@app.errorhandler(werkzeug.exceptions.MethodNotAllowed)
def http_405(err):
    response = {
        'code': 405,
        'status': 'fail',
        'message': 'Method Not Allowed',
        'description': 'The method is not allowed for the requested URL.'
    }
    return json.dumps(response, indent = 4, sort_keys = True) + '\n', 405

@app.errorhandler(werkzeug.exceptions.NotAcceptable)
def http_406(err):
    response = {
        'code': 406,
        'status': 'fail',
        'message': 'Not Acceptable',
        'description': 'The resource identified by the request is only capable of generating response entities which have content characteristics not acceptable according to the accept headers sent in the request.'
    }
    return json.dumps(response, indent = 4, sort_keys = True) + '\n', 406

@app.errorhandler(werkzeug.exceptions.Conflict)
def http_409(err):
    response = {
        'code': 409,
        'status': 'fail',
        'message': 'Conflict',
        'description': 'A conflict happened while processing the request. The resource might have been modified while the request was being processed.'
    }
    return json.dumps(response, indent = 4, sort_keys = True) + '\n', 409

@app.errorhandler(werkzeug.exceptions.InternalServerError)
def http_500(err):
    response = {
        'code': 500,
        'status': 'fail',
        'message': 'Internal Server Error',
        'description': 'The server encountered an internal error and was unable to complete your request.  Either the server is overloaded or there is an error in the application.'
    }
    return json.dumps(response, indent = 4, sort_keys = True) + '\n', 500

# Routing

# curl -k -s -X GET "http://127.0.0.1:5000/api/v1/vlans/site_a/1"
# curl -k -s -X POST -d "{\"id\":3,\"site_id\":\"site_a\"}" -H 'Content-type: application/json' "http://127.0.0.1:5000/api/v1/vlans"
api.add_resource(VLAN, '/api/v1/vlans', '/api/v1/vlans/<string:site_id>', '/api/v1/vlans/<string:site_id>/<int:id>')

# curl -k -s -X GET "http://127.0.0.1:5000/api/v1/networks/vrf_a/10.0.0.0%2F8"
# curl -k -s -X POST -d "{\"id\":\"10.0.0.0/8\",\"vrf\":\"vrf_a\"}" -H 'Content-type: application/json' "http://127.0.0.1:5000/api/v1/vlans"
api.add_resource(Network, '/api/v1/networks', '/api/v1/networks/<string:vrf>/<string:id>')



#api.add_resource(Auth, '/api/v1/auth')
#api.add_resource(BootstrapNode, '/api/v1/bootstrap/nodes/<int:label>')
#api.add_resource(BootstrapRouter, '/api/v1/bootstrap/routers/<int:router_id>')
#api.add_resource(Ctrl, '/api/v1/controller')
#api.add_resource(Lab, '/api/v1/labs', '/api/v1/labs/<string:lab_id>')
#api.add_resource(Node, '/api/v1/nodes', '/api/v1/nodes/<int:label>', '/api/v1/nodes/<int:label>/<string:action>')
#api.add_resource(Repository, '/api/v1/repositories', '/api/v1/repositories/<string:repository_id>')
#api.add_resource(Role, '/api/v1/roles', '/api/v1/roles/<string:role>')
#api.add_resource(Router, '/api/v1/routers', '/api/v1/routers/<int:router_id>')
#api.add_resource(Routing, '/api/v1/routing')
#api.add_resource(Task, '/api/v1/tasks', '/api/v1/tasks/<string:task_id>')
#api.add_resource(User, '/api/v1/users', '/api/v1/users/<string:username>')
