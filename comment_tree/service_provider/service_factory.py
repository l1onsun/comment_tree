import inspect
from collections import UserDict
from dataclasses import dataclass
from typing import Protocol, Type

from comment_tree.service_provider.types import BuilderFunc, Service, ServiceClass


class _ServiceProvider(Protocol):
    async def solve(self, service_class: Type[Service]) -> Service:
        ...

    async def solve_sync(self, service_class: Type[Service]) -> Service:
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
        builder_signature = _get_signature_if_annotated_else_raise(build_function)
        return cls(
            service_class=service_class,
            dependencies=[
                parameter.annotation
                for parameter in builder_signature.parameters.values()
            ],
            build_function=build_function,
            is_async=inspect.iscoroutinefunction(build_function),
        )

    async def build_with_provider(self, service_provider: _ServiceProvider) -> Service:
        solved_dependencies: list[Service] = [
            await service_provider.solve(service_class)
            for service_class in self.dependencies
        ]
        return await self.build_with_dependencies(solved_dependencies)

    def build_with_provider_sync(self, service_provider: _ServiceProvider) -> Service:
        solved_dependencies: list[Service] = [
            service_provider.solve_sync(service_class)
            for service_class in self.dependencies
        ]
        return self.build_with_dependencies_sync(solved_dependencies)

    async def build_with_dependencies(
        self, solved_dependencies: list[Service]
    ) -> Service:
        result = self.build_function(*solved_dependencies)
        return await result if self.is_async else result

    async def build_with_dependencies_sync(
        self, solved_dependencies: list[Service]
    ) -> Service:
        if self.is_async:
            raise RuntimeError(
                f"Can't build async factory {self.build_function.__name__}"
            )
        return self.build_function(*solved_dependencies)


def _get_signature_if_annotated_else_raise(
    build_function: BuilderFunc,
) -> inspect.Signature:
    builder_signature: inspect.Signature = inspect.signature(build_function)
    for parameter in builder_signature.parameters.values():
        if parameter.annotation is inspect.Signature.empty:
            raise RuntimeError(
                f"{build_function.__name__} parameter {parameter}"
                f" does not have annotation"
            )
    return builder_signature


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
