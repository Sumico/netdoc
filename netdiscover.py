#!/usr/bin/python3

import configparser, getopt, os, sys

from pysnmp.hlapi import *

sysName = '.1.3.6.1.2.1.1.5.0'
cdpCacheDeviceId = '.1.3.6.1.4.1.9.9.23.1.2.1.1.6'
cdpCacheDevicePort = '.1.3.6.1.4.1.9.9.23.1.2.1.1.7'
cdpCachePlatform = '.1.3.6.1.4.1.9.9.23.1.2.1.1.8'
cdpInterfaceName = '.1.3.6.1.4.1.9.9.23.1.1.1.1.6'

def usage():
    print('Usage: {} [OPTIONS]'.format(sys.argv[0]))
    print('  -w STRING')
    print('     working directory')
    print('  -u STRING')
    print('     SNMPv3 username (AuthNoPriv, SHA')
    print('  -p STRING')
    print('     SNMPv3 password (AuthNoPriv, SHA)')
    print('  -h STRING')
    print('     device host or IP address (allowed multiple times)')

def getImage(platform):
    if platform == 'cisco 2610': return 'router.svg'
    if platform == 'N77-C7706': return 'nexus7k.svg'
    if platform == 'cisco WS-C2960X-48FPD-L': return 'switchl2.svg'
    if platform == 'cisco WS-C4500X-16': return 'switchl3.svg'
    if platform == 'cisco AIR-CAP2702I-E-K9': return 'apdualmode.svg'
    if platform == 'CTS-CODEC-SX10': return 'videoconf.svg'
    if platform == 'CTS-CODEC-MX300 G2': return 'videoconf.svg'
    if platform == 'CTS-CODEC-MX700/MX800': return 'videoconf.svg'
    if platform == 'CTS-CODEC-inTouch G2': return 'videoconf.svg'
    if platform == 'Cisco IP Phone SPA504G': return 'ipphone.svg'
    if platform == 'Cisco IP Phone 8945 ': return 'ipphone.svg'
    return 'unknown.svg'

def getLocal(username, password, host):
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
    device = {
        'id': str(varBinds[0][1])
    }
    return device

def getNeighbors(username, password, host):
    neighbors = []
    local_port = {}

    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        UsmUserData(username, password, authProtocol = usmHMACSHAAuthProtocol),
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(cdpInterfaceName)),
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
        neighbors.append({
            'id': str(varBinds[0][1]),
            'port': shortensIf(str(varBinds[1][1])),
            'platform': str(varBinds[2][1]),
            'local_port': shortensIf(local_port[neighbor_id]),
            'image': getImage(str(varBinds[2][1]))
        })


    return neighbors

def shortensIf(interface_name):
    interface_name = interface_name.replace('TenGigabitEthernet', 'te')
    interface_name = interface_name.replace('GigabitEthernet', 'gi')
    interface_name = interface_name.replace('FastEthernet', 'fa')
    interface_name = interface_name.replace('Ethernet', 'e')
    return interface_name

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'u:p:h:w:')
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    username = None
    password = None
    hosts = []
    working_dir = os.path.dirname(os.path.abspath(__file__))
    for opt, arg in opts:
        if opt == '-u':
            username = arg
        elif opt == '-p':
            password = arg
        elif opt == '-h':
            hosts.append(arg)
        elif opt == '-w':
            working_dir = arg
        else:
            assert False, 'unhandled option'
    if not username or not password or len(hosts) == 0:
        usage()
        sys.exit(2)

    discovered_nodes_file = 'discovered_nodes.ini'
    discovered_connections_file = 'discovered_connections.ini'
    # Creating configuration files
    for config_file in [discovered_nodes_file, discovered_connections_file]:
        config = configparser.ConfigParser()
        config_file = '{}/{}'.format(working_dir, config_file)
        if not os.path.isfile(config_file):
            with open(config_file, 'w') as config_fd:
                config.write(config_fd)
    # Reading configuration files
    discovered_nodes = configparser.ConfigParser()
    discovered_nodes.read(discovered_nodes_file)
    discovered_connections = configparser.ConfigParser()
    discovered_connections.read(discovered_connections_file)

    # Disabling all nodes
    for discovered_node in discovered_nodes.sections():
        discovered_nodes[discovered_node]['disabled'] = 'true'
    # Disabling all connections
    for discovered_connection in discovered_connections.sections():
        discovered_connections[discovered_connection]['disabled'] = 'true'

    for host in hosts:
        device = getLocal(username = username, password = password, host = host)
        neighbors = getNeighbors(username = username, password = password, host = host)
        if not discovered_nodes.has_section(device['id']):
            discovered_nodes[device['id']] = {
                'id': device['id'],
                'disabled': 'false'
            }
        else:
            # Activate node
            discovered_nodes[device['id']]['disabled'] = 'false'
        for neighbor in neighbors:
            if not discovered_nodes.has_section(neighbor['id']):
                # Adding node
                discovered_nodes[neighbor['id']] = {
                    'id': neighbor['id'],
                    'image': getImage(neighbor['platform']),
                    'platform': neighbor['platform'],
                    'disabled': 'false'
                }
            else:
                # Activate node and setting attributes
                discovered_nodes[neighbor['id']]['disabled'] = 'false'
                discovered_nodes[neighbor['id']]['platform'] = neighbor['platform']

            if device['id'] < neighbor['id']:
                source = device['id']
                source_if = neighbor['local_port']
                destination = neighbor['id']
                destination_if = neighbor['port']
            else:
                source = neighbor['id']
                source_if = neighbor['port']
                destination = device['id']
                destination_if = neighbor['local_port']
            if not discovered_connections.has_section('{}:{}-{}:{}'.format(source, source_if, destination, destination_if)):
                # Adding connections
                discovered_connections['{}:{}-{}:{}'.format(source, source_if, destination, destination_if)] = {
                    'source': source,
                    'source_if': source_if,
                    'destination': destination,
                    'destination_if': destination_if,
                    'disabled': 'false'
                }
            else:
                # Activate connection
                discovered_connections['{}:{}-{}:{}'.format(source, source_if, destination, destination_if)]['disabled'] = 'false'

    # Save current state after scanning
    with open(discovered_nodes_file, 'w') as config_fd:
        discovered_nodes.write(config_fd)
    with open(discovered_connections_file, 'w') as config_fd:
        discovered_connections.write(config_fd)

    print(username)
    print(password)
    print(hosts)
    print(working_dir)

if __name__ == "__main__":
    main()
    sys.exit(0)

