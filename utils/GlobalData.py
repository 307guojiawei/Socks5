from utils.Singleton import Singleton


@Singleton
class WorkerInfo:
    def __init__(self):
        self.workerList = []
        self.freePorts = []
        self.startPort = 10000

    def getFreePort(self):

        if len(self.freePorts) == 0:
            self.startPort += 1
            return self.startPort
        else:
            port = self.freePorts[len(self.freePorts) - 1]
            self.freePorts.remove(port)
            return port

    def addFreePort(self, port):
        self.freePorts.append(port)


