from typing import TypeVar, Union

from graphql_relay.connection.connectiontypes import (
    ConnectionType as ReferenceConnectionType,
)

from .base import BaseConnection, ConnectionArguments
from .snake_case import SnakeCaseConnectionType

ConnectionType = Union[ReferenceConnectionType, SnakeCaseConnectionType]
ConnectionType_T = TypeVar("ConnectionType_T", bound=ConnectionType)


class ConnectionProxy(BaseConnection[ConnectionType]):
    def __call__(
        self, data: ConnectionType_T, connection_args: ConnectionArguments
    ) -> ConnectionType_T:
        return data
