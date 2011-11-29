#!/bin/bash
#
# TODO: make this create a .pkg instead


SCRIPTDIR=`dirname "$0"`
SRCDIR=`cd "$SCRIPTDIR/.."; pwd`

cd "$SRCDIR"


# Check for virtualenv
if [ ! -z "$VIRTUAL_ENV" ]; then
    echo "Deactivate virtualenv before running this script."
    exit 1
fi


# Version
VERSION=`python -c 'import munkireport; print munkireport.__version__'`
SVNREV=`svnversion . | cut -d: -f2 | tr -cd '[:digit:]'`


# Build distribution egg
rm -rf build dist
python setup.py --quiet bdist_egg
if [ $? -ne 0 ]; then
    echo "Egg build failed"
    exit 1
fi
rm -rf build
rm -rf Paste*.egg


# Build PreferencePane
pushd "MunkiReportPrefPane" > /dev/null
/usr/bin/xcodebuild -project "MunkiReport.xcodeproj" -alltargets -configuration Release clean > /dev/null
/usr/bin/xcodebuild -project "MunkiReport.xcodeproj" -alltargets -configuration Release build > /dev/null
XCODEBUILD_RESULT="$?"
popd > /dev/null
if [ "$XCODEBUILD_RESULT" -ne 0 ]; then
    echo "Error building MunkiReport.xcodeproj: $XCODEBUILD_RESULT"
    exit 2
fi
if [ ! -e "MunkiReportPrefPane/build/Release/MunkiReport.prefPane" ]; then
    echo "Need a release build of MunkiReport.prefPane!"
    exit 2
fi


# Create pkg
sudo Setup/make_pkg.sh dist/*.egg "MunkiReportPrefPane/build/Release/MunkiReport.prefPane"
if [ $? -ne 0 ]; then
    echo "Package creation failed"
    exit 1
fi
gid=`id -g`
sudo chown ${UID}:${gid} dist/*.pkg


# Create distribution template
DISTDIR="dist/MunkiReport-$VERSION.$SVNREV"
mkdir "$DISTDIR"
mv dist/*.pkg "$DISTDIR/"
rsync -rlptC Scripts "$DISTDIR/"
cp README.txt LICENSE.txt "$DISTDIR/"
cp "$SCRIPTDIR/uninstall.sh" "$DISTDIR/"

# Clean up
find dist -name '.DS_Store' -exec rm {} \;
xattr -d -r com.apple.FinderInfo dist
xattr -d -r com.macromates.caret dist


# Create archive
(
    cd dist
    hdiutil create -srcfolder "MunkiReport-$VERSION.$SVNREV" -ov "MunkiReport-$VERSION.$SVNREV.dmg"
    #tar jcf "MunkiReport-$VERSION.$SVNREV.tar.bz2" "MunkiReport-$VERSION.$SVNREV"
)


# Done
open dist
