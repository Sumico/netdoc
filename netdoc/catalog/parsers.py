#!/usr/bin/env python3
""" Data parsers """
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20170430'

from flask import abort, jsonify, make_response, request
from netdoc.catalog.models import *
import logging

# Generic parsers
def parse_json():
    post_args = request.json
    if not post_args:
        abort(make_response(jsonify(message = 'Input data is not a valid JSON'), 400))
    return post_args

def parse_type(arg, arg_name, arg_type):
    if not isinstance(arg, arg_type):
        abort(make_response(jsonify(message = 'Argument "{}" must be "{}"'.format(arg_name, arg_type)), 400))
    return arg

# Custom parsers
def vlan_parser_post():
    args = {}
    post_args = parse_json()

    if 'id' in post_args:
        args['id'] = parse_type(post_args['id'], 'id', int)
        if args['id'] < 1 or args['id'] > 4096:
            abort(make_response(jsonify(message = 'VLAN "{}" is invalid'.format(post_args['id'])), 400))
    else:
        abort(make_response(jsonify(message = 'id is mandatory'), 400))

    if 'site_id' in post_args:
        args['site_id'] = parse_type(post_args['site_id'], 'site_id', str)
        if args['site_id'] == '':
            abort(make_response(jsonify(message = 'site_id is invalid'), 400))
    else:
        args['site_id'] = 'default'

    if 'name' in post_args:
        args['name'] = parse_type(post_args['name'], 'name', str)
        if args['name'] == '':
            abort(make_response(jsonify(message = 'name is invalid'), 400))
    else:
        args['name'] = 'VLAN{:04}'.format(args['id'])

    if 'description' in post_args:
        args['description'] = parse_type(post_args['description'], 'description', str)
        if args['description'] == '':
            abort(make_response(jsonify(message = 'description is invalid'), 400))
    else:
        args['description'] = ''

    return args
