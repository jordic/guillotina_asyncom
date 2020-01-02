from .base import ServiceAsyncOm
from guillotina import configure
from guillotina.component import query_multi_adapter
from guillotina.interfaces import IResourceSerializeToJsonSummary
from guillotina.response import ErrorResponse
from guillotina.response import Response
from guillotina.utils import get_object_url
from guillotina_asyncom.content import IDBFolder
from guillotina_asyncom.content import IDBResource


@configure.service(
    context=IDBFolder,
    method="POST",
    permission="guillotina.AddContent",
    summary="Add a new resource",
)
class POSTDBFolder(ServiceAsyncOm):
    async def __call__(self):
        db = await self.db()
        async with db.transaction():
            class_ = self.get_class()

            # todo validate json request
            data = await self.get_data()
            try:
                ins = class_(**data)
            except ValueError as e:
                raise ErrorResponse(
                    "PreconditionFailed", e, status=412, reason=e
                )

            await db.add(ins)
            # await notify(ObjectAddedEvent(
            #     obj, self.context, obj.id, payload=data
            # ))
            ins.__parent__ = self.context
            headers = {
                "Access-Control-Expose-Headers": "Location",
                "Location": get_object_url(ins, self.request),
            }
            serializer = query_multi_adapter(
                (ins, self.request), IResourceSerializeToJsonSummary
            )
            response = await serializer()
        return Response(content=response, status=201, headers=headers)


@configure.service(
    context=IDBResource,
    method="PATCH",
    permission="guillotina.ModifyContent",
    summary="Modify the content of this resource",
    responses={"200": {"description": "Resource Data"}},
)
class PatchDBResource(ServiceAsyncOm):
    async def __call__(self):
        db = await self.db()
        # TODO events
        async with db.transaction():
            data = await self.get_data()
            for key, val in data.items():
                setattr(self.context, key, val)
            await db.update(self.context)
        return Response(status=204)


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
    name="@addable-types",
)
class AvailableTypes(ServiceAsyncOm):
    async def __call__(self):
        return [self.context.model]
