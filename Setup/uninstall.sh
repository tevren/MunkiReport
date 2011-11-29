#!/bin/bash


if [ `id -u` -ne 0 ]; then
    echo "$0 must be run with sudo"
    exit 1
fi


if [ -f /Library/LaunchDaemons/com.googlecode.munkireport.plist ]; then
    launchctl unload -w /Library/LaunchDaemons/com.googlecode.munkireport.plist
fi
rm -f /Library/LaunchDaemons/com.googlecode.munkireport.plist
rm -rf /Library/MunkiReport
rm -rf /Library/PreferencePanes/MunkiReport.prefPane
dscl -f /var/db/dslocal/nodes/Default localonly -delete /Local/Target/Users/munkireport
pkgutil --forget com.googlecode.pkg.MunkiReport
#rm -rf "/Library/Application Support/MunkiReport"


exit 0
