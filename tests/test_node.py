from ariadne import InterfaceType, make_executable_schema, QueryType
from graphql import graphql_sync
from graphql_relay import to_global_id

from ariadne_relay import NodeObjectType, resolve_node_query_sync
from .conftest import Foo


def test_node_resolver(type_defs: str, node_query: str) -> None:
    test_nodes = {str(i): Foo(id=i) for i in range(10)}

    query_type = QueryType()
    query_type.set_field("node", resolve_node_query_sync)

    node_interface = InterfaceType(
        "Node",
        type_resolver=lambda obj, *_: obj.__class__.__name__,
    )

    test_type = NodeObjectType(
        "Foo",
        instance_resolver=lambda id, *_: test_nodes[id],
    )

    schema = make_executable_schema(type_defs, query_type, node_interface, test_type)

    for obj in test_nodes.values():
        type_name = obj.__class__.__name__
        global_id = to_global_id(type_name, str(obj.id))
        result = graphql_sync(schema, node_query, variable_values={"id": global_id})
        assert result.errors is None
        assert result.data == {
            "node": {
                "__typename": type_name,
                "id": global_id,
            }
        }


def test_non_node_typename(type_defs: str, node_query: str) -> None:
    query_type = QueryType()
    query_type.set_field("node", resolve_node_query_sync)
    node_interface = InterfaceType(
        "Node",
        type_resolver=lambda obj, *_: obj.__class__.__name__,
    )
    schema = make_executable_schema(type_defs, query_type, node_interface)
    global_id = to_global_id("Bar", "bar")
    result = graphql_sync(schema, node_query, variable_values={"id": global_id})
    assert result.errors is None
    assert result.data == {"node": None}
