![Build Status](https://github.com/g18e/ariadne-relay/actions/workflows/tests.yml/badge.svg?branch=main)
[![Codecov](https://codecov.io/gh/g18e/ariadne-relay/branch/main/graph/badge.svg)](https://codecov.io/gh/g18e/ariadne-relay)

- - - - -

# Ariadne-Relay

Ariadne-Relay provides a toolset for implementing [GraphQL](http://graphql.github.io/) servers
in Python that conform to the [Relay specification](https://relay.dev/docs/guides/graphql-server-specification/),
using the [Ariadne](https://ariadnegraphql.org) library.

The goals of Ariadne-Relay are to:

- Make building Relay features feel as close as possible to core Ariadne
- Minimize boilerplate for common cases
- Make it as easy as possible to fully customize and optimize a Relay deployment


## Installation

Ariadne-Relay can be installed with pip:

```console
pip install ariadne-relay
```


## Quickstart

If you are not familiar with Ariadne usage in general, the [Araidne docs](https://ariadnegraphql.org/docs/intro) are the best place to start.

Here's a variation of the Ariadne quickstart as a Relay implementation:

```python
from dataclasses import dataclass

from ariadne import gql, InterfaceType, make_executable_schema
from ariadne.asgi import GraphQL

from ariadne_relay import NodeObjectType, RelayQueryType, resolve_node_query


# Using a dataclass for Person rather than a dict,
# since it works better with a Node implementation
@dataclass
class Person:
    id: int
    firstName: str
    lastName: str
    age: int


type_defs = gql(
    """
    type Query {
        node(id: ID!): Node
        people(
            after: String
            before: String
            first: Int
            last: Int
        ): PeopleConnection!
    }

    interface Node {
        id: ID!
    }

    type PageInfo {
        hasNextPage: Boolean!
        hasPreviousPage: Boolean!
        startCursor: String
        endCursor: String
    }

    type Person implements Node {
        id: ID!
        firstName: String
        lastName: String
        age: Int
        fullName: String
    }

    type PersonEdge {
        cursor: String!
        node: Person
    }

    type PeopleConnection {
        pageInfo: PageInfo!
        edges: [PersonEdge]!
    }
"""
)

# A mock data store of people
people_data = {
    "1": Person(id=1, firstName="John", lastName="Doe", age=21),
    "2": Person(id=2, firstName="Bob", lastName="Boberson", age=24),
}

# Instead of using Ariadne's QueryType, use the Relay-enabled
# RelayQueryType class
query = RelayQueryType()

# resolve_node_query is provided as a resolver for Query.node()
query.set_field("node", resolve_node_query)

# Connection resolvers work exactly like standard Ariadne resolvers,
# except they convert the returned value to a connection structure
@query.connection("people")
def resolve_people(*_):
    return list(people_data.values())


# Define the Node interface
node = InterfaceType("Node")

# Add a Node type resolver
@node.type_resolver
def resolve_node_type(obj, *_):
    return obj.__class__.__name__


# Instead of Ariadne's ObjectType, use the Relay-enabled
# NodeObjectType class for types that implement Node
person = NodeObjectType("Person")


# Add an instance_resolver to define how an instance of
# this type is retrieved, given an id
@person.instance_resolver
def resolve_person_instance(id, *_):
    return people_data.get(id)


@person.field("fullName")
def resolve_person_fullname(person, *_):
    return "%s %s" % (person.firstName, person.lastName)


# Create executable GraphQL schema
schema = make_executable_schema(type_defs, node, query, person)

# Create an ASGI app using the schema, running in debug mode
app = GraphQL(schema, debug=True)
```


## Connection Factories

The heavy lifting of generating a connection structure in a `RelayObjectType.connection()`
is performed by the chosen factory.  It is possible to specify a factory of your chosing
by passing it in the call to `connection()`:
```
@query.connection("people", factory=CustomConnection)
```

### ReferenceConnection
The default that is used when `factory` is not overridden is `ReferenceConnection`.  This
implementation wraps `graphql_relay.connection_from_array_slice()` and provides the expected
behavior of the Relay reference implementation.


### SnakeCaseConnection
The `SnakeCaseConnection` factory provides equivalent functionality to `ReferenceConnection`,
but returns a connection structure with snake-case field names.  This is useful in conjunction
with `ariadne.snake_case_fallback_resolvers`.


### ConnectionProxy
The `ConnectionProxy` factory can be used to proxy an already-formed connection structure,
for example a payload that was produced by an external GraphQL endpoint. It simply passes through
the data untouched.


### Custom Factories
Many deployments will benefit from customizing the connection factory. One example would be
properly integrating a given ORM like Djano. Other examples might be extending the functionality
of connections, or customizing how cursors are formed. The `BaseConnection` and `SnakeCaseBaseConnection`
classes can be useful for this purpose.


## Contributing
Please see [CONTRIBUTING.md](CONTRIBUTING.md).
