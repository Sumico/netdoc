#!/usr/bin/env python3
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://www.gnu.org/licenses/gpl.html'
__revision__ = '20170329'

import getopt, json, logging, os, sys
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager

def usage():
    print('Usage: {} [OPTIONS]'.format(sys.argv[0]))
    print('  -i STRING  inventory file')
    print('  -d         enable debug')

def checkOpts():
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
            working_dir = '{}/working/default'.format(os.path.dirname(os.path.abspath(arg)))
        else:
            logging.error('unhandled option ({})'.format(opt))
            usage()
            sys.exit(255)

    # Checking options and environment
    if not inventory_file:
        logging.error('inventory file not specified')
        sys.exit(255)
    if not os.path.isfile(inventory_file):
        logging.error('inventory file "{}" does not exist'.format(inventory_file))
        sys.exit(255)

    # Loading Ansible inventory
    ansible_loader = DataLoader()
    try:
        ansible_inventory = InventoryManager(loader = ansible_loader, sources = inventory_file)
    except Exception as err:
        logging.error('cannot read inventory file "{}"'.format(inventory_file))
        logging.error(err)
        sys.exit(255)
    variable_manager = VariableManager(loader = ansible_loader, inventory = ansible_inventory)
    return ansible_inventory.get_hosts(), working_dir

def writeDeviceInfo(device_info, path):
    for key, value in device_info.items():
        try:
            os.makedirs(path, exist_ok = True)
        except Exception as err:
            logging.error('cannot create directory "{}"'.format(path))
            logging.error(err)
            sys.exit(1)
        try:
            output = open('{}/{}.json'.format(path, key), 'w+')
            output.write(json.dumps(value))
            output.close()
        except Exception as err:
            logging.error('cannot write "{}/{}.json"'.format(path, key))
            logging.error(err)
            sys.exit(1)
    return True
