#!/usr/bin/env python3
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20171206'

import configparser, flask, getopt, json, logging, os, random, sys

# Default settings
logging.basicConfig(level = logging.WARNING)

# Global variables
working_dir = '{}/working/{}'.format(os.path.dirname(os.path.abspath(__file__)), os.environ.get('NETDOC_FOLDER', 'default'))
app = flask.Flask(__name__)
links = []
devices_file = '{}/devices.ini'.format(working_dir)
device_options = configparser.ConfigParser()
device_options.read(devices_file)

def usage():
    print('Usage: {} [OPTIONS]'.format(sys.argv[0]))
    print('  -d         enable debug')

def saveConfig():
    with open(devices_file, 'w') as device_fp:
        device_options.write(device_fp)

@app.route('/', methods = ['GET'])
def getPage():
    return flask.render_template('template.html', name = 'netdoc')

# curl -s -D- -X GET http://127.0.0.1:5000/api/nodes
@app.route('/api/nodes', methods = ['GET'])
def getNodes():
    nodes = {}
    for link in links:
        if not link['source'] in nodes:
            nodes[link['source']] = {}
        if not link['destination'] in nodes:
            nodes[link['destination']] = {}

    response = {
        'code': 200,
        'status': 'success',
        'data': {}
    }

    for node in nodes:
        # Read parameters or use defaults
        try:
            hide = device_options.getboolean(node, 'hide')
            continue
        except:
            hide = False

        try:
            label = device_options.get(node, 'label')
        except:
            label = node.lower()

        try:
            left = device_options.get(node, 'left')
        except:
            left = random.randint(0, 10) * 10

        try:
            top = device_options.get(node, 'top')
        except:
            top = random.randint(0, 10) * 10

        try:
            icon = device_options.get(node, 'icon')
        except:
            icon = 'generic.png'

        response['data'][node] = {
            'icon': icon,
            'id': node,
            'label': label,
            'left': left,
            'top': top
        }
    return flask.jsonify(response), response['code']

# curl -s -D- -X PUT -d '{"left": 181, "top": 818"}' -H 'Content-type: application/json' http://127.0.0.1:5000/api/nodes/nodeid
@app.route('/api/nodes/<id>', methods = ['PUT'])
def putNode(id):
    if not device_options.has_section(id):
        device_options.add_section(id)
    data = flask.request.get_json(silent = True)
    if not data:
        flask.abort(400)
    if not 'left' in data.keys() and not 'top' in data.keys():
        flask.abort(400)
    if 'left' in data.keys():
        device_options[id]['left'] = str(data['left'])
    if 'top' in data.keys():
        device_options[id]['top'] = str(data['top'])
    saveConfig()
    response = {
        'code': 200,
        'status': 'success',
    }
    return flask.jsonify(response), response['code']

# curl -s -D- -X GET http://127.0.0.1:5000/api/connections
@app.route('/api/connections', methods = ['GET'])
def getConnections():
    response = {
        'code': 200,
        'status': 'success',
        'data': links
    }
    return flask.jsonify(response), response['code']

