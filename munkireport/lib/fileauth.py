# -*- coding: utf-8 -*-
"""Authentication of users stored in a plist

Users are stored in an XML plist where the root object is an array, and each
entry is a dictionary with username, realname, and password keys.

The password is a salted sha224 hash stored as a hex string. The first eight
characters (four bytes) is the salt, which is fed to the digest algorithm
before the password string. The 56 remaining characters is the digested result
of salt + password string.
"""

import tg
import logging
import hashlib
import codecs
import os
import plistlib
from repoze.what.adapters import BaseSourceAdapter, SourceError


__all__ = ['FileAuthenticator', 'FileMetadataProvider', 'get_users']


# Get a logger.
log = logging.getLogger(__name__.split(".")[0])

# FIXME: create a real cache instead, you have to restart the application to add new users
users = None
users_filename = "users.plist"

class FileUser(object):
    """Container for users."""
    
    def __init__(self, username, realname, password):
        """Store name and password attributes."""
        self.username = username
        self.realname = realname
        self.salt = password[:8].decode("hex")
        self.hexdigest = password[8:64]
    

def read_file_users():
    """Read and parse users file."""
    
    # path to where the users are stored
    appsupport_dir = tg.config.get("appsupport_dir")
    users_path = os.path.join(appsupport_dir, users_filename)
    
    file_users = dict()
    
    try:
        users = plistlib.readPlist(users_path)
    except BaseException as e:
        log.warn("Couldn't read users from %s: %s" % (users_path, str(e)))
        return file_users
    
    for user in users:
        file_users[user.username] = FileUser(user.username,
                                             user.realname,
                                             user.password)
    
    return file_users
    

def create_file_users(username, realname, password):
    """Create a users file with a single user if one doesn't exit."""
    
    # path to where the users are stored
    appsupport_dir = tg.config.get("appsupport_dir")
    users_path = os.path.join(appsupport_dir, users_filename)
    
    salt = os.urandom(4)
    
    sha = hashlib.sha224()
    sha.update(salt)
    sha.update(password)
    hexpassword = salt.encode("hex") + sha.hexdigest()
    
    try:
        log.info("Creating %s" % users_path)
        log.info("Creating %s user (%s)" % (username, realname))
        plistlib.writePlist([{
            "username": username,
            "realname": realname,
            "password": hexpassword
        }], users_path)
    except BaseException as e:
        log.error("Couldn't write users to %s: %s" % (users_path, str(e)))
        raise SourceError
    
    global users
    users = read_file_users()
    

def get_users():
    """Return users, read from disk if necessary."""
    
    global users
    if users is None:
        users = read_file_users()
    
    return users
    

class FileAuthenticator(object):
    """Authenticate users in a passwd style file."""
    
    def authenticate(self, environ, identity):
        print "FileAuthenticator.authenticate"
        # Read login and password.
        try:
            login = identity["login"]
            password = identity["password"]
        except KeyError:
            return None
        
        u = get_users()
        if login in u:
            user = u[login]
            sha = hashlib.sha224()
            sha.update(user.salt)
            sha.update(password)
            if sha.hexdigest() == user.hexdigest:
                log.info("FileAuthenticator successfully authenticated %s" % login)
                return login
        
        log.info("FileAuthenticator failed for %s" % login)
        return None
    

class FileMetadataProvider(object):
    """Provide metadata for Mac OS X users."""
    
    metadata = {}
    
    def add_metadata(self, environ, identity):
        # Read userid.
        userid = identity.get("repoze.who.userid")
        
        u = get_users()
        if userid in u:
            identity.update({"display_name": u[userid].realname})
            return
    

if __name__ == '__main__':
    import sys
    
    import getpass
    
    a = FileAuthenticator()
    md = FileMetadataProvider()
    
    username = raw_input("Username: ")
    password = getpass.getpass()
    
    userid = a.authenticate({}, {"login": username, "password": password})
    if userid is None:
        sys.stderr.write("Authentication failed\n")
        sys.exit(1)
    
    identity = {"repoze.who.userid": userid}
    md.add_metadata({}, identity)
    print "Metadata for %s:" % userid, repr(identity)
    
    sys.exit(0)
