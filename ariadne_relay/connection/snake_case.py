from dataclasses import dataclass
from typing import List, Optional

try:
    from typing import Protocol
except ImportError:  # Python < 3.8
    from typing_extensions import Protocol  # type: ignore

from graphql_relay.connection.arrayconnection import SizedSliceable
from graphql_relay.connection.connectiontypes import (
    ConnectionCursor,
    EdgeConstructor,
    EdgeType,
    PageInfoConstructor,
    PageInfoType,
)

from .base import (
    BaseConnection,
    ConnectionArguments,
    ConnectionConstructor,
    ConnectionType_T,
)


class SnakeCasePageInfoType(Protocol):
    @property
    def start_cursor(self) -> Optional[ConnectionCursor]:
        ...

    @property
    def end_cursor(self) -> Optional[ConnectionCursor]:
        ...

    @property
    def has_previous_page(self) -> Optional[bool]:
        ...

    @property
    def has_next_page(self) -> Optional[bool]:
        ...


class SnakeCaseConnectionType(Protocol):
    @property
    def edges(self) -> List[EdgeType]:
        ...

    @property
    def page_info(self) -> SnakeCasePageInfoType:
        ...


@dataclass(frozen=True, init=False)
class PageInfo:
    start_cursor: Optional[ConnectionCursor]
    end_cursor: Optional[ConnectionCursor]
    has_previous_page: Optional[bool]
    has_next_page: Optional[bool]

    def __init__(
        self,
        *,
        startCursor: Optional[ConnectionCursor] = None,
        endCursor: Optional[ConnectionCursor] = None,
        hasPreviousPage: Optional[bool] = None,
        hasNextPage: Optional[bool] = None,
    ) -> None:
        object.__setattr__(self, "start_cursor", startCursor)
        object.__setattr__(self, "end_cursor", endCursor)
        object.__setattr__(self, "has_previous_page", hasPreviousPage)
        object.__setattr__(self, "has_next_page", hasNextPage)


@dataclass(frozen=True, init=False)
class Connection:
    edges: List[EdgeType]
    page_info: SnakeCasePageInfoType

    def __init__(
        self,
        *,
        edges: List[EdgeType],
        pageInfo: PageInfoType,
    ) -> None:
        object.__setattr__(self, "edges", edges)
        object.__setattr__(self, "page_info", pageInfo)


class SnakeCaseBaseConnection(BaseConnection[ConnectionType_T]):
    def __init__(
        self,
        *,
        connection_type: Optional[ConnectionConstructor[ConnectionType_T]] = Connection,
        edge_type: Optional[EdgeConstructor] = None,
        page_info_type: Optional[PageInfoConstructor] = None,
    ) -> None:
        self._connection_type = connection_type
        self._edge_type = edge_type
        self._page_info_type = page_info_type or PageInfo


class SnakeCaseConnection(SnakeCaseBaseConnection[Connection]):
    def __call__(
        self,
        data: SizedSliceable,
        connection_args: ConnectionArguments,
        *,
        data_length: Optional[int] = None,
    ) -> SnakeCaseConnectionType:
        return self.create_connection(data, connection_args, data_length=data_length)
