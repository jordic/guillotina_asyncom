

def cast_to_pk(model, value):
    """ Cast an string value to primary key type """
    pk = model.__table__.columns.values()[0]
    return pk.type.python_type(value)
