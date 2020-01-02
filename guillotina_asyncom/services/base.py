from guillotina.api.service import Service
from guillotina.component import get_utility
from guillotina_asyncom.db import Base
from guillotina_asyncom.interfaces import IAsyncOm


class ServiceAsyncOm(Service):
    async def db(self):
        return await get_utility(IAsyncOm).get()

    def get_class(self):
        return Base._decl_class_registry.get(self.context.model)
