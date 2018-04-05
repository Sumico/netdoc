#!/usr/bin/env python3
""" Printers  """
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20170430'

from netdoc.catalog.models import *

def printableNetwork(network):
    return {
        'id': network.id,
        'vrf': network.vrf,
        'description': network.description
    }

def printableSite(site, summary = True):
    data = {
        'id': site.id,
        'description': site.description
    }
    if not summary:
        data['vlans'] = {}
        for vlan in site.vlans:
            data['vlans'][vlan.id] = printableVLAN(vlan)
    return data

def printableVLAN(vlan):
    data = {
        'id': vlan.id,
        'name': vlan.name,
        'site_id': vlan.site_id,
        'description': vlan.description
    }
    data['networks'] = {}
    #for
    return data
