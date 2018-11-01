import json
import os
import tempfile

from utils.Singleton import Singleton


@Singleton
class Config:
    def __init__(self):
        self.path = str(os.path.dirname(os.path.realpath(__file__)))
        self.properties = Properties(os.path.join(self.path, '../config.json'))
        self.properties.put("root",str(self.path)+"/../")


class Properties:
    def __init__(self, file_name):
        self.file_name = file_name
        self.properties = {}
        try:
            fopen = open(self.file_name, 'r')
            self.properties = json.load(fopen)
        except Exception as e:
            raise e
        else:
            fopen.close()

    def has_key(self, key):
        return key in self.properties

    def get(self, key, default_value=''):
        if key in self.properties:
            return self.properties[key]
        return default_value

    def put(self, key, value):
        self.properties[key] = value
        #self.flush()

    def flush(self):
        with open(self.file_name,"w") as f:
            json.dump(self.properties,f)
