from inspect import isawaitable
from typing import Any, Awaitable, Callable, cast, Optional, Tuple, Union

from ariadne.types import Resolver
from graphql import (
    default_field_resolver,
    GraphQLNamedType,
    GraphQLObjectType,
    GraphQLResolveInfo,
)
from graphql_relay import from_global_id, to_global_id

from .interfaces import RelayInterfaceType
from .objects import RelayObjectType
from .utils import is_coroutine_callable

NodeIdAwaitable = Callable[..., Awaitable[str]]
NodeIdCallable = Callable[..., str]
NodeIdResolver = Union[NodeIdAwaitable, NodeIdCallable]
NodeInstanceAwaitable = Callable[..., Awaitable[Any]]
NodeInstanceCallable = Callable[..., Any]
NodeInstanceResolver = Union[NodeInstanceAwaitable, NodeInstanceCallable]
NodeTypenameAwaitable = Callable[..., Awaitable[str]]
NodeTypenameCallable = Callable[..., str]
NodeTypenameResolver = Union[NodeTypenameAwaitable, NodeTypenameCallable]

ID_RESOLVER = "ariadne_relay_node_id_resolver"
INSTANCE_RESOLVER = "ariadne_relay_node_instance_resolver"
TYPENAME_RESOLVER = "ariadne_relay_node_typename_resolver"


async def resolve_node_query(
    _: None,
    info: GraphQLResolveInfo,
    *,
    id: str,  # noqa: A002
) -> Any:
    instance_resolver_and_node_id = _get_instance_resolver_and_node_id(info, id)
    if instance_resolver_and_node_id:
        instance_resolver, node_id = instance_resolver_and_node_id
        node_instance = instance_resolver(node_id, info)
        if isawaitable(node_instance):
            node_instance = await node_instance
        return node_instance
    return None


def resolve_node_query_sync(
    _: None,
    info: GraphQLResolveInfo,
    *,
    id: str,  # noqa: A002
) -> Any:
    instance_resolver_and_node_id = _get_instance_resolver_and_node_id(info, id)
    if instance_resolver_and_node_id:
        instance_resolver, node_id = instance_resolver_and_node_id
        return instance_resolver(node_id, info)
    return None


class NodeType:
    name: str
    _resolve_id: Optional[NodeIdResolver]
    _resolve_instance: Optional[NodeInstanceResolver]
    _resolve_typename: Optional[NodeTypenameResolver]

    def bind_node_resolvers_to_graphql_type(
        self, graphql_type: GraphQLObjectType, replace_existing: bool = True
    ) -> None:
        if "id" not in graphql_type.fields:
            raise ValueError(f"Field id is not defined on type {self.name}")
        if graphql_type.fields["id"].resolve is None or replace_existing:
            if is_coroutine_callable(self._resolve_typename) or is_coroutine_callable(
                self._resolve_id
            ):
                graphql_type.fields["id"].resolve = self._resolve_node_id_field
            else:
                graphql_type.fields["id"].resolve = self._resolve_node_id_field_sync
        if self._resolve_id is not None:
            _set_extension(
                graphql_type,
                ID_RESOLVER,
                self._resolve_id,
                replace_existing,
            )
        if self._resolve_instance is not None and graphql_type.name == self.name:
            _set_extension(
                graphql_type,
                INSTANCE_RESOLVER,
                self._resolve_instance,
                replace_existing,
            )
        if self._resolve_typename is not None:
            _set_extension(
                graphql_type,
                TYPENAME_RESOLVER,
                self._resolve_typename,
                replace_existing,
            )

    async def _resolve_node_id_field(self, obj: Any, info: GraphQLResolveInfo) -> str:
        node_typename = self._resolve_node_typename(obj, info)
        if isawaitable(node_typename):
            node_typename = await cast(Awaitable[str], node_typename)
        node_id = self._resolve_node_id(obj, info)
        if isawaitable(node_id):
            node_id = await cast(Awaitable[str], node_id)
        return to_global_id(cast(str, node_typename), cast(str, node_id))

    def _resolve_node_id_field_sync(self, obj: Any, info: GraphQLResolveInfo) -> str:
        node_typename = cast(str, self._resolve_node_typename(obj, info))
        node_id = cast(str, self._resolve_node_id(obj, info))
        return to_global_id(node_typename, node_id)

    def _resolve_node_id(
        self,
        obj: Any,
        info: GraphQLResolveInfo,
    ) -> Union[str, Awaitable[str]]:
        resolve_id = cast(
            Optional[NodeIdResolver],
            _get_extension(info.parent_type, ID_RESOLVER),
        )
        if resolve_id:
            return resolve_id(obj, info)
        return cast(str, default_field_resolver(obj, info))

    def _resolve_node_typename(
        self,
        obj: Any,
        info: GraphQLResolveInfo,
    ) -> Union[str, Awaitable[str]]:
        resolve_typename = cast(
            Optional[NodeTypenameResolver],
            _get_extension(info.parent_type, TYPENAME_RESOLVER),
        )
        if resolve_typename:
            return resolve_typename(obj, info)
        return info.parent_type.name

    def set_id_resolver(self, id_resolver: NodeIdResolver) -> NodeIdResolver:
        self._resolve_id = id_resolver
        return id_resolver

    def set_instance_resolver(
        self, instance_resolver: NodeInstanceResolver
    ) -> NodeInstanceResolver:
        self._resolve_instance = instance_resolver
        return instance_resolver

    def set_typename_resolver(
        self,
        typename_resolver: NodeTypenameResolver,
    ) -> NodeTypenameResolver:
        self._resolve_typename = typename_resolver
        return typename_resolver

    # Alias resolvers for consistent decorator API
    id_resolver = set_id_resolver
    instance_resolver = set_instance_resolver
    typename_resolver = set_typename_resolver


