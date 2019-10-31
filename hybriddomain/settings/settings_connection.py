import os
import getpass
from collections import OrderedDict


class Connection(object):
    def __init__(self):

        self.host = "corp7.uniyar.ac.ru"
        self.port = 2222
        self.username = "tester"
        self.password = ""

    def toDict(self):
        connDict = OrderedDict([
            ("Host", self.host),
            ("Port", self.port),
            ("Username", self.username),
            ("Password", self.password)])
        return connDict

    def fromDict(self, connDict):
        self.host = connDict["Host"]
        self.port = connDict["Port"]
        self.username = connDict["Username"]
        self.password = connDict["Password"]
    
    def loadFromFile(self, fileNamePath):
        pass

    def get_password(self):

        if self.password == "":
            self.password = os.getenv("CLUSTER_PASS")
            if self.password is None:
                print("Please enter password for user "
                      + self.username + ":")
                self.password = getpass.getpass()


