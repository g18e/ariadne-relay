from typing import (
    Any,
    Awaitable,
    Callable,
    cast,
    Dict,
    Generic,
    List,
    NamedTuple,
    Optional,
    TypeVar,
    Union,
)

try:
    from typing import Protocol
except ImportError:  # Python < 3.8
    from typing_extensions import Protocol  # type: ignore

from graphql_relay import connection_from_array_slice
from graphql_relay.connection.arrayconnection import SizedSliceable
from graphql_relay.connection.connectiontypes import (
    EdgeConstructor,
    EdgeType,
    PageInfoConstructor,
    PageInfoType,
)

ConnectionType_T = TypeVar("ConnectionType_T", covariant=True)


class ConnectionConstructor(Protocol[ConnectionType_T]):
    def __call__(
        self,
        *,
        edges: List[EdgeType],
        pageInfo: PageInfoType,
    ) -> ConnectionType_T:
        ...


class ConnectionArguments(NamedTuple):
    after: Optional[str] = None
    before: Optional[str] = None
    first: Optional[int] = None
    last: Optional[int] = None


ConnectionAwaitable = Callable[..., Awaitable[Any]]
ConnectionCallable = Callable[..., Any]
ConnectionFactory = Union[ConnectionAwaitable, ConnectionCallable]


class AsyncConnectionFactoryConstructor(Protocol):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    async def __call__(
        self,
        data: SizedSliceable,
        connection_args: ConnectionArguments,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        ...


class SyncConnectionFactoryConstructor(Protocol):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def __call__(
        self,
        data: SizedSliceable,
        connection_args: ConnectionArguments,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        ...


ConnectionFactoryConstructor = Union[
    AsyncConnectionFactoryConstructor, SyncConnectionFactoryConstructor
]
ConnectionFactoryOrConstructor = Union[ConnectionFactory, ConnectionFactoryConstructor]


class BaseConnection(Generic[ConnectionType_T]):
    def __init__(
        self,
        *,
        connection_type: Optional[ConnectionConstructor[ConnectionType_T]] = None,
        edge_type: Optional[EdgeConstructor] = None,
        page_info_type: Optional[PageInfoConstructor] = None,
    ) -> None:
        self._connection_type = connection_type
        self._edge_type = edge_type
        self._page_info_type = page_info_type

    def create_connection(
        self,
        data: SizedSliceable,
        connection_args: ConnectionArguments,
        *,
        data_length: Optional[int] = None,
    ) -> ConnectionType_T:
        data_length = len(data) if data_length is None else data_length
        kwargs: Dict[str, Any] = dict(array_slice_length=data_length)
        if self._connection_type is not None:
            kwargs["connection_type"] = self._connection_type
        if self._edge_type is not None:
            kwargs["edge_type"] = self._edge_type
        if self._page_info_type is not None:
            kwargs["page_info_type"] = self._page_info_type
        return cast(
            ConnectionType_T,
            connection_from_array_slice(
                data,
                connection_args._asdict(),
                **kwargs,
            ),
        )
