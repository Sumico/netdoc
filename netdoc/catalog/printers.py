#!/usr/bin/env python3
""" Printers  """
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20170430'

from netdoc.catalog.models import *

def printableVLAN(vlan):
    return {
        'id': vlan.id,
        'name': vlan.name,
        'site_id': vlan.site_id,
        'description': vlan.description
    }
