import logging
import sys

import typing

logger = logging.getLogger()


class Service:
    def __init__(self, service: typing.Dict):

        self.service_name = service['service_name']
        self.service_type = service['service_type']

        if 1 <= service['vlan'] <= 4095:
            self.vlan = service['vlan']
        else:
            logger.error(
                "VLAN {} is not in range 1 to 4095".format(service['vlan']))
            sys.exit(1)

        self.all_peers = [peer['device'] for peer in service['endpoints']]

    def to_dict(self) -> typing.Dict:
        return {
            'service_name': self.service_name,
            'service_type': self.service_type,
            'vlan': self.vlan
        }

    def __repr__(self):
        return self.service_name


class Vpws(Service):
    def __init__(self, service):
        super(Vpws, self).__init__(service)

        if len(self.all_peers) != 2:
            logger.error('Error: VPWS service only allow for 2 endpoints. {} have {}.'.format(
                self, len(self.all_peers)))
            sys.exit(1)


class Vpls(Service):
    def __init__(self, service):
        super(Vpls, self).__init__(service)


class Vlan(Service):
    def __init__(self, service):
        super(Vlan, self).__init__(service)


class BsoBb(Service):
    def __init__(self, service):
        super(BsoBb, self).__init__(service)


class Trs(Service):
    def __init__(self, service):
        super(Trs, self).__init__(service)


class Dia(Service):
    def __init__(self, service):
        super(Dia, self).__init__(service)


class Service_c2c:
    def __init__(self, service: typing.Dict):

        self.service_name = service['service_name']
        self.service_type = service['service_type']
        self.so = service['so']
        self.all_peers = [peer['device'] for peer in service['endpoints']]

    def to_dict(self) -> typing.Dict:
        return {
            'service_name': self.service_name,
            'service_type': self.service_type,
            'so': self.so,
        }

    def __repr__(self):
        return self.service_name
