import logging
import sys
import typing

from functools import reduce

from utils import resolve

logger = logging.getLogger()


class Endpoint:
    def __init__(self, endpoint: typing.Dict, all_peers: typing.List, service_type):

        self.device: str = endpoint['device']
        self.ip: str = resolve(self.device)
        self.service_type = service_type
        self.ports: typing.List = endpoint['ports']
        self.all_ports: typing.List = reduce(lambda x, y: x+y, [x['name'] for x in self.ports])

        self.peers_ip = []
        for position, peer in enumerate(all_peers):
            if peer == self.device:
                if position == 0 or position == len(all_peers) - 1:
                    self.is_pe = True
                else:
                    self.is_pe = False
            else:
                self.peers_ip.append(peer)

    def __repr__(self):
        return self.device


class Extreme(Endpoint):
    def __init__(self, endpoint, all_peers, service_type):
        super(Extreme, self).__init__(endpoint, all_peers, service_type)
        self.vendor = "extreme"
        self.ether_type: str = endpoint['ether_type']

        # Check that there is only one port per endpoint in VPWS configuration
        if service_type == 'vpws' and len(self.ports) != 1:
            logger.error('Error: VPWS service only allow for 1 port per endpoint {} have {}.'.format(
                self, len(self.ports)))
            sys.exit(1)

    def to_dict(self) -> typing.Dict:
        return {
            'device': self.device,
            'device_ip': self.ip,
            'ether_type': self.ether_type,
            'ports': self.ports,
            'all_ports': self.all_ports,
            'peers_ip': self.peers_ip,
            'is_pe': self.is_pe,
            'vendor': self.vendor
        }


class Juniper(Endpoint):
    def __init__(self, endpoint, all_peers, service_type):
        super(Juniper, self).__init__(endpoint, all_peers, service_type)
        self.vendor = "juniper"
        self.ip_address_v4 = endpoint['ip_address_v4']
        self.ip_address_v6 = endpoint['ip_address_v6']
        self.peers_ip: typing.List = [resolve(x) for x in all_peers if x != self.device]
        self.service_type = service_type
        if self.service_type == "trs":
            self.asn = endpoint['bgp']['asn']
            self.group = endpoint['bgp']['group']
            self.prefix_limit_v4 = endpoint['bgp']['v4']['prefix_limit']
            self.prefix_list_v4 = endpoint['bgp']['v4']['prefix_list']
            self.prefix_limit_v6 = endpoint['bgp']['v6']['prefix_limit']
            self.prefix_list_v6 = endpoint['bgp']['v6']['prefix_list']

    def to_dict(self) -> typing.Dict:
        if self.service_type == "trs":
            return {
                'device': self.device,
                'device_ip': self.ip,
                'service_type': self.service_type,
                'ports': self.ports,
                'peers_ip': self.peers_ip,
                'vendor': self.vendor,
                'ip_address_v4': self.ip_address_v4,
                'ip_address_v6': self.ip_address_v6,
                'asn': self.asn,
                'group': self.group,
                'prefix_limit_v4': self.prefix_limit_v4,
                'prefix_list_v4': self.prefix_list_v4,
                'prefix_limit_v6': self.prefix_limit_v6,
                'prefix_list_v6': self.prefix_list_v6
            }
        else:
            return {
                'device': self.device,
                'device_ip': self.ip,
                'service_type': self.service_type,
                'ports': self.ports,
                'peers_ip': self.peers_ip,
                'vendor': self.vendor,
                'ip_address_v4': self.ip_address_v4
            }
