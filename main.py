#!/usr/bin/env python3
import logging
import os
import sys
import argparse
import typing
import jinja2
from tabulate import tabulate

from models.services import Vpws, Vpls, Vlan, BsoBb, Trs, Dia, Service_c2c
from models.endpoints import Extreme, Juniper, Juniper_c2c

from pprint import pprint

from utils import yml_load, j2_render

# Create and configure the logger object

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)  # Overall minimum logging level

# Configure the logging messages displayed in the Terminal
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
# Minimum logging level for the StreamHandler
stream_handler.setLevel(logging.INFO)

# Configure the logging messages written to a file
file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
# Minimum logging level for the FileHandler
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

DIR = os.path.dirname(os.path.realpath(__file__)) + '/'
TEMPLATE = DIR + 'templates/jinja/main.j2'
EMPTY_YML_TEMPLATE = DIR + 'templates/yaml/'
EXAMPLE = DIR + 'example.txt'


def report(datas: typing.Dict):

    table = []
    for data in datas['services']:
        row = []
        row.append(data['service_name'])
        row.append(data['vlan'])

        for endpoint in data['endpoints']:
            row.append(endpoint['device'])
            row.append(endpoint['ports'][0]['name'][0])

        table.append(row)

    return table


empty_template = {
    'bb': 'bso-bb.yml',
    'trs': 'transit.yml',
    'dia': 'dia.yml',
    'vlan': 'vlan.yml',
    'vpls': 'vpls.yml',
    'vpws': 'vpws.yml',
    'c2c': 'c2c.yml',
}

parser = argparse.ArgumentParser()
parser.add_argument('-c', type=str, action="store",
                    dest="config", required=False, help="Path to .yml file")
parser.add_argument('-t', type=str, action="store", dest="template", required=False,
                    help=f"Can be one of the following: {list(empty_template.keys())}.")
# parser.add_argument('-e', action="store_true", dest="example",
#                     required=False, help="Print example")
parser.add_argument('-v', action="store_true", dest="verbose",
                    required=False, help="Verbose output")


if __name__ == '__main__':

    args = parser.parse_args()
    # if args.example:
    #     with open(EXAMPLE, 'r') as f:
    #         lines = f.readlines()
    #         for line in lines:
    #             print(line.rstrip())
    #         sys.exit(0)

    if args.template in empty_template:
        with open(EMPTY_YML_TEMPLATE + empty_template[args.template], 'r') as f:
            lines = f.readlines()
            for line in lines:
                print(line.rstrip())
            sys.exit(0)

    if args.config:
        yml_file: object = args.config
        if not yml_file:
            yml_file = 'conf.yml'
        config = yml_load(yml_file)

        data = {'customer_name': config['customer_name']}

        for service in config['services']:

            if service['service_type'] == 'vpws':
                service_obj = Vpws(service)
            elif service['service_type'] == "vpls":
                service_obj = Vpls(service)
            elif service['service_type'] == "vlan":
                service_obj = Vlan(service)
            elif service['service_type'] == "bso-bb":
                service_obj = BsoBb(service)
            elif service['service_type'] == "trs":
                service_obj = Trs(service)
            elif service['service_type'] == "dia":
                service_obj = Dia(service)
            elif service['service_type'] == "c2c":
                data['firewall_conf'] = config['firewall_conf']
                data['policy_conf'] = config['policy_conf']
                service_obj = Service_c2c(service)

            if service['service_type'] != "c2c":
                print("\n########################\n## Service: v{}-{} ##\n".format(
                    service_obj.vlan, data['customer_name']))

            data = data | service_obj.to_dict()
            # pprint(data)
            for endpoint in service['endpoints']:

                if endpoint['device'].startswith("sdx") or endpoint['device'].startswith("sds"):
                    endpoint_obj = Extreme(
                        endpoint, service_obj.all_peers, service_obj.service_type)
                elif service['service_type'] == "c2c":
                    endpoint_obj = Juniper_c2c(
                        endpoint, service_obj.all_peers, service_obj.service_type, data['customer_name'])
                elif endpoint['device'].startswith("icr"):
                    endpoint_obj = Juniper(
                        endpoint, service_obj.all_peers, service_obj.service_type, data['customer_name'])

                data = data | endpoint_obj.to_dict()

                if args.verbose:
                    pprint(data)
                print('')
                print(j2_render(TEMPLATE, data))

        # REPORT
        # print('')
        # headers = ['Service ID', 'Vlan', 'A-end',
        #            'A-end port', 'Z-end', 'Z-end port']
        # table = report(config)
        # print(tabulate(table, headers=headers))
