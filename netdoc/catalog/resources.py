#!/usr/bin/env python3
""" Resources """
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20170430'

import hashlib, io, ipaddress, json, logging, os, random, shutil, uuid
from flask import abort, request, send_file
from flask_restful import Resource
from sqlalchemy import and_
from netdoc.catalog.parsers import *
from netdoc.catalog.printers import *
from netdoc.catalog.models import *

class Network(Resource):
    def delete(self, site_id = None, vlan_id = None):
        print('TODO')
        abort(500)

    def get(self, site_id = None, id = None):
        vlan = VLANTable.query.get_or_404((site_id, id))
        return {
          'status': 'success',
          'message': 'VLAN "{}" found'.format(id),
          'data': printableVLAN(vlan)
        }, 200

    def patch(self, site_id = None, vlan_id = None):
        print('TODO')
        abort(500)

    def post(self):
        args = network_parser_post()

        if NetworkTable.query.get((args['vrf'], args['id'])):
            abort(409)
        network = NetworkTable(
            id = args['id'],
            vrf = args['vrf'],
            description = args['description']
        )
        db.session.add(network)
        db.session.commit()

        return {
            'status': 'success',
            'message': 'Network "{}" added'.format(args['id']),
            'data': printableNetworkN(network)
        }, 201

class VLAN(Resource):
    def delete(self, site_id = None, vlan_id = None):
        print('TODO')
        abort(500)

    def get(self, site_id = None, id = None):
        if site_id and id:
            print("HERE1")
            vlan = VLANTable.query.get_or_404((site_id, id))
            return {
              'status': 'success',
              'message': 'VLAN "{}" found'.format(id),
              'data': printableVLAN(vlan)
            }, 200
        if site_id:
            data = {}
            vlans = VLANTable.query.filter(VLANTable.site_id == site_id).order_by(VLANTable.id)
            for vlan in vlans:
                data[vlan.id] = printableVLAN(vlan)
            if not data:
                abort(404)
            return {
              'status': 'success',
              'message': 'VLAN on site "{}" found'.format(site_id),
              'data': data
            }, 200
        data = []
        vlans = VLANTable.query.order_by(VLANTable.site_id)
        for vlan in vlans:
            if not vlan.site_id in data:
                data.append(vlan.site_id)
        if not data:
            abort(404)
        return {
          'status': 'success',
          'message': 'Sites found',
          'data': data
        }, 200

    def patch(self, site_id = None, vlan_id = None):
        print('TODO')
        abort(500)

    def post(self):
        args = vlan_parser_post()

        if VLANTable.query.get((args['site_id'], args['id'])):
            abort(409)
        vlan = VLANTable(
            id = args['id'],
            name = args['name'],
            site_id = args['site_id'],
            description = args['description']
        )
        db.session.add(vlan)
        db.session.commit()

        return {
            'status': 'success',
            'message': 'VLAN "{}" added'.format(args['id']),
            'data': printableVLAN(vlan)
        }, 201
