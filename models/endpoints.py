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
        self.all_ports: typing.List = reduce(
            lambda x, y: x+y, [x['name'] for x in self.ports])

        self.peers_ip = []
        for position, peer in enumerate(all_peers):
            if peer == self.device:
                if position == 0 or position == len(all_peers) - 1:
                    self.is_pe = True
                else:
                    self.is_pe = False
            else:
                self.peers_ip.append(resolve(peer))

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
    def __init__(self, endpoint, all_peers, service_type, customer_name):
        super(Juniper, self).__init__(endpoint, all_peers, service_type)
        self.vendor = "juniper"
        self.ip_address_v4 = endpoint['ip_address_v4']
        self.peers_ip: typing.List = [
            resolve(x) for x in all_peers if x != self.device]
        self.service_type = service_type
        self.customer_name = customer_name
        self.routing_instance = endpoint['routing_instance']

        if self.service_type == "trs":
            self.asn = endpoint['bgp']['asn']
            self.group = endpoint['bgp']['group']
            self.export_policy = endpoint['bgp']['export_policy']
            self.prefix_limit_v4 = endpoint['bgp']['v4']['prefix_limit']
            self.prefix_list_v4 = endpoint['bgp']['v4']['prefix_list']

            def _neighbor_v4(prefix):
                ip, cidr = prefix.split('/')
                a, b, c, d = ip.split('.')
                return "{}.{}.{}.{}".format(a, b, c, int(d) + 1)

            def _neighbor_v6(prefix):
                ip, cidr = prefix.split('/')
                return "{}{}".format(ip, 1)

            self.bgp_neighbor_v4 = _neighbor_v4(self.ip_address_v4)

            if 'ip_address_v6' in endpoint:
                self.ip_address_v6 = endpoint['ip_address_v6']
                self.prefix_limit_v6 = endpoint['bgp']['v6']['prefix_limit']
                self.prefix_list_v6 = endpoint['bgp']['v6']['prefix_list']
                self.bgp_neighbor_v6 = _neighbor_v6(self.ip_address_v6)
            else:
                self.ip_address_v6 = None
                self.prefix_limit_v6 = None
                self.prefix_list_v6 = None
                self.bgp_neighbor_v6 = None

    def to_dict(self) -> typing.Dict:
        if self.service_type == "trs":
            return {
                'customer_name': self.customer_name,
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
                'export_policy': self.export_policy,
                'prefix_limit_v4': self.prefix_limit_v4,
                'prefix_list_v4': self.prefix_list_v4,
                'bgp_neighbor_v4': self.bgp_neighbor_v4,
                'prefix_limit_v6': self.prefix_limit_v6,
                'prefix_list_v6': self.prefix_list_v6,
                'bgp_neighbor_v6': self.bgp_neighbor_v6,
                'routing_instance': self.routing_instance
            }
        else:
            return {
                'device': self.device,
                'device_ip': self.ip,
                'service_type': self.service_type,
                'ports': self.ports,
                'peers_ip': self.peers_ip,
                'vendor': self.vendor,
                'ip_address_v4': self.ip_address_v4,
                'routing_instance': self.routing_instance
            }


class Juniper_c2c(Endpoint):
    def __init__(self, endpoint, all_peers, service_type, customer_name):
        super(Juniper_c2c, self).__init__(endpoint, all_peers, service_type)
        self.ip_base = '172.18.10.'
        self.last_octect = self._ip_octects(resolve(self.device))[-1]
        self.loopback: str = self.ip_base + self.last_octect
        self.routing_instance = 'LOLAC2C-' + customer_name

        self.peer_as = endpoint['bgp']['asn']
        self.group_ebgp = endpoint['cloud_type']
        self.group_ibgp = 'iBGP'
        # self.lo0 = endpoint['lo0']
        self.neighbor_ibgp = []
        self.neighbor_ebgp = []

        for port in endpoint['ports']:
            if port['type'] == 'internal':
                self.neighbor_ibgp.append(self._neighbor_v4(port['address']))
            elif port['type'] == 'cloud':
                self.neighbor_ebgp.append(self._neighbor_v4(port['address']))

    def _neighbor_v4(self, prefix):
        ip, cidr = prefix.split('/')
        a, b, c, d = ip.split('.')
        return "{}.{}.{}.{}".format(a, b, c, int(d) + 1)

    def _ip_octects(self, ip: str) -> str:
        octects = ip.split('.')
        return octects

    # def bgp_neighbor(bgp_type) -> typing.List:

    def to_dict(self) -> typing.Dict:
        return {
            'device': self.device,
            'service_type': self.service_type,
            'ports': self.ports,
            'loopback': self.loopback,
            'routing_instance': self.routing_instance,
            'peer_as': self.peer_as,
            'neighbor_ibgp': self.neighbor_ibgp,
            'neighbor_ebgp': self.neighbor_ebgp,
            'group_ebgp': self.group_ebgp.capitalize(),
            'group_ibgp': self.group_ibgp,
            # 'lo0': self.lo0,
        }
