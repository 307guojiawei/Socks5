from eventlet.green import select

from utils.Singleton import Singleton


@Singleton
class WorkerInfo:
    def __init__(self):
        self.targetSocketList = []
        self.clientSocketList = []
        self.socketDict = {}
        self.epoll = select.epoll()



