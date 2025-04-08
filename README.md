Beautiful Soup Documentation
============================

[Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/) is a
Python library for pulling data out of HTML and XML files. It works
with your favorite parser to provide idiomatic ways of navigating,
searching, and modifying the parse tree. It commonly saves programmers
hours or days of work.

Installing Beautiful Soup

If you're using a recent version of Debian or Ubuntu Linux, you can
install Beautiful Soup with the system package manager:

    apt-get install python-bs4

Beautiful Soup 4 is published through PyPi, so if you can't install it
with the system package manager, you can install it with ``pip``. The
package name is ``beautifulsoup4``, and the same package works on both
Python 2 and Python 3.

    pip install beautifulsoup4

(The ``BeautifulSoup`` package is probably `not` what you want. That's
the previous major release, `Beautiful Soup 3`_. Lots of software uses
BS3, so it's still available, but if you're writing new code you
should install ``beautifulsoup4``.)

If you don't have ``easy_install`` or ``pip`` installed, you can
download the Beautiful Soup 4 source tarball
<http://www.crummy.com/software/BeautifulSoup/download/4.x/> and
install it with ``setup.py``.

    python setup.py install

If all else fails, the license for Beautiful Soup allows you to
package the entire library with your application. You can download the
tarball, copy its ``bs4`` directory into your application's codebase,
and use Beautiful Soup without installing it at all.

I use Python 2.7 and Python 3.2 to develop Beautiful Soup, but it
should work with other recent versions.
