import json
import socket
import time
import base64
from eventlet.green.select import select

from utils.Config import Config


def broker(client,target,typeConn="None"):  # type 加密类型，None为不加密，Client为client->target加密,反向解密，Server为client->target解密，反向加密
    inputList=[client,target]

    while True:
        try:
            stdinput, stdoutput, stderr = select(inputList, [], inputList)
            for inputSocket in stdinput:
                if inputSocket == client:
                    forwardWorker(client,target,typeConn)
                else:
                    backwardWorker(client,target,typeConn)
            time.sleep(0)
        except Exception as e:
            #print('broker err',e)
            #print('client',client.fileno(),'target',target.fileno())
            target.close()
            client.close()
            break



def forwardWorker(client,target,typeConn):
    payload = client.recv(4096)


    if len(payload)==0:
        #raise BrokerException
        pass
    if typeConn == "Client":
        payload = encode(payload)
    elif typeConn == "Server":
        payload = decode(payload)

    target.sendall(payload)

def backwardWorker(client,target,typeConn):
    payload = target.recv(4096)
    if len(payload)==0:
        raise BrokerException
        pass
    if typeConn == "Server":
        payload = encode(payload)
    elif typeConn == "Client":
        payload = decode(payload)
    client.sendall(payload)


def encode(source):
    sourceMap = Config().properties.get('keyMapDict')
    result = list()
    for char in source:
        result.append(int(sourceMap[str(char)]))
    #print('encode',bytes(result))

    return bytes(result)
    #return source

def decode(source):
    sourceMapRev = Config().properties.get('keyMapRevDict')

    result = list()
    for char in source:
        #print(char)
        result.append(int(sourceMapRev[str(char)]))


    #print('decode',bytes(result))
    return bytes(result)
    #return source

def initCycription():
    dir = Config().properties.get('root')+Config().properties.get('keymap')
    with open(dir,"r") as f:
        keyMap = json.load(f)
        Config().properties.put('keyMapDict',keyMap)
        keyMapRev = dict()
        for key in keyMap.keys():
            keyMapRev[str(keyMap[key])]=key
        Config().properties.put('keyMapRevDict',keyMapRev)
    print('init cycription done')



class BrokerException(Exception):
    pass

