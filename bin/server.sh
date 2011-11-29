#!/bin/bash

echo "server.sh launching MunkiReport"

SCRIPTDIR=`dirname "$0"`
MRDIR=`cd "$SCRIPTDIR/.."; pwd`
SUPPORTDIR="/Library/Application Support/MunkiReport"

export PYTHON_EGG_CACHE="$SUPPORTDIR/Cache/.python-eggs"
if [ ! -d "$PYTHON_EGG_CACHE" ]; then
    mkdir -p "$PYTHON_EGG_CACHE"
fi

# Change to application directory
cd "$MRDIR"

# Check configuration
for INIFILE in groups.ini permissions.ini MunkiReport.ini; do
    if [ ! -f "$SUPPORTDIR/$INIFILE" ]; then
        echo "$SUPPORTDIR/$INIFILE does not exist"
        sleep 10
        exit 1
    fi
done

# Activate virtualenv
source "$MRDIR/Python/bin/activate"

# FIXME: Check actual DB path in ini file
if [ ! -e "$SUPPORTDIR/MunkiReport.db" ]; then
    echo "Creating database..."
    paster setup-app "$SUPPORTDIR/MunkiReport.ini"
fi

# Start web server
exec paster serve "$SUPPORTDIR/MunkiReport.ini"
