from setuptools import setup, find_packages

setup(
    name='grokproject',
    version='0.2dev',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='https://launchpad.net/grok',
    download_url='svn://svn.zope.org/repos/main/grokproject/trunk#egg=grokproject-dev',
    description='Script that sets up a grok project directory, installs Zope 3 and grok and creates a template for a grok application.',
    long_description=open('README.txt').read(),
    license='ZPL',

    package_dir = {'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=['PasteScript==dev,>1.1',
                      # this is needed only because PasteScript==dev
                      # depends on a dev version of Paste now.  Once
                      # these two are released, remove the dependency
                      # on Paste (TODO).
                      'Paste==dev,>1.2.1'
                      ],
    entry_points="""
    [console_scripts]
    grokproject = grokproject:main
    [paste.paster_create_template]
    grokproject = grokproject:GrokProject
    """,
)
