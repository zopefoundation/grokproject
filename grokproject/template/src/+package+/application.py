import sys, os
import ZConfig
import zope.event
import zope.app.appsetup
from zope.app.wsgi import WSGIPublisherApplication
from zope.app.appsetup.appsetup import multi_database
from zope.app.appsetup.interfaces import DatabaseOpened, ProcessStarting

def application_factory(global_conf, conf='zope.conf'):
    # load 'zope.conf' configuration
    schema_xml = os.path.join(
        os.path.dirname(zope.app.appsetup.__file__), 'schema', 'schema.xml')
    schema = ZConfig.loadSchema(schema_xml)
    options, handlers = ZConfig.loadConfig(
        schema, os.path.join(global_conf['here'], conf))

    if options.path:
        sys.path[0:0] = [os.path.abspath(p) for p in options.path]
    options.eventlog()

    # load ZCML configuration
    features = ()
    if options.devmode:
        features += ('devmode',)
    zope.app.appsetup.config(options.site_definition, features)

    # notify of ZODB database opening
    db = multi_database(options.databases)[0][0]
    zope.event.notify(DatabaseOpened(db))

    zope.event.notify(ProcessStarting())
    return WSGIPublisherApplication(db)
