import pytest

import sqlalchemy as sa
import os
from .data import DataModel  # noqa
from guillotina.testing import get_settings
from guillotina.component import globalregistry
from async_asgi_testclient import TestClient


@pytest.fixture
def asyncom(db):
    from guillotina_asyncom.db import Base
    host, port = db
    DSN = f"postgresql://postgres@{host}:{port}/guillotina"
    engine = sa.create_engine(DSN)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
async def omapp2(app_client, asyncom):
    app, client = app_client
    app.settings["applications"]
    yield app, client


@pytest.fixture(scope="function")
async def omapp(event_loop, db, request, asyncom):
    from guillotina.tests.fixtures import _clear_dbs
    from guillotina.tests.fixtures import clear_task_vars
    from guillotina.factory import make_app

    host, port = db
    globalregistry.reset()
    settings = get_settings()
    settings["applications"] = ["guillotina_asyncom"]

    settings["databases"]["db"]["storage"] = "postgresql"
    settings["databases"]["db"]["db_schema"] = "public"
    settings["databases"]["db"]["dsn"] = {
        "scheme": "postgres",
        "dbname": "guillotina",
        "user": "postgres",
        "host": host,
        "port": int(port),
        "password": "",
    }
    app = make_app(settings=settings, loop=event_loop)
    async with TestClient(app, timeout=30) as client:
        await _clear_dbs(app.app.root)
        yield app, client
    clear_task_vars()
