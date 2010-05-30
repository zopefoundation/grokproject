from setuptools import setup, find_packages

long_description = (open('README.txt').read()
                    + '\n\n' +
                    open('CHANGES.txt').read())

setup(
    name='grokproject',
    version='2.0',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='https://launchpad.net/grok',
    download_url='http://pypi.python.org/pypi/grokproject',
    description="""
    Script that sets up a grok project directory, installs Zope 3 and grok and
    creates a template for a grok application.""",
    long_description=long_description,
    license='ZPL',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['PasteScript>=1.6'],
    extras_require=dict(tests=['zope.testing',]),
    test_suite='tests.test_suite',
    entry_points={
    'console_scripts': ['grokproject = grokproject:main'],
    'paste.paster_create_template': ['grok = grokproject:GrokProject']},
    )
