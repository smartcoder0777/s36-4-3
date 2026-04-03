"""URL utilities: seed preservation, localhost validation, normalization."""
from __future__ import annotations
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qs, urlencode, parse_qsl, urlparse, urlunparse

_LOCALHOST_HOSTS = {"localhost", "127.0.0.1", "::1"}
_ALLOWED_SCHEMES = {"http", "https"}


def extract_seed(url: str) -> str | None:
    if not url:
        return None
    params = parse_qs(urlsplit(url).query)
    seed_vals = params.get("seed")
    return seed_vals[0] if seed_vals else None


def preserve_seed(target_url: str, current_url: str) -> str:
    seed = extract_seed(current_url)
    if seed is None:
        return target_url
    if extract_seed(target_url) == seed:
        return target_url
    parts = urlsplit(target_url)
    params = [(k, v) for k, v in parse_qsl(parts.query) if k != "seed"]
    params.append(("seed", seed))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(params), parts.fragment))


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    hostname = parts.hostname
    if hostname and hostname not in _LOCALHOST_HOSTS:
        port = parts.port
        new_netloc = f"localhost:{port}" if port else "localhost"
        return urlunsplit((parts.scheme, new_netloc, parts.path, parts.query, parts.fragment))
    return url


def is_localhost_url(url: str) -> bool:
    parts = urlsplit(url)
    if parts.scheme not in _ALLOWED_SCHEMES:
        return False
    hostname = parts.hostname
    return hostname is not None and hostname in _LOCALHOST_HOSTS


def same_page(url_a: str, url_b: str) -> bool:
    a, b = urlsplit(url_a), urlsplit(url_b)
    return a.path == b.path and a.query == b.query


def resolve_url(url: str, base_url: str) -> str:
    """Resolve relative URLs against base (validator page URL)."""
    try:
        u = str(url or "").strip()
        b = str(base_url or "").strip()
        if not u:
            return ""
        return urljoin(b, u) if b else u
    except Exception:
        return str(url or "").strip()


def reconcile_nav_origin_with_base(resolved: str, base: str) -> str:
    """Align scheme/host/port with *base* when model omits explicit port on localhost."""
    try:
        r = urlparse((resolved or "").strip())
        b = urlparse((base or "").strip())
        if not b.netloc or not r.netloc:
            return (resolved or "").strip()
        if (r.scheme or "").lower() != (b.scheme or "").lower():
            return (resolved or "").strip()
        rh = (r.hostname or "").lower()
        bh = (b.hostname or "").lower()
        if not rh or not bh or rh != bh:
            return (resolved or "").strip()
        if r.netloc == b.netloc:
            return (resolved or "").strip()
        if r.port is not None and b.port is not None and r.port != b.port:
            return (resolved or "").strip()
        if r.port is None and b.port is not None:
            fixed = r._replace(netloc=b.netloc)
            return urlunparse(fixed)
        return (resolved or "").strip()
    except Exception:
        return (resolved or "").strip()


def enforce_same_origin(url_value: str, base: str) -> str:
    """Pin absolute URL origin to evaluator page (avoid wrong port on localhost)."""
    try:
        u = urlparse((url_value or "").strip())
        b = urlparse((base or "").strip())
        if not b.scheme or not b.netloc:
            return (url_value or "").strip()
        if not u.netloc:
            return (url_value or "").strip()
        fixed = u._replace(scheme=b.scheme, netloc=b.netloc)
        return urlunparse(fixed)
    except Exception:
        return (url_value or "").strip()
