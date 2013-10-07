import unittest
from sys import path
from os.path import join, abspath, dirname
from json import dumps, dump
from hashlib import md5
from uuid import uuid4

path.append(join(abspath(dirname(__file__)), '..'))

from Driver.User import User

class UserTest(unittest.TestCase):
    def runTest(self):
        unittest.main()

    def setUp(self):
        self.user = User()

    def test_add_user(self):
        # Generate random 16 byte username
        u = uuid4()
        m = md5(u.bytes)
        username = m.hexdigest()[:16]

        # Export it to the class for delete_user test
        self.username = username

        # Use full username as temporary password
        password = m.hexdigest()

        home = '/home/' + username

        assert self.user.adduser(username, password, home)

    def test_delete_user(self):
        assert self.user.deluser(self.username)

if __name__ == '__main__':
    unittest.main()
