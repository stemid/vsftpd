from __future__ import print_function
import MySQLdb as mysql
from sh import sudo, id, grep, ErrorReturnCode_1

class User:
    def __init__(self, s):
        conn = mysql.connect(
            host = s.get('db', 'hostname'),
            user = s.get('db', 'username'),
            passwd = s.get('db', 'password'),
            db = s.get('db', 'database'),
            use_unicode = s.get('db', 'unicode')
        )

        self._c = conn.cursor()
        self._db = conn

        # Copy the configuration options globally
        self._s = s

    def _db_is_user(self, username):
        c = self._c
        s = self._s
        rows = 0
        rows = c.execute(
            '''
            select {db_users_id} 
            from {db_table_users} 
            where {db_users_name}=%s
            '''.format(
                db_users_id = s.get('db', 'users_id'),
                db_table_users = s.get('db', 'table_users'),
                db_users_name = s.get('db', 'users_name')
            ),
            (username, )
        )
        if rows <= 0:
            raise DriverError('User does not exist in db')
        return rows

    def _db_add_user(self, **kw):
        username = kw.get('username')
        password = kw.get('password')
        contact = kw.get('contact', None)
        email = kw.get('email', None)
        phone = kw.get('phone', None)

        c = self._c
        s = self._s

        c.execute(
            '''
            insert into {db_table_users} 
            (
                {db_users_name}, 
                {db_users_password}, 
                {db_users_contact}, 
                {db_users_email}, 
                {db_users_phone}
            )
            values (%s, %s, %s, %s, %s)
            '''.format(
                db_table_users = s.get('db', 'table_users'),
                db_users_name = s.get('db', 'users_name'),
                db_users_password = s.get('db', 'users_password'),
                db_users_contact = s.get('db', 'users_contact'),
                db_users_email = s.get('db', 'users_email'),
                db_users_phone = s.get('db', 'users_phone')
            ),
            (username, password, contact, email, phone, )
        )
        self._db.commit()

    def _db_del_user(self, username):
        c = self._c
        s = self._s
        c.execute(
            '''
            delete from {db_table_users}
            where username = %s
            '''.format(
                db_table_users = s.get('db', 'table_users')
            ),
            (username, )
        )
        self._db.commit()

    def _sys_is_user(self, username):
        sys_user = id(username)
        return sys_user

    def _sys_is_group(self, groupname):
        sys_group = grep('^' + groupname, '/etc/group')
        return sys_group

    def _sys_add_group(self, group):
        sudo.groupadd(group)

    def _sys_add_user(self, username, home_dir, groups=[], comment=u''):
        if not home_dir:
            raise DriverError('Must have home_dir')

        print('Debug')
        args = ('-d', home_dir, '-m', username, '-C', "'%s'" % comment)
        ex_args = ()

        if len(groups):
            ex_args = (
                '-G', ','.join(groups)
            )

        ex_args += args
        sudo.useradd(*ex_args)

    def _sys_del_user(self, username):
        sudo.userdel(username)

    def _sys_del_group(self, group):
        sudo.groupdel(group)

    def _sys_setquota(self, username, soft_quota, hard_quota):
        sudo.setquota('-a', username, soft_quota, hard_quota, 0, 0)

    def adduser(self, **kw):
        username = kw.get('username')
        password = kw.get('password')
        home = kw.get('home', None)
        groups = kw.get('groups', [])
        comment = kw.get('comment', '')
        email = kw.get('email', None)
        phone = kw.get('phone', None)
        soft_quota, hard_quota = kw.get('quota')

        contact = comment

        # Check that we have some quota set
        #if len(soft_quota)

        # If we have extra contact info then append it to the comment
        if email:
            comment = comment + '|' + email
        if phone:
            comment = comment + '|' + phone

        # Check if groups already exist so they can be used
        for group in groups:
            if group == username:
                continue
            try:
                self._sys_is_group(group)
            except:
                self._sys_add_group(group)

        # Check if username exists in DB and add it
        try:
            self._db_is_user(username)
        except DriverError:
            self._db_add_user(
                username = username, 
                password = password,
                contact = contact,
                email = email,
                phone = phone
            )

        # Check if username exists in system and add it
        try:
            self._sys_is_user(username)
        except:
            self._sys_add_user(username, home, groups, comment)

    def deluser(self, username, groups=[]):
        for group in groups:
            if group == username or group == '':
                continue
            try:
                self._sys_del_group(group)
            except Exception as e:
                raise DriverError('Could not delete group %s from system' % group)

        try:
            self._db_del_user(username)
        except Exception as e:
            raise DriverError('Could not delete user %s from db: %s' % (
                username,
                str(e)
            ))

        try:
            self._sys_del_user(username)
        except Exception as e:
            raise DriverError('Could not delete user %s from system' % username)

class DriverError(Exception):
    def __init__(self, errstr):
        self.errstr = errstr

    def __str__(self):
        return repr(self.errstr)
