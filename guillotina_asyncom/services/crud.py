
from guillotina import configure
from guillotina_asyncom.content import IDBFolder
from guillotina_asyncom.content import IDBResource
from guillotina.event import notify
from guillotina.events import ObjectAddedEvent
from guillotina.utils import get_object_url
from guillotina.component import query_multi_adapter
from guillotina.response import Response
from guillotina.interfaces import IResourceSerializeToJsonSummary
from .base import ServiceAsyncOm


@configure.service(
    context=IDBFolder,
    method="POST",
    permission="guillotina.AddContent",
    summary="Add a new resource"
)
class POSTDBFolder(ServiceAsyncOm):
    async def __call__(self):
        db = await self.db()
        async with db.transaction():
            class_ = self.get_class()

            # todo validate json request
            data = await self.get_data()
            ins = class_(**data)

            await db.add(ins)
            # await notify(ObjectAddedEvent(
            #     obj, self.context, obj.id, payload=data
            # ))
            ins.__parent__ = self.context
            headers = {
                "Access-Control-Expose-Headers": "Location",
                "Location": get_object_url(ins, self.request)
            }
            serializer = query_multi_adapter(
                (ins, self.request),
                IResourceSerializeToJsonSummary
            )
            response = await serializer()
        return Response(content=response, status=201, headers=headers)



@configure.service(
    context=IDBResource,
    method="DELETE",
    permission="guillotina.DeleteContent",
    summary="Delete resource",
    responses={"200": {"description": "Successfully deleted resource"}},
)
class DeleteDBResource(ServiceAsyncOm):
    async def __call__(self):
        db = await self.db()
        # TODO events
        async with db.transaction():
            await db.delete(self.context)


@configure.service(
    context=IDBFolder,
    method="GET",
    permission="guillotina.AddContent",
    summary="Get addable types",
    name="@addable-types"
)
class AvailableTypes(ServiceAsyncOm):
    async def __call__(self):
        return [self.context.model]
