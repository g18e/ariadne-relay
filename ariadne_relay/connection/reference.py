from typing import Optional

from graphql_relay.connection.arrayconnection import SizedSliceable
from graphql_relay.connection.connectiontypes import ConnectionType

from .base import BaseConnection, ConnectionArguments


class ReferenceConnection(BaseConnection[ConnectionType]):
    def __call__(
        self,
        data: SizedSliceable,
        connection_args: ConnectionArguments,
        *,
        data_length: Optional[int] = None,
    ) -> ConnectionType:
        return self.create_connection(data, connection_args, data_length=data_length)
