"""
Redis-backed cache for job search results.
"""
import hashlib
import json
import logging
from typing import Any, Optional

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_PREFIX = "job_search"
DEFAULT_TTL = 3600  # 1 hour


def _cache_key(job_id: str, k: int, description_hash: str = "") -> str:
    # Django cache adds KEY_PREFIX, we use a short key
    if job_id:
        raw = f"{CACHE_PREFIX}:job:{job_id}:k:{k}"
    else:
        raw = f"{CACHE_PREFIX}:desc:{description_hash}:k:{k}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached_search(job_id: Optional[str], k: int, description: Optional[str] = None) -> Optional[list]:
    """Retrieve cached job search results."""
    try:
        desc_hash = hashlib.sha256((description or "").encode()).hexdigest() if description else ""
        key = _cache_key(job_id or "", k, desc_hash)
        data = cache.get(key)
        if data is not None:
            return json.loads(data) if isinstance(data, str) else data
    except Exception as e:
        logger.warning(f"Cache get failed: {e}")
    return None


def set_cached_search(
    job_id: Optional[str],
    k: int,
    results: list,
    description: Optional[str] = None,
    ttl: int = DEFAULT_TTL,
) -> None:
    """Store job search results in cache."""
    try:
        desc_hash = hashlib.sha256((description or "").encode()).hexdigest() if description else ""
        key = _cache_key(job_id or "", k, desc_hash)
        cache.set(key, json.dumps(results), timeout=ttl)
    except Exception as e:
        logger.warning(f"Cache set failed: {e}")
