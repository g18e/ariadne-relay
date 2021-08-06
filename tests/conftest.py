from dataclasses import dataclass
from typing import Dict

from ariadne import InterfaceType, make_executable_schema, ObjectType
from graphql import GraphQLSchema
import pytest

from ariadne_relay import RelayQueryType, resolve_node_query_sync
from ariadne_relay.node import NodeInterfaceType, NodeObjectType


@dataclass(frozen=True)
class Foo:
    id: int  # noqa: A003


@dataclass(frozen=True)
class Qux:
    id: int  # noqa: A003


@pytest.fixture
def type_defs() -> str:
    return """
        type Query {
            node(id: ID!): Node
            foos(
                after: String
                before: String
                first: Int
                last: Int
            ): FoosConnection!
            quxes(
                after: String
                before: String
                first: Int
                last: Int
            ): QuxesConnection!
        }

        interface Node {
            id: ID!
        }

        type PageInfo {
            hasNextPage: Boolean!
            hasPreviousPage: Boolean!
            startCursor: String
            endCursor: String
        }

        type Foo implements Node {
            id: ID!
        }

        type FooEdge {
            cursor: String!
            node: Foo
        }

        type FoosConnection {
            pageInfo: PageInfo!
            edges: [FooEdge]!
        }

        type Bar {
            id: String!
        }

        interface Baz {
            id: ID!
        }

        type Qux implements Node & Baz {
            id: ID!
        }

        type QuxEdge {
            cursor: String!
            node: Qux
        }

        type QuxesConnection {
            pageInfo: PageInfo!
            edges: [QuxEdge]!
        }
    """


@pytest.fixture
def foo_nodes() -> Dict[str, Foo]:
    return {str(i): Foo(id=i) for i in range(10)}


@pytest.fixture
def qux_nodes() -> Dict[str, Qux]:
    return {str(i): Qux(id=i) for i in range(10)}


@pytest.fixture
def query_type(foo_nodes: Dict[str, Foo], qux_nodes: Dict[str, Qux]) -> RelayQueryType:
    query_type = RelayQueryType()
    query_type.set_field("node", resolve_node_query_sync)
    query_type.set_connection("foos", lambda *_: list(foo_nodes.values()))
    query_type.set_connection("quxes", lambda *_: list(qux_nodes.values()))
    return query_type


@pytest.fixture
def node_interface_type() -> InterfaceType:
    node_interface_type = InterfaceType("Node")
    node_interface_type.set_type_resolver(lambda obj, *_: obj.__class__.__name__)
    return node_interface_type


@pytest.fixture
def baz_interface_type(qux_nodes: Dict[str, Qux]) -> NodeInterfaceType:
    baz_interface_type = NodeInterfaceType("Baz")
    baz_interface_type.set_typename_resolver(lambda obj, *_: "Baz")
    baz_interface_type.set_type_resolver(lambda obj, *_: obj.__class__.__name__)
    baz_interface_type.set_instance_resolver(lambda id, *_: qux_nodes[id])
    return baz_interface_type


@pytest.fixture
def foo_type(foo_nodes: Dict[str, Foo]) -> NodeObjectType:
    foo_type = NodeObjectType("Foo")
    foo_type.set_instance_resolver(lambda id, *_: foo_nodes[id])
    return foo_type


@pytest.fixture
def bar_type() -> ObjectType:
    return ObjectType("Bar")


@pytest.fixture
def qux_type() -> NodeObjectType:
    return NodeObjectType("Qux")


@pytest.fixture
def schema(
    type_defs: str,
    query_type: RelayQueryType,
    node_interface_type: InterfaceType,
    baz_interface_type: NodeInterfaceType,
    foo_type: NodeObjectType,
    bar_type: ObjectType,
    qux_type: NodeObjectType,
) -> GraphQLSchema:
    return make_executable_schema(
        type_defs,
        [
            query_type,
            node_interface_type,
            baz_interface_type,
            foo_type,
            bar_type,
            qux_type,
        ],
    )


@pytest.fixture
def node_query() -> str:
    return "query($id: ID!) { node(id: $id) { __typename, id } }"


@pytest.fixture
def foo_connection_query() -> str:
    return """
        {
            foos {
                edges {
                    cursor
                    node  {
                        __typename
                        id
                    }
                }
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                    startCursor
                    endCursor
                }
            }
        }
    """


@pytest.fixture
def qux_connection_query() -> str:
    return """
        {
            quxes {
                edges {
                    node  {
                        __typename
                        id
                    }
                }
            }
        }
    """
