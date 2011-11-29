# -*- coding: utf-8 -*-
"""Admin Controller"""

#from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.config import AdminConfig, CrudRestControllerConfig
#from tgext.admin.config import CrudRestControllerConfig
from sprox.formbase import EditableForm
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller
from repoze.what import predicates

from munkireport.model import Client

__all__ = ['MunkiReportAdminController']

class ClientForm(EditableForm):
    __model__ = Client
    __require_fields__     = ['id', 'name']
    __omit_fields__        = ['report_plist', 'activity']
    __field_order__        = ['id', 'name', 'mac', 'serial', 'console_user', 'div', 'manifest', 'remote_ip', 'timestamp']

class client(CrudRestControllerConfig):
    edit_form_type = ClientForm
    class table_type(TableBase):
        __entity__ = Client
        __omit_fields__  = ['report_plist', 'activity']
        __limit_fields__ = ['id', 'name', 'mac', 'serial', 'div', 'manifest', 'remote_ip', 'timestamp', 'console_user']
        __url__ = "../clients" # FIXME: pagination doesn't work

    class table_filler_type(TableFiller):
        __entity__ = Client
        __omit_fields__  = ['report_plist', 'activity']
        __limit_fields__ = ['id', 'name', 'mac', 'serial','div', 'manifest', 'remote_ip', 'timestamp', 'console_user']

class MunkiReportAdminController(AdminConfig):
    """Subclassing TGAdminConfig to override permissions."""
    allow_only = predicates.has_permission("admin", msg=u"Only available to users with admin permission.")
    client = client
