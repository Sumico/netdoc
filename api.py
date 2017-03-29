#!/usr/bin/env python3
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
    - 422 fail - Input data missing or not valid
    - 500 error - Server error, maybe a bug/exception or a backend/database error
"""
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://www.gnu.org/licenses/gpl.html'
__revision__ = '20170329'

import configparser, flask, json, logging, os, random

working_dir = os.path.dirname(os.path.abspath(__file__))
app = flask.Flask(__name__)

discovered_nodes_file = 'discovered_nodes.ini'
discovered_nodes = configparser.ConfigParser()
discovered_nodes.read(discovered_nodes_file)
discovered_connections_file = 'discovered_connections.ini'
discovered_connections = configparser.ConfigParser()
discovered_connections.read(discovered_connections_file)

def saveConfig():
    with open(discovered_nodes_file, 'w') as config_fd:
        discovered_nodes.write(config_fd)
    with open(discovered_connections_file, 'w') as config_fd:
        discovered_connections.write(config_fd)

@app.errorhandler(400)
def http_401(err):
    response = {
        'code': 400,
        'status': 'bad request',
        'message': str(err)
    }
    return flask.jsonify(response), response['code']

@app.errorhandler(401)
def http_401(err):
    response = {
        'code': 401,
        'status': 'unauthorized',
        'message': str(err)
    }
    return flask.jsonify(response), response['code']

@app.errorhandler(403)
def http_403(err):
    response = {
        'code': 403,
        'status': 'forbidden',
        'message': str(err)
    }
    return flask.jsonify(response), response['code']

@app.errorhandler(404)
def http_404(err):
    response = {
        'code': 404,
        'status': 'fail',
        'message': str(err)
    }
    return flask.jsonify(response), response['code']

@app.errorhandler(405)
def http_405(err):
    response = {
        'code': 405,
        'status': 'fail',
        'message': str(err)
    }
    return flask.jsonify(response), response['code']

@app.errorhandler(409)
def http_409(err):
    response = {
        'code': 409,
        'status': 'fail',
        'message': str(err)
    }
    return flask.jsonify(response), response['code']

@app.errorhandler(422)
def http_422(err):
    response = {
        'code': 422,
        'status': 'fail',
        'message': str(err)
    }
    return flask.jsonify(response), response['code']

@app.errorhandler(Exception)
def http_500(err):
    import traceback
    response = {
        'code': 500,
        'status': 'error',
        'message': traceback.format_exc()
    }
    logging.error(err)
    logging.error(traceback.format_exc())
    return flask.jsonify(response), response['code']

@app.route('/', methods = ['GET'])
def getPage():
    return flask.render_template('template.html', name = 'netdoc')

# curl -s -D- -X GET http://127.0.0.1:5000/api/nodes
# curl -s -D- -X GET http://127.0.0.1:5000/api/nodes/nodeid
@app.route('/api/nodes', methods = ['GET'])
@app.route('/api/nodes/<id>', methods = ['GET'])
def getNodes(id = None):
    nodes = {}
    if id and discovered_nodes.has_section(id):
        nodes[id] = discovered_nodes[id]
    elif id:
        flask.abort(404)
    else:
        for discovered_node in discovered_nodes.sections():
            nodes[discovered_node] = discovered_nodes[discovered_node]

    response = {
        'code': 200,
        'status': 'success',
        'data': {}
    }

    for node in nodes:
        label = discovered_nodes[node]['label'] if discovered_nodes.has_option(node, 'label') else discovered_nodes[node]['id']
        left = discovered_nodes[node]['left'] if discovered_nodes.has_option(node, 'left') else random.randint(0, 10) * 10
        top = discovered_nodes[node]['top'] if discovered_nodes.has_option(node, 'top') else random.randint(0, 10) * 10
        response['data'][node] = {
            'disabled': discovered_nodes[node]['disabled'],
            'image': discovered_nodes[node]['image'],
            'id': discovered_nodes[node]['id'],
            'label': label,
            'left': left,
            'platform': discovered_nodes[node]['platform'],
            'top': top
        }
    return flask.jsonify(response), response['code']

# curl -s -D- -X PUT -d '{"left": 181, "top": 818"}' -H 'Content-type: application/json' http://127.0.0.1:5000/api/nodes/nodeid
@app.route('/api/nodes/<id>', methods = ['PUT'])
def putNode(id):
    if not discovered_nodes.has_section(id):
        flask.abort(404)
    data = flask.request.get_json(silent = True)
    if not data:
        flask.abort(400)
    if not 'left' in data.keys() and not 'top' in data.keys():
        flask.abort(400)
    if 'left' in data.keys():
        discovered_nodes[id]['left'] = str(data['left'])
    if 'top' in data.keys():
        discovered_nodes[id]['top'] = str(data['top'])
    saveConfig()
    return getNodes(id)

# curl -s -D- -X GET http://127.0.0.1:5000/api/connections
# curl -s -D- -X GET http://127.0.0.1:5000/api/connections/connectionid
@app.route('/api/connections', methods = ['GET'])
@app.route('/api/connections/<id>', methods = ['GET'])
def getConnections(id = None):
    connections = {}
    if id and discovered_connections.has_section(id):
        connections[id] = discovered_connections[id]
    elif id:
        flask.abort(404)
    else:
        for discovered_connection in discovered_connections.sections():
            connections[discovered_connection] = discovered_connections[discovered_connection]

    response = {
        'code': 200,
        'status': 'success',
        'data': {}
    }

    for connection in connections:
        response['data'][connection] = {
            'disabled': discovered_connections[connection]['disabled'],
            'source': discovered_connections[connection]['source'],
            'source_if': discovered_connections[connection]['source_if'],
            'destination': discovered_connections[connection]['destination'],
            'destination_if': discovered_connections[connection]['destination_if']
        }
    return flask.jsonify(response), response['code']

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, extra_files = ['{}/{}'.format(working_dir, 'discovered_nodes.ini'), '{}/{}'.format(working_dir, 'discovered_connections.ini'), '{}/template.html'.format(working_dir)], debug = True)

