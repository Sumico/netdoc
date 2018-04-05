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
    - PATCH /api/objects/1 - Edits a specific object
    - PUT /api/objects/1 - Replace a specific object (not implemented)
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
import logging, werkzeug.exceptions
from flask import Flask
#from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_script import Command, Manager, Server
from netdoc.config import *
from netdoc.catalog.errors import *

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
api = MyApi(app, catch_all_404s=True)


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

# Routing

api.add_resource(Device, '/api/v1/devices', '/api/v1/devices/<string:device_id>')

# curl -k -s -X GET "http://127.0.0.1:5000/api/v1/networks/vrf_a/10.0.0.0/8"
# curl -k -s -X POST -d "{\"id\":\"10.0.0.0/8\",\"vrf\":\"vrf_a\"}" -H 'Content-type: application/json' "http://127.0.0.1:5000/api/v1/vlans"
api.add_resource(Network, '/api/v1/networks', '/api/v1/networks/<string:vrf>', '/api/v1/networks/<string:vrf>/<string:id>/<int:mask>')

# curl -k -s -X GET "http://127.0.0.1:5000/api/v1/sites"
# curl -k -s -X POST -d "{\"id\":\"site_a\"}" -H 'Content-type: application/json' "http://127.0.0.1:5000/api/v1/sites"
api.add_resource(Site, '/api/v1/sites', '/api/v1/sites/<string:id>')

# curl -k -s -X GET "http://127.0.0.1:5000/api/v1/vlans/site_a/1"
# curl -k -s -X POST -d "{\"id\":3,\"site_id\":\"site_a\"}" -H 'Content-type: application/json' "http://127.0.0.1:5000/api/v1/vlans"
api.add_resource(VLAN, '/api/v1/vlans', '/api/v1/vlans/<string:site_id>', '/api/v1/vlans/<string:site_id>/<int:id>')
