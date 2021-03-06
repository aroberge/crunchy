"""This plugin handles loading all pages not loaded by other plugins"""

import codecs
import sys
import traceback
from os.path import normpath, join, isdir, exists
from os import listdir

# All plugins should import the crunchy plugin API via interface.py
from src.interface import (
    translate, config, plugin, server, debug,
    debug_msg, preprocessor, python_version,
    crunchy_bytes, crunchy_unicode, unknown_user_name)
from src.utilities import meta_content_open, account_exists
import src.interface

_ = translate['_']

def register(): # tested
    '''registers a default http handler'''
    plugin['register_http_handler'](None, handler)

# the root of the server is in a separate directory:
root_path = join(config['crunchy_base_dir'], "server_root/")

def index(npath):
    """ Normalizes npath to an index.htm or index.html file if
    possible. Returns normalized path. """

    if not isdir(npath):
        return npath

    childs = listdir(npath)
    for i in ("index.htm", "index.html"):
        if i in childs:
            return join(npath, i)

    return npath

def path_to_filedata(path, root, username=None):
    """
    Given a path, finds the matching file and returns a read-only
    reference to it. If the path specifies a directory and does not
    have a trailing slash (ie. /example instead of /example/) this
    function will return none, the browser should then be redirected
    to the same path with a trailing /. Root is the fully qualified
    path to server root. Paths starting with / and containing .. will
    return an error message. POSIX version, should work in Windows.
    Data will be returned in encoded, non-Unicode form because the
    path could point to a binary file and is tailored for the
    request.wfile.write method.
    """
    # Path is guaranteed to be Unicode. See parse_headers in
    # http_serve.py for details.
    assert isinstance(path, crunchy_unicode)

    if path == server['exit']:
        server['server'].still_serving = False
        exit_file = join(root, "exit_en.html")

        f = open(exit_file, mode="rb")
        x = f.read()
        f.close()
        return x

    if path.startswith("/") and (path.find("/../") != -1):
        return error_page(path).encode('utf8')

    if path == "/null":
        return " "

    extension = path.split('.')[-1]

    if exists(path) and path != "/":
        npath = path
    # next, attempting to deal with the case where a css file imports another
    # one via something like @import "s5-core.css"
    # which slides by docutils do.
    elif extension == "css" and src.interface.last_local_base_url is not None:
        npath = normpath(join(src.interface.last_local_base_url, normpath(path[1:])))
        npath_normal = normpath(join(root, normpath(path[1:])))
    else:
        npath = normpath(join(root, normpath(path[1:])))

    npath = index(npath)

    if isdir(npath):
        if path[-1] != "/":
            return None
        return get_directory(npath, username).encode('utf8')

    try:
        creator = plugin['create_vlam_page']
        if extension in ["htm", "html"]:
            f = meta_content_open(npath)
            text = creator(f, path, username)
            f.close()
            text = text.read().encode('utf8')
            return text
        elif extension in preprocessor:
            f = preprocessor[extension](npath)
            text = creator(f, path, username)
            f.close()
            text = text.read().encode('utf8')
            return text

        if extension == 'css':
            try:
                f = open(npath, mode="rb")
            except: # reset
                f = open(npath_normal, mode="rb")
                src.interface.last_local_base_url = None
        else:
            # Note: we need binary mode because otherwise the file may not get
            # read properly on windows (e.g. for image files)
            f = open(npath, mode="rb")
        x = f.read()
        f.close()
        return x
    except IOError:
        print("In path_to_filedata, can not open path: " + npath)
        traceback.print_exc()
        return error_page(path).encode('utf8')

tell_Safari_page_is_html = False

def handler(request):
    """the actual handler"""
    global tell_Safari_page_is_html
    if debug['handle_default'] or debug['handle_default.handler']:
        debug_msg("--> entering handler() in handle_default.py")

    try:
        dummy = request.crunchy_username
    except:
        request.crunchy_username = unknown_user_name

    data = path_to_filedata(request.path, root_path, request.crunchy_username)
    if debug['handle_default'] or debug['handle_default.handler']:
        debug_msg("in handle_default.handler(), beginning of data =")
        try:
            d = data[0:80]
            if "\n" in d:
                d = d.split("\n")[0]
            debug_msg(d)
        except:
            debug_msg(data)
    if data == None:
        request.send_response(301)
        request.send_header("Location", request.path + "/")
        request.end_headers()
    else:
        request.send_response(200)
        # Tell Firefox not to cache; otherwise back button can bring back to
        # a page with a broken interpreter
        request.send_header('Cache-Control', 'no-cache, must-revalidate, no-store')
        # Set cookies only once per session.  In single user mode, this
        # will be used to prevent other users to access Crunchy.
        if 'session_cookie_set' not in plugin:
            request.send_header('Set-Cookie', plugin['session_random_id'])
            plugin['session_cookie_set'] = True
        if tell_Safari_page_is_html:
            request.send_header ("Content-Type", "text/html; charset=UTF-8")
            tell_Safari_page_is_html = False
        request.end_headers()
        # path_to_filedata guaranteed to return bytestrings.
        request.wfile.write(data)

def annotate(path, filenames): # tested
    '''Add '/' suffixes to directories in a directory listing'''
    fnames = []
    for name in filenames:
        if isdir(join(path, name)):
            fnames.append(name + '/')
        else:
            fnames.append(name)
    return fnames


def get_directory(npath, crunchy_username):
    '''gets a directory listing from a path or, if a default page, such as
    index.html, is found, gives that page instead.'''
    global tell_Safari_page_is_html
    childs = listdir(npath)
    childs = annotate(npath, childs)
    for i in ["index.htm", "index.html"]:
        if i in childs:
            tell_Safari_page_is_html = True
            return path_to_filedata("/"+i, npath, crunchy_username)
    tstring = []
    for child in childs:
        tstring.append( '<li><a href="%s">%s</a></li>' % (child, child) )
    tstring = ''.join(tstring)
    return dir_list_page % (_("Directory Listing"), tstring)

not_found = codecs.open(join(root_path, "404.html"), 'r', 'utf8').read()

dir_list_page = """
<html>
<head>
<title>
%s
</title>
</head>
<body>
<ul>
<li><a href="../">..</a></li>
%s
</ul>
</body>
</html>
"""

def error_page(path):
    '''returns a page with an error message; used when a path is not found'''
    return not_found % (path, path)
