from typing import Any, Callable, Type, TypeAlias, TypeVar

TService = TypeVar("TService")
BuilderFunc: TypeAlias = Callable

Service: TypeAlias = Any
ServiceClass: TypeAlias = Type[Service]
