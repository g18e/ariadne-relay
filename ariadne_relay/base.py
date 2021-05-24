import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, cast, Dict, Optional

from ariadne.types import Resolver
from graphql import GraphQLObjectType, GraphQLResolveInfo

from .connection import (
    ConnectionArguments,
    ConnectionAwaitable,
    ConnectionCallable,
    ConnectionFactory,
    ConnectionFactoryOrConstructor,
    ReferenceConnection,
)
from .utils import is_coroutine_callable


@dataclass
class RelayConnectionConfig:
    factory: ConnectionFactory
    resolver: Resolver


DefaultConnectionFactory: ConnectionFactoryOrConstructor = ReferenceConnection


def set_default_connection_factory(factory: ConnectionFactoryOrConstructor) -> None:
    global DefaultConnectionFactory
    DefaultConnectionFactory = factory


class RelayConnectionType:
    __connection_config: Optional[Dict[str, RelayConnectionConfig]] = None

    @property
    def _connection_configs(self) -> Dict[str, RelayConnectionConfig]:
        if self.__connection_config is None:
            self.__connection_config = {}
        return self.__connection_config

    def connection(
        self,
        name: str,
        *,
        factory: Optional[ConnectionFactoryOrConstructor] = None,
    ) -> Callable[[Resolver], Resolver]:
        if not isinstance(name, str):
            raise ValueError(
                "connection decorator should be passed "
                'a field name: @foo.connection("name")'
            )
        return self.create_register_connection_resolver(name, factory=factory)

    def create_register_connection_resolver(
        self,
        name: str,
        *,
        factory: Optional[ConnectionFactoryOrConstructor] = None,
    ) -> Callable[[Resolver], Resolver]:
        def register_connection_resolver(f: Resolver) -> Resolver:
            self.set_connection(name, f, factory=factory)
            return f

        return register_connection_resolver

    def set_connection(
        self,
        name: str,
        resolver: Resolver,
        *,
        factory: Optional[ConnectionFactoryOrConstructor] = None,
    ) -> Resolver:
        factory = factory or DefaultConnectionFactory
        factory_instance: ConnectionFactory = (
            factory() if isinstance(factory, type) else factory
        )
        self._connection_configs[name] = RelayConnectionConfig(
            factory=factory_instance,
            resolver=resolver,
        )
        return resolver

    def bind_connection_resolvers_to_graphql_type(
        self,
        graphql_type: GraphQLObjectType,
        replace_existing: bool = True,
    ) -> None:
        for field_name, config in self._connection_configs.items():
            if field_name not in graphql_type.fields:
                raise ValueError(
                    "Field %s is not defined on type %s"
                    % (field_name, getattr(self, "name"))
                )
            if graphql_type.fields[field_name].resolve is None or replace_existing:
                connection_field = graphql_type.fields[field_name]
                if is_coroutine_callable(config.resolver) or is_coroutine_callable(
                    config.factory
                ):
                    connection_field.resolve = create_connection_resolver(
                        config.resolver, config.factory
                    )
                else:
                    connection_field.resolve = create_connection_resolver_sync(
                        config.resolver,
                        cast(ConnectionCallable, config.factory),
                    )


def create_connection_resolver(
    resolver: Resolver, factory: ConnectionFactory
) -> ConnectionAwaitable:
    async def resolve_connection(
        obj: Any,
        info: GraphQLResolveInfo,
        *,
        after: Optional[str] = None,
        before: Optional[str] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
        **kwargs: Any,
    ) -> Any:
        connection_args = ConnectionArguments(
            after=after, before=before, first=first, last=last
        )
        data = resolver(obj, info, connection_args, **kwargs)
        if asyncio.iscoroutine(data):
            data = await data
        connection = factory(data, connection_args)
        if asyncio.iscoroutine(connection):
            connection = await cast(Awaitable[Any], connection)
        return connection

    return resolve_connection


def create_connection_resolver_sync(
    resolver: Resolver, factory: ConnectionCallable
) -> ConnectionCallable:
    def resolve_connection(
        obj: Any,
        info: GraphQLResolveInfo,
        *,
        after: Optional[str] = None,
        before: Optional[str] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
        **kwargs: Any,
    ) -> Any:
        connection_args = ConnectionArguments(
            after=after, before=before, first=first, last=last
        )
        data = resolver(obj, info, connection_args, **kwargs)
        return factory(data, connection_args)

    return resolve_connection
