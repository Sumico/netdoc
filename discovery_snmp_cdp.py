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
    print('  -d         enable debug')
    print('  -u STRING  SNMPv3 username (AuthNoPriv, SHA')
    print('  -p STRING  SNMPv3 password (AuthNoPriv, SHA)')
    print('  -h STRING  device host or IP address (allowed multiple times)')

#def getImage(platform):
#    if platform == 'AIR-WLC4402-12-K9': return 'icons/wifi_controller.png'
#    if platform == 'Cisco 1841': return 'icons/router.png'
#    if platform == 'cisco 2610': return 'icons/router.png'
#    if platform == 'Cisco 3845': return 'icons/router.png'
#    if platform == 'cisco AIR-CAP2702I-E-K9': return 'icons/wifi_access_point_dual_band.png'
#    if platform == 'cisco AIR-LAP1142N-E-K9': return 'icons/wifi_access_point_dual_band.png'
#    if platform == 'Cisco IP Phone 8945 ': return 'icons/phone_ip.png'
#    if platform == 'Cisco IP Phone SPA504G': return 'icons/phone_ip.png'
#    if platform == 'cisco WS-C2960S-48FPS-L': return 'icons/switch_l2.png'
#    if platform == 'cisco WS-C2960X-48FPD-L': return 'icons/switch_l2.png'
#    if platform == 'cisco WS-C3750G-12S': return 'icons/switch_l3.png'
#    if platform == 'cisco WS-C3750G-24TS-1U': return 'icons/switch_l3.png'
#    if platform == 'cisco WS-C3750G-48TS': return 'icons/switch_l3.png'
#    if platform == 'cisco WS-C4500X-16': return 'icons/switch_l3.png'
#    if platform == 'CTS-CODEC-MX300 G2': return 'icons/vcf_500.png'
#    if platform == 'CTS-CODEC-MX700/MX800': return 'icons/vcf_1000.png'
#    if platform == 'DS-C9148-16P-K9': return 'icons/mds_fabric_a.png'
#    if platform == 'DS-C9148S-K9': return 'icons/mds_fabric_a.png'
#    if platform == 'FAS8060': return 'icons/storage_nfs.png'
#    if platform == 'N10-S6100': return 'icons/nexus_6000.png'
#    if platform == 'N5K-C5010P-BF': return 'icons/nexus_5000.png'
#    if platform == 'N5K-C5672UP': return 'icons/nexus_5000.png'
#    if platform == 'N77-C7706': return 'icons/nexus_7000.png'
#    if platform == 'N9K-C93180YC-EX': return 'icons/nexus_9300_aci_mode.png'
#    if platform == 'UCS-FI-6296UP': return 'icons/nexus_6000.png'
#    return 'icons/generic.png'

def getFacts(username, password, host):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
            UsmUserData(username, password, authProtocol = usmHMACSHAAuthProtocol),
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

def getCDPNeighbors(username, password, host):
    # TODO: add multiple neighbors under a single interface
    neighbors = {}
    local_port = {}

    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        UsmUserData(username, password, authProtocol = usmHMACSHAAuthProtocol),
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
        UsmUserData(username, password, authProtocol = usmHMACSHAAuthProtocol),
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

    # Reading options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'di:u:p:')
    except getopt.GetoptError as err:
        logging.error(err)
        usage()
        sys.exit(255)

    for opt, arg in opts:
        if opt == '-d':
            logging.basicConfig(level = logging.DEBUG)
        elif opt == '-i':
            inventory_file = arg
        elif opt == '-u':
            username = arg
        elif opt == '-p':
            password = arg
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
    if not username or not password:
        logging.error('username and/or password not set'.format(base_dir))
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

        facts = getFacts(username = host.vars['snmp_username'], password = host.vars['snmp_password'], host = host.vars['ansible_host'])
        cdp_neighbors = getCDPNeighbors(username = host.vars['snmp_username'], password = host.vars['snmp_password'], host = host.vars['ansible_host'])

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

