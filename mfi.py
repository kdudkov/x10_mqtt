#!/usr/bin/env python3

import logging

import requests

log = logging.getLogger(__name__)


class Mfi(object):
    timeout = 5

    def __init__(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.password = password
        self.sessionid = '01234567890123456789012345678901'

    def login(self):
        cookies = {'AIROS_SESSIONID': self.sessionid}
        r = requests.post('http://%s/login.cgi' % self.ip, data={'username': self.user, 'password': self.password},
                          cookies=cookies, timeout=self.timeout)
        if r.status_code != 200:
            log.error('error on login: %s, %s', r.status_code, r.text[:50])
            raise Exception('login error: status code %s' % r.status.code)

    def _or_login(self, fn, *args, **kv):
        r = fn(*args, **kv)
        if r.status_code == 302:
            log.info('login to %s', self.ip)
            self.login()
            r = fn(*args, **kv)
        return r

    def state(self):
        cookies = {'AIROS_SESSIONID': self.sessionid}
        r = self._or_login(requests.get, 'http://%s/sensors' % self.ip, cookies=cookies, allow_redirects=False,
                           timeout=self.timeout)
        if r.status_code != 200:
            raise Exception('code %s' % r.status_code)
        return r.json()

    def set(self, port, **d):
        cookies = {'AIROS_SESSIONID': self.sessionid}
        r = self._or_login(requests.put, 'http://%s/sensors/%s' % (self.ip, port), cookies=cookies, data=d,
                           allow_redirects=False, timeout=self.timeout)
        if r.status_code != 200:
            raise Exception('code %s' % r.status_code)
        return r.json()


if __name__ == '__main__':
    m = Mfi('192.168.0.220', 'ubnt', 'ubnt')
    print(m.state())
