#!/usr/bin/env python

from __future__ import print_function
from sys import path, exit, stderr
from os.path import join, abspath, dirname
import optparse

def main():
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

    parser.add_option(
        '-d', '--directory',
        action = 'store',
        metavar = '/home/user',
        type = 'string',
        help = 'Home directory of user'
    )

    parser.add_option(
        '-c', '--comment',
        action = 'store',
        metavar = 'User Name',
        type = 'string',
        help = 'User description'
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
        exit(1)

    try:
        user.adduser(username, opts.password, opts.directory, opts.groups, opts.comment)
    except Exception as e:
        print('Problem importing user=%s, groups=%s: %s' % (username, opts.groups.split(' '), str(e)), file=stderr)

    print('Finished importing %s' % username)

try:
    main()
except KeyboardInterrupt as e:
    print("Received interrupt, exiting...", file=stderr)
    exit(1)
