#!/usr/bin/env python3
""" Data parsers """
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20170430'

import ipaddress, logging, re, werkzeug.exceptions
from flask import abort, jsonify, make_response, request
from netdoc.catalog.models import *

re_site_id = re.compile('^[0-9A-Za-z_]+$')

# Generic parsers
def parse_json():
    post_args = request.json
    if not post_args:
        abort(400, 'JSON "{}" is not valid'.format(post_args))
    return post_args

def parse_type(arg, arg_name, arg_type):
    if not isinstance(arg, arg_type):
        abort(400, 'Argument "{}" must be "{}"'.format(arg_name, arg_type))
    return arg

# Custom parsers
def network_parser_post():
    args = {}
    post_args = parse_json()

    if 'id' in post_args:
        args['id'] = parse_type(post_args['id'], 'id', str)
        try:
            network = ipaddress.IPv4Network(args['id'])
        except Exception as err:
            abort(400, 'Network "{}" is not valid'.format(id))
    else:
        abort(400, 'Network "id" is mandatory')

    if 'vrf' in post_args:
        args['vrf'] = parse_type(post_args['vrf'], 'vrf', str)
        if args['vrf'] == '':
            abort(400, 'VRF "{}" is not valid'.format(vrf))
    else:
        args['vrf'] = 'default'

    if 'site_id' in post_args:
        args['site_id'] = parse_type(post_args['site_id'], 'site_id', str)
        if args['site_id'] == '':
            abort(400, 'Site "{}" is not valid'.format(site_id))
    else:
        args['site_id'] = 'default'

    if 'description' in post_args:
        args['description'] = parse_type(post_args['description'], 'description', str)
        if args['description'] == '':
            abort(400, 'description "{}" is not valid'.format(description))
    else:
        args['description'] = ''

    if 'vlan_id' in post_args:
        args['vlan_id'] = parse_type(post_args['vlan_id'], 'vlan_id', int)
        if args['vlan_id'] < 1 or args['vlan_id'] > 4096:
            abort(400, 'VLAN "{}" is not valid'.format(id))
    else:
        args['vlan_id'] = 0

    return args

def site_parser_post():
    args = {}
    post_args = parse_json()

    if 'id' in post_args:
        args['id'] = parse_type(post_args['id'], 'id', str)
        if not re_site_id.match(args['id']):
            abort(400, 'Site "{}" is not valid'.format(args['id']))
    else:
        abort(400, 'Site "id" is mandatory')

    if 'description' in post_args:
        args['description'] = parse_type(post_args['description'], 'description', str)
        if args['description'] == '':
            abort(400, 'description "{}" is not valid'.format(description))
    else:
        args['description'] = ''

    return args

def vlan_parser_post():
    args = {}
    post_args = parse_json()

    if 'id' in post_args:
        args['id'] = parse_type(post_args['id'], 'id', int)
        if args['id'] < 1 or args['id'] > 4096:
            abort(400, 'VLAN "{}" is not valid'.format(id))
    else:
        abort(make_response(jsonify(message = 'id is mandatory'), 400))

    if 'site_id' in post_args:
        args['site_id'] = parse_type(post_args['site_id'], 'site_id', str)
        if args['site_id'] == '':
            abort(400, 'Site "{}" is not valid'.format(site_id))
    else:
        args['site_id'] = 'default'

    if 'name' in post_args:
        args['name'] = parse_type(post_args['name'], 'name', str)
        if args['name'] == '':
            abort(400, 'name "{}" is not valid'.format(name))
    else:
        args['name'] = 'VLAN{:04}'.format(args['id'])

    if 'description' in post_args:
        args['description'] = parse_type(post_args['description'], 'description', str)
        if args['description'] == '':
            abort(400, 'description "{}" is not valid'.format(description))
    else:
        args['description'] = ''

    return args
