#!/usr/bin/env python3
"""Build a source-free current Steam PC dialogue ledger after Wave 14.

This is a read-only reconciliation tool for Base and PK ``msggame``.  It
enumerates every current literal coordinate, preserves the PC-only coverage
history, and validates Waves 7--14 against the *current target record hash*
rather than their historical whole-file candidate hashes.  Older full-file
candidate hashes are intentionally not used as current-state evidence because
later waves compose valid changes into the same packed resources.

The builder never writes a game resource, calls Git, opens a network
connection, or reads a Switch Korean or historic Korean translation.  Its
only optional writes are deterministic source-free JSON artifacts below this
workstream's ``tmp`` directory.
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
DEFAULT_OUTPUT_ROOT = TMP / WORKSTREAM.name

MSGGAME_ROOT = REPO / "workstreams" / "msggame"
sys.path.insert(0, str(MSGGAME_ROOT))

from msggame_format import MsgGameRecord, iter_literals, parse_packed_msggame  # noqa: E402


SCHEMA = "nobu16.kr.current-pc-dialogue-coordinate-ledger.v2"
SUMMARY_SCHEMA = "nobu16.kr.current-pc-dialogue-coordinate-ledger-summary.v2"
HOLD_SCHEMA = "nobu16.kr.current-pc-dialogue-hold-evidence.v2"
STALE_HOLD_SCHEMA = "nobu16.kr.current-pc-dialogue-stale-legacy-hold.v2"
COVERAGE_SCHEMA = "nobu16.kr.pc-only-coverage-merged-disposition.v1"

BASE_RELATIVE = Path("MSG/JP/msggame.bin")
PK_RELATIVE = Path("MSG_PK/JP/msggame.bin")
BASE_PRISTINE = Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin")
PK_PRISTINE_RELATIVE = Path(
    "KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin"
)

COVERAGE_SUMMARY = TMP / "translation_quality_pc_coverage_manifest_v1" / "summary.source_free.json"
COVERAGE_LEDGER = (
    TMP
    / "translation_quality_pc_coverage_manifest_v1"
    / "merged_pc_only_coordinate_dispositions.v1.jsonl"
)

# This is the exact, installed Wave 14 11-file profile.  The ledger itself is
# scoped to the two msggame resources, but requiring the surrounding profile
# prevents a mixed transaction from being presented as the reviewed state.
CURRENT_WAVE14_PROFILE_SHA256: dict[str, str] = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    "MSG/JP/msggame.bin": "4D147A4AD73466E882043D8A5E47F0D4DAF37473702A8CEABAEFFBF4E76F2EB8",
    "MSG/JP/strdata.bin": "5F308F416378976C1AB0B50D4A91C9DA38C637A0A842BAB04FB48256B2103E28",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "69090EC9EEE1DF9EAFB64BB35CEFD285A5089FDE78E9A4A855EAA0AE5991C168",
    "MSG_PK/JP/msgev.bin": "3E2323DDFAD70DAA15713DD1C4D622508BD2E610C65683C0A06D3D1FAC9827A5",
    "MSG_PK/JP/msggame.bin": "BD789D1C5230159433BDB9F2FCBE4B0ABABF9D84FAD2FE1C16EED45B071CE860",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}


@dataclass(frozen=True)
class ResourceSpec:
    name: str
    relative: Path
    pristine_kind: str
    expected_pristine_sha256: str
    context_relatives: Mapping[str, Path]
    expected_context_sha256: Mapping[str, str]


SPECS: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        name="base_msggame",
        relative=BASE_RELATIVE,
        pristine_kind="workspace_pc_jp",
        expected_pristine_sha256="EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        context_relatives={
            "SC": Path("MSG/SC/msggame.bin"),
            "TC": Path("MSG/TC/msggame.bin"),
        },
        expected_context_sha256={
            "SC": "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7",
            "TC": "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95",
        },
    ),
    ResourceSpec(
        name="pk_msggame",
        relative=PK_RELATIVE,
        pristine_kind="steam_transaction_pc_jp",
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
    ),
)

EXPECTED_PRIOR_COUNTS = {"base_msggame": 24_262, "pk_msggame": 29_524}
EXPECTED_CURRENT_COUNTS = {"base_msggame": 24_241, "pk_msggame": 29_502}
EXPECTED_CURRENT_LITERAL_COUNT = 53_743
EXPECTED_PRIOR_LITERAL_COUNT = 53_786
EXPECTED_RETIRED_PRIOR_COORDINATES = {
    "base_msggame": {
        "13:9:1", "13:17:1", "13:24:1", "13:27:1", "13:27:2", "13:28:1", "13:30:1",
        "13:40:1", "13:55:1", "13:108:1", "13:110:1", "13:116:1", "13:122:1",
        "13:127:1", "13:128:1", "13:136:1", "13:142:1", "16:4:1", "16:15:1",
        "16:32:1", "16:38:1",
    },
    "pk_msggame": {
        "13:9:1", "13:17:1", "13:24:1", "13:27:1", "13:27:2", "13:28:1", "13:30:1",
        "13:40:1", "13:55:1", "13:108:1", "13:110:1", "13:116:1", "13:122:1",
        "13:127:1", "13:128:1", "13:136:1", "13:142:1", "16:4:1", "16:15:1",
        "16:32:1", "16:38:1", "16:45:1",
    },
}
EXPECTED_RETIRED_LITERAL_COUNT = 43
EXPECTED_PRIOR_HASH_MATCH_COUNT = 52_192
EXPECTED_PRIOR_HASH_DIFFERENT_COUNT = 1_551
EXPECTED_LEGACY_LINEAGE_DIFFERENT_COUNT = 1_285


@dataclass(frozen=True)
class RepairAuditSpec:
    wave: str
    path: Path
    expected_file_sha256: str
    schema: str
    rows_key: str
    default_resource: str | None
    target_record_hash_key: str
    expected_record_count: int
    expected_changed_literal_count: int


REPAIR_AUDITS: tuple[RepairAuditSpec, ...] = (
    RepairAuditSpec(
        "wave7",
        REPO / "workstreams" / "pc_dialogue_goodwill_runtime_wave7_v1" / "audit_pc_current_static_repairs_wave7.v1.json",
        "83B4E88AC51A7DBA21AF4F1617AC3283CAB1F85D795D5F6883383BFA7C797233",
        "nobu16.kr.pc-dialogue-current-static-repairs-wave7.audit.v1",
        "records",
        None,
        "output_record_sha256",
        12,
        24,
    ),
    RepairAuditSpec(
        "wave8",
        REPO / "workstreams" / "pc_dialogue_quality_wave8_candidate_v1" / "audit_pc_dialogue_quality_wave8.v1.json",
        "0C688267C8CF77E066C162469F91AB8A89A0EFB97C164F5F333A51182719DAC4",
        "nobu16.kr.pc-dialogue-quality-wave8-audit.v1",
        "msggame_records",
        None,
        "output_record_sha256",
        48,
        108,
    ),
    RepairAuditSpec(
        "wave9",
        TMP / "pc_dialogue_runtime_wave9_candidate_v1" / "audit_pc_dialogue_runtime_wave9.v1.json",
        "F428C9455C02D34C2CE59E3436BE60D114E5EB17FB3A9950F256D446E95751AF",
        "nobu16.kr.pc-dialogue-runtime-wave9.audit.v1",
        "records",
        "pk_msggame",
        "output_record_sha256",
        33,
        59,
    ),
    RepairAuditSpec(
        "wave10",
        TMP / "pc_dialogue_quality_wave10_candidate_v1" / "audit_pc_dialogue_quality_wave10.v1.json",
        "D3419E76F3CA7BD3B2D5E70BEBF1A5F5AB08223AA5F4533B8DCFD06E361E7680",
        "nobu16.kr.pc-dialogue-quality-wave10-audit.v1",
        "records",
        "pk_msggame",
        "output_record_sha256",
        12,
        24,
    ),
    RepairAuditSpec(
        "wave11",
        TMP / "pc_dialogue_quality_wave11_candidate_v1" / "audit_pc_dialogue_quality_wave11.v1.json",
        "3E72E594DC8E4220FE408B9E3138E9BD699A06CAF4EA66898573CE342CB9E846",
        "nobu16.kr.pc-dialogue-quality-wave11-audit.v1",
        "records",
        "pk_msggame",
        "output_record_sha256",
        8,
        8,
    ),
    RepairAuditSpec(
        "wave12",
        TMP / "pc_dialogue_quality_wave12_candidate_v1" / "audit_pc_dialogue_quality_wave12.v1.json",
        "D97990147E3B0E3E51A642512154A35DFDA5DCFF9FB2A0D73D61E883C242FD6D",
        "nobu16.kr.pc-dialogue-quality-wave12-audit.v1",
        "records",
        None,
        "output_record_sha256",
        2,
        2,
    ),
    RepairAuditSpec(
        "wave13",
        TMP / "pc_dialogue_quality_wave13_static12_candidate_v1" / "audit.v1.json",
        "ABBBF688C7D1CD98A121C946BD86ABF4DF5B61598A78EA6ABE5DC2D3C2E1AB5E",
        "nobu16.kr.pc-dialogue-quality-wave13-static12-audit.v1",
        "records",
        "pk_msggame",
        "target_record_sha256",
        12,
        22,
    ),
    RepairAuditSpec(
        "wave14",
        TMP / "pc_dialogue_quality_wave14_static_inflection_v1" / "audit.v1.json",
        "1C2726DF8282D68787E6D7990F433FD1E9E5E7C53AB680D184AFAD49FF777C43",
        "nobu16.kr.pc-dialogue-quality-wave14-static-inflection-audit.v1",
        "records",
        None,
        "target_record_sha256",
        11,
        19,
    ),
)

EXPECTED_REPAIR_RECORD_COUNT = 138
EXPECTED_REPAIR_LITERAL_COUNT = 266
EXPECTED_REPAIR_LITERAL_COUNTS = {
    "wave7": 24,
    "wave8": 108,
    "wave9": 59,
    "wave10": 24,
    "wave11": 8,
    "wave12": 2,
    "wave13": 22,
    "wave14": 19,
}

WAVE5_RUNTIME_HOLD = (
    REPO / "workstreams" / "pc_dialogue_quality_wave5_v1" / "audit" / "audit_base_suffix_batch03_dynamic_particle.jsonl"
)
WAVE5_PK_RUNTIME_HOLDS = (
    REPO / "workstreams" / "pc_dialogue_quality_wave5_v1" / "audit_pk_donor_runtime_particle_holds.jsonl"
)
WAVE5_PK_RECLASSIFICATION = (
    REPO / "workstreams" / "pc_dialogue_quality_wave5_v1" / "audit_pk_colon_manual_96_runtime_particle_reclassification.json"
)
WAVE5_RESIDUAL_HOLDS = (
    REPO / "workstreams" / "pc_dialogue_quality_wave5_v1" / "audit" / "audit_residual_korean_quality_scan_hold_v1.jsonl"
)

EXPECTED_HOLD_SOURCE_RECORD_COUNTS = {
    "base_suffix_batch03": {"matched_record_count": 0, "stale_record_count": 2},
    "pk_donor_runtime_particle": {"matched_record_count": 96, "stale_record_count": 25},
    "pk_reclassification": {"matched_record_count": 57, "stale_record_count": 4},
    "residual_policy": {"matched_record_count": 10, "stale_record_count": 0},
    "wave7_runtime_visual_qa": {"matched_record_count": 7, "stale_record_count": 0},
    "wave8_historical_real_game_qa": {"matched_record_count": 48, "stale_record_count": 0},
    "wave9_historical_real_game_qa": {"matched_record_count": 33, "stale_record_count": 0},
}
EXPECTED_CURRENT_HOLD_LITERAL_COUNT = 597
EXPECTED_CURRENT_HOLD_GROUP_COUNTS = {
    "wave5_runtime_or_policy": 421,
    "wave7_runtime_visual_qa": 16,
    "wave8_historical_real_game_qa": 108,
    "wave9_historical_real_game_qa": 60,
}
EXPECTED_STALE_LEGACY_HOLD_RECORD_COUNT = 31


class LedgerError(ValueError):
    """A pinned input, source policy, or current-state invariant changed."""


@dataclass(frozen=True)
class LoadedRepairAudit:
    spec: RepairAuditSpec
    payload: Mapping[str, Any]
    rows: tuple[Mapping[str, Any], ...]


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


def relative_path(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


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


def record_from_coordinate(value: str) -> str:
    parts = value.split(":")
    if len(parts) not in {2, 3} or any(not part.isdecimal() for part in parts):
        raise LedgerError(f"invalid audit coordinate: {value!r}")
    record = f"{parts[0]}:{parts[1]}"
    record_key(record)
    return record


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("ascii")


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(
        json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
        for row in rows
    )


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


def require_text(row: Mapping[str, Any], key: str, source: Path) -> str:
    value = row.get(key)
    if not isinstance(value, str):
        raise LedgerError(f"{source} lacks string {key}")
    return value


def read_json(path: Path, label: str) -> dict[str, Any]:
    require_file(path, label)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LedgerError(f"{label} is invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise LedgerError(f"{label} is not an object")
    return value


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    require_file(path, "JSONL input")
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise LedgerError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise LedgerError(f"non-object JSONL row at {path}:{line_number}")
            yield row


def parse_msggame(path: Path) -> tuple[dict[str, str], dict[str, str], dict[str, tuple[str, ...]]]:
    archive = parse_packed_msggame(path.read_bytes()).archive
    literal_hashes: dict[str, str] = {}
    record_hashes: dict[str, str] = {}
    record_literals: dict[str, list[str]] = defaultdict(list)
    for record in (record for block in archive.blocks for record in block.records):
        record = record  # retain the explicit record type for static checkers.
        key = f"{record.block_id}:{record.record_id}"
        record_hashes[key] = sha256_bytes(record.data)
    for literal in iter_literals(archive):
        key = f"{literal.block_id}:{literal.record_id}:{literal.literal_id}"
        if key in literal_hashes:
            raise LedgerError(f"duplicate parsed literal coordinate: {key}")
        literal_hashes[key] = sha256_text(literal.text)
        record_literals[f"{literal.block_id}:{literal.record_id}"].append(key)
    return (
        literal_hashes,
        record_hashes,
        {record: tuple(sorted(coordinates, key=coordinate_key)) for record, coordinates in record_literals.items()},
    )


def pristine_path(spec: ResourceSpec, steam_root: Path) -> Path:
    if spec.pristine_kind == "workspace_pc_jp":
        return BASE_PRISTINE
    if spec.pristine_kind == "steam_transaction_pc_jp":
        return steam_root / PK_PRISTINE_RELATIVE
    raise LedgerError(f"unknown pristine kind: {spec.pristine_kind}")


def validate_current_profile(steam_root: Path) -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in sorted(CURRENT_WAVE14_PROFILE_SHA256.items()):
        actual = sha256_file(require_file(steam_root / relative, f"current Steam profile resource {relative}"))
        if actual != expected:
            raise LedgerError(f"current Wave 14 profile hash drift for {relative}: {actual}")
        observed[relative] = actual
    return observed


def load_coverage_rows() -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, Any]]:
    summary = read_json(COVERAGE_SUMMARY, "coverage summary")
    if summary.get("schema") != "nobu16.kr.pc-only-coverage-manifest.v1":
        raise LedgerError("coverage summary schema differs")
    expected_flags = {
        "all_input_pc_only_provenance_checks_passed": True,
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "steam_installation_written": False,
        "semantic_completion": False,
    }
    for key, expected in expected_flags.items():
        if summary.get(key) is not expected:
            raise LedgerError(f"coverage summary {key} differs")
    resources = summary.get("resource_coordinate_counts")
    if not isinstance(resources, dict) or any(
        resources.get(resource) != expected for resource, expected in EXPECTED_PRIOR_COUNTS.items()
    ):
        raise LedgerError("coverage summary resource coordinate counts differ")

    accepted = set(EXPECTED_PRIOR_COUNTS)
    rows: dict[str, dict[str, dict[str, Any]]] = {resource: {} for resource in accepted}
    for row in read_jsonl(COVERAGE_LEDGER):
        resource = row.get("resource")
        if resource not in accepted:
            continue
        if row.get("schema") != COVERAGE_SCHEMA or row.get("semantic_completion") is not False:
            raise LedgerError(f"coverage row schema/semantic state differs at {resource}")
        coordinate = row.get("coordinate")
        evidence = row.get("source_free_evidence")
        if not isinstance(coordinate, str) or not isinstance(evidence, dict):
            raise LedgerError(f"coverage row lacks coordinate/evidence at {resource}")
        coordinate_key(coordinate)
        if not isinstance(evidence.get("current_ko_utf16le_sha256"), str):
            raise LedgerError(f"coverage row lacks prior hash at {resource}:{coordinate}")
        if coordinate in rows[resource]:
            raise LedgerError(f"duplicate coverage coordinate: {resource}:{coordinate}")
        rows[resource][coordinate] = row
    for resource, expected in EXPECTED_PRIOR_COUNTS.items():
        if len(rows[resource]) != expected:
            raise LedgerError(f"coverage row count differs for {resource}: {len(rows[resource])}")
    return rows, summary


def resource_from_audit_row(row: Mapping[str, Any], spec: RepairAuditSpec) -> str:
    relative = row.get("resource")
    if relative == BASE_RELATIVE.as_posix():
        return "base_msggame"
    if relative == PK_RELATIVE.as_posix():
        return "pk_msggame"
    if spec.default_resource is not None:
        return spec.default_resource
    raise LedgerError(f"{spec.wave} audit row lacks a supported resource")


def validate_repair_policy(spec: RepairAuditSpec, payload: Mapping[str, Any]) -> None:
    """Reject audit artifacts whose declared source policy widened beyond PC-only."""
    wave = spec.wave
    if wave == "wave7":
        scope = payload.get("scope")
        if not isinstance(scope, dict) or scope.get("platform") != "Steam PC" or scope.get("excluded_sources") != ["Switch Korean"]:
            raise LedgerError("Wave 7 source policy differs")
        return
    if wave == "wave8":
        scope = payload.get("scope")
        if not isinstance(scope, dict):
            raise LedgerError("Wave 8 scope is absent")
        if scope.get("platform") != "Steam PC" or scope.get("excluded_sources") != ["Switch Korean"]:
            raise LedgerError("Wave 8 source policy differs")
        if scope.get("steam_game_resource_written") is not False:
            raise LedgerError("Wave 8 no longer asserts read-only construction")
        return
    if wave in {"wave9", "wave10", "wave11", "wave12"}:
        policy = payload.get("source_policy")
        if not isinstance(policy, dict) or policy.get("platform") != "Steam PC":
            raise LedgerError(f"{wave} source policy is absent")
        if policy.get("excluded") != ["Nintendo Switch Korean"] or policy.get("switch_korean_used") is not False:
            raise LedgerError(f"{wave} source policy permits Switch Korean")
        if payload.get("steam_write_capability") != "absent":
            raise LedgerError(f"{wave} no longer asserts no Steam writer")
        return
    if wave == "wave13":
        policy = payload.get("source_policy")
        if not isinstance(policy, dict) or policy.get("platform") != "Steam PC":
            raise LedgerError("Wave 13 source policy is absent")
        if policy.get("switch_korean_used") is not False or policy.get("steam_write_capability") != "absent":
            raise LedgerError("Wave 13 source policy differs")
        return
    if wave == "wave14":
        policy = payload.get("source_policy")
        if not isinstance(policy, dict) or policy.get("platform") != "Steam PC":
            raise LedgerError("Wave 14 source policy is absent")
        required = {
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "pristine_pc_japanese_read": True,
            "pc_en_sc_tc_context_read": True,
        }
        if any(policy.get(key) is not value for key, value in required.items()):
            raise LedgerError("Wave 14 source policy differs")
        return
    raise LedgerError(f"unsupported repair wave: {wave}")


def load_repair_audits() -> dict[str, LoadedRepairAudit]:
    result: dict[str, LoadedRepairAudit] = {}
    for spec in REPAIR_AUDITS:
        require_file(spec.path, f"{spec.wave} audit")
        if sha256_file(spec.path) != spec.expected_file_sha256:
            raise LedgerError(f"{spec.wave} audit file hash differs")
        payload = read_json(spec.path, f"{spec.wave} audit")
        if payload.get("schema") != spec.schema:
            raise LedgerError(f"{spec.wave} audit schema differs")
        validate_repair_policy(spec, payload)
        rows = payload.get(spec.rows_key)
        if not isinstance(rows, list) or len(rows) != spec.expected_record_count:
            raise LedgerError(f"{spec.wave} audit record count differs")
        if not all(isinstance(row, dict) for row in rows):
            raise LedgerError(f"{spec.wave} audit has a non-object row")
        result[spec.wave] = LoadedRepairAudit(spec, payload, tuple(rows))
    return result


def load_current_repair_evidence(
    audits: Mapping[str, LoadedRepairAudit],
    coverage_rows: Mapping[str, Mapping[str, Mapping[str, Any]]],
    live_literals: Mapping[str, Mapping[str, str]],
    record_hashes: Mapping[str, Mapping[str, str]],
    record_literals: Mapping[str, Mapping[str, tuple[str, ...]]],
) -> tuple[dict[str, dict[str, list[dict[str, str]]]], dict[str, Any]]:
    """Validate each historic wave against its exact current target records.

    The changed literal projection is deliberately derived from the current
    record slots that differ from the immutable prior PC-only coverage ledger.
    Every target record must contain at least one such slot and each wave's
    exact reviewed count is pinned below.  This avoids emitting audit text and
    avoids falsely requiring historical whole-file candidate hashes.
    """
    evidence: dict[str, dict[str, list[dict[str, str]]]] = {
        resource: defaultdict(list) for resource in EXPECTED_CURRENT_COUNTS
    }
    seen_records: set[tuple[str, str]] = set()
    changed_counts: Counter[str] = Counter()
    record_counts: Counter[str] = Counter()
    record_rows: list[dict[str, Any]] = []

    for spec in REPAIR_AUDITS:
        audit = audits[spec.wave]
        source = relative_path(spec.path)
        for row in audit.rows:
            resource = resource_from_audit_row(row, spec)
            coordinate = require_text(row, "coordinate", spec.path)
            record = record_from_coordinate(coordinate)
            target_record_sha256 = require_text(row, spec.target_record_hash_key, spec.path)
            key = (resource, record)
            if key in seen_records:
                raise LedgerError(f"duplicate repair record across waves: {resource}:{record}")
            seen_records.add(key)
            actual_record_sha256 = record_hashes[resource].get(record)
            if actual_record_sha256 != target_record_sha256:
                raise LedgerError(
                    f"{spec.wave} current target record differs: {resource}:{record}: {actual_record_sha256}"
                )
            slots = record_literals[resource].get(record, ())
            if not slots:
                raise LedgerError(f"{spec.wave} target record has no current literal slots: {resource}:{record}")
            changed_slots: list[str] = []
            for slot in slots:
                prior = coverage_rows[resource].get(slot)
                if prior is None:
                    raise LedgerError(f"{spec.wave} target slot is absent from prior coverage: {resource}:{slot}")
                prior_hash = prior["source_free_evidence"]["current_ko_utf16le_sha256"]
                if live_literals[resource][slot] != prior_hash:
                    changed_slots.append(slot)
            if not changed_slots:
                raise LedgerError(f"{spec.wave} target record has no changed literal slot: {resource}:{record}")
            for slot in changed_slots:
                row_evidence = {
                    "current_record_sha256": actual_record_sha256,
                    "record": record,
                    "source": source,
                    "source_sha256": spec.expected_file_sha256,
                    "target_record_sha256": target_record_sha256,
                    "wave": spec.wave,
                }
                if row_evidence in evidence[resource][slot]:
                    raise LedgerError(f"duplicate repair literal evidence: {resource}:{slot}")
                evidence[resource][slot].append(row_evidence)
            changed_counts[spec.wave] += len(changed_slots)
            record_counts[spec.wave] += 1
            record_rows.append(
                {
                    "resource": resource,
                    "record": record,
                    "target_record_sha256": target_record_sha256,
                    "wave": spec.wave,
                }
            )

    if len(seen_records) != EXPECTED_REPAIR_RECORD_COUNT:
        raise LedgerError(f"verified repair record count differs: {len(seen_records)}")
    if dict(sorted(record_counts.items())) != {spec.wave: spec.expected_record_count for spec in REPAIR_AUDITS}:
        raise LedgerError("per-wave verified repair record counts differ")
    if dict(sorted(changed_counts.items())) != EXPECTED_REPAIR_LITERAL_COUNTS:
        raise LedgerError(f"per-wave changed literal counts differ: {dict(sorted(changed_counts.items()))}")
    if sum(changed_counts.values()) != EXPECTED_REPAIR_LITERAL_COUNT:
        raise LedgerError("verified repair literal count differs")
    return evidence, {
        "all_target_record_hashes_match_current": True,
        "changed_literal_counts": dict(sorted(changed_counts.items())),
        "record_count": len(seen_records),
        "record_counts": dict(sorted(record_counts.items())),
        "record_rows": sorted(record_rows, key=lambda value: (value["wave"], value["resource"], record_key(value["record"]))),
    }


def append_hold(
    holds: dict[str, dict[str, list[dict[str, str]]]],
    hold_groups: dict[str, dict[str, set[str]]],
    *,
    resource: str,
    record: str,
    record_hash: str,
    source: Path,
    source_kind: str,
    source_sha256: str,
    status: str,
    category: str,
    group: str,
    record_literals: Mapping[str, Mapping[str, tuple[str, ...]]],
    validation_kind: str,
) -> None:
    slots = record_literals[resource].get(record, ())
    if not slots:
        raise LedgerError(f"hold record has no literal slots: {resource}:{record}")
    source_text = relative_path(source)
    item = {
        "category": category,
        "current_record_sha256": record_hash,
        "evidence_status": "record_hash_matches_current" if validation_kind == "record_hash" else "coordinate_present_current_record_observed",
        "group": group,
        "record": record,
        "source": source_text,
        "source_kind": source_kind,
        "source_sha256": source_sha256,
        "status": status,
        "validation_kind": validation_kind,
    }
    for slot in slots:
        if item not in holds[resource][slot]:
            holds[resource][slot].append(item)
        hold_groups[resource][slot].add(group)


def stale_hold_row(
    *,
    resource: str,
    record: str,
    source: Path,
    source_kind: str,
    source_sha256: str,
    status: str,
    category: str,
    expected_record_sha256: str | None,
    observed_record_sha256: str | None,
    reason: str,
) -> dict[str, Any]:
    return {
        "schema": STALE_HOLD_SCHEMA,
        "category": category,
        "expected_record_sha256": expected_record_sha256,
        "observed_record_sha256": observed_record_sha256,
        "reason": reason,
        "record": record,
        "resource": resource,
        "source": relative_path(source),
        "source_kind": source_kind,
        "source_sha256": source_sha256,
        "status": status,
    }


def load_current_hold_evidence(
    audits: Mapping[str, LoadedRepairAudit],
    record_hashes: Mapping[str, Mapping[str, str]],
    record_literals: Mapping[str, Mapping[str, tuple[str, ...]]],
) -> tuple[dict[str, dict[str, list[dict[str, str]]]], dict[str, Any], list[dict[str, Any]]]:
    """Reconcile current, hash-valid attention evidence and stale hold preimages.

    "current" here means the evidence still binds to a present current record;
    it does not assert that a historical real-game QA requirement was completed.
    Stale legacy preimages remain in a separate artifact for re-triage.
    """
    holds: dict[str, dict[str, list[dict[str, str]]]] = {
        resource: defaultdict(list) for resource in EXPECTED_CURRENT_COUNTS
    }
    hold_groups: dict[str, dict[str, set[str]]] = {
        resource: defaultdict(set) for resource in EXPECTED_CURRENT_COUNTS
    }
    stale_rows: list[dict[str, Any]] = []
    source_stats: dict[str, dict[str, int]] = {}

    def attach_hash_bound_rows(
        *,
        source: Path,
        source_kind: str,
        resource: str,
        rows: Iterable[Mapping[str, Any]],
        select: callable,
        status_for: callable,
        category: str,
        group: str,
    ) -> None:
        source_sha = sha256_file(require_file(source, source_kind))
        matched = stale = 0
        for row in rows:
            if not select(row):
                continue
            record = require_text(row, "coordinate", source)
            record = record_from_coordinate(record)
            expected = require_text(row, "current_record_sha256", source)
            actual = record_hashes[resource].get(record)
            status = status_for(row)
            if actual != expected:
                stale += 1
                stale_rows.append(
                    stale_hold_row(
                        resource=resource,
                        record=record,
                        source=source,
                        source_kind=source_kind,
                        source_sha256=source_sha,
                        status=status,
                        category=category,
                        expected_record_sha256=expected,
                        observed_record_sha256=actual,
                        reason="legacy_record_preimage_no_longer_matches_current",
                    )
                )
                continue
            matched += 1
            append_hold(
                holds,
                hold_groups,
                resource=resource,
                record=record,
                record_hash=actual,
                source=source,
                source_kind=source_kind,
                source_sha256=source_sha,
                status=status,
                category=category,
                group=group,
                record_literals=record_literals,
                validation_kind="record_hash",
            )
        source_stats[source_kind] = {"matched_record_count": matched, "stale_record_count": stale}

    attach_hash_bound_rows(
        source=WAVE5_RUNTIME_HOLD,
        source_kind="base_suffix_batch03",
        resource="base_msggame",
        rows=read_jsonl(WAVE5_RUNTIME_HOLD),
        select=lambda row: row.get("status") == "candidate_requires_runtime_qa",
        status_for=lambda row: "candidate_requires_runtime_qa",
        category="runtime_particle_and_suffix",
        group="wave5_runtime_or_policy",
    )
    attach_hash_bound_rows(
        source=WAVE5_PK_RUNTIME_HOLDS,
        source_kind="pk_donor_runtime_particle",
        resource="pk_msggame",
        rows=read_jsonl(WAVE5_PK_RUNTIME_HOLDS),
        select=lambda row: row.get("eligible_for_steam_application") is False,
        status_for=lambda row: "hold_runtime_particle",
        category="runtime_particle_allomorph",
        group="wave5_runtime_or_policy",
    )

    reclassification_payload = read_json(WAVE5_PK_RECLASSIFICATION, "PK runtime reclassification")
    reclassification_rows = reclassification_payload.get("records")
    if not isinstance(reclassification_rows, list) or not all(isinstance(row, dict) for row in reclassification_rows):
        raise LedgerError("PK runtime reclassification records are invalid")
    attach_hash_bound_rows(
        source=WAVE5_PK_RECLASSIFICATION,
        source_kind="pk_reclassification",
        resource="pk_msggame",
        rows=reclassification_rows,
        select=lambda row: isinstance(row.get("final_application_status"), str) and row["final_application_status"].startswith("hold_"),
        status_for=lambda row: require_text(row, "final_application_status", WAVE5_PK_RECLASSIFICATION),
        category="runtime_particle_or_opaque_grammar",
        group="wave5_runtime_or_policy",
    )

    residual_source_sha = sha256_file(require_file(WAVE5_RESIDUAL_HOLDS, "residual hold ledger"))
    residual_matched = residual_stale = 0
    for row in read_jsonl(WAVE5_RESIDUAL_HOLDS):
        if row.get("status") != "hold" or not isinstance(row.get("kind"), str) or not isinstance(row.get("coordinates"), dict):
            continue
        category = row["kind"]
        for short_name, records in row["coordinates"].items():
            resource = {"Base": "base_msggame", "PK": "pk_msggame"}.get(short_name)
            if resource is None or not isinstance(records, list):
                raise LedgerError("residual hold coordinates are invalid")
            for raw_record in records:
                if not isinstance(raw_record, str):
                    raise LedgerError("residual hold record is invalid")
                record = record_from_coordinate(raw_record)
                actual = record_hashes[resource].get(record)
                if actual is None or not record_literals[resource].get(record):
                    residual_stale += 1
                    stale_rows.append(
                        stale_hold_row(
                            resource=resource,
                            record=record,
                            source=WAVE5_RESIDUAL_HOLDS,
                            source_kind="residual_policy",
                            source_sha256=residual_source_sha,
                            status="hold_project_term_or_glyph_policy",
                            category=category,
                            expected_record_sha256=None,
                            observed_record_sha256=actual,
                            reason="coordinate_bound_legacy_hold_record_absent",
                        )
                    )
                    continue
                residual_matched += 1
                append_hold(
                    holds,
                    hold_groups,
                    resource=resource,
                    record=record,
                    record_hash=actual,
                    source=WAVE5_RESIDUAL_HOLDS,
                    source_kind="residual_policy",
                    source_sha256=residual_source_sha,
                    status="hold_project_term_or_glyph_policy",
                    category=category,
                    group="wave5_runtime_or_policy",
                    record_literals=record_literals,
                    validation_kind="coordinate_presence",
                )
    source_stats["residual_policy"] = {"matched_record_count": residual_matched, "stale_record_count": residual_stale}

    def attach_repair_hold(
        wave: str,
        source_kind: str,
        group: str,
        category: str,
        status: str,
        select: callable = lambda row: True,
    ) -> None:
        audit = audits[wave]
        matched = stale = 0
        for row in audit.rows:
            if not select(row):
                continue
            resource = resource_from_audit_row(row, audit.spec)
            record = record_from_coordinate(require_text(row, "coordinate", audit.spec.path))
            expected = require_text(row, audit.spec.target_record_hash_key, audit.spec.path)
            actual = record_hashes[resource].get(record)
            if actual != expected:
                stale += 1
                stale_rows.append(
                    stale_hold_row(
                        resource=resource,
                        record=record,
                        source=audit.spec.path,
                        source_kind=source_kind,
                        source_sha256=audit.spec.expected_file_sha256,
                        status=status,
                        category=category,
                        expected_record_sha256=expected,
                        observed_record_sha256=actual,
                        reason="pinned_repair_target_record_no_longer_matches_current",
                    )
                )
                continue
            matched += 1
            append_hold(
                holds,
                hold_groups,
                resource=resource,
                record=record,
                record_hash=actual,
                source=audit.spec.path,
                source_kind=source_kind,
                source_sha256=audit.spec.expected_file_sha256,
                status=status,
                category=category,
                group=group,
                record_literals=record_literals,
                validation_kind="record_hash",
            )
        source_stats[source_kind] = {"matched_record_count": matched, "stale_record_count": stale}

    # These are preserved as historical QA evidence only.  The source-free
    # ledger cannot infer whether a human later completed an in-game check.
    attach_repair_hold(
        "wave7",
        "wave7_runtime_visual_qa",
        "wave7_runtime_visual_qa",
        "wave7_runtime_visual_qa",
        "runtime_visual_qa_required",
        select=lambda row: row.get("runtime_visual_qa_required") is True,
    )
    attach_repair_hold(
        "wave8",
        "wave8_historical_real_game_qa",
        "wave8_historical_real_game_qa",
        "wave8_static_repair",
        "real_game_qa_required_before_release",
    )
    attach_repair_hold(
        "wave9",
        "wave9_historical_real_game_qa",
        "wave9_historical_real_game_qa",
        "wave9_static_repair",
        "real_game_qa_required_before_release",
    )

    if source_stats != EXPECTED_HOLD_SOURCE_RECORD_COUNTS:
        raise LedgerError(f"hold source validation counts differ: {source_stats}")
    group_sets: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for resource, coordinates in hold_groups.items():
        for coordinate, groups in coordinates.items():
            for group in groups:
                group_sets[group].add((resource, coordinate))
    group_counts = {group: len(group_sets[group]) for group in sorted(group_sets)}
    if group_counts != EXPECTED_CURRENT_HOLD_GROUP_COUNTS:
        raise LedgerError(f"hold group literal counts differ: {group_counts}")
    current_hold_coordinates = {
        (resource, coordinate)
        for resource, coordinates in holds.items()
        for coordinate, values in coordinates.items()
        if values
    }
    if len(current_hold_coordinates) != EXPECTED_CURRENT_HOLD_LITERAL_COUNT:
        raise LedgerError(f"current hold literal count differs: {len(current_hold_coordinates)}")
    if len(stale_rows) != EXPECTED_STALE_LEGACY_HOLD_RECORD_COUNT:
        raise LedgerError(f"stale legacy hold record count differs: {len(stale_rows)}")
    return holds, {
        "current_hold_group_literal_counts": group_counts,
        "current_hold_literal_count": len(current_hold_coordinates),
        "source_record_validation": source_stats,
        "stale_legacy_hold_record_count": len(stale_rows),
    }, sorted(stale_rows, key=lambda row: (row["source_kind"], row["resource"], record_key(row["record"])))


def is_prior_review(disposition: object) -> bool:
    return isinstance(disposition, str) and (disposition.startswith("review_") or disposition.startswith("hold_"))


def scope() -> dict[str, bool]:
    return {
        "current_steam_read": True,
        "historic_korean_read": False,
        "pristine_pc_japanese_read": True,
        "semantic_completion": False,
        "steam_game_resource_written": False,
        "switch_korean_read": False,
    }


def build(steam_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    steam_root = steam_root.resolve(strict=True)
    profile_hashes = validate_current_profile(steam_root)
    coverage_rows, coverage_summary = load_coverage_rows()
    repair_audits = load_repair_audits()

    live_literals: dict[str, dict[str, str]] = {}
    pristine_literals: dict[str, dict[str, str]] = {}
    record_hashes: dict[str, dict[str, str]] = {}
    record_literals: dict[str, dict[str, tuple[str, ...]]] = {}
    resources_summary: dict[str, Any] = {}

    for spec in SPECS:
        live_path = require_file(steam_root / spec.relative, f"current Steam {spec.name}")
        pristine = require_file(pristine_path(spec, steam_root), f"pristine PC Japanese {spec.name}")
        expected_live_sha = CURRENT_WAVE14_PROFILE_SHA256[spec.relative.as_posix()]
        if sha256_file(live_path) != expected_live_sha:
            raise LedgerError(f"current Steam {spec.name} differs from Wave 14 profile")
        if sha256_file(pristine) != spec.expected_pristine_sha256:
            raise LedgerError(f"pristine PC Japanese {spec.name} hash drift")
        current, records, literals_by_record = parse_msggame(live_path)
        original, _ignored_records, _ignored_literals = parse_msggame(pristine)
        if not set(current).issubset(original):
            missing = sorted(set(current).difference(original), key=coordinate_key)
            raise LedgerError(f"current {spec.name} has literals absent from pristine PC JP: {missing[:5]!r}")
        if len(current) != EXPECTED_CURRENT_COUNTS[spec.name]:
            raise LedgerError(f"current literal count differs for {spec.name}: {len(current)}")
        retired = set(coverage_rows[spec.name]).difference(current)
        if retired != EXPECTED_RETIRED_PRIOR_COORDINATES[spec.name]:
            raise LedgerError(f"retired coordinate set differs for {spec.name}")
        context_hashes: dict[str, str] = {}
        for language, relative in spec.context_relatives.items():
            actual = sha256_file(require_file(steam_root / relative, f"PC {language} context {spec.name}"))
            if actual != spec.expected_context_sha256[language]:
                raise LedgerError(f"PC {language} context hash drift for {spec.name}")
            context_hashes[language] = actual
        live_literals[spec.name] = current
        pristine_literals[spec.name] = original
        record_hashes[spec.name] = records
        record_literals[spec.name] = literals_by_record
        resources_summary[spec.name] = {
            "current_literal_coordinate_count": len(current),
            "current_steam_packed_sha256": expected_live_sha,
            "current_steam_relative_path": spec.relative.as_posix(),
            "pc_context_packed_sha256": context_hashes,
            "pristine_pc_jp_packed_sha256": spec.expected_pristine_sha256,
            "prior_coverage_coordinate_count": len(coverage_rows[spec.name]),
            "retired_prior_literal_coordinate_count": len(retired),
        }

    repair_evidence, repair_summary = load_current_repair_evidence(
        repair_audits, coverage_rows, live_literals, record_hashes, record_literals
    )
    holds, hold_summary, stale_rows = load_current_hold_evidence(repair_audits, record_hashes, record_literals)

    rows: list[dict[str, Any]] = []
    retired_rows: list[dict[str, Any]] = []
    hold_rows: list[dict[str, Any]] = []
    classification_counts: Counter[str] = Counter()
    semantic_status_counts: Counter[str] = Counter()
    prior_hash_match_count = prior_hash_different_count = 0
    verified_repair_literal_count = legacy_lineage_different_count = 0

    for spec in SPECS:
        for coordinate in sorted(live_literals[spec.name], key=coordinate_key):
            prior = coverage_rows[spec.name][coordinate]
            source_free_evidence = prior["source_free_evidence"]
            current_hash = live_literals[spec.name][coordinate]
            prior_hash = source_free_evidence["current_ko_utf16le_sha256"]
            current_matches_prior = current_hash == prior_hash
            prior_disposition = prior.get("input_disposition")
            prior_semantic_status = prior.get("input_semantic_status")
            current_repair_evidence = sorted(
                repair_evidence[spec.name].get(coordinate, []), key=lambda value: (value["wave"], value["record"])
            )
            current_hold_evidence = sorted(
                holds[spec.name].get(coordinate, []), key=lambda value: (value["source_kind"], value["record"], value["status"])
            )
            if current_matches_prior:
                prior_hash_match_count += 1
            else:
                prior_hash_different_count += 1
            if current_repair_evidence:
                if current_matches_prior or len(current_repair_evidence) != 1:
                    raise LedgerError(f"verified repair literal relation differs: {spec.name}:{coordinate}")
                wave = current_repair_evidence[0]["wave"]
                classification = f"verified_current_{wave}_repair"
                semantic_status = f"pinned_{wave}_repair_no_global_semantic_completion"
                verified_repair_literal_count += 1
            elif not current_matches_prior:
                legacy_lineage_different_count += 1
                classification = (
                    "profile_changed_prior_review_requires_rebase"
                    if is_prior_review(prior_disposition)
                    else "known_pc_only_profile_lineage_change"
                )
                semantic_status = "legacy_profile_lineage_change_no_global_semantic_completion"
            elif current_hold_evidence:
                classification = "known_current_explicit_hold_evidence"
                semantic_status = "current_hold_evidence_outcome_not_semantically_complete"
            elif is_prior_review(prior_disposition):
                classification = "known_prior_review_carried_forward"
                semantic_status = (
                    str(prior_semantic_status)
                    if isinstance(prior_semantic_status, str)
                    else "prior_review_no_global_semantic_completion"
                )
            else:
                classification = "known_prior_pc_only_screened_unchanged"
                semantic_status = (
                    str(prior_semantic_status)
                    if isinstance(prior_semantic_status, str)
                    else "prior_pc_only_screened_no_semantic_completion"
                )
            classification_counts[classification] += 1
            semantic_status_counts[semantic_status] += 1
            row = {
                "schema": SCHEMA,
                "classification": classification,
                "coordinate": coordinate,
                "current_hash_matches_prior_pc_only_ledger": current_matches_prior,
                "current_hold_evidence": current_hold_evidence,
                "current_ko_utf16le_sha256": current_hash,
                "current_profile_packed_sha256": CURRENT_WAVE14_PROFILE_SHA256[spec.relative.as_posix()],
                "current_repair_evidence": current_repair_evidence,
                "prior_pc_only_ledger": {
                    "coverage_input": prior.get("coverage_input"),
                    "input_disposition": prior_disposition,
                    "input_semantic_status": prior_semantic_status,
                    "prior_current_ko_utf16le_sha256": prior_hash,
                },
                "pristine_pc_jp_utf16le_sha256": pristine_literals[spec.name][coordinate],
                "relative_path": spec.relative.as_posix(),
                "resource": spec.name,
                "scope": scope(),
                "semantic_status": semantic_status,
            }
            rows.append(row)
            if current_hold_evidence:
                hold_rows.append(
                    {
                        "schema": HOLD_SCHEMA,
                        "coordinate": coordinate,
                        "current_hold_evidence": current_hold_evidence,
                        "current_ko_utf16le_sha256": current_hash,
                        "relative_path": spec.relative.as_posix(),
                        "resource": spec.name,
                        "scope": scope(),
                    }
                )
        for coordinate in sorted(EXPECTED_RETIRED_PRIOR_COORDINATES[spec.name], key=coordinate_key):
            prior = coverage_rows[spec.name][coordinate]
            evidence = prior["source_free_evidence"]
            retired_rows.append(
                {
                    "schema": SCHEMA,
                    "classification": "known_pc_only_profile_retired_literal_coordinate",
                    "coordinate": coordinate,
                    "current_literal_present": False,
                    "current_profile_packed_sha256": CURRENT_WAVE14_PROFILE_SHA256[spec.relative.as_posix()],
                    "prior_pc_only_ledger": {
                        "coverage_input": prior.get("coverage_input"),
                        "input_disposition": prior.get("input_disposition"),
                        "input_semantic_status": prior.get("input_semantic_status"),
                        "prior_current_ko_utf16le_sha256": evidence["current_ko_utf16le_sha256"],
                    },
                    "pristine_pc_jp_utf16le_sha256": pristine_literals[spec.name][coordinate],
                    "relative_path": spec.relative.as_posix(),
                    "resource": spec.name,
                    "retirement_reason": "current PC-only profile coalesced an earlier literal slot during static dialogue rewrite",
                    "scope": scope(),
                    "semantic_status": "retired_literal_slot_no_current_text_to_adjudicate",
                }
            )

    if len(rows) != EXPECTED_CURRENT_LITERAL_COUNT:
        raise LedgerError(f"current ledger total differs: {len(rows)}")
    if len(retired_rows) != EXPECTED_RETIRED_LITERAL_COUNT:
        raise LedgerError(f"retired ledger total differs: {len(retired_rows)}")
    if prior_hash_match_count != EXPECTED_PRIOR_HASH_MATCH_COUNT or prior_hash_different_count != EXPECTED_PRIOR_HASH_DIFFERENT_COUNT:
        raise LedgerError(
            f"prior hash split differs: matches={prior_hash_match_count}, differs={prior_hash_different_count}"
        )
    if verified_repair_literal_count != EXPECTED_REPAIR_LITERAL_COUNT:
        raise LedgerError(f"verified repair literal count differs in ledger: {verified_repair_literal_count}")
    if legacy_lineage_different_count != EXPECTED_LEGACY_LINEAGE_DIFFERENT_COUNT:
        raise LedgerError(f"legacy lineage different count differs: {legacy_lineage_different_count}")
    if len(hold_rows) != EXPECTED_CURRENT_HOLD_LITERAL_COUNT:
        raise LedgerError(f"current hold row count differs: {len(hold_rows)}")

    summary: dict[str, Any] = {
        "schema": SUMMARY_SCHEMA,
        "scope": "current Steam Base and PK msggame source-free reconciliation after Wave 14; record hashes and coordinate metadata only",
        "coverage_manifest": {
            "all_input_pc_only_provenance_checks_passed": True,
            "ledger": relative_path(COVERAGE_LEDGER),
            "ledger_sha256": sha256_file(COVERAGE_LEDGER),
            "summary": relative_path(COVERAGE_SUMMARY),
            "summary_sha256": sha256_file(COVERAGE_SUMMARY),
        },
        "current_explicit_hold_evidence": hold_summary,
        "current_literal_coordinate_count": len(rows),
        "current_literal_resource_coordinate_counts": EXPECTED_CURRENT_COUNTS,
        "current_profile": {
            "profile_name": "wave14_installed_11_file_profile",
            "sha256": profile_hashes,
        },
        "current_classification_counts": dict(sorted(classification_counts.items())),
        "prior_coverage_coordinate_count": EXPECTED_PRIOR_LITERAL_COUNT,
        "prior_coverage_resource_coordinate_counts": EXPECTED_PRIOR_COUNTS,
        "prior_hash_relation": {
            "current_hash_matches_prior_count": prior_hash_match_count,
            "current_hash_differs_prior_count": prior_hash_different_count,
            "verified_wave7_to_wave14_repair_literal_count": verified_repair_literal_count,
            "legacy_profile_lineage_different_literal_count": legacy_lineage_different_count,
        },
        "repair_record_validation": repair_summary,
        "retired_prior_literal_coordinate_count": len(retired_rows),
        "semantic_completion": False,
        "semantic_completion_reason": (
            "Coordinate coverage, record-target validation, and PC-only provenance do not prove "
            "context-sensitive Korean quality or real-game rendering for every dialogue."
        ),
        "semantic_status_counts": dict(sorted(semantic_status_counts.items())),
        "source_text_emitted": False,
        "steam_installation_written": False,
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "stale_legacy_hold_record_count": len(stale_rows),
        "deterministic_serialization": "ASCII JSONL sorted by resource and numeric literal coordinate; sorted JSON keys",
    }
    return rows, retired_rows, hold_rows, stale_rows, summary


def output_paths(output_root: Path) -> dict[str, Path]:
    root = require_output_root(output_root)
    return {
        "ledger": root / "current_pc_dialogue_coordinate_ledger.source_free.v2.jsonl",
        "retired": root / "retired_prior_literal_coordinates.source_free.v2.jsonl",
        "holds": root / "current_explicit_hold_evidence.source_free.v2.jsonl",
        "stale": root / "stale_legacy_hold_records.source_free.v2.jsonl",
        "summary": root / "summary.source_free.v2.json",
    }


def assert_source_free_bytes(label: str, payload: bytes) -> None:
    """Keep the public output structurally source-free and ASCII-only."""
    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError as exc:
        raise LedgerError(f"{label} output is not ASCII source-free JSON") from exc
    forbidden = ('"current_literals"', '"target_literals"', '"input_literals"', '"output_literals"', '"literal_text"')
    if any(token in text for token in forbidden):
        raise LedgerError(f"{label} output includes a forbidden literal-text field")


def validate_rows(
    rows: list[dict[str, Any]],
    retired_rows: list[dict[str, Any]],
    hold_rows: list[dict[str, Any]],
    stale_rows: list[dict[str, Any]],
    summary: Mapping[str, Any],
) -> None:
    by_resource: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("schema") != SCHEMA or row.get("resource") not in EXPECTED_CURRENT_COUNTS:
            raise LedgerError("ledger row schema/resource differs")
        coordinate = row.get("coordinate")
        if not isinstance(coordinate, str):
            raise LedgerError("ledger coordinate is invalid")
        coordinate_key(coordinate)
        row_scope = row.get("scope")
        if not isinstance(row_scope, dict) or row_scope.get("switch_korean_read") or row_scope.get("historic_korean_read") or row_scope.get("steam_game_resource_written"):
            raise LedgerError("ledger row scope is no longer PC-only/read-only")
        if row_scope.get("semantic_completion") is not False:
            raise LedgerError("ledger row claims semantic completion")
        by_resource[row["resource"]].append(row)
    for resource, expected in EXPECTED_CURRENT_COUNTS.items():
        coordinates = [row["coordinate"] for row in by_resource[resource]]
        if len(coordinates) != expected or len(coordinates) != len(set(coordinates)):
            raise LedgerError(f"ledger coordinate validation differs for {resource}")
    if len(retired_rows) != EXPECTED_RETIRED_LITERAL_COUNT:
        raise LedgerError("retired row count differs")
    if len(hold_rows) != EXPECTED_CURRENT_HOLD_LITERAL_COUNT:
        raise LedgerError("hold row count differs")
    if len(stale_rows) != EXPECTED_STALE_LEGACY_HOLD_RECORD_COUNT:
        raise LedgerError("stale hold row count differs")
    if summary.get("semantic_completion") is not False:
        raise LedgerError("summary claims semantic completion")
    if summary.get("current_literal_coordinate_count") != EXPECTED_CURRENT_LITERAL_COUNT:
        raise LedgerError("summary current literal count differs")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--write", action="store_true", help="write deterministic source-free artifacts below KR_PATCH_WORK/tmp")
    parser.add_argument("--validate", action="store_true", help="compare deterministic artifacts already under the output root")
    args = parser.parse_args()

    rows, retired_rows, hold_rows, stale_rows, summary = build(args.steam_root)
    validate_rows(rows, retired_rows, hold_rows, stale_rows, summary)
    payloads = {
        "ledger": canonical_jsonl(rows),
        "retired": canonical_jsonl(retired_rows),
        "holds": canonical_jsonl(hold_rows),
        "stale": canonical_jsonl(stale_rows),
        "summary": canonical_json(summary),
    }
    for label, payload in payloads.items():
        assert_source_free_bytes(label, payload)
    paths = output_paths(args.output_root)
    if args.write:
        for key, path in paths.items():
            atomic_write(path, payloads[key])
    if args.validate:
        for key, path in paths.items():
            if not path.is_file():
                raise LedgerError(f"expected deterministic {key} output is absent: {path}")
            if path.read_bytes() != payloads[key]:
                raise LedgerError(f"deterministic {key} output differs: {path}")
    print(
        json.dumps(
            {
                "current_explicit_hold_literal_count": summary["current_explicit_hold_evidence"]["current_hold_literal_count"],
                "current_literal_coordinate_count": summary["current_literal_coordinate_count"],
                "prior_hash_relation": summary["prior_hash_relation"],
                "retired_prior_literal_coordinate_count": summary["retired_prior_literal_coordinate_count"],
                "semantic_completion": False,
                "stale_legacy_hold_record_count": summary["stale_legacy_hold_record_count"],
                "steam_installation_written": False,
                "switch_korean_translation_used": False,
                "verified_repair_record_count": summary["repair_record_validation"]["record_count"],
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
