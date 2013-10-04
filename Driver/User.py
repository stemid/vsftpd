import sh
import MySQLdb as mysql

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

        # Init system commands here to catch possible exceptions early
        self._useradd = sh.Command(s.useradd_binary)
        self._id = sh.Command(s.id_binary)
        self._setquota = sh.Command(s.setquota_binary)

    def _db_is_user(self, username):
        c = self._c
        rows = 0
        c.execute('''
                  select %{db_users_id} 
                  from %{db_table_users} 
                  where %{db_users_name}='%{username}'
                  '''
                 ).format(
                     db_users_id = s.db_users_id,
                     db_table_users = s.db_table_users,
                     username
                 )

    def _db_add_user(self, username, password):
        c = self._c
        c.execute('''
                  insert into %{db_table_users} 
                  (%{db_users_name}, %{db_users_password})
                  values ('%{username}', md5('%{password}'))
                  '''
                 ).format(
                     db_table_users = s.db_table_users,
                     db_users_name = s.db_users_name,
                     db_users_password = s.db_users_password,
                     username = username,
                     password = password
                 )
        self._db.commit()

    def _db_del_user(self, username):
        c = self._c
        c.execute('''
                  delete from %{db_table_users}
                  where username='%{username}'
                  '''
                 )

    def _sys_is_user(self, username):
        id = sh.Command(s.id_binary)
        id(username)

    def _sys_add_user(self, username, home_dir):
        useradd = sh.Command(s.useradd_binary)
        useradd(
            '-d',
            home_dir,
            '-m',
            username
        )

    def _sys_del_user(self, username):
        userdel = sh.Command(s.userdel_binary)
        userdel(username)

    def adduser(self, username, password, home=None, groups=None):
