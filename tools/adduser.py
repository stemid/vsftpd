#!/usr/bin/env python

from sys import path
from os.path import join, abspath, dirname
try:
    import argparse
    parser = argparse.ArgumentParser(
        description = 'Add a vsftpd user',
        epilog = 'By Stefan.Midjich@cygate.se'
    )
    add_argument = parser.add_argument
except:
    import optparse
    parser = optparse.OptionParser(
        description = 'Add a vsftpd user',
        epilog = 'By Stefan.Midjich@cygate.se'
    )
    add_argument = parser.add_option

path.append(join(abspath(dirname(__file__)), '..'))

from Driver.User import User

user = User()

add_argument(
    '-g', '--groups',
    nargs = 1,
    default = None,
    dest = 'groups',
    metavar = 'sudo,staff',
    help = 'Comma-separated list of additional group memberships'
)

add_argument(
    '-d', '--directory',
    nargs = 1,
    default = None,
    dest = 'directory',
    metavar = '/home/user',
    help = 'Home directory of user'
)

add_argument(
    '-p', '--password',
    nargs = 1,
    default = None,
    dest = 'password',
    metavar = 'Secret2013',
    help = 'Password of user'
)

add_argument(
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
