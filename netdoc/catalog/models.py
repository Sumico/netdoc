#!/usr/bin/env python3
""" Database structure """
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20170430'

from netdoc import db

"""
    Every object is defined into:
    - models.py (database structure)
    - resources.py (GET/POST/... methods)
    - parsers.py (parse HTTP request and set defaults)
    - printers.py (define how to print JSONs)
"""

class DeviceTable(db.Model):
    __tablename__ = 'devices'
    __mapper_args__ = {'confirm_deleted_rows': False}
    id = db.Column(db.String(128), primary_key = True) # RouterA
    icon = db.Column(db.String(128)) # router.png
    interfaces = db.Column(db.Text) # {'Ethernet0/0': {'l2_addresses': [], 'l3_addresses': []}
    description = db.Column(db.Text)
    def __repr__(self):
        return '<Device(id={},type={})>'.format(self.id, self.type)

class L2ConnectionTable(db.Model):
    __tablename__ = 'l2_connections'
    __mapper_args__ = {'confirm_deleted_rows': False}
    #source = db.Column(db.String(128), db.ForeignKey('devices.id'), primary_key = True)
    source_if = db.Column(db.String(128), primary_key = True)
    #destination = db.Column(db.String(128), db.ForeignKey('devices.id'), primary_key = True)
    destination_if = db.Column(db.String(128), primary_key = True)
    type = db.Column(db.String(128)) # access|trunk
    vlans = db.Column(db.Text) # all|none|1,2,3,5,8
    def __repr__(self):
        return '<VLAN(source={}:{},destination={}:{})>'.format(self.source, self.source_if, self.destination, self.destination_if)

class NetworkTable(db.Model):
    __tablename__ = 'networks'
    __mapper_args__ = {'confirm_deleted_rows': False}
    vrf = db.Column(db.String(128), primary_key = True)
    id = db.Column(db.String(128), primary_key = True) # 10.1.2.3/28
    #vlan = db.relationship('VLANTable', cascade = 'save-update, merge, delete')
    description = db.Column(db.Text)
    def __repr__(self):
        return '<Network(vrf={},id={})>'.format(self.vrf, self.network)

class VLANTable(db.Model):
    __tablename__ = 'vlans'
    __mapper_args__ = {'confirm_deleted_rows': False}
    site_id = db.Column(db.String(128), primary_key = True)
    id = db.Column(db.Integer, primary_key = True)
    #network = db.Column(db.String(128), db.ForeignKey('networks.vrf_id'), db.ForeignKey('networks.network_id'))
    name = db.Column(db.String(128))
    #stp_root = db.Column(db.String(128), db.ForeignKey('devices.id'))
    description = db.Column(db.Text)
    def __repr__(self):
        return '<VLAN(site_id={},id={})>'.format(self.site_id, self.id)
