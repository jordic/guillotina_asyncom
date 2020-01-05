from contextlib import asynccontextmanager
from guillotina.component import get_utility
from guillotina.db.interfaces import IPostgresStorage
from guillotina.interfaces import IDatabase
from guillotina_asyncom.interfaces import IAsyncOm


@asynccontextmanager
async def get_database(app):
    root = app.app.root
    for _, db in root:
        if not IDatabase.providedBy(db):
            continue
        storage = db.storage
        if IPostgresStorage.providedBy(storage):
            tool = get_utility(IAsyncOm)
            conn = await storage.pool.acquire()
            yield await tool.get(conn=conn)
            await storage.pool.release(conn)
