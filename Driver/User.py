import MySQLdb as mysql
from sh import sudo, id, grep, ErrorReturnCode_1

from Settings import Settings
s = Settings()

class User:
    def __init__(self):
        conn = mysql.connect(
            host = s.db_host,
            user = s.db_user,
            passwd = s.db_pass,
            db = s.db_name,
            use_unicode = True
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
            where {db_users_name}='{username}'
            '''.format(
                db_users_id = s.db_users_id,
                db_table_users = s.db_table_users,
                db_users_name = s.db_users_name,
                username = username
            )
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
            values ('{username}', md5('{password}'))
            '''.format(
                db_table_users = s.db_table_users,
                db_users_name = s.db_users_name,
                db_users_password = s.db_users_password,
                username = username,
                password = password
            )
        )
        self._db.commit()

    def _db_del_user(self, username):
        c = self._c
        c.execute(
            '''
            delete from {db_table_users}
            where username = '{username}'
            '''.format(
                db_table_users = s.db_table_users,
                username = username
            )
        )

    def _sys_is_user(self, username):
        sys_user = id(username)
        return sys_user

    def _sys_is_group(self, groupname):
        sys_group = grep('^' + groupname, '/etc/group')
        return sys_group

    def _sys_add_group(self, group):
        sudo.groupadd(group)

    def _sys_add_user(self, username, home_dir, groups=None, comment=None):
        args = ('-d', home_dir, '-m', username)

        if groups and not comment:
            ex_args = (
                '-G', groups
            )
        elif comment and not groups:
            ex_args = (
                '-c', comment
            )
        elif groups and comment:
            ex_args = (
                '-G', groups,
                '-c', "'" + comment + "'"
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
        # Check if username exists in DB and add it
        try:
            self._db_is_user(username)
        except UserError:
            self._db_add_user(username, password)

        # Check if username exists in system and add it
        try:
            self._sys_is_user(username):
        except:
            self._sys_add_user(username, home, groups, comment)

        if groups:
            # Check if groups already exist so they can be used
            for group in groups.split(','):
                if group == username:
                    continue
                try:
                    self._sys_is_group(group)
                except:
                    self._sys_add_group(group)

    def deluser(self, username, groups=[]):
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
        
        for group in groups:
            if group == username:
                continue
            try:
                self._sys_del_group(group)
            except Exception as e:
                raise UserError('Could not delete group %s from system' % group)

class UserError(Exception):
    def __init__(self, errstr):
        self.errstr = errstr

    def __str__(self):
        return repr(self.errstr)
