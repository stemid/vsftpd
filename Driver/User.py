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

    def _db_is_user(self, username):
        c = self._c
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
            raise UserError('User does not exist in db')
        return rows

    def _db_add_user(self, username, password):
        c = self._c
        c.execute(
            '''
            insert into {db_table_users} 
            ({db_users_name}, {db_users_password})
            values (%s, %s)
            '''.format(
                db_table_users = s.get('db', 'table_users'),
                db_users_name = s.get('db', 'users_name'),
                db_users_password = s.get('db', 'users_password')
            ),
            (username, password, )
        )
        self._db.commit()

    def _db_del_user(self, username):
        c = self._c
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

    def _sys_add_user(self, username, home_dir, groups=[], comment=None):
        args = ('-d', home_dir, '-m', username)

        if groups and not comment:
            ex_args = (
                '-G', ','.join(groups)
            )
        elif comment and not groups:
            ex_args = (
                '-c', comment
            )
        elif groups and comment:
            ex_args = (
                '-G', ','.join(groups),
                '-c', "'" + comment.encode('utf-8') + "'"
            )
        else:
            ex_args = ()

        ex_args += args
        sudo.useradd(*ex_args)

    def _sys_del_user(self, username):
        sudo.userdel(username)

    def _sys_del_group(self, group):
        sudo.groupdel(group)

    def adduser(self, username, password, home=None, groups=[], comment=None):
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
        except UserError:
            self._db_add_user(username, password)

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
                raise UserError('Could not delete group %s from system' % group)

        try:
            self._db_del_user(username)
        except Exception as e:
            raise UserError('Could not delete user %s from db: %s' % (
                username,
                str(e)
            ))

        try:
            self._sys_del_user(username)
        except Exception as e:
            raise UserError('Could not delete user %s from system' % username)
        
class UserError(Exception):
    def __init__(self, errstr):
        self.errstr = errstr

    def __str__(self):
        return repr(self.errstr)
