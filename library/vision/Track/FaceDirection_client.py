# Author: Yehang Liu, Last Modified Date: 2016-02-17

import socket


class FDClient(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost', 8001))

    def fd_client(self, flag):
        if flag is None:
            pass
        elif flag == '1':
            self.sock.send(flag)
            return self.sock.recv(23)
        else:
            self.sock.send('2')
            self.sock.close()

if __name__ == "__main__":
        fdc = FDClient()
        fdc.fd_client('1')
