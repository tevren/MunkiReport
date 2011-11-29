# -*- coding: utf-8 -*-
"""Authentication of Mac OS X users

Currently uses shell commands to do lookup, should probably be rewritten to
use PAM and/or PyObjC.
"""

import re
import logging
import pexpect
from repoze.what.adapters import BaseSourceAdapter, SourceError


__all__ = ['MacOSXAuthenticator', 'MacOSXMetadataProvider', 'MacOSXGroupAdapter']


# Get a logger.
log = logging.getLogger(__name__.split(".")[0])

# allow something resembling unix userids, and common email addresses
valid_userid = re.compile(r'^[a-zA-Z][a-zA-Z0-9@.\-_]{1,63}$')


def get_output(argv):
    # Spawn a shell command and return all output, or None if there is an
    # error.
    if len(argv) == 1:
        cmd = pexpect.spawn(argv[0])
    else:
        cmd = pexpect.spawn(argv[0], argv[1:])
    # Read output.
    output = cmd.read()
    # Close the program.
    cmd.close()
    # Force close if it doesn't shutdown nicely.
    if cmd.isalive():
        cmd.close(force=True)
    # If the command exited abnormally we abort.
    if cmd.signalstatus:
        log.debug("%s died with signal %d" % (argv[0], cmd.signalstatus))
        return None
    # An exit status different from 0 means the command failed.
    if cmd.exitstatus != 0:
        log.debug("%s failed with exit status %d" % (argv[0], cmd.exitstatus))
        return None
    # Return output.
    return output
    

class MacOSXAuthenticator(object):
    """Authenticate Mac OS X users with dscl /Search -authonly."""
    
    def authenticate(self, environ, identity):
        # Read userid and password.
        try:
            userid = identity["login"]
            password = identity["password"]
        except KeyError:
            return None
        
        # Make sure the userid doesn't contain funny characters.
        if not valid_userid.match(userid):
            log.info("MacOSXAuthenticator failed with invalid userid")
            return None
        
        # Verify userid and password with dscl.
        dscl_cmd = pexpect.spawn("/usr/bin/dscl", ["/Search", "-authonly", userid])
        # Wait for the password prompt.
        dscl_cmd.waitnoecho()
        # Send the password.
        dscl_cmd.sendline(password)
        # Flush output.
        dscl_cmd.read()
        # Close the program.
        dscl_cmd.close()
        # Force close if it doesn't shutdown nicely.
        if dscl_cmd.isalive():
            dscl_cmd.close(force=True)
        # If dscl exited abnormally authorization failed.
        if dscl_cmd.signalstatus:
            log.info("MacOSXAuthenticator failed for %s as dscl exited with status %s" % (userid, str(dscl_cmd.signalstatus)))
            return None
        # An exit status different from 0 means authorization failed.
        if dscl_cmd.exitstatus != 0:
            log.info("MacOSXAuthenticator failed for %s" % (userid))
            return None
        
        # Success, return userid.
        log.info("MacOSXAuthenticator successfully authenticated %s" % userid)
        return userid
    

class MacOSXMetadataProvider(object):
    """Provide metadata for Mac OS X users."""
    
    metadata = {}
    
    def add_metadata(self, environ, identity):
        # Read userid.
        userid = identity.get("repoze.who.userid")
        
        # Make sure the userid doesn't contain funny characters.
        if not valid_userid.match(userid):
            return
        
        if userid in self.metadata:
            log.debug("Returning cached metadata for %s: %s" % (userid, repr(self.metadata[userid])))
            identity.update(self.metadata[userid])
            return
        
        self.metadata[userid] = {}
        
        log.debug("spawning dscl for %s" % userid)
        # Read display_name with dscl.
        dscl_cmd = pexpect.spawn("/usr/bin/dscl", ["/Search", "-read", "/Users/%s" % userid, "RealName"])
        # Read output.
        realname_output = dscl_cmd.read().decode("utf-8")
        # Close the program.
        dscl_cmd.close()
        # Force close if it doesn't shutdown nicely.
        if dscl_cmd.isalive():
            dscl_cmd.close(force=True)
        # If dscl exited abnormally we abort.
        if dscl_cmd.signalstatus:
            log.debug("dscl died for %s" % userid)
            return
        # An exit status different from 0 means the record couldn't re read.
        if dscl_cmd.exitstatus != 0:
            log.debug("RealName lookup with dscl failed for %s" % userid)
            return
        
        # If output doesn't match what we expect we abort.
        if not realname_output.startswith("RealName:"):
            log.debug("RealName lookup for %s returned unexpected result" % userid)
            return
        
        realname = realname_output.replace("RealName:", "").strip()
        log.debug("dscl returned RealName for %s: %s" % (userid, repr(realname)))
        self.metadata[userid]["display_name"] = realname
        identity.update({"display_name": realname})
    

