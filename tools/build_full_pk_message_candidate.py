#!/usr/bin/env python3
"""Rebuild the current seven-file PK message candidate offline.

The builder consumes only source-free public overlays named by
``data/public/translation_progress.v0.1.json`` and explicitly supplied,
verified baseline resource files.  It has no ``--game-root`` argument on
purpose: a live game resource is rejected as a baseline and every output must
be a new directory below ``KR_PATCH_WORK/tmp``.

The emitted binaries are private build artifacts, never a public payload.  The
adjacent manifest contains hashes, counts and validation evidence only; it
does not copy publisher source strings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
for import_root in (TOOLS_ROOT, MSGGAME_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import build_common_message_overlay as common  # noqa: E402
import msgui_catalog_v2 as msgui  # noqa: E402
from msggame_format import (  # noqa: E402
    iter_literals,
    parse_packed_msggame,
    rebuild_packed_with_literals,
    sha256 as msggame_sha256,
)
from nobu16_lz4 import LZ4Error, decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTableError, parse_message_table, rebuild_message_table  # noqa: E402


PROGRESS_SCHEMA = "nobu16.kr.translation-progress.v0.1"
MANIFEST_SCHEMA = "nobu16.kr.full-pk-message-candidate-manifest.v1"
COMMON_SCHEMA = "nobu16.kr.common-message-overlay.v1"
MSGUI_SCHEMA = "nobu16.kr.msgui-translation-overlay.v1"
MSGGAME_SCHEMA = "nobu16.kr.msggame-literal-overlay.v1"
CASTLE_SCHEMA = "nobu16.kr.castle-name-overlay.v0.2"
PROVINCE_SCHEMA = "nobu16.kr.province-names.v0.2"
DEFAULT_PROGRESS = REPO_ROOT / "data" / "public" / "translation_progress.v0.1.json"

TARGET_RESOURCES = (
    "MSG_PK/SC/msgui.bin",
    "MSG_PK/SC/msgev.bin",
    "MSG_PK/SC/msgdata.bin",
    "MSG_PK/SC/msgbre.bin",
    "MSG_PK/SC/msgire.bin",
    "MSG_PK/SC/msgstf.bin",
    "MSG_PK/SC/msggame.bin",
)
COMMON_RESOURCES = frozenset(TARGET_RESOURCES) - {
    "MSG_PK/SC/msgui.bin",
    "MSG_PK/SC/msggame.bin",
}
HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
OVERLAY_ID_RE = re.compile(r"[a-z0-9][a-z0-9._-]{0,127}\Z")
BUILDABLE_STATUSES = frozenset(("translated", "reviewed"))


class BuildError(ValueError):
    """Raised for a rejected input or a failed offline verification."""


@dataclass(frozen=True)
class OverlayInput:
    path: Path
    relative_path: str
    blob: bytes
    value: dict[str, Any]

    @property
    def sha256(self) -> str:
        return sha256_bytes(self.blob)


@dataclass(frozen=True)
class BaselineInput:
    resource: str
    path: Path
    blob: bytes
    sha256: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256_bytes(text.encode("utf-16le"))


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: dict[str, str] = {}
    for key, value in pairs:
        if not isinstance(key, str):
            raise BuildError("JSON object key is not a string")
        normalized = key.casefold()
        if normalized in folded:
            raise BuildError(
                f"duplicate or case-colliding JSON key: {key!r} / {folded[normalized]!r}"
            )
        folded[normalized] = key
        result[key] = value
    return result


def load_json_strict(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        blob = path.read_bytes()
        value = json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"invalid UTF-8 JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"JSON root must be an object: {path}")
    return value, blob


def require_exact_keys(value: Any, expected: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise BuildError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise BuildError(
            f"{label} keys differ: missing={sorted(expected - actual)!r}, "
            f"extra={sorted(actual - expected)!r}"
        )


def require_bool(value: Any, expected: bool, label: str) -> None:
    if type(value) is not bool or value is not expected:
        raise BuildError(f"{label} must be JSON {str(expected).lower()}")


def require_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise BuildError(f"{label} must be an integer >= {minimum}")
    return value


def require_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or HEX64_RE.fullmatch(value.upper()) is None:
        raise BuildError(f"{label} must be an uppercase SHA-256 hex string")
    return value.upper()


def require_semantic_ko(value: Any, label: str) -> str:
    if not isinstance(value, str) or "\x00" in value or not common.has_semantic_text(value):
        raise BuildError(f"{label} must contain semantic, NUL-free text")
    try:
        value.encode("utf-16le")
    except UnicodeEncodeError as exc:
        raise BuildError(f"{label} is not valid UTF-16 text: {exc}") from exc
    return value


def require_relative_glob(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise BuildError(f"{label} must be a non-empty relative glob")
    pure = PurePosixPath(value.replace("\\", "/"))
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
        raise BuildError(f"{label} is not a safe relative glob: {value!r}")
    if any(":" in part for part in pure.parts):
        raise BuildError(f"{label} contains a Windows drive/path separator")
    return pure.as_posix()


def assert_ordinary_existing(path: Path, label: str) -> Path:
    # Check the lexical path before resolving it: ``Path.resolve`` alone
    # would hide a symlink/junction that has already been followed.
    lexical = path if path.is_absolute() else (Path.cwd() / path)
    for candidate in (lexical, *lexical.parents):
        is_junction = getattr(candidate, "is_junction", lambda: False)()
        if candidate.is_symlink() or is_junction:
            raise BuildError(f"{label} includes a symlink or junction: {candidate}")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise BuildError(f"{label} does not exist: {path}") from exc
    for candidate in (resolved, *resolved.parents):
        is_junction = getattr(candidate, "is_junction", lambda: False)()
        if candidate.is_symlink() or is_junction:
            raise BuildError(f"{label} includes a symlink or junction: {candidate}")
    return resolved


def assert_under(root: Path, path: Path, label: str) -> Path:
    resolved_root = assert_ordinary_existing(root, f"{label} root")
    resolved_path = assert_ordinary_existing(path, label)
    if not resolved_path.is_relative_to(resolved_root):
        raise BuildError(f"{label} escapes its permitted root: {path}")
    return resolved_path


def progress_resource_overlays(progress_path: Path) -> dict[str, list[OverlayInput]]:
    progress_path = assert_under(REPO_ROOT, progress_path, "translation progress")
    progress, _progress_blob = load_json_strict(progress_path)
    if progress.get("schema") != PROGRESS_SCHEMA:
        raise BuildError("unsupported translation-progress schema")
    resources = progress.get("resources")
    if not isinstance(resources, list):
        raise BuildError("translation progress resources must be an array")

    resource_specs: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(resources):
        if not isinstance(item, dict):
            raise BuildError(f"resources[{index}] must be an object")
        path = item.get("path")
        if not isinstance(path, str):
            raise BuildError(f"resources[{index}].path must be a string")
        if path.startswith("MSG/SC/"):
            raise BuildError("base MSG/SC content is outside the PK candidate")
        if path in TARGET_RESOURCES:
            if path in resource_specs:
                raise BuildError(f"translation progress duplicates resource {path}")
            resource_specs[path] = item
    missing = sorted(set(TARGET_RESOURCES) - set(resource_specs))
    if missing:
        raise BuildError("translation progress is missing PK resource(s): " + ", ".join(missing))

    results: dict[str, list[OverlayInput]] = {}
    seen_paths: set[Path] = set()
    for resource in TARGET_RESOURCES:
        globs = resource_specs[resource].get("overlay_globs")
        if not isinstance(globs, list) or not globs:
            raise BuildError(f"{resource} has no tracked source-free overlay globs")
        overlays: list[OverlayInput] = []
        for index, raw_pattern in enumerate(globs):
            pattern = require_relative_glob(raw_pattern, f"{resource}.overlay_globs[{index}]")
            matches = sorted(REPO_ROOT.glob(pattern), key=lambda item: item.as_posix().casefold())
            if not matches:
                raise BuildError(f"tracked overlay glob has no match: {pattern}")
            for match in matches:
                match = assert_under(REPO_ROOT, match, f"tracked overlay {pattern}")
                if not match.is_file():
                    raise BuildError(f"tracked overlay is not an ordinary file: {match}")
                if match in seen_paths:
                    raise BuildError(f"overlay is listed more than once: {match}")
                seen_paths.add(match)
                value, blob = load_json_strict(match)
                overlays.append(
                    OverlayInput(
                        path=match,
                        relative_path=match.relative_to(REPO_ROOT).as_posix(),
                        blob=blob,
                        value=value,
                    )
                )
        results[resource] = overlays
    return results


def common_stock_signature(stock: Mapping[str, Any]) -> tuple[int, str, int, str, int]:
    return (
        int(stock["size"]),
        str(stock["packed_sha256"]).upper(),
        int(stock["raw_size"]),
        str(stock["raw_sha256"]).upper(),
        int(stock["string_count"]),
    )


def parse_common_overlay(value: dict[str, Any], expected_resource: str, label: str) -> dict[str, Any]:
    require_exact_keys(
        value,
        {
            "schema",
            "overlay_id",
            "resource",
            "base_language",
            "entry_count",
            "distribution_policy",
            "stock_sc",
            "defaults",
            "entries",
        },
        label,
    )
    if value["schema"] != COMMON_SCHEMA:
        raise BuildError(f"{label} has an unsupported common-message schema")
    if value["resource"] != expected_resource or expected_resource not in COMMON_RESOURCES:
        raise BuildError(f"{label} resource does not match {expected_resource}")
    if value["base_language"] != "SC":
        raise BuildError(f"{label} base_language must be SC")
    overlay_id = value["overlay_id"]
    if not isinstance(overlay_id, str) or OVERLAY_ID_RE.fullmatch(overlay_id) is None:
        raise BuildError(f"{label} overlay_id is invalid")
    policy = value["distribution_policy"]
    require_exact_keys(policy, {"contains_commercial_source_text", "contains_complete_game_resource"}, f"{label}.distribution_policy")
    require_bool(policy["contains_commercial_source_text"], False, f"{label}.contains_commercial_source_text")
    require_bool(policy["contains_complete_game_resource"], False, f"{label}.contains_complete_game_resource")
    stock = value["stock_sc"]
    require_exact_keys(stock, {"size", "packed_sha256", "raw_size", "raw_sha256", "string_count"}, f"{label}.stock_sc")
    normalized_stock = {
        "size": require_int(stock["size"], f"{label}.stock_sc.size", minimum=1),
        "packed_sha256": require_hash(stock["packed_sha256"], f"{label}.stock_sc.packed_sha256"),
        "raw_size": require_int(stock["raw_size"], f"{label}.stock_sc.raw_size", minimum=1),
        "raw_sha256": require_hash(stock["raw_sha256"], f"{label}.stock_sc.raw_sha256"),
        "string_count": require_int(stock["string_count"], f"{label}.stock_sc.string_count", minimum=1),
    }
    defaults = value["defaults"]
    require_exact_keys(defaults, {"status"}, f"{label}.defaults")
    if defaults["status"] not in BUILDABLE_STATUSES:
        raise BuildError(f"{label}.defaults.status is not buildable")
    entries = value["entries"]
    if not isinstance(entries, list):
        raise BuildError(f"{label}.entries must be an array")
    if require_int(value["entry_count"], f"{label}.entry_count", minimum=1) != len(entries):
        raise BuildError(f"{label}.entry_count does not match entries")
    normalized_entries: list[dict[str, Any]] = []
    ids: list[int] = []
    for index, entry in enumerate(entries):
        entry_label = f"{label}.entries[{index}]"
        if not isinstance(entry, dict):
            raise BuildError(f"{entry_label} must be an object")
        required = {"id", "source_sc_utf16le_sha256", "ko"}
        allowed = required | {"status", "allow_edge_whitespace_change"}
        actual = set(entry)
        if not required <= actual or not actual <= allowed:
            raise BuildError(f"{entry_label} contains unsupported keys")
        entry_id = require_int(entry["id"], f"{entry_label}.id")
        status = entry.get("status", defaults["status"])
        if status not in BUILDABLE_STATUSES:
            raise BuildError(f"{entry_label}.status is not buildable")
        allow_edge_whitespace_change = entry.get("allow_edge_whitespace_change", False)
        if type(allow_edge_whitespace_change) is not bool:
            raise BuildError(f"{entry_label}.allow_edge_whitespace_change must be boolean")
        ids.append(entry_id)
        normalized_entries.append(
            {
                "id": entry_id,
                "source_hash": require_hash(entry["source_sc_utf16le_sha256"], f"{entry_label}.source hash"),
                "ko": require_semantic_ko(entry["ko"], f"{entry_label}.ko"),
                "status": status,
                "allow_edge_whitespace_change": allow_edge_whitespace_change,
            }
        )
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise BuildError(f"{label} ids must be sorted and unique")
    return {"kind": "common", "overlay_id": overlay_id, "stock": normalized_stock, "entries": normalized_entries}


def parse_castle_overlay(value: dict[str, Any], label: str) -> dict[str, Any]:
    require_exact_keys(
        value,
        {"entries", "review", "schema", "source_text_free", "target", "translation_policy"},
        label,
    )
    if value["schema"] != CASTLE_SCHEMA or value["source_text_free"] is not True:
        raise BuildError(f"{label} is not a source-free castle-name overlay")
    target = value["target"]
    require_exact_keys(
        target,
        {"entry_count", "first_id", "last_id", "resource", "shared_suffix_id_range_not_modified"},
        f"{label}.target",
    )
    if target["resource"] != "MSG_PK/SC/msgdata.bin":
        raise BuildError(f"{label} targets a non-PK msgdata resource")
    entries = value["entries"]
    if not isinstance(entries, list) or not entries:
        raise BuildError(f"{label}.entries must be a non-empty array")
    if require_int(target["entry_count"], f"{label}.target.entry_count", minimum=1) != len(entries):
        raise BuildError(f"{label}.target entry count does not match entries")
    normalized: list[dict[str, Any]] = []
    ids: list[int] = []
    allowed_methods = {"en_romaji", "en_romaji_words", "en_romaji_jp_n_y_boundary"}
    for index, entry in enumerate(entries):
        entry_label = f"{label}.entries[{index}]"
        require_exact_keys(entry, {"id", "ko", "method", "status"}, entry_label)
        if entry["method"] not in allowed_methods or entry["status"] != "reviewed":
            raise BuildError(f"{entry_label} is not a reviewed approved name mapping")
        entry_id = require_int(entry["id"], f"{entry_label}.id")
        ids.append(entry_id)
        normalized.append({"id": entry_id, "ko": require_semantic_ko(entry["ko"], f"{entry_label}.ko"), "status": "reviewed"})
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise BuildError(f"{label} ids must be sorted and unique")
    if ids[0] != require_int(target["first_id"], f"{label}.target.first_id") or ids[-1] != require_int(target["last_id"], f"{label}.target.last_id"):
        raise BuildError(f"{label} target range does not match entries")
    return {"kind": "castle", "overlay_id": value["schema"], "stock": None, "entries": normalized}


def parse_province_overlay(value: dict[str, Any], label: str) -> dict[str, Any]:
    require_exact_keys(
        value,
        {"base_language", "distribution_policy", "entries", "resource", "review", "schema", "scope", "translation_policy"},
        label,
    )
    if value["schema"] != PROVINCE_SCHEMA or value["resource"] != "MSG_PK/SC/msgdata.bin" or value["base_language"] != "SC":
        raise BuildError(f"{label} is not a PK SC province-name overlay")
    policy = value["distribution_policy"]
    require_exact_keys(policy, {"contains_commercial_source_text", "contains_complete_game_resource"}, f"{label}.distribution_policy")
    require_bool(policy["contains_commercial_source_text"], False, f"{label}.contains_commercial_source_text")
    require_bool(policy["contains_complete_game_resource"], False, f"{label}.contains_complete_game_resource")
    scope = value["scope"]
    require_exact_keys(scope, {"entry_count", "first_id", "last_id"}, f"{label}.scope")
    entries = value["entries"]
    if not isinstance(entries, list) or not entries:
        raise BuildError(f"{label}.entries must be a non-empty array")
    if require_int(scope["entry_count"], f"{label}.scope.entry_count", minimum=1) != len(entries):
        raise BuildError(f"{label}.scope entry count does not match entries")
    normalized: list[dict[str, Any]] = []
    ids: list[int] = []
    for index, entry in enumerate(entries):
        entry_label = f"{label}.entries[{index}]"
        require_exact_keys(entry, {"id", "ko", "status"}, entry_label)
        if entry["status"] != "reviewed":
            raise BuildError(f"{entry_label}.status must be reviewed")
        entry_id = require_int(entry["id"], f"{entry_label}.id")
        ids.append(entry_id)
        normalized.append({"id": entry_id, "ko": require_semantic_ko(entry["ko"], f"{entry_label}.ko"), "status": "reviewed"})
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise BuildError(f"{label} ids must be sorted and unique")
    if ids[0] != require_int(scope["first_id"], f"{label}.scope.first_id") or ids[-1] != require_int(scope["last_id"], f"{label}.scope.last_id"):
        raise BuildError(f"{label} scope range does not match entries")
    return {"kind": "province", "overlay_id": value["schema"], "stock": None, "entries": normalized}


def parse_msgui_overlay(value: dict[str, Any], label: str) -> dict[str, Any]:
    try:
        msgui.validate_translation_overlay_shape(value)
    except msgui.CatalogError as exc:
        raise BuildError(f"{label} is not a valid source-free MSGUI overlay: {exc}") from exc
    if value["schema"] != MSGUI_SCHEMA:
        raise BuildError(f"{label} has an unsupported MSGUI schema")
    entries: list[dict[str, Any]] = []
    for item in value["entries"]:
        status = item.get("status", value["defaults"]["status"])
        entries.append(
            {
                "id": int(item["id"]),
                "source_hash": str(item["source_sc_utf16le_sha256"]).upper(),
                "ko": str(item["ko"]),
                "status": status,
                "invariant_overrides": tuple(item.get("invariant_overrides", [])),
            }
        )
    return {"overlay_id": value["overlay_id"], "stock": value["stock_sc"], "entries": entries}


def parse_msggame_overlay(value: dict[str, Any], label: str) -> dict[str, Any]:
    allowed_root = {
        "schema", "overlay_id", "resource", "base_language", "entry_count", "distribution_policy", "stock_sc", "defaults", "entries"
    }
    for optional_key in (
        "migration_provenance",
        "selection_policy",
        "translation_provenance",
    ):
        if optional_key in value:
            allowed_root.add(optional_key)
    require_exact_keys(value, allowed_root, label)
    if value["schema"] != MSGGAME_SCHEMA or value["resource"] != "MSG_PK/SC/msggame.bin" or value["base_language"] != "SC":
        raise BuildError(f"{label} is not a PK SC msggame overlay")
    overlay_id = value["overlay_id"]
    if not isinstance(overlay_id, str) or OVERLAY_ID_RE.fullmatch(overlay_id) is None:
        raise BuildError(f"{label}.overlay_id is invalid")
    policy = value["distribution_policy"]
    require_exact_keys(policy, {"contains_commercial_source_text", "contains_complete_game_resource"}, f"{label}.distribution_policy")
    require_bool(policy["contains_commercial_source_text"], False, f"{label}.contains_commercial_source_text")
    require_bool(policy["contains_complete_game_resource"], False, f"{label}.contains_complete_game_resource")
    defaults = value["defaults"]
    require_exact_keys(defaults, {"status"}, f"{label}.defaults")
    if defaults["status"] not in BUILDABLE_STATUSES:
        raise BuildError(f"{label}.defaults.status is not buildable")
    stock = value["stock_sc"]
    require_exact_keys(stock, {"packed_size", "packed_sha256", "raw_size", "raw_sha256", "record_count", "literal_slot_count"}, f"{label}.stock_sc")
    normalized_stock = {
        "packed_size": require_int(stock["packed_size"], f"{label}.stock_sc.packed_size", minimum=1),
        "packed_sha256": require_hash(stock["packed_sha256"], f"{label}.stock_sc.packed_sha256"),
        "raw_size": require_int(stock["raw_size"], f"{label}.stock_sc.raw_size", minimum=1),
        "raw_sha256": require_hash(stock["raw_sha256"], f"{label}.stock_sc.raw_sha256"),
        "record_count": require_int(stock["record_count"], f"{label}.stock_sc.record_count", minimum=1),
        "literal_slot_count": require_int(stock["literal_slot_count"], f"{label}.stock_sc.literal_slot_count", minimum=1),
    }
    provenance = value.get("migration_provenance")
    if provenance is not None:
        base_provenance_keys = {
            "asset_sha256",
            "author",
            "kind",
            "release_tag",
            "repository_url",
            "source_text_embedded",
        }
        provenance_keys = set(provenance)
        if provenance_keys not in (
            base_provenance_keys,
            base_provenance_keys | {"v13_text_identical_to_v11"},
        ):
            missing = sorted(base_provenance_keys - provenance_keys)
            extra = sorted(provenance_keys - base_provenance_keys - {"v13_text_identical_to_v11"})
            raise BuildError(
                f"{label}.migration_provenance keys differ: "
                f"missing={missing}, extra={extra}"
            )
        require_hash(provenance["asset_sha256"], f"{label}.migration_provenance.asset_sha256")
        require_bool(provenance["source_text_embedded"], False, f"{label}.migration_provenance.source_text_embedded")
        if "v13_text_identical_to_v11" in provenance:
            require_bool(
                provenance["v13_text_identical_to_v11"],
                True,
                f"{label}.migration_provenance.v13_text_identical_to_v11",
            )
        for key in ("author", "kind", "release_tag", "repository_url"):
            if not isinstance(provenance[key], str) or not provenance[key]:
                raise BuildError(f"{label}.migration_provenance.{key} must be a non-empty string")
    translation_provenance = value.get("translation_provenance")
    if translation_provenance is not None:
        base_translation_keys = {
            "context_languages",
            "kind",
            "runtime_reviewed",
            "source_text_embedded",
        }
        translation_keys = set(translation_provenance)
        missing_translation_keys = sorted(base_translation_keys - translation_keys)
        extra_translation_keys = sorted(
            translation_keys - base_translation_keys - {"switch_context"}
        )
        if missing_translation_keys or extra_translation_keys:
            raise BuildError(
                f"{label}.translation_provenance keys differ: "
                f"missing={missing_translation_keys}, extra={extra_translation_keys}"
            )
        if translation_provenance["context_languages"] not in (
            ["SC", "JP", "EN"],
            ["SC", "JP", "EN", "TC"],
        ):
            raise BuildError(
                f"{label}.translation_provenance.context_languages must be "
                "the reviewed SC/JP/EN or SC/JP/EN/TC context set"
            )
        if not isinstance(translation_provenance["kind"], str) or not translation_provenance["kind"]:
            raise BuildError(f"{label}.translation_provenance.kind must be a non-empty string")
        if not isinstance(translation_provenance["runtime_reviewed"], bool):
            raise BuildError(f"{label}.translation_provenance.runtime_reviewed must be boolean")
        require_bool(
            translation_provenance["source_text_embedded"],
            False,
            f"{label}.translation_provenance.source_text_embedded",
        )
        switch_context = translation_provenance.get("switch_context")
        if switch_context is not None:
            require_exact_keys(
                switch_context,
                {
                    "asset_sha256",
                    "author",
                    "release_tag",
                    "repository_url",
                    "unique_jp_hash_alignment_count",
                    "use",
                },
                f"{label}.translation_provenance.switch_context",
            )
            require_hash(
                switch_context["asset_sha256"],
                f"{label}.translation_provenance.switch_context.asset_sha256",
            )
            for key in ("author", "release_tag", "repository_url", "use"):
                if not isinstance(switch_context[key], str) or not switch_context[key]:
                    raise BuildError(
                        f"{label}.translation_provenance.switch_context.{key} "
                        "must be a non-empty string"
                    )
            require_int(
                switch_context["unique_jp_hash_alignment_count"],
                f"{label}.translation_provenance.switch_context.unique_jp_hash_alignment_count",
                minimum=1,
            )
    selection_policy = value.get("selection_policy")
    if selection_policy is not None:
        base_selection_keys = {"priority", "source_text_embedded"}
        allowed_selection_keys = base_selection_keys | {
            "block_entry_counts",
            "blocks",
            "dynamic_fragments_excluded",
            "event_dialogue_block_17_excluded",
            "event_dialogue_excluded",
            "format_control_pua_free_selection",
            "read_only_predecessor",
            "read_only_predecessors",
            "single_literal_records_only",
        }
        selection_keys = set(selection_policy)
        missing_selection_keys = sorted(base_selection_keys - selection_keys)
        extra_selection_keys = sorted(selection_keys - allowed_selection_keys)
        if missing_selection_keys or extra_selection_keys:
            raise BuildError(
                f"{label}.selection_policy keys differ: "
                f"missing={missing_selection_keys}, extra={extra_selection_keys}"
            )
        for key in (
            "dynamic_fragments_excluded",
            "event_dialogue_block_17_excluded",
            "event_dialogue_excluded",
            "format_control_pua_free_selection",
            "single_literal_records_only",
        ):
            if key in selection_policy:
                require_bool(
                    selection_policy[key],
                    True,
                    f"{label}.selection_policy.{key}",
                )
        if not isinstance(selection_policy["priority"], str) or not selection_policy["priority"]:
            raise BuildError(f"{label}.selection_policy.priority must be a non-empty string")
        require_bool(
            selection_policy["source_text_embedded"],
            False,
            f"{label}.selection_policy.source_text_embedded",
        )
        blocks = selection_policy.get("blocks")
        if blocks is not None:
            if (
                not isinstance(blocks, list)
                or not blocks
                or any(not isinstance(block, int) or isinstance(block, bool) for block in blocks)
                or blocks != sorted(set(blocks))
            ):
                raise BuildError(
                    f"{label}.selection_policy.blocks must be sorted unique integers"
                )
        block_entry_counts = selection_policy.get("block_entry_counts")
        if block_entry_counts is not None:
            if not isinstance(block_entry_counts, dict) or not block_entry_counts:
                raise BuildError(
                    f"{label}.selection_policy.block_entry_counts must be a non-empty object"
                )
            normalized_count_blocks: list[int] = []
            for block, count in block_entry_counts.items():
                if not isinstance(block, str) or not block.isdecimal():
                    raise BuildError(
                        f"{label}.selection_policy.block_entry_counts keys must be decimal block ids"
                    )
                normalized_count_blocks.append(int(block))
                require_int(
                    count,
                    f"{label}.selection_policy.block_entry_counts[{block}]",
                    minimum=1,
                )
            if blocks is not None and sorted(normalized_count_blocks) != blocks:
                raise BuildError(
                    f"{label}.selection_policy.block_entry_counts must match blocks"
                )
        predecessor = selection_policy.get("read_only_predecessor")
        predecessors = selection_policy.get("read_only_predecessors")
        if predecessor is not None and predecessors is not None:
            raise BuildError(
                f"{label}.selection_policy cannot declare both predecessor forms"
            )
        if predecessor is not None and (not isinstance(predecessor, str) or not predecessor):
            raise BuildError(
                f"{label}.selection_policy.read_only_predecessor must be a non-empty string"
            )
        if predecessors is not None and (
            not isinstance(predecessors, list)
            or not predecessors
            or any(not isinstance(item, str) or not item for item in predecessors)
            or len(predecessors) != len(set(predecessors))
        ):
            raise BuildError(
                f"{label}.selection_policy.read_only_predecessors must be unique non-empty strings"
            )
    entries = value["entries"]
    if not isinstance(entries, list):
        raise BuildError(f"{label}.entries must be an array")
    if require_int(value["entry_count"], f"{label}.entry_count", minimum=1) != len(entries):
        raise BuildError(f"{label}.entry_count does not match entries")
    normalized_entries: list[dict[str, Any]] = []
    coordinates: list[tuple[int, int, int]] = []
    for index, entry in enumerate(entries):
        entry_label = f"{label}.entries[{index}]"
        require_exact_keys(entry, {"block_id", "record_id", "literal_id", "source_sc_utf16le_sha256", "ko"}, entry_label)
        coordinate = (
            require_int(entry["block_id"], f"{entry_label}.block_id"),
            require_int(entry["record_id"], f"{entry_label}.record_id"),
            require_int(entry["literal_id"], f"{entry_label}.literal_id"),
        )
        coordinates.append(coordinate)
        normalized_entries.append(
            {
                "coordinate": coordinate,
                "source_hash": require_hash(entry["source_sc_utf16le_sha256"], f"{entry_label}.source hash"),
                "ko": require_semantic_ko(entry["ko"], f"{entry_label}.ko"),
            }
        )
    if len(coordinates) != len(set(coordinates)):
        raise BuildError(f"{label} contains a duplicate literal coordinate")
    return {"overlay_id": overlay_id, "stock": normalized_stock, "entries": normalized_entries}


def common_source_spec(blob: bytes, raw: bytes, string_count: int) -> dict[str, Any]:
    return {
        "size": len(blob),
        "packed_sha256": sha256_bytes(blob),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
        "string_count": string_count,
    }


def msggame_source_spec(blob: bytes) -> tuple[dict[str, Any], Any, dict[tuple[int, int, int], Any]]:
    parsed = parse_packed_msggame(blob)
    _header, raw = decompress_wrapper(blob)
    literals = {
        (literal.block_id, literal.record_id, literal.literal_id): literal
        for literal in iter_literals(parsed.archive)
    }
    return (
        {
            "packed_size": len(blob),
            "packed_sha256": msggame_sha256(blob),
            "raw_size": len(raw),
            "raw_sha256": msggame_sha256(raw),
            "record_count": parsed.archive.record_count,
            "literal_slot_count": len(literals),
        },
        parsed,
        literals,
    )


def matching_common_stage(stock: Mapping[str, Any], stage: Mapping[str, Any]) -> bool:
    return common_stock_signature(stock) == common_stock_signature(stage)


def matching_msggame_stage(stock: Mapping[str, Any], stage: Mapping[str, Any]) -> bool:
    return tuple(stock[key] for key in ("packed_size", "packed_sha256", "raw_size", "raw_sha256", "record_count", "literal_slot_count")) == tuple(
        stage[key] for key in ("packed_size", "packed_sha256", "raw_size", "raw_sha256", "record_count", "literal_slot_count")
    )


def msggame_manifest_stage(stage: Mapping[str, Any]) -> dict[str, Any]:
    """Use the same compact target naming as the other candidate resources."""

    return {
        "size": int(stage["packed_size"]),
        "sha256": str(stage["packed_sha256"]),
        "raw_size": int(stage["raw_size"]),
        "raw_sha256": str(stage["raw_sha256"]),
        "record_count": int(stage["record_count"]),
        "literal_slot_count": int(stage["literal_slot_count"]),
    }


def id_digest(ids: Sequence[int]) -> str:
    return sha256_bytes(json.dumps(list(ids), separators=(",", ":")).encode("utf-8"))


def coordinate_digest(coordinates: Sequence[tuple[int, int, int]]) -> str:
    return sha256_bytes(json.dumps([list(item) for item in coordinates], separators=(",", ":")).encode("utf-8"))


def apply_common_resource(resource: str, baseline: BaselineInput, overlays: Sequence[OverlayInput]) -> tuple[bytes, dict[str, Any]]:
    try:
        _header, raw = decompress_wrapper(baseline.blob)
        table = parse_message_table(raw)
    except (LZ4Error, MessageTableError) as exc:
        raise BuildError(f"{resource} baseline cannot be parsed as a wrapped message table: {exc}") from exc
    if rebuild_message_table(table, table.texts) != raw:
        raise BuildError(f"{resource} baseline message-table parse/rebuild is not byte-exact")
    initial_stage = common_source_spec(baseline.blob, raw, table.string_count)
    texts = list(table.texts)
    observed_stages = [initial_stage]
    parsed_overlays: list[tuple[OverlayInput, dict[str, Any]]] = []
    for overlay in overlays:
        label = overlay.relative_path
        schema = overlay.value.get("schema")
        if schema == COMMON_SCHEMA:
            parsed = parse_common_overlay(overlay.value, resource, label)
        elif resource == "MSG_PK/SC/msgdata.bin" and schema == CASTLE_SCHEMA:
            parsed = parse_castle_overlay(overlay.value, label)
        elif resource == "MSG_PK/SC/msgdata.bin" and schema == PROVINCE_SCHEMA:
            parsed = parse_province_overlay(overlay.value, label)
        else:
            raise BuildError(f"{label} uses an unsupported schema for {resource}: {schema!r}")
        parsed_overlays.append((overlay, parsed))
    common_specs = [parsed["stock"] for _overlay, parsed in parsed_overlays if parsed["stock"] is not None]
    if not any(matching_common_stage(spec, initial_stage) for spec in common_specs):
        raise BuildError(f"{resource} baseline does not match a declared pinned source stage")

    seen: dict[int, tuple[str, str]] = {}
    overlap_overrides: list[dict[str, Any]] = []
    operation_ids: list[int] = []
    source_hash_validated = 0
    generated_source_hashes = 0
    invariant_checks = 0
    reviewed_name_edge_whitespace_exception_count = 0
    stage_records: list[dict[str, Any]] = []
    overlay_manifest: list[dict[str, Any]] = []
    for overlay, parsed in parsed_overlays:
        kind = str(parsed["kind"])
        stock = parsed["stock"]
        stock_matches_prior_stage = stock is None or any(
            matching_common_stage(stock, stage) for stage in observed_stages
        )
        if not stock_matches_prior_stage:
            raise BuildError(
                f"{overlay.relative_path} stock pin is not a known prior verified stage for {resource}"
            )
        changed_before = len(operation_ids)
        for entry in parsed["entries"]:
            entry_id = int(entry["id"])
            if not 0 <= entry_id < table.string_count:
                raise BuildError(f"{overlay.relative_path} id {entry_id} is outside message table")
            source = texts[entry_id]
            if "source_hash" in entry:
                if text_hash(source) != entry["source_hash"]:
                    raise BuildError(f"{overlay.relative_path} source hash mismatch at id {entry_id}")
                source_hash_validated += 1
            else:
                generated_source_hashes += 1
            allow_edge = bool(entry.get("allow_edge_whitespace_change", False)) or kind in {"castle", "province"}
            if allow_edge:
                before_whitespace = common.message_invariants(source)
                after_whitespace = common.message_invariants(entry["ko"])
                if (
                    before_whitespace["leading_whitespace"] != after_whitespace["leading_whitespace"]
                    or before_whitespace["trailing_whitespace"] != after_whitespace["trailing_whitespace"]
                ):
                    reviewed_name_edge_whitespace_exception_count += 1
            mismatches = common.invariant_mismatches(
                source, entry["ko"], allow_edge_whitespace_change=allow_edge
            )
            if mismatches:
                raise BuildError(
                    f"{overlay.relative_path} invariant mismatch at id {entry_id}: {'; '.join(mismatches)}"
                )
            invariant_checks += 1
            if entry_id in seen:
                previous_kind, previous_overlay = seen[entry_id]
                if not (
                    resource == "MSG_PK/SC/msgdata.bin"
                    and kind in {"castle", "province"}
                    and previous_kind == "common"
                ):
                    raise BuildError(
                        f"unapproved overlapping id {entry_id}: {previous_overlay} -> {overlay.relative_path}"
                    )
                overlap_overrides.append(
                    {
                        "id": entry_id,
                        "previous_overlay": previous_overlay,
                        "effective_overlay": overlay.relative_path,
                        "rule": "reviewed_geographic_name_overrides_prior_generic_name",
                    }
                )
            if entry["ko"] != source:
                operation_ids.append(entry_id)
            texts[entry_id] = entry["ko"]
            seen[entry_id] = (kind, overlay.relative_path)
        staged_raw = rebuild_message_table(table, texts)
        staged_blob = recompress_wrapper(staged_raw, baseline.blob)
        _staged_header, staged_raw_check = decompress_wrapper(staged_blob)
        if staged_raw_check != staged_raw:
            raise BuildError(f"{overlay.relative_path} staged wrapper verification failed")
        stage = common_source_spec(staged_blob, staged_raw, table.string_count)
        observed_stages.append(stage)
        stage_records.append(
            {
                "overlay": overlay.relative_path,
                "kind": kind,
                "changed_entry_count": len(operation_ids) - changed_before,
                "stage_sha256": stage["packed_sha256"],
                "stage_raw_sha256": stage["raw_sha256"],
            }
        )
        overlay_manifest.append(
            {
                "path": overlay.relative_path,
                "sha256": overlay.sha256,
                "schema": overlay.value["schema"],
                "overlay_id": parsed["overlay_id"],
                "entry_count": len(parsed["entries"]),
                "source_pin_matches_prior_stage": stock_matches_prior_stage,
            }
        )
    rebuilt_raw = rebuild_message_table(table, texts)
    reparsed = parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise BuildError(f"{resource} rebuilt message table failed parse verification")
    target = recompress_wrapper(rebuilt_raw, baseline.blob)
    _target_header, target_raw_check = decompress_wrapper(target)
    if target_raw_check != rebuilt_raw:
        raise BuildError(f"{resource} rebuilt wrapper failed decompression verification")
    result = {
        "resource": resource,
        "kind": "common_message_table",
        "baseline": {
            "size": initial_stage["size"],
            "sha256": initial_stage["packed_sha256"],
            "raw_size": initial_stage["raw_size"],
            "raw_sha256": initial_stage["raw_sha256"],
            "string_count": table.string_count,
        },
        "target": {
            "size": len(target),
            "sha256": sha256_bytes(target),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256_bytes(rebuilt_raw),
            "string_count": table.string_count,
        },
        "overlay_entry_count": sum(len(parsed["entries"]) for _overlay, parsed in parsed_overlays),
        "unique_effective_id_count": len(seen),
        "changed_entry_count": len(set(operation_ids)),
        "changed_ids_sha256": id_digest(sorted(set(operation_ids))),
        "source_hash_validated_count": source_hash_validated,
        "source_hash_generated_for_name_overlay_count": generated_source_hashes,
        "control_printf_esc_whitespace_invariant_count": invariant_checks,
        "reviewed_name_edge_whitespace_exception_count": reviewed_name_edge_whitespace_exception_count,
        "ordered_overlap_overrides": overlap_overrides,
        "overlays": overlay_manifest,
        "verified_stages": stage_records,
        "checks": {
            "baseline_matches_declared_source_stage": True,
            "declared_source_hashes": True,
            "source_free_reviewed_geographic_name_entries": generated_source_hashes > 0,
            "control_printf_esc_whitespace": True,
            "reviewed_name_edge_whitespace_exceptions": True,
            "ordered_overlaps": True,
            "table_parse_roundtrip": True,
            "wrapper_decompress_roundtrip": True,
            "publisher_source_text_in_manifest": False,
        },
    }
    return target, result


def apply_msgui_resource(baseline: BaselineInput, overlays: Sequence[OverlayInput]) -> tuple[bytes, dict[str, Any]]:
    if len(overlays) != 1:
        raise BuildError("MSGUI must have exactly one tracked current overlay")
    overlay = overlays[0]
    parsed = parse_msgui_overlay(overlay.value, overlay.relative_path)
    try:
        _header, raw = decompress_wrapper(baseline.blob)
        table = parse_message_table(raw)
    except (LZ4Error, MessageTableError) as exc:
        raise BuildError(f"MSGUI baseline cannot be parsed: {exc}") from exc
    stock = parsed["stock"]
    if sha256_bytes(baseline.blob) != str(stock["packed_sha256"]).upper() or sha256_bytes(raw) != str(stock["raw_sha256"]).upper() or table.string_count != int(stock["string_count"]):
        raise BuildError("MSGUI baseline does not match the source-free overlay stock pins")
    if rebuild_message_table(table, table.texts) != raw:
        raise BuildError("MSGUI baseline parse/rebuild is not byte-exact")
    texts = list(table.texts)
    changed_ids: list[int] = []
    invariant_override_records: list[dict[str, Any]] = []
    activated_whitespace_source_ids: list[int] = []
    for entry in parsed["entries"]:
        entry_id = int(entry["id"])
        if not 0 <= entry_id < table.string_count:
            raise BuildError(f"MSGUI id {entry_id} is outside message table")
        source = texts[entry_id]
        if text_hash(source) != entry["source_hash"]:
            raise BuildError(f"MSGUI source hash mismatch at id {entry_id}")
        before = common.message_invariants(source)
        after = common.message_invariants(entry["ko"])
        override_keys: set[str] = set()
        for token in entry["invariant_overrides"]:
            if not isinstance(token, str) or ":" not in token:
                raise BuildError(f"MSGUI id {entry_id} has an invalid invariant override")
            key, language = token.split(":", 1)
            if key not in {"printf", "line_breaks"} or language not in {"EN", "JP"}:
                raise BuildError(f"MSGUI id {entry_id} has an unsupported invariant override")
            override_keys.add(key)
        reference_override_keys = set(override_keys)
        # The public MSGUI catalog intentionally activates a small number of
        # stock whitespace-only slots.  Preserve all non-whitespace contracts
        # for them, but do not mistake the stock spacer itself for visible
        # leading/trailing text.  This exception is derived from the live
        # source value and recorded by id in the source-free build manifest.
        if not common.has_semantic_text(source):
            override_keys.update({"leading_whitespace", "trailing_whitespace"})
            activated_whitespace_source_ids.append(entry_id)
        mismatches = [
            key
            for key in before
            if key not in override_keys and before[key] != after[key]
        ]
        if mismatches:
            raise BuildError(f"MSGUI invariant mismatch at id {entry_id}: {', '.join(mismatches)}")
        if reference_override_keys:
            invariant_override_records.append(
                {
                    "id": entry_id,
                    "keys": sorted(reference_override_keys),
                    "reviewed": entry["status"] == "reviewed",
                    "policy": "explicit_source_free_reviewed_reference_override",
                }
            )
            if entry["status"] != "reviewed":
                raise BuildError(f"MSGUI id {entry_id} invariant overrides require reviewed status")
        if entry["ko"] != source:
            changed_ids.append(entry_id)
        texts[entry_id] = entry["ko"]
    rebuilt_raw = rebuild_message_table(table, texts)
    if parse_message_table(rebuilt_raw).texts != tuple(texts):
        raise BuildError("MSGUI rebuilt table failed parse verification")
    target = recompress_wrapper(rebuilt_raw, baseline.blob)
    _target_header, target_raw = decompress_wrapper(target)
    if target_raw != rebuilt_raw:
        raise BuildError("MSGUI rebuilt wrapper failed decompression verification")
    result = {
        "resource": "MSG_PK/SC/msgui.bin",
        "kind": "msgui_translation_overlay",
        "baseline": {
            "size": len(baseline.blob),
            "sha256": sha256_bytes(baseline.blob),
            "raw_size": len(raw),
            "raw_sha256": sha256_bytes(raw),
            "string_count": table.string_count,
        },
        "target": {
            "size": len(target),
            "sha256": sha256_bytes(target),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256_bytes(rebuilt_raw),
            "string_count": table.string_count,
        },
        "overlay_entry_count": len(parsed["entries"]),
        "unique_effective_id_count": len(parsed["entries"]),
        "changed_entry_count": len(changed_ids),
        "changed_ids_sha256": id_digest(changed_ids),
        "source_hash_validated_count": len(parsed["entries"]),
        "control_printf_esc_whitespace_invariant_count": len(parsed["entries"]),
        "activated_whitespace_source_slot_count": len(activated_whitespace_source_ids),
        "activated_whitespace_source_ids_sha256": id_digest(activated_whitespace_source_ids),
        "explicit_reviewed_reference_override_count": len(invariant_override_records),
        "explicit_reviewed_reference_overrides": invariant_override_records,
        "overlays": [{"path": overlay.relative_path, "sha256": overlay.sha256, "schema": overlay.value["schema"], "overlay_id": parsed["overlay_id"], "entry_count": len(parsed["entries"])}],
        "checks": {
            "baseline_matches_declared_source_stage": True,
            "declared_source_hashes": True,
            "control_printf_esc_whitespace": True,
            "whitespace_only_stock_slots_explicitly_classified": True,
            "explicit_reference_overrides_reviewed": True,
            "table_parse_roundtrip": True,
            "wrapper_decompress_roundtrip": True,
            "publisher_source_text_in_manifest": False,
        },
    }
    return target, result


def apply_msggame_resource(baseline: BaselineInput, overlays: Sequence[OverlayInput]) -> tuple[bytes, dict[str, Any]]:
    try:
        initial_stage, parsed_archive, literals = msggame_source_spec(baseline.blob)
    except (LZ4Error, ValueError) as exc:
        raise BuildError(f"msggame baseline cannot be parsed: {exc}") from exc
    parsed_overlays = [parse_msggame_overlay(item.value, item.relative_path) for item in overlays]
    if not any(matching_msggame_stage(item["stock"], initial_stage) for item in parsed_overlays):
        raise BuildError("msggame baseline does not match a declared pinned source stage")
    replacements: dict[tuple[int, int, int], str] = {}
    coordinates: list[tuple[int, int, int]] = []
    invariant_checks = 0
    overlay_manifest: list[dict[str, Any]] = []
    for overlay, parsed in zip(overlays, parsed_overlays, strict=True):
        if not matching_msggame_stage(parsed["stock"], initial_stage):
            raise BuildError(f"{overlay.relative_path} stock pin is not the verified msggame source stage")
        for entry in parsed["entries"]:
            coordinate = entry["coordinate"]
            source = literals.get(coordinate)
            if source is None:
                raise BuildError(f"{overlay.relative_path} literal coordinate does not exist: {coordinate}")
            if coordinate in replacements:
                raise BuildError(f"duplicate msggame literal coordinate across overlays: {coordinate}")
            if text_hash(source.text) != entry["source_hash"]:
                raise BuildError(f"{overlay.relative_path} source hash mismatch at coordinate {coordinate}")
            mismatches = common.invariant_mismatches(source.text, entry["ko"])
            if mismatches:
                raise BuildError(
                    f"{overlay.relative_path} invariant mismatch at coordinate {coordinate}: {'; '.join(mismatches)}"
                )
            replacements[coordinate] = entry["ko"]
            coordinates.append(coordinate)
            invariant_checks += 1
        overlay_manifest.append(
            {
                "path": overlay.relative_path,
                "sha256": overlay.sha256,
                "schema": overlay.value["schema"],
                "overlay_id": parsed["overlay_id"],
                "entry_count": len(parsed["entries"]),
            }
        )
    target = rebuild_packed_with_literals(baseline.blob, replacements)
    target_stage, target_parsed, target_literals = msggame_source_spec(target)
    if target_parsed.archive.record_count != parsed_archive.archive.record_count:
        raise BuildError("msggame record count changed while rebuilding")
    for coordinate, replacement in replacements.items():
        if target_literals[coordinate].text != replacement:
            raise BuildError(f"msggame rebuilt literal failed verification at {coordinate}")
    result = {
        "resource": "MSG_PK/SC/msggame.bin",
        "kind": "msggame_literal_overlay",
        "baseline": msggame_manifest_stage(initial_stage),
        "target": msggame_manifest_stage(target_stage),
        "overlay_entry_count": sum(len(item["entries"]) for item in parsed_overlays),
        "unique_effective_coordinate_count": len(replacements),
        "changed_coordinate_count": len(replacements),
        "changed_coordinates_sha256": coordinate_digest(sorted(coordinates)),
        "source_hash_validated_count": len(replacements),
        "control_printf_esc_whitespace_invariant_count": invariant_checks,
        "overlays": overlay_manifest,
        "checks": {
            "baseline_matches_declared_source_stage": True,
            "declared_source_hashes": True,
            "control_printf_esc_whitespace": True,
            "literal_coordinates_unique": True,
            "record_count_preserved": True,
            "wrapper_decompress_roundtrip": True,
            "publisher_source_text_in_manifest": False,
        },
    }
    return target, result


def parse_stock_args(values: Sequence[str]) -> dict[str, Path]:
    supplied: dict[str, Path] = {}
    for raw in values:
        resource, separator, path_text = raw.partition("=")
        if not separator or resource not in TARGET_RESOURCES or not path_text:
            raise BuildError("--stock must be exactly RESOURCE=ABSOLUTE_PATH for a PK target resource")
        if resource in supplied:
            raise BuildError(f"duplicate --stock resource: {resource}")
        path = Path(path_text)
        if not path.is_absolute():
            raise BuildError(f"--stock path must be absolute: {path}")
        supplied[resource] = path
    missing = sorted(set(TARGET_RESOURCES) - set(supplied))
    extra = sorted(set(supplied) - set(TARGET_RESOURCES))
    if missing or extra:
        raise BuildError(f"--stock must supply exactly seven PK resources; missing={missing}, extra={extra}")
    return supplied


def read_baselines(stock_paths: Mapping[str, Path]) -> dict[str, BaselineInput]:
    baselines: dict[str, BaselineInput] = {}
    for resource in TARGET_RESOURCES:
        path = assert_ordinary_existing(stock_paths[resource], f"baseline {resource}")
        if not path.is_file():
            raise BuildError(f"baseline {resource} is not a regular file")
        active = (GAME_ROOT / Path(resource)).resolve(strict=True)
        try:
            if path.samefile(active):
                raise BuildError(f"refusing to read the live game resource as baseline: {resource}")
        except FileNotFoundError:
            pass
        blob = path.read_bytes()
        baselines[resource] = BaselineInput(resource, path, blob, sha256_bytes(blob))
    return baselines


def validate_output_root(output_root: Path, baselines: Mapping[str, BaselineInput]) -> Path:
    if not output_root.is_absolute():
        raise BuildError("--output-root must be an absolute path")
    tmp_root = assert_ordinary_existing(REPO_ROOT / "tmp", "repository tmp")
    resolved = output_root.resolve(strict=False)
    if not resolved.is_relative_to(tmp_root):
        raise BuildError("--output-root must be a new directory below KR_PATCH_WORK/tmp")
    if resolved.exists():
        raise BuildError(f"--output-root must not already exist: {resolved}")
    for baseline in baselines.values():
        if resolved == baseline.path or resolved.is_relative_to(baseline.path.parent) and resolved.name == baseline.path.name:
            raise BuildError("--output-root overlaps a baseline path")
    parent = resolved.parent
    parent.mkdir(parents=True, exist_ok=True)
    assert_ordinary_existing(parent, "output parent")
    return resolved


def verify_baselines_unchanged(baselines: Mapping[str, BaselineInput]) -> None:
    for baseline in baselines.values():
        if sha256_file(baseline.path) != baseline.sha256:
            raise BuildError(f"baseline changed during offline build: {baseline.resource}")


def build_candidate(
    *,
    progress_path: Path,
    stock_paths: Mapping[str, Path],
    output_root: Path,
) -> dict[str, Any]:
    overlays = progress_resource_overlays(progress_path)
    baselines = read_baselines(stock_paths)
    final_output = validate_output_root(output_root, baselines)
    staging = Path(tempfile.mkdtemp(prefix=f".{final_output.name}.staging-", dir=final_output.parent))
    try:
        outputs: dict[str, bytes] = {}
        resource_results: dict[str, dict[str, Any]] = {}
        for resource in TARGET_RESOURCES:
            if resource == "MSG_PK/SC/msgui.bin":
                target, result = apply_msgui_resource(baselines[resource], overlays[resource])
            elif resource == "MSG_PK/SC/msggame.bin":
                target, result = apply_msggame_resource(baselines[resource], overlays[resource])
            else:
                target, result = apply_common_resource(resource, baselines[resource], overlays[resource])
            outputs[resource] = target
            resource_results[resource] = result
        verify_baselines_unchanged(baselines)
        for resource, target in outputs.items():
            atomic_write(staging / Path(resource), target)
            written = staging / Path(resource)
            if sha256_file(written) != sha256_bytes(target):
                raise BuildError(f"candidate output hash changed while writing: {resource}")
        manifest = {
            "schema": MANIFEST_SCHEMA,
            "scope": "PK-only MSG_PK/SC seven-resource offline candidate",
            "file_only": True,
            "process_memory_access": False,
            "registry_modified": False,
            "executable_modified": False,
            "installed_game_files_modified": False,
            "base_msg_sc_included": False,
            "manifest_contains_commercial_source_text": False,
            "private_candidate_contains_complete_game_resources": True,
            "public_distribution_eligible": False,
            "progress": {
                "path": assert_under(REPO_ROOT, progress_path, "translation progress").relative_to(REPO_ROOT).as_posix(),
                "sha256": sha256_file(progress_path),
            },
            "resources": [resource_results[resource] for resource in TARGET_RESOURCES],
            "checks": {
                "all_seven_msg_pk_sc_resources": True,
                "all_declared_source_hashes": True,
                "all_control_printf_esc_whitespace_invariants": True,
                "all_parse_rebuild_roundtrips": True,
                "all_baselines_unchanged": True,
                "live_game_resources_not_read_as_baselines": True,
                "output_root_is_explicit_tmp": True,
            },
        }
        atomic_write(staging / "full_pk_messages.build-manifest.json", json_bytes(manifest))
        verify_baselines_unchanged(baselines)
        os.replace(staging, final_output)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return {
        "output_root": final_output,
        "manifest_path": final_output / "full_pk_messages.build-manifest.json",
        "resources": resource_results,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="build the seven current PK message resources into a new tmp directory")
    build.add_argument("--progress", type=Path, default=DEFAULT_PROGRESS)
    build.add_argument("--stock", action="append", required=True, metavar="RESOURCE=ABSOLUTE_PATH")
    build.add_argument("--output-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command != "build":
            raise BuildError(f"unsupported command: {args.command}")
        result = build_candidate(
            progress_path=args.progress,
            stock_paths=parse_stock_args(args.stock),
            output_root=args.output_root,
        )
    except (OSError, KeyError, TypeError, BuildError, LZ4Error, MessageTableError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"output_root={result['output_root']}")
    for resource in TARGET_RESOURCES:
        details = result["resources"][resource]
        target = details["target"]
        changed = details.get("changed_entry_count", details.get("changed_coordinate_count"))
        print(f"{resource} sha256={target['sha256']} changed={changed}")
    print(f"manifest={result['manifest_path']}")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
