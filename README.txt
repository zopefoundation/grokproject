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
the code for your web application.  

To start the application server, execute::

  $ cd MammothHerd
  $ bin/paster serve etc/deploy.ini
  
There is also an Ajax enabled debugger 
(point your browser to http://localhost:8080/@@login.html when using this)::

  $ bin/paster serve etc/debug.ini
  
Start/stop it in daemon mode::

  $ bin/mammothherd-ctl start
  $ bin/mammothherd-ctl stop
  
Start the debugger::

  $ bin/mammothherd-debug

For those who know paster: ``grokproject`` is just a wrapper around a
paster template.  So instead of running the ``grokproject`` command,
you can also run::

  $ paster create -t grok MammotHerd

To create a project with the previous ``zopectl`` layout run the ``grokproject`` 
script like::

  $ grokproject --zopectl MammothHerd

or::

  $ paster create -t grok MammothHerd zopectl=True

