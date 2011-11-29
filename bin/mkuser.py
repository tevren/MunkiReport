#!/usr/bin/env python


################ TO BE REMOVED ################
### Users are now stored in a plist instead ###
################ TO BE REMOVED ################


import hashlib
import os
import sys
import getpass
import codecs


USERS_PATH = "/Library/Application Support/MunkiReport/users"


class FileUser(object):
    """Container for users."""
    
    def __init__(self, username, realname, password):
        """Store name and password attributes."""
        self.username = username
        self.realname = realname
        self.salt = password[:8].decode("hex")
        self.hexdigest = password[8:64]
    

def main(argv):
    users = dict()
    
    if os.path.exists(USERS_PATH):
        try:
            with codecs.open(USERS_PATH, "r", "utf-8") as f:
                for line in f:
                    fields = line.strip().split(":")
                    username, realname, password = [f.strip() for f in fields]
                    users[username] = FileUser(username, realname, password)
        except IOError as e:
            print "Couldn't read users from %s: %s" % (USERS_PATH, str(e))
            return 1
    
    username = raw_input("Username: ")
    realname = raw_input("Realname: ").decode(sys.stdout.encoding)
    password = getpass.getpass()
    salt = os.urandom(4)
    
    sha = hashlib.sha224()
    sha.update(salt)
    sha.update(password)
    hexpassword = salt.encode("hex") + sha.hexdigest()
    
    if username in users:
        print "Updating %s" % username
    else:
        print "Creating %s" % username
    
    users[username] = FileUser(username, realname, hexpassword)
    
    with codecs.open(USERS_PATH, "w", "utf-8") as f:
        for username in users.iterkeys():
            f.write(u"%s:%s:%s%s\n" % (
                username,
                users[username].realname,
                users[username].salt.encode("hex"),
                users[username].hexdigest
            ))
    
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))