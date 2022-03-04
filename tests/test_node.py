from typing import Dict

from ariadne import InterfaceType, make_executable_schema, QueryType
from graphql import graphql_sync
from graphql_relay import to_global_id
from graphql_relay.utils import base64

from ariadne_relay import NodeInterfaceType, RelayObjectType, RelayQueryType
from .conftest import Foo, Qux


def test_node_instance_resolver(
    type_defs: str,
    foo_nodes: Dict[str, Foo],
    foo_type: RelayObjectType,
    query_type: RelayQueryType,
    node_query: str,
    node_interface_type: InterfaceType,
) -> None:
    schema = make_executable_schema(
        type_defs,
        foo_type,
        query_type,
        node_interface_type,
    )
    for obj in foo_nodes.values():
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


def test_node_interface_instance_resolver(
    type_defs: str,
    baz_interface_type: NodeInterfaceType,
    qux_nodes: Dict[str, Qux],
    qux_type: RelayObjectType,
    query_type: RelayQueryType,
    node_query: str,
    node_interface_type: InterfaceType,
) -> None:
    schema = make_executable_schema(
        type_defs,
        query_type,
        baz_interface_type,
        qux_type,
        node_interface_type,
    )
    for obj in qux_nodes.values():
        global_id = to_global_id("Baz", str(obj.id))
        result = graphql_sync(schema, node_query, variable_values={"id": global_id})
        assert result.errors is None
        assert result.data == {
            "node": {
                "__typename": obj.__class__.__name__,
                "id": global_id,
            }
        }
        # a NodeInterfaceType instance resolver does not
        # propagate to types that implement the interface
        invalid_global_id = to_global_id("Qux", str(obj.id))
        result = graphql_sync(
            schema,
            node_query,
            variable_values={"id": invalid_global_id},
        )
        assert result.errors is None
        assert result.data == {"node": None}


def test_node_typename_resolver(
    type_defs: str,
    baz_interface_type: NodeInterfaceType,
    qux_nodes: Dict[str, Qux],
    qux_type: RelayObjectType,
    query_type: RelayQueryType,
    qux_connection_query: str,
) -> None:
    schema = make_executable_schema(type_defs, query_type, baz_interface_type, qux_type)
    result = graphql_sync(schema, qux_connection_query)
    assert result.errors is None
    assert result.data == {
        "quxes": {
            "edges": [
                {
                    "node": {
                        "__typename": obj.__class__.__name__,
                        "id": to_global_id("Baz", str(obj.id)),
                    },
                }
                for obj in qux_nodes.values()
            ],
        },
    }


def test_non_node_typename(
    type_defs: str,
    query_type: QueryType,
    node_query: str,
    node_interface_type: InterfaceType,
) -> None:
    schema = make_executable_schema(type_defs, query_type, node_interface_type)
    global_id = to_global_id("Bar", "bar")
    result = graphql_sync(schema, node_query, variable_values={"id": global_id})
    assert result.errors is None
    assert result.data == {"node": None}


def test_invalid_encoding(
    type_defs: str,
    query_type: QueryType,
    node_query: str,
    node_interface_type: InterfaceType,
) -> None:
    schema = make_executable_schema(type_defs, query_type, node_interface_type)
    global_id = "invalid"
    result = graphql_sync(schema, node_query, variable_values={"id": global_id})
    assert result.errors is None
    assert result.data == {"node": None}


def test_missing_separator(
    type_defs: str,
    query_type: QueryType,
    node_query: str,
    node_interface_type: InterfaceType,
) -> None:
    schema = make_executable_schema(type_defs, query_type, node_interface_type)
    global_id = base64("foo")
    result = graphql_sync(schema, node_query, variable_values={"id": global_id})
    assert result.errors is None
    assert result.data == {"node": None}


def test_missing_typename(
    type_defs: str,
    query_type: QueryType,
    node_query: str,
    node_interface_type: InterfaceType,
) -> None:
    schema = make_executable_schema(type_defs, query_type, node_interface_type)
    global_id = base64(":bar")
    result = graphql_sync(schema, node_query, variable_values={"id": global_id})
    assert result.errors is None
    assert result.data == {"node": None}


def test_missing_id(
    type_defs: str,
    query_type: QueryType,
    node_query: str,
    node_interface_type: InterfaceType,
) -> None:
    schema = make_executable_schema(type_defs, query_type, node_interface_type)
    global_id = base64("foo:")
    result = graphql_sync(schema, node_query, variable_values={"id": global_id})
    assert result.errors is None
    assert result.data == {"node": None}


def test_empty_global_id(
    type_defs: str,
    query_type: QueryType,
    node_query: str,
    node_interface_type: InterfaceType,
) -> None:
    schema = make_executable_schema(type_defs, query_type, node_interface_type)
    global_id = ""
    result = graphql_sync(schema, node_query, variable_values={"id": global_id})
    assert result.errors is None
    assert result.data == {"node": None}
