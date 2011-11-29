#!/bin/bash


SCRIPTDIR=`dirname "$0"`
SRCDIR=`cd "$SCRIPTDIR/.."; pwd`
MRDIR="/Library/MunkiReport"
VENVDIR="$MRDIR/Python"
PKGID="com.googlecode.pkg.MunkiReport"

# Sanity checks.
if [ ! -x "/Developer/usr/bin/packagemaker" ]; then
    echo "PackageMaker is not installed!"
    exit 1
fi

if [ $(id -u) -ne 0 ]; then
    echo "Package creation needs to be run as root"
    exit
fi

if [ -z "$1" ]; then
    echo "Please provide .egg as argument"
    exit 1
else
    EGG="$1"
fi

if [ -z "$2" ]; then
    echo "Please provide .prefpane as argument"
    exit 1
else
    PREFPANE="$2"
fi

if [ -e "$MRDIR" ]; then
    echo "$MRDIR already exists"
    exit 1
fi


# Version
MRVERSION=`python -c 'import munkireport; print munkireport.__version__'`
SVNREV=`svnversion . | cut -d: -f2 | tr -cd '[:digit:]'`
VERSION="$MRVERSION.$SVNREV"

PKG="$SRCDIR/dist/MunkiReport-$VERSION.pkg"


# Create a PackageInfo.
makeinfo() {
    out="$1"
    id="$2"
    ver="$3"
    size="$4"
    nfiles="$5"
    restart="$6"
    if [ "$restart" == "restart" ]; then
        restart=' postinstall-action="restart"' # Leading space is important.
    else
        restart=""
    fi
    cat > "$out" <<EOF
<pkg-info format-version="2" identifier="$id" version="$ver" install-location="/" auth="root"$restart>
    <payload installKBytes="$size" numberOfFiles="$nfiles"/>
</pkg-info>
EOF
}


# Create directory structure.
mkdir "$MRDIR"
mkdir "$MRDIR"/Python
rsync -rlptC "$SRCDIR/bin" "$MRDIR/"
rsync -rlptC "$SRCDIR/Scripts" "$MRDIR/"

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
easy_install --quiet "$EGG"
if [ $? -ne 0 ]; then
    echo
    echo "Install failed."
    exit 1
fi

# Set modes.
find "$MRDIR" -print0 | xargs -0 chmod u+rw,go-w


# Pre-build cleanup.
rm -rf "$PKG"

# Create temporary directory
PKGTMP=`mktemp -d -t mrpkg`


echo "* Creating package template"


# Create directory structure.
PKGROOT="$PKGTMP/munkireport"
mkdir -m 1775 "$PKGROOT"
mkdir -m 1775 "$PKGROOT/Library"
mkdir -m 0755 "$PKGROOT/Library/LaunchDaemons"
mkdir -m 0755 "$PKGROOT/Library/PreferencePanes"
cp "$SCRIPTDIR/com.googlecode.munkireport.plist" "$PKGROOT/Library/LaunchDaemons"
ditto "$PREFPANE" "$PKGROOT/Library/PreferencePanes/MunkiReport.prefpane"

# Move MunkiReport into package root.
mv /Library/MunkiReport "$PKGROOT/Library"

# Copy ini file template.
cp "$SCRIPTDIR/MunkiReport.ini.template" "$PKGROOT/Library/MunkiReport"

# Create version.plist
cat > "$PKGROOT/Library/MunkiReport/version.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleShortVersionString</key>
	<string>$VERSION</string>
	<key>CFBundleVersion</key>
	<string>$VERSION</string>
	<key>CFBundleName</key>
	<string>MunkiReport</string>
</dict>
</plist>
EOF

# Create package info file.
PKGSIZE=`du -sk $PKGROOT | cut -f1`
NFILES=$(echo `find $PKGROOT/ | wc -l`)
makeinfo "$PKGTMP/info" "$PKGID" "$VERSION" $PKGSIZE $NFILES norestart

# Clean up
find "$PKGROOT" -name '.DS_Store' -exec rm {} \;
xattr -d -r com.apple.FinderInfo "$PKGROOT"
xattr -d -r com.macromates.caret "$PKGROOT"

# Set ownership.
chown -hR root:admin "$PKGROOT"
chown -hR root:wheel "$PKGROOT/Library/LaunchDaemons"


echo "* Packaging $PKG"
/Developer/usr/bin/packagemaker \
    --root "$PKGROOT" \
    --info "$PKGTMP/info" \
    --resources "$SCRIPTDIR/PkgTemplate/Resources" \
    --scripts "$SCRIPTDIR/PkgTemplate/Scripts" \
    --id "$PKGID" \
    --version "$VERSION" \
    --no-recommend \
    --no-relocate \
    --target 10.5 \
    --out "$PKG" \
    #--verbose


echo "* Removing temporary files..."
sudo rm -rf "$PKGTMP"

echo "Done."
