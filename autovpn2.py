#! /usr/bin/env python2
#
# Autovpn2 Written by Rupe Wed May 13 2020, Version 1.0
#
# Connects to VPN Gate Public VPN Relay Servers.
#
# https://www.vpngate.net/en/
#

from base64 import b64decode
from commands import getoutput
from contextlib import closing
from os import geteuid, remove
from os.path import isfile
from random import choice
from subprocess import call
from sys import argv, exit, stderr
from urllib2 import urlopen


class AutoVpn(object):
    def __init__(self, country='US'):
        self.country = country.upper()
        self.servers = list()
        self.get_serverlist()
        self.openvpn()

    def save_config_file(self):
        print "[autovpn2] writing config file"
        try:
            with open('/tmp/openvpnconf', 'w') as config_file:
                server = self.servers.index(self.country)
                config_file.write(
                    '\n'.join(
                        str(b64decode(self.servers[server + 8])
                           ).split('\n')[:-1]
                    )
                )
        except:
            print "[autovpn2] rewriting config file"
            self.get_serverlist()
        else:
            print "[autovpn2] running openvpn\n"

    def get_serverlist(self):
        if not self.country:
            self.country = "US"
        print "[autovpn2] looking for %s" % self.country

        with closing(urlopen("http://www.vpngate.net/api/iphone/")
                    ) as serverlist:
            serverlist = serverlist.read().split(',')
            self.servers = [x for x in serverlist if len(serverlist) > 15]
            try:
                self.servers.index(self.country)
            except ValueError:
                exit(
                    "[\033[91m!\033[0m] Country code " + "\033[93m" +
                    self.country + "\033[0m" + " not in server list"
                )
            else:
                self.save_config_file()

    def openvpn(self):
        call(['openvpn', '--config', '%s' % '/tmp/openvpnconf'])


if __name__ == '__main__':
    if geteuid() is not 0:
        exit("\033[91m[!]\033[0m Run as super user!")

    try:
        print "\n[autovpn2] getting server list"
        print "[autovpn2] parsing response"
        AutoVpn(''.join(argv[1:]))

    except KeyboardInterrupt:
        call(["kill", "-9", "%s" % getoutput('pidof openvpn')])
        stderr.write("\x1b[2J\x1b[H")
        if isfile("/tmp/openvpnconf"):
            remove("/tmp/openvpnconf")
        retry = ('y', 'yes')
        try:
            ans = raw_input(
                "\033[92m\n[autovpn2]\033[93m try another VPN? (y/n)\033[0m " +
                "\033[92m"
            )
            if ans.lower() in retry:
                try:
                    servers = ('JP', 'JP')
                    AutoVpn(choice(servers))
                except:
                    if isfile("/tmp/openvpnconf"):
                        remove("/tmp/openvpnconf")
        except:
            pass
