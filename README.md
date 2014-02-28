# Vsftpd User interface

This is an attempt to make a Vsftpd+pam\_mysql+MariaDB server easier to manage. 

Check app.cfg for configuration options.

# Driver

This is a module that handles user creation in DB and in system. 

## DB Schema

This interface works with the DB schema in tools/vsftpd.sql.

# Tools

Here are two tools that I generally install on the server like this. 

## Installation of tools

Either install these modules globally or in a virtualenv. 

  * mysqldb
  * sh

Then symlink the tools from /usr/local/sbin like this. 

    sudo ln -s /usr/local/sbin/vsftpd_adduser /home/me/vsftpd/tools/adduser.py
    sudo ln -s /usr/local/sbin/vsftpd_deluser /home/me/vsftpd/tools/deluser.py

Modify the paths to where you store the cloned vsftpd repo. 

If you're using a virtualenv then modify app.cfg and uncomment the virtualenv line while also setting it to the virtualenv you have created where the above modules are installed. 

    virtualenv: /home/me/.venvs/vsftpd/lib64/python2.6/site-packages

Note that the above example is for a 64-bit system. 
