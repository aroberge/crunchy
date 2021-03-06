#!/usr/bin/env python
# encoding: utf-8
"""
build_release.py

Created by Johannes Woolard on 2008-04-14.
"""

import sys
from subprocess import call

import pysvn

help_message = '''build_release.py
Usage: python build_release version targets

targets should be a space separated list. If no target is given, then the source will be downloaded
but no targets will be built. The following targets are currently supported:
 * zip
 * tar.gz

Run this from an empty directory - it will download the appropriate release version from
http://crunchy.googlecode.com/svn/tags/'version' (where version is the version given as
an argument to te command).

IMPORTANT: Always run this from an empty directory.

Final release files will end up in the curent working directory.

This script relies on pysvn from http://pysvn.tigris.org/
'''


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) < 2:
        sys.stderr.write(help_message)
        return 2
    version = argv[1]
    print "Creating dist packages for Crunchy, version %s" % version
    
    print "Exporting dist from http://crunchy.googlecode.com/svn/tags/%s" % version
    client = pysvn.Client()
    revision = client.export("http://crunchy.googlecode.com/svn/tags/%s" % version, 
                                "./crunchy-%s"%version)
    print "Successfully exported revision %s from http://crunchy.googlecode.com/svn/tags/%s" % \
                                (revision.number, version)
    
    if "zip" in argv:
        create_zip(version)
    
    if "tar.gz" in argv:
        create_targz(version)
    
    #this doesn't work yet :(
    if "mac" in argv:
        build_mac_app(version)
        
    if "deb" in argv:
        print "deb file creation not currently supported"
        
    if "rpm" in argv:
        print "rpm file creation not currently supported"
        
    if "py2exe" in argv:
        print "py2exe not currently supported"
        
    if "nsis" in argv:
        print "nsis not currently supported"
        
    if "msi" in argv:
        print "msi file creation not currently supported"
    
    return 0

def create_zip(version):
    print "Creating crunchy-%s.zip" % version
    retcode = call(["/usr/bin/zip", "-q", "-r", "crunchy-%s.zip" % version, "crunchy-%s" % version])
    if retcode == 0:
        print "zip file succesfully created"
    else:
        raise "zip returned error code %s" % retcode

def create_targz(version):
    print "Creating crunchy-%s.tar.gz" % version
    retcode = call(["/usr/bin/tar", "-czf", "crunchy-%s.tar.gz" % version, "crunchy-%s/" % version])
    if retcode == 0:
        print "tar.gz file succesfully created"
    else:
        raise "tar returned error code %s" % retcode
        
def build_mac_app(version):
    print "Creating setup.py for OSX .app"
    f = open("setup.py", 'w')
    f.write("""
from setuptools import setup

APP = ['crunchy-%s/crunchy.py']
DATA_FILES = ['crunchy-%s/translations',
 'crunchy-%s/server_root',
 'crunchy-%s/LICENSE.txt',
 'crunchy-%s/src/plugins']
OPTIONS = {'argv_emulation': True}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
    """ % (version, version, version, version, version))
    f.close()
    print "Created setup.py, running py2app"
    retcode = call(["/usr/bin/python", "setup.py", "py2app", "-s"])
    if retcode == 0:
        print ".app file succesfully created - you will have to put it into a .dmg manually"
    else:
        raise ("py2app returned error code %s" % retcode)
    
    
if __name__ == "__main__":
    sys.exit(main())
