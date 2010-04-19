# -*- coding: utf-8 -*-
"""
Grabs the tests in doctest

Previously Taken virtually verbatim from zopeskel with permission (for ZPL)
from Tarek Ziade. (c) Tarek Ziade
"""
__docformat__ = 'restructuredtext'

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from zope.testing import doctest

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
SHORTTESTFILE = os.path.join(os.path.dirname(__file__), 'shorttests')

def rmdir(*args):
    dirname = os.path.join(*args)
    if os.path.isdir(dirname):
        shutil.rmtree(dirname)

def read_sh(command, input=None):
    # XXX check for other platforms too?
    close_fds = not sys.platform.startswith('win')
    p = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        close_fds=close_fds
        )
    out, err_ = p.communicate(input)
    return out

def sh(cmd):
    print cmd
    print read_sh(cmd)

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

def cat(*args):
    filename = os.path.join(*args)
    if os.path.isfile(filename):
        print open(filename).read()
    else:
        print 'No file named %s' % filename

def touch(*args, **kwargs):
    filename = os.path.join(*args)
    open(filename, 'w').write(kwargs.get('data',''))

def shorttests():
    return os.path.exists(SHORTTESTFILE)

def maybe_mkdir(path):
    if shorttests() and os.path.isdir(path):
        return
    rmdir(path)
    os.makedirs(path)

def maybe_rmdir(path):
    if shorttests() and os.path.isdir(path):
        return
    rmdir(path)

def setup(test):
    eggsdir = os.path.join(tempfile.gettempdir(), 'grokproject-test-eggs')
    maybe_mkdir(eggsdir)
    test.globs['eggsdir'] = eggsdir
    test.globs['testdir'] = tempfile.mkdtemp()

def teardown(test):
    maybe_rmdir(test.globs['eggsdir'])
    shutil.rmtree(test.globs['testdir'])

def doc_suite(package_dir):
    """Returns a test suite"""
    suite = []
    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    if package_dir not in sys.path:
        sys.path.append(package_dir)

    tests = [os.path.join(package_dir, filename)
            for filename in [
                'tests_paste.txt',
                'tests_alternative_release_url.txt'
                ]]
    globs = {
        'ls': ls,
        'cd': cd,
        'cat': cat,
        'touch': touch,
        'sh': sh,
        'read_sh': read_sh,
        'current_dir': CURRENT_DIR,
        }

    for test in tests:
        suite.append(
            doctest.DocFileSuite(
                test,
                optionflags=flags,
                globs=globs,
                setUp=setup,
                tearDown=teardown,
                module_relative=False
                ))
    return unittest.TestSuite(suite)

def show_shorttests_message():
    if shorttests():
        print
        print 'WARNING: running shorttests.'
        print
        print '  This reduces the runtime of testruns by making use of'
        print '  a once filled eggs directory.'
        print '  If you want clean test runs with an empty eggs directory,'
        print '  remove the file "' + SHORTTESTFILE + '".'
        print
        print '  Running shorttests might lead to failing tests. Please run'
        print '  the full tests before submitting code.'
        print
    else:
        print
        print 'NOTE: running full tests.'
        print
        print '  If you want to reuse a prefilled eggs directory between'
        print '  test runs (which dramatically reduces runtime), create a'
        print '  file "' + SHORTTESTFILE + '" and rerun the tests.'
        print

def test_suite():
    """returns the test suite"""
    show_shorttests_message()
    return doc_suite(CURRENT_DIR)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
