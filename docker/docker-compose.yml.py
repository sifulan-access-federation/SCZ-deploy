#!/usr/bin/env python3

import yaml
from typing import Dict

# this generates a docker-compose.yml file for SCZ

# these are the Docker containers that need to be spun up
hosts = {
    'ldap':     20,
    'proxy':    22,
    'meta':     23,
    'lb':       24,
    'client':   25,
    'sandbox1': 26,
    'sbs':      27,
    'db':       28
}

# these are the hostnames of virtual hosts on the loadbalancer
logical_hosts = [
    'proxy',    'mdq',         'cm',        'comanage',
    'ldap',     'meta',        'oidc-test', 'sp-test',
    'idp-test', 'google-test', 'sbs',       'sandbox1',
]

subnet = '172.20.1'
domain = 'aseanfilm.org'


# generates config for a single host
def host_config(num: int, name: str) -> Dict:
    data = dict()
    data['image'       ] = 'scz-base'
    data['hostname'    ] =  name
    data['volumes'     ] = [ './ansible_key.pub:/tmp/authorized_keys', '/sys/fs/cgroup:/sys/fs/cgroup:ro' ]
    data['tmpfs'       ] = [ '/run', '/run/lock', '/tmp' ]
    data['privileged'  ] = False
    data['security_opt'] = [ 'seccomp:unconfined', 'apparmor:unconfined' ]
    data['cap_add'     ] = [ 'SYS_ADMIN', 'SYS_PTRACE' ]
    data['networks'    ] = {
        'scznet': {
            'ipv4_address': f'{subnet}.{num}',
            'aliases':      [ f'{name}.scz.{domain}' ]
        }
    }
    data['extra_hosts'] = [ f'{h}.{domain}:{subnet}.{hosts["lb"]}' for h in logical_hosts ]

    return data

# generate the full docker-compose.yml file
compose = dict()
compose['version' ] = '2'
compose['networks'] = {
    'scznet': {
        'driver': 'bridge',
        'ipam': {
            'driver': 'default',
            'config': [ { 'subnet': f'{subnet}.0/24', 'gateway': f'{subnet}.1' } ]
        }
    }
}
compose['services'] = { h: host_config(ip, h) for h, ip in hosts.items() }

# dump the yaml
print("---")
print("# This file has been automatically generated.  DO NOT EDIT, CHANGES WILL BE LOST!")
print("# yamllint disable")
print(yaml.dump(compose))
