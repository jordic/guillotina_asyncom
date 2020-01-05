from contextvars import ContextVar
from asyncom import OMDatabase
from databases.backends.postgres import PostgresBackend
from databases.backends.postgres import PostgresConnection
from guillotina import configure
from guillotina.transactions import get_transaction
from guillotina_asyncom.interfaces import IAsyncOm
from databases.core import Connection


class CustomConnection(Connection):
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class GuillotinaBackend(PostgresBackend):
    def __init__(self, conn):
        self._dialect = self._get_dialect()
        self._con = conn

    def connection(self):
        pg = PostgresConnection(None, self._dialect)
        pg._connection = self._con
        return pg


class GuillotinaOM(OMDatabase):
    def __init__(self, conn):
        self.is_connected = True
        self._backend = GuillotinaBackend(conn)
        self._global_connection = None
        self._global_transacion = None
        self._connection_context = ContextVar("connection_context")

    def connection(self):
        if self._global_connection is not None:
            return self._global_connection

        try:
            return self._connection_context.get()
        except LookupError:
            connection = CustomConnection(self._backend)
            self._connection_context.set(connection)
            return connection


@configure.utility(provides=IAsyncOm)
class AsyncOMUtility:
    async def get(self, conn=None):
        if conn is None:
            txn = get_transaction()
            conn = await txn.get_connection()
        return GuillotinaOM(conn)
