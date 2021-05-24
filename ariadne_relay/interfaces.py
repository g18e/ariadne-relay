from ariadne import InterfaceType
from graphql import GraphQLObjectType

from .base import RelayConnectionType


class RelayInterfaceType(RelayConnectionType, InterfaceType):
    def bind_resolvers_to_graphql_type(
        self, graphql_type: GraphQLObjectType, replace_existing: bool = True
    ) -> None:
        super().bind_resolvers_to_graphql_type(  # type: ignore
            graphql_type,
            replace_existing,
        )
        self.bind_connection_resolvers_to_graphql_type(graphql_type, replace_existing)
