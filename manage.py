#!/usr/bin/env python

import os

from flask.ext.script import Manager, Server
from flask.ext.script.commands import ShowUrls, Clean
from pymailtrack import create_app
from pymailtrack.models import db, User, Logs, TrackingCode

# default to dev config because no one should use this in
# production anyway
env = os.environ.get('APPNAME_ENV', 'dev')
app = create_app('pymailtrack.settings.%sConfig' % env.capitalize(), env=env)


manager = Manager(app)
manager.add_command("server", Server())
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())


@manager.shell
def make_shell_context():
    """ Creates a python REPL with several default imports
        in the context of the app
    """
    return dict(
        app=app,
        db=db,
        User=User,
        Logs=Logs,
        Track=TrackingCode
    )


@manager.command
def createdb():
    """ Creates a database with all of the tables defined in
        your SQLAlchemy models
    """
    db.create_all()
    u = User(username='admin', password='sorcery')
    db.session.add(u)
    db.session.commit()

if __name__ == "__main__":
    manager.run()
