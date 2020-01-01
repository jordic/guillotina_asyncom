
from .base import ServiceAsyncOm
from guillotina import configure
from guillotina_asyncom.content import IDBFolder
from guillotina_asyncom.serializers import serializer


@configure.service(
    context=IDBFolder,
    name="@search",
    method="GET"
)
class SearchDBFolder(ServiceAsyncOm):
    async def __call__(self):
        db = await self.db()
        qs = db.query(self.get_class())
        amount = await qs.count()
        data = await qs.all()
        for item in data:
            item.__parent__ = self.context
        return {
            "member": [await serializer(item, self.context) for item in data],
            "items_count": amount
        }
