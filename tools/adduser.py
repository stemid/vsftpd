#!/usr/bin/env python -i

import argparse
from Driver.User import User

user = User()

parser = argparse.ArgumentParser(
    description = 'Add a vsftpd user',
    epilog = 'By Stefan.Midjich@cygate.se'
)

parser.add_argument(
    '-g', '--groups',
    nargs = 1,
    default = None,
    dest = 'groups',
    metavar = 'sudo,staff',
    help = 'Comma-separated list of additional group memberships'
)

parser.add_argument(
    '-d', '--directory',
    nargs = 1,
    default = None,
    dest = 'directory',
    metavar = '/home/user',
    help = 'Home directory of user'
)

parser.add_argument(
    '-p', '--password',
    nargs = 1,
    default = None,
    dest = 'password',
    metavar = 'Secret2013',
    help = 'Password of user'
)

parser.add_argument(
    'username',
    nargs = 1,
    default = None,
    metavar = 'user',
    help = 'Users login name'
)

args = parser.parse_args()

print args.groups
print args.directory
print args.password
print args.username

