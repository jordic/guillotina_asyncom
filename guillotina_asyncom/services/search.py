from .base import ServiceAsyncOm
from guillotina import configure
from guillotina_asyncom.content import IDBFolder
from guillotina_asyncom.serializers import serializer

from sqlalchemy.sql import operators


class QBuilder:
    _underscore_operators = {
        'gt':           operators.gt,
        'lte':          operators.lt,
        'gte':          operators.ge,
        'le':           operators.le,
        'contains':     operators.contains_op,
        'in':           operators.in_op,
        'exact':        operators.eq,
        'iexact':       operators.ilike_op,
        'startswith':   operators.startswith_op,
        'istartswith':  lambda c, x: c.ilike(x.replace('%', '%%') + '%'),
        'iendswith':    lambda c, x: c.ilike('%' + x.replace('%', '%%')),
        'endswith':     operators.endswith_op,
        'isnull':       lambda c, x: x and c != None or c == None,
        'range':        operators.between_op,
        'year':         lambda c, x: extract('year', c) == x,
        'month':        lambda c, x: extract('month', c) == x,
        'day':          lambda c, x: extract('day', c) == x
    }

    non_search = ["b_size", "b_start", "depth"]

    def __init__(self, qs, model):
        self.qs = qs  # query string
        self.model = model

    def get_searchable_params(self):
        items = {}
        for key, val in self.qs.items():
            if key not in self.non_search:
                items[key] = val
        return items.items()

    def apply_limit(self, query):
        qs = int(self.qs.get("b_size", 20))
        return query.limit(qs)

    def apply_offset(self, query):
        qs = int(self.qs.get("b_start", 0))
        return query.offset(qs)

    def get_filters(self, query):
        filters = []
        for key, val in self.get_searchable_params():
            parts = key.split("__")
            field = parts[0]
            column = self.model.__table__.c[field]
            if len(parts) > 1:
                op = self._underscore_operators[parts[1]]
                filters.append(
                    op(column, val)
                )
            else:
                filters.append(
                    column==val
                )
        return query.filter(*filters)



@configure.service(context=IDBFolder, name="@search", method="GET")
class SearchDBFolder(ServiceAsyncOm):
    async def __call__(self):
        query_string = dict(self.request.query)
        builder = QBuilder(query_string, self.get_class())
        db = await self.db()
        qs = db.query(self.get_class())
        qs = builder.get_filters(qs)
        amount = await qs.count()

        qs = builder.apply_limit(qs)
        qs = builder.apply_offset(qs)
        data = await qs.all()
        for item in data:
            item.__parent__ = self.context
        return {
            "member": [await serializer(item, self.context) for item in data],
            "items_count": amount,
        }
