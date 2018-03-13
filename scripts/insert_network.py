#!/usr/bin/env python3
""" Resources """
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20170430'

import ipaddress
from openpyxl import load_workbook

wb = load_workbook(filename = 'vlan.xlsx', data_only = True)
ws = wb.active

for row in ws:
    vlan_id = row[0].value
    vlan_name = row[1].value
    network = row[2].value
    netmask = row[3].value
    print(vlan_id)