def main():
    # Set default
    discovered_devices = {}

    # Reading options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:')
    except getopt.GetoptError as err:
        logging.error(err)
        usage()
        sys.exit(255)

    for opt, arg in opts:
        if opt == '-d':
            logging.basicConfig(level = logging.DEBUG)
        else:
            logging.error('unhandled option ({})'.format(opt))
            sys.exit(255)

    # Checking options and environment
    if not os.path.isdir(working_dir):
        logging.error('base directory does not exist ({})'.format(working_dir))
        sys.exit(255)

    # Looking for devices
    if os.path.isdir('{}/devices'.format(working_dir)):
        for dirname in os.listdir('{}/devices'.format(working_dir)):
            device_dir = '{}/devices/{}'.format(working_dir, dirname)

            # Setting device name
            fqdn = dirname.lower().split('.')[0]

            # Reading CDP neighbors
            try:
                cdp_neighbors = json.load(open('{}/cdp_neighbors.json'.format(device_dir)))
            except FileNotFoundError:
                logging.warning('missing CDP neighbors for device ({})'.format(dirname))
                cdp_neighbors = {}
            except:
                logging.warning('cannot read CDP neighbors for device ({})'.format(dirname))
                cdp_neighbors = {}

            # Saving data
            discovered_devices.setdefault(fqdn, {})
            discovered_devices[fqdn] = {
                'neighbors': cdp_neighbors
            }

    # For each device
    for device_name, device in discovered_devices.items():
        if device['neighbors']:
            # For each interface where a neighbor exists
            for device_if_name, neighbors in device['neighbors'].items():
                # For each neighbor
                for neighbor in neighbors:
                    remote_device_name = neighbor['remote_system_name'].lower().split('.')[0]
                    remote_if_name = neighbor['remote_port']
                    remote_platform = neighbor['remote_system_description']
                    should_save = False
                    if not device_options.has_section(remote_device_name):
                        device_options.add_section(remote_device_name)
                        should_save = True
                    try:
                        icon = device_options.get(remote_device_name, 'icon')
                    except:
                        if remote_platform.startswith('AIR-WLC'): icon = 'wifi_controller.png'
                        elif remote_platform.startswith('AIR-CT55'): icon = 'wifi_controller.png'
                        elif remote_platform.startswith('Cisco 18'): icon = 'router.png'
                        elif remote_platform.startswith('cisco 26'): icon = 'router.png'
                        elif remote_platform.startswith('Cisco 38'): icon = 'router.png'
                        elif remote_platform.startswith('cisco AIR-CAP'): icon = 'wifi_access_point_dual_band.png'
                        elif remote_platform.startswith('cisco AIR-LAP'): icon = 'wifi_access_point_dual_band.png'
                        elif remote_platform.startswith('Cisco IP Phone'): icon = 'phone_ip.png'
                        elif remote_platform.startswith('Polycom SoundPoint IP'): icon = 'phone_ip.png'
                        elif remote_platform.startswith('cisco WS-C29'): icon = 'switch_l2.png'
                        elif remote_platform.startswith('cisco WS-CB'): icon = 'switch_l2.png'
                        elif remote_platform.startswith('cisco WS-C35'): icon = 'switch_l3.png'
                        elif remote_platform.startswith('cisco WS-C36'): icon = 'switch_l3.png'
                        elif remote_platform.startswith('cisco WS-C37'): icon = 'switch_l3.png'
                        elif remote_platform.startswith('cisco WS-C38'): icon = 'switch_l3.png'
                        elif remote_platform.startswith('cisco WS-C45'): icon = 'switch_l3.png'
                        elif remote_platform.startswith('CTS-CODEC-MX300'): icon = 'vcf_500.png'
                        elif remote_platform.startswith('CTS-CODEC-MX700/MX800'): icon = 'vcf_1000.png'
                        elif remote_platform.startswith('DS-C9148'): icon = 'mds_fabric_a.png'
                        elif remote_platform.startswith('DS-C9513'): icon = 'mds_fabric_a.png'
                        elif remote_platform.startswith('FAS'): icon = 'storage_nfs.png'
                        elif remote_platform.startswith('N10-S6100'): icon = 'nexus_6000.png'
                        elif remote_platform.startswith('N3K-'): icon = 'nexus_3000.png'
                        elif remote_platform.startswith('N5K-'): icon = 'nexus_5000.png'
                        elif remote_platform.startswith('N7K-'): icon = 'nexus_7000.png'
                        elif remote_platform.startswith('N77-'): icon = 'nexus_7000.png'
                        elif remote_platform.startswith('N9K-'): icon = 'nexus_9300_aci_mode.png'
                        elif remote_platform.startswith('UCS-FI-'): icon = 'nexus_6000.png'
                        elif remote_platform.startswith('VMware ESX'): icon = 'server.png'
                        elif remote_platform == 'Linux Unix': icon = 'router.png'
                        elif remote_platform.startswith('Cisco IOSv'): icon = 'switch_l3.png'
                        else: icon = 'generic.png'
                        device_options.set(remote_device_name, 'icon', icon)
                    if should_save:
                        saveConfig()
                    if device_name > remote_device_name:
                        source = remote_device_name
                        source_if = remote_if_name
                        destination = device_name
                        destination_if = device_if_name
                    else:
                        source = device_name
                        source_if = device_if_name
                        destination = remote_device_name
                        destination_if = remote_if_name
                    link = {
                        'source': source,
                        'source_if': source_if,
                        'destination': destination,
                        'destination_if': destination_if
                    }

                    if not link in links:
                        links.append(link)

if __name__ == "__main__":
    main()
    app.run(host = '0.0.0.0', port = 5000, extra_files = [devices_file, 'devices/*/cdp_neighbors.json', 'templates/template.html'], debug = True)
    sys.exit(0)
