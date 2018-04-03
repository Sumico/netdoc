#!/usr/bin/env python3
""" Resources """
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20170430'

import ipaddress, logging, requests
from openpyxl import load_workbook

wb = load_workbook(filename = 'vlan.xlsx', data_only = True)
ws = wb.active

for row in ws:
    if not row[0].value:
        break
    try:
        vlan_id = int(row[0].value)
    except Exception as err:
        logging.warning('invalid VLAN "{}"'.format(row[0].value))
        continue
    vlan_name = row[1].value
    if vlan_id < 1 or vlan_id > 4096:
        logging.warning('invalid VLAN ID "{}"'.format(row[0].value))
        continue
    try:
        network = ipaddress.IPv4Network('{}/{}'.format(row[2].value, row[3].value))
    except Exception as err:
        logging.warning('invalid network "{}" with subnet mask "{}"'.format(row[2].value, row[3].value))
        continue

    # Adding network
    data = {
        'vrf': 'default',
        'id': str(network.with_prefixlen)
    }
    try:
        r = requests.post('http://localhost:5000/api/v1/networks', json = data)
        if r.status_code != 200:
            logging.warning('adding network "{}" fails with "{}"'.format(data['id'], r.status_code))
            logging.warning(r.json())
        else:
            logging.warning('cannot add network "{}"'.format(data['id']))
            logging.warning(r.json())
    except Exception as err:
        logging.warning('cannot add network "{}"'.format(data['id']))
        logging.warning(err)