class MacOSXGroupAdapter(BaseSourceAdapter):
    
    def __init__(self):
        self.groups = None
        super(MacOSXGroupAdapter, self).__init__(writable=False)
    
    def _get_all_sections(self):
        log.debug("spawning dscl to list all groups")
        dscl_output = get_output(["/usr/bin/dscl", "/Search", "-list", "/Groups"])
        if dscl_output is None:
            raise SourceError("Couldn't list groups with dscl")
        self.groups = dict([(group, None) for group in dscl_output.strip().split()])
        log.debug("dscl found %d groups" % len(self.groups))
        return self.groups
    
    def _get_section_items(self, section):
        log.debug("spawning dscl to get members of %s" % section)
        dscl_output = get_output(["/usr/bin/dscl", "/Search", "-read", "/Groups/%s" % section, "GroupMembership"])
        if dscl_output is None:
            raise SourceError("Couldn't read members of group %s with dscl" % section)
        if not dscl_output.startswith("GroupMembership:"):
            raise SourceError("Unexpected output when reading group members of %s with dscl" % section)
        return set(dscl_output.replace("GroupMembership:", "").strip().split())
    
    def _find_sections(self, credentials):
        log.debug("finding sections for credentials %s" % repr(credentials))
        userid = credentials['repoze.what.userid']
        
        log.debug("spawning id to read groups for %s" % userid)
        # Read group membership with id -Gn <username>
        group_output = get_output(["/usr/bin/id", "-Gn", userid])
        if group_output is None:
            return set()
            #raise SourceError("Couldn't read group membership for %s with id" % userid)
        groups = group_output.strip().split()
        log.debug("id returned groups for %s: %s" % (userid, repr(groups)))
        return set(groups)
    
    def _item_is_included(self, section, item):
        return item in self._get_section_items(section)
    
    def _section_exists(self, section):
        if self.groups is not None:
            return self.groups.has_key(section)
        else:
            self._get_all_sections()
            return self.groups.has_key(section)
    

if __name__ == '__main__':
    import sys
    
    g = MacOSXGroupAdapter()
    print repr(g._section_exists("admin"))
    print repr(g._get_section_items("admin"))
    
    sys.exit(0)
    
    import getpass
    
    a = MacOSXAuthenticator()
    md = MacOSXMetadataProvider()
    
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
    
    print "Authenticating chuck with norris"
    print "Result:", repr(a.authenticate({}, {"login": u"chuck", "password": u"norris"}))
    print "Authenticating chuck with hejsan"
    print "Result:", repr(a.authenticate({}, {"login": u"chuck", "password": u"hejsan"}))
    print "Authenticating authtest with hejsan99"
    print "Result:", repr(a.authenticate({}, {"login": u"authtest", "password": u"hejsan99"}))
    
    print "Getting metadata for chuck"
    identity = {"repoze.who.userid": "chuck"}
    md.add_metadata({}, identity)
    print "Result:", repr(identity)
    print "Getting metadata for authtest"
    identity = {"repoze.who.userid": "authtest"}
    md.add_metadata({}, identity)
    print "Result:", repr(identity)

