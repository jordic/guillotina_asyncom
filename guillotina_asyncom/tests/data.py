from guillotina_asyncom.db import Base

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from zope.interface import implementer
from guillotina.interfaces import IResource


class IDataModel(IResource):
    pass


@implementer(IDataModel)
class DataModel(Base):

    __tablename__ = "asyncom_datamodel"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(200), nullable=False)
    props = sa.Column(JSONB, default={})
    integer = sa.Column(sa.Integer)
    date = sa.Column(sa.Date)
    datetime = sa.Column(sa.DateTime)
