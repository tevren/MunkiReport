# -*- coding: utf-8 -*-
"""Sample controller with all its actions protected."""
from tg import expose, flash, validate, abort
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
#from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
#from dbsprockets.saprovider import SAProvider

from formencode import validators

from munkireport.lib.base import BaseController
from munkireport.model import DBSession, Client

import re
import plistlib


__all__ = ['ViewController']


re_result = re.compile(r'^(Removal|Install) of (?P<dname>.+?)(-(?P<version>[^:]+))?: (?P<result>.*)$')


class ViewController(BaseController):
    """Gather client updates."""
    
    # The predicate that must be met for all the actions in this controller:
    allow_only = has_permission("view",
        msg=l_("Reports are only available for users with 'view' permission."))
    
    
    @expose()
    def error(self):
        abort(403)
    
    
    @expose('munkireport.templates.view.index')
    @validate(
        validators={
            "order_by": validators.OneOf((u"name", u"user", u"addr", u"mani", u"div", u"time")),
            "reverse": validators.StringBool(if_missing=True)
        },
        error_handler=error
    )
    def index(self, order_by=None, reverse=None):
        """Report overview."""
        if reverse is None:
            reverse = True
        if not order_by:
            order_by = u"time"
        sort_keys = {
            u"name": Client.name,
            u"user": Client.console_user,
            u"addr": Client.remote_ip,
            u"mani": Client.manifest,
            u"div": Client.div,
            u"time": Client.timestamp,
        }
        sort_key = sort_keys[order_by]
        error_clients=DBSession.query(Client).filter(Client.errors > 0).order_by(sort_key).all()
        warning_clients=DBSession.query(Client).filter(Client.errors == 0).filter(Client.warnings > 0).order_by(sort_key).all()
        activity_clients=DBSession.query(Client).filter(Client.activity != None).order_by(sort_key).all()
        if reverse:
            error_clients.reverse()
            warning_clients.reverse()
            activity_clients.reverse()
        return dict(
            page="reports",
            order_by=order_by,
            reverse=reverse,
            error_clients=error_clients,
            warning_clients=warning_clients,
            activity_clients=activity_clients
        )
    
    @expose('munkireport.templates.view.client_list')
    @validate(
        validators={
            "order_by": validators.OneOf((u"name", u"user", u"addr", u"div", u"mani", u"time")),
            "reverse": validators.StringBool(if_missing=True)
        },
        error_handler=error
    )
    def client_list(self, order_by=None, reverse=None):
        """List all clients."""
        if reverse is None:
            reverse = True
        if not order_by:
            order_by = u"time"
        sort_keys = {
            u"name": Client.name,
            u"user": Client.console_user,
            u"addr": Client.remote_ip,
            u"div":  Client.div,
            u"mani": Client.manifest,
            u"time": Client.timestamp,
        }
        sort_key = sort_keys[order_by]
        clients=DBSession.query(Client).order_by(sort_key).all()
        if reverse:
            clients.reverse()
        return dict(
            page="clients",
            order_by=order_by,
            reverse=reverse,
            clients=clients,
        )

    @expose('munkireport.templates.view.division_list')
    @validate(
        validators={
            "order_by": validators.OneOf((u"div")),
            "reverse": validators.StringBool(if_missing=True)
        },
        error_handler=error
    )
    def division_list(self, order_by=None, reverse=None):
        """List all Divisions."""
        if reverse is None:
            reverse = True
        if not order_by:
            order_by = u"div"
        sort_keys = {
            u"div":  Client.div,
        }
        divisions=DBSession.query(Client.div).distinct()
        return dict(
            page="divisions",
            divisions=divisions,
            order_by=order_by,
            reverse=reverse,
        )

    @expose('munkireport.templates.view.division')
    @validate(
        validators={
            "order_by": validators.OneOf((u"name", u"mani",u"user", u"addr", u"time")),
            "reverse": validators.StringBool(if_missing=True),
            "div": validators.UnicodeString(max=64, notempty=True)
        },
        error_handler=error
    )
    def division(self, div=None, order_by=None, reverse=None):
        """List all clients."""
        if reverse is None:
            reverse = True
        if not order_by:
            order_by = u"time"
        sort_keys = {
            u"name": Client.name,
            u"mani": Client.manifest,
            u"user": Client.console_user,
            u"addr": Client.remote_ip,
            u"time": Client.timestamp,
        }
        sort_key = sort_keys[order_by]
        clients=DBSession.query(Client).filter_by(div=div).order_by(sort_key).all()
        if reverse:
            clients.reverse()
        return dict(
            page="divisions",
            order_by=order_by,
            reverse=reverse,
            clients=clients,
        )

    @expose('munkireport.templates.view.manifest_list')
    @validate(
        validators={
            "order_by": validators.OneOf((u"mani")),
            "reverse": validators.StringBool(if_missing=True)
        },
        error_handler=error
    )
    def manifest_list(self, order_by=None, reverse=None):
        """List all manifests."""
        if reverse is None:
            reverse = True
        if not order_by:
            order_by = u"mani"
        sort_keys = {
            u"mani":  Client.manifest,
        }
        manifests=DBSession.query(Client.manifest).distinct()
        return dict(
            page="manifests",
            manifests=manifests,
            order_by=order_by,
            reverse=reverse,
        )

    @expose('munkireport.templates.view.manifest')
    @validate(
        validators={
            "order_by": validators.OneOf((u"name", u"div", u"user", u"addr", u"time")),
            "reverse": validators.StringBool(if_missing=True),
            "manifest": validators.UnicodeString(max=64, notempty=True)
        },
        error_handler=error
    )
    def manifest(self, manifest=None, order_by=None, reverse=None):
        """List all clients."""
        if reverse is None:
            reverse = True
        if not order_by:
            order_by = u"time"
        sort_keys = {
            u"name": Client.name,
            u"div": Client.div,
            u"user": Client.console_user,
            u"addr": Client.remote_ip,
            u"time": Client.timestamp,
        }
        sort_key = sort_keys[order_by]
        clients=DBSession.query(Client).filter_by(manifest=manifest).order_by(sort_key).all()
        if reverse:
            clients.reverse()
        return dict(
            page="manifests",
            order_by=order_by,
            reverse=reverse,
            clients=clients,
        )
    @expose(content_type="application/xml")
    @validate(
        validators={
            "serial":      validators.UnicodeString(max=64, notempty=True)
        },
        error_handler=error
    )
    def report_plist(self, serial=None):
        """View a munki report."""
        client=Client.by_serial(unicode(serial))
        if not client:
            abort(404)
        
        # Work with a copy of the client report so we can modify it without
        # causing a database update.
        report = dict(client.report_plist)
        return plistlib.writePlistToString(report)
    
    @expose('munkireport.templates.view.report')
    @validate(
        validators={
            "serial":      validators.UnicodeString(max=64, notempty=True)
        },
        error_handler=error
    )
    def report(self, serial=None):
        """View a munki report."""
        client=Client.by_serial(unicode(serial))
        if not client:
            abort(404)
        
        # Work with a copy of the client report so we can modify it without
        # causing a database update.
        report = dict(client.report_plist)
        
        # Move install results over to their install items.
        install_results = dict()
        if "InstallResults" in report:
            for result in report["InstallResults"]:
                if isinstance(result, basestring):
                    # Older Munki clients return an array of strings
                    m = re_result.search(result)
                    if m:
                        install_results["%s-%s" % (m.group("dname"), m.group("version"))] = {
                            "result": "Installed" if m.group("result") == "SUCCESSFUL" else m.group("result")
                        }
                else:
                    # Newer Munki clients return an array of dicts
                    install_results["%s-%s" % (result["name"], result["version"])] = {
                        "result": "Installed" if result["status"] == 0 else "error %d" % result["status"]
                    }
        if "ItemsToInstall" in report:
            for item in report["ItemsToInstall"]:
                item["install_result"] = "Pending"
                dversion = "%s-%s" % (item["display_name"], item["version_to_install"])
                if dversion in install_results:
                    res = install_results[dversion]
                    item["install_result"] = res["result"]
        if "AppleUpdateList" in report:
            for item in report["AppleUpdateList"]:
                item["install_result"] = "Pending"
                dversion = "%s-%s" % (item["display_name"], item["version_to_install"])
                if dversion in install_results:
                    res = install_results[dversion]
                    item["install_result"] = res["result"]
        
        # Move removal results over to their removal items.
        removal_results = dict()
        if "RemovalResults" in report:
            for result in report["RemovalResults"]:
                m = re_result.search(result)
                if m:
                    removal_results[m.group("dname")] = {
                        "result": "Removed" if m.group("result") == "SUCCESSFUL" else m.group("result")
                    }
        if "ItemsToRemove" in report:
            for item in report["ItemsToRemove"]:
                item["removal_result"] = "Pending"
                dversion = item["display_name"]
                if dversion in removal_results:
                    res = removal_results[dversion]
                    item["removal_result"] = res["result"]
        
        return dict(
            page="reports",
            client=client,
            report=report,
            install_results=install_results,
            removal_results=removal_results
        )
    
