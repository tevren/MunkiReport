#!/bin/bash

SCRIPTDIR=`dirname "$0"`
MRDIR=`cd "$SCRIPTDIR/.."; pwd`
SUPPORTDIR="/Library/Application Support/MunkiReport"

# Change to application directory
cd "$MRDIR"

# Activate virtualenv
source "$MRDIR/Python/bin/activate"

echo
echo "*************************************************************************"
echo "******************* LIVE APPLICATION DATABASE ACCESS ********************"
echo "*************************************************************************"
echo
echo "from litsadmin.model import DBSession, Client"
echo "import transaction"
echo

paster --plugin=Pylons shell "$SUPPORTDIR/MunkiReport.ini"
