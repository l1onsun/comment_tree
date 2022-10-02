from typing import Any, Callable, Type, TypeAlias, TypeVar

TService = TypeVar("TService")
BuilderFunc: TypeAlias = Callable

Service: TypeAlias = Any
ServiceClass: TypeAlias = Type[Service]


# ToDo: TServiceClass = Type[TService]
# There is mypy bag, now TypeAlias on TypeVar is not working
# github issue: https://github.com/python/mypy/issues/13449
