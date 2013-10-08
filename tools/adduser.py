#!/usr/bin/env python

from sys import path
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
    nargs = 1,
    default = None,
    metavar = 'sudo,staff',
    help = 'Comma-separated list of additional group memberships'
)

parser.add_option(
    '-d', '--directory',
    nargs = 1,
    default = None,
    metavar = '/home/user',
    help = 'Home directory of user'
)

parser.add_option(
    '-p', '--password',
    nargs = 1,
    default = None,
    metavar = 'Secret2013',
    help = 'Password of user'
)

parser.add_option(
    '-u', '--username',
    nargs = 1,
    default = '',
    metavar = 'user',
    help = 'Users login name'
)

args = parser.parse_args()

print args.groups
print args.directory
print args.password
print args.username
