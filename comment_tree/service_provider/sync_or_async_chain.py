from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

TResult = TypeVar("TResult")
TOtherResult = TypeVar("TOtherResult")


@dataclass
class SyncOrAsyncChain(Generic[TResult]):
    _resolve: Callable
    is_async: bool

    def sync_resolve(self) -> TResult:
        if self.is_async:
            raise RuntimeError("Can not resolve async chain with 'sync_resolve'")
        return self._resolve()

    async def async_resolve(self) -> TResult:
        result = self._resolve()
        return await result if self.is_async else result

    @staticmethod
    def from_chain_list(
        chain_list: list["SyncOrAsyncChain[TResult]"],
    ) -> "SyncOrAsyncChain[list[TResult]]":
        is_async = any(chain.is_async for chain in chain_list)
        if is_async:

            async def _resolve():
                return [await chain.async_resolve() for chain in chain_list]

        else:

            def _resolve():
                return [chain.sync_resolve() for chain in chain_list]

        return SyncOrAsyncChain[list[TResult]](_resolve, is_async)

    def append_callable(
        self,
        callable_: Callable,
        callable_is_async: bool,
    ) -> "SyncOrAsyncChain[TOtherResult]":
        new_chain_is_async = self.is_async or callable_is_async
        if new_chain_is_async:

            async def _resolve():
                result = callable_(await self.async_resolve())
                return await result if callable_is_async else result

        else:

            def _resolve():
                return callable_(self.sync_resolve())

        return SyncOrAsyncChain(_resolve, new_chain_is_async)
