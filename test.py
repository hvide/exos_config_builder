import unittest

from utils import yml_load
from models.services import Service
from models.endpoints import Endpoint, Extreme, Juniper

config = yml_load('conf.yml')

service = {
    'service_name': 'DIA/LON/IXR-10556',
    'service_type': 'vpws',
    'vlan': 45
}

endpoint = {
    'device': 'sdx3.thn.lon',
    'ether_type': 'vlan',
    'ports': [{'dot1q': 'tagged', 'name': [3, 4]},
              {'dot1q': 'tagged', 'name': [10]}]
}

peers = ['sdx3.thn.lon', 'sdx1.the.lon', 'sdx1.eq5.fra']


class UtilsTest(unittest.TestCase):

    def test_yml_load(self):
        self.assertIsInstance(config, dict)


class VlanTest(unittest.TestCase):

    service['vlan'] = 5000

    def test_vlan_range(self):
        with self.assertRaises(SystemExit) as cm:
            Service(service)
        self.assertEqual(cm.exception.code, 1)


class EndpointTest(unittest.TestCase):

    def test_peers_ip(self):
        ep = Extreme(endpoint, peers, 'vpls')
        self.assertNotIn(ep.device, ep.peers_ip)


class BsoBbTest(unittest.TestCase):

    peers = ['sdx3.thn.lon', 'sdx1.the.lon', 'sdx1.eq5.fra']

    def test_first_ep(self):
        endpoint['device'] = peers[0]
        ep = Extreme(endpoint, peers, 'bso-bb')
        self.assertEqual(ep.is_pe, True)

    def test_second_ep(self):
        endpoint['device'] = peers[1]
        ep = Extreme(endpoint, peers, 'bso-bb')
        self.assertEqual(ep.is_pe, False)

    def test_last_ep(self):
        endpoint['device'] = peers[-1]
        ep = Extreme(endpoint, peers, 'bso-bb')
        self.assertEqual(ep.is_pe, True)


class VpwsTest(unittest.TestCase):

    def test_vpws_port_number(self):
        # print("Testing: 'test_vpws_port_number'")
        with self.assertRaises(SystemExit) as cm:
            Extreme(endpoint, peers, 'vpws')
        self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
