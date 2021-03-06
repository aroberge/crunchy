doc_code_check.py tests
================================


doc_code_check.py has the following methods that need to be tested:

1. `register()`_
#. `all_code_samples_check_callback()`_
#. `doc_code_check_callback()`_
#. `do_single_test()`_
#. `code_setup_process()`_
#. `code_sample_process()`_
#. `expected_output_process()`_
#. `insert_comprehensive_test_button()`_
#. `run_sample()`_
#. `compare()`_
#. `extract_name()`_
#. `MockPageInfo.dummy_pageid()`_
#. `MockPageInfo.dummy_uid()`_
#. `MockPageInfo.set()`_
#. `MockPageInfo.restore()`_


Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

    >>> from src.interface import plugin, config
    >>> plugin.clear()
    >>> config.clear()
    >>> from os import getcwd
    >>> config['crunchy_base_dir'] = getcwd()
    >>> import src.plugins.doc_code_check as dcc

.. _`compare()`:

Testing compare()
--------------------

compare() is a function used to compare two strings.  In order to test
it, we need to set up a few cases.

    >>> test1 = """This is a short test."""
    >>> test2 = """This is a short test too."""
    >>> test3 = """This is a much longer test
    ... that spans multiple lines
    ... with some meaningless dribble."""
    >>> test4 = test3 + " Yes, it is."
    >>> print(dcc.compare(test1, test1))
    Checked!
    >>> print(dcc.compare(test1, test2))
    - This is a short test.
    + This is a short test too.
    ?                     ++++
    <BLANKLINE>
    >>> print(dcc.compare(test3, test3))
    Checked!
    >>> print(dcc.compare(test3, test4))
      This is a much longer test
      that spans multiple lines
    - with some meaningless dribble.
    + with some meaningless dribble. Yes, it is.
    ?                               ++++++++++++
    <BLANKLINE>

.. _`run_sample()`:

Testing run_sample()
-----------------------

First, we create a simple example.

    >>> dcc.code_setups['1'] = "a = 1"
    >>> dcc.code_samples['1'] = "print(a)"
    >>> dcc.expected_outputs['1'] = "1\n"
    >>> dcc.run_sample('1')
    'Checked!'

A second example with no setup code.

    >>> dcc.code_samples['2'] = "print(1)"
    >>> dcc.expected_outputs['2'] = "1\n"
    >>> dcc.run_sample('2')
    'Checked!'


.. _`extract_name()`:

Testing extract_name()
-------------------------

    >>> s1 = "junk name=some_name1 ok"
    >>> print(dcc.extract_name(s1))
    some_name1

Same example as s1 but with spaces on each side of the equal sign.
    >>> s2 = "junk name  =  some_name2 ok"
    >>> print(dcc.extract_name(s2))
    some_name2

Same example as s2 but with other equal signs.
    >>> s3 = "junk name  =  some_name3 ok= not"
    >>> print(dcc.extract_name(s3))
    some_name3


# Test - check that the two http_handlers have been registered
