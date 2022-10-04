import inspect
from collections import UserDict
from dataclasses import dataclass
from typing import Protocol, Type

from comment_tree.service_provider.sync_or_async_chain import SyncOrAsyncChain
from comment_tree.service_provider.types import BuilderFunc, Service, ServiceClass


class _ServiceProvider(Protocol):
    def solve_to_chain(self, service_class: Type[Service]) -> SyncOrAsyncChain[Service]:
        ...


@dataclass
class ServiceFactory:
    service_class: ServiceClass
    dependencies: list[ServiceClass]
    build_function: BuilderFunc
    is_async: bool

    @classmethod
    def from_builder_function(
        cls, service_class: ServiceClass, build_function: BuilderFunc
    ) -> "ServiceFactory":
        return cls(
            service_class=service_class,
            dependencies=_get_annotations_or_raise(build_function),
            build_function=build_function,
            is_async=inspect.iscoroutinefunction(build_function),
        )

    def build_to_chain(
        self, service_provider: _ServiceProvider
    ) -> SyncOrAsyncChain[Service]:
        dependencies_chain = self.solve_dependencies_to_chain(service_provider)
        return dependencies_chain.append_callable(
            lambda result: self.build_function(*result),
            callable_is_async=self.is_async,
        )

    def solve_dependencies_to_chain(
        self, service_provider: _ServiceProvider
    ) -> SyncOrAsyncChain[list[Service]]:
        return SyncOrAsyncChain.from_chain_list(
            [
                service_provider.solve_to_chain(service_class)
                for service_class in self.dependencies
            ]
        )


def _get_annotations_or_raise(
    build_function: BuilderFunc,
) -> list[ServiceClass]:
    builder_signature: inspect.Signature = inspect.signature(build_function)
    for parameter in builder_signature.parameters.values():
        if parameter.annotation is inspect.Signature.empty:
            raise RuntimeError(
                f"{build_function.__name__} parameter {parameter}"
                f" does not have annotation"
            )
    return [parameter.annotation for parameter in builder_signature.parameters.values()]


class ServiceFactories(UserDict[ServiceClass, ServiceFactory]):
    def add(self, service_class: ServiceClass):
        if service_class in self:
            raise RuntimeError(f"{service_class} already has factory")
        return self._decorator(service_class)

    def override(self, service_class: ServiceClass):
        if service_class not in self:
            raise RuntimeError(f"Can't find {service_class} factory to override")
        return self._decorator(service_class)

    def _decorator(self, service_class: ServiceClass):
        def decorator(builder_function: BuilderFunc):
            factory = ServiceFactory.from_builder_function(
                service_class, builder_function
            )
            self[factory.service_class] = factory
            return builder_function

        return decorator

    def get_factory(self, service_class: Type[Service]) -> ServiceFactory:
        try:
            return self[service_class]
        except KeyError:
            raise RuntimeError(f"no factory found for {service_class}")
