io_widget.py tests
================================

io_widget.py is a plugin which handles text and graphical IO
It has the following functions that require testing:

1. `register()`_
#. `kill_thread_handler()`_
#. `insert_io_subwidget()`_

0. Setting things up
--------------------

See how_to.rst_ for details.
Note that io_widget imports editarea.py which requires 
config['editarea_language'].

.. _how_to.rst: how_to.rst


    >>> from src.interface import plugin, config, Element
    >>> import src.interface
    >>> src.interface.crunchy_pygments = 'crunchy_pygments'
    >>> plugin.clear()
    >>> plugin['session_random_id'] = 42
    >>> config.clear()
    >>> config['Crunchy'] = {}
    >>> config['Crunchy']['editarea_language'] = 'en'


To do: we should have a test with the following set to True
    >>> config['Crunchy']['popups'] = False
    >>> import src.plugins.io_widget as io_widget
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> try:
    ...     import ctypes
    ...     config['ctypes_available'] = True
    ... except:
    ...     config['ctypes_available'] = False

We also need to define some mock functions and values.

    >>> site_security = {'trusted_url': 'trusted',
    ...                  'display_only_url': 'display normal'}
    >>> def get_security_level(url):
    ...     return site_security[url]
    >>> config['Crunchy']['page_security_level'] = get_security_level


.. _`register()`:

Testing register()
----------------------

    >>> io_widget.register()
    >>> mocks.registered_services['insert_io_subwidget'] == io_widget.insert_io_subwidget
    True

.. _`kill_thread_handler()`:

Testing kill_thread_handler()
-----------------------------

To do.

.. _`insert_io_subwidget()`:

Testing insert_io_subwidget()
--------------------------------

There are various options that we need to tests, depending on the page content.

a. Testing the display only option.
------------------------------------

We first consider the simplest possible case (in terms of information 
included by io_widget.py), that of a page that does not include an
interpreter and whose security level is such that we "display" only the
page, and no interactive element is included.

    >>> page = mocks.Page()
    >>> page.url = 'display_only_url'
    >>> elem = Element('parent')
    >>> uid = '42'
    >>> io_widget.insert_io_subwidget(page, elem, uid)

In this simplest case, two elements will have been included.
As a first crude test, we investigate to see if all the required elements 
have been inserted (and none unexpected).

    >>> spans = []
    >>> inputs = []
    >>> buttons = []
    >>> parent = []
    >>> divs = []
    >>> for el in elem.getiterator():
    ...     if el.tag == "parent":
    ...         parent.append(el)
    ...     elif el.tag == "div":
    ...         divs.append(el)
    ...     else:
    ...         print("Unexpected element found: " + str(el.tag))
    ...
    >>> len(parent)
    1
    >>> len(divs)
    2
    >>> page.added_info
    []

Next, we look at each elements in a bit more detail.

    >>> divs[0].attrib['class'] == "io_div crunchy_pygments"
    True
    >>> divs[1].attrib['class'] == "end_io_widget"
    True

b. Testing a non-Borg interpreter
----------------------------------

We now consider a page that does include an
interpreter and whose security level is such that we do more than
"display" only the page.

    >>> page = mocks.Page()
    >>> page.url = 'trusted_url'
    >>> elem = Element('parent')
    >>> uid = '42'
    >>> io_widget.insert_io_subwidget(page, elem, uid, interp_kind="Human")

In this simplest case, three elements will have been included.
As a first crude test, we investigate to see if all the required elements 
have been inserted (and none unexpected).

    >>> spans = []
    >>> inputs = []
    >>> imgs = []
    >>> textareas = []
    >>> a_s = []
    >>> parent = []
    >>> divs = []
    >>> for el in elem.getiterator():
    ...     if el.tag == "span":
    ...         spans.append(el)
    ...     elif el.tag == "input":
    ...         inputs.append(el)
    ...     elif el.tag == "parent":
    ...         parent.append(el)
    ...     elif el.tag == "a":
    ...         a_s.append(el)
    ...     elif el.tag == "img":
    ...         imgs.append(el)
    ...     elif el.tag == "textarea":
    ...         textareas.append(el)
    ...     elif el.tag == "div":
    ...         divs.append(el)
    ...     else:
    ...         print("Unexpected element found: " + str(el.tag))
    ...
    >>> len(spans)
    2
    >>> len(inputs)
    1
    >>> len(parent)
    1
    >>> if config['ctypes_available']:
    ...     print(len(a_s))
    ... else:
    ...     print(len(a_s) + 1)
    2
    >>> len(textareas)
    1
    >>> if config['ctypes_available']:
    ...     print(len(imgs))
    ... else:
    ...     print(len(imgs) + 1)
    2
    >>> len(divs)
    2

Note that we also need to check if the proper "includes" have been inserted.

    >>> page.added_info
    ['includes', ('add_include', 'io_included'), 'add_js_code', 'includes', ('add_include', 'push_input_included'), 'add_js_code', 'includes', ('add_include', 'editarea_included'), 'add_js_code', ('insert_js_file', '/edit_area/edit_area_crunchy.js')]

todo: we need to conclude this test as we did with the previous one, to check
the content of the new elements.

c. Testing with a Borg interpreter
------------------------------------

to do


Clean up
----------

    >>> del src.interface.crunchy_pygments
