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
    tags = db.Column(db.String(128)) # ['prod', 'core']
    interfaces = db.Column(db.String(128), db.ForeignKey('interfaces.id'), db.ForeignKey('interfaces.device'))
    site_id = db.Column(db.String(128), db.ForeignKey('sites.id')) # Padova
    # root_bridge =
    description = db.Column(db.Text)
    def __repr__(self):
        return '<Device(id={},type={})>'.format(self.id, self.type)

class InterfaceTable(db.Model):
    __tablename__ = 'interfaces'
    __mapper_args__ = {'confirm_deleted_rows': False}
    id = db.Column(db.String(128), primary_key = True) # GigabitEthernet0/0
    l2_address = db.Column(db.String(128)) # 0000.0000.0000
    type = db.Column(db.String(128)) # 40GbE
    device = db.Column(db.String(128), db.ForeignKey('devices.id'), primary_key = True)
    l3_address = db.Column(db.String(128), db.ForeignKey('l3_addresses.id'), db.ForeignKey('l3_addresses.network'))
    # remote =
    description = db.Column(db.Text)
    def __repr__(self):
        return '<Interface(id={}:{})>'.format(self.device.name, self.id)

class L2ConnectionTable(db.Model):
    __tablename__ = 'l2_connections'
    __mapper_args__ = {'confirm_deleted_rows': False}
    type = db.Column(db.String(128)) # access|trunk
    vlans = db.Column(db.Text) # all|none|1,2,3,5
    source = db.Column(db.String(128), db.ForeignKey('interfaces.device'), db.ForeignKey('interfaces.id'), primary_key = True)
    destination = db.Column(db.String(128), db.ForeignKey('interfaces.device'), db.ForeignKey('interfaces.id'), primary_key = True)
    description = db.Column(db.Text)
    def __repr__(self):
        return '<L2Connection(source={}:{},destination={}:{})>'.format(self.source, self.source_if, self.destination, self.destination_if)

class L3AddressTable(db.Model):
    __tablename__ = 'l3_addresses'
    __mapper_args__ = {'confirm_deleted_rows': False}
    id = db.Column(db.String(128), primary_key = True) # 192.168.1.1
    interface = db.Column(db.String(128), db.ForeignKey('interfaces.id'), db.ForeignKey('interfaces.device'))
    network = db.Column(db.String(128), db.ForeignKey('networks.vrf'), db.ForeignKey('networks.id'), primary_key = True)
    description = db.Column(db.Text)
    def __repr__(self):
        return '<L3Address(id={})>'.format(self.id)

class NetworkTable(db.Model):
    __tablename__ = 'networks'
    __mapper_args__ = {'confirm_deleted_rows': False}
    description = db.Column(db.Text)
    id = db.Column(db.String(128), primary_key = True) # 10.1.2.3/28
    vlan_id = db.Column(db.String(128), db.ForeignKey('vlans.id'), db.ForeignKey('vlans.site_id'))
    vrf = db.Column(db.String(128), primary_key = True) # vrf_a
    def __repr__(self):
        return '<Network(vrf={},id={})>'.format(self.vrf, self.network)

class SiteTable(db.Model):
    __tablename__ = 'sites'
    __mapper_args__ = {'confirm_deleted_rows': False}
    description = db.Column(db.Text)
    id = db.Column(db.String(128), primary_key = True) # site_a
    vlans = db.relationship('VLANTable', cascade = 'save-update, merge, delete')
    def __repr__(self):
        return '<Site(id={})>'.format(self.id)

class VLANTable(db.Model):
    __tablename__ = 'vlans'
    __mapper_args__ = {'confirm_deleted_rows': False}
    description = db.Column(db.Text)
    id = db.Column(db.Integer, primary_key = True) # 103
    name = db.Column(db.String(128)) # DMZ
    #networks = db.relationship('NetworkTable', foreign_keys = [NetworkTable.id, NetworkTable.vrf], cascade = 'save-update, merge, delete')
    #network_id = db.Column(db.String(128), db.ForeignKey('networks.id'))
    #vrf_id  = db.Column(db.String(128), db.ForeignKey('networks.vrf'))
    site_id = db.Column(db.String(128), db.ForeignKey('sites.id'), primary_key = True) # Padova
    stp_root = db.Column(db.String(128), db.ForeignKey('devices.id'))
    def __repr__(self):
        return '<VLAN(site_id={},id={})>'.format(self.site_id, self.id)
