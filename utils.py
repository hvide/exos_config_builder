import logging
import typing
import sys
import yaml
import jinja2
import socket

logger = logging.getLogger()


# def add_log(msg: str):
#     """
#     Add a log to the list so that it can be picked by the update_ui() method of the root component.
#     :param msg:
#     :return:
#     """
#
#     logger.info("%s", msg)
#     # logs.append({"log": msg, "displayed": False})


def yml_load(x):
    try:
        with open(x) as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError as e:
        print(str(e) + '\nCreate a "vpws.yml" file in the current working directoy.'
                       '\nOr specify the path to your .yml file with the "-c" option')
        sys.exit(0)


def jinja2_load(filename: str):
    with open(filename) as t:
        # return jinja2.Template(t.read())
        return jinja2.Environment(loader=jinja2.FileSystemLoader('./templates/')).from_string(t.read())


def j2_render(template: str, data: typing.Dict):
    t = jinja2_load(template)
    return t.render(data)


def resolve(hostname):
    domain = '.as43531.net'
    try:
        return socket.gethostbyname(hostname + domain)
    except socket.gaierror as e:
        # print('%s\nThe hostname %s could not be resolved.' % (str(e), hostname))
        add_log('%s\nThe hostname %s could not be resolved.' % (str(e), hostname))
        sys.exit(1)
