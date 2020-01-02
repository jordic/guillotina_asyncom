from guillotina import configure
from guillotina import schema
from guillotina.component import get_utility
from guillotina.content import Folder
from guillotina.interfaces import IFolder
from guillotina.interfaces import IResource
from guillotina_asyncom.db import Base
from guillotina_asyncom.interfaces import IAsyncOm
from zope.interface import directlyProvides


class IDBFolder(IFolder):
    model = schema.TextLine(title="Model Name", required=True)
    filters = schema.Dict(required=False, default={})
    also_provides = schema.TextLine(
        title="Interfaces also provided", required=False
    )


class IDBResource(IResource):
    pass


@configure.contenttype(
    type_name="DBFolder",
    schema=IDBFolder,
    behaviors=["guillotina.behaviors.dublincore.IDublinCore"],
)
class DBFolder(Folder):
    async def db(self):
        return await get_utility(IAsyncOm).get()

    def get_class(self):
        return Base._decl_class_registry.get(self.model)

    async def query(self):
        db = await self.db()
        return db.query(self.get_class())

    async def async_contains(self, key: str) -> bool:
        # TODO: Perhaps convert key from str to (type on primary_key)
        return await self.query().get(int(key)) is not None

    async def async_get(self, key, suppress_events=True, default=None):
        db = await self.query()
        obj = await db.get(int(key))
        if not obj:
            return default
        # factory
        obj.__parent__ = self
        directlyProvides(obj, IDBResource)
        return obj
