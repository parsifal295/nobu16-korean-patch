#!/usr/bin/env python3
"""Build a current, source-free ledger for the two PC ``msggame`` resources.

This is deliberately a *read-only* reconciliation artifact.  It enumerates
every current Steam literal coordinate in Base and PK ``msggame``, ties that
coordinate to the exact current Steam packed-file profile, and reconciles it
with the pre-existing PC-only coverage ledger.  It does not open a Switch
resource, historic Korean translation, generic-overlay Korean text, or any
Steam-writing route.

The output contains coordinates, hashes, dispositions, and provenance only;
it does not copy game text.  It is not a claim that static coverage proves
semantic translation completion or real-game layout completion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
BASE_PRISTINE = Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin")
PK_PRISTINE_RELATIVE = Path(
    "KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin"
)
DEFAULT_OUTPUT_ROOT = TMP / WORKSTREAM.name

COVERAGE_SUMMARY = TMP / "translation_quality_pc_coverage_manifest_v1" / "summary.source_free.json"
COVERAGE_LEDGER = TMP / "translation_quality_pc_coverage_manifest_v1" / "merged_pc_only_coordinate_dispositions.v1.jsonl"

WAVE5_BUILDER = REPO / "workstreams" / "pc_dialogue_quality_wave5_v1" / "build_pc_dialogue_quality_wave5_v1.py"
WAVE6_BUILDER = REPO / "workstreams" / "pc_dialogue_quality_wave6_v1" / "build_pc_dialogue_quality_wave6_v1.py"
WAVE7_WORKSTREAM = REPO / "workstreams" / "pc_dialogue_goodwill_runtime_wave7_v1"
WAVE7_BUILDER = WAVE7_WORKSTREAM / "build_pc_dialogue_goodwill_runtime_wave7_v1.py"
WAVE7_AUDIT = WAVE7_WORKSTREAM / "audit_pc_current_static_repairs_wave7.v1.json"

WAVE5_RUNTIME_HOLD = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave5_v1"
    / "audit"
    / "audit_base_suffix_batch03_dynamic_particle.jsonl"
)
WAVE5_PK_RUNTIME_HOLDS = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave5_v1"
    / "audit_pk_donor_runtime_particle_holds.jsonl"
)
WAVE5_PK_RECLASSIFICATION = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave5_v1"
    / "audit_pk_colon_manual_96_runtime_particle_reclassification.json"
)
WAVE5_RESIDUAL_HOLDS = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave5_v1"
    / "audit"
    / "audit_residual_korean_quality_scan_hold_v1.jsonl"
)

MSGGAME_ROOT = REPO / "workstreams" / "msggame"
sys.path.insert(0, str(MSGGAME_ROOT))

from msggame_format import MsgGameRecord, iter_literals, parse_packed_msggame  # noqa: E402


SCHEMA = "nobu16.kr.current-pc-dialogue-coordinate-ledger.v1"
SUMMARY_SCHEMA = "nobu16.kr.current-pc-dialogue-coordinate-ledger-summary.v1"
COVERAGE_SCHEMA = "nobu16.kr.pc-only-coverage-merged-disposition.v1"


class LedgerError(ValueError):
    """A pinned input or ledger contract has changed."""


@dataclass(frozen=True)
class ResourceSpec:
    name: str
    relative: Path
    pristine_kind: str
    expected_current_sha256: str
    expected_pristine_sha256: str
    context_relatives: Mapping[str, Path]
    expected_context_sha256: Mapping[str, str]
    profile_builder: Path
    profile_name: str


SPECS: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        name="base_msggame",
        relative=Path("MSG/JP/msggame.bin"),
        pristine_kind="workspace_pc_jp",
        expected_current_sha256="83C4DF9326DB1487707FDABE9CF2A00380144D14D3AC4A4FCD02513C8E3C279E",
        expected_pristine_sha256="EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        context_relatives={
            "SC": Path("MSG/SC/msggame.bin"),
            "TC": Path("MSG/TC/msggame.bin"),
        },
        expected_context_sha256={
            "SC": "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7",
            "TC": "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95",
        },
        profile_builder=WAVE7_BUILDER,
        profile_name="pc_dialogue_goodwill_runtime_wave7_v1",
    ),
    ResourceSpec(
        name="pk_msggame",
        relative=Path("MSG_PK/JP/msggame.bin"),
        pristine_kind="steam_transaction_pc_jp",
        expected_current_sha256="31950B8213AC80C9BCB866163EE7B4B655440ADF863DED21186273E3F8A34BDB",
        expected_pristine_sha256="31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
        context_relatives={
            "EN": Path("MSG_PK/EN/msggame.bin"),
            "SC": Path("MSG_PK/SC/msggame.bin"),
            "TC": Path("MSG_PK/TC/msggame.bin"),
        },
        expected_context_sha256={
            "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
            "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
            "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
        },
        profile_builder=WAVE7_BUILDER,
        profile_name="pc_dialogue_goodwill_runtime_wave7_v1",
    ),
)

# The old PC-only coverage ledger had 24,262 Base and 29,524 PK literals.
# The current Wave-5/Wave-6 profiles intentionally have fewer literal slots
# after earlier static rewrites coalesced JP suffix fragments into Korean
# literals.  Do not conceal that topology change by pretending the current
# files have the old coordinate sets.
EXPECTED_PRIOR_COUNTS = {"base_msggame": 24_262, "pk_msggame": 29_524}
EXPECTED_CURRENT_COUNTS = {"base_msggame": 24_241, "pk_msggame": 29_502}
EXPECTED_RETIRED_PRIOR_COORDINATES = {
    "base_msggame": {
        "13:9:1",
        "13:17:1",
        "13:24:1",
        "13:27:1",
        "13:27:2",
        "13:28:1",
        "13:30:1",
        "13:40:1",
        "13:55:1",
        "13:108:1",
        "13:110:1",
        "13:116:1",
        "13:122:1",
        "13:127:1",
        "13:128:1",
        "13:136:1",
        "13:142:1",
        "16:4:1",
        "16:15:1",
        "16:32:1",
        "16:38:1",
    },
    "pk_msggame": {
        "13:9:1",
        "13:17:1",
        "13:24:1",
        "13:27:1",
        "13:27:2",
        "13:28:1",
        "13:30:1",
        "13:40:1",
        "13:55:1",
        "13:108:1",
        "13:110:1",
        "13:116:1",
        "13:122:1",
        "13:127:1",
        "13:128:1",
        "13:136:1",
        "13:142:1",
        "16:4:1",
        "16:15:1",
        "16:32:1",
        "16:38:1",
        "16:45:1",
    },
}


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


def coordinate_key(value: str) -> tuple[int, int, int]:
    parts = value.split(":")
    if len(parts) != 3 or any(not part.isdecimal() for part in parts):
        raise LedgerError(f"invalid literal coordinate: {value!r}")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def record_key(value: str) -> tuple[int, int]:
    parts = value.split(":")
    if len(parts) != 2 or any(not part.isdecimal() for part in parts):
        raise LedgerError(f"invalid record coordinate: {value!r}")
    return int(parts[0]), int(parts[1])


def relative_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise LedgerError(f"{label} is missing: {path}")
    return path


def require_output_root(path: Path) -> Path:
    root = TMP.resolve(strict=True)
    resolved = path.resolve(strict=False)
    if resolved == root or root not in resolved.parents:
        raise LedgerError(f"output root must be below repository tmp: {resolved}")
    return resolved


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        for row in rows
    )


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def parse_msggame(path: Path) -> tuple[dict[str, str], dict[str, str], dict[str, tuple[str, ...]]]:
    """Return literal hashes, record hashes, and record literal-coordinate lists."""
    archive = parse_packed_msggame(path.read_bytes()).archive
    literal_hashes: dict[str, str] = {}
    record_hashes: dict[str, str] = {}
    record_literals: dict[str, tuple[str, ...]] = {}
    grouped: dict[str, list[str]] = defaultdict(list)
    for record in (record for block in archive.blocks for record in block.records):
        key = f"{record.block_id}:{record.record_id}"
        record_hashes[key] = sha256_bytes(record.data)
    for literal in iter_literals(archive):
        key = f"{literal.block_id}:{literal.record_id}:{literal.literal_id}"
        if key in literal_hashes:
            raise LedgerError(f"duplicate parsed literal coordinate: {key}")
        literal_hashes[key] = sha256_text(literal.text)
        grouped[f"{literal.block_id}:{literal.record_id}"].append(key)
    for key, coordinates in grouped.items():
        record_literals[key] = tuple(sorted(coordinates, key=coordinate_key))
    return literal_hashes, record_hashes, record_literals


def pristine_path(spec: ResourceSpec, steam_root: Path) -> Path:
    if spec.pristine_kind == "workspace_pc_jp":
        return BASE_PRISTINE
    if spec.pristine_kind == "steam_transaction_pc_jp":
        return steam_root / PK_PRISTINE_RELATIVE
    raise LedgerError(f"unknown pristine kind: {spec.pristine_kind}")


def load_coverage_rows() -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, Any]]:
    """Load only source-free rows for the two msggame resources."""
    require_file(COVERAGE_SUMMARY, "coverage summary")
    require_file(COVERAGE_LEDGER, "coverage ledger")
    try:
        summary = json.loads(COVERAGE_SUMMARY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LedgerError(f"coverage summary is invalid JSON: {exc}") from exc
    if not isinstance(summary, dict):
        raise LedgerError("coverage summary is not an object")
    if summary.get("schema") != "nobu16.kr.pc-only-coverage-manifest.v1":
        raise LedgerError("coverage summary schema differs")
    for key in (
        "all_input_pc_only_provenance_checks_passed",
        "switch_korean_translation_used",
        "historic_korean_translation_used",
        "steam_installation_written",
        "semantic_completion",
    ):
        expected = key == "all_input_pc_only_provenance_checks_passed"
        if summary.get(key) is not expected:
            raise LedgerError(f"coverage summary {key} is no longer {expected}")
    resources = summary.get("resource_coordinate_counts")
    if not isinstance(resources, dict):
        raise LedgerError("coverage summary resource counts are absent")
    for name, expected in EXPECTED_PRIOR_COUNTS.items():
        if resources.get(name) != expected:
            raise LedgerError(f"coverage summary count differs for {name}")

    accepted = set(EXPECTED_PRIOR_COUNTS)
    rows: dict[str, dict[str, dict[str, Any]]] = {name: {} for name in accepted}
    with COVERAGE_LEDGER.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise LedgerError(f"coverage ledger invalid JSON at line {line_number}: {exc}") from exc
            if not isinstance(row, dict) or row.get("resource") not in accepted:
                continue
            resource = row["resource"]
            if row.get("schema") != COVERAGE_SCHEMA or row.get("semantic_completion") is not False:
                raise LedgerError(f"coverage row schema/semantic state differs at {resource}:{line_number}")
            coordinate = row.get("coordinate")
            evidence = row.get("source_free_evidence")
            if not isinstance(coordinate, str) or not isinstance(evidence, dict):
                raise LedgerError(f"coverage row lacks a coordinate/evidence at {resource}:{line_number}")
            coordinate_key(coordinate)
            if not isinstance(evidence.get("current_ko_utf16le_sha256"), str):
                raise LedgerError(f"coverage row lacks prior current-text hash at {resource}:{coordinate}")
            if coordinate in rows[resource]:
                raise LedgerError(f"duplicate coverage coordinate: {resource}:{coordinate}")
            rows[resource][coordinate] = row
    for resource, expected in EXPECTED_PRIOR_COUNTS.items():
        if len(rows[resource]) != expected:
            raise LedgerError(f"coverage ledger count differs for {resource}: {len(rows[resource])} != {expected}")
    return rows, summary


def builder_evidence(spec: ResourceSpec) -> dict[str, str]:
    """Tie the exact live profile to its public PC-only build artifact."""
    builder = require_file(spec.profile_builder, f"{spec.profile_name} builder")
    source = builder.read_text(encoding="utf-8")
    if spec.expected_current_sha256 not in source:
        raise LedgerError(f"{spec.profile_name} does not pin current {spec.name} target hash")
    return {
        "build_artifact": relative_path(builder),
        "build_artifact_sha256": sha256_file(builder),
        "current_profile_name": spec.profile_name,
        "current_profile_packed_sha256": spec.expected_current_sha256,
    }


def add_record_hold(
    holds: dict[str, dict[str, list[dict[str, str]]]],
    *,
    resource: str,
    record: str,
    current_record_hash: str,
    observed_record_hashes: Mapping[str, Mapping[str, str]],
    literal_coordinates: Mapping[str, Mapping[str, tuple[str, ...]]],
    source: Path,
    status: str,
    category: str,
) -> bool:
    """Attach a current record-validated hold to every literal in that record."""
    record_key(record)
    if observed_record_hashes[resource].get(record) != current_record_hash:
        return False
    coordinates = literal_coordinates[resource].get(record, ())
    if not coordinates:
        return False
    evidence = {
        "category": category,
        "current_record_sha256": current_record_hash,
        "record": record,
        "source": relative_path(source),
        "status": status,
    }
    for coordinate in coordinates:
        if evidence not in holds[resource][coordinate]:
            holds[resource][coordinate].append(evidence)
    return True


def load_wave7_repair_evidence(
    holds: dict[str, dict[str, list[dict[str, str]]]],
    observed_record_hashes: Mapping[str, Mapping[str, str]],
    literal_coordinates: Mapping[str, Mapping[str, tuple[str, ...]]],
) -> tuple[dict[str, dict[str, list[dict[str, Any]]]], dict[str, int]]:
    """Validate the applied Wave-7 audit and project its record evidence.

    The audit is record-oriented because it also removes opaque Japanese
    inflection commands.  Each literal receives the record evidence, with a
    separate flag identifying whether that literal payload itself changed.
    Seven records deliberately remain runtime visual-QA holds.
    """
    require_file(WAVE7_AUDIT, "Wave 7 current static-repair audit")
    try:
        audit = json.loads(WAVE7_AUDIT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LedgerError(f"Wave 7 audit is invalid JSON: {exc}") from exc
    if not isinstance(audit, dict) or audit.get("schema") != "nobu16.kr.pc-dialogue-current-static-repairs-wave7.audit.v1":
        raise LedgerError("Wave 7 audit schema differs")
    scope = audit.get("scope")
    if not isinstance(scope, dict) or scope.get("excluded_sources") != ["Switch Korean"]:
        raise LedgerError("Wave 7 audit no longer asserts its Switch exclusion")
    inputs = audit.get("input_profile_sha256")
    outputs = audit.get("output_profile_sha256")
    rows = audit.get("records")
    if not isinstance(inputs, dict) or not isinstance(outputs, dict) or not isinstance(rows, list):
        raise LedgerError("Wave 7 audit profile/records are absent")
    expected_input = {
        "MSG/JP/msggame.bin": "32247AB97112243E58F8EB5B2930EE8A8AB9DF6A2FE0907A49AE28A255720610",
        "MSG_PK/JP/msggame.bin": "CE56A3C6577929513FFEEDFB71637316AA41822DC6F7B26749A6276D572CDF0A",
    }
    path_to_resource = {spec.relative.as_posix(): spec.name for spec in SPECS}
    for relative, expected in expected_input.items():
        if inputs.get(relative) != expected:
            raise LedgerError(f"Wave 7 input profile differs for {relative}")
        resource = path_to_resource[relative]
        if outputs.get(relative) != next(spec.expected_current_sha256 for spec in SPECS if spec.name == resource):
            raise LedgerError(f"Wave 7 output profile differs for {relative}")

    repairs: dict[str, dict[str, list[dict[str, Any]]]] = {
        name: defaultdict(list) for name in EXPECTED_CURRENT_COUNTS
    }
    seen_records: set[tuple[str, str]] = set()
    changed_literal_count = 0
    runtime_record_count = 0
    for row in rows:
        if not isinstance(row, dict):
            raise LedgerError("Wave 7 audit contains a non-object row")
        relative = require_text(row, "resource", WAVE7_AUDIT)
        resource = path_to_resource.get(relative)
        if resource is None:
            raise LedgerError(f"Wave 7 audit has an unsupported resource: {relative}")
        record = require_text(row, "coordinate", WAVE7_AUDIT)
        record_key(record)
        key = (resource, record)
        if key in seen_records:
            raise LedgerError(f"duplicate Wave 7 audit record: {resource}:{record}")
        seen_records.add(key)
        output_hash = require_text(row, "output_record_sha256", WAVE7_AUDIT)
        if observed_record_hashes[resource].get(record) != output_hash:
            raise LedgerError(f"current Steam does not match applied Wave 7 record: {resource}:{record}")
        current_literals = row.get("current_literals")
        output_literals = row.get("output_literals")
        if not isinstance(current_literals, list) or not isinstance(output_literals, list):
            raise LedgerError(f"Wave 7 literal lists are absent at {resource}:{record}")
        if not all(isinstance(value, str) for value in current_literals + output_literals):
            raise LedgerError(f"Wave 7 literal list is invalid at {resource}:{record}")
        coordinates = literal_coordinates[resource].get(record, ())
        if len(current_literals) != len(output_literals) or len(output_literals) != len(coordinates):
            raise LedgerError(f"Wave 7 literal topology differs at {resource}:{record}")
        changed_ids = [index for index, pair in enumerate(zip(current_literals, output_literals)) if pair[0] != pair[1]]
        if not changed_ids:
            raise LedgerError(f"Wave 7 audit row has no literal change: {resource}:{record}")
        kind = require_text(row, "kind", WAVE7_AUDIT)
        runtime_visual_qa_required = row.get("runtime_visual_qa_required")
        if not isinstance(runtime_visual_qa_required, bool):
            raise LedgerError(f"Wave 7 runtime QA flag is invalid at {resource}:{record}")
        evidence = {
            "changed_literal_ids": changed_ids,
            "kind": kind,
            "output_record_sha256": output_hash,
            "record": record,
            "runtime_visual_qa_required": runtime_visual_qa_required,
            "source": relative_path(WAVE7_AUDIT),
        }
        for coordinate in coordinates:
            literal_id = coordinate_key(coordinate)[2]
            literal_evidence = {**evidence, "literal_changed": literal_id in changed_ids}
            repairs[resource][coordinate].append(literal_evidence)
            if literal_id in changed_ids:
                changed_literal_count += 1
        if runtime_visual_qa_required:
            runtime_record_count += 1
            if not add_record_hold(
                holds,
                resource=resource,
                record=record,
                current_record_hash=output_hash,
                observed_record_hashes=observed_record_hashes,
                literal_coordinates=literal_coordinates,
                source=WAVE7_AUDIT,
                status="runtime_visual_qa_required",
                category="wave7_runtime_visual_qa",
            ):
                raise LedgerError(f"Wave 7 runtime QA hold did not attach: {resource}:{record}")
    if len(seen_records) != 12:
        raise LedgerError(f"Wave 7 audit record count differs: {len(seen_records)}")
    if runtime_record_count != 7:
        raise LedgerError(f"Wave 7 runtime visual-QA record count differs: {runtime_record_count}")
    return repairs, {
        "changed_literal_count": changed_literal_count,
        "matched_record_count": len(seen_records),
        "runtime_visual_qa_record_count": runtime_record_count,
    }


def load_current_hold_evidence(
    observed_record_hashes: Mapping[str, Mapping[str, str]],
    literal_coordinates: Mapping[str, Mapping[str, tuple[str, ...]]],
) -> tuple[dict[str, dict[str, list[dict[str, str]]]], dict[str, dict[str, list[dict[str, Any]]]], dict[str, Any]]:
    """Load only explicit PC-only current hold records whose record hash still matches."""
    holds: dict[str, dict[str, list[dict[str, str]]]] = {
        name: defaultdict(list) for name in EXPECTED_CURRENT_COUNTS
    }
    source_stats: dict[str, dict[str, int]] = {}

    def source_stat(source: Path, matched: int, stale: int) -> None:
        source_stats[relative_path(source)] = {"matched_record_count": matched, "stale_or_resolved_record_count": stale}

    # Base candidate explicitly withheld for runtime particle QA.
    require_file(WAVE5_RUNTIME_HOLD, "base runtime hold")
    matched = stale = 0
    for row in read_jsonl(WAVE5_RUNTIME_HOLD):
        if row.get("status") != "candidate_requires_runtime_qa":
            continue
        record = require_text(row, "coordinate", WAVE5_RUNTIME_HOLD)
        current_hash = require_text(row, "current_record_sha256", WAVE5_RUNTIME_HOLD)
        if add_record_hold(
            holds,
            resource="base_msggame",
            record=record,
            current_record_hash=current_hash,
            observed_record_hashes=observed_record_hashes,
            literal_coordinates=literal_coordinates,
            source=WAVE5_RUNTIME_HOLD,
            status="candidate_requires_runtime_qa",
            category="runtime_particle_and_suffix",
        ):
            matched += 1
        else:
            stale += 1
    source_stat(WAVE5_RUNTIME_HOLD, matched, stale)

    # PK records explicitly excluded from static application because a runtime
    # particle is fixed beside a dynamic value.
    require_file(WAVE5_PK_RUNTIME_HOLDS, "PK runtime hold ledger")
    matched = stale = 0
    for row in read_jsonl(WAVE5_PK_RUNTIME_HOLDS):
        if row.get("eligible_for_steam_application") is not False:
            continue
        record = require_text(row, "coordinate", WAVE5_PK_RUNTIME_HOLDS)
        current_hash = require_text(row, "current_record_sha256", WAVE5_PK_RUNTIME_HOLDS)
        if add_record_hold(
            holds,
            resource="pk_msggame",
            record=record,
            current_record_hash=current_hash,
            observed_record_hashes=observed_record_hashes,
            literal_coordinates=literal_coordinates,
            source=WAVE5_PK_RUNTIME_HOLDS,
            status="hold_runtime_particle",
            category="runtime_particle_allomorph",
        ):
            matched += 1
        else:
            stale += 1
    source_stat(WAVE5_PK_RUNTIME_HOLDS, matched, stale)

    # The reclassification document has both retired static candidates and
    # unresolved runtime entries.  Only retained records with a matching live
    # record hash are carried forward.
    require_file(WAVE5_PK_RECLASSIFICATION, "PK runtime reclassification")
    try:
        payload = json.loads(WAVE5_PK_RECLASSIFICATION.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LedgerError(f"PK runtime reclassification is invalid JSON: {exc}") from exc
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        raise LedgerError("PK runtime reclassification records are absent")
    matched = stale = 0
    for row in records:
        if not isinstance(row, dict):
            raise LedgerError("PK runtime reclassification contains a non-object record")
        status = row.get("final_application_status")
        if not isinstance(status, str) or not status.startswith("hold_"):
            continue
        record = require_text(row, "coordinate", WAVE5_PK_RECLASSIFICATION)
        current_hash = require_text(row, "current_record_sha256", WAVE5_PK_RECLASSIFICATION)
        if add_record_hold(
            holds,
            resource="pk_msggame",
            record=record,
            current_record_hash=current_hash,
            observed_record_hashes=observed_record_hashes,
            literal_coordinates=literal_coordinates,
            source=WAVE5_PK_RECLASSIFICATION,
            status=status,
            category="runtime_particle_or_opaque_grammar",
        ):
            matched += 1
        else:
            stale += 1
    source_stat(WAVE5_PK_RECLASSIFICATION, matched, stale)

    # The residual ledger names a small number of coordinate-bound terminology
    # and glyph holds.  It does not need game text to keep those rows visible.
    require_file(WAVE5_RESIDUAL_HOLDS, "residual hold ledger")
    matched = stale = 0
    for row in read_jsonl(WAVE5_RESIDUAL_HOLDS):
        coordinates = row.get("coordinates")
        status = row.get("status")
        kind = row.get("kind")
        if status != "hold" or not isinstance(kind, str) or not isinstance(coordinates, dict):
            continue
        for short_name, records_for_resource in coordinates.items():
            resource = {"Base": "base_msggame", "PK": "pk_msggame"}.get(short_name)
            if resource is None or not isinstance(records_for_resource, list):
                raise LedgerError("residual hold resource/coordinates are invalid")
            for record in records_for_resource:
                if not isinstance(record, str):
                    raise LedgerError("residual hold coordinate is invalid")
                record_key(record)
                literal_set = literal_coordinates[resource].get(record, ())
                if not literal_set:
                    stale += 1
                    continue
                evidence = {
                    "category": kind,
                    "current_record_sha256": observed_record_hashes[resource][record],
                    "record": record,
                    "source": relative_path(WAVE5_RESIDUAL_HOLDS),
                    "status": "hold_project_term_or_glyph_policy",
                }
                for coordinate in literal_set:
                    if evidence not in holds[resource][coordinate]:
                        holds[resource][coordinate].append(evidence)
                matched += 1
    source_stat(WAVE5_RESIDUAL_HOLDS, matched, stale)

    wave7_repairs, wave7_stats = load_wave7_repair_evidence(holds, observed_record_hashes, literal_coordinates)
    source_stats[relative_path(WAVE7_AUDIT)] = {
        "matched_record_count": wave7_stats["matched_record_count"],
        "runtime_visual_qa_record_count": wave7_stats["runtime_visual_qa_record_count"],
        "stale_or_resolved_record_count": 0,
    }
    return holds, wave7_repairs, {
        "source_record_validation": source_stats,
        "wave7_repair_validation": wave7_stats,
    }


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise LedgerError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise LedgerError(f"non-object JSONL row at {path}:{line_number}")
            yield row


def require_text(row: Mapping[str, Any], key: str, source: Path) -> str:
    value = row.get(key)
    if not isinstance(value, str):
        raise LedgerError(f"{source} row lacks string {key}")
    return value


def is_prior_review(disposition: object) -> bool:
    return isinstance(disposition, str) and (disposition.startswith("review_") or disposition.startswith("hold_"))


def build(steam_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    steam_root = steam_root.resolve(strict=True)
    coverage_rows, coverage_summary = load_coverage_rows()

    live_literals: dict[str, dict[str, str]] = {}
    pristine_literals: dict[str, dict[str, str]] = {}
    record_hashes: dict[str, dict[str, str]] = {}
    record_literals: dict[str, dict[str, tuple[str, ...]]] = {}
    resources_summary: dict[str, Any] = {}
    builder_metadata: dict[str, dict[str, str]] = {}

    for spec in SPECS:
        live = require_file(steam_root / spec.relative, f"current Steam {spec.name}")
        pristine = require_file(pristine_path(spec, steam_root), f"pristine PC Japanese {spec.name}")
        live_sha = sha256_file(live)
        pristine_sha = sha256_file(pristine)
        if live_sha != spec.expected_current_sha256:
            raise LedgerError(f"current Steam {spec.name} hash drift: {live_sha}")
        if pristine_sha != spec.expected_pristine_sha256:
            raise LedgerError(f"pristine PC Japanese {spec.name} hash drift: {pristine_sha}")

        current, records, literals_by_record = parse_msggame(live)
        original, _ignored_records, _ignored_literals = parse_msggame(pristine)
        if not set(current).issubset(original):
            unknown = sorted(set(current).difference(original), key=coordinate_key)
            raise LedgerError(f"current {spec.name} has literals absent from pristine PC JP: {unknown[:5]!r}")
        if len(current) != EXPECTED_CURRENT_COUNTS[spec.name]:
            raise LedgerError(f"literal count differs for {spec.name}: {len(current)}")
        retired = set(coverage_rows[spec.name]).difference(current)
        expected_retired = EXPECTED_RETIRED_PRIOR_COORDINATES[spec.name]
        if retired != expected_retired:
            raise LedgerError(
                f"current/coverage retired-coordinate set differs for {spec.name}: "
                f"expected={sorted(expected_retired, key=coordinate_key)!r}, "
                f"actual={sorted(retired, key=coordinate_key)!r}"
            )

        context_hashes: dict[str, str] = {}
        for language, relative in spec.context_relatives.items():
            context = require_file(steam_root / relative, f"PC {language} context {spec.name}")
            actual = sha256_file(context)
            expected = spec.expected_context_sha256[language]
            if actual != expected:
                raise LedgerError(f"PC {language} context hash drift for {spec.name}: {actual}")
            context_hashes[language] = actual

        live_literals[spec.name] = current
        pristine_literals[spec.name] = original
        record_hashes[spec.name] = records
        record_literals[spec.name] = literals_by_record
        builder_metadata[spec.name] = builder_evidence(spec)
        resources_summary[spec.name] = {
            "current_literal_coordinate_count": len(current),
            "prior_coverage_coordinate_count": len(coverage_rows[spec.name]),
            "retired_prior_literal_coordinate_count": len(retired),
            "current_steam_relative_path": spec.relative.as_posix(),
            "current_steam_packed_sha256": live_sha,
            "pc_context_packed_sha256": context_hashes,
            "pristine_pc_jp_packed_sha256": pristine_sha,
            "pristine_pc_jp_source_kind": spec.pristine_kind,
            **builder_metadata[spec.name],
        }

    holds, wave7_repairs, hold_metadata = load_current_hold_evidence(record_hashes, record_literals)
    rows: list[dict[str, Any]] = []
    retired_rows: list[dict[str, Any]] = []
    current_classification_counts: Counter[str] = Counter()
    prior_disposition_counts: Counter[str] = Counter()
    semantic_gap_counts: Counter[str] = Counter()
    current_hold_literal_count = 0

    for spec in SPECS:
        for coordinate in sorted(live_literals[spec.name], key=coordinate_key):
            prior = coverage_rows[spec.name][coordinate]
            evidence = prior["source_free_evidence"]
            current_text_hash = live_literals[spec.name][coordinate]
            prior_text_hash = evidence["current_ko_utf16le_sha256"]
            current_matches_prior = current_text_hash == prior_text_hash
            prior_disposition = prior.get("input_disposition")
            prior_semantic_status = prior.get("input_semantic_status")
            active_holds = sorted(holds[spec.name].get(coordinate, []), key=lambda value: (value["source"], value["record"], value["status"]))
            current_wave7_repair_evidence = sorted(
                wave7_repairs[spec.name].get(coordinate, []),
                key=lambda value: (value["source"], value["record"]),
            )
            wave7_literal_changed = any(value["literal_changed"] for value in current_wave7_repair_evidence)

            if active_holds:
                classification = "known_current_context_or_runtime_hold"
                semantic_status = "runtime_or_context_review_required"
                current_hold_literal_count += 1
            elif wave7_literal_changed:
                classification = "known_current_wave7_static_repair"
                semantic_status = "pinned_wave7_static_repair_no_global_semantic_completion"
            elif is_prior_review(prior_disposition):
                classification = (
                    "known_prior_review_carried_forward"
                    if current_matches_prior
                    else "profile_changed_prior_review_requires_rebase"
                )
                semantic_status = (
                    str(prior_semantic_status)
                    if current_matches_prior and isinstance(prior_semantic_status, str)
                    else "changed_since_prior_review_no_global_semantic_completion"
                )
            elif current_matches_prior:
                classification = "known_prior_pc_only_screened_unchanged"
                semantic_status = (
                    str(prior_semantic_status)
                    if isinstance(prior_semantic_status, str)
                    else "prior_pc_only_screened_no_semantic_completion"
                )
            else:
                classification = "known_pc_only_profile_lineage_change"
                semantic_status = "pinned_pc_only_profile_change_no_global_semantic_completion"

            current_classification_counts[classification] += 1
            prior_disposition_counts[str(prior_disposition)] += 1
            semantic_gap_counts[semantic_status] += 1
            rows.append(
                {
                    "schema": SCHEMA,
                    "resource": spec.name,
                    "relative_path": spec.relative.as_posix(),
                    "coordinate": coordinate,
                    "current_ko_utf16le_sha256": current_text_hash,
                    "pristine_pc_jp_utf16le_sha256": pristine_literals[spec.name][coordinate],
                    "current_hash_matches_prior_pc_only_ledger": current_matches_prior,
                    "prior_pc_only_ledger": {
                        "coverage_input": prior.get("coverage_input"),
                        "input_disposition": prior_disposition,
                        "input_semantic_status": prior_semantic_status,
                        "prior_current_ko_utf16le_sha256": prior_text_hash,
                    },
                    "current_profile_lineage": builder_metadata[spec.name],
                    "classification": classification,
                    "semantic_status": semantic_status,
                    "current_hold_evidence": active_holds,
                    "current_wave7_repair_evidence": current_wave7_repair_evidence,
                    "scope": {
                        "current_steam_read": True,
                        "pristine_pc_japanese_read": True,
                        "pc_context_hashes_verified": True,
                        "switch_korean_read": False,
                        "historic_korean_read": False,
                        "steam_game_resource_written": False,
                        "semantic_completion": False,
                    },
                }
            )

        # These entries were literal coordinates in the old PC-only coverage
        # ledger but are no longer literal slots in the exact current target.
        # Keep them as a separate reconciliation projection instead of faking a
        # current text hash or silently dropping their audit history.
        for coordinate in sorted(EXPECTED_RETIRED_PRIOR_COORDINATES[spec.name], key=coordinate_key):
            prior = coverage_rows[spec.name][coordinate]
            evidence = prior["source_free_evidence"]
            retired_rows.append(
                {
                    "schema": SCHEMA,
                    "resource": spec.name,
                    "relative_path": spec.relative.as_posix(),
                    "coordinate": coordinate,
                    "current_literal_present": False,
                    "pristine_pc_jp_utf16le_sha256": pristine_literals[spec.name][coordinate],
                    "prior_pc_only_ledger": {
                        "coverage_input": prior.get("coverage_input"),
                        "input_disposition": prior.get("input_disposition"),
                        "input_semantic_status": prior.get("input_semantic_status"),
                        "prior_current_ko_utf16le_sha256": evidence["current_ko_utf16le_sha256"],
                    },
                    "current_profile_lineage": builder_metadata[spec.name],
                    "classification": "known_pc_only_profile_retired_literal_coordinate",
                    "semantic_status": "retired_literal_slot_no_current_text_to_adjudicate",
                    "retirement_reason": "current pinned PC-only profile coalesced an earlier literal slot during static dialogue rewrite",
                    "scope": {
                        "current_steam_read": True,
                        "pristine_pc_japanese_read": True,
                        "pc_context_hashes_verified": True,
                        "switch_korean_read": False,
                        "historic_korean_read": False,
                        "steam_game_resource_written": False,
                        "semantic_completion": False,
                    },
                }
            )

    expected_total = sum(EXPECTED_CURRENT_COUNTS.values())
    if len(rows) != expected_total:
        raise LedgerError(f"current ledger total differs: {len(rows)} != {expected_total}")
    if sum(current_classification_counts.values()) != expected_total:
        raise LedgerError("current classification sum differs")
    expected_retired_total = sum(len(value) for value in EXPECTED_RETIRED_PRIOR_COORDINATES.values())
    if len(retired_rows) != expected_retired_total:
        raise LedgerError("retired prior coordinate count differs")
    summary: dict[str, Any] = {
        "schema": SUMMARY_SCHEMA,
        "scope": "current Steam Base and PK msggame literal-coordinate reconciliation against PC-only source-free coverage; hashes and dispositions only",
        "current_literal_coordinate_count": expected_total,
        "current_literal_resource_coordinate_counts": EXPECTED_CURRENT_COUNTS,
        "prior_coverage_coordinate_count": sum(EXPECTED_PRIOR_COUNTS.values()),
        "prior_coverage_resource_coordinate_counts": EXPECTED_PRIOR_COUNTS,
        "retired_prior_literal_coordinate_count": expected_retired_total,
        "reconciliation_coordinate_count": expected_total + expected_retired_total,
        "resources": resources_summary,
        "current_classification_counts": dict(sorted(current_classification_counts.items())),
        "prior_input_disposition_counts": dict(sorted(prior_disposition_counts.items())),
        "semantic_status_counts": dict(sorted(semantic_gap_counts.items())),
        "current_explicit_hold_literal_count": current_hold_literal_count,
        "current_explicit_hold_source_validation": hold_metadata,
        "current_wave7_repair_record_count": hold_metadata["wave7_repair_validation"]["matched_record_count"],
        "current_wave7_changed_literal_count": hold_metadata["wave7_repair_validation"]["changed_literal_count"],
        "current_wave7_runtime_visual_qa_record_count": hold_metadata["wave7_repair_validation"]["runtime_visual_qa_record_count"],
        "coverage_manifest": {
            "ledger": relative_path(COVERAGE_LEDGER),
            "ledger_sha256": sha256_file(COVERAGE_LEDGER),
            "summary": relative_path(COVERAGE_SUMMARY),
            "summary_sha256": sha256_file(COVERAGE_SUMMARY),
            "all_input_pc_only_provenance_checks_passed": True,
        },
        "semantic_completion": False,
        "semantic_completion_reason": (
            "Every current literal has a PC-only prior-ledger or pinned-profile lineage, "
            "but static provenance/coverage does not prove context-sensitive Korean quality or in-game rendering."
        ),
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "steam_installation_written": False,
        "source_text_emitted": False,
        "deterministic_serialization": "UTF-8 JSONL sorted by resource and numeric literal coordinate; sorted JSON keys",
    }
    return rows, retired_rows, summary


def output_paths(output_root: Path) -> dict[str, Path]:
    root = require_output_root(output_root)
    return {
        "ledger": root / "current_pc_dialogue_coordinate_ledger.source_free.v1.jsonl",
        "retired": root / "retired_prior_literal_coordinates.source_free.v1.jsonl",
        "holds": root / "current_pc_dialogue_explicit_holds.source_free.v1.jsonl",
        "summary": root / "summary.source_free.v1.json",
    }


def validate_rows(rows: list[dict[str, Any]], summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    by_resource: dict[str, list[dict[str, Any]]] = defaultdict(list)
    holds: list[dict[str, Any]] = []
    for row in rows:
        if row.get("schema") != SCHEMA:
            raise LedgerError("ledger row schema differs")
        resource = row.get("resource")
        if resource not in EXPECTED_CURRENT_COUNTS:
            raise LedgerError("ledger resource differs")
        coordinate = row.get("coordinate")
        if not isinstance(coordinate, str):
            raise LedgerError("ledger coordinate is invalid")
        coordinate_key(coordinate)
        scope = row.get("scope")
        if not isinstance(scope, dict) or scope.get("switch_korean_read") or scope.get("historic_korean_read") or scope.get("steam_game_resource_written"):
            raise LedgerError("ledger scope is no longer PC-only/read-only")
        if scope.get("semantic_completion") is not False:
            raise LedgerError("ledger row claims semantic completion")
        by_resource[resource].append(row)
        if row.get("current_hold_evidence"):
            holds.append(row)
    for resource, expected in EXPECTED_CURRENT_COUNTS.items():
        resource_rows = by_resource[resource]
        if len(resource_rows) != expected:
            raise LedgerError(f"validation count differs for {resource}")
        coordinates = [row["coordinate"] for row in resource_rows]
        if len(coordinates) != len(set(coordinates)):
            raise LedgerError(f"duplicate current ledger coordinate for {resource}")
    if summary.get("current_literal_coordinate_count") != len(rows):
        raise LedgerError("summary coordinate count differs")
    if summary.get("semantic_completion") is not False:
        raise LedgerError("summary claims semantic completion")
    return holds


def validate_retired_rows(rows: list[dict[str, Any]], summary: Mapping[str, Any]) -> None:
    expected_total = sum(len(value) for value in EXPECTED_RETIRED_PRIOR_COORDINATES.values())
    if len(rows) != expected_total:
        raise LedgerError("retired ledger count differs")
    by_resource: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if row.get("schema") != SCHEMA or row.get("current_literal_present") is not False:
            raise LedgerError("retired ledger row schema/state differs")
        resource = row.get("resource")
        coordinate = row.get("coordinate")
        if resource not in EXPECTED_RETIRED_PRIOR_COORDINATES or not isinstance(coordinate, str):
            raise LedgerError("retired ledger resource/coordinate is invalid")
        coordinate_key(coordinate)
        scope = row.get("scope")
        if not isinstance(scope, dict) or scope.get("switch_korean_read") or scope.get("historic_korean_read") or scope.get("steam_game_resource_written"):
            raise LedgerError("retired ledger scope is no longer PC-only/read-only")
        by_resource[resource].add(coordinate)
    if {name: by_resource[name] for name in EXPECTED_RETIRED_PRIOR_COORDINATES} != EXPECTED_RETIRED_PRIOR_COORDINATES:
        raise LedgerError("retired ledger coordinate set differs")
    if summary.get("retired_prior_literal_coordinate_count") != len(rows):
        raise LedgerError("summary retired count differs")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--write", action="store_true", help="write deterministic source-free artifacts below KR_PATCH_WORK/tmp")
    parser.add_argument("--validate", action="store_true", help="compare deterministic artifacts already under the output root")
    args = parser.parse_args()

    rows, retired_rows, summary = build(args.steam_root)
    holds = validate_rows(rows, summary)
    validate_retired_rows(retired_rows, summary)
    paths = output_paths(args.output_root)
    payloads = {
        "ledger": canonical_jsonl(rows),
        "retired": canonical_jsonl(retired_rows),
        "holds": canonical_jsonl(holds),
        "summary": canonical_json(summary),
    }
    if args.write:
        for key, path in paths.items():
            atomic_write(path, payloads[key])
    if args.validate:
        for key, path in paths.items():
            if not path.is_file():
                raise LedgerError(f"expected deterministic {key} output is absent: {path}")
            if path.read_bytes() != payloads[key]:
                raise LedgerError(f"deterministic {key} output differs: {path}")
    public_result = {
        "current_literal_coordinate_count": summary["current_literal_coordinate_count"],
        "retired_prior_literal_coordinate_count": summary["retired_prior_literal_coordinate_count"],
        "current_classification_counts": summary["current_classification_counts"],
        "current_explicit_hold_literal_count": summary["current_explicit_hold_literal_count"],
        "semantic_completion": summary["semantic_completion"],
        "steam_installation_written": False,
        "switch_korean_translation_used": False,
    }
    print(json.dumps(public_result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
