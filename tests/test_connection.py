from ariadne import make_executable_schema
from graphql import graphql_sync
from graphql_relay import offset_to_cursor, to_global_id

from ariadne_relay import NodeObjectType, RelayQueryType
from .conftest import Foo


def test_default_connection_factory(type_defs: str, foo_connection_query: str) -> None:
    test_nodes = [Foo(id=i) for i in range(10)]

    query_type = RelayQueryType()
    query_type.set_connection("foos", lambda *_: test_nodes)

    test_type = NodeObjectType("Foo")

    schema = make_executable_schema(type_defs, query_type, test_type)

    result = graphql_sync(schema, foo_connection_query)
    assert result.errors is None
    assert result.data == {
        "foos": {
            "edges": [
                {
                    "cursor": offset_to_cursor(i),
                    "node": {
                        "__typename": obj.__class__.__name__,
                        "id": to_global_id(obj.__class__.__name__, str(obj.id)),
                    },
                }
                for i, obj in enumerate(test_nodes)
            ],
            "pageInfo": {
                "hasNextPage": False,
                "hasPreviousPage": False,
                "startCursor": offset_to_cursor(0),
                "endCursor": offset_to_cursor(len(test_nodes) - 1),
            },
        },
    }
