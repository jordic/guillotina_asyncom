## guillotina_asyncom

POC of integrating a new Content-type DBFolder

- A DBFolder represents a table on postgres
  with a related sqlalchemy model

### Benefits

- Use guillotina permission system
- Use guillotina framework.
- Lookup views on a context (a sqlalchemy object)
- Integrate with the guillotina gmi interface

## Howto use

1. Create your regular sqlalchemy model, like, import your Base,
   from guillotina_asyncom.db

```python
from guillotina_asyncom.db import Base
import sqlalchemy as sa

@implementer(IModel)
class Model(Base):
    __tablename__ = "extras"

    pk = sa.Column(sa.Integer, primary_key=True)
    value = sa.Column(sa.JSONB)

```

Add an object whenever you want of your guillotina content tree:

```
POST /db/guillotina/
{
    "@type": "DBFolder",
    "id", : "dbmodel",
    "model": "Model"
}
```

From here, we can just use the guillotina API with our new endpoint.

POST /db/guillotina/dbmodel/
{
"value": {"prop", "value"}
}

GET /db/guillotina/dbmodel/@search
GET /db/guillotina/dbmodel/{pk}
DELETE /db/guillotina/dbmodel/{pk}
PATCH /db/guillotina/dbmodel/{pk}

Thought it should work registering services for instances...

POST /db/guillotina/dbmodel/{pk}/@requeue

- Cool feature: It integrates with guillotina_react :)

## IDEAS and TODOS

- It's not hard to build a generic model explorer from here.
  All registered models on sqlalchemy live on Base.metadata...
  just build a small traversal around

- Generate the expected schema for every new type,
  perhaps on the /db/guillotina/dbmodel/@schema
  taking it from declarative sqlalchemy models

- Integrate the permission system on rows... Just implement an acl
  jsonb column in your models. (Setting the ownership, or whatever you want..)

- The event system is still not implemented, perhaps could be implemented
  but with some new events. (If we do with the actuals we will mess with the
  catalog)

- Implement a rich @search model (on the end we can just translate,
  the actual implementations to sqlalchemy querys). Also implement pagger,
  and the rest. This will make this fit so well with guillotina_react.
