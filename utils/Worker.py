from eventlet.green.select import select


def broker(client,target):
    inputList=[client,target]
    while True:
        try:
            stdinput, stdoutput, stderr = select(inputList, [], inputList)
            for inputSocket in stdinput:
                if inputSocket == client:
                    forwardWorker(client,target)
                else:
                    backwardWorker(client,target)
        except Exception as e:
            #print('broker err',e)
            #print('client',client.fileno(),'target',target.fileno())

            target.close()
            client.close()
            #raise BrokerException


def forwardWorker(client,target):
    payload = client.recv(4096)
    if len(payload)==0:
        #raise BrokerException
        pass
    target.sendall(payload)

def backwardWorker(client,target):
    payload = target.recv(4096)
    if len(payload)==0:
        raise BrokerException
        pass
    client.sendall(payload)


class BrokerException(Exception):
    pass

