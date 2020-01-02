from guillotina import configure
from guillotina.component import ComponentLookupError
from guillotina.component import get_multi_adapter
from guillotina.interfaces import IResourceSerializeToJson
from guillotina.interfaces import IResourceSerializeToJsonSummary
from guillotina_asyncom.content import IDBResource
from zope.interface import Interface


async def serializer(obj, context):
    item = obj.to_dict()
    item.update(
        {
            "path": f"/{obj.pk_}",
            "@type": f"DB_{context.model}",
            "@name": obj.title(),
            "@id": obj.absolute_url(),
            "is_folderish": False,
            "parent": {},
        }
    )
    return item


@configure.adapter(
    for_=(IDBResource, Interface), provides=IResourceSerializeToJson
)
class SerializeToJson(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.permission_cache = {}

    async def __call__(self, include=None, omit=None):
        self.include = include or []
        self.omit = omit or []

        parent = self.context.__parent__
        if parent is not None:
            # We render the summary of the parent
            try:
                parent_summary = await get_multi_adapter(
                    (parent, self.request), IResourceSerializeToJsonSummary
                )()
            except ComponentLookupError:
                parent_summary = {}
        else:
            parent_summary = {}

        result = {
            "@id": self.context.absolute_url(),
            "@type": self.context.type_name,
            "@name": self.context.__name__,
            "@uid": self.context.id,
            "@static_behaviors": [],
            "@dynamic_behaviors": [],
            "parent": parent_summary,  # should be @parent
            "is_folderish": False,
        }
        result.update(self.context.to_dict())
        return result
