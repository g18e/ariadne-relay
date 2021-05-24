# Contributing

Before contributing to Ariadne-Relay, please familiarize yourself with the project's code of conduct, available in the [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) file.


## Reporting bugs, asking for help, offering feedback and ideas

Please use [GitHub issues](https://github.com/g18e/ariadne-relay/issues) and [GitHub discussions](https://github.com/g18e/ariadne-relay/discussions).


## Development setup

Ariadne-Relay is written to support Python 3.6, 3.7, 3.8, and 3.9.

The codebase is formatted with [Black](https://black.readthedocs.io/).  It is also linted with [flake8] and strictly type-checked with [mypy](http://mypy-lang.org/index.html).

Tests use [pytest](https://pytest.org/) with [Codecov](https://codecov.io/gh/g18e/ariadne-relay) for monitoring coverage.

Dev requirements can be installed using `requirements-dev.txt`.


## Goals

### Tests

Before any further feature work, test coverage needs to be at or near 100%.


### 0.1.0 Release

Beyond tests, the immediate development priority is stabilizing the API and shipping the first release.
