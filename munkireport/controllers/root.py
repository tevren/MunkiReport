# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect, abort
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController
from repoze.what import predicates


from munkireport.lib.base import BaseController
from munkireport.model import DBSession, metadata
from munkireport.controllers.error import ErrorController
from munkireport import model
from munkireport.controllers.admin import MunkiReportAdminController
from munkireport.controllers.update import UpdateController
from munkireport.controllers.view import ViewController
from munkireport.controllers.lookup import LookupController
from munkireport.lib.fileauth import get_users, create_file_users


__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the munkireport application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    update = UpdateController()
    view = ViewController()
    lookup = LookupController()
    
    admin = AdminController(model, DBSession, config_type=MunkiReportAdminController)
    
    error = ErrorController()

    @expose('munkireport.templates.index')
    def index(self):
        """Handle the front-page."""
        
        users = get_users()
        num_users = len(users)
        
        return dict(
            page='index',
            num_users=num_users
        )
    
    @expose('munkireport.templates.index')
    def reset_munkiadminadmin_password(self, password=None, password_verify=None):
        """Reset munkiadmin password."""
        
        if get_users():
            abort(403)
        
        if password != password_verify:
            abort(404)
        
        create_file_users("munkiadmin", "MunkiAdmin", password)
        flash(_("Created munkiadmin user"), "ok")
        
        return dict(
            page='index',
            num_users=len(get_users())
        )
    
    @expose('munkireport.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from='/'):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login', came_from=came_from, __logins=login_counter)
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
