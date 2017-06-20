import yaml
import getpass
import os

HOME = os.path.expanduser('~')
CONFIG_LOCATION = HOME + '/.ffconf.yaml'
SKELETON_CONFIG = dict(username=None, email=None, password=None)

class Config(object):
    def __init__(self, file):
        if file == None:
            self._set_config()
            file = CONFIG_LOCATION

        self.config = yaml.load(open(file, 'r'))
        self._file = file
        print self.config

    def _set_config(self):
        if not os.path.isfile(CONFIG_LOCATION):
            print "No config file detected."
            begin = raw_input('Would you like to create a config file in %s? y/n ' % (HOME))
            if begin.lower().startswith('y'):
                yaml.dump(SKELETON_CONFIG, open(CONFIG_LOCATION, 'w'))
                print 'Created %s' % (CONFIG_LOCATION)

    def get(self, key):
        return self.config[key]

    def put(self, key, value):
        self.config[key] = value
        yaml.dump(self.config, open(self._file, 'w'))

    def set_username(self, username):
        self.put('username', username)

    def set_email(self, email):
        self.put('email', email)

    def set_password(self, password=None):
        if password == None:
            password = getpass.getpass("Enter password: ")
        self.put('password', password)

    def reset(self):
        yaml.dump(SKELETON_CONFIG, open(self._file, 'w'))
