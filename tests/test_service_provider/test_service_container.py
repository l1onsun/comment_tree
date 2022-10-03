from dataclasses import dataclass

import pytest

from comment_tree.service_provider.service_factory import ServiceFactories
from comment_tree.service_provider.service_provider import ServiceProvider


@dataclass
class ServiceA:
    some_str: str


@dataclass
class ServiceB:
    a: ServiceA


@dataclass
class ServiceC:
    a: ServiceA
    b: ServiceB
    is_some: bool


factories = ServiceFactories()


@factories.add(ServiceA)
def build_some_service_a() -> ServiceA:
    return ServiceA("some_str")


@factories.add(ServiceB)
async def build_some_service_b(a: ServiceA) -> ServiceB:
    return ServiceB(a)


@factories.add(ServiceC)
def build_some_service_c(a: ServiceA, b: ServiceB) -> ServiceC:
    return ServiceC(a, b, is_some=True)


@pytest.mark.asyncio
async def test_provider_solve_all():
    provider = ServiceProvider(factories)
    await provider.solve_all()
    assert provider.services.keys() == {
        ServiceProvider,
        ServiceA,
        ServiceB,
        ServiceC,
    }
    assert provider.provide(ServiceC).a.some_str == "some_str"


def test_provider_solve_sync():
    provider = ServiceProvider(factories)
    service_a = provider.solve_sync(ServiceA)
    assert service_a.some_str == "some_str"
