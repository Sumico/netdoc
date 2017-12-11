#!/usr/bin/env python3.5

import io, re

class FilterModule(object):
    def filters(self):
        return {
            'ios_domainname_filter': self.ios_domainname_filter,
            'ios_cdp_filter': self.ios_cdp_filter
        }
 
    def ios_domainname_filter(self, cdp_hosts_output):
        domainname = re.findall(r"Default domain is (.+)", cdp_hosts_output)[0]
        return domainname

    def ios_cdp_filter(self, cdp_detail_output):
        cdp = {}
        cdp_detail = re.split(r"^------------------.*$", cdp_detail_output, flags=re.M)[1:]

        for cdp_entry in cdp_detail:
            cdp_fields = self._cdp_detail_parser(cdp_entry)
            # Convert any 'not advertised' to 'N/A'
            for field in cdp_fields:
                for i, value in enumerate(field):
                    if 'not advertised' in value:
                        field[i] = 'N/A'
            number_entries = len(cdp_fields[0])

            # re.findall will return a list. Make sure same number of entries always returned.
            for test_list in cdp_fields:
                if len(test_list) != number_entries:
                    raise ValueError("Failure processing show cdp neighbors detail")

            # Standardize the fields
            local_intf, port_id, port_description, chassis_id, system_name, system_description, \
                system_capabilities, enabled_capabilities, remote_address = cdp_fields
            standardized_fields = zip(local_intf, port_id, port_description, chassis_id, \
                                      system_name, system_description, system_capabilities, \
                                      enabled_capabilities, remote_address)

            for entry in standardized_fields:
                local_intf, remote_port_id, remote_port_description, remote_chassis_id, \
                    remote_system_name, remote_system_description, remote_system_capab, \
                    remote_enabled_capab, remote_mgmt_address = entry
            #if local_intf:
                #local_intf = canonical_interface_name(local_intf)

            cdp.setdefault(local_intf, [])
            cdp[local_intf].append({
                'parent_interface': u'N/A',
                'remote_port': remote_port_id,
                'remote_port_description': remote_port_description,
                'remote_chassis_id': remote_chassis_id,
                'remote_system_name': remote_system_name,
                'remote_system_description': remote_system_description,
                'remote_system_capab': remote_system_capab,
                'remote_system_enable_capab': remote_enabled_capab})

        return cdp

    def _cdp_detail_parser(self, output):
        # Cisco generally use : for string divider, but sometimes has ' - '
        local_intf = re.findall(r"Interface\s*?[:-]\s+(.+),.*", output)
        port_id = re.findall(r".*Port ID \(outgoing port\)\s*?[:-]\s+(.+)", output)
        port_description = re.findall(r".*Port ID \(outgoing port\)\s*?[:-]\s+(.+)", output)
        chassis_id = ["not advertised"]
        system_name = re.findall(r"Device ID\s*?[:-]\s+([^(\n]+)", output)
        system_description = re.findall(r"Platform\s*?[:-]\s+([^,]+)\s*.*", output)
        system_capabilities = re.findall(r".*Capabilities\s*?[:-]\s+(.+)", output)
        if system_capabilities:
            system_capabilities[0] = system_capabilities[0].replace("Router", "R")
            system_capabilities[0] = system_capabilities[0].replace("Trans Bridge", "T")
            system_capabilities[0] = system_capabilities[0].replace("Trans-Bridge", "T")
            system_capabilities[0] = system_capabilities[0].replace("Source Route Bridge", "B")
            system_capabilities[0] = system_capabilities[0].replace("Source-Route-Bridge", "B")
            system_capabilities[0] = system_capabilities[0].replace("Switch", "S")
            system_capabilities[0] = system_capabilities[0].replace("Host", "H")
            system_capabilities[0] = system_capabilities[0].replace("IGMP", "I")
            system_capabilities[0] = system_capabilities[0].replace("Repeater", "r")
            system_capabilities[0] = system_capabilities[0].replace("Phone", "P")
            system_capabilities[0] = system_capabilities[0].replace("Remote", "D")
            system_capabilities[0] = system_capabilities[0].replace("CVTA", "C")
            system_capabilities[0] = system_capabilities[0].replace("Two-port Mac Relay", "M")
            system_capabilities[0] = system_capabilities[0].strip()
        else:
            system_capabilities = ["not advertised"]
        remote_address = re.findall(r"Management address\(es\)\s*[:-]\s*(\n.+)", output)
        # get management addresses and fall back to entry addresses
        new_remote_address = []
        for val in remote_address:
            val = val.strip()
            pattern = r'\s*IP address\s*[:-]\s+(.+)'
            match = re.search(pattern, val)
            if match:
                new_remote_address.append(match.group(1))
            else:
                new_remote_address.append(val)
        if not new_remote_address:
            remote_address = re.findall(r"Entry address\(es\)\s*[:-]\s*(\n.+)", output)
            for val in remote_address:
                val = val.strip()
                pattern = r'\s*IP address\s*[:-]\s+(.+)'
                match = re.search(pattern, val)
                if match:
                    new_remote_address.append(match.group(1))
                else:
                    new_remote_address.append(val)
        remote_address = new_remote_address
        return [local_intf, port_id, port_description, chassis_id, system_name, system_description,
                system_capabilities, system_capabilities, remote_address]

