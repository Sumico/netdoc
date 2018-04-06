#!/usr/bin/env python3
""" Resources """
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20170430'

import ipaddress, werkzeug.exceptions
from flask import abort, request, send_file
from flask_restful import Resource
from sqlalchemy import and_
from netdoc.catalog.parsers import *
from netdoc.catalog.printers import *
from netdoc.catalog.models import *

class Device(Resource):
    def delete(self, site_id = None, id = None):
        abort(500, 'TODO')

    def get(self, vrf = None, id = None):
        if vrf and id:
            # List network inside a VRF
            network = NetworkTable.query.get((vrf, id))
            if not network:
                abort(404, 'Network "{}" not found under VRF "{}"'.format(id, vrf))
            return {
              'status': 'success',
              'message': 'Network "{}" found'.format(id),
              'data': printableVLAN(vlan)
            }, 200
        if vrf:
            # List all networks inside a VRF
            data = {}
            networks = NetworkTable.query.filter(NetworkTable.vrf == vrf).order_by(NetworkTable.id)
            for network in networks:
                data[network.id] = printableNetwork(network)
            if not data:
                abort(404, 'No networks under VRF "{}"'.format(vrf))
            return {
              'status': 'success',
              'message': 'Network on VRF "{}" found'.format(vrf),
              'data': data
            }, 200
        # List all VRFs
        data = []
        networks = NetworkNTable.query.order_by(NetworkTable.vrf)
        for network in networks:
            if not network.vrf in data:
                data.append(network.vrf)
        if not data:
            abort(404, 'No VRF found')
        return {
          'status': 'success',
          'message': 'VRFs found',
          'data': data
        }, 200

    def patch(self):
        abort(500, 'TODO')

    def post(self):
        args = network_parser_post()

        if NetworkTable.query.get((args['vrf'], args['id'])):
            abort(409, 'Network "{}" already exists under VRF "{}"'.format(args['id'], args['vrf']))
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
            'data': printableNetwork(network)
        }, 201

    def put(self):
        abort(500, 'TODO')

class Network(Resource):
    def delete(self):
        abort(500, 'TODO')

    def get(self, vrf = None, id = None, mask = None):
        if vrf and id and mask:
            # List network inside a VRF
            network = NetworkTable.query.get(('{}/{}'.format(id, mask), vrf))
            if not network:
                abort(404, 'Network "{}/{}" not found under VRF "{}"'.format(id, mask, vrf))
            return {
              'status': 'success',
              'message': 'Network "{}" found'.format(id),
              'data': printableNetwork(network)
            }, 200
        if vrf:
            # List all networks inside a VRF
            data = {}
            networks = NetworkTable.query.filter(NetworkTable.vrf == vrf).order_by(NetworkTable.id)
            for network in networks:
                data[network.id] = printableNetwork(network)
            if not data:
                abort(404, 'No networks under VRF "{}"'.format(vrf))
            return {
              'status': 'success',
              'message': 'Network on VRF "{}" found'.format(vrf),
              'data': data
            }, 200
        # List all VRFs
        data = []
        networks = NetworkTable.query.order_by(NetworkTable.vrf)
        for network in networks:
            if not network.vrf in data:
                data.append(network.vrf)
        if not data:
            abort(404, 'No VRF found')
        return {
          'status': 'success',
          'message': 'VRFs found',
          'data': data
        }, 200

    def patch(self):
        abort(500, 'TODO')

    def post(self):
        args = network_parser_post()

        if NetworkTable.query.get((args['id'], args['vrf'])):
            abort(409, 'Network "{}" already exists under VRF "{}"'.format(args['id'], args['vrf']))
        network = NetworkTable(
            id = args['id'],
            vrf = args['vrf'],
            site_id = args['site_id'],
            vlan_id = args['vlan_id'],
            description = args['description']
        )
        db.session.add(network)
        db.session.commit()

        return {
            'status': 'success',
            'message': 'Network "{}" added'.format(args['id']),
            'data': printableNetwork(network)
        }, 201

    def put(self):
        abort(500, 'TODO')

class Site(Resource):
    def delete(self):
        abort(500, 'TODO')

    def get(self, id = None):
        if id:
            # List all sites
            site = SiteTable.query.get((id))
            if not site:
                abort(404, 'Site "{}" not found'.format(id))
            return {
              'status': 'success',
              'message': 'Site "{}" found'.format(id),
              'data': printableSite(site, summary = False)
            }, 200
        # List all sites
        data = []
        sites = SiteTable.query.order_by(SiteTable.id)
        for site in sites:
            data.append(site.id)
        if not data:
            abort(404, 'No site found')
        return {
          'status': 'success',
          'message': 'Sites found',
          'data': data
        }, 200

    def patch(self):
        abort(500, 'TODO')

    def post(self):
        args = site_parser_post()

        if SiteTable.query.get((args['id'])):
            abort(409, 'Site "{}" already exists'.format(args['id']))
        site = SiteTable(
            id = args['id'],
            description = args['description']
        )
        db.session.add(site)
        db.session.commit()

        return {
            'status': 'success',
            'message': 'Site "{}" added'.format(args['id']),
            'data': printableSite(site)
        }, 201

    def put(self):
        abort(500, 'TODO')

class VLAN(Resource):
    def delete(self):
        abort(500, 'TODO')

    def get(self, site_id = None, id = None):
        if site_id and id:
            # List a VLAN inside a site
            vlan = VLANTable.query.get((id, site_id))
            if not vlan:
                abort(404, 'VLAN "{}" not found under site "{}"'.format(id, site_id))
            return {
              'status': 'success',
              'message': 'VLAN "{}" found'.format(id),
              'data': printableVLAN(vlan)
            }, 200
        if site_id:
            # List all VLANs inside a site
            data = {}
            vlans = VLANTable.query.filter(VLANTable.site_id == site_id).order_by(VLANTable.id)
            for vlan in vlans:
                data[vlan.id] = printableVLAN(vlan)
            if not data:
                abort(404, 'No VLANs under site "{}"'.format(site_id))
            return {
              'status': 'success',
              'message': 'VLAN on site "{}" found'.format(site_id),
              'data': data
            }, 200
        # List all sites
        data = []
        vlans = VLANTable.query.order_by(VLANTable.site_id)
        for vlan in vlans:
            if not vlan.site_id in data:
                data.append(vlan.site_id)
        if not data:
            abort(404, 'No site found')
        return {
          'status': 'success',
          'message': 'Sites found',
          'data': data
        }, 200

    def patch(self):
        abort(500, 'TODO')

    def post(self):
        args = vlan_parser_post()

        site = SiteTable.query.get((args['site_id']))
        if not site:
            abort(406, 'Site "{}" not found'.format(args['site_id']))
        if VLANTable.query.get((args['id'], args['site_id'])):
            abort(409, 'VLAN "{}" already exists under site "{}"'.format(args['id'], args['site_id']))

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

    def put(self):
        abort(500, 'TODO')
