"""Async pagination primitives."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class Page(Generic[T]):
    """A single page of data returned by an endpoint."""

    items: list[T]
    has_more: bool
    next_page: int | None


PageFetcher = Callable[[int, int], Awaitable[Page[T]]]


class AsyncPager(Generic[T]):
    """Iterate over page-based list endpoints.

    Example:
        ```python
        pager = AsyncPager(fetch_page=fetch_page, page_size=200)
        async for item in pager:
            ...
        ```
    """

    def __init__(
        self, *, fetch_page: PageFetcher[T], page_size: int = 200, start_page: int = 1
    ) -> None:
        self._fetch_page = fetch_page
        self._page_size = page_size
        self._start_page = start_page

    async def __aiter__(self) -> AsyncIterator[T]:
        page_num = self._start_page
        while True:
            page = await self._fetch_page(page_num, self._page_size)
            for item in page.items:
                yield item

            if not page.has_more:
                break

            if page.next_page is None:
                page_num += 1
            else:
                page_num = page.next_page
