from typing import Dict

from graphql_relay import offset_to_cursor, to_global_id
from starlette.testclient import TestClient

from ..conftest import Foo


def test_node_query(
    client: TestClient,
    node_query: str,
    foo_nodes: Dict[str, Foo],
) -> None:
    test_node = next(iter(foo_nodes.values()))
    type_name = test_node.__class__.__name__
    global_id = to_global_id(type_name, str(test_node.id))
    response = client.post(
        "/",
        json={
            "query": node_query,
            "variables": {
                "id": global_id,
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "node": {
                "__typename": type_name,
                "id": global_id,
            }
        }
    }


def test_connection_query(
    client: TestClient,
    connection_query: str,
    foo_nodes: Dict[str, Foo],
) -> None:
    response = client.post("/", json={"query": connection_query})
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "foos": {
                "edges": [
                    {
                        "cursor": offset_to_cursor(i),
                        "node": {
                            "__typename": obj.__class__.__name__,
                            "id": to_global_id(obj.__class__.__name__, str(obj.id)),
                        },
                    }
                    for i, obj in enumerate(foo_nodes.values())
                ],
                "pageInfo": {
                    "hasNextPage": False,
                    "hasPreviousPage": False,
                    "startCursor": offset_to_cursor(0),
                    "endCursor": offset_to_cursor(len(foo_nodes) - 1),
                },
            },
        }
    }
