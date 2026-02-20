from __future__ import annotations

import json
import time
from pathlib import Path

from zoho.core.discovery_cache import DiscoveryDiskCache


def test_discovery_cache_roundtrip(tmp_path: Path) -> None:
    cache = DiscoveryDiskCache(base_dir=tmp_path / "cache", ttl_seconds=60)
    entries = [{"api_name": "Leads"}, {"api_name": "Contacts"}]

    cache.save(
        product="crm",
        resource="modules",
        scope="tenant_a:US:production",
        entries=entries,
    )
    loaded = cache.load(product="crm", resource="modules", scope="tenant_a:US:production")

    assert loaded == entries


def test_discovery_cache_expiry(tmp_path: Path) -> None:
    cache = DiscoveryDiskCache(base_dir=tmp_path / "cache", ttl_seconds=60)
    entries = [{"link_name": "inventory-app"}]

    cache.save(
        product="creator",
        resource="applications",
        scope="tenant_a:US:production",
        entries=entries,
    )

    cache_files = list((tmp_path / "cache" / "creator").glob("*.json"))
    assert cache_files

    payload = json.loads(cache_files[0].read_text(encoding="utf-8"))
    payload["expires_at"] = time.time() - 1
    cache_files[0].write_text(json.dumps(payload), encoding="utf-8")

    assert (
        cache.load(product="creator", resource="applications", scope="tenant_a:US:production")
        is None
    )


def test_discovery_cache_uses_safe_file_components(tmp_path: Path) -> None:
    cache = DiscoveryDiskCache(base_dir=tmp_path / "cache", ttl_seconds=60)

    cache.save(
        product="crm",
        resource="modules:list",
        scope="tenant/a:US:production",
        entries=[{"api_name": "Leads"}],
    )

    cache_files = list((tmp_path / "cache" / "crm").glob("*.json"))
    assert len(cache_files) == 1

    file_name = cache_files[0].name
    assert ":" not in file_name
    assert "/" not in file_name
