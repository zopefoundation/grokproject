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

To start the Zope server, choose one of the two command schemes::

  - ``bin/zopectl fg``
  
    starts the twisted server
    
  - ``bin/paster serve etc/debug.ini``
  
    starts the pythonpaste http server with an interactive AJAX debugger enabled
    authentication: first access should go to http://localhost:8080/@@login.html
    
  - ``bin/paster serve etc/deploy.ini``
  
    starts the pythonpaste http server without error console
    
When using paster, automatic reloading after code changes can be enabled
by running::

  - ``bin/paster serve --reload etc/debug.ini``

For those who know paster: ``grokproject`` is just a wrapper around a
paster template.  So instead of running the ``grokproject`` command,
you can also run:

  $ paster create -t grok MammotHerd
  
