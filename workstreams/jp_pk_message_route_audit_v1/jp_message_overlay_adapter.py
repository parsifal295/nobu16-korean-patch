#!/usr/bin/env python3
"""Fail-closed in-memory adapter for applying audited Korean rows to JP bins.

This module intentionally has no file-writing CLI.  Callers must supply an
official JP resource and project-authored replacement strings, and must also
pass the route assigned by the audit.  Rows classified as blocked or missing
are rejected before any rebuild is attempted.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Mapping


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[2]
sys.path[:0] = [
    str(REPO_ROOT / "tools"),
    str(REPO_ROOT / "workstreams" / "msggame"),
    str(REPO_ROOT / "workstreams" / "switch_msgbre_v11"),
]

from msggame_format import rebuild_packed_with_literals  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
from strdata_container import parse_strdata, rebuild_strdata  # noqa: E402


SAFE_ROUTES = frozenset(("exact_direct_transfer",))
COMMON_RESOURCES = frozenset(
    ("msgui", "msgev", "msgdata", "msgbre", "msgire", "msgstf")
)
HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")


class JpOverlayAdapterError(ValueError):
    """Raised when a caller tries to bypass an audit or structure guard."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def _validate_stock(packed_jp: bytes, expected_stock_sha256: str) -> None:
    """Reject every unpinned JP input before parsing or rebuilding it."""
    if (
        not isinstance(expected_stock_sha256, str)
        or HEX64_RE.fullmatch(expected_stock_sha256) is None
    ):
        raise JpOverlayAdapterError(
            "expected_stock_sha256 must be an uppercase SHA-256"
        )
    observed = sha256(packed_jp)
    if observed != expected_stock_sha256:
        raise JpOverlayAdapterError(
            f"JP stock SHA-256 mismatch: expected={expected_stock_sha256}, "
            f"observed={observed}"
        )


def _validate_routes(
    replacements: Mapping[object, str], routes: Mapping[object, str]
) -> None:
    if set(replacements) != set(routes):
        missing = sorted(set(replacements) - set(routes), key=repr)
        extra = sorted(set(routes) - set(replacements), key=repr)
        raise JpOverlayAdapterError(
            f"replacement/route coordinates differ: missing={missing[:5]!r}, "
            f"extra={extra[:5]!r}"
        )
    rejected = sorted(
        ((coordinate, route) for coordinate, route in routes.items() if route not in SAFE_ROUTES),
        key=lambda pair: repr(pair[0]),
    )
    if rejected:
        raise JpOverlayAdapterError(
            f"audit rejected {len(rejected)} replacement(s); first={rejected[0]!r}"
        )
    for coordinate, value in replacements.items():
        if not isinstance(value, str) or "\0" in value:
            raise JpOverlayAdapterError(
                f"replacement at {coordinate!r} must be NUL-free text"
            )


def build_common_candidate(
    packed_jp: bytes,
    replacements: Mapping[int, str],
    routes: Mapping[int, str],
    *,
    expected_stock_sha256: str,
) -> bytes:
    """Rebuild a single-block JP message resource entirely in memory."""
    _validate_stock(packed_jp, expected_stock_sha256)
    _validate_routes(replacements, routes)
    header, raw = decompress_wrapper(packed_jp)
    table = parse_message_table(raw)
    unknown = sorted(set(replacements) - set(range(table.string_count)))
    if unknown:
        raise JpOverlayAdapterError(f"JP table has no string ids {unknown[:5]!r}")
    texts = list(table.texts)
    for entry_id, replacement in replacements.items():
        texts[entry_id] = replacement
    rebuilt_raw = rebuild_message_table(table, texts)
    candidate = recompress_wrapper(rebuilt_raw, header)
    _new_header, check_raw = decompress_wrapper(candidate)
    if check_raw != rebuilt_raw:
        raise JpOverlayAdapterError("common resource wrapper round-trip differs")
    if parse_message_table(check_raw).texts != tuple(texts):
        raise JpOverlayAdapterError("common resource replacement verification differs")
    return candidate


def build_msggame_candidate(
    packed_jp: bytes,
    replacements: Mapping[tuple[int, int, int], str],
    routes: Mapping[tuple[int, int, int], str],
    *,
    expected_stock_sha256: str,
) -> bytes:
    """Rebuild audited JP msggame literal coordinates entirely in memory."""
    _validate_stock(packed_jp, expected_stock_sha256)
    _validate_routes(replacements, routes)
    return rebuild_packed_with_literals(packed_jp, replacements)


def build_strdata_candidate(
    packed_jp: bytes,
    replacements: Mapping[tuple[int, int], str],
    routes: Mapping[tuple[int, int], str],
    *,
    expected_stock_sha256: str,
) -> bytes:
    """Rebuild audited JP strdata block/slot coordinates entirely in memory."""
    _validate_stock(packed_jp, expected_stock_sha256)
    _validate_routes(replacements, routes)
    header, raw = decompress_wrapper(packed_jp)
    archive = parse_strdata(raw)
    texts = {block.block_id: list(block.texts) for block in archive.blocks}
    valid = {
        (block.block_id, slot_id)
        for block in archive.blocks
        for slot_id in range(block.slot_count)
    }
    unknown = sorted(set(replacements) - valid)
    if unknown:
        raise JpOverlayAdapterError(f"JP strdata has no coordinates {unknown[:5]!r}")
    for (block_id, slot_id), replacement in replacements.items():
        texts[block_id][slot_id] = replacement
    rebuilt_raw = rebuild_strdata(archive, texts)
    candidate = recompress_wrapper(rebuilt_raw, header)
    _new_header, check_raw = decompress_wrapper(candidate)
    if check_raw != rebuilt_raw:
        raise JpOverlayAdapterError("strdata wrapper round-trip differs")
    return candidate


def build_candidate(
    resource: str,
    packed_jp: bytes,
    replacements: Mapping[object, str],
    routes: Mapping[object, str],
    *,
    expected_stock_sha256: str,
) -> bytes:
    """Dispatch to the fixed-format builder for one audited resource."""
    if resource in COMMON_RESOURCES:
        return build_common_candidate(  # type: ignore[arg-type]
            packed_jp,
            replacements,
            routes,
            expected_stock_sha256=expected_stock_sha256,
        )
    if resource == "msggame":
        return build_msggame_candidate(  # type: ignore[arg-type]
            packed_jp,
            replacements,
            routes,
            expected_stock_sha256=expected_stock_sha256,
        )
    if resource == "strdata":
        return build_strdata_candidate(  # type: ignore[arg-type]
            packed_jp,
            replacements,
            routes,
            expected_stock_sha256=expected_stock_sha256,
        )
    raise JpOverlayAdapterError(f"unsupported resource: {resource!r}")
