#!/usr/bin/env python

import paramiko

host = '192.168.0.220'
user = 'ubnt'
password = 'ubnt'
port = 22


class SshConnection(object):
    def __init__(self, host, user, password, port=22):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.client = None

    def __enter__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.host, username=self.user, password=self.password, port=self.port)
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.client.close()
        except:
            pass


def get_val(s):
    try:
        if '.' in s:
            return float(s.strip())
        else:
            return int(s.strip())
    except:
        return s.strip()


def get_data(client, key):
    stdin, stdout, stderr = client.exec_command('cat /proc/power/%s' % key)
    data = stdout.read().decode("utf-8")
    return get_val(data)


def switch(host, user, password, n, st):
    with SshConnection(host, user, password) as client:
        val = int(str(st).lower() in ('on', '1'))
        client.exec_command('echo "%s" > /proc/power/relay%s' % (val, n))


def get_all(host, user, password):
    with SshConnection(host, user, password) as client:
        data = {}
        for i in ('1',):
            d = {}
            for k, nk in (('v_rms', 'voltage'), ('i_rms', 'current'), ('pf', 'pf'), ('active_pwr', 'power'),
                          ('energy_sum', 'energy_sum'), ('relay', 'relay')):
                d[nk] = get_data(client, '%s%s' % (k, i))
            data[i] = d
        return data
