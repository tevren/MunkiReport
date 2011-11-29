# -*- coding: utf-8 -*-
"""Sample model module."""
import re
from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, PickleType
#from sqlalchemy.orm import relation, backref

from munkireport.model import DeclarativeBase, metadata, DBSession

from datetime import datetime


class Client(DeclarativeBase):
    __tablename__ = 'client'
    
    #{ Columns
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    mac = Column(Unicode(17), nullable=False, unique=True)
    serial = Column(Unicode(64), nullable=False, unique=True)
    remote_ip = Column(Unicode(15))
    timestamp = Column(DateTime, default=datetime.now)
    runtype = Column(Unicode(64))
    runstate = Column(Unicode(16))	
    console_user = Column(Unicode(64))
    errors = Column(Integer, default=0)
    warnings = Column(Integer, default=0)
    activity = Column(PickleType(mutable=False))
    report_plist = Column(PickleType(mutable=False))
    div = Column(Unicode(64))
    manifest = Column(Unicode(64))
    
    #}
    
    def __repr__(self):
        return "<Client(%s)>" % ", ".join([repr(a) for a in
            (self.name, self.mac, self.serial, self.remote_ip, self.timestamp,
             self.runtype, self.runstate, self.console_user, self.div, self.manifest)])
    
    def update_report(self, plist):
        # Save plist.
        self.report_plist = plist
        
        if plist is None:
            self.activity = None
            self.errors = 0
            self.warnings = 0
            self.console_user = None
            return
        
        # Check activity.
        activity = dict()
        for section in ("ItemsToInstall",
                        "InstallResults",
                        "ItemsToRemove",
                        "RemovalResults",
                        "AppleUpdateList"):
            if (section in plist) and len(plist[section]):
                activity[section] = plist[section]
        if activity:
            self.activity = activity
        else:
            self.activity = None
        
        # Check errors and warnings.
        if "Errors" in plist:
            self.errors = len(plist["Errors"])
        else:
            self.errors = 0
        
        if "Warnings" in plist:
            self.warnings = len(plist["Warnings"])
        else:
            self.warnings = 0
        
        # Check console user.
        self.console_user = None
        if "ConsoleUser" in plist:
            if plist["ConsoleUser"] != "<None>":
                self.console_user = unicode(plist["ConsoleUser"])
                
    @classmethod
    def by_serial(c, serial):
        return DBSession.query(c).filter_by(serial=serial).first()
    
    def by_mac(c, mac):
        return DBSession.query(c).filter_by(mac=mac).first()

    def by_manifest(c, manifest):
        return DBSession.query(c).filter_by(manifest=manifest).first()
