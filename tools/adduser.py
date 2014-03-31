#!/usr/bin/env python

from __future__ import print_function
from sys import path, exit, stderr, stdout, stdin
from os.path import join, abspath, dirname
from termios import ECHO, TCSADRAIN, tcgetattr, tcsetattr
from random import randint
from crypt import crypt
from json import loads
from urllib import urlencode
import urllib2
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

def password_push(**config):
    url = config.get('api_url')
    values = {'password': config.get('password')}
    data = urlencode(values)

    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return loads(response.read())

def get_random_password(**config):
    url = config.get('api_url')

    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    json_response = loads(response.read())
    return json_response.get('phrase')

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
    metavar = '"Firstname Lastname"',
    type = 'string',
    help = 'Account contact person'
)

parser.add_option(
    '-E', '--email',
    metavar = '"Email address"',
    type = 'string',
    help = 'Contact persons e-mail address'
)

parser.add_option(
    '-P', '--phone',
    metavar = 'Phone#',
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
    metavar = '"Secret2013"',
    dest = 'password',
    type = 'string',
    help = 'Password of user'
)

parser.add_option(
    '-q', '--soft-quota',
    metavar = 'Size',
    dest = 'soft_quota',
    default = '50M',
    type = 'string',
    help = 'Soft quota limit. Symbols K, M, G, and T can be appended to numeric value to express kibibytes, mebibytes, gibibytes, and tebibytes. '
)

parser.add_option(
    '-Q', '--hard-quota',
    metavar = 'Size',
    dest = 'hard_quota',
    default = '60M',
    type = 'string',
    help = 'Hard quota limit. Symbols K, M, G, and T can be appended to numeric value to express kibibytes, mebibytes, gibibytes, and tebibytes. '
)

parser.add_option(
    '-v', '--verbose',
    action = 'store_true',
    dest = 'verbose',
    help = 'Verbose output'
)

(opts, args) = parser.parse_args()
password = None

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

# Prompt for password
if opts.prompt:
    # Disable echo to stdout
    stdin_fd = stdin.fileno()
    old_stdin = tcgetattr(stdin_fd)
    new_stdin = tcgetattr(stdin_fd)
    new_stdin[3] = new_stdin[3] & ~ECHO
    try:
        # Apply termcap config to stdin
        tcsetattr(stdin_fd, TCSADRAIN, new_stdin)
        # Custom prompt since echo is disabled raw_input can't show any prompt
        print('Password: ', end='')
        password = raw_input()
    finally:
        # Reset termcap config for stdin
        tcsetattr(stdin_fd, TCSADRAIN, old_stdin)
        stdout.write('\n') # Makes the following printed line better
else: # Take cli argument provided password
    if opts.password:
        password = opts.password

# Request random password from pwpusher as last resort
if not password:
    random_password = get_random_password(
        api_url = s.get('passwordpusher', 'api_url') + '/password'
    )
    password = random_password

# Create password pusher link
try:
    pusher = password_push(
        api_url = s.get('passwordpusher', 'api_url') + '/password',
        password = password,
        link_url = s.get('passwordpusher', 'api_url')
    )
    pusher_link = s.get('passwordpusher', 'api_url') + '/' + pusher.get('code')
except Exception as e:
    print('Problem creating password pusher link: %s' % str(e))

# Encrypt password
if password:
    # Generate salt for encryption
    salt_chars = '/.' + string.ascii_letters + string.digits
    salt_string = [salt_chars[randint(0, len(salt_chars)-1)] for c in range(0, 8)]
    salt = '$2$' + ''.join(salt_string) + '$'

    # Encrypt password
    encrypted_password = crypt(password, salt)

# Show summary and request confirmation before executing user creation
print(
    '''
    !!! PLEASE CONFIRM USER CREATION !!!

    No changes have been made yet.

    Username: {username}s
    Password: {password}s
    Home: {home}s
    Groups: {groups}s
    Contact: {comment}s
    E-mail: {email}s
    Phone#: {phone}s
    Soft Quota: {soft_quota}s
    Hard Quota: {hard_quota}s
    Password pusher link: {pusher_link}s

    No changes have been made yet.
    
    When you confirm user will receive an e-mail with all this info, 
    sans the cleartext password. 

    !!! ARE YOU SURE THAT LOOKS OK? !!!
    '''.format(
        username = username,
        password = password,
        home = opts.directory,
        groups = opts.groups,
        comment = opts.comment,
        email = opts.email,
        phone = opts.phone,
        soft_quota = opts.soft_quota,
        hard_quota = opts.hard_quota,
        pusher_link = pusher_link
    )
)

confirm_answer = raw_input('Confirm with yes or no: ')
if confirm_answer != 'yes':
    exit(0)

try:
    user.adduser(
        username = username, 
        password = encrypted_password, 
        home = opts.directory, 
        groups = opts.groups.split(','), 
        comment = opts.comment,
        email = opts.email,
        phone = opts.phone,
        quota = (opts.soft_quota, opts.hard_quota)
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
