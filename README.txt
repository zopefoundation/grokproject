grokproject provides an easy way to get started with a `grok
<http://cheeseshop.python.org/pypi/grok>`_ web application.  Simply
install ``grokproject``::

  $ easy_install grokproject

and run the ``grokproject`` script with the name of the project you'd
like to create as an argument::

  $ grokproject MammothHerd
  ... many lines of output here

This will not only create a project area for you to work in, it will
also download and install grok and Zope 3 (the application server grok
is built on).

After the project area has been created successfully, you will find an
empty Python package in the ``src`` directory in which you can place
the code for your web application.  To start the Zope server, execute
``bin/zopectl fg``.

Changes
=======

0.5.1 (2007-07-14)
------------------

* Use the new 'application' recipe from zc.zope3recipes so that we can
  get rid of the dead chicken [zope3] section in buildout.cfg.

0.5 (2007-07-14)
----------------

* The bin/instance script has been renamed to bin/zopectl for better
  recognizability.

* grokproject is much quieter by default (by quieting down
  PasteScript, easy_install and zc.buildout).  Use the -v option for
  verbose mode.

* Fixed https://bugs.launchpad.net/grok/+bug/119805:
  A new project created with grokproject can't be called 'grok' or 'zope'.

* By default, zc.buildout will now be told to place eggs in a
  user-specified shared eggs directory.  Also, it will not look for
  newer versions of existing eggs by default.

0.4 (2007-07-12)
----------------

* As grok now depends on Zope 3.4 eggs, use zc.zope3recipes
  application and instance recipes.

* Don't spawn processes to bootstrap and run the buildout.  Instead,
  try to simply import zc.buildout.  If that doesn't work, call the
  setuptools API to install it and then simply import it.

* Fixed https://bugs.launchpad.net/grok/+bug/113103:
  Default index template was missing closing html tag.

0.1 thru 0.3
------------

Initial development versions, supporting Zope 3.3.
