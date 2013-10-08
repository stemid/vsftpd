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
        # Generate random 16 byte username
        u = uuid4()
        m = md5(u.bytes)
        self.username = m.hexdigest()[:16]

        # Use full username as temporary password
        self.password = m.hexdigest()

        self.user = User()

    def test_add_user(self):
        home = '/home/' + self.username

        assert self.user.adduser(
            self.username.encode('utf-8'), 
            self.password.encode('utf-8'), 
            home
        )

    def test_delete_user(self):
        assert self.user.deluser(self.username)

if __name__ == '__main__':
    unittest.main()
