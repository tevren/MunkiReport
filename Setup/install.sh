#!/bin/bash
#
# Quick and dirty install script for development testing.


if [ -z "$3" ]; then
    TARGET=""
else
    TARGET="$3"
fi


SCRIPTDIR=`dirname "$0"`
SRCDIR=`cd "$SCRIPTDIR/.."; pwd`
MRDIR="/Library/MunkiReport"
VENVDIR="$MRDIR/Python"
SUPPORTDIR="/Library/Application Support/MunkiReport"


if [ `id -u` -ne 0 ]; then
    echo "Run as root"
    exit 1
fi

DSNODE="${TARGET}/var/db/dslocal/nodes/Default"
DSCL="${TARGET}/usr/bin/dscl"
# MRUSER=`"$DSCL" -f "$DSNODE" localonly -read /Local/Target/Users/munkireport UniqueID`
id -u munkireport &> /dev/null
if [ $? -ne 0 ]; then
    echo "munkireport user does not exist"
    exit
fi

if [ -e "$MRDIR" ]; then
    echo "$MRDIR already exists"
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "Provide .egg to install as argument"
    exit 1
fi


mkdir "$MRDIR"
mkdir "$MRDIR"/Python
rsync -rlptC "$SRCDIR/bin" "$MRDIR/"
rsync -rlptC "$SRCDIR/Scripts" "$MRDIR/"
mkdir -p "$SUPPORTDIR"
mkdir -p "$SUPPORTDIR"/Cache
mkdir -p "$SUPPORTDIR"/Logs


# Create virtualenv
echo "* Creating virtual environment"
(
    cd "$MRDIR"
    virtualenv --no-site-packages -p python2.6 `basename "$VENVDIR"`
    if [ $? -ne 0 ]; then echo "virtual environment creation failed"; exit 1; fi
)
echo "* Activating virtual environment"
source "$VENVDIR/bin/activate"
if [ $? -ne 0 ]; then echo "virtual environment activation failed"; exit 1; fi


# Install egg
echo "* Installing MunkiReport into virtual environment"
EGG="$1"
easy_install --quiet "$EGG"
if [ $? -ne 0 ]; then
    echo
    echo "Install failed."
    exit 1
fi


# Create users, groups, and permissions
cat > "$SUPPORTDIR/permissions.ini" <<EOF
[admin]
admins

[view]
viewers
EOF

cat > "$SUPPORTDIR/groups.ini" <<EOF
[admins]
munkiadmin

[viewers]
munkiadmin
EOF

cat > "$SUPPORTDIR/users" <<EOF
munkiadmin:Munki Administrator:7451df44cffe637e9e899881a9c2197bee3b8d63994d7ddbd7f9d631d0e3278b
EOF


# Create production.ini
echo "* Creating $SUPPORTDIR/production.ini"
perl -e '
    $uuid = `uuidgen`;
    foreach $line (<>) {
        $line =~ s/^#(.+)SET SECRET STRING HERE/$1$uuid/;
        print $line
    }
' < "$SRCDIR/etc/production.ini.template" > "$SUPPORTDIR/MunkiReport.ini"


# Initialize application
if [ ! -e "$SUPPORTDIR/MunkiReport.db" ]; then
    echo
    echo "Creating database..."
    (
        cd "$MRDIR"
        paster setup-app "$SUPPORTDIR/MunkiReport.ini"
    )
else
    echo
    echo "Database already exists"
    # TODO: schema changes
fi


# Setting ownership
chown -hR root:admin "$MRDIR"
find "$MRDIR" -print0 | xargs -0 chmod u+rw,go-w
chown -hR munkireport:admin "$SUPPORTDIR"
find "$SUPPORTDIR" -print0 | xargs -0 chmod ug+rw,o-w
