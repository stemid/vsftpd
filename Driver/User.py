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
        try:
            sys_user = id(username)
        except ErrorReturnCode_1 as e:
            return False
        return True

    def _sys_is_group(self, groupname):
        sys_group = grep('^' + groupname, '/etc/group')
        return True

    def _sys_add_user(self, username, home_dir, groups=None, comment=None):
        args = ('-d', home_dir, '-m', username)

        if groups and not comment:
            args = (
                '-G', groups,
                '-d', home_dir,
                '-m', username
            )
        elif comment and not groups:
            args = (
                '-c', comment,
                '-d', home_dir,
                '-m', username
            )
        elif groups and comment:
            args = (
                '-G', groups,
                '-c', comment,
                '-d', home_dir,
                '-m', username
            )
        else:
            args = (
                '-d', home_dir,
                '-m', username
            )

        sudo.useradd(*args)

    def _sys_del_user(self, username):
        sudo.userdel(username)

    def adduser(self, username, password, home=None, groups=None, comment=None):
        if groups:
            # Check if groups already exist so they can be used
            for group in groups.split(','):
                try:
                    self._sys_is_group(group)
                except:
                    raise UserError('Group does not exist')

        # Check if username exists in DB
        db_users = self._db_is_user(username)
        if db_users >= 1:
            raise UserError('User already exists in DB')

        # Check if username exists in system
        if self._sys_is_user(username):
            raise UserError('User already exists in system')

        self._db_add_user(username, password)
        self._sys_add_user(username, home, groups, comment)
        return True

    def deluser(self, username, groups):
        (exc_str1, exc_str2) = (None, None)
        try:
            self._db_del_user(username)
        except Exception as e:
            exc_str1 = str(e)
            pass
        try:
            self._sys_del_user(username)
        except Exception as e:
            exc_str2 = str(e)
            pass
        
        if exc_str1 is not None or exc_str2 is not None:
            return (exc_str1, exc_str2)
        else:
            for group in groups:
                try:
                    self._sys_del_group(group)
                except Exception as e:
                    
        return True

class UserError(Exception):
    def __init__(self, errstr):
        self.errstr = errstr

    def __str__(self):
        return repr(self.errstr)
