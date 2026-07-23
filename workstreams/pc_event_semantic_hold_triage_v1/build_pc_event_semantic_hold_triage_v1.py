#!/usr/bin/env python3
"""Build a source-free, PC-only ledger for live event semantic holds.

The source inventories predate later Steam applications, so a hold is carried
forward only when its old Korean UTF-16LE hash still matches the current Steam
cell.  The generated ledger intentionally contains IDs, hashes, structure
flags, and anchor classifications only: it never emits Japanese, Korean, or
PC-reference text.

This is a read-only audit of game resources.  ``--write`` is restricted to a
deterministic artifact directory under ``KR_PATCH_WORK/tmp``.
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
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TMP_ROOT = REPO / "tmp"
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "pc_event_semantic_hold_triage_v1"
VALIDATION_PATH = HERE / "validation.v1.json"

STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
BASE_PRISTINE_ROOT = Path(r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root")
PK_PRISTINE = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)

BASE_AUDIT_LEDGER = (
    REPO
    / "tmp"
    / "translation_quality_audit_v1"
    / "semantic"
    / "ev_strdata_pc_only_full_audit.v1.jsonl"
)
PK_AUDIT_LEDGER = (
    REPO
    / "tmp"
    / "translation_quality_pc_core_closure_v1"
    / "pc_coordinate_dispositions.source_free.v1.jsonl"
)

LEDGER_SCHEMA = "nobu16.kr.pc-event-semantic-hold-triage-row.v1"
SUMMARY_SCHEMA = "nobu16.kr.pc-event-semantic-hold-triage-summary.v1"
VALIDATION_SCHEMA = "nobu16.kr.pc-event-semantic-hold-triage-validation.v1"

RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)


class TriageError(ValueError):
    """Raised when a pinned source, provenance ledger, or output diverges."""


@dataclass(frozen=True)
class ResourceSpec:
    key: str
    relative_path: str
    expected_count: int
    languages: tuple[str, ...]
    paths: Mapping[str, Path]


BASE_SPEC = ResourceSpec(
    key="base_ev_strdata",
    relative_path="MSG/JP/ev_strdata.bin",
    expected_count=17_868,
    # Steam PC does not ship MSG/EN/ev_strdata.bin.  SC and TC are the full
    # reference context available for the Base event table.
    languages=("JP", "KO", "SC", "TC"),
    paths={
        "JP": BASE_PRISTINE_ROOT / "MSG" / "JP" / "ev_strdata.bin",
        "KO": STEAM_ROOT / "MSG" / "JP" / "ev_strdata.bin",
        "SC": STEAM_ROOT / "MSG" / "SC" / "ev_strdata.bin",
        "TC": STEAM_ROOT / "MSG" / "TC" / "ev_strdata.bin",
    },
)
PK_SPEC = ResourceSpec(
    key="pk_msgev",
    relative_path="MSG_PK/JP/msgev.bin",
    expected_count=17_916,
    languages=("JP", "KO", "EN", "SC", "TC"),
    paths={
        "JP": PK_PRISTINE,
        "KO": STEAM_ROOT / "MSG_PK" / "JP" / "msgev.bin",
        "EN": STEAM_ROOT / "MSG_PK" / "EN" / "msgev.bin",
        "SC": STEAM_ROOT / "MSG_PK" / "SC" / "msgev.bin",
        "TC": STEAM_ROOT / "MSG_PK" / "TC" / "msgev.bin",
    },
)
SPECS = (BASE_SPEC, PK_SPEC)
SPEC_BY_KEY = {spec.key: spec for spec in SPECS}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TriageError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("ascii")


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    lines = [json.dumps(row, ensure_ascii=True, separators=(",", ":"), sort_keys=True) for row in rows]
    return (("\n".join(lines) + "\n") if lines else "").encode("ascii")


def relative_to_repo(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError as exc:
        raise TriageError(f"path is outside repository: {path}") from exc


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"required JSON is absent: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TriageError(f"invalid JSON: {path}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    require(path.is_file(), f"required JSONL is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TriageError(f"invalid JSONL: {path}:{line_number}: {exc}") from exc
        require(isinstance(row, dict), f"JSONL row is not an object: {path}:{line_number}")
        rows.append(row)
    return rows


def load_validation() -> dict[str, Any]:
    validation = read_json(VALIDATION_PATH)
    require(validation.get("schema") == VALIDATION_SCHEMA, "validation schema differs")
    require(validation.get("source_free") is True, "validation must be source-free")
    return validation


def load_table(path: Path) -> tuple[str, ...]:
    require(path.is_file(), f"required PC source is absent: {path}")
    tools_root = REPO / "tools"
    if str(tools_root) not in sys.path:
        sys.path.insert(0, str(tools_root))
    from nobu16_lz4 import decompress_wrapper  # pylint: disable=import-outside-toplevel
    from nobu16_msg_table import parse_message_table  # pylint: disable=import-outside-toplevel

    _header, raw = decompress_wrapper(path.read_bytes())
    return tuple(parse_message_table(raw).texts)


def load_resources(validation: Mapping[str, Any]) -> tuple[dict[str, dict[str, tuple[str, ...]]], dict[str, dict[str, str]]]:
    expected_hashes = validation.get("input_file_sha256")
    require(isinstance(expected_hashes, dict), "validation input hashes are absent")
    tables: dict[str, dict[str, tuple[str, ...]]] = {}
    observed_hashes: dict[str, dict[str, str]] = {}
    for spec in SPECS:
        expected_for_spec = expected_hashes.get(spec.key)
        require(isinstance(expected_for_spec, dict), f"validation hashes are absent: {spec.key}")
        tables[spec.key] = {}
        observed_hashes[spec.key] = {}
        for language in spec.languages:
            path = spec.paths[language]
            observed = sha256_file(path)
            expected = expected_for_spec.get(language)
            require(isinstance(expected, str) and observed == expected, f"PC source hash differs: {spec.key}/{language}")
            texts = load_table(path)
            require(len(texts) == spec.expected_count, f"PC table count differs: {spec.key}/{language}")
            tables[spec.key][language] = texts
            observed_hashes[spec.key][language] = observed
    return tables, observed_hashes


def format_flags(texts: Sequence[str]) -> dict[str, bool]:
    merged = "\x00".join(texts)
    other_control = any(
        ord(character) < 32 and character not in "\r\n\t\x1b"
        for text in texts
        for character in text
    )
    return {
        "runtime_token_present": bool(RUNTIME_RE.search(merged)),
        "printf_token_present": bool(PRINTF_RE.search(merged)),
        "esc_tag_present": bool(ESC_RE.search(merged)),
        "linebreak_present": any("\r" in text or "\n" in text for text in texts),
        "outer_whitespace_present": any(text != text.strip(" \t\r\n") for text in texts),
        "other_control_present": other_control,
    }


def classify(flags: Mapping[str, bool]) -> str:
    if flags["runtime_token_present"] or flags["printf_token_present"] or flags["esc_tag_present"]:
        return "runtime_printf_esc_structural"
    if flags["linebreak_present"] or flags["outer_whitespace_present"] or flags["other_control_present"]:
        return "linebreak_or_whitespace_layout"
    return "pure_static_wording"


def context_hashes(spec: ResourceSpec, tables: Mapping[str, Mapping[str, tuple[str, ...]]], identifier: int) -> dict[str, str]:
    return {
        language: sha256_text(tables[spec.key][language][identifier])
        for language in spec.languages
        if language != "KO"
    }


def same_resource_signature(spec: ResourceSpec, tables: Mapping[str, Mapping[str, tuple[str, ...]]], identifier: int) -> tuple[str, ...]:
    return tuple(tables[spec.key][language][identifier] for language in spec.languages if language != "KO")


def cross_resource_signature(tables: Mapping[str, Mapping[str, tuple[str, ...]]], spec: ResourceSpec, identifier: int) -> tuple[str, str, str]:
    # Base has no EN sibling.  Cross-table reuse is permitted only over the
    # language contexts present in both PC event resources.
    return tuple(tables[spec.key][language][identifier] for language in ("JP", "SC", "TC"))  # type: ignore[return-value]


def load_live_holds(
    tables: Mapping[str, Mapping[str, tuple[str, ...]]], validation: Mapping[str, Any]
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    expected_ledger_hashes = validation.get("provenance_ledger_sha256")
    require(isinstance(expected_ledger_hashes, dict), "validation provenance hashes are absent")
    require(
        sha256_file(BASE_AUDIT_LEDGER) == expected_ledger_hashes.get("base"),
        "Base audit ledger hash differs",
    )
    require(
        sha256_file(PK_AUDIT_LEDGER) == expected_ledger_hashes.get("pk"),
        "PK audit ledger hash differs",
    )

    holds: dict[str, list[dict[str, Any]]] = {spec.key: [] for spec in SPECS}
    base_total = base_stale = 0
    base_source_counts: Counter[str] = Counter()
    base_live_counts: Counter[str] = Counter()
    for row in read_jsonl(BASE_AUDIT_LEDGER):
        disposition = row.get("disposition")
        if not isinstance(disposition, str) or not disposition.startswith("hold_"):
            continue
        identifier = row.get("id")
        expected_current_hash = row.get("current_ko_utf16le_sha256")
        require(isinstance(identifier, int), "Base hold lacks integer ID")
        require(isinstance(expected_current_hash, str), f"Base hold lacks current hash: {identifier}")
        require(0 <= identifier < BASE_SPEC.expected_count, f"Base hold ID outside table: {identifier}")
        base_total += 1
        base_source_counts[disposition] += 1
        current_hash = sha256_text(tables[BASE_SPEC.key]["KO"][identifier])
        if current_hash != expected_current_hash:
            base_stale += 1
            continue
        base_live_counts[disposition] += 1
        holds[BASE_SPEC.key].append(
            {
                "id": identifier,
                "source_hold_classification": disposition,
                "source_hold_reason_codes": [],
                "source_ledger_current_ko_utf16le_sha256": expected_current_hash,
            }
        )

    pk_total = pk_stale = 0
    pk_source_counts: Counter[str] = Counter()
    pk_live_counts: Counter[str] = Counter()
    for row in read_jsonl(PK_AUDIT_LEDGER):
        if row.get("resource") != "msgev" or row.get("disposition") != "pc_only_hold_requires_contextual_or_runtime_review":
            continue
        coordinate = row.get("coordinate")
        expected_current_hash = row.get("current_ko_utf16le_sha256")
        reasons = row.get("hold_or_screen_reason_codes")
        require(isinstance(coordinate, str) and coordinate.isdecimal(), "PK hold coordinate is invalid")
        require(isinstance(expected_current_hash, str), f"PK hold lacks current hash: {coordinate}")
        require(isinstance(reasons, list) and all(isinstance(reason, str) for reason in reasons), f"PK hold reasons are invalid: {coordinate}")
        identifier = int(coordinate)
        require(0 <= identifier < PK_SPEC.expected_count, f"PK hold ID outside table: {identifier}")
        pk_total += 1
        for reason in reasons:
            pk_source_counts[reason] += 1
        current_hash = sha256_text(tables[PK_SPEC.key]["KO"][identifier])
        if current_hash != expected_current_hash:
            pk_stale += 1
            continue
        for reason in reasons:
            pk_live_counts[reason] += 1
        holds[PK_SPEC.key].append(
            {
                "id": identifier,
                "source_hold_classification": "pc_only_hold_requires_contextual_or_runtime_review",
                "source_hold_reason_codes": sorted(reasons),
                "source_ledger_current_ko_utf16le_sha256": expected_current_hash,
            }
        )

    for spec in SPECS:
        holds[spec.key].sort(key=lambda row: int(row["id"]))
    reproduction = {
        "base": {
            "ledger_hold_count": base_total,
            "live_hold_count": len(holds[BASE_SPEC.key]),
            "stale_or_changed_count": base_stale,
            "ledger_source_classification_counts": dict(sorted(base_source_counts.items())),
            "live_source_classification_counts": dict(sorted(base_live_counts.items())),
        },
        "pk": {
            "ledger_hold_count": pk_total,
            "live_hold_count": len(holds[PK_SPEC.key]),
            "stale_or_changed_count": pk_stale,
            "ledger_reason_counts": dict(sorted(pk_source_counts.items())),
            "live_reason_counts": dict(sorted(pk_live_counts.items())),
        },
    }
    return holds, reproduction


def build_static_indexes(
    tables: Mapping[str, Mapping[str, tuple[str, ...]]]
) -> tuple[
    dict[str, dict[int, dict[str, bool]]],
    dict[str, dict[int, str]],
    dict[tuple[str, tuple[str, ...]], list[tuple[str, int]]],
    dict[tuple[str, str, str], list[tuple[str, int]]],
]:
    flags_by_resource: dict[str, dict[int, dict[str, bool]]] = {}
    class_by_resource: dict[str, dict[int, str]] = {}
    same_resource_index: dict[tuple[str, tuple[str, ...]], list[tuple[str, int]]] = defaultdict(list)
    cross_resource_index: dict[tuple[str, str, str], list[tuple[str, int]]] = defaultdict(list)
    for spec in SPECS:
        flags_by_resource[spec.key] = {}
        class_by_resource[spec.key] = {}
        for identifier in range(spec.expected_count):
            values = [tables[spec.key][language][identifier] for language in spec.languages]
            flags = format_flags(values)
            triage_class = classify(flags)
            flags_by_resource[spec.key][identifier] = flags
            class_by_resource[spec.key][identifier] = triage_class
            if triage_class != "pure_static_wording":
                continue
            same_resource_index[(spec.key, same_resource_signature(spec, tables, identifier))].append((spec.key, identifier))
            cross_resource_index[cross_resource_signature(tables, spec, identifier)].append((spec.key, identifier))
    return flags_by_resource, class_by_resource, same_resource_index, cross_resource_index


def anchor_record(
    group: Sequence[tuple[str, int]],
    self_coordinate: tuple[str, int],
    tables: Mapping[str, Mapping[str, tuple[str, ...]]],
) -> dict[str, Any]:
    anchors = sorted((resource, identifier) for resource, identifier in group if (resource, identifier) != self_coordinate)
    ko_hashes = sorted({sha256_text(tables[resource]["KO"][identifier]) for resource, identifier in group})
    if not anchors:
        verdict = "no_anchor"
    elif len(ko_hashes) == 1:
        verdict = "consensus"
    else:
        verdict = "conflict"
    return {
        "verdict": verdict,
        "anchor_count": len(anchors),
        "anchor_coordinates": [{"resource": resource, "id": identifier} for resource, identifier in anchors],
        "current_ko_utf16le_sha256_values": ko_hashes,
    }


def source_free_row_check(rows: Sequence[Mapping[str, Any]]) -> None:
    forbidden_keys = {
        "current_ko",
        "source_jp",
        "source_en",
        "source_sc",
        "source_tc",
        "translation",
        "proposed_korean",
    }
    payload = canonical_jsonl(rows)
    require(payload.isascii(), "source-free ledger serialization is not ASCII")
    for row in rows:
        require(not forbidden_keys.intersection(row.keys()), "source-free ledger includes text-bearing row fields")


def count_anchor_verdicts(rows: Sequence[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        if row["triage_class"] != "pure_static_wording":
            continue
        anchor = row["static_anchor"]
        require(isinstance(anchor, dict), "static anchor is invalid")
        verdict = anchor[key]["verdict"]
        require(isinstance(verdict, str), "static anchor verdict is invalid")
        counts[verdict] += 1
    return {verdict: counts[verdict] for verdict in ("consensus", "conflict", "no_anchor")}


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    validation = load_validation()
    tables, observed_hashes = load_resources(validation)
    holds, reproduction = load_live_holds(tables, validation)
    flags_by_resource, class_by_resource, same_resource_index, cross_resource_index = build_static_indexes(tables)

    rows: list[dict[str, Any]] = []
    class_counts_by_resource: dict[str, Counter[str]] = {spec.key: Counter() for spec in SPECS}
    feature_counts_by_resource: dict[str, Counter[str]] = {spec.key: Counter() for spec in SPECS}
    for spec in SPECS:
        for hold in holds[spec.key]:
            identifier = int(hold["id"])
            flags = flags_by_resource[spec.key][identifier]
            triage_class = class_by_resource[spec.key][identifier]
            class_counts_by_resource[spec.key][triage_class] += 1
            for flag, present in flags.items():
                if present:
                    feature_counts_by_resource[spec.key][flag] += 1
            if triage_class == "pure_static_wording":
                full_group = same_resource_index[(spec.key, same_resource_signature(spec, tables, identifier))]
                cross_group = cross_resource_index[cross_resource_signature(tables, spec, identifier)]
                static_anchor: dict[str, Any] = {
                    "eligible": True,
                    "same_resource_full_available_pc_context": anchor_record(full_group, (spec.key, identifier), tables),
                    "cross_resource_jp_sc_tc": anchor_record(cross_group, (spec.key, identifier), tables),
                }
            else:
                static_anchor = {
                    "eligible": False,
                    "same_resource_full_available_pc_context": {"verdict": "not_applicable", "anchor_count": 0, "anchor_coordinates": [], "current_ko_utf16le_sha256_values": []},
                    "cross_resource_jp_sc_tc": {"verdict": "not_applicable", "anchor_count": 0, "anchor_coordinates": [], "current_ko_utf16le_sha256_values": []},
                }
            rows.append(
                {
                    "schema": LEDGER_SCHEMA,
                    "resource": spec.relative_path,
                    "resource_key": spec.key,
                    "id": identifier,
                    "current_ko_utf16le_sha256": sha256_text(tables[spec.key]["KO"][identifier]),
                    "source_context_utf16le_sha256": context_hashes(spec, tables, identifier),
                    "format_flags": flags,
                    "triage_class": triage_class,
                    "source_hold": hold,
                    "static_anchor": static_anchor,
                    "source_text_emitted": False,
                }
            )

    rows.sort(key=lambda row: (row["resource_key"], int(row["id"])))
    source_free_row_check(rows)

    classification_counts = {
        "base": {name: class_counts_by_resource[BASE_SPEC.key][name] for name in ("runtime_printf_esc_structural", "linebreak_or_whitespace_layout", "pure_static_wording")},
        "pk": {name: class_counts_by_resource[PK_SPEC.key][name] for name in ("runtime_printf_esc_structural", "linebreak_or_whitespace_layout", "pure_static_wording")},
    }
    classification_counts["total"] = {
        name: classification_counts["base"][name] + classification_counts["pk"][name]
        for name in ("runtime_printf_esc_structural", "linebreak_or_whitespace_layout", "pure_static_wording")
    }
    feature_counts = {
        "base": {name: feature_counts_by_resource[BASE_SPEC.key][name] for name in sorted(feature_counts_by_resource[BASE_SPEC.key])},
        "pk": {name: feature_counts_by_resource[PK_SPEC.key][name] for name in sorted(feature_counts_by_resource[PK_SPEC.key])},
    }
    feature_counts["total"] = {
        name: feature_counts["base"].get(name, 0) + feature_counts["pk"].get(name, 0)
        for name in sorted(set(feature_counts["base"]) | set(feature_counts["pk"]))
    }
    summary = {
        "schema": SUMMARY_SCHEMA,
        "source_free": True,
        "source_text_emitted": False,
        "input_file_sha256": observed_hashes,
        "provenance_ledgers": {
            "base": {"path": relative_to_repo(BASE_AUDIT_LEDGER), "sha256": sha256_file(BASE_AUDIT_LEDGER)},
            "pk": {"path": relative_to_repo(PK_AUDIT_LEDGER), "sha256": sha256_file(PK_AUDIT_LEDGER)},
        },
        "live_hold_reproduction": reproduction,
        "classification_counts": classification_counts,
        "format_feature_counts_nonexclusive": feature_counts,
        "static_anchor_counts": {
            "same_resource_full_available_pc_context": count_anchor_verdicts(rows, "same_resource_full_available_pc_context"),
            "cross_resource_jp_sc_tc": count_anchor_verdicts(rows, "cross_resource_jp_sc_tc"),
        },
        "row_count": len(rows),
        "scope": {
            "base_reference_contexts": ["JP", "SC", "TC"],
            "pk_reference_contexts": ["JP", "EN", "SC", "TC"],
            "switch_korean_translation_used": False,
            "historic_korean_translation_used": False,
            "steam_game_resource_written": False,
            "semantic_completion": False,
        },
        "semantic_completion_reason": "Duplicate consensus proves current rendering consistency only; it does not prove translation quality or authorize an automatic wording edit.",
    }
    validate_contract(rows, summary, validation)
    return rows, summary


def validate_contract(rows: Sequence[Mapping[str, Any]], summary: Mapping[str, Any], validation: Mapping[str, Any]) -> None:
    expected = validation.get("expected")
    require(isinstance(expected, dict), "validation expected contract is absent")
    require(summary.get("row_count") == expected.get("row_count"), "live triage row count differs")
    require(summary.get("live_hold_reproduction") == expected.get("live_hold_reproduction"), "live hold reproduction differs")
    require(summary.get("classification_counts") == expected.get("classification_counts"), "triage classification counts differ")
    require(summary.get("static_anchor_counts") == expected.get("static_anchor_counts"), "static anchor counts differ")
    require(summary.get("format_feature_counts_nonexclusive") == expected.get("format_feature_counts_nonexclusive"), "format feature counts differ")
    require(sum(summary["classification_counts"]["total"].values()) == len(rows), "classification total differs from row count")
    require(summary.get("source_text_emitted") is False, "summary claims source text was emitted")
    scope = summary.get("scope")
    require(isinstance(scope, dict), "summary scope is absent")
    require(scope.get("switch_korean_translation_used") is False, "Switch Korean source policy differs")
    require(scope.get("historic_korean_translation_used") is False, "historic Korean source policy differs")
    require(scope.get("steam_game_resource_written") is False, "Steam write policy differs")
    require(scope.get("semantic_completion") is False, "triage must not claim semantic completion")
    source_free_row_check(rows)


def require_output_root(path: Path) -> Path:
    root = path.resolve(strict=False)
    tmp = TMP_ROOT.resolve(strict=True)
    require(root == tmp or tmp in root.parents, f"output must remain below tmp: {root}")
    return root


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def output_paths(output_root: Path) -> dict[str, Path]:
    root = require_output_root(output_root)
    return {
        "ledger": root / "pc_event_semantic_hold_triage.source_free.v1.jsonl",
        "summary": root / "summary.source_free.v1.json",
    }


def payloads(rows: Sequence[Mapping[str, Any]], summary: Mapping[str, Any]) -> dict[str, bytes]:
    result = {"ledger": canonical_jsonl(rows), "summary": canonical_json(summary)}
    for name, payload in result.items():
        require(payload.isascii(), f"{name} payload is not ASCII/source-free")
    return result


def validate_persisted(paths: Mapping[str, Path], expected_payloads: Mapping[str, bytes], validation: Mapping[str, Any]) -> None:
    for name, expected in expected_payloads.items():
        path = paths[name]
        require(path.is_file(), f"missing generated artifact: {path}")
        actual = path.read_bytes()
        require(actual == expected, f"generated artifact differs: {path}")
    expected_outputs = validation.get("expected_output_sha256")
    if expected_outputs is None:
        return
    require(isinstance(expected_outputs, dict), "validation output hashes are invalid")
    for name, payload in expected_payloads.items():
        expected_hash = expected_outputs.get(name)
        require(isinstance(expected_hash, str) and sha256_bytes(payload) == expected_hash, f"deterministic output hash differs: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--write", action="store_true", help="write deterministic source-free artifacts under tmp")
    parser.add_argument("--validate", action="store_true", help="validate the deterministic artifacts under tmp")
    args = parser.parse_args()
    if not args.write and not args.validate:
        parser.error("choose --write and/or --validate")
    validation = load_validation()
    rows, summary = build()
    built_payloads = payloads(rows, summary)
    paths = output_paths(args.output_root)
    if args.write:
        for name, payload in built_payloads.items():
            atomic_write(paths[name], payload)
    if args.validate:
        validate_persisted(paths, built_payloads, validation)
    print(
        json.dumps(
            {
                "row_count": summary["row_count"],
                "classification_counts": summary["classification_counts"],
                "static_anchor_counts": summary["static_anchor_counts"],
                "source_text_emitted": False,
                "steam_game_resource_written": False,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
