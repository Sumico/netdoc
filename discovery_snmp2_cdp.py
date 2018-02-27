#!/usr/bin/python3
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://www.gnu.org/licenses/gpl.html'
__revision__ = '20170329'

import configparser, getopt, json, logging, os, re, sys
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from pysnmp.hlapi import *

# Default settings
logging.basicConfig(level = logging.WARNING)

# Global variables
sysName = '.1.3.6.1.2.1.1.5.0'
cdpCacheDeviceId = '.1.3.6.1.4.1.9.9.23.1.2.1.1.6'
cdpCacheDevicePort = '.1.3.6.1.4.1.9.9.23.1.2.1.1.7'
cdpCachePlatform = '.1.3.6.1.4.1.9.9.23.1.2.1.1.8'
ifDescr = '.1.3.6.1.2.1.2.2.1.2'

def usage():
    print('Usage: {} [OPTIONS]'.format(sys.argv[0]))
    print('  -i STRING  inventory file')
    print('  -d         enable debug')

def getFacts(community, host):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((host, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(sysName)),
            lookupMib = False
        )
    )
    if errorIndication or errorStatus or errorIndex:
        return None
    facts = {
        'ansible_facts': {
            'ansible_net_hostname': str(varBinds[0][1])
        }
    }
    return facts

def getCDPNeighbors(community, host):
    # TODO: add multiple neighbors under a single interface
    neighbors = {}
    local_port = {}

    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(ifDescr)),
        lookupMib = False,
        lexicographicMode = False
    ):
        if errorIndication or errorStatus or errorIndex:
            return None
        local_port[int(str(varBinds[0][0]).split('.')[-1])] = str(varBinds[0][1])

    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(cdpCacheDeviceId)),
        ObjectType(ObjectIdentity(cdpCacheDevicePort)),
        ObjectType(ObjectIdentity(cdpCachePlatform)),
        lookupMib = False,
        lexicographicMode = False
    ):
        if errorIndication or errorStatus or errorIndex:
            return None
        neighbor_id = int(str(varBinds[0][0]).split('.')[-2])
        neighbors.setdefault(local_port[neighbor_id], [])
        neighbors[local_port[neighbor_id]].append({
            'remote_system_name': re.findall(r'([^(\n]+).*', str(varBinds[0][1]))[0],
            'remote_port': str(varBinds[1][1]),
            'remote_port_description': str(varBinds[1][1]),
            'remote_system_description': str(varBinds[2][1])
        })

    return neighbors

def main():
    # Set default
    base_dir = '.'
    discovered_devices = {}
    inventory_file = None
    username = None
    password = None
    community = None

    # Reading options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'di:')
    except getopt.GetoptError as err:
        logging.error(err)
        usage()
        sys.exit(255)

    for opt, arg in opts:
        if opt == '-d':
            logging.basicConfig(level = logging.DEBUG)
        elif opt == '-i':
            inventory_file = arg
        else:
            logging.error('unhandled option ({})'.format(opt))
            usage()
            sys.exit(255)

    # Checking options and environment
    if not os.path.isdir(base_dir):
        logging.error('base directory does not exist ({})'.format(base_dir))
        sys.exit(255)
    if not inventory_file:
        logging.error('inventory file not specified'.format(base_dir))
        sys.exit(255)
    if not os.path.isfile(inventory_file):
        logging.error('inventory file does not exist ({})'.format(inventory_file))
        sys.exit(255)

    # Loading Ansible inventory
    ansible_loader = DataLoader()
    try:
        ansible_inventory = InventoryManager(loader = ansible_loader, sources = inventory_file)
    except:
        logging.error('cannot read inventory file ({})'.format(inventory_file))
        sys.exit(255)
    variable_manager = VariableManager(loader = ansible_loader, inventory = ansible_inventory)

    # Discover each host
    for host in ansible_inventory.get_hosts():
        try:
            os.makedirs('devices/{}'.format(host), exist_ok = True)
        except:
            logging.error('cannot create directory (devices/{})'.format(host))

        facts = getFacts(community = host.vars['snmp_community'], host = host.vars['ansible_host'])
        logging.debug('connecting to {} using community {}'.format(host.vars['ansible_host'], host.vars['snmp_community']))
        cdp_neighbors = getCDPNeighbors(community = host.vars['snmp_community'], host = host.vars['ansible_host'])

        try:
            facts_output = open('devices/{}/facts.json'.format(host), 'w+')
            facts_output.write(json.dumps(facts))
            facts_output.close()
        except:
            logging.error('cannot write facts (devices/{}/facts.json)'.format(host))
            continue

        try:
            cdp_neighbors_output = open('devices/{}/cdp_neighbors.json'.format(host), 'w+')
            cdp_neighbors_output.write(json.dumps(cdp_neighbors))
            cdp_neighbors_output.close()
        except:
            logging.error('cannot write facts (devices/{}/cdp_neighbors.json)'.format(host))
            continue

if __name__ == "__main__":
    main()
    sys.exit(0)

