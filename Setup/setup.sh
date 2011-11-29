#!/bin/bash


# Don't perform setup if there's already a production database.
if [ -e var/db/production.db ]; then
    echo "A production database already exists. Please refer to the documentation if you"
    echo "are upgrading to a new version."
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


# Create virtualenv
if [ ! -d "$HOME/Library/Python/MunkiReportEnv" ]; then
    echo "* Creating virtual environment"
    mkdir -p "$HOME/Library/Python"
    (
        cd "$HOME/Library/Python"
        virtualenv --no-site-packages -p python2.6 MunkiReportEnv
        if [ $? -ne 0 ]; then echo "virtual environment creation failed"; exit 1; fi
    )
fi
echo "* Activating virtual environment"
source "$HOME/Library/Python/MunkiReportEnv/bin/activate"
if [ $? -ne 0 ]; then echo "virtual environment activation failed"; exit 1; fi


# Install egg
echo "* Installing MunkiReport into virtual environment"
cat <<EOF

 *****************************************************************************
 **                                                                         **
 **         Installing required modules from http://pypi.python.org/        **
 **         This may take a while, please ignore any warnings.              **
 **                                                                         **
 *****************************************************************************

EOF
EGG=`ls *.egg | tail -1`
easy_install --quiet "$EGG"
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


# Create production.ini
echo "* Creating etc/production.ini"
perl -e '
    use IO::Socket::INET;
    $uuid = `uuidgen`;
    foreach $line (<>) {
        $line =~ s/^#(.+)SET SECRET STRING HERE/$1$uuid/;
        print $line
    }
' < etc/production.ini.template > etc/production.ini && rm etc/production.ini.template


# Create users
echo "* Creating munkireport admin user"
bin/mkuser.py
if [ $? -ne 0 ]; then
    echo "User creation failed"
    exit 1
fi
USERNAME=`cut -d: -f1 etc/users | head -1`


# Create groups.ini
echo "* Creating etc/groups.ini"
echo "Adding $USERNAME to admins and viewers"
cat > etc/groups.ini <<EOF
[admins]
$USERNAME

[viewers]
$USERNAME
EOF


# Initialize application
echo
echo "Creating database..."
paster setup-app etc/production.ini


# Done
echo
echo "Setup done. The server can be started with ./start.sh."
echo
