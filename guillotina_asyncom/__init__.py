
from guillotina import configure

def includeme(root):
    configure.scan("guillotina_asyncom.content")
    configure.scan("guillotina_asyncom.utilities")
    configure.scan("guillotina_asyncom.services")
    configure.scan("guillotina_asyncom.serializers")
