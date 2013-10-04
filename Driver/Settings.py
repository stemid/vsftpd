# This file holds the Settings class that basically just reads the 
# config.json file to know what to do. 

### DO NOT EDIT BELOW THIS POINT (Unless you're a nerd) ###

# Helpful functions for relative paths
from os.path import join, abspath, dirname
here = lambda *p: join(abspath(dirname(__file__)), *p)
PROJECT_ROOT = here('..') # assume settings.py is one step under root
root = lambda *p: join(abspath(PROJECT_ROOT), *p)

# Process the config dictionary into a Settings class
class Settings:
    def __init__(self, **kw):
        from fnmatch import filter
        from json import load

        # Take optional configuration file path from arguments
        if kw.get('config', None):
            config_file = kw.get('config')
        else:
            config_file = root('config.json')

        # Load the json configuration
        self.config = load(open(config_file, 'r'))

        # Make all paths absolute
        settings = filter(self.config.keys(), '*_path')
        for setting in settings:
            self.config[setting] = root(self.config[setting])

        # Create read only attributes for all settings
        for setting in self.config:
            setattr(self, setting, self.config[setting])
