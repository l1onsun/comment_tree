import functools
import inspect
from typing import Any, Callable, Container, Type

from comment_tree.service_provider.types import Service


def partial_function_resolve(
    function: Callable,
    services_to_resolve: Container[Type[Service]],
    resolve_by_callable: Callable[[Type[Service]], Any],
):
    partial_kwargs = {}
    for parameter in inspect.signature(function).parameters.values():
        if parameter.annotation in services_to_resolve:
            partial_kwargs[parameter.name] = resolve_by_callable(parameter.annotation)

    return functools.partial(function, **partial_kwargs)
