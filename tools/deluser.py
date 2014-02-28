#!/usr/bin/env python

from __future__ import print_function
from sys import path, exit, stderr
from os.path import join, abspath, dirname
import optparse

from ConfigParser import ConfigParser
s = ConfigParser()
s.read(['/etc/vsftpd/app.cfg', 'app.cfg'])

path.append(join(abspath(dirname(__file__)), s.get('main', 'path')))

# Add virtualenv to path if present in config. 
# This happens before Driver.User is initiated so it can find the sh module. 
try:
    path.append(join(abspath(dirname(__file__)), s.get('main', 'virtualenv')))
except:
    pass

from Driver.User import User

user = User(s)

parser = optparse.OptionParser(
    description = 'Delete a vsftpd user',
    epilog = 'By Stefan.Midjich@cygate.se',
    usage = 'Usage: %prog [options] <username>'
)

parser.add_option(
    '-g', '--groups',
    action = 'store',
    metavar = 'sudo,staff',
    default = '',
    type = 'string',
    help = 'Comma-separated list of additional groups to delete'
)

parser.add_option(
    '-v', '--verbose',
    action = 'store_true',
    dest = 'verbose',
    help = 'Verbose output'
)

(opts, args) = parser.parse_args()

try:
    username = args[0]
except:
    parser.print_usage()
    exit(1)

try:
    user.deluser(username, opts.groups.split(','))
except Exception as e:
    print('Problem deleting %s: %s' % (username, str(e)), file=stderr)
    exit(1)

if opts.verbose:
    print('Finished deleting %s' % username)
exit(0)
