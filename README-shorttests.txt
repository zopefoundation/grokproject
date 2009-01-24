Shortening test runs
********************

By default testruns of `grokproject` take a huge amount of time.

This is primarily caused by eggs, which are downloaded and installed
in freshly created eggs directories during test runs. A complete set
of eggs is downloaded and installed at least two times during each
run.

Most time is taken by compiling and installing all the eggs.

We can reduce this large amount of time by skipping recreation of
eggs-directories between single tests and between test runs.

This can be forced by creating a file 'shorttests' in this directory,
which, if it exists, cares for leaving an existing eggs dir
untouched. You can create such a file like this::

  $ touch shorttests

Note, that the first run, however, will take much time but subsequent
runs will be much shorter (by factor 10 or more).

Before submitting to the repository you might want to run the 'full'
tests again, which can be done by removing the marker file::

  $ rm shorttests
