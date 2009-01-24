# -*- coding: utf-8 -*-
"""
Grabs the tests in doctest

Taken virtually verbatim from zopeskel with permission (for zpl) from Tarek
Ziade. (c) Tarek Ziade
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest
import sys
import os
import shutil
import popen2
import StringIO

from zope.testing import doctest

current_dir = os.path.abspath(os.path.dirname(__file__))

def rmdir(*args):
    dirname = os.path.join(*args)
    if os.path.isdir(dirname):
        shutil.rmtree(dirname)

def read_sh(cmd):
    _cmd = cmd
    old = sys.stdout
    child_stdout_and_stderr, child_stdin = popen2.popen4(_cmd)
    child_stdin.close()
    return child_stdout_and_stderr.read()

def sh(cmd):
    _cmd = cmd
    print cmd
    # launch command 2 times to see what append and be able
    # to test in doc tests
    os.system(_cmd)
    child_stdout_and_stderr, child_stdin = popen2.popen4(_cmd)
    child_stdin.close()
    print child_stdout_and_stderr.read()

def ls(*args):
    dirname = os.path.join(*args)
    if os.path.isdir(dirname):
        filenames = os.listdir(dirname)
        for filename in sorted(filenames):
            print filename
    else:
        print 'No directory named %s' % dirname

def cd(*args):
    dirname = os.path.join(*args)
    os.chdir(dirname)


def config(filename):
    return os.path.join(current_dir, filename)

def cat(*args):
    filename = os.path.join(*args)
    if os.path.isfile(filename):
        print open(filename).read()
    else:
        print 'No file named %s' % filename

def touch(*args, **kwargs):
    filename = os.path.join(*args)
    open(filename, 'w').write(kwargs.get('data',''))

def shorttests(show_message=False):
    shorttestfile = os.path.join(
        os.path.dirname(__file__), 'shorttests')
    if not show_message:
        return os.path.exists(shorttestfile)
    if os.path.exists(shorttestfile):
        print
        print "WARNING: running shorttests."
        print "  This reduces the runtime of testruns by making use of"
        print "  a once filled eggs directory."
        print "  If you want clean test runs with an empty eggs directory,"
        print "  remove the file"
        print "    " + os.path.join(__file__, 'shorttests')
        print "  Running shorttests might lead to failing tests. Please run"
        print "  the full tests before submitting code."
        print
    else:
        print
        print "NOTE: running full tests."
        print "  If you want to reuse a prefilled eggs directory between"
        print "  test runs (which dramatically reduces runtime), create a"
        print "  file "
        print "    " + shorttestfile
        print "  and rerun the tests."
        print
    return os.path.exists(shorttestfile)

def maybe_mkdir(path):
    """Create a directory `path` conditionally.

    If the dir already exists and `shorttest()` is ``True`` we leave
    the directory untouched.

    Otherwise any old file/directory with path `path` is removed and
    recreated.
    """
    if shorttests() and os.path.isdir(path):
        return
    rmdir(path)
    os.makedirs(path)

def maybe_rmdir(path):
    """Remove a directory conditionally.

    If `shorttest()` is True, we do not remove the directory.
    """
    if shorttests() and os.path.isdir(path):
        return
    rmdir(path)
    

execdir = os.path.abspath(os.path.dirname(sys.executable))
tempdir = os.getenv('TEMP','/tmp')

def doc_suite(package_dir, setUp=None, tearDown=None, globs=None):
    """Returns a test suite, based on doctests found in /doctest."""
    suite = []
    if globs is None:
        globs = globals()

    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | 
             doctest.REPORT_ONLY_FIRST_FAILURE)

    if package_dir not in sys.path:
        sys.path.append(package_dir)

    docs = [os.path.join(package_dir, 'tests_zopectl.txt'),
            os.path.join(package_dir, 'tests_paste.txt'),
            ]

    for test in docs:
        suite.append(doctest.DocFileSuite(test, optionflags=flags,
                                          globs=globs, setUp=setUp,
                                          tearDown=tearDown,
                                          module_relative=False))

    return unittest.TestSuite(suite)

def test_suite():
    """returns the test suite"""
    short = shorttests(show_message=True)
    return doc_suite(current_dir)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
