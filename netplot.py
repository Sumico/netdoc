#!/usr/bin/python3

import configparser, getopt, os, sys

def shortensDivId(id):
    id = id.replace('.', '')
    id = id.replace('(', '')
    id = id.replace(')', '')
    return id

def main():
    working_dir = os.path.dirname(os.path.abspath(__file__))

    discovered_nodes_file = 'discovered_nodes.ini'
    discovered_connections_file = 'discovered_connections.ini'
    static_nodes_file = 'static_nodes.ini'
    static_connections_file = 'static_connections.ini'
    # Reading configuration files
    discovered_nodes = configparser.ConfigParser()
    discovered_nodes.read(discovered_nodes_file)
    discovered_connections = configparser.ConfigParser()
    discovered_connections.read(discovered_connections_file)
    # Remove disabled nodes
    for discovered_node in discovered_nodes.sections():
        if discovered_nodes.has_option(discovered_node, 'disabled') and discovered_nodes[discovered_node]['disabled'] == 'true':
            discovered_nodes.remove_section(discovered_node)
    # Remove disabled connections
    for discovered_connection in discovered_connections.sections():
        if discovered_connections.has_option(discovered_connection, 'disabled') and discovered_connections[discovered_connection]['disabled'] == 'true':
            discovered_connections.remove_section(discovered_connection)

    print('<!DOCTYPE html>')
    print('<html>')
    print('<head>')
    print('\t<style>')
    print('\t\t.node_container {')
    print('\t\t\tposition: absolute;')
    print('\t\t}')
    print('\t\t.node_label {')
    print('\t\t\tposition: absolute;')
    print('\t\t}')
    print('\t</style>')
    print('</head>')
    print('<body>')
    print('<div id="diagramContainer">')
    for discovered_node in discovered_nodes.sections():
        print('\t<div id="{}" class="node_container">'.format(shortensDivId(discovered_node)))
        print('\t\t<div class="node_image"><img src="images/{}"/></div>'.format(discovered_nodes[discovered_node]['image']))
        print('\t\t<div class="node_label">{}</div>'.format(discovered_node))
        print('\t</div>')
    print('</div>')
    print('<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>')
    print('<script src="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>')
    print('<script src="https://cdnjs.cloudflare.com/ajax/libs/jsPlumb/2.2.9/jsplumb.min.js"></script>')
    print('<script>')
    print('\tjsPlumb.ready(function() {')
    print('\t\tjsPlumb.importDefaults({')
    print('\t\t\tAnchor: "Continuous",')
    print('\t\t\tConnector: ["Straight"],')
    print('\t\t\tEndpoint: "Blank",')
    #print('\t\t\tPaintStyle: {lineWidth: 2, strokeStyle: "#58585a"},')
    #print('\t\t\tcssClass: "link"')
    print('\t\t});')
    print('\t\tjsPlumb.draggable($(".node_container"), {grid: [10, 10]});')
    for discovered_connection in discovered_connections.sections():
        print('\t\tjsPlumb.connect({')
        print('\t\t\tsource: "{}",'.format(shortensDivId(discovered_connections[discovered_connection]['source'])))
        print('\t\t\ttarget: "{}",'.format(shortensDivId(discovered_connections[discovered_connection]['destination'])))
        #print('\t\t\toverlays: ["{}", "{}"]'.format(discovered_connections[discovered_connection]['source_if'], discovered_connections[discovered_connection]['destination_if']))
        print('\t\t\toverlays:[[ "Label", {{label: "{}", location:0.15}}], ["Label", {{label: "{}", location:0.85}}]]'.format(
            discovered_connections[discovered_connection]['source_if'],
            discovered_connections[discovered_connection]['destination_if']
        ))
        print('\t\t});')
    print('\t});')
    print('</script>')
    print('</body>')
    print('</html>')

if __name__ == "__main__":
    main()
    sys.exit(0)

