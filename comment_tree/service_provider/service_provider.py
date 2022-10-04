from dataclasses import dataclass, field
from typing import Type

from comment_tree.service_provider.service_factory import ServiceFactories
from comment_tree.service_provider.sync_or_async_chain import SyncOrAsyncChain
from comment_tree.service_provider.types import Service, ServiceClass, TService

_service_locked_sentinel = object()


@dataclass
class ServiceProvider:
    factories: ServiceFactories
    services: dict[ServiceClass, Service] = field(default_factory=dict)

    def __post_init__(self):
        self.services[ServiceProvider] = self

    def provide(self, service_class: Type[TService]) -> TService:
        try:
            return self._get_service(service_class)
        except KeyError:
            raise RuntimeError(f"Service {service_class} not found")

    async def solve_async(self, service_class: Type[TService]) -> TService:
        return await self.solve_to_chain(service_class).async_resolve()

    def solve_sync(self, service_class: Type[TService]) -> TService:
        return self.solve_to_chain(service_class).sync_resolve()

    async def solve_all_async(self):
        for service_class in self.factories:
            await self.solve_async(service_class)

    def solve_all_sync(self):
        for service_class in self.factories:
            self.solve_sync(service_class)

    def solve_to_chain(
        self, service_class: Type[TService]
    ) -> SyncOrAsyncChain[TService]:
        try:
            service: Service = self._get_service(service_class)
            chain = SyncOrAsyncChain[TService](lambda: service, is_async=False)
        except KeyError:
            chain = self._build_to_chain(service_class)
        return chain

    def _build_to_chain(
        self, service_class: Type[Service]
    ) -> SyncOrAsyncChain[Service]:
        self.services[service_class] = _service_locked_sentinel
        return (
            self.factories.get_factory(service_class)
            .build_to_chain(self)
            .append_callable(
                lambda service: self._set_service(service_class, service),
                callable_is_async=False,
            )
        )

    def _set_service(self, service_class: ServiceClass, service: Service) -> Service:
        self.services[service_class] = service
        return service

    def _get_service(self, service_class: Type[Service]) -> Service:
        service = self.services[service_class]
        self._check_not_locked(service_class, service)
        return service

    def _check_not_locked(self, service_class: ServiceClass, service: Service):
        if service is _service_locked_sentinel:
            raise RuntimeError(
                f"Service {service_class} is locked (probably cyclic dependencies)"
            )
