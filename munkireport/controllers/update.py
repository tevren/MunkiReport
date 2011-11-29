# -*- coding: utf-8 -*-
"""Sample controller with all its actions protected."""
from tg import expose, flash, request, abort, validate
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
#from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
#from dbsprockets.saprovider import SAProvider

from formencode import validators

from munkireport.lib.base import BaseController
from munkireport.model import DBSession, Client

from datetime import datetime
import sys
sys.path.append("/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/PyObjC")
#from Foundation import NSData, NSPropertyListSerialization, NSPropertyListMutableContainers
import plistlib
import base64
import bz2
import pprint


__all__ = ['UpdateController']


class UpdateController(BaseController):
    """Gather client updates."""
    
    # The predicate that must be met for all the actions in this controller:
    #allow_only = has_permission("report",
    #   msg=l_("Only users with the 'report' permission can submit report updates."))
    
    @expose()
    def index(self):
        abort(403)
    
    
    @expose(content_type="text/plain")
    @validate(validators={
        "runtype":  validators.UnicodeString(max=64, notempty=True),
        "mac":      validators.MACAddress(add_colons=True, notempty=True),
        "name":     validators.UnicodeString(max=64, notempty=True),
        "serial":   validators.UnicodeString(max=64, notempty=True)
    })
    def report_broken_client(self, runtype=None, mac=None, name=None):
        """Log report_broken_client."""

        client = Client.by_serial(serial)
        if not client:
            client = Client()
            client.serial = serial
            DBSession.add(client)
        
        client.runtype = runtype
        client.name = name
        client.mac = mac
        client.runstate = u"broken client"
        client.timestamp = datetime.now()
        client.remote_ip = unicode(request.environ['REMOTE_ADDR'])
        client.report_plist = None
        client.errors = 1
        client.warnings = 0
        
        DBSession.flush()
        
        return "report_broken_client logged for %s\n" % (name, remote_ip)
    
    
    @expose(content_type="text/plain")
    @validate(validators={
        "runtype":  validators.UnicodeString(max=64, notempty=True),
        "mac":      validators.MACAddress(add_colons=True, notempty=True),
        "name":     validators.UnicodeString(max=64, notempty=True),
        "serial":   validators.UnicodeString(max=64, notempty=True),
        "manifest": validators.UnicodeString(max=64, notempty=True)
    })
    def preflight(self, runtype=None, mac=None, name=None, serial=None, manifest=None):
        """Log preflight."""

        client = Client.by_serial(serial)
        if not client:
            client = Client()
            client.serial = serial
            DBSession.add(client)
        
        client.runtype = runtype
        if name:
            client.name = name
        else:
            client.name = "<NO NAME>"
        client.mac = mac
        client.manifest = manifest
        client.runstate = u"in progress"
        client.timestamp = datetime.now()
        client.remote_ip = unicode(request.environ['REMOTE_ADDR'])
        client.activity = {"Updating": "preflight"}
        
        DBSession.flush()
        
        return "preflight logged for %s\n" % name
    
    
    @expose(content_type="text/plain")
    @validate(validators={
        "runtype":          validators.UnicodeString(max=64, notempty=True),
        "mac":              validators.MACAddress(add_colons=True, notempty=True),
        "name":             validators.UnicodeString(max=64, notempty=True),
        "serial":	    validators.UnicodeString(max=64, notempty=True),
        "manifest":         validators.UnicodeString(max=64, notempty=True),
        "base64bz2report":  validators.UnicodeString(max=200000, notempty=True)
    })
    def postflight(self, runtype=None, mac=None, name=None, serial=None, manifest=None, base64bz2report=None):
        """Log postflight."""
        
        # Decode report
        # FIXME: there has to be a better way to submit a binary blob
        try:
            base64bz2report = base64bz2report.replace(" ", "+")
            bz2report = base64.b64decode(base64bz2report)
            report = bz2.decompress(bz2report)
        except BaseException as e:
            print "Can't decode report from %s (%s): %s" % (request.environ['REMOTE_ADDR'], mac, str(e))
            abort(403)
        
        # Parse plist with plistlib, as Objective-C objects can't be pickled.
        try:
            plist = plistlib.readPlistFromString(report)
        except BaseException as e:
            print "Received invalid plist from %s (%s): %s" % (request.environ['REMOTE_ADDR'], mac, str(e))
            abort(403)
        #plist, format, error = \
        #    NSPropertyListSerialization.propertyListFromData_mutabilityOption_format_errorDescription_(
        #        buffer(report),
        #        NSPropertyListMutableContainers,
        #        None,
        #        None
        #    )
        #if error:
        #    print "error:", error
        #    abort(401)
        
        # Create client if needed.
        client = Client.by_serial(serial)
        if not client:
            print "postflight running without preflight for %s" % mac
            client = Client()
            client.serial = serial
            DBSession.add(client)
        
        # Update client attributes.
        client.runtype = runtype
        if name:
            client.name = name
        else:
            client.name = "<NO NAME>"

        # Get manifest id from plist
        client.mac = mac
        client.manifest = manifest
        client.runstate = u"done"
        client.timestamp = datetime.now()
        client.remote_ip = unicode(request.environ['REMOTE_ADDR'])
        # Save report, updating activity, errors, warnings, and console_user.
        client.update_report(plist)
                
        DBSession.flush()
        
        return "postflight logged for %s\n" % name
        
