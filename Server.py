import json
import socket
import socketserver

from utils.Config import Config
from utils.Worker import broker, initCycription


class RemoteServer(socketserver.BaseRequestHandler):
    def handle(self):
        client = self.request
        try:
            targetInfo = self._parseHeader(client)
            if targetInfo['pwd'] != Config().properties.get('pwd'):
                client.close()
                return
            self._initWorker(client,targetInfo['targetAddr'],targetInfo['targetPort'])
        except Exception as e:
            client.close()

    def _initWorker(self,client,targetAddr,targetPort):
        print("connect to",targetAddr)
        target = socket.socket()
        target.connect((targetAddr, targetPort))
        broker(client,target,"Server")


    def _parseHeader(self,client):
        res = client.recv(1)
        length = int.from_bytes(res, byteorder='big', signed=False)
        res = self._recvBytes(client,length)
        targetInfo = res.decode('utf-8')
        targetInfo = json.loads(targetInfo)
        return targetInfo


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



def main():
    initCycription()
    server = socketserver.ThreadingTCPServer((Config().properties.get('bindAddr'), Config().properties.get('remotePort')), RemoteServer)
    server.serve_forever()


if __name__ == '__main__':
    main()