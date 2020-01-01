from guillotina import configure
from guillotina_asyncom.interfaces import IAsyncOm
from guillotina.transactions import get_transaction
from asyncom import OMDatabase


@configure.utility(provides=IAsyncOm)
class AsyncOMUtility(OMDatabase):
    async def get(self):
        txn = get_transaction()
        conn = await txn.get_connection()
        return OMDatabase(conn=conn)
