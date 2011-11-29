#!/usr/bin/env python


import os
import sys
import pickle

try:
    from munkireport.model import DBSession, Client
except ImportError:
    activate_this = "/Library/MunkiReport/Python/bin/activate_this.py"
    execfile(activate_this, dict(__file__=activate_this))
    from munkireport.model import DBSession, Client

import sqlalchemy


def usage():
    print "Usage: dump_db.py database.db dest_dir"
    

def main(argv):
    try:
        dbpath = argv[1]
        dest_dir = argv[2]
    except IndexError:
        usage()
        return 1
    
    try:
        engine = sqlalchemy.create_engine('sqlite:///%s' % dbpath)
        DBSession.configure(bind=engine)
    except BaseException as e:
        print >>sys.stderr, "Couldn't open sqlite database %s: %s" % (dbpath, e)
    
    if not os.path.exists(dest_dir):
        try:
            os.makedirs(dest_dir)
        except BaseException as e:
            print >>sys.stderr, "Couldn't create dump directory %s: %s" % (dest_dir, e)
            return 2
    
    for client in DBSession.query(Client).all():
        print "%d %s %s %s" % (client.id, client.name, client.mac, client.remote_ip)
        c = dict()
        for prop in dir(Client):
            attr = getattr(Client, prop)
            if isinstance(attr, sqlalchemy.orm.attributes.InstrumentedAttribute):
                c[prop] = getattr(client, prop)
        with open("%s/%s.pickle" % (dest_dir, client.mac), "wb") as f:
            pickle.dump(c, f, pickle.HIGHEST_PROTOCOL)
    
    return 0
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
    
