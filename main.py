import logging
import os
import sys

from models.services import Vpws, Vpls, Vlan, BsoBb, Trs
from models.endpoints import Extreme, Juniper

from pprint import pprint

from utils import yml_load, j2_render

# Create and configure the logger object

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)  # Overall minimum logging level

stream_handler = logging.StreamHandler()  # Configure the logging messages displayed in the Terminal
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)  # Minimum logging level for the StreamHandler

file_handler = logging.FileHandler('info.log')  # Configure the logging messages written to a file
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)  # Minimum logging level for the FileHandler

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

DIR = os.path.dirname(os.path.realpath(__file__)) + '/'
TEMPLATE = DIR + 'templates/main.j2'

if __name__ == '__main__':

    config = yml_load('conf.yml')

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

        print("\n########################\n## Service: v{}-{} ##\n".format(service_obj.vlan, data['customer_name']))
        data = data | service_obj.to_dict()

        for endpoint in service['endpoints']:

            if endpoint['device'].startswith("sdx") or endpoint['device'].startswith("sds"):
                endpoint_obj = Extreme(endpoint, service_obj.all_peers, service_obj.service_type)
            elif endpoint['device'].startswith("icr"):
                endpoint_obj = Juniper(endpoint, service_obj.all_peers, service_obj.service_type)

            pprint(endpoint_obj.to_dict())
            data = data | endpoint_obj.to_dict()
            print(j2_render(TEMPLATE, data))



# pprint(service_obj.__dict__)

        # for obj in endpoint_list:
        #     temp_dict = dict(host_dict)
        #     del temp_dict[obj.device]
        #     obj.peer_ip = list(temp_dict.values())
        #     obj.device_ip = host_dict[obj.device]
        #     template = set_template(obj.device)
        #     print(template.render(obj.__dict__))


