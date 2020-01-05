from .data import DataModel
from .utils import get_database
from guillotina.component import get_utility
from guillotina_asyncom.interfaces import IAsyncOm

import pytest

pytestmark = pytest.mark.asyncio


async def test_fixture_is_working(omapp):
    app, client = omapp
    resp = await client.get("/")
    assert resp.status_code == 200
    resp = await client.get("/db/guillotina")
    assert resp.status_code == 401

    async with get_database(app) as db:
        ins = DataModel(name="foo")
        await db.add(ins)
        res = await db.query(DataModel).count()
        assert res == 1


