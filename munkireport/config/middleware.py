# -*- coding: utf-8 -*-
"""WSGI middleware initialization for the munkireport application."""

from repoze.who.plugins.friendlyform import FriendlyFormPlugin
from repoze.who.interfaces import IIdentifier
from repoze.who.interfaces import IChallenger
from repoze.who.plugins.auth_tkt import make_plugin as AuthTktPlugin

from repoze.what.middleware import setup_auth
from repoze.what.plugins.ini import INIGroupAdapter, INIPermissionsAdapter

from munkireport.config.app_cfg import base_config
from munkireport.config.environment import load_environment

from munkireport.lib.macosxauth import MacOSXAuthenticator, MacOSXMetadataProvider, MacOSXGroupAdapter
from munkireport.lib.fileauth import FileAuthenticator, FileMetadataProvider


import os.path


__all__ = ['make_app']

# Use base_config to setup the necessary PasteDeploy application factory. 
# make_base_app will wrap the TG2 app with all the middleware it needs. 
make_base_app = base_config.setup_tg_wsgi_app(load_environment)


def make_app(global_conf, full_stack=True, **app_conf):
    """
    Set munkireport up with the settings found in the PasteDeploy configuration
    file used.
    
    :param global_conf: The global settings for munkireport (those
        defined under the ``[DEFAULT]`` section).
    :type global_conf: dict
    :param full_stack: Should the whole TG2 stack be set up?
    :type full_stack: str or bool
    :return: The munkireport application with all the relevant middleware
        loaded.
    
    This is the PasteDeploy factory for the munkireport application.
    
    ``app_conf`` contains all the application-specific settings (those defined
    under ``[app:main]``.
    
   
    """
    app = make_base_app(global_conf, full_stack=True, **app_conf)
    
    # Wrap your base TurboGears 2 application with custom middleware here
    
    # Initialize repoze.what plugins.
    groups_path = os.path.join(global_conf.get("appsupport_dir"), "groups.ini")
    groups = {
        "ini_groups": INIGroupAdapter(app_conf.get("what.groups_file", groups_path)),
        "dscl_groups": MacOSXGroupAdapter()
    }
    permissions_path = os.path.join(global_conf.get("appsupport_dir"), "permissions.ini")
    permissions = {
        "ini_permissions": INIPermissionsAdapter(app_conf.get("what.permissions_file", permissions_path))
    }
    
    # Initialize repoze.who plugins.
    friendlyform = FriendlyFormPlugin(
        "/login",
        "/login_handler",
        None,
        "/logout_handler",
        None,
        "auth_tkt",
        login_counter_name=None
    )
    friendlyform.classifications = {
        IIdentifier: ['browser'],
        IChallenger: ['browser']
    }
    auth_tkt = AuthTktPlugin(secret=app_conf["beaker.session.secret"])
    macosx_authenticator = MacOSXAuthenticator()
    macosx_metadataprovider = MacOSXMetadataProvider()
    file_authenticator = FileAuthenticator()
    file_metadataprovider = FileMetadataProvider()
    
    # Configuration for repoze.who.
    identifiers = [
        ('friendlyform', friendlyform),
        ('auth_tkt', auth_tkt)
    ]
    authenticators = [
        ('macosx_authenticator', macosx_authenticator),
        ('file_authenticator', file_authenticator)
    ]
    challengers = [
        ('friendlyform', friendlyform)
    ]
    mdproviders = [
        ('macosx_metadataprovider', macosx_metadataprovider),
        ('file_metadataprovider', file_metadataprovider)
    ]
    
    # Setup authentication and authorization through repoze.what.
    app = setup_auth(
        app,
        groups,
        permissions,
        identifiers=identifiers,
        authenticators=authenticators,
        challengers=challengers,
        mdproviders=mdproviders,
        #log_stream=sys.stdout,
        #log_level=logging.DEBUG
    )
    
    return app
