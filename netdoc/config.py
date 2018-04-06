#!/usr/bin/env python3
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20170430'

import configparser, logging, os, random, sys

def loadConfig(app_root):
    config_file = '{}/../working/{}/config.ini'.format(app_root, os.environ.get('NETDOC_FOLDER', 'default'))
    try:
        config_dir = os.path.dirname(config_file)
        os.makedirs(config_dir, mode = 0o755, exist_ok = True)
    except Exception as err:
        logging.error('cannot create ""{}"" folder'.format(config_dir))
        logging.error(err)
        sys.exit(1)

    if not os.path.isfile(config_file):
        # File is not present
        try:
            # Write an empty file
            open(config_file, 'a').close()
        except Exception as err:
            # Cannot write configuration file
            logging.error('cannot create configuration file "{}"'.format(config_file))
            logging.error(err)
            sys.exit(1)

    # Loading Config
    config = configparser.ConfigParser()
    need_to_save = False
    try:
        # Loading configuration file
        config.read(config_file)
    except Exception as err:
        # Cannot load configuration file
        logging.error('cannot load configuration file "{}"'.format(config_file))
        logging.error(err)
        sys.exit(1)

    # Setting default values
    if not config.has_section('app'):
        config.add_section('app')
        need_to_save = True
    if not config.has_option('app', 'api_key'):
        api_key = os.environ.get('API')
        if not api_key:
            api_key = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for c in range(40))
        config['app']['api_key'] = api_key
        need_to_save = True
    if not config.has_option('app', 'database_uri'):
        config['app']['database_uri'] = 'sqlite:///{}/database.sdb'.format(os.path.dirname(config_file))
        #config['app']['database_uri'] = 'mysql://root:eve-ng@192.168.102.130/netdoc'.format(os.path.dirname(config_file))
        need_to_save = True

    if need_to_save:
        # Need to update configuration file
        try:
            with open(config_file, 'w') as config_fd:
                config.write(config_fd)
                config_fd.close()
        except Exception as err:
            # Cannot update configuration file
            logging.error('cannot update configuration file "{}"'.format(config_file))
            logging.error(err)
            sys.exit(1)

    return config._sections
