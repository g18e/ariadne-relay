from ariadne import InterfaceType, make_executable_schema, QueryType
from graphql import graphql_sync
from graphql_relay import to_global_id

from ariadne_relay import NodeType, resolve_node_query_sync


def test_node_resolver() -> None:
    type_defs = """
        type Query {
            node(id: ID!): Node
        }

        interface Node {
            id: ID!
        }

        type Test implements Node {
            id: ID!
        }
    """
    test_nodes = {str(i): {"__typename": "Test", "id": i} for i in range(10)}

    query_type = QueryType()
    query_type.set_field("node", resolve_node_query_sync)

    node_interface = InterfaceType(
        "Node",
        type_resolver=lambda obj, *_: obj["__typename"],
    )

    test_type = NodeType(
        "Test",
        instance_resolver=lambda _0, _1, id: test_nodes[id],
    )

    schema = make_executable_schema(type_defs, query_type, node_interface, test_type)

    for obj in test_nodes.values():
        global_id = to_global_id(str(obj["__typename"]), str(obj["id"]))
        result = graphql_sync(
            schema,
            "query($id: ID!) { node(id: $id) { __typename, id } }",
            variable_values={"id": global_id},
        )
        assert result.errors is None
        assert result.data == {
            "node": {
                "__typename": obj["__typename"],
                "id": global_id,
            }
        }
