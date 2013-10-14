#!/usr/bin/env python

from sys import path, exit
from os.path import join, abspath, dirname
import optparse

path.append(join(abspath(dirname(__file__)), '..'))

from Driver.User import User

user = User()

parser = optparse.OptionParser(
    description = 'Add a vsftpd user',
    epilog = 'By Stefan.Midjich@cygate.se'
)

parser.add_option(
    '-g', '--groups',
    action = 'store',
    metavar = 'sudo,staff',
    type = 'string',
    help = 'Comma-separated list of additional group memberships'
)

parser.add_option(
    '-d', '--directory',
    action = 'store',
    metavar = '/home/user',
    type = 'string',
    help = 'Home directory of user'
)

parser.add_option(
    '-p', '--password',
    action = 'store',
    metavar = 'Secret2013',
    type = 'string',
    help = 'Password of user'
)

(opts, args) = parser.parse_args()

try:
    username = args[0]
except:
    parser.print_usage()
    sys.exit(1)

try:
    user.adduser(username, opts.password, opts.directory, opts.groups)
except Exception as e:
    print str(e)
    sys.exit(1)
