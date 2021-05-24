from ariadne import ObjectType
from graphql.type import GraphQLObjectType

from .base import RelayConnectionType


class RelayObjectType(RelayConnectionType, ObjectType):
    def bind_resolvers_to_graphql_type(
        self, graphql_type: GraphQLObjectType, replace_existing: bool = True
    ) -> None:
        super().bind_resolvers_to_graphql_type(  # type: ignore
            graphql_type,
            replace_existing,
        )
        self.bind_connection_resolvers_to_graphql_type(graphql_type, replace_existing)


class RelayQueryType(RelayObjectType):
    """Convenience class for defining Query type"""

    def __init__(self) -> None:
        super().__init__("Query")


class RelayMutationType(RelayObjectType):
    """Convenience class for defining Mutation type"""

    def __init__(self) -> None:
        super().__init__("Mutation")
