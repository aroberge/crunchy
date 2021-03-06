﻿interface.py tests
==================

Note: this file is encoded in utf-8.

interface.py contains various functions whose definitions are dependent on the
Python version being used, but provided to the user in a totally transparent way.

    >>> import src.interface as interface
    >>> interface.config.clear()
    >>> interface.plugin.clear()
    >>> from os import getcwd
    >>> interface.config['crunchy_base_dir'] = getcwd()


Testing ElementTree and friends
-------------------------------

The following is incomplete.

    >>> elem = interface.Element("p")
    >>> elem.attrib['class'] = 'crunchy'
    >>> elem.text = "This is a neat sentence."
    >>> interface.u_print(interface.tostring(elem))
    <p class="crunchy">This is a neat sentence.</p>

We create a fake html file  -- WARNING: this test is currently useless

    >>> html_content = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    ... "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    ... <html>
    ... <head>
    ... <title>Crunchy fun</title>
    ... </head>
    ... <body>
    ... <p>This is some text.</p>
    ... </body>
    ... </html>"""
    >>> fake_file = interface.StringIO()
    >>> dummy = fake_file.write(html_content) # return value in Py3k
    >>> dummy = fake_file.seek(0)  # return value in Py3k
    >>> #tree = interface.parse(fake_file)

Testing exec_code()
-------------------

Whereas exec used to be a statement, in Python 3000 it is now a function.
So, just like for print, we need to give a transparent access to the right version.

    >>> def double(n):
    ...     return 2*n
    ...
    >>> locals = {'double': double, 'interface': interface}
    >>> test_code = "a = double(21)\ninterface.u_print(str(a))"
    >>> interface.exec_code(test_code, locals)
    42
