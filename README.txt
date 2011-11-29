MunkiReport
===========

MunkiReport gathers Munki reports from your clients, quickly showing you
errors and current activity on its front page, and lets you view details of
individual clients.


Requirements
------------

MunkiReport has been developed with system Python 2.6 on Mac OS X 10.6.

virtualenv is required, to avoid cluttering the system Python install with
modules. Install it with easy_install if needed:

    $ easy_install virtualenv

Of course you also have to be running Munki:

    http://code.google.com/p/munki/

The major.minor version number of MunkiReport matches that of the Munki
version it was developed against. E.g. if you're running Munki 0.7.0.980, a
MunkiReport version starting with 0.7 should work.


Installation
------------

Untar the distribution, cd to it, and run setup.sh. This will create a virtual
environment, install the MunkiReport module, create a config file, an admin
user (with permission to admin and view reports), and create an empty database.

    $ tar jxf MunkiReport-x.y.z.XXX.tar.bz2
    $ cd MunkiReport-x.y.z.XXX/
    $ ./setup.sh


Testing the server
------------------

Start the server with `./start.sh` and point your browser to
`http://your.external.ip.or.hostname:8444/` and you should be greeted with a
link to view reports. Click it and log in as the user you created during setup.
Distribute the reporting scripts to your clients (see below), do a munki run,
and their reports should start showing up.


Adding clients
--------------

Under `Scripts` you'll find preflight, postflight and report_broken_client
scripts. Edit the URL to point to your MunkiReport server. To wrap them in a
dmg for distribution, as MunkiScripts-1.0, run:

    $ ./make_script_dmg.sh 1.0

The resulting dmg and package info can be added to your Munki repository, and
your clients will automatically install the scripts and start submitting their
reports.


Adding a LaunchDaemon
---------------------

TODO: add launchd instructions.


Configuring logging
-------------------

TODO: add logging instructions.


Adding users, and using AD/OD
-----------------------------

By default, MunkiReport authenticates users against both the local `etc/users`
file, and with Directory Services. To add more local users, run:

    $ bin/mkuser.py

Open `etc/groups.ini` and add this user to the appropriate groups (admins can
admin the database, viewers can view reports).

You can also add regular Mac OS X users (including AD and OD users) to
`etc/groups.ini`.

You can also add a group of users to `etc/permissions.ini`. For example, if
your IT staff is in the active directory group APPLE\IT-staff, and you want
all of them to be able to view Munki reports, simply grant it [view]
permission:

    [admin]
    admins
    
    [view]
    viewers
    APPLE\IT-staff

TODO: verify that group names with backslash and space works.


LICENSE
-------

Copyright 2011 Per Olofsson, University of Gothenburg

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
