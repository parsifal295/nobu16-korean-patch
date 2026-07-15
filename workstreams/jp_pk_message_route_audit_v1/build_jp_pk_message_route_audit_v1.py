#!/usr/bin/env python3
"""Audit and build the file-only Japanese-language message route.

Two deliberately separate candidates are produced:

* ``mirror`` places the fully reconstructed Korean SC containers at the
  same-named JP resource paths.  This is the coverage-preserving route.
* ``native_exact_subset`` rebuilds the pinned stock JP containers only at
  coordinates whose JP control/format profile is exactly compatible with
  the Korean replacement.  Every other coordinate remains stock JP.

Complete publisher resources and candidate binaries are written only below
``KR_PATCH_WORK/tmp``.  Tracked artifacts contain coordinates, hashes,
counts, and project-authored Korean text hashes, never publisher source text.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
STRDATA_ROOT = REPO_ROOT / "workstreams" / "switch_msgbre_v11"
sys.path[:0] = [str(TOOLS_ROOT), str(MSGGAME_ROOT), str(STRDATA_ROOT), str(WORKSTREAM_ROOT)]

import build_common_message_overlay as common  # noqa: E402
import build_full_pk_message_candidate as full  # noqa: E402
import msggame_format as msggame  # noqa: E402
from jp_message_overlay_adapter import build_candidate as build_native_candidate  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
from strdata_container import parse_strdata, rebuild_strdata  # noqa: E402


SC_PK_RESOURCES = tuple(full.TARGET_RESOURCES)
SC_STRDATA_RESOURCE = "MSG/SC/strdata.bin"
SC_RESOURCES = SC_PK_RESOURCES + (SC_STRDATA_RESOURCE,)
TARGET_BY_SOURCE = {
    resource: resource.replace("/SC/", "/JP/") for resource in SC_RESOURCES
}
RESOURCE_KEY = {
    **{resource: Path(resource).stem for resource in SC_PK_RESOURCES},
    SC_STRDATA_RESOURCE: "strdata",
}
COMMON_SC_RESOURCES = frozenset(SC_PK_RESOURCES) - {"MSG_PK/SC/msggame.bin"}

DEFAULT_PROGRESS = REPO_ROOT / "data" / "public" / "translation_progress.v0.1.json"
DEFAULT_PK_SC_ROOT = REPO_ROOT / "tmp" / "full_pk_messages_wave04_final_d_20260715"
DEFAULT_SC_STRDATA = (
    REPO_ROOT
    / "tmp"
    / "strdata_pk_shared_manual_b02"
    / "candidate"
    / "MSG"
    / "SC"
    / "strdata.bin"
)
DEFAULT_JP_GAME_ROOT = GAME_ROOT
DEFAULT_LOCK = WORKSTREAM_ROOT / "route_lock.v1.json"
DEFAULT_MSGGAME_EXTERNAL_VALIDATION = (
    REPO_ROOT
    / "workstreams"
    / "msggame_pk_jp_transfer_v1"
    / "msggame_pk_jp_transfer_v1_validation.v1.json"
)

# These completed batches were intentionally committed before their shared
# progress registration.  The loader includes each path exactly once whether
# it is still pending or has subsequently been registered.
SUPPLEMENTAL_OVERLAYS: dict[str, tuple[str, ...]] = {
    "MSG_PK/SC/msgdata.bin": (
        "workstreams/msgdata_pk_structural_review_b12/public/msgdata_ko_pk_structural_review_b12_500.v1.json",
        "workstreams/msgdata_pk_structural_review_b13/public/msgdata_ko_pk_structural_review_b13_500.v1.json",
        "workstreams/msgdata_pk_structural_review_b14/public/msgdata_ko_pk_structural_review_b14_500.v1.json",
        "workstreams/msgdata_pk_structural_review_b15/public/msgdata_ko_pk_structural_review_b15_final_110.v1.json",
    ),
    "MSG_PK/SC/msggame.bin": (
        "workstreams/msggame_pk_ui_priority_b07/public/msggame_ko_pk_ui_priority_b07_300.v1.json",
    ),
}

LOCK_SCHEMA = "nobu16.kr.jp-pk-message-route-lock.v1"
ROUTE_SCHEMA = "nobu16.kr.jp-pk-message-native-route-map.v1"
EVIDENCE_SCHEMA = "nobu16.kr.jp-pk-message-route-evidence.v1"
REVIEW_SCHEMA = "nobu16.kr.jp-pk-message-route-blocked-review.v1"
VALIDATION_SCHEMA = "nobu16.kr.jp-pk-message-route-validation.v1"
PRIVATE_MANIFEST_SCHEMA = "nobu16.kr.jp-pk-message-private-candidate-manifest.v1"
STRDATA_SCHEMA = "nobu16.kr.strdata-block-overlay.v1"
HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
BUILDABLE_STATUSES = frozenset(("translated", "reviewed"))


class RouteAuditError(ValueError):
    """Raised whenever a pinned input or structural contract differs."""


@dataclass(frozen=True)
class OverlayFile:
    source_resource: str
    relative_path: str
    path: Path
    blob: bytes
    value: dict[str, Any]

    @property
    def sha256(self) -> str:
        return sha256(self.blob)


@dataclass(frozen=True)
class EffectiveEntry:
    coordinate: int | tuple[int, int] | tuple[int, int, int]
    ko: str
    overlay_path: str
    overlay_sha256: str
    source_sc_hash: str | None
    allow_edge_whitespace_change: bool = False


@dataclass(frozen=True)
class OverlayUnion:
    files: dict[str, tuple[OverlayFile, ...]]
    entries: dict[str, dict[object, EffectiveEntry]]
    operation_counts: dict[str, int]
    manifest: dict[str, list[dict[str, Any]]]
    manifest_sha256: str


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return sha256(canonical_bytes(value))


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: dict[str, str] = {}
    for key, value in pairs:
        if not isinstance(key, str):
            raise RouteAuditError("JSON object key is not a string")
        normalized = key.casefold()
        if normalized in folded:
            raise RouteAuditError(
                f"duplicate or case-colliding JSON key: {key!r} / {folded[normalized]!r}"
            )
        folded[normalized] = key
        result[key] = value
    return result


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RouteAuditError(f"invalid UTF-8 JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RouteAuditError(f"JSON root is not an object: {path}")
    return value, blob


def require_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or HEX64_RE.fullmatch(value) is None:
        raise RouteAuditError(f"{label} must be an uppercase SHA-256")
    return value


def require_int(value: Any, label: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise RouteAuditError(f"{label} must be an integer >= {minimum}")
    return value


def safe_repo_file(relative_path: str) -> Path:
    pure = Path(relative_path.replace("/", os.sep))
    if pure.is_absolute() or ".." in pure.parts:
        raise RouteAuditError(f"unsafe repository path: {relative_path!r}")
    path = (REPO_ROOT / pure).resolve(strict=True)
    if not path.is_relative_to(REPO_ROOT.resolve()):
        raise RouteAuditError(f"repository path escapes root: {relative_path!r}")
    if not path.is_file():
        raise RouteAuditError(f"repository input is not a file: {relative_path}")
    return path


def assert_private_input(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        raise RouteAuditError(f"{label} is not a file: {path}")
    if resolved.is_relative_to(WORKSTREAM_ROOT.resolve()):
        raise RouteAuditError(f"{label} must not be stored in the tracked workstream")
    return resolved


def resolve_progress_files(progress_path: Path) -> dict[str, tuple[OverlayFile, ...]]:
    progress, _blob = read_json(progress_path)
    if progress.get("schema") != full.PROGRESS_SCHEMA:
        raise RouteAuditError("unsupported translation-progress schema")
    rows = progress.get("resources")
    shared = progress.get("shared_strings")
    if not isinstance(rows, list) or not isinstance(shared, list):
        raise RouteAuditError("translation progress has invalid resource arrays")
    by_resource: dict[str, dict[str, Any]] = {}
    for row in rows + shared:
        if isinstance(row, dict) and row.get("path") in SC_RESOURCES:
            resource = str(row["path"])
            if resource in by_resource:
                raise RouteAuditError(f"duplicate progress resource: {resource}")
            by_resource[resource] = row
    if set(by_resource) != set(SC_RESOURCES):
        raise RouteAuditError(
            f"progress resource set differs: missing={sorted(set(SC_RESOURCES)-set(by_resource))}"
        )

    result: dict[str, tuple[OverlayFile, ...]] = {}
    globally_seen: dict[str, str] = {}
    for resource in SC_RESOURCES:
        patterns = by_resource[resource].get("overlay_globs")
        if not isinstance(patterns, list) or not patterns:
            raise RouteAuditError(f"{resource} has no overlay_globs")
        ordered: list[str] = []
        for pattern in patterns:
            if not isinstance(pattern, str) or not pattern:
                raise RouteAuditError(f"{resource} has an invalid overlay glob")
            matches = sorted(REPO_ROOT.glob(pattern), key=lambda item: item.as_posix().casefold())
            if not matches:
                raise RouteAuditError(f"overlay glob matched no files: {pattern}")
            for path in matches:
                relative = path.relative_to(REPO_ROOT).as_posix()
                if relative not in ordered:
                    ordered.append(relative)
        for relative in SUPPLEMENTAL_OVERLAYS.get(resource, ()):
            if relative not in ordered:
                safe_repo_file(relative)
                ordered.append(relative)
        files: list[OverlayFile] = []
        for relative in ordered:
            if relative in globally_seen and globally_seen[relative] != resource:
                raise RouteAuditError(
                    f"overlay reused by two resources: {relative}"
                )
            globally_seen[relative] = resource
            path = safe_repo_file(relative)
            value, blob = read_json(path)
            files.append(OverlayFile(resource, relative, path, blob, value))
        result[resource] = tuple(files)
    return result


def validate_distribution_policy(value: Mapping[str, Any], label: str) -> None:
    policy = value.get("distribution_policy")
    if not isinstance(policy, dict):
        raise RouteAuditError(f"{label} has no distribution_policy")
    if policy.get("contains_commercial_source_text") is not False:
        raise RouteAuditError(f"{label} is not declared source-free")
    if policy.get("contains_complete_game_resource") is not False:
        raise RouteAuditError(f"{label} embeds a complete game resource")


def normalize_common_file(overlay: OverlayFile) -> list[EffectiveEntry]:
    value = overlay.value
    schema = value.get("schema")
    try:
        if schema == full.MSGUI_SCHEMA and overlay.source_resource == "MSG_PK/SC/msgui.bin":
            parsed = full.parse_msgui_overlay(value, overlay.relative_path)
            rows = parsed["entries"]
            return [
                EffectiveEntry(
                    coordinate=int(row["id"]),
                    ko=str(row["ko"]),
                    overlay_path=overlay.relative_path,
                    overlay_sha256=overlay.sha256,
                    source_sc_hash=str(row["source_hash"]),
                )
                for row in rows
            ]
        if schema == full.COMMON_SCHEMA:
            validate_distribution_policy(value, overlay.relative_path)
            parsed = full.parse_common_overlay(
                value, overlay.source_resource, overlay.relative_path
            )
        elif (
            overlay.source_resource == "MSG_PK/SC/msgdata.bin"
            and schema == full.CASTLE_SCHEMA
        ):
            parsed = full.parse_castle_overlay(value, overlay.relative_path)
        elif (
            overlay.source_resource == "MSG_PK/SC/msgdata.bin"
            and schema == full.PROVINCE_SCHEMA
        ):
            parsed = full.parse_province_overlay(value, overlay.relative_path)
        else:
            raise RouteAuditError(
                f"unsupported common overlay schema {schema!r}: {overlay.relative_path}"
            )
    except (full.BuildError, ValueError) as exc:
        raise RouteAuditError(str(exc)) from exc
    result: list[EffectiveEntry] = []
    for row in parsed["entries"]:
        result.append(
            EffectiveEntry(
                coordinate=int(row["id"]),
                ko=str(row["ko"]),
                overlay_path=overlay.relative_path,
                overlay_sha256=overlay.sha256,
                source_sc_hash=(str(row["source_hash"]) if "source_hash" in row else None),
                allow_edge_whitespace_change=bool(
                    row.get("allow_edge_whitespace_change", False)
                ),
            )
        )
    return result


def normalize_msggame_file(overlay: OverlayFile) -> list[EffectiveEntry]:
    validate_distribution_policy(overlay.value, overlay.relative_path)
    try:
        parsed = full.parse_msggame_overlay(overlay.value, overlay.relative_path)
    except (full.BuildError, ValueError) as exc:
        # A newly completed UI batch may carry additional source-free review
        # counters before the central seven-file builder learns that metadata
        # key.  The actual build contract remains the fixed source-free entry
        # tuple below, so validate that tuple independently and fail closed on
        # every semantic field.
        value = overlay.value
        if (
            value.get("schema") != full.MSGGAME_SCHEMA
            or value.get("resource") != "MSG_PK/SC/msggame.bin"
            or value.get("base_language") != "SC"
        ):
            raise RouteAuditError(str(exc)) from exc
        defaults = value.get("defaults")
        raw_entries = value.get("entries")
        if (
            not isinstance(defaults, dict)
            or defaults.get("status") not in BUILDABLE_STATUSES
            or not isinstance(raw_entries, list)
            or require_int(value.get("entry_count"), "msggame entry_count")
            != len(raw_entries)
        ):
            raise RouteAuditError(str(exc)) from exc
        normalized: list[dict[str, Any]] = []
        coordinates: list[tuple[int, int, int]] = []
        for index, row in enumerate(raw_entries):
            if not isinstance(row, dict) or set(row) - {
                "block_id",
                "record_id",
                "literal_id",
                "source_sc_utf16le_sha256",
                "ko",
                "status",
            }:
                raise RouteAuditError(
                    f"unsupported msggame entry shape: {overlay.relative_path}[{index}]"
                ) from exc
            coordinate = tuple(
                require_int(row.get(key), f"msggame {key}")
                for key in ("block_id", "record_id", "literal_id")
            )
            ko = row.get("ko")
            status = row.get("status", defaults["status"])
            if (
                not isinstance(ko, str)
                or "\0" in ko
                or not common.has_semantic_text(ko)
                or status not in BUILDABLE_STATUSES
            ):
                raise RouteAuditError(
                    f"invalid msggame Korean/status: {overlay.relative_path}:{coordinate}"
                ) from exc
            coordinates.append(coordinate)
            normalized.append(
                {
                    "coordinate": coordinate,
                    "ko": ko,
                    "source_hash": require_hash(
                        row.get("source_sc_utf16le_sha256"),
                        "msggame source hash",
                    ),
                }
            )
        if coordinates != sorted(set(coordinates)):
            raise RouteAuditError(
                f"msggame coordinates are not sorted/unique: {overlay.relative_path}"
            ) from exc
        parsed = {"entries": normalized}
    return [
        EffectiveEntry(
            coordinate=tuple(row["coordinate"]),
            ko=str(row["ko"]),
            overlay_path=overlay.relative_path,
            overlay_sha256=overlay.sha256,
            source_sc_hash=str(row["source_hash"]),
        )
        for row in parsed["entries"]
    ]


def normalize_strdata_file(overlay: OverlayFile) -> list[EffectiveEntry]:
    value = overlay.value
    if value.get("schema") != STRDATA_SCHEMA:
        raise RouteAuditError(
            f"unsupported strdata schema {value.get('schema')!r}: {overlay.relative_path}"
        )
    if value.get("resource") != SC_STRDATA_RESOURCE or value.get("base_language") != "SC":
        raise RouteAuditError(f"strdata overlay target differs: {overlay.relative_path}")
    validate_distribution_policy(value, overlay.relative_path)
    defaults = value.get("defaults")
    if not isinstance(defaults, dict) or defaults.get("status") not in BUILDABLE_STATUSES:
        raise RouteAuditError(f"strdata overlay status is not buildable: {overlay.relative_path}")
    entries = value.get("entries")
    if not isinstance(entries, list) or require_int(
        value.get("entry_count"), f"{overlay.relative_path}.entry_count"
    ) != len(entries):
        raise RouteAuditError(f"strdata entry count differs: {overlay.relative_path}")
    result: list[EffectiveEntry] = []
    coordinates: list[tuple[int, int]] = []
    for index, row in enumerate(entries):
        if not isinstance(row, dict) or set(row) != {
            "block_id",
            "slot_id",
            "source_sc_utf16le_sha256",
            "ko",
        }:
            raise RouteAuditError(
                f"invalid strdata entry shape at {overlay.relative_path}[{index}]"
            )
        coordinate = (
            require_int(row["block_id"], "strdata block_id"),
            require_int(row["slot_id"], "strdata slot_id"),
        )
        ko = row["ko"]
        if not isinstance(ko, str) or "\0" in ko or not common.has_semantic_text(ko):
            raise RouteAuditError(f"invalid Korean text at {overlay.relative_path}:{coordinate}")
        coordinates.append(coordinate)
        result.append(
            EffectiveEntry(
                coordinate=coordinate,
                ko=ko,
                overlay_path=overlay.relative_path,
                overlay_sha256=overlay.sha256,
                source_sc_hash=require_hash(
                    row["source_sc_utf16le_sha256"], "strdata source hash"
                ),
            )
        )
    if coordinates != sorted(set(coordinates)):
        raise RouteAuditError(f"strdata coordinates are not sorted/unique: {overlay.relative_path}")
    return result


def load_overlay_union(progress_path: Path = DEFAULT_PROGRESS) -> OverlayUnion:
    files = resolve_progress_files(progress_path)
    effective: dict[str, dict[object, EffectiveEntry]] = {}
    operation_counts: dict[str, int] = {}
    manifest: dict[str, list[dict[str, Any]]] = {}
    for resource in SC_RESOURCES:
        current: dict[object, EffectiveEntry] = {}
        operations = 0
        rows_manifest: list[dict[str, Any]] = []
        previous_kind: dict[object, str] = {}
        for overlay in files[resource]:
            if resource == "MSG_PK/SC/msggame.bin":
                rows = normalize_msggame_file(overlay)
                kind = "msggame"
            elif resource == SC_STRDATA_RESOURCE:
                rows = normalize_strdata_file(overlay)
                kind = "strdata"
            else:
                rows = normalize_common_file(overlay)
                schema = overlay.value.get("schema")
                kind = (
                    "geographic"
                    if schema in {full.CASTLE_SCHEMA, full.PROVINCE_SCHEMA}
                    else "common"
                )
            operations += len(rows)
            for row in rows:
                coordinate = row.coordinate
                if coordinate in current:
                    allowed = (
                        resource == "MSG_PK/SC/msgdata.bin"
                        and previous_kind[coordinate] == "common"
                        and kind == "geographic"
                    )
                    if not allowed:
                        raise RouteAuditError(
                            f"unapproved duplicate coordinate {coordinate!r}: "
                            f"{current[coordinate].overlay_path} -> {overlay.relative_path}"
                        )
                current[coordinate] = row
                previous_kind[coordinate] = kind
            rows_manifest.append(
                {
                    "path": overlay.relative_path,
                    "sha256": overlay.sha256,
                    "schema": overlay.value.get("schema"),
                    "entry_count": len(rows),
                }
            )
        effective[resource] = current
        operation_counts[resource] = operations
        manifest[resource] = rows_manifest
    return OverlayUnion(
        files=files,
        entries=effective,
        operation_counts=operation_counts,
        manifest=manifest,
        manifest_sha256=canonical_hash(manifest),
    )


def common_structure(blob: bytes) -> tuple[dict[str, Any], dict[int, str]]:
    _header, raw = decompress_wrapper(blob)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise RouteAuditError("common message raw parse/rebuild differs")
    return (
        {
            "packed_size": len(blob),
            "packed_sha256": sha256(blob),
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
            "string_count": table.string_count,
            "raw_roundtrip_exact": True,
        },
        dict(enumerate(table.texts)),
    )


def msggame_structure(blob: bytes) -> tuple[dict[str, Any], dict[tuple[int, int, int], str]]:
    _header, raw = decompress_wrapper(blob)
    packed = msggame.parse_packed_msggame(blob)
    if msggame.rebuild_raw_msggame(packed.archive) != raw:
        raise RouteAuditError("msggame raw parse/rebuild differs")
    literals = {
        (item.block_id, item.record_id, item.literal_id): item.text
        for item in msggame.iter_literals(packed.archive)
    }
    return (
        {
            "packed_size": len(blob),
            "packed_sha256": sha256(blob),
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
            "block_count": len(packed.archive.blocks),
            "record_count": packed.archive.record_count,
            "literal_slot_count": len(literals),
            "raw_roundtrip_exact": True,
        },
        literals,
    )


def strdata_structure(blob: bytes) -> tuple[dict[str, Any], dict[tuple[int, int], str]]:
    _header, raw = decompress_wrapper(blob)
    archive = parse_strdata(raw)
    if rebuild_strdata(archive) != raw:
        raise RouteAuditError("strdata raw parse/rebuild differs")
    texts = {
        (block.block_id, slot_id): text
        for block in archive.blocks
        for slot_id, text in enumerate(block.texts)
    }
    return (
        {
            "packed_size": len(blob),
            "packed_sha256": sha256(blob),
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
            "block_count": len(archive.blocks),
            "slot_counts": [block.slot_count for block in archive.blocks],
            "raw_roundtrip_exact": True,
        },
        texts,
    )


def structure(resource: str, blob: bytes) -> tuple[dict[str, Any], Mapping[object, str]]:
    if resource == "MSG_PK/SC/msggame.bin":
        return msggame_structure(blob)
    if resource == SC_STRDATA_RESOURCE:
        return strdata_structure(blob)
    return common_structure(blob)


def reconstruct_full_sc(
    resource: str, base_blob: bytes, entries: Mapping[object, EffectiveEntry]
) -> bytes:
    if resource == "MSG_PK/SC/msggame.bin":
        replacements = {
            coordinate: entry.ko for coordinate, entry in entries.items()
        }
        return msggame.rebuild_packed_with_literals(base_blob, replacements)  # type: ignore[arg-type]
    header, raw = decompress_wrapper(base_blob)
    if resource == SC_STRDATA_RESOURCE:
        archive = parse_strdata(raw)
        texts = {block.block_id: list(block.texts) for block in archive.blocks}
        valid = {
            (block.block_id, slot_id)
            for block in archive.blocks
            for slot_id in range(block.slot_count)
        }
        missing = sorted(set(entries) - valid)
        if missing:
            raise RouteAuditError(f"SC strdata candidate lacks coordinates: {missing[:5]!r}")
        for coordinate, entry in entries.items():
            block_id, slot_id = coordinate  # type: ignore[misc]
            texts[block_id][slot_id] = entry.ko
        rebuilt_raw = rebuild_strdata(archive, texts)
    else:
        table = parse_message_table(raw)
        missing = sorted(set(entries) - set(range(table.string_count)))
        if missing:
            raise RouteAuditError(f"SC common candidate lacks ids: {missing[:5]!r}")
        texts = list(table.texts)
        for coordinate, entry in entries.items():
            texts[int(coordinate)] = entry.ko
        rebuilt_raw = rebuild_message_table(table, texts)
    candidate = recompress_wrapper(rebuilt_raw, header)
    _check_header, check_raw = decompress_wrapper(candidate)
    if check_raw != rebuilt_raw:
        raise RouteAuditError(f"SC reconstruction wrapper differs: {resource}")
    return candidate


def verify_overlay_inclusion(
    resource: str, blob: bytes, entries: Mapping[object, EffectiveEntry]
) -> None:
    _stats, texts = structure(resource, blob)
    for coordinate, entry in entries.items():
        if texts.get(coordinate) != entry.ko:
            raise RouteAuditError(
                f"full SC reconstruction omitted {resource} coordinate {coordinate!r}"
            )


def invariant_keys(source: str, replacement: str) -> list[str]:
    before = common.message_invariants(source)
    after = common.message_invariants(replacement)
    return [key for key in before if before[key] != after[key]]


def coordinate_value(coordinate: object) -> int | list[int]:
    if isinstance(coordinate, int):
        return coordinate
    if isinstance(coordinate, tuple):
        return list(coordinate)
    raise RouteAuditError(f"unsupported coordinate type: {coordinate!r}")


def coordinate_sort_key(value: object) -> tuple[int, ...]:
    return (value,) if isinstance(value, int) else tuple(value)  # type: ignore[arg-type]


def coordinate_set_hash(values: Iterable[object]) -> str:
    return canonical_hash(
        [coordinate_value(value) for value in sorted(values, key=coordinate_sort_key)]
    )


def compact_native_rows(
    rows: Sequence[dict[str, Any]], *, include_hashes_for_blocked: bool
) -> dict[str, Any]:
    """Encode the exhaustive classification without repeated field names.

    Direct rows need only their coordinates: the Korean value is recovered
    from the independently pinned overlay union and the JP stock/profile is
    recomputed before every candidate build.  Blocked rows retain reason-key
    indexes and, in the route map, their two text hashes for auditability.
    The canonical digest commits to the full in-memory detailed rows.
    """

    mismatch_dictionary = sorted(
        {
            key
            for row in rows
            for key in row.get("mismatch_keys", [])
        }
    )
    mismatch_index = {value: index for index, value in enumerate(mismatch_dictionary)}
    resources: list[dict[str, Any]] = []
    for resource in SC_RESOURCES:
        if resource == "MSG_PK/SC/msggame.bin":
            continue
        selected = [row for row in rows if row["source_resource"] == resource]
        direct = [
            row["coordinate"]
            for row in selected
            if row["route"] == "exact_direct_transfer"
        ]
        blocked_rows = [
            row for row in selected if row["route"] != "exact_direct_transfer"
        ]
        blocked: list[list[Any]] = []
        for row in blocked_rows:
            compact: list[Any] = [
                row["coordinate"],
                [mismatch_index[key] for key in row["mismatch_keys"]],
            ]
            if include_hashes_for_blocked:
                compact.extend(
                    [
                        row["source_jp_utf16le_sha256"],
                        row["ko_utf16le_sha256"],
                    ]
                )
            blocked.append(compact)
        resources.append(
            {
                "source_resource": resource,
                "target_resource": TARGET_BY_SOURCE[resource],
                "entry_count": len(selected),
                "transferable_count": len(direct),
                "blocked_count": len(blocked),
                "transferable_coordinates": direct,
                "transferable_coordinates_sha256": coordinate_set_hash(
                    row_coordinate(value) for value in direct
                ),
                "blocked_entries": blocked,
                "blocked_coordinates_sha256": coordinate_set_hash(
                    row_coordinate(row["coordinate"]) for row in blocked_rows
                ),
                "detailed_rows_sha256": canonical_hash(selected),
            }
        )
    return {
        "encoding": {
            "coordinate": "integer id or [block_id,slot_id]",
            "blocked_entry": (
                "[coordinate,mismatch_key_indexes,source_jp_utf16le_sha256,ko_utf16le_sha256]"
                if include_hashes_for_blocked
                else "[coordinate,mismatch_key_indexes]"
            ),
            "transferable_entry": "coordinate only; replacement is resolved from the pinned overlay union and re-audited against pinned JP stock",
        },
        "mismatch_key_dictionary": mismatch_dictionary,
        "entry_count": len(rows),
        "transferable_count": sum(row["transferable_count"] for row in resources),
        "blocked_count": sum(row["blocked_count"] for row in resources),
        "detailed_rows_sha256": canonical_hash(list(rows)),
        "resources": resources,
    }


def classify_native_routes(
    resource: str,
    jp_blob: bytes,
    entries: Mapping[object, EffectiveEntry],
) -> tuple[list[dict[str, Any]], dict[object, str], dict[object, str]]:
    _stats, jp_texts = structure(resource, jp_blob)
    rows: list[dict[str, Any]] = []
    replacements: dict[object, str] = {}
    routes: dict[object, str] = {}
    for coordinate in sorted(entries, key=coordinate_sort_key):
        entry = entries[coordinate]
        source = jp_texts.get(coordinate)
        if source is None:
            route = "blocked_missing_coordinate"
            mismatch_keys = ["coordinate"]
            source_hash = None
            source_profile_hash = None
        else:
            mismatch_keys = invariant_keys(source, entry.ko)
            route = (
                "exact_direct_transfer"
                if not mismatch_keys
                else "blocked_control_format_contract"
            )
            source_hash = text_hash(source)
            source_profile_hash = canonical_hash(common.message_invariants(source))
        row = {
            "coordinate": coordinate_value(coordinate),
            "route": route,
            "source_jp_utf16le_sha256": source_hash,
            "ko_utf16le_sha256": text_hash(entry.ko),
            "source_jp_invariant_profile_sha256": source_profile_hash,
            "ko_invariant_profile_sha256": canonical_hash(
                common.message_invariants(entry.ko)
            ),
            "mismatch_keys": mismatch_keys,
            "overlay_path": entry.overlay_path,
            "overlay_sha256": entry.overlay_sha256,
        }
        rows.append(row)
        if route == "exact_direct_transfer":
            replacements[coordinate] = entry.ko
            routes[coordinate] = route
    return rows, replacements, routes


def load_lock(path: Path) -> dict[str, Any]:
    value, _blob = read_json(path)
    if value.get("schema") != LOCK_SCHEMA:
        raise RouteAuditError("unsupported route-lock schema")
    if value.get("source_free") is not True or value.get("contains_complete_game_resource") is not False:
        raise RouteAuditError("route lock is not source-free")
    return value


def verify_pin(blob: bytes, pin: Mapping[str, Any], label: str) -> None:
    expected_size = require_int(pin.get("size"), f"{label}.size", 1)
    expected_hash = require_hash(pin.get("sha256"), f"{label}.sha256")
    if len(blob) != expected_size or sha256(blob) != expected_hash:
        raise RouteAuditError(
            f"{label} differs: expected size={expected_size} sha256={expected_hash}, "
            f"observed size={len(blob)} sha256={sha256(blob)}"
        )


def collect_private_inputs(
    lock: Mapping[str, Any], pk_sc_root: Path, sc_strdata: Path, jp_game_root: Path
) -> tuple[dict[str, bytes], dict[str, bytes]]:
    resources = lock.get("resources")
    if not isinstance(resources, dict) or set(resources) != set(SC_RESOURCES):
        raise RouteAuditError("route lock resource set differs")
    sc_blobs: dict[str, bytes] = {}
    jp_blobs: dict[str, bytes] = {}
    for resource in SC_RESOURCES:
        row = resources[resource]
        if not isinstance(row, dict):
            raise RouteAuditError(f"lock resource row is invalid: {resource}")
        sc_path = (
            assert_private_input(sc_strdata, "SC strdata candidate")
            if resource == SC_STRDATA_RESOURCE
            else assert_private_input(pk_sc_root / Path(resource), f"SC candidate {resource}")
        )
        jp_path = assert_private_input(
            jp_game_root / Path(TARGET_BY_SOURCE[resource]),
            f"JP stock {TARGET_BY_SOURCE[resource]}",
        )
        sc_blob = sc_path.read_bytes()
        jp_blob = jp_path.read_bytes()
        verify_pin(sc_blob, row.get("base_sc_candidate", {}), f"{resource}.base_sc_candidate")
        verify_pin(jp_blob, row.get("jp_stock", {}), f"{resource}.jp_stock")
        sc_blobs[resource] = sc_blob
        jp_blobs[resource] = jp_blob
    return sc_blobs, jp_blobs


def build_lock(
    *,
    progress_path: Path,
    pk_sc_root: Path,
    sc_strdata: Path,
    jp_game_root: Path,
    msggame_external_validation: Path,
) -> dict[str, Any]:
    union = load_overlay_union(progress_path)
    resources: dict[str, Any] = {}
    for resource in SC_RESOURCES:
        sc_path = sc_strdata if resource == SC_STRDATA_RESOURCE else pk_sc_root / Path(resource)
        jp_path = jp_game_root / Path(TARGET_BY_SOURCE[resource])
        sc_blob = assert_private_input(sc_path, f"SC candidate {resource}").read_bytes()
        jp_blob = assert_private_input(jp_path, f"JP stock {resource}").read_bytes()
        sc_stats, _sc_texts = structure(resource, sc_blob)
        jp_stats, _jp_texts = structure(resource, jp_blob)
        resources[resource] = {
            "target_resource": TARGET_BY_SOURCE[resource],
            "base_sc_candidate": {"size": len(sc_blob), "sha256": sha256(sc_blob)},
            "jp_stock": {"size": len(jp_blob), "sha256": sha256(jp_blob)},
            "base_sc_structure": sc_stats,
            "jp_stock_structure": jp_stats,
        }
    external_blob = assert_private_input(
        msggame_external_validation, "external msggame validation"
    ).read_bytes()
    return {
        "schema": LOCK_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "overlay_union_manifest_sha256": union.manifest_sha256,
        "overlay_union_operation_total": sum(union.operation_counts.values()),
        "overlay_union_effective_total": sum(len(values) for values in union.entries.values()),
        "supplemental_overlays": {
            key: list(value) for key, value in SUPPLEMENTAL_OVERLAYS.items()
        },
        "resources": resources,
        "external_msggame_native_validation": {
            "path": msggame_external_validation.relative_to(REPO_ROOT).as_posix(),
            "size": len(external_blob),
            "sha256": sha256(external_blob),
        },
    }


def load_external_msggame_validation(lock: Mapping[str, Any]) -> dict[str, Any]:
    pin = lock.get("external_msggame_native_validation")
    if not isinstance(pin, dict):
        raise RouteAuditError("external msggame validation pin is missing")
    path = safe_repo_file(str(pin.get("path")))
    value, blob = read_json(path)
    verify_pin(blob, pin, "external msggame validation")
    if value.get("passed") is not True:
        raise RouteAuditError("external msggame native validation did not pass")
    counts = value.get("counts")
    if not isinstance(counts, dict):
        raise RouteAuditError("external msggame validation counts are missing")
    input_count = require_int(counts.get("input"), "msggame input")
    transferable = require_int(counts.get("transferable"), "msggame transferable")
    blocked = require_int(counts.get("blocked"), "msggame blocked")
    if input_count != transferable + blocked:
        raise RouteAuditError("external msggame route counts do not partition input")
    return {
        "path": path.relative_to(REPO_ROOT).as_posix(),
        "sha256": sha256(blob),
        "input": input_count,
        "transferable": transferable,
        "blocked": blocked,
        "transferable_coordinates_sha256": value["coordinate_sets"]["transferable_sha256"],
        "blocked_coordinates_sha256": value["coordinate_sets"]["blocked_sha256"],
        "candidate_ab": {
            "mirror": value.get("mirror_candidate_ab"),
            "native": value.get("native_candidate_ab"),
        },
    }


def artifact_source_scan(value: Any) -> dict[str, int]:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return {
        "embedded_nul_count": text.count("\0"),
        # Evidence is deliberately hash/coordinate only; any Japanese scripts
        # here would indicate an accidental source-text leak.
        "kana_count": sum(1 for char in text if "\u3040" <= char <= "\u30ff"),
        "cjk_unified_count": sum(
            1 for char in text if "\u3400" <= char <= "\u9fff"
        ),
    }


def run_audit(
    *,
    progress_path: Path,
    lock_path: Path,
    pk_sc_root: Path,
    sc_strdata: Path,
    jp_game_root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, bytes], dict[str, bytes]]:
    lock = load_lock(lock_path)
    union = load_overlay_union(progress_path)
    if union.manifest_sha256 != lock.get("overlay_union_manifest_sha256"):
        raise RouteAuditError(
            "current overlay union differs from route lock: "
            f"expected={lock.get('overlay_union_manifest_sha256')} "
            f"observed={union.manifest_sha256}"
        )
    if sum(union.operation_counts.values()) != lock.get("overlay_union_operation_total"):
        raise RouteAuditError("overlay operation total differs from route lock")
    if sum(len(values) for values in union.entries.values()) != lock.get(
        "overlay_union_effective_total"
    ):
        raise RouteAuditError("overlay effective total differs from route lock")
    base_sc, jp_stock = collect_private_inputs(lock, pk_sc_root, sc_strdata, jp_game_root)

    mirror_a: dict[str, bytes] = {}
    mirror_b: dict[str, bytes] = {}
    mirror_rows: list[dict[str, Any]] = []
    for resource in SC_RESOURCES:
        first = reconstruct_full_sc(resource, base_sc[resource], union.entries[resource])
        second = reconstruct_full_sc(resource, base_sc[resource], union.entries[resource])
        if first != second:
            raise RouteAuditError(f"mirror A/B reconstruction differs: {resource}")
        verify_overlay_inclusion(resource, first, union.entries[resource])
        mirror_stats, _mirror_texts = structure(resource, first)
        jp_stats, _jp_texts = structure(resource, jp_stock[resource])
        if resource == "MSG_PK/SC/msggame.bin":
            if (
                mirror_stats["block_count"] != jp_stats["block_count"]
                or mirror_stats["record_count"] != jp_stats["record_count"]
            ):
                raise RouteAuditError("mirror msggame block/record counts differ from JP")
            structure_match = {
                "block_count_equal": True,
                "record_count_equal": True,
                "literal_slot_count_equal": (
                    mirror_stats["literal_slot_count"] == jp_stats["literal_slot_count"]
                ),
            }
        elif resource == SC_STRDATA_RESOURCE:
            if mirror_stats["slot_counts"] != jp_stats["slot_counts"]:
                raise RouteAuditError("mirror strdata block/slot counts differ from JP")
            structure_match = {"block_slot_counts_equal": True}
        else:
            if mirror_stats["string_count"] != jp_stats["string_count"]:
                raise RouteAuditError(f"mirror string count differs from JP: {resource}")
            structure_match = {"string_count_equal": True}
        mirror_a[resource] = first
        mirror_b[resource] = second
        mirror_rows.append(
            {
                "source_resource": resource,
                "target_resource": TARGET_BY_SOURCE[resource],
                "filename_preserved": Path(resource).name == Path(TARGET_BY_SOURCE[resource]).name,
                "language_folder_only_changed": True,
                "overlay_operation_count": union.operation_counts[resource],
                "effective_coordinate_count": len(union.entries[resource]),
                "effective_coordinates_sha256": coordinate_set_hash(union.entries[resource]),
                "base_sc_candidate": structure(resource, base_sc[resource])[0],
                "mirror_target": mirror_stats,
                "jp_stock": jp_stats,
                "structure_match": structure_match,
                "mirror_bytes_equal_reconstructed_sc_container": True,
                "overlay_union_values_verified": True,
                "in_memory_a_b_equal": True,
            }
        )

    route_rows: list[dict[str, Any]] = []
    blocked_rows: list[dict[str, Any]] = []
    native_outputs: dict[str, bytes] = {}
    native_resource_rows: list[dict[str, Any]] = []
    reason_counts: collections.Counter[str] = collections.Counter()
    for resource in SC_RESOURCES:
        if resource == "MSG_PK/SC/msggame.bin":
            continue
        rows, replacements, routes = classify_native_routes(
            resource, jp_stock[resource], union.entries[resource]
        )
        route_rows.extend(
            [{"source_resource": resource, "target_resource": TARGET_BY_SOURCE[resource], **row} for row in rows]
        )
        for row in rows:
            if row["route"] != "exact_direct_transfer":
                blocked = {
                    "source_resource": resource,
                    "target_resource": TARGET_BY_SOURCE[resource],
                    **row,
                }
                blocked_rows.append(blocked)
                for reason in row["mismatch_keys"]:
                    reason_counts[f"{resource}:{reason}"] += 1
        key = RESOURCE_KEY[resource]
        first = build_native_candidate(
            key,
            jp_stock[resource],
            replacements,
            routes,
            expected_stock_sha256=sha256(jp_stock[resource]),
        )
        second = build_native_candidate(
            key,
            jp_stock[resource],
            replacements,
            routes,
            expected_stock_sha256=sha256(jp_stock[resource]),
        )
        if first != second:
            raise RouteAuditError(f"native exact candidate A/B differs: {resource}")
        candidate_stats, candidate_texts = structure(resource, first)
        _jp_stats, jp_texts = structure(resource, jp_stock[resource])
        for coordinate, replacement in replacements.items():
            if candidate_texts.get(coordinate) != replacement:
                raise RouteAuditError(f"native replacement verification failed: {resource}:{coordinate}")
        for coordinate, text in jp_texts.items():
            if coordinate not in replacements and candidate_texts.get(coordinate) != text:
                raise RouteAuditError(f"native nonselected coordinate changed: {resource}:{coordinate}")
        native_outputs[resource] = first
        transferable = len(replacements)
        blocked = len(rows) - transferable
        native_resource_rows.append(
            {
                "source_resource": resource,
                "target_resource": TARGET_BY_SOURCE[resource],
                "input_effective_count": len(rows),
                "transferable_count": transferable,
                "blocked_count": blocked,
                "transferable_coordinates_sha256": coordinate_set_hash(replacements),
                "blocked_coordinates_sha256": coordinate_set_hash(
                    row_coordinate(row["coordinate"])
                    for row in rows
                    if row["route"] != "exact_direct_transfer"
                ),
                "stock_jp": structure(resource, jp_stock[resource])[0],
                "native_exact_candidate": candidate_stats,
                "nonselected_coordinates_preserved": True,
                "in_memory_a_b_equal": True,
            }
        )

    external_msggame = load_external_msggame_validation(lock)
    expected_msggame_count = len(union.entries["MSG_PK/SC/msggame.bin"])
    if external_msggame["input"] != expected_msggame_count:
        raise RouteAuditError(
            f"external msggame input={external_msggame['input']} differs from overlay union={expected_msggame_count}"
        )

    compact_route_rows = compact_native_rows(
        route_rows, include_hashes_for_blocked=True
    )
    compact_blocked_review = compact_native_rows(
        route_rows, include_hashes_for_blocked=False
    )
    route_map = {
        "schema": ROUTE_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "overlay_union_manifest_sha256": union.manifest_sha256,
        "scope": "native JP exact-subset routes for six common tables and shared strdata; msggame uses the separately pinned deep-record recipe",
        "entry_count": len(route_rows),
        "classification": compact_route_rows,
        "external_msggame_route": external_msggame,
    }
    review = {
        "schema": REVIEW_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "blocked_count": len(blocked_rows) + external_msggame["blocked"],
        "local_blocked_count": len(blocked_rows),
        "external_msggame_blocked_count": external_msggame["blocked"],
        "reason_counts": dict(sorted(reason_counts.items())),
        "classification": compact_blocked_review,
        "external_msggame_route": external_msggame,
    }
    local_transferable = sum(row["transferable_count"] for row in native_resource_rows)
    local_blocked = sum(row["blocked_count"] for row in native_resource_rows)
    effective_total = sum(len(values) for values in union.entries.values())
    native_transferable = local_transferable + external_msggame["transferable"]
    native_blocked = local_blocked + external_msggame["blocked"]
    if native_transferable + native_blocked != effective_total:
        raise RouteAuditError("native route partition does not cover overlay union")
    evidence = {
        "schema": EVIDENCE_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "overlay_union": {
            "manifest_sha256": union.manifest_sha256,
            "manifest": union.manifest,
            "operation_counts": union.operation_counts,
            "operation_total": sum(union.operation_counts.values()),
            "effective_counts": {
                resource: len(union.entries[resource]) for resource in SC_RESOURCES
            },
            "effective_total": effective_total,
        },
        "mirror_route": {
            "priority": "coverage_preserving_full_sc_container_mirror",
            "runtime_verified": False,
            "runtime_status": "pending in-game JP-launch screen validation",
            "resource_count": len(mirror_rows),
            "effective_coordinate_count": effective_total,
            "all_overlay_values_verified": True,
            "all_filenames_preserved": True,
            "only_language_folder_changes": True,
            "all_in_memory_a_b_equal": True,
            "resources": mirror_rows,
        },
        "native_jp_control": {
            "purpose": "conservative comparison route",
            "effective_coordinate_count": effective_total,
            "transferable_count": native_transferable,
            "blocked_count": native_blocked,
            "classification_covers_union": True,
            "local_resources": native_resource_rows,
            "external_msggame": external_msggame,
        },
        "stock_lock_sha256": file_sha256(lock_path),
    }
    validation = {
        "schema": VALIDATION_SCHEMA,
        "passed": True,
        "scope": {
            "source_resource_count": len(SC_RESOURCES),
            "target_resource_count": len(TARGET_BY_SOURCE),
            "overlay_operation_count": sum(union.operation_counts.values()),
            "overlay_effective_coordinate_count": effective_total,
            "mirror_transferred_count": effective_total,
            "mirror_blocked_count": 0,
            "native_transferable_count": native_transferable,
            "native_blocked_count": native_blocked,
        },
        "proofs": {
            "all_overlay_files_source_free_and_complete_resource_free": True,
            "overlay_union_manifest_pinned": True,
            "all_jp_stock_sha256_fail_closed": True,
            "all_base_sc_candidate_sha256_fail_closed": True,
            "mirror_all_eight_containers_strictly_parse": True,
            "mirror_common_string_counts_match_jp": True,
            "mirror_msggame_block_and_record_counts_match_jp": True,
            "mirror_strdata_block_and_slot_counts_match_jp": True,
            "mirror_all_overlay_values_verified": True,
            "mirror_in_memory_a_b_equal": True,
            "native_coordinates_fail_closed": True,
            "native_control_format_profiles_fail_closed": True,
            "native_nonselected_values_preserved": True,
            "native_in_memory_a_b_equal": True,
            "native_msggame_deep_record_audit_pinned": True,
            "publisher_source_text_in_public_artifacts": False,
            "installed_game_files_modified": False,
            "runtime_compatibility_claimed": False,
        },
        "safety": {
            "process_memory_access": False,
            "dll_injection": False,
            "executable_modified": False,
            "registry_modified": False,
            "installed_game_files_modified": False,
            "complete_candidate_binaries_tracked": False,
            "shared_progress_modified": False,
            "root_readme_modified": False,
        },
    }
    private_manifest = {
        "schema": PRIVATE_MANIFEST_SCHEMA,
        "public_distribution_eligible": False,
        "contains_complete_game_resources": True,
        "installed_game_files_modified": False,
        "runtime_verified": False,
        "overlay_union_manifest_sha256": union.manifest_sha256,
        "mirror": [
            {
                "path": TARGET_BY_SOURCE[resource],
                "size": len(mirror_a[resource]),
                "sha256": sha256(mirror_a[resource]),
                "a_b_equal": mirror_a[resource] == mirror_b[resource],
            }
            for resource in SC_RESOURCES
        ],
        "native_exact_subset": [
            {
                "path": TARGET_BY_SOURCE[resource],
                "size": len(native_outputs[resource]),
                "sha256": sha256(native_outputs[resource]),
            }
            for resource in native_outputs
        ],
        "native_msggame_external": external_msggame,
    }
    return validation, evidence, review, route_map, mirror_a, native_outputs


def row_coordinate(value: int | list[int]) -> object:
    return value if isinstance(value, int) else tuple(value)


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def write_private_candidate(
    output_root: Path,
    mirror: Mapping[str, bytes],
    native: Mapping[str, bytes],
    manifest: Mapping[str, Any],
) -> None:
    tmp_root = (REPO_ROOT / "tmp").resolve(strict=True)
    resolved = output_root.resolve(strict=False)
    if not resolved.is_relative_to(tmp_root):
        raise RouteAuditError("private output root must be below KR_PATCH_WORK/tmp")
    if resolved.exists():
        raise RouteAuditError(f"private output root already exists: {resolved}")
    staging = Path(tempfile.mkdtemp(prefix=f".{resolved.name}.staging-", dir=resolved.parent))
    try:
        for resource, blob in mirror.items():
            atomic_write(staging / "mirror" / Path(TARGET_BY_SOURCE[resource]), blob)
        for resource, blob in native.items():
            atomic_write(
                staging / "native_exact_subset" / Path(TARGET_BY_SOURCE[resource]), blob
            )
        atomic_write(staging / "private_candidate_manifest.json", pretty_bytes(manifest))
        os.replace(staging, resolved)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("refresh-lock", "verify", "generate"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--progress", type=Path, default=DEFAULT_PROGRESS)
        sub.add_argument("--pk-sc-root", type=Path, default=DEFAULT_PK_SC_ROOT)
        sub.add_argument("--sc-strdata", type=Path, default=DEFAULT_SC_STRDATA)
        sub.add_argument("--jp-game-root", type=Path, default=DEFAULT_JP_GAME_ROOT)
        sub.add_argument(
            "--msggame-external-validation",
            type=Path,
            default=DEFAULT_MSGGAME_EXTERNAL_VALIDATION,
        )
        if command == "refresh-lock":
            sub.add_argument("--output", type=Path)
        else:
            sub.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
        if command == "generate":
            sub.add_argument("--output-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "refresh-lock":
            value = build_lock(
                progress_path=args.progress,
                pk_sc_root=args.pk_sc_root,
                sc_strdata=args.sc_strdata,
                jp_game_root=args.jp_game_root,
                msggame_external_validation=args.msggame_external_validation,
            )
            blob = pretty_bytes(value)
            if args.output:
                atomic_write(args.output, blob)
                print(f"lock={args.output}")
            else:
                sys.stdout.buffer.write(blob)
            return 0

        validation, evidence, review, route_map, mirror, native = run_audit(
            progress_path=args.progress,
            lock_path=args.lock,
            pk_sc_root=args.pk_sc_root,
            sc_strdata=args.sc_strdata,
            jp_game_root=args.jp_game_root,
        )
        artifacts = {
            "evidence/jp_pk_message_route_evidence.v1.json": evidence,
            "review/jp_pk_message_native_blocked_review.v1.json": review,
            "public/jp_pk_message_native_route_map.v1.json": route_map,
        }
        validation["artifacts"] = {
            relative: {
                "size": len(pretty_bytes(value)),
                "sha256": sha256(pretty_bytes(value)),
            }
            for relative, value in artifacts.items()
        }
        validation["source_free_scan"] = {
            relative: artifact_source_scan(value) for relative, value in artifacts.items()
        }
        for relative, scan in validation["source_free_scan"].items():
            if scan != {"embedded_nul_count": 0, "kana_count": 0, "cjk_unified_count": 0}:
                raise RouteAuditError(f"public artifact source-text scan failed: {relative}: {scan}")
        private_manifest = {
            "schema": PRIVATE_MANIFEST_SCHEMA,
            "public_distribution_eligible": False,
            "contains_complete_game_resources": True,
            "installed_game_files_modified": False,
            "runtime_verified": False,
            "overlay_union_manifest_sha256": evidence["overlay_union"]["manifest_sha256"],
            "mirror": [
                {
                    "path": TARGET_BY_SOURCE[resource],
                    "size": len(mirror[resource]),
                    "sha256": sha256(mirror[resource]),
                }
                for resource in SC_RESOURCES
            ],
            "native_exact_subset": [
                {
                    "path": TARGET_BY_SOURCE[resource],
                    "size": len(native[resource]),
                    "sha256": sha256(native[resource]),
                }
                for resource in native
            ],
            "native_msggame_external": evidence["native_jp_control"]["external_msggame"],
        }
        if args.command == "generate":
            for relative, value in artifacts.items():
                atomic_write(WORKSTREAM_ROOT / relative, pretty_bytes(value))
            atomic_write(
                WORKSTREAM_ROOT / "translation_validation.v1.json",
                pretty_bytes(validation),
            )
            write_private_candidate(args.output_root, mirror, native, private_manifest)
            print(f"private_output={args.output_root}")
        else:
            tracked = {
                **artifacts,
                "translation_validation.v1.json": validation,
            }
            for relative, expected in tracked.items():
                path = WORKSTREAM_ROOT / relative
                if not path.exists() or path.read_bytes() != pretty_bytes(expected):
                    raise RouteAuditError(f"tracked artifact differs: {relative}")
        scope = validation["scope"]
        print(
            f"mirror={scope['mirror_transferred_count']}/{scope['overlay_effective_coordinate_count']} "
            f"native_transferable={scope['native_transferable_count']} "
            f"native_blocked={scope['native_blocked_count']}"
        )
        print("installed_game_files_modified=False")
        return 0
    except (OSError, KeyError, TypeError, ValueError, RouteAuditError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
