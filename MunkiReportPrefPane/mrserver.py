#!/usr/bin/python
# encoding: utf-8
#
# MunkiReport
#
# Created by Per Olofsson on 2011-02-21.
# Copyright 2011 University of Gothenburg. All rights reserved.


import os
import sys
import optparse
import subprocess
import plistlib
import cStringIO


JOB = "com.googlecode.munkireport"
LAUNCHDAEMON_PATH = "/Library/LaunchDaemons/%s.plist" % JOB
APPSUPPORT_PATH = "/Library/Application Support/MunkiReport"
users_path = os.path.join(APPSUPPORT_PATH, "users.plist")
groups_path = os.path.join(APPSUPPORT_PATH, "groups.ini")


def enable(argv):
    """Enable and start server."""
    
    try:
        subprocess.check_call(["/bin/launchctl", "load", "-w", LAUNCHDAEMON_PATH])
    except subprocess.CalledProcessError as e:
        print >>sys.stderr, "LaunchDaemon load failed: %s" % e
        return 2
    return 0
    

def disable(argv):
    """Stop and disable server."""
    
    try:
        subprocess.check_call(["/bin/launchctl", "unload", "-w", LAUNCHDAEMON_PATH])
    except subprocess.CalledProcessError as e:
        print >>sys.stderr, "LaunchDaemon unload failed: %s" % e
        return 2
    return 0
    

def status(argv):
    """Display server status."""
    
    process = subprocess.Popen(["/bin/launchctl", "list", "-x", JOB],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output, error = process.communicate()
    retcode = process.poll()
    if process.poll():
        print "stopped"
        return 0
    # launchctl list -x outputs the plist to stderr.
    plist = plistlib.readPlistFromString(error)
    if "PID" in plist:
        print "running"
    elif plist.LastExitStatus == 0:
        print "stopped"
    else:
        print "error"
    return 0
    

def saveusers(argv):
    """Save stdin to users.plist."""
    
    try:
        plist = plistlib.readPlist(sys.stdin)
    except:
        print >>sys.stderr, "Malformed users.plist"
        return 2
    
    os.unlink(users_path)
    plistlib.writePlist(plist, users_path)
    
    return 0
    

def savegroups(argv):
    """Save stdin to groups.ini."""
    
    groups = sys.stdin.read()
    
    os.unlink(groups_path)
    with open(groups_path, "wb") as f:
        f.write(groups)
    
    return 0
    

def main(argv):
    actions = {
        u"enable": enable,
        u"disable": disable,
        u"status": status,
        u"saveusers": saveusers,
        u"savegroups": savegroups,
    }
    
    action_str = "\n".join(["    %-10s  %s" % (a, b.__doc__) for a, b in actions.items()])
    p = optparse.OptionParser()
    p.set_usage(u"""Usage: %prog action

Available actions:
""" + action_str + """

%prog must be run as root.""")
    options, argv = p.parse_args(argv)
    if len(argv) < 2:
        print >>sys.stderr, p.get_usage()
        return 1
    
    try:
        os.setuid(0)
    except OSError as e:
        print >>sys.stderr, u"Permission denied, must be run as root."
        return 1
    
    action = argv[1]
    
    if action in actions:
        return actions[action](argv[1:])
    else:
        print >>sys.stderr, u"Unknown action: %s\n" % action
        print >>sys.stderr, p.get_usage()
        return 1
    

if __name__ == '__main__':
    # Return stdout, stderr, and exit code as a plist on stdout as
    # AuthorizationExecuteWithPrivileges doesn't return stderr or the
    # exit code.
    org_stdout = sys.stdout
    org_stderr = sys.stderr
    
    my_stdout = cStringIO.StringIO()
    sys.stdout = my_stdout
    my_stderr = cStringIO.StringIO()
    sys.stderr = my_stderr
    my_exitcode = main(sys.argv)
    
    sys.stdout = org_stdout
    sys.stderr = org_stderr
    
    plistlib.writePlist(
        {
            "exitcode": my_exitcode,
            "stdout": my_stdout.getvalue(),
            "stderr": my_stderr.getvalue(),
        },
        sys.stdout,
    )
    
    sys.exit(0)
