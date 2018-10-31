import eventlet

from utils.GlobalData import WorkerInfo

workerThreadPool = eventlet.GreenPool(10000)


def recvBytesList(client, count=-1):
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


def recvBytes(client, count=-1):
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


def handle(client):
    # recv version identifier/method selection message
    request = recvBytesList(client, 3)

    # send accept methods: no auth
    payload = b'\x05\x00'
    client.sendall(payload)

    # get required request header
    request = recvBytesList(client, 5)

    # get address number count
    addrCount = int.from_bytes(request[4], byteorder='big', signed=False)
    print('addrCount', addrCount)

    # recv target address
    targetAddr = recvBytes(client, addrCount)
    targetAddr = targetAddr.decode('utf-8')
    print('target addr:', targetAddr)

    # recv target port
    targetPort = recvBytes(client, 2)
    targetPort = int.from_bytes(targetPort, byteorder='big', signed=False)
    print('port:', targetPort)

    localAddr = '10.1.30.110'
    localPort = WorkerInfo().getFreePort()
    workerThreadPool.spawn_n(worker, client, targetAddr, targetPort, localAddr, localPort)

    payload = b'\x05'  # version
    payload += b'\x00'  # success
    payload += b'\x00'  # reserved
    payload += b'\x03'  # domain name
    payload += bytes((len(localAddr),))  # len of addr
    payload += localAddr.encode('ascii')

    localPortByte = bytes()
    if localPort > 256:
        payload += bytes((int(localPort // 256),))
        payload += bytes((localPort % 256,))
    else:
        payload += bytes((localPort,))

    print(payload)
    client.sendall(payload)


# worker thread,redirect client's request
def worker(client, targetAddr, targetPort, localAddr, localPort):
    # targetSocket = eventlet.connect((targetAddr, targetPort), bind=(localAddr, localPort))
    print("init worker", targetAddr, targetPort, localAddr, localPort)
    

def main():
    server = eventlet.listen(('0.0.0.0', 1080))
    pool = eventlet.GreenPool(10000)
    while True:
        new_sock, address = server.accept()
        pool.spawn_n(handle, new_sock)


if __name__ == '__main__':
    main()
