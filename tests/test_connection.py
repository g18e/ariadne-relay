from ariadne import make_executable_schema
from graphql import graphql_sync
from graphql_relay import offset_to_cursor, to_global_id

from ariadne_relay import NodeObjectType, RelayQueryType


def test_default_connection_factory() -> None:
    type_defs = """
        type Query {
            test(
                after: String
                before: String
                first: Int
                last: Int
            ): TestConnection!
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

        type Test implements Node {
            id: ID!
        }

        type TestEdge {
            cursor: String!
            node: Test
        }

        type TestConnection {
            pageInfo: PageInfo!
            edges: [TestEdge]!
        }
    """
    test_nodes = [{"id": i} for i in range(10)]

    query_type = RelayQueryType()
    query_type.set_connection("test", lambda *_: test_nodes)

    test_type = NodeObjectType("Test")

    schema = make_executable_schema(type_defs, query_type, test_type)

    result = graphql_sync(
        schema,
        """
            {
                test {
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
        """,
    )
    assert result.errors is None
    assert result.data == {
        "test": {
            "edges": [
                {
                    "cursor": offset_to_cursor(i),
                    "node": {
                        "__typename": "Test",
                        "id": to_global_id("Test", str(obj["id"])),
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
