#!/bin/bash
#
# This is a work in progress and doesn't work.
# If you want to upgrade a dev snapshot, just activate the virtualenv and
# easy_install the new .egg.


# Don't perform upgrade if there's isn't a production database.
if [ ! -e var/db/production.db ]; then
    echo "MunkiReport database not found. Please run setup.sh if you're setting up"
    echo "MunkiReport for the first time."
    exit 1
fi


echo
echo "Checking requirements..."


# Make sure virtualenv is installed
echo -n "* Checking virtualenv"
which -s virtualenv
if [ $? -ne 0 ]; then
    echo " FAILED"
    echo "virtualenv is not installed, install with:"
    echo "easy_install virtualenv"
    exit 1
else
    echo " OK"
fi


# Check PyPI
echo -n "* Checking PyPI access"
PYPIURL="http://pypi.python.org/"
curl -s -f "$PYPIURL" > /dev/null
if [ $? -ne 0 ]; then
    echo " FAILED"
    echo "Can't reach $PYPIURL"
    exit 1
else
    echo " OK"
fi


# Check Python version
echo -n "* Checking Python version"
PYVER=`python -V 2>&1 | awk '{print $2}'`
PYMAJOR=`echo $PYVER | cut -d. -f1`
PYMINOR=`echo $PYVER | cut -d. -f2`
if [ $PYMAJOR -eq 2 -a $PYMINOR -gt 5 ]; then
    echo " OK"
else
    echo " FAILED"
    echo "Only Python 2.x version 2.6 or higher is supported"
    exit 1
fi


echo
echo "Setting up..."


# Activate virtualenv
echo "* Activating virtual environment"
source "$HOME/Library/Python/MunkiReportEnv/bin/activate"
if [ $? -ne 0 ]; then; echo "virtual environment activation failed"; exit 1; fi


# Stop LaunchDaemon
# FIXME: Not implemented yet.


# Install egg
echo "* Upgrading MunkiReport"
cat <<EOF

 *****************************************************************************
 **                                                                         **
 **          Updating required modules from http://pypi.python.org/         **
 **          This may take a while, please ignore any warnings.             **
 **                                                                         **
 *****************************************************************************

EOF
EGG=`ls *.egg | tail -1`
easy_install --upgrade --quiet "$EGG"
if [ $? -ne 0 ]; then
    echo
    echo "Install failed."
    exit 1
fi
cat <<EOF

 *****************************************************************************
 **                                                                         **
 **                            Modules installed.                           **
 **                                                                         **
 *****************************************************************************

EOF


# Apply schema changes to database
# FIXME: Not implemented yet, but no changes so far.


# Start LaunchDaemon
# FIXME: Not implemented yet.


# Done
echo
echo "Upgrade done. The server can be started with ./start.sh."
echo
