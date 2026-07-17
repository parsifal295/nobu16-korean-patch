#!/usr/bin/env python3
"""Build a source-free, PC-only coverage manifest for all 159,341 text coordinates.

The manifest consumes only the completed PC-only full-audit/closure ledgers:

* five full audits: ev_strdata, msgbre, msgire, msgstf, msgui;
* core msggame closure: base_msggame and pk_msggame;
* PC core closure: strdata, msgdata, and msgev.

Each input's provenance flags are checked before its rows are accepted.  The
``ev_strdata`` full audit deliberately excluded 106 active-builder coordinates;
their numeric coordinate complement is derived from that audit's own PC
inventory count and summary.  No generic overlay, Switch text, historic Korean
text, game resource, or Steam write is read or performed by this builder.

The output is a coordinate-accounting artifact, not a semantic completion
claim.  Every merged row and the summary therefore state that semantic
completion is false.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp"
AUDIT_SEMANTIC = TMP / "translation_quality_audit_v1" / "semantic"
CORE_MSGGAME_ROOT = TMP / "translation_quality_core_msggame_closure_v1"
PC_CORE_ROOT = TMP / "translation_quality_pc_core_closure_v1"
DEFAULT_OUTPUT = TMP / "translation_quality_pc_coverage_manifest_v1"

LEDGER_NAME = "merged_pc_only_coordinate_dispositions.v1.jsonl"
SUMMARY_NAME = "summary.source_free.json"
HEX64_RE = re.compile(r"^[0-9A-F]{64}$")
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9_.:-]+$")


class CoverageError(ValueError):
    """An input ledger, provenance guarantee, or coordinate contract changed."""


@dataclass(frozen=True)
class FullAuditSpec:
    input_id: str
    resource: str
    filename: str
    schema: str
    expected_coordinate_count: int
    pc_context_key: str


RESOURCE_ORDER = (
    "ev_strdata",
    "base_msggame",
    "strdata",
    "msgbre",
    "msgdata",
    "msgev",
    "pk_msggame",
    "msgire",
    "msgstf",
    "msgui",
)
RESOURCE_EXPECTED_COUNTS = {
    "ev_strdata": 17868,
    "base_msggame": 24262,
    "strdata": 32311,
    "msgbre": 3000,
    "msgdata": 29218,
    "msgev": 17916,
    "pk_msggame": 29524,
    "msgire": 122,
    "msgstf": 20,
    "msgui": 5100,
}
PC_CORE_RELATIVE_PATHS = {
    "strdata": "MSG/JP/strdata.bin",
    "msgdata": "MSG_PK/JP/msgdata.bin",
    "msgev": "MSG_PK/JP/msgev.bin",
}
EXPECTED_TOTAL = sum(RESOURCE_EXPECTED_COUNTS.values())
RESOURCE_ORDER_INDEX = {resource: index for index, resource in enumerate(RESOURCE_ORDER)}

FULL_AUDITS = (
    FullAuditSpec(
        "ev_strdata_pc_only_full_audit",
        "ev_strdata",
        "ev_strdata_pc_only_full_audit.v1.jsonl",
        "nobu16.kr.ev-strdata-pc-only-full-audit.v1",
        RESOURCE_EXPECTED_COUNTS["ev_strdata"],
        "pc_sc_tc_references",
    ),
    FullAuditSpec(
        "msgbre_pc_only_full_audit",
        "msgbre",
        "msgbre_pc_only_full_audit.v1.jsonl",
        "nobu16.kr.msgbre-pc-only-full-audit.v1",
        RESOURCE_EXPECTED_COUNTS["msgbre"],
        "pc_en_sc_tc_references",
    ),
    FullAuditSpec(
        "msgire_pc_only_full_audit",
        "msgire",
        "msgire_pc_only_full_audit.v1.jsonl",
        "nobu16.kr.msgire-pc-only-full-audit.v1",
        RESOURCE_EXPECTED_COUNTS["msgire"],
        "pc_en_sc_tc_references",
    ),
    FullAuditSpec(
        "msgstf_pc_only_full_audit",
        "msgstf",
        "msgstf_pc_only_full_audit.v1.jsonl",
        "nobu16.kr.msgstf-pc-only-full-audit.v1",
        RESOURCE_EXPECTED_COUNTS["msgstf"],
        "pc_en_sc_tc_references",
    ),
    FullAuditSpec(
        "msgui_pc_only_full_audit",
        "msgui",
        "msgui_pc_only_full_audit.v1.jsonl",
        "nobu16.kr.msgui-pc-only-full-audit.v1",
        RESOURCE_EXPECTED_COUNTS["msgui"],
        "pc_en_sc_tc_context_only",
    ),
)

EV_SUMMARY = AUDIT_SEMANTIC / "ev_strdata_pc_only_full_audit_summary.v1.json"
CORE_MSGGAME_LEDGER = CORE_MSGGAME_ROOT / "private_core_msggame_pc_only_closure.v1.jsonl"
CORE_MSGGAME_SUMMARY = CORE_MSGGAME_ROOT / "summary.source_free.v1.json"
PC_CORE_LEDGER = PC_CORE_ROOT / "pc_coordinate_dispositions.source_free.v1.jsonl"
PC_CORE_SUMMARY = PC_CORE_ROOT / "summary.source_free.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def relative_to_repo(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")
    except ValueError as exc:
        raise CoverageError(f"input is outside repository: {path}") from exc


def require_file(path: Path) -> None:
    if not path.is_file():
        raise CoverageError(f"required input is absent: {path}")


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CoverageError(f"{label} must be an object")
    return value


def require_bool(mapping: Mapping[str, Any], key: str, expected: bool, label: str) -> None:
    if mapping.get(key) is not expected:
        raise CoverageError(f"{label}.{key} must be {expected!r}")


def require_identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise CoverageError(f"{label} is not a safe identifier")
    return value


def require_hex64(value: Any, label: str) -> str:
    if not isinstance(value, str) or not HEX64_RE.fullmatch(value.upper()):
        raise CoverageError(f"{label} is not a SHA-256 value")
    return value.upper()


def optional_hex64(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return require_hex64(value, label)


def optional_hash_mapping(value: Any, label: str) -> dict[str, str] | None:
    if value is None:
        return None
    mapping = require_mapping(value, label)
    result: dict[str, str] = {}
    for key, item in mapping.items():
        if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9_]+", key):
            raise CoverageError(f"{label} has an invalid key")
        result[key] = require_hex64(item, f"{label}.{key}")
    return dict(sorted(result.items()))


def optional_identifier_list(value: Any, label: str) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise CoverageError(f"{label} must be a list")
    return [require_identifier(item, f"{label} item") for item in value]


def coordinate_key(value: str) -> tuple[int, ...]:
    if not isinstance(value, str) or not value:
        raise CoverageError("coordinate must be a nonempty string")
    try:
        result = tuple(int(part) for part in value.split(":"))
    except ValueError as exc:
        raise CoverageError(f"invalid coordinate: {value!r}") from exc
    if not result or any(part < 0 for part in result):
        raise CoverageError(f"invalid coordinate: {value!r}")
    return result


def serialized_line(row: Mapping[str, Any]) -> bytes:
    return (json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def digest_rows(rows: Iterable[Mapping[str, Any]]) -> tuple[int, str]:
    digest = hashlib.sha256()
    count = 0
    for row in rows:
        digest.update(serialized_line(row))
        count += 1
    return count, digest.hexdigest().upper()


def atomic_write_rows(path: Path, rows: Iterable[Mapping[str, Any]]) -> tuple[int, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    digest = hashlib.sha256()
    count = 0
    try:
        with os.fdopen(descriptor, "wb") as stream:
            for row in rows:
                payload = serialized_line(row)
                stream.write(payload)
                digest.update(payload)
                count += 1
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return count, digest.hexdigest().upper()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def read_json(path: Path) -> Mapping[str, Any]:
    require_file(path)
    try:
        return require_mapping(json.loads(path.read_text(encoding="utf-8")), str(path))
    except json.JSONDecodeError as exc:
        raise CoverageError(f"invalid JSON: {path}") from exc


def read_jsonl(path: Path) -> Iterator[tuple[int, Mapping[str, Any]]]:
    require_file(path)
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise CoverageError(f"invalid JSONL at {path}:{line_number}") from exc
            yield line_number, require_mapping(value, f"{path}:{line_number}")


def require_full_audit_scope(scope_value: Any, spec: FullAuditSpec, label: str) -> dict[str, bool]:
    scope = require_mapping(scope_value, f"{label}.audit_scope")
    required = {
        "current_pc_korean": True,
        "pristine_pc_japanese": True,
        spec.pc_context_key: True,
        "historic_korean_read": False,
        "switch_korean_read": False,
        "steam_game_resource_written": False,
    }
    for key, expected in required.items():
        require_bool(scope, key, expected, f"{label}.audit_scope")
    return required


def require_core_scope(scope_value: Any, label: str) -> dict[str, bool]:
    scope = require_mapping(scope_value, f"{label}.audit_scope")
    required = {
        "current_pc_korean": True,
        "pristine_pc_japanese": True,
        "pc_en_sc_tc_context_only": True,
        "frozen_overlay_read_for_status_only": True,
        "historic_korean_read": False,
        "switch_korean_read": False,
        "steam_game_resource_written": False,
    }
    for key, expected in required.items():
        require_bool(scope, key, expected, f"{label}.audit_scope")
    return required


def source_free_evidence_from_full(row: Mapping[str, Any], label: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for source_key, output_key in (
        ("source_jp_utf16le_sha256", "source_jp_utf16le_sha256"),
        ("current_ko_utf16le_sha256", "current_ko_utf16le_sha256"),
        ("source_file_sha256", "source_file_sha256"),
        ("current_file_sha256", "current_file_sha256"),
    ):
        value = optional_hex64(row.get(source_key), f"{label}.{source_key}")
        if value is not None:
            result[output_key] = value
    references = optional_hash_mapping(row.get("reference_file_sha256"), f"{label}.reference_file_sha256")
    if references is not None:
        result["reference_file_sha256"] = references
    return result


def source_free_evidence_from_core(row: Mapping[str, Any], label: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for source_key, output_key in (
        ("source_jp_utf16le_sha256", "source_jp_utf16le_sha256"),
        ("current_ko_utf16le_sha256", "current_ko_utf16le_sha256"),
        ("pristine_jp_file_sha256", "pristine_jp_file_sha256"),
        ("current_pc_ko_file_sha256", "current_pc_ko_file_sha256"),
    ):
        value = optional_hex64(row.get(source_key), f"{label}.{source_key}")
        if value is not None:
            result[output_key] = value
    references = optional_hash_mapping(row.get("pc_reference_file_sha256"), f"{label}.pc_reference_file_sha256")
    if references is not None:
        result["pc_reference_file_sha256"] = references
    return result


def source_free_evidence_from_pc_core(row: Mapping[str, Any], label: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "source_jp_utf16le_sha256": require_hex64(row.get("jp_utf16le_sha256"), f"{label}.jp_utf16le_sha256"),
        "current_ko_utf16le_sha256": require_hex64(row.get("current_ko_utf16le_sha256"), f"{label}.current_ko_utf16le_sha256"),
    }
    contexts = optional_hash_mapping(row.get("context_utf16le_sha256"), f"{label}.context_utf16le_sha256")
    if contexts is not None:
        result["context_utf16le_sha256"] = contexts
    return result


def full_audit_record(spec: FullAuditSpec, row: Mapping[str, Any], coordinate: str, label: str) -> dict[str, Any]:
    disposition = require_identifier(row.get("disposition"), f"{label}.disposition")
    return {
        "schema": "nobu16.kr.pc-only-coverage-merged-disposition.v1",
        "resource": spec.resource,
        "coordinate": coordinate,
        "coverage_input": spec.input_id,
        "coverage_origin": "full_pc_only_audit",
        "input_schema": spec.schema,
        "input_disposition": disposition,
        "semantic_completion": False,
        "source_free_evidence": source_free_evidence_from_full(row, label),
    }


def load_full_audit(spec: FullAuditSpec) -> tuple[list[dict[str, Any]], set[int], dict[str, Any]]:
    path = AUDIT_SEMANTIC / spec.filename
    records: list[dict[str, Any]] = []
    identifiers: set[int] = set()
    canonical_scope: dict[str, bool] | None = None
    disposition_counts: Counter[str] = Counter()
    for line_number, row in read_jsonl(path):
        label = f"{path}:{line_number}"
        if row.get("schema") != spec.schema:
            raise CoverageError(f"unexpected schema at {label}")
        if row.get("resource") != spec.resource:
            raise CoverageError(f"unexpected resource at {label}")
        identifier = row.get("id")
        if not isinstance(identifier, int) or isinstance(identifier, bool):
            raise CoverageError(f"{label}.id must be an integer")
        if identifier < 0 or identifier >= spec.expected_coordinate_count:
            raise CoverageError(f"{label}.id is outside the PC coordinate universe")
        if identifier in identifiers:
            raise CoverageError(f"duplicate full-audit coordinate: {spec.resource}:{identifier}")
        scope = require_full_audit_scope(row.get("audit_scope"), spec, label)
        if canonical_scope is None:
            canonical_scope = scope
        elif scope != canonical_scope:
            raise CoverageError(f"full-audit provenance changed within {spec.resource}")
        coordinate = str(identifier)
        record = full_audit_record(spec, row, coordinate, label)
        records.append(record)
        identifiers.add(identifier)
        disposition_counts[record["input_disposition"]] += 1
    if not records:
        raise CoverageError(f"full-audit ledger is empty: {path}")
    if spec.resource != "ev_strdata" and identifiers != set(range(spec.expected_coordinate_count)):
        missing = sorted(set(range(spec.expected_coordinate_count)).difference(identifiers))
        raise CoverageError(f"full-audit coordinate coverage differs for {spec.resource}: missing {missing[:5]!r}")
    provenance = {
        "input_id": spec.input_id,
        "input_kind": "source_paired_pc_only_full_audit",
        "ledger": relative_to_repo(path),
        "ledger_sha256": sha256_file(path),
        "observed_coordinate_count": len(records),
        "expected_coordinate_count": spec.expected_coordinate_count,
        "audit_scope_checks": canonical_scope,
        "switch_korean_read": False,
        "historic_korean_read": False,
        "steam_game_resource_written": False,
        "disposition_counts": dict(sorted(disposition_counts.items())),
    }
    return records, identifiers, provenance


def ev_excluded_coordinate_complement(audit_ids: set[int], audit_provenance: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    summary = read_json(EV_SUMMARY)
    if summary.get("schema") != "nobu16.kr.ev-strdata-pc-only-full-audit-summary.v1":
        raise CoverageError("ev full-audit summary schema differs")
    require_bool(summary, "switch_korean_translation_used", False, "ev full-audit summary")
    require_bool(summary, "historic_korean_translation_used", False, "ev full-audit summary")
    require_bool(summary, "game_files_written", False, "ev full-audit summary")
    expected = RESOURCE_EXPECTED_COUNTS["ev_strdata"]
    if summary.get("inventory_coordinate_count") != expected:
        raise CoverageError("ev full-audit summary inventory count differs")
    if summary.get("audited_coordinate_count") != len(audit_ids):
        raise CoverageError("ev full-audit summary audited count differs")
    excluded_count = summary.get("excluded_active_generic_builder_coordinate_count")
    if not isinstance(excluded_count, int) or isinstance(excluded_count, bool):
        raise CoverageError("ev full-audit excluded count is invalid")
    missing = set(range(expected)).difference(audit_ids)
    if len(missing) != excluded_count:
        raise CoverageError("ev full-audit numeric coordinate complement differs from excluded count")
    if audit_ids.union(missing) != set(range(expected)) or audit_ids.intersection(missing):
        raise CoverageError("ev full-audit complement is not a disjoint complete PC coordinate partition")
    records = [
        {
            "schema": "nobu16.kr.pc-only-coverage-merged-disposition.v1",
            "resource": "ev_strdata",
            "coordinate": str(identifier),
            "coverage_input": "ev_strdata_full_audit_excluded_coordinate_complement",
            "coverage_origin": "ev_full_audit_coordinate_complement",
            "input_schema": "nobu16.kr.ev-strdata-pc-only-full-audit-summary.v1",
            "input_disposition": "excluded_active_generic_builder_coordinate_not_rejudged_by_manifest",
            "semantic_completion": False,
            "source_free_evidence": {
                "coordinate_universe": "pristine_pc_ev_strdata_0_through_17867",
                "full_audit_excluded_coordinate_count": excluded_count,
            },
        }
        for identifier in sorted(missing)
    ]
    provenance = {
        "input_id": "ev_strdata_full_audit_excluded_coordinate_complement",
        "input_kind": "numeric_pc_coordinate_complement_from_pc_only_full_audit",
        "summary": relative_to_repo(EV_SUMMARY),
        "summary_sha256": sha256_file(EV_SUMMARY),
        "observed_coordinate_count": len(records),
        "expected_coordinate_count": excluded_count,
        "source_audit_input_id": audit_provenance["input_id"],
        "switch_korean_read": False,
        "historic_korean_read": False,
        "steam_game_resource_written": False,
        "generic_overlay_read": False,
        "generic_overlay_korean_text_read": False,
        "semantic_text_rejudged": False,
    }
    return records, provenance


def core_msggame_record(row: Mapping[str, Any], label: str) -> dict[str, Any]:
    resource = require_identifier(row.get("resource"), f"{label}.resource")
    coordinate = require_identifier(row.get("coordinate"), f"{label}.coordinate")
    coordinate_key(coordinate)
    disposition = require_identifier(row.get("disposition"), f"{label}.disposition")
    semantic_status = require_identifier(row.get("semantic_status"), f"{label}.semantic_status")
    coverage = require_mapping(row.get("pc_reference_coverage"), f"{label}.pc_reference_coverage")
    available = optional_identifier_list(coverage.get("available_languages"), f"{label}.pc_reference_coverage.available_languages") or []
    expected = optional_identifier_list(coverage.get("expected_languages"), f"{label}.pc_reference_coverage.expected_languages") or []
    missing = optional_identifier_list(coverage.get("missing_languages"), f"{label}.pc_reference_coverage.missing_languages") or []
    return {
        "schema": "nobu16.kr.pc-only-coverage-merged-disposition.v1",
        "resource": resource,
        "coordinate": coordinate,
        "coverage_input": "core_msggame_pc_only_closure",
        "coverage_origin": "core_msggame_pc_only_closure",
        "input_schema": "nobu16.kr.core-msggame-pc-only-closure.v1",
        "input_disposition": disposition,
        "input_semantic_status": semantic_status,
        "pc_reference_coverage": {
            "available_languages": available,
            "expected_languages": expected,
            "missing_languages": missing,
        },
        "semantic_completion": False,
        "source_free_evidence": source_free_evidence_from_core(row, label),
    }


def load_core_msggame() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    summary = read_json(CORE_MSGGAME_SUMMARY)
    if summary.get("schema") != "nobu16.kr.core-msggame-pc-only-closure-summary.v1":
        raise CoverageError("core msggame summary schema differs")
    require_bool(summary, "automatic_semantic_completion_claim", False, "core msggame summary")
    require_bool(summary, "historic_korean_translation_used", False, "core msggame summary")
    require_bool(summary, "switch_korean_translation_used", False, "core msggame summary")
    require_bool(summary, "steam_installation_written", False, "core msggame summary")
    if summary.get("coordinate_count") != RESOURCE_EXPECTED_COUNTS["base_msggame"] + RESOURCE_EXPECTED_COUNTS["pk_msggame"]:
        raise CoverageError("core msggame summary coordinate count differs")
    summary_resources = require_mapping(summary.get("resources"), "core msggame summary.resources")
    for resource in ("base_msggame", "pk_msggame"):
        resource_summary = require_mapping(summary_resources.get(resource), f"core msggame summary.resources.{resource}")
        if resource_summary.get("coordinate_count") != RESOURCE_EXPECTED_COUNTS[resource]:
            raise CoverageError(f"core msggame summary resource count differs: {resource}")

    records: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    resource_counts: Counter[str] = Counter()
    canonical_scope: dict[str, bool] | None = None
    disposition_counts: Counter[str] = Counter()
    for line_number, row in read_jsonl(CORE_MSGGAME_LEDGER):
        label = f"{CORE_MSGGAME_LEDGER}:{line_number}"
        if row.get("schema") != "nobu16.kr.core-msggame-pc-only-closure.v1":
            raise CoverageError(f"unexpected core msggame schema at {label}")
        scope = require_core_scope(row.get("audit_scope"), label)
        if canonical_scope is None:
            canonical_scope = scope
        elif scope != canonical_scope:
            raise CoverageError("core msggame provenance changed within one closure ledger")
        record = core_msggame_record(row, label)
        if record["resource"] not in {"base_msggame", "pk_msggame"}:
            raise CoverageError(f"unexpected core msggame resource at {label}")
        key = (record["resource"], record["coordinate"])
        if key in seen:
            raise CoverageError(f"duplicate core msggame coordinate: {key[0]}:{key[1]}")
        seen.add(key)
        resource_counts[record["resource"]] += 1
        disposition_counts[record["input_disposition"]] += 1
        records.append(record)
    for resource in ("base_msggame", "pk_msggame"):
        if resource_counts[resource] != RESOURCE_EXPECTED_COUNTS[resource]:
            raise CoverageError(f"core msggame ledger count differs: {resource}")
    if len(records) != summary["coordinate_count"]:
        raise CoverageError("core msggame ledger count differs from summary")
    frozen = require_mapping(summary.get("frozen_overlay"), "core msggame summary.frozen_overlay")
    require_bool(frozen, "switch_korean_translation_used", False, "core msggame summary.frozen_overlay")
    if frozen.get("read_for_status_only_not_semantic_source") is not True:
        raise CoverageError("core msggame frozen overlay policy changed")
    provenance = {
        "input_id": "core_msggame_pc_only_closure",
        "input_kind": "source_paired_pc_only_closure",
        "ledger": relative_to_repo(CORE_MSGGAME_LEDGER),
        "ledger_sha256": sha256_file(CORE_MSGGAME_LEDGER),
        "summary": relative_to_repo(CORE_MSGGAME_SUMMARY),
        "summary_sha256": sha256_file(CORE_MSGGAME_SUMMARY),
        "observed_coordinate_count": len(records),
        "expected_coordinate_count": summary["coordinate_count"],
        "audit_scope_checks": canonical_scope,
        "switch_korean_read": False,
        "historic_korean_read": False,
        "steam_game_resource_written": False,
        "automatic_semantic_completion_claim": False,
        "disposition_counts": dict(sorted(disposition_counts.items())),
    }
    return records, provenance


def pc_core_record(row: Mapping[str, Any], label: str) -> dict[str, Any]:
    resource = require_identifier(row.get("resource"), f"{label}.resource")
    coordinate = require_identifier(row.get("coordinate"), f"{label}.coordinate")
    coordinate_key(coordinate)
    disposition = require_identifier(row.get("disposition"), f"{label}.disposition")
    confidence = require_identifier(row.get("evidence_confidence"), f"{label}.evidence_confidence")
    require_bool(row, "switch_korean_translation_used", False, label)
    require_bool(row, "new_high_confidence_candidate", False, label)
    flags = optional_identifier_list(row.get("flags"), f"{label}.flags") or []
    reasons = optional_identifier_list(row.get("hold_or_screen_reason_codes"), f"{label}.hold_or_screen_reason_codes") or []
    existing_overlay_coordinate = row.get("existing_quality_overlay_coordinate")
    if not isinstance(existing_overlay_coordinate, bool):
        raise CoverageError(f"{label}.existing_quality_overlay_coordinate must be bool")
    relative_path = row.get("relative_path")
    if relative_path != PC_CORE_RELATIVE_PATHS.get(resource):
        raise CoverageError(f"{label}.relative_path differs from the expected PC resource path")
    return {
        "schema": "nobu16.kr.pc-only-coverage-merged-disposition.v1",
        "resource": resource,
        "coordinate": coordinate,
        "coverage_input": "pc_core_coordinate_closure",
        "coverage_origin": "pc_core_coordinate_closure",
        "input_schema": "nobu16.kr.pc-core-coordinate-disposition.v1",
        "input_disposition": disposition,
        "input_evidence_confidence": confidence,
        "input_flags": flags,
        "input_hold_or_screen_reason_codes": reasons,
        "existing_quality_overlay_coordinate": existing_overlay_coordinate,
        "relative_path": relative_path,
        "semantic_completion": False,
        "source_free_evidence": source_free_evidence_from_pc_core(row, label),
    }


def load_pc_core() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    summary = read_json(PC_CORE_SUMMARY)
    if summary.get("schema") != "nobu16.kr.translation-quality-pc-core-closure.v1":
        raise CoverageError("PC core summary schema differs")
    if not isinstance(summary.get("translation_completion_claim"), str) or not summary["translation_completion_claim"].startswith("not_made:"):
        raise CoverageError("PC core summary must not claim semantic completion")
    require_bool(summary, "switch_korean_translation_used", False, "PC core summary")
    require_bool(summary, "non_pc_korean_translation_sources_read", False, "PC core summary")
    require_bool(summary, "steam_installation_written", False, "PC core summary")
    require_bool(summary, "source_or_public_overlay_written", False, "PC core summary")
    if summary.get("coordinate_count") != sum(RESOURCE_EXPECTED_COUNTS[resource] for resource in ("strdata", "msgdata", "msgev")):
        raise CoverageError("PC core summary coordinate count differs")
    summary_resources = require_mapping(summary.get("resources"), "PC core summary.resources")
    for resource in ("strdata", "msgdata", "msgev"):
        resource_summary = require_mapping(summary_resources.get(resource), f"PC core summary.resources.{resource}")
        if resource_summary.get("coordinate_count") != RESOURCE_EXPECTED_COUNTS[resource]:
            raise CoverageError(f"PC core summary resource count differs: {resource}")
        source_metadata = require_mapping(resource_summary.get("pristine_pc_japanese"), f"PC core summary.{resource}.pristine_pc_japanese")
        if source_metadata.get("unchanged_parse_rebuild") != "OK":
            raise CoverageError(f"PC core source parse/rebuild status differs: {resource}")

    records: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    resource_counts: Counter[str] = Counter()
    disposition_counts: Counter[str] = Counter()
    for line_number, row in read_jsonl(PC_CORE_LEDGER):
        label = f"{PC_CORE_LEDGER}:{line_number}"
        if row.get("schema") != "nobu16.kr.pc-core-coordinate-disposition.v1":
            raise CoverageError(f"unexpected PC core schema at {label}")
        record = pc_core_record(row, label)
        if record["resource"] not in {"strdata", "msgdata", "msgev"}:
            raise CoverageError(f"unexpected PC core resource at {label}")
        key = (record["resource"], record["coordinate"])
        if key in seen:
            raise CoverageError(f"duplicate PC core coordinate: {key[0]}:{key[1]}")
        seen.add(key)
        resource_counts[record["resource"]] += 1
        disposition_counts[record["input_disposition"]] += 1
        records.append(record)
    for resource in ("strdata", "msgdata", "msgev"):
        if resource_counts[resource] != RESOURCE_EXPECTED_COUNTS[resource]:
            raise CoverageError(f"PC core ledger count differs: {resource}")
    if len(records) != summary["coordinate_count"]:
        raise CoverageError("PC core ledger count differs from summary")
    provenance = {
        "input_id": "pc_core_coordinate_closure",
        "input_kind": "source_free_pc_only_coordinate_closure",
        "ledger": relative_to_repo(PC_CORE_LEDGER),
        "ledger_sha256": sha256_file(PC_CORE_LEDGER),
        "summary": relative_to_repo(PC_CORE_SUMMARY),
        "summary_sha256": sha256_file(PC_CORE_SUMMARY),
        "observed_coordinate_count": len(records),
        "expected_coordinate_count": summary["coordinate_count"],
        "switch_korean_read": False,
        "historic_korean_read": False,
        "historic_korean_read_basis": "non_pc_korean_translation_sources_read=false",
        "steam_game_resource_written": False,
        "automatic_semantic_completion_claim": False,
        "disposition_counts": dict(sorted(disposition_counts.items())),
    }
    return records, provenance


def validate_and_sort_records(records: list[dict[str, Any]]) -> dict[str, int]:
    seen: set[tuple[str, str]] = set()
    resource_counts: Counter[str] = Counter()
    for row in records:
        resource = row.get("resource")
        coordinate = row.get("coordinate")
        if resource not in RESOURCE_EXPECTED_COUNTS:
            raise CoverageError(f"merged record has unexpected resource: {resource!r}")
        if not isinstance(coordinate, str):
            raise CoverageError("merged record coordinate is invalid")
        coordinate_key(coordinate)
        key = (resource, coordinate)
        if key in seen:
            raise CoverageError(f"merged duplicate resource+coordinate: {resource}:{coordinate}")
        seen.add(key)
        resource_counts[resource] += 1
        if row.get("semantic_completion") is not False:
            raise CoverageError(f"merged row incorrectly claims semantic completion: {resource}:{coordinate}")
    if dict(resource_counts) != RESOURCE_EXPECTED_COUNTS:
        details = {resource: resource_counts[resource] for resource in RESOURCE_ORDER}
        raise CoverageError(f"merged resource counts differ: {details!r}")
    if len(records) != EXPECTED_TOTAL or len(seen) != EXPECTED_TOTAL:
        raise CoverageError("merged total does not equal the 159,341-coordinate PC universe")
    records.sort(
        key=lambda row: (
            RESOURCE_ORDER_INDEX[row["resource"]],
            coordinate_key(row["coordinate"]),
            row["coverage_origin"],
        )
    )
    return {resource: resource_counts[resource] for resource in RESOURCE_ORDER}


def ensure_private_output(output: Path) -> Path:
    resolved = output.resolve()
    tmp = TMP.resolve()
    if resolved == tmp or tmp not in resolved.parents:
        raise CoverageError(f"output must stay below {tmp}")
    return resolved


def build(output: Path) -> tuple[list[dict[str, Any]], dict[str, Any], str]:
    output = ensure_private_output(output)
    all_records: list[dict[str, Any]] = []
    input_validations: list[dict[str, Any]] = []

    ev_audit_ids: set[int] | None = None
    ev_audit_provenance: dict[str, Any] | None = None
    for spec in FULL_AUDITS:
        records, identifiers, provenance = load_full_audit(spec)
        all_records.extend(records)
        input_validations.append(provenance)
        if spec.resource == "ev_strdata":
            ev_audit_ids = identifiers
            ev_audit_provenance = provenance
    if ev_audit_ids is None or ev_audit_provenance is None:
        raise CoverageError("ev full-audit input is missing")
    ev_complement, ev_complement_provenance = ev_excluded_coordinate_complement(ev_audit_ids, ev_audit_provenance)
    all_records.extend(ev_complement)
    input_validations.append(ev_complement_provenance)

    core_records, core_provenance = load_core_msggame()
    all_records.extend(core_records)
    input_validations.append(core_provenance)

    pc_core_records, pc_core_provenance = load_pc_core()
    all_records.extend(pc_core_records)
    input_validations.append(pc_core_provenance)

    resource_counts = validate_and_sort_records(all_records)
    ledger_count, ledger_sha256 = digest_rows(all_records)
    if ledger_count != EXPECTED_TOTAL:
        raise CoverageError("merged ledger digest count differs")
    origin_counts: Counter[str] = Counter(row["coverage_origin"] for row in all_records)
    disposition_counts: Counter[str] = Counter(row["input_disposition"] for row in all_records)
    summary = {
        "schema": "nobu16.kr.pc-only-coverage-manifest.v1",
        "scope": "all ten PC text resources merged from PC-only audits and closures; source-free coordinate accounting only",
        "resource_count": len(RESOURCE_ORDER),
        "expected_coordinate_count": EXPECTED_TOTAL,
        "merged_coordinate_count": ledger_count,
        "resource_coordinate_counts": resource_counts,
        "coverage_origin_counts": dict(sorted(origin_counts.items())),
        "input_disposition_counts": dict(sorted(disposition_counts.items())),
        "input_validations": input_validations,
        "all_input_pc_only_provenance_checks_passed": True,
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "steam_installation_written": False,
        "generic_overlay_read": False,
        "generic_overlay_korean_text_read": False,
        "semantic_completion": False,
        "semantic_completion_reason": "Coverage and static/closure dispositions do not prove semantic translation quality in gameplay context.",
        "merged_source_free_ledger": str((output / LEDGER_NAME).relative_to(REPO)).replace("\\", "/"),
        "merged_source_free_ledger_sha256": ledger_sha256,
        "merged_ledger_contains_commercial_source_text": False,
        "game_resource_candidate_generated": False,
        "source_or_public_overlay_written": False,
        "deterministic_serialization": "UTF-8 JSONL, sorted resource/coordinate order, sorted JSON keys",
    }
    summary_text = json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return all_records, summary, summary_text


def count_lines(path: Path) -> int:
    with path.open("rb") as stream:
        return sum(1 for _ in stream)


def write_artifacts(output: Path, records: list[dict[str, Any]], summary_text: str) -> None:
    ledger = output / LEDGER_NAME
    summary = output / SUMMARY_NAME
    expected_count, expected_sha256 = digest_rows(records)
    actual_count, actual_sha256 = atomic_write_rows(ledger, records)
    if (actual_count, actual_sha256) != (expected_count, expected_sha256):
        raise CoverageError("written merged ledger differs from deterministic payload")
    atomic_write_text(summary, summary_text)


def validate_artifacts(output: Path, records: list[dict[str, Any]], summary_text: str) -> None:
    ledger = output / LEDGER_NAME
    summary = output / SUMMARY_NAME
    require_file(ledger)
    require_file(summary)
    expected_count, expected_sha256 = digest_rows(records)
    if count_lines(ledger) != expected_count:
        raise CoverageError("existing merged ledger line count differs from deterministic build")
    if sha256_file(ledger) != expected_sha256:
        raise CoverageError("existing merged ledger hash differs from deterministic build")
    if summary.read_text(encoding="utf-8") != summary_text:
        raise CoverageError("existing merged summary differs from deterministic build")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write", action="store_true", help="write source-free artifacts beneath tmp")
    action.add_argument("--validate", action="store_true", help="verify existing artifacts against a deterministic rebuild")
    args = parser.parse_args()
    try:
        output = ensure_private_output(args.output)
        records, summary, summary_text = build(output)
        if args.write:
            write_artifacts(output, records, summary_text)
        if args.validate:
            validate_artifacts(output, records, summary_text)
        print(
            json.dumps(
                {
                    "merged_coordinate_count": summary["merged_coordinate_count"],
                    "resource_coordinate_counts": summary["resource_coordinate_counts"],
                    "semantic_completion": summary["semantic_completion"],
                    "steam_installation_written": summary["steam_installation_written"],
                    "switch_korean_translation_used": summary["switch_korean_translation_used"],
                    "historic_korean_translation_used": summary["historic_korean_translation_used"],
                    "generic_overlay_read": summary["generic_overlay_read"],
                    "artifacts_written": args.write,
                    "artifacts_validated": args.validate,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    except (CoverageError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
