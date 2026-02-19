from __future__ import annotations

from zoho.core.pagination import AsyncPager, Page


async def test_async_pager_iterates_all_pages() -> None:
    calls: list[int] = []

    async def fetch_page(page: int, page_size: int) -> Page[int]:
        _ = page_size
        calls.append(page)
        if page == 1:
            return Page(items=[1, 2], has_more=True, next_page=2)
        return Page(items=[3], has_more=False, next_page=None)

    pager = AsyncPager(fetch_page=fetch_page, page_size=200)
    values = [value async for value in pager]

    assert values == [1, 2, 3]
    assert calls == [1, 2]
