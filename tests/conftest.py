from dataclasses import dataclass
from typing import Dict

from ariadne import InterfaceType, make_executable_schema
from graphql import GraphQLSchema
import pytest

from ariadne_relay import RelayQueryType, resolve_node_query_sync
from ariadne_relay.node import NodeObjectType


@dataclass(frozen=True)
class Foo:
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
    """


@pytest.fixture
def foo_nodes() -> Dict[str, Foo]:
    return {str(i): Foo(id=i) for i in range(10)}


@pytest.fixture
def query_type(foo_nodes: Dict[str, Foo]) -> RelayQueryType:
    query_type = RelayQueryType()
    query_type.set_field("node", resolve_node_query_sync)
    query_type.set_connection("foos", lambda *_: list(foo_nodes.values()))
    return query_type


@pytest.fixture
def node_interface_type() -> InterfaceType:
    node_interface_type = InterfaceType("Node")
    node_interface_type.set_type_resolver(lambda obj, *_: obj.__class__.__name__)
    return node_interface_type


@pytest.fixture
def foo_type(foo_nodes: Dict[str, Foo]) -> NodeObjectType:
    foo_type = NodeObjectType("Foo")
    foo_type.set_instance_resolver(lambda id, *_: foo_nodes[id])
    return foo_type


@pytest.fixture
def schema(
    type_defs: str,
    query_type: RelayQueryType,
    node_interface_type: InterfaceType,
    foo_type: NodeObjectType,
) -> GraphQLSchema:
    return make_executable_schema(
        type_defs,
        [query_type, node_interface_type, foo_type],
    )


@pytest.fixture
def node_query() -> str:
    return "query($id: ID!) { node(id: $id) { __typename, id } }"


@pytest.fixture
def connection_query() -> str:
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
