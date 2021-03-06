utilities.py tests
==================


utilities.py is a module that contains the following functions, many of 
which are used by more than one module:

#. `uidgen()`_
#. `extract_log_id()`_
#. `trim_empty_lines_from_end()`_
#. `changeHTMLspecialCharacters()`_
#. `log_session()`_
#. `append_checkmark()`_
#. `append_warning()`_
#. `append_image()`_

We begin by importing the module.

    >>> import src.utilities as utilities
    >>> from src.interface import Element, SubElement

.. _`uidgen()`:

Testing uidgen()
-------------------

uidgen() generates a unique integer id (returned as a string).
The current implementation is such that consecutive integers are generated.

    >>> first = int(utilities.uidgen('dummy'))
    >>> second = int(utilities.uidgen('dummy'))
    >>> second - first
    1

.. _`extract_log_id()`:

Testing extract_log_id()
---------------------------

First, creating some test log id.
    >>> fake_id1 = "id"
    >>> fake_id2 = "id with space"
    >>> fake_id3 = "_id: with 8.66, _numbers123"

    >>> fake_vlam1 = "interpreter log_id=(%s)"%fake_id1
    >>> fake_vlam1a = "interpreter log_id = ( %s )"%fake_id1
    >>> fake_vlam2 = "interpreter log_id=(%s)"%fake_id2
    >>> fake_vlam2a = "interpreter log_id = ( %s )"%fake_id2
    >>> fake_vlam3 = "interpreter log_id=(%s)"%fake_id3
    >>> fake_vlam3a = "interpreter log_id = ( %s )  other = (dumb)"%fake_id3
    
Now, testing the extraction itself
    >>> print(fake_id1 == utilities.extract_log_id(fake_vlam1))
    True
    >>> print(fake_id1 == utilities.extract_log_id(fake_vlam1a))
    True
    >>> print(fake_id2 == utilities.extract_log_id(fake_vlam2))
    True
    >>> print(fake_id2 == utilities.extract_log_id(fake_vlam2a))
    True
    >>> print(fake_id3 == utilities.extract_log_id(fake_vlam3))
    True
    >>> print(fake_id3 == utilities.extract_log_id(fake_vlam3a))
    True

It's probably a good idea to check at some failing tests as well
    >>> print(fake_id2 == utilities.extract_log_id(fake_vlam1))
    False
    >>> print(utilities.extract_log_id("Move along, there is nothing here"))
    <BLANKLINE>

.. _`insert_file_browser()`:


Testing trim_empty_lines_from_end()
--------------------------------------


Define test data.

    >>> strip_none = "Hello, World!"
    >>> strip_top = "\nHello, World!"
    >>> strip_bottom = "Hello, World!\n"
    >>> strip_both = "\nHello, World!\n"
    >>> strip_mixed = "\nHello,\n\nWorld!\n"
    >>> strip_with_spaces = "   \nHello World!\n \r "

Carry out tests on test data, checking that results were correct.

	>>> print(utilities.trim_empty_lines_from_end(strip_none) == "Hello, World!")
	True
	>>> print(utilities.trim_empty_lines_from_end(strip_top) == "Hello, World!")
	True
	>>> print(utilities.trim_empty_lines_from_end(strip_bottom) == "Hello, World!")
	True
	>>> print(utilities.trim_empty_lines_from_end(strip_both) == "Hello, World!")
	True
	>>> print(utilities.trim_empty_lines_from_end(strip_mixed) == "Hello,\n\nWorld!")
	True
	>>> print(utilities.trim_empty_lines_from_end(strip_with_spaces) == "Hello World!")
	True

.. _`changeHTMLspecialCharacters()`:

Testing changeHTMLspecialCharacters()
----------------------------------------

Define tests and expected results.

	>>> html_lt_test = "Airspeed Velocity of Unladen African Swallow < Airspeed Velocity of Unladen European Swallow"
	>>> html_lt_result = "Airspeed Velocity of Unladen African Swallow &lt; Airspeed Velocity of Unladen European Swallow"
	>>> html_and_test = "Arthur & Patsy"
	>>> html_and_result = "Arthur &amp; Patsy"
	>>> html_gt_test = "Witch's Weight > Duck's Weight?"
	>>> html_gt_result = "Witch's Weight &gt; Duck's Weight?"
	>>> html_combo_test = "x < y && y > z"
	>>> html_combo_result = "x &lt; y &amp;&amp; y &gt; z"

Carry out tests
	>>> print(utilities.changeHTMLspecialCharacters(html_lt_test) == html_lt_result)
	True
	>>> print(utilities.changeHTMLspecialCharacters(html_and_test) == html_and_result)
	True
	>>> print(utilities.changeHTMLspecialCharacters(html_gt_test) == html_gt_result)
	True
	>>> print(utilities.changeHTMLspecialCharacters(html_combo_test) == html_combo_result)
	True

.. _`log_session()`:

Testing log_session()
------------------------

To do

.. _`append_checkmark()`:

Testing append_checkmark()
-----------------------------

To do.

.. _`append_warning()`:

Testing append_warning()
---------------------------

To do

.. _`append_image()`:

Testing append_image()
-------------------------

To do