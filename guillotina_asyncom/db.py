from guillotina.utils import get_object_url
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base

import typing


class BaseModel(object):

    __behaviors__ = []
    __acl__ = {}

    def get_primary_key_field(self):
        return self.__table__.columns.values()[0].name

    def to_typed_pk(self, value: str) -> typing.Any:
        pk = self.__table__.columns.values()[0]
        return pk.type.python_type(value)

    def absolute_url(self):
        pk = self.get_primary_key_field()
        value = getattr(self, pk)
        return get_object_url(self.__parent__) + f"/{value}"

    @property
    def pk_(self):
        pk = self.get_primary_key_field()
        return getattr(self, pk)

    @property
    def uuid(self):
        return f"{self.__class__}/{self.pk_}"

    @property
    def __name__(self):
        return str(self.pk_)

    @property
    def acl(self) -> dict:
        """
        Access control list stores security information on the object
        """
        if self.__acl__ is None:
            return dict({})
        return self.__acl__

    @property
    def type_name(self):
        return f"DB{self.__class__}"

    def to_dict(self):
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }


Base = declarative_base(cls=BaseModel)
