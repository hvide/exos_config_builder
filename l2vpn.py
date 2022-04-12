#!/usr/local/bin/python3
import socket
import argparse
import os
import sys
from utils import yml_load, jinja2_load


class Endpoint:
    def __init__(self, customer_name, service_name, service_type, ether_type, vlan, device, dot1q, ports, ip_address_v4=None, uplink=None):
        self.customer_name = customer_name
        self.service_name = service_name
        self.service_type = service_type
        self.ether_type = ether_type
        self.vlan = vlan
        self.device = device
        self.dot1q = dot1q
        self.ports = ports
        self.ip_address_v4 = ip_address_v4
        self.uplink = uplink

    def validate_dot1q(self):
        try:
            """Check that the port is either tagged or untagged."""
            if self.dot1q != 'tagged' and \
                    self.dot1q != 'untagged':
                raise IOError('The "dot1q" attribute for %s was set to %s.\n'
                              'It needs to be either "tagged" or "untagged".' % (self.device, self.dot1q))
        except OSError as e:
            print(e)
            sys.exit(1)
        return True


def validate_vpws(service_type, endpoints_number):
        try:
            """Check that there are only two enpoints per service/vlan."""
            if service_type == 'vpws':
                if endpoints_number != 2:
                    raise IOError("Only two endpoints need to be defined for a VPWS service.")
        except OSError as e:
            print(e)
            sys.exit(1)
        return True


def validate_vlan(vlan):
    try:
        """Check that the vlan ID is valid."""
        if not 0 < int(vlan) < 4096:
            raise IOError('The vlan ID needs to be within 0 and 4095.')
    except OSError as e:
        print(e)
        sys.exit(1)
    return True


def ip(host):
    domain = '.as43531.net'
    try:
        return socket.gethostbyname(host + domain)
    except socket.gaierror as e:
        print('%s\nThe hostname %s could not be resolved.' % (str(e), host))
        sys.exit(1)


def set_template(device_name):
    if device_name.startswith('icr') or device_name.startswith('r'):
        return jinja2_load(JUNIPER_DIA_TEMPLATE)
    else:
        return jinja2_load(EXOS_TEMPLATE)


DIR = os.path.dirname(os.path.realpath(__file__)) + '/'
EXOS_TEMPLATE = DIR + 'templates/l2vpn.j2'
JUNIPER_DIA_TEMPLATE = DIR + 'templates/juniper_DIA.j2'
EXAMPLE = DIR + 'example.txt'
EMPTY_YML_TEMPLATE = DIR + 'empty_template.yml'

parser = argparse.ArgumentParser()
parser.add_argument('-c', type=str, action="store", dest="config", required=False, help="Path to .yml file")
parser.add_argument('-t', action="store_true", dest="empty_template", required=False, help="Print empty template")
parser.add_argument('-e', action="store_true", dest="example", required=False, help="Print example")


def main():
    args = parser.parse_args()
    if args.example:
        with open(EXAMPLE, 'r') as f:
            lines = f.readlines()
            for line in lines:
                print(line.rstrip())
            sys.exit(0)

    if args.empty_template:
        with open(EMPTY_YML_TEMPLATE, 'r') as f:
            lines = f.readlines()
            for line in lines:
                print(line.rstrip())
            sys.exit(0)

    yml_file: object = args.config
    if not yml_file:
        yml_file = 'conf.yml'
    data = yml_load(yml_file)
#    template = jinja2_load(EXOS_TEMPLATE)
    for service in data['services']:

        validate_vlan(service['vlan'])
        validate_vpws(service['service_type'], len(service['endpoints']))

        endpoint_list = []
        host_dict = {}

        for endpoint in service['endpoints']:
            # Set Template base on device

            endpoint_obj = Endpoint(
                    data['customer_name'],
                    service['service_name'],
                    service['service_type'],
                    service['ether_type'],
                    service['vlan'],
                    endpoint['device'],
                    endpoint['dot1q'],
                    endpoint['ports'],
                )

            if "uplink" in endpoint.keys():
                endpoint_obj.uplink = endpoint['uplink']
            endpoint_obj.validate_dot1q()
            if "ip_address_v4" in endpoint.keys():
                endpoint_obj.ip_address_v4 = endpoint['ip_address_v4']

            host_dict['%s' % endpoint_obj.device] = '%s' % ip(endpoint_obj.device)
            endpoint_list.append(endpoint_obj)

        service_description = '## Service: w%s-%s ##' % (str(service['vlan']), data['customer_name'])
        print(''.ljust(len(service_description), '#'))
        print(service_description)
        print('')

        for obj in endpoint_list:
            temp_dict = dict(host_dict)
            del temp_dict[obj.device]
            obj.peer_ip = list(temp_dict.values())
            obj.device_ip = host_dict[obj.device]
            template = set_template(obj.device)
            print(template.render(obj.__dict__))


if __name__ == '__main__':
    main()
