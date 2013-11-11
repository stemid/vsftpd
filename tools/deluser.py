#!/usr/bin/env python

from __future__ import print_function
from sys import path, exit, stderr
from os.path import join, abspath, dirname
import optparse

path.append(join(abspath(dirname(__file__)), '..'))

from Driver.User import User

user = User()

parser = optparse.OptionParser(
    description = 'Add a vsftpd user',
    epilog = 'By Stefan.Midjich@cygate.se',
    usage = 'Usage: %prog [options] <username>'
)

parser.add_option(
    '-g', '--groups',
    action = 'store',
    metavar = 'sudo,staff',
    type = 'string',
    help = 'Comma-separated list of additional group memberships'
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
    print('Exception while deleting user %s: %s' % (username, str(e)), file=stderr)
    exit(1)

print('%s was deleted.' % username)
