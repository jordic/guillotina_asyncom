from .base import ServiceAsyncOm
from guillotina import configure
from guillotina_asyncom.content import IDBFolder
from guillotina_asyncom.serializers import serializer
from sqlalchemy.sql import operators
from guillotina import error_reasons
from guillotina.response import ErrorResponse


class QBuilder:
    _underscore_operators = {
        "gt": operators.gt,
        "lte": operators.lt,
        "gte": operators.ge,
        "le": operators.le,
        "contains": operators.contains_op,
        "in": operators.in_op,
        "exact": operators.eq,
        "iexact": operators.ilike_op,
        "startswith": operators.startswith_op,
        "istartswith": lambda c, x: c.ilike(x.replace("%", "%%") + "%"),
        "iendswith": lambda c, x: c.ilike("%" + x.replace("%", "%%")),
        "endswith": operators.endswith_op,
        "isnull": lambda c, x: x and c != None or c == None,
        "range": operators.between_op,
        "year": lambda c, x: extract("year", c) == x,
        "month": lambda c, x: extract("month", c) == x,
        "day": lambda c, x: extract("day", c) == x,
    }

    non_search = ["b_size", "b_start", "depth", "sort_on"]

    def __init__(self, qs, model):
        self.qs = qs  # query string
        self.model = model
        self.available_fields = dict(model.__table__.columns).keys()

    def get_searchable_params(self):
        items = {}
        for key, val in self.qs.items():
            field = key.split("__")
            if field[0] in self.non_search:
                continue
            if field[0] not in self.available_fields:
                continue
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
            # cast value
            # TODO: Test if this works with dates
            func = column.type.python_type
            try:
                casted = func(val)
            except:
                raise ErrorResponse(
                    "InvalidParam",
                    f"Invalid value for field {field}",
                    status=412,
                    reason=error_reasons.DESERIALIZATION_FAILED
                )

            if len(parts) > 1:
                op = self._underscore_operators[parts[1]]
                # cast value
                filters.append(op(column, casted))
            else:
                filters.append(column == casted)
        return query.filter(*filters)

    def apply_order_by(self, query):
        asc = True
        if "sort_on" not in self.qs:
            return query
        sort = self.qs.get("sort_on")
        if sort.startswith("-"):
            asc = False
            sort = sort[1:]
        field = self.model.__table__.c[sort]
        if asc:
            return query.order_by(field.asc())
        return query.order_by(field.desc())


@configure.service(context=IDBFolder, name="@search", method="GET")
class SearchDBFolder(ServiceAsyncOm):
    async def __call__(self):
        query_string = dict(self.request.query)
        builder = QBuilder(query_string, self.get_class())
        db = await self.db()
        qs = db.query(self.get_class())
        qs = builder.get_filters(qs)
        # calculate the total count before apply pagination
        amount = await qs.count()
        # apply pagination and ordering
        qs = builder.apply_order_by(qs)
        qs = builder.apply_limit(qs)
        qs = builder.apply_offset(qs)
        data = await qs.all()
        for item in data:
            item.__parent__ = self.context
        return {
            "member": [await serializer(item, self.context) for item in data],
            "items_count": amount,
        }
