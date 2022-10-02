import inspect
from collections import UserDict
from dataclasses import dataclass
from typing import Protocol, Type

from comment_tree.service_provider.types import BuilderFunc, Service, ServiceClass


class _ServiceProvider(Protocol):
    def solve(self, service_class: Type[Service]) -> Service:
        ...


@dataclass
class ServiceFactory:
    service_class: ServiceClass
    dependencies: list[ServiceClass]
    build_function: BuilderFunc

    @classmethod
    def from_builder_function(cls, build_function: BuilderFunc) -> "ServiceFactory":
        builder_signature = _get_signature_if_annotated_else_raise(build_function)
        return cls(
            service_class=builder_signature.return_annotation,
            dependencies=[
                parameter.annotation
                for parameter in builder_signature.parameters.values()
            ],
            build_function=build_function,
        )

    def build_with_provider(self, service_provider: _ServiceProvider) -> Service:
        solved_dependencies: list[Service] = [
            service_provider.solve(service_class) for service_class in self.dependencies
        ]
        return self.build_function(*solved_dependencies)


def _get_signature_if_annotated_else_raise(
    build_function: BuilderFunc,
) -> inspect.Signature:
    builder_signature: inspect.Signature = inspect.signature(build_function)
    if builder_signature.return_annotation is inspect.Signature.empty:
        raise RuntimeError(f"{build_function.__name__} does not have return annotation")
    for parameter in builder_signature.parameters.values():
        if parameter.annotation is inspect.Signature.empty:
            raise RuntimeError(
                f"{build_function.__name__} parameter {parameter}"
                f" does not have annotation"
            )
    return builder_signature


class ServiceFactories(UserDict[ServiceClass, ServiceFactory]):
    def add(self, builder_function: BuilderFunc):
        factory = ServiceFactory.from_builder_function(builder_function)
        self[factory.service_class] = factory
        return builder_function

    def get_factory(self, service_class: Type[Service]) -> ServiceFactory:
        try:
            return self[service_class]
        except KeyError:
            raise RuntimeError(f"no factory found for {service_class}")
