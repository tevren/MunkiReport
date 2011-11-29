#!/bin/bash


if [ -z "$3" ]; then
    TARGET=""
else
    TARGET="$3"
fi

SHORTNAME="munkireport"
LONGNAME="MunkiReport"
HOME=/Library/MunkiReport
SHELL=/bin/bash
GID=20

DSNODE="${TARGET}/var/db/dslocal/nodes/Default"
DSCL="${TARGET}/usr/bin/dscl"
USERROOT="/Local/Target/Users"
USERPATH="$USERROOT/$SHORTNAME"


"$DSCL" -f "$DSNODE" localonly -read $USERROOT/$SHORTNAME UniqueID &> /dev/null
if [ $? -eq 0 ]; then
    echo "User munkireport already exists"
    exit 0
fi


STARTUID=501
STOPUID=600 
for (( uid=$STARTUID; uid<$STOPUID; uid++ )); do
	output=`"$DSCL" -f "$DSNODE" localonly -search $USERROOT UniqueID $uid`
	if [ "$output" == "" ]; then
		break
	fi
done
if [ $uid -eq $STOPUID ]; then
    echo "$STARTUID <= UID < $STOPUID not found"
    exit 1
fi

echo "Creating $USERPATH with name '$LONGNAME' gid $GID UniqueID $uid home $HOME in '$DSNODE'"
"$DSCL" -f "$DSNODE" localonly -create $USERPATH || exit 1
"$DSCL" -f "$DSNODE" localonly -create $USERPATH realname "$LONGNAME"
"$DSCL" -f "$DSNODE" localonly -create $USERPATH gid $GID
"$DSCL" -f "$DSNODE" localonly -create $USERPATH UniqueID $uid
"$DSCL" -f "$DSNODE" localonly -create $USERPATH home "$HOME"
"$DSCL" -f "$DSNODE" localonly -merge $USERPATH authentication_authority ";ShadowHash;"
"$DSCL" -f "$DSNODE" localonly -create $USERPATH passwd "*"
"$DSCL" -f "$DSNODE" localonly -create $USERPATH shell "$SHELL"


#/usr/bin/defaults write "${TARGET_DIR}/Library/Preferences/com.apple.loginwindow" HiddenUsersList -array-add $SHELL
