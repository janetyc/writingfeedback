import os
from ConfigParser import ConfigParser

configfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')
mturk_config = ConfigParser()
mturk_config.read(configfilepath)
