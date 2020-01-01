
from zope.interface import Interface


class IAsyncOm(Interface):
    async def get():
        """ Get an instance of asyncom to interact with postgresql """
