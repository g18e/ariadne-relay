from ariadne.asgi import GraphQL
from graphql import GraphQLSchema
import pytest
from starlette.testclient import TestClient


@pytest.fixture
def app(schema: GraphQLSchema) -> GraphQL:
    return GraphQL(schema)


@pytest.fixture
def client(app: GraphQL) -> TestClient:
    return TestClient(app)
