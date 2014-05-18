===============
interlex-export
===============

A command-line utility for converting Interlex' vocabulary files to a text format that is easier to process and import into other programs.

`Interlex`_ is a great program for learning foreign vocabulary.
Sadly, it's no longer actively maintained and does not provide any export feature.
Its file format is simple but binary and not widely supported, which is a significant obstacle in moving your vocabulary to a different application.

*interlex-export* lets you convert your ``.ilx`` files to ``.csv`` format which is easy to import into a spreadsheet or even directly into another application.

It has been created and tested with `Anki`_ in mind, though it's meant to be generic enough to be used with any application.

Status
======

At this point the project is of alpha-quality.
It's still at a very early stage of development.
It's not foolproof, lacks features, has not been extensively tested.
It may be hard to use it without knowing the source code.

If's likely to remain in that state unless there's some interest in it.
Feel free to submit a feature/improvement request through `Github Issues`_ if you find it useful.

The code has only been tested on Arch Linux, with files produced by Interlex 2.5.0.7.
It's likely but not guaranteed to work on Windows without any modifications.

Installation and usage
======================

Download the code, install PyPI packages listed in ``requirements.in`` and use ``--help`` command to see available options:

.. code-block:: bash

    python interlex_export.py --help

The script requires Python 3.

License
=======

Copyright © Kamil Śliwak

Released under the `MIT License`_.

.. _`Interlex`: http://www.vocab.co.uk
.. _`Anki`:  http://ankisrs.net
.. _`Github Issues`: https://github.com/cameel/interlex-export/issues
.. _`MIT License`: http://opensource.org/licenses/MIT
