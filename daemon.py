#!/usr/bin/env python3

import time
import logging
import paho.mqtt.client as mqtt
import heyu

import settings

__author__ = 'madrider'


LOG = logging.getLogger()


class Main(object):
    server = '127.0.0.1'
    port = 1883
    user = None
    password = None
    pause = 0.5
    password = None
    __targets = settings.targets.split()
    resend_timeout = settings.resend_timeout
    commands = []
    status = {}
    time = {}

    def __init__(self, server=None, port=None, user=None, password=None):
        self.__gen = self.__next_command_generator()
        if server:
            self.server = server
        if port:
            self.port = port
        if user:
            self.user = user
        if password:
            self.password = password
        self.client = mqtt.Client()

    def add_command(self, addr, cmd):
        self.commands.append((addr, cmd))

    def __next_command_generator(self):
        while 1:
            for d in self.__targets:
                while self.commands:
                    yield self.commands.pop()
                yield (d, 'status')

    def on_connect(self, client, userdata, flags, rc):
        LOG.info('Connected with result code %s', rc)
        client.subscribe([('x10/+/command', 0), ('x10/+/command', 1)])

    def on_disconnect(self, client, userdata, rc):
        LOG.info('disconnect with %s', rc)

    def on_message(self, client, userdata, msg):
        if msg.retain:
            return
        parts = msg.topic.split('/')
        if parts[2] == 'command':
            cmd = msg.payload.decode('utf-8').lower()
            addr = parts[1]
            LOG.info('got cmd %s to %s', cmd, addr)
            self.add_command(addr, cmd)

    def main(self):
        if self.user:
            self.client.username_pw_set(self.user, self.password)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.client.connect(self.server, self.port, 60)
        self.client.loop_start()
        try:
            while 1:
                self.cycle()
                time.sleep(0.1)
        finally:
            self.client.loop_stop()

    def cycle(self):
        addr, cmd = self.__gen.__next__()

        LOG.debug(cmd)
        if cmd == 'status':
            status = heyu.get_status(addr)
            if status:
                LOG.debug('status of %s is %s', addr, status)
                if self.status.get(addr) != status:
                    self.publish(addr, status)
                elif time.time() - self.time.get(addr, 0) > self.resend_timeout:
                    self.publish(addr, status)


        else:
            heyu.send_command(cmd, addr)

    def publish(self, addr, status):
        self.status[addr] = status
        self.time[addr] = time.time()
        self.client.publish('x10/%s' % addr.lower(), status, qos=0, retain=False)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    Main(server=settings.server, port=settings.port, user=settings.user, password=settings.password).main()