def _get_extension(graphql_type: GraphQLNamedType, name: str) -> Any:
    if not isinstance(graphql_type.extensions, dict):
        return None
    return graphql_type.extensions.get(name)


def _set_extension(
    graphql_type: GraphQLNamedType,
    name: str,
    value: Any,
    replace_existing: bool,
) -> None:
    graphql_type.extensions = graphql_type.extensions or {}
    if name not in graphql_type.extensions or replace_existing:
        graphql_type.extensions[name] = value


def _get_instance_resolver_and_node_id(
    info: GraphQLResolveInfo,
    raw_id: str,
) -> Optional[Tuple[NodeInstanceResolver, str]]:
    node_type_name, node_id = from_global_id(raw_id)
    node_type = info.schema.type_map.get(node_type_name)
    if node_type:
        instance_resolver = _get_extension(node_type, INSTANCE_RESOLVER)
        if instance_resolver:
            return instance_resolver, node_id
    return None


class NodeObjectType(NodeType, RelayObjectType):
    def __init__(
        self,
        name: str,
        *,
        id_resolver: Optional[NodeIdResolver] = None,
        instance_resolver: Optional[NodeInstanceResolver] = None,
        typename_resolver: Optional[NodeTypenameResolver] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name)
        self._resolve_id = id_resolver
        self._resolve_instance = instance_resolver
        self._resolve_typename = typename_resolver

    def bind_resolvers_to_graphql_type(
        self,
        graphql_type: GraphQLObjectType,
        replace_existing: bool = True,
    ) -> None:
        super().bind_resolvers_to_graphql_type(graphql_type, replace_existing)
        self.bind_node_resolvers_to_graphql_type(graphql_type, replace_existing)


class NodeInterfaceType(NodeType, RelayInterfaceType):
    def __init__(
        self,
        name: str,
        type_resolver: Optional[Resolver] = None,
        *,
        id_resolver: Optional[NodeIdResolver] = None,
        instance_resolver: Optional[NodeInstanceResolver] = None,
        typename_resolver: Optional[NodeTypenameResolver] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name, type_resolver)
        self._resolve_id = id_resolver
        self._resolve_instance = instance_resolver
        self._resolve_typename = typename_resolver

    def bind_resolvers_to_graphql_type(
        self,
        graphql_type: GraphQLObjectType,
        replace_existing: bool = True,
    ) -> None:
        super().bind_resolvers_to_graphql_type(graphql_type, replace_existing)
        self.bind_node_resolvers_to_graphql_type(graphql_type, replace_existing)
