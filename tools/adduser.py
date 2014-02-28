#!/usr/bin/env python

from __future__ import print_function
from sys import path, exit, stderr, stdout, stdin
from os.path import join, abspath, dirname
from termios import ECHO, TCSADRAIN, tcgetattr, tcsetattr
from random import randint
from crypt import crypt
import string
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
    description = 'Add a vsftpd user',
    epilog = 'By Stefan.Midjich@cygate.se',
    usage = 'Usage: %prog [options] <username>'
)

parser.add_option(
    '-g', '--groups',
    metavar = 'sudo,staff',
    default = 'ftp',
    type = 'string',
    help = 'Comma-separated list of additional group memberships'
)

parser.add_option(
    '-d', '--directory',
    metavar = '/home/user',
    default = None,
    type = 'string',
    help = 'Home directory of user'
)

parser.add_option(
    '-C', '--comment',
    metavar = 'Firstname Lastname',
    type = 'string',
    help = 'Account contact person'
)

parser.add_option(
    '-E', '--email',
    metavar = 'Email address',
    type = 'string',
    help = 'Contact persons e-mail address'
)

parser.add_option(
    '-P', '--phone',
    metavar = 'Phone #',
    type = 'string',
    help = 'Contact persons phone number'
)

parser.add_option(
    '-p', '--prompt',
    action = 'store_true',
    dest = 'prompt',
    help = 'Prompt for a password'
)

parser.add_option(
    '--password',
    metavar = 'Secret2013',
    dest = 'password',
    type = 'string',
    help = 'Password of user'
)

parser.add_option(
    '-v', '--verbose',
    action = 'store_true',
    dest = 'verbose',
    help = 'Verbose output'
)

(opts, args) = parser.parse_args()

# Take final positional argument as username
try:
    username = args[0]
except:
    parser.error('Must specify username argument')
    parser.print_usage()
    exit(1)

# Make default home dir
if not opts.directory:
    opts.directory = s.get('system', 'home_dir') + '/' + username

if opts.prompt and opts.password:
    parser.error('Options --prompt and --password are mutually exclusive.')
    exit(1)

if opts.prompt:
    # Prompt for a password from stdin
    password_prompt = ''
    if opts.verbose:
        password_prompt = 'Enter password: '

    # Disable echo to stdout
    stdin_fd = stdin.fileno()
    old_stdin = tcgetattr(stdin_fd)
    new_stdin = tcgetattr(stdin_fd)
    new_stdin[3] = new_stdin[3] & ~ECHO
    try:
        tcsetattr(stdin_fd, TCSADRAIN, new_stdin)
        password = raw_input(password_prompt)
    finally:
        tcsetattr(stdin_fd, TCSADRAIN, old_stdin)
        stdout.write('\n') # Makes the following printed line better
else:
    password = opts.password

if password:
    # Generate salt for encryption
    salt_chars = '/.' + string.ascii_letters + string.digits
    salt_string = [salt_chars[randint(0, len(salt_chars)-1)] for c in range(0, 8)]
    salt = '$2$' + ''.join(salt_string) + '$'

    # Encrypt password
    encrypted_password = crypt(password, salt)

try:
    user.adduser(
        username = username, 
        password = encrypted_password, 
        home = opts.directory, 
        groups = opts.groups.split(','), 
        comment = opts.comment,
        email = opts.email,
        phone = opts.phone
    )

    # 4d-bug
    #print(username, encrypted_password, opts.directory, opts.groups.split(','), opts.comment)
except Exception as e:
    print('Problem importing user=%s, groups=%s: %s' % (
        username.encode('utf-8'), 
        opts.groups.split(','), 
        str(e)
    ), file=stderr)
    exit(1)

if opts.verbose:
    print('Finished importing %s' % username)
