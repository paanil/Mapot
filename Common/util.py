import json
import sys

class Config:
    def __init__(self, default_config):
        self.default_config = default_config
        self.config = None
        
    def get_value(self, key):
        value = self.config[key]
        if value is not None: return value
        return self.default_config[key]

    def read(self, config_file):
        self.config = read_json(config_file)
        if self.config is None:
            self.config = self.default_config
            write_json(config_file, self.config)

#-------------------------------------------------------------------------------

def read_file(file_name):
    try:
        with open(file_name, "r") as f:
            return f.read()
    except FileNotFoundError:
        print("Cannot open file", file_name, ":", sys.exc_info()[0])
    except IOError:
        print("Cannot read from file", file_name, ":", sys.exc_info()[0])
    except:
        print("Unexpected error when reading file", file_name, ":",  sys.exc_info()[0])
    return None

def read_json(file_name):
    data_string = read_file(file_name)
    if data_string is None: return None
    try:
        return json.loads(data_string)
    except ValueError:
        print("File", file_name, "does not contain valid json :",  sys.exc_info()[0])
    return None

def write_json(filename, data):
    with open(filename, "w") as f:
        f.write(json.dumps(data, sort_keys=True, indent=4))
