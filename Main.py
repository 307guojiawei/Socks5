import socket
import socketserver

import multiprocessing
import threading

import time

from utils.Worker import backwardWorker, broker


class MyServer(socketserver.BaseRequestHandler):
    def handle(self):
        client = self.request
        try:
            # recv version identifier/method selection message
            request = self._recvBytesList(client, 3)

            # send accept methods: no auth
            payload = b'\x05\x00'
            client.sendall(payload)

            targetAddr, targetPort = self._decodeTargetInfo(client)

            localAddr = '127.0.0.1'
            localPort = 10000

            self._initWorker(client, targetAddr, targetPort, localAddr, localPort)

            payload = b'\x05'  # version
            payload += b'\x00'  # success
            payload += b'\x00'  # reserved
            payload += b'\x03'  # domain name
            payload += bytes((len(localAddr),))  # len of addr
            payload += localAddr.encode('ascii')

            localPortByte = bytes()
            if localPort > 256:
                payload += bytes([localPort // 256])
                payload += bytes([localPort % 256])
            else:
                payload += bytes([localPort])
            # print(payload)
            client.sendall(payload)
            while True:
                time.sleep(0)
                pass
        except Exception as e:
            #print('handler err', e)
            client.close()

    # worker thread,redirect client's request
    def _initWorker(self, client, targetAddr, targetPort, localAddr, localPort):
        targetSocket = socket.socket()
        targetSocket.connect((targetAddr, targetPort))
        print('connect to ',targetAddr,targetPort,' fileno ',targetSocket.fileno())
        #p = multiprocessing.Process(target=broker, args=(client, targetSocket))
        p = threading.Thread(target=broker, args=(client, targetSocket))
        p.start()

    def _recvBytesList(self, client, count=-1):
        ret = []
        recvCount = 0
        while True:
            if count != -1:
                if recvCount == count:
                    break
                recvCount += 1
            c = client.recv(1)
            if not c:
                break
            ret.append(c)
            # print("\tget:",c)

        return ret

    def _recvBytes(self, client, count=-1):
        ret = b''
        recvCount = 0
        while True:
            if count != -1:
                if recvCount == count:
                    break
                recvCount += 1
            c = client.recv(1)
            if not c:
                break
            ret += c
            # print("\tget:",c)

        return ret

    def _decodeTargetInfo(self, client):
        targetAddr = b''
        targetPort = 0
        # get required request header
        request = self._recvBytesList(client, 4)
        if request[3] == b'\x01':  # ipv4
            res = self._recvBytes(client, 4)
            targetAddr = socket.inet_ntoa(res)
        elif request[3] == b'\x03':  # domain
            res = self._recvBytesList(client, 1)
            # get address number count
            addrCount = int.from_bytes(res[0], byteorder='big', signed=False)
            #print('addrCount', addrCount)
            # recv target address
            targetAddr = self._recvBytes(client, addrCount)
            targetAddr = targetAddr.decode('utf-8')
            #print('target addr:', targetAddr)
        elif request[3] == b'\x04':  # ipv6
            res = self._recvBytes(client, 16)
            targetAddr = socket.inet_ntoa(res)

        # recv target port
        targetPort = self._recvBytes(client, 2)
        targetPort = int.from_bytes(targetPort, byteorder='big', signed=False)
        return targetAddr, targetPort


def main():
    server = socketserver.ThreadingTCPServer(('0.0.0.0', 1091), MyServer)
    server.serve_forever()


if __name__ == '__main__':
    main()
