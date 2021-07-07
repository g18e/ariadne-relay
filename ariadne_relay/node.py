import asyncio
from typing import Any, Awaitable, Callable, cast, Optional, Tuple, Union

from graphql import default_field_resolver, GraphQLObjectType, GraphQLResolveInfo
from graphql_relay import from_global_id, to_global_id

from .objects import RelayObjectType
from .utils import is_coroutine_callable

NodeIdAwaitable = Callable[..., Awaitable[str]]
NodeIdCallable = Callable[..., str]
NodeIdResolver = Union[NodeIdAwaitable, NodeIdCallable]
NodeInstanceAwaitable = Callable[..., Awaitable[Any]]
NodeInstanceCallable = Callable[..., Any]
NodeInstanceResolver = Union[NodeInstanceAwaitable, NodeInstanceCallable]

INSTANCE_RESOLVER = "ariadne_relay_node_instance_resolver"


class NodeObjectType(RelayObjectType):
    _resolve_id: NodeIdResolver
    _resolve_instance: Optional[NodeInstanceResolver]

    def __init__(
        self,
        name: str,
        *,
        id_resolver: NodeIdResolver = default_field_resolver,
        instance_resolver: Optional[NodeInstanceResolver] = None,
    ) -> None:
        super().__init__(name)
        self._resolve_id = id_resolver
        self._resolve_instance = instance_resolver

    def bind_resolvers_to_graphql_type(
        self, graphql_type: GraphQLObjectType, replace_existing: bool = True
    ) -> None:
        super().bind_resolvers_to_graphql_type(graphql_type, replace_existing)
        if "id" not in graphql_type.fields:
            raise ValueError(f"Field id is not defined on type {self.name}")
        if graphql_type.fields["id"].resolve is None or replace_existing:
            if is_coroutine_callable(self._resolve_id):
                graphql_type.fields["id"].resolve = self._resolve_node_id_field
            else:
                graphql_type.fields["id"].resolve = self._resolve_node_id_field_sync
        if self._resolve_instance is not None:
            graphql_type.extensions = graphql_type.extensions or {}
            graphql_type.extensions[INSTANCE_RESOLVER] = self._resolve_instance

    async def _resolve_node_id_field(self, obj: Any, info: GraphQLResolveInfo) -> str:
        resolve_id = cast(NodeIdAwaitable, self._resolve_id)
        return to_global_id(self.name, await resolve_id(obj, info))

    def _resolve_node_id_field_sync(self, obj: Any, info: GraphQLResolveInfo) -> str:
        resolve_id = cast(NodeIdCallable, self._resolve_id)
        return to_global_id(self.name, resolve_id(obj, info))

    def set_id_resolver(self, id_resolver: NodeIdResolver) -> NodeIdResolver:
        self._resolve_id = id_resolver
        return id_resolver

    def set_instance_resolver(
        self, instance_resolver: NodeInstanceResolver
    ) -> NodeInstanceResolver:
        self._resolve_instance = instance_resolver
        return instance_resolver

    # Alias resolvers for consistent decorator API
    id_resolver = set_id_resolver
    instance_resolver = set_instance_resolver


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
        if asyncio.iscoroutine(node_instance):
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


def _get_instance_resolver_and_node_id(
    info: GraphQLResolveInfo,
    raw_id: str,
) -> Optional[Tuple[NodeInstanceResolver, str]]:
    try:
        node_type_name, node_id = from_global_id(raw_id)
    except Exception as e:
        raise ValueError(f'Invalid ID "{raw_id}"') from e
    node_type = info.schema.type_map.get(node_type_name)
    extensions = getattr(node_type, "extensions", None) or {}
    instance_resolver = extensions.get(INSTANCE_RESOLVER)
    if instance_resolver is None:
        return None
    return instance_resolver, node_id
