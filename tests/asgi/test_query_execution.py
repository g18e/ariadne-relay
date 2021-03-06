from typing import Dict

from graphql_relay import offset_to_cursor, to_global_id
from starlette.testclient import TestClient

from ..conftest import Foo, Qux


def test_query_node_instance_resolver(
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


def test_query_node_interface_instance_resolver(
    client: TestClient,
    node_query: str,
    qux_nodes: Dict[str, Qux],
) -> None:
    test_node = next(iter(qux_nodes.values()))
    type_name = test_node.__class__.__name__
    global_id = to_global_id("Baz", str(test_node.id))
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


def test_query_non_node_typename(
    client: TestClient,
    node_query: str,
) -> None:
    global_id = to_global_id("Bar", "bar")
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
            "node": None,
        }
    }


def test_node_typename_resolver(
    client: TestClient,
    qux_connection_query: str,
    qux_nodes: Dict[str, Foo],
) -> None:
    response = client.post("/", json={"query": qux_connection_query})
    assert response.status_code == 200
    assert response.json() == {
        "data": {
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
    }


def test_connection_query(
    client: TestClient,
    foo_connection_query: str,
    foo_nodes: Dict[str, Foo],
) -> None:
    response = client.post("/", json={"query": foo_connection_query})
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
