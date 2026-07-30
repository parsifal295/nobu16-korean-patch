#!/usr/bin/env python3
"""Build the PK 0:2546-2552 / selector 0:1066 full caller closure.

The two translation-bearing review handoffs and the frozen predecessor
checkpoint remain below ``tmp``.  Only source-free coverage/promotion reports
are tracked.  The live Steam installation is read-only.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
CALLER_BUILDER_PATH = (
    WORKSTREAM / "build_pk_bound_terminal_caller_full_closure_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_bound_terminal_caller_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_bound_terminal_caller_checkpoint.source_free.v1.json"
)
HANDOFF_000_151_PATH = (
    DIALOGUE_TMP / "family2546_ord000_151_analysis.private.v1.json"
)
HANDOFF_152_303_PATH = (
    DIALOGUE_TMP / "family2546_ord152_303_analysis.private.v1.json"
)
RESIDUAL_LEDGER_PATH = (
    DIALOGUE_TMP / "family2546_full_ledger.private.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_2546_full_caller_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_2546_full_caller_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / (
        "pk_bound_terminal_2546_full_caller_closure_"
        "integrated_decisions.private.v1.jsonl"
    )
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / (
        "pk_bound_terminal_2546_full_caller_closure_"
        "evidence.private.v1.jsonl"
    )
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-full-caller-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-full-caller-closure-promotion.v1"
)
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-full-caller-closure-evidence-row.v1"
)
METHOD = "reversed_vm_pk_bound_terminal_2546_full_caller_closure"
UPDATE_ACTION_FIELD = "bound_terminal_2546_full_caller_update_action"

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "54B4255C29F256B84E1CA4EE8A9B5D21FE254100A2A71CA28657F7EF6EB34E45"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "B537FF47B803667E1A40527431DC9764308361DCDE8CF2464AF6A77D8DE76AB6"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_577
EXPECTED_HANDOFF_000_151_SHA256 = (
    "CD6A535AFA08678924EA6296FAFAFE192BF70D78F96F616BAC09B741A7CCBEA9"
)
EXPECTED_HANDOFF_152_303_SHA256 = (
    "0E83FCEC00A894B444899B251CABE8F6E0506FE987C29025DB26EEA804A9350B"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "498A9A19FA33B57789C6FBF3732DA61967FEDE8055F034F68E43E628C16ED74F"
)
EXPECTED_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_OVERRIDE_ROWS = 216
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "212DEF7EE8B508CEA406FF223BADE5E2DC0DC7D7B1EE5255AD828764B6A866B5"
)
EXPECTED_OVERRIDE_MAP_SHA256 = (
    "C877CB29B74391257DE579F1AAFF6B9C1F5524DB6367AF18C3AE5DD5E5D5448A"
)
EXPECTED_CALL_SITES = 304
EXPECTED_REVIEWED_ACCEPTED_SITES = 229
EXPECTED_CARRY_SITES = 45
EXPECTED_BLOCKER_SITES = 30
EXPECTED_PROMOTION_ROWS = 364
EXPECTED_PROMOTION_ROOTS = 189
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "667E25717B1F8CB5E8AD4C26DC4615CD2D52B38D69529BCB9E62AB562FD23320"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "058875D11217722C73F6D37E48B8D4DB51248C006BF1EE960308AE4E33D331A7"
)
EXPECTED_RENEWAL_ROWS = 292
EXPECTED_RENEWAL_ROOTS = 192
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "203B38F2EFD645D710467F7663ECE6B65EDAB32D1BF376B17C092BCFE898FA5F"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "5BC0596B3682DEE1E4A3CCBBC85A77808CD2498585673ABFCDB483B7D25B9AE6"
)
EXPECTED_REJECTED_ROWS = 74
EXPECTED_REJECTED_ROOTS = 28
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "5D59CBD547FBFE1E27D8284A12698768923FDD74C3C9F0B8021A39E6252B318D"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "B2A2116CEA91982E5C1FDBC2D882D0AD55F9B80C488CC379E016E849E0870873"
)
EXPECTED_DECISION_ROWS = 656
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "F176E7D99EC74F07AE6041B29EC5CCB3DB36A356B7600CF291B2B61B51ABC349"
)
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "4042EE2A22505B34CE944521C45AA73075053518E2B5ABE3E6C35C25211FC4B5"
)
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "05EDD038E66467C40A143E1595B70AEB45CB7EE6E0270FC38C5F8353B389303C"
)
EXPECTED_PENDING_AFTER = 8_213
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 279,
    "translation_override_and_runtime_promotion": 85,
    "translation_override_and_verification_renewal": 131,
    "verification_renewal": 161,
}
EXPECTED_TERMINALS = tuple(f"0:{record_id}:0" for record_id in range(2546, 2553))
SELECTOR = 1066

# Frozen after an independently reproducible build.
EXPECTED_AUDIT_FILE_SHA256: str | None = (
    "567FE83E1BD6ED9B4A8D7C1E303CC4760A5DCFB3061C622C55F0565B9960AF57"
)
EXPECTED_PROMOTION_FILE_SHA256: str | None = (
    "58F734F65A6D0C48BB245ED0E515A05EF51F844D53D8FA50ECC8A84DEAB4005B"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "39652CFB6923E43D30D0CF422642C3B996DDC0495E620EFCE1B3B310E5D7D82F"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "3D5AA831D7F891DEABE0E79667416F96C12366A968F1E662F4519FC1C4025DD6"
)
EXPECTED_RESIDUAL_LEDGER_SHA256: str | None = (
    "90987EC88A5AA06DA1BAB681E84D59ECD1E8090EE1AFCD472A0A5D646C3399EE"
)


class ClosureError(ValueError):
    """Raised when a frozen closure contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ClosureError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(
        spec is not None and spec.loader is not None,
        f"cannot import {path}",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CALLER = load_module(
    CALLER_BUILDER_PATH,
    "pk_bound_terminal_2546_full_caller_predecessor_helpers_v1",
)
HONORIFIC = CALLER.HONORIFIC
CROSS = CALLER.CROSS
BASE_AUDIT = CALLER.BASE_AUDIT
ENGINE = CALLER.ENGINE
LIVE_STEAM_BASE = CALLER.LIVE_STEAM_BASE
LIVE_STEAM_PK = CALLER.LIVE_STEAM_PK


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(canonical_json(row) for row in rows)


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def parse_coordinate(value: str) -> tuple[int, int, int]:
    return BASE_AUDIT.parse_literal_coordinate(value)


def coordinate_digest(values: Iterable[str]) -> str:
    return HONORIFIC.coordinate_digest(values)


def record_digest(values: Iterable[tuple[int, int]]) -> str:
    return HONORIFIC.record_digest(values)


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    return HONORIFIC.row_sort_key(row)


def load_utf8_json_exact(
    path: Path,
    expected_sha256: str,
    expected_schema: str,
) -> dict[str, Any]:
    raw = path.read_bytes()
    require(
        sha256_bytes(raw) == expected_sha256,
        f"private handoff hash drifted: {path}",
    )
    require(not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM rejected: {path}")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ClosureError(f"private handoff is not strict UTF-8: {path}") from exc
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ClosureError(f"private handoff JSON invalid: {path}") from exc
    require(isinstance(value, dict), f"private handoff must be an object: {path}")
    require(
        value.get("schema") == expected_schema,
        f"private handoff schema drifted: {path}",
    )
    return value


def validate_private_handoff(
    value: Mapping[str, Any],
    *,
    baseline_sha256: str,
) -> None:
    privacy = value.get("privacy", {})
    scope = value.get("scope", {})
    require(
        privacy.get("classification") == "private"
        and privacy.get("public") is False
        and privacy.get("shared") is False
        and privacy.get("tracked") is False,
        "private handoff privacy contract drifted",
    )
    require(
        scope.get("resource") == "pk_msggame"
        and scope.get("selector_coordinate") == "0:1066:0"
        and tuple(scope.get("terminal_coordinates", ())) == EXPECTED_TERMINALS
        and scope.get("baseline_candidate_sha256") == baseline_sha256,
        "private handoff scope drifted",
    )


def load_handoffs() -> tuple[dict[str, Any], dict[str, Any]]:
    first = load_utf8_json_exact(
        HANDOFF_000_151_PATH,
        EXPECTED_HANDOFF_000_151_SHA256,
        "family2546_ord000_151_analysis.private.v1",
    )
    second = load_utf8_json_exact(
        HANDOFF_152_303_PATH,
        EXPECTED_HANDOFF_152_303_SHA256,
        "family2546_ord152_303_analysis.private.v1",
    )
    validate_private_handoff(
        first,
        baseline_sha256=EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
    )
    validate_private_handoff(
        second,
        baseline_sha256=(
            "902CD3A1372BC19ABCA846C6A9F43195085C0782994ECFCE8A8353B2F9E0A628"
        ),
    )
    union = first.get("union", {})
    integrity = union.get("integrity_assertions", {})
    proof = second.get("proof", {})
    require(
        union.get("counts", {}).get("accepted") == 89
        and union.get("counts", {}).get("rewrite") == 87
        and union.get("counts", {}).get("keep") == 2
        and union.get("counts", {}).get("reject") == 18
        and all(integrity.values())
        and second.get("counts", {}).get("accepted") == 140
        and second.get("counts", {}).get("rejected") == 12
        and second.get("counts", {}).get("final_exact_overrides") == 129
        and proof.get("combined_rebase", {}).get("failures") == 0
        and proof.get("unicode_integrity", {}).get(
            "all_129_values_roundtrip_utf8"
        )
        is True
        and second.get("scope", {}).get("steam_write_performed") is False,
        "private handoff proof assertions drifted",
    )
    require(
        proof.get("bindings", {}).get("final_candidate_sha256")
        == "45F514FCD77457201F38B3741FB2ECD56FA72DB8DFA65D65204D9ADA5E74964C",
        "corrected second handoff candidate binding drifted",
    )
    return first, second


def load_residual_ledger() -> dict[str, Any]:
    require(
        EXPECTED_RESIDUAL_LEDGER_SHA256 is not None,
        "residual ledger hash has not been frozen",
    )
    ledger = load_utf8_json_exact(
        RESIDUAL_LEDGER_PATH,
        EXPECTED_RESIDUAL_LEDGER_SHA256,
        "nobu16.kr.family2546-full-ledger.private.v1",
    )
    privacy = ledger.get("privacy", {})
    scope = ledger.get("scope", {})
    counts = ledger.get("counts", {})
    digests = ledger.get("digests", {})
    require(
        privacy.get("classification") == "private"
        and privacy.get("public") is False
        and privacy.get("contains_translation_bodies") is False
        and privacy.get("shared_integration_mutated") is False,
        "residual ledger privacy contract drifted",
    )
    require(
        scope.get("resource") == "pk_msggame"
        and scope.get("selector_coordinate") == "0:1066:0"
        and tuple(scope.get("terminal_coordinates", ())) == EXPECTED_TERMINALS
        and scope.get("selector_site_counts", {}).get("1066")
        == EXPECTED_CALL_SITES,
        "residual ledger scope drifted",
    )
    require(
        counts.get("candidate_affected_graph_roots") == 408
        and counts.get("source_affected_graph_roots") == 465
        and counts.get("candidate_affected_pending_rows") == 438
        and counts.get("candidate_affected_pending_roots") == 217
        and counts.get("promotion_rows") == EXPECTED_PROMOTION_ROWS
        and counts.get("promotion_roots") == EXPECTED_PROMOTION_ROOTS
        and counts.get("verified_renewal_rows") == EXPECTED_RENEWAL_ROWS
        and counts.get("verified_renewal_roots") == EXPECTED_RENEWAL_ROOTS
        and counts.get("rejected_pending_rows") == EXPECTED_REJECTED_ROWS
        and counts.get("rejected_pending_roots") == EXPECTED_REJECTED_ROOTS
        and counts.get("translation_override_rows") == EXPECTED_OVERRIDE_ROWS
        and counts.get("decision_rows") == EXPECTED_DECISION_ROWS
        and counts.get("evidence_rows") == EXPECTED_DECISION_ROWS
        and counts.get("ledger_pending_before")
        == EXPECTED_PREDECESSOR_PENDING
        and counts.get("ledger_pending_after") == EXPECTED_PENDING_AFTER
        and counts.get("action_rows") == EXPECTED_ACTION_COUNTS,
        "residual ledger counts drifted",
    )
    require(
        digests.get("candidate_blob_sha256") == EXPECTED_CANDIDATE_SHA256
        and digests.get("post_caller_candidate_blob_sha256")
        == EXPECTED_PREDECESSOR_CANDIDATE_SHA256
        and digests.get("candidate_affected_root_sha256")
        == EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256
        and digests.get("source_affected_root_sha256")
        == EXPECTED_SOURCE_AFFECTED_ROOT_SHA256
        and digests.get("decision_evidence_delta_coordinate_sha256")
        == EXPECTED_DECISION_COORDINATE_SHA256
        and digests.get("exact_override_coordinate_sha256")
        == EXPECTED_OVERRIDE_COORDINATE_SHA256
        and digests.get("exact_override_map_canonical_utf8_sha256")
        == EXPECTED_OVERRIDE_MAP_SHA256
        and all(ledger.get("assertions", {}).values()),
        "residual ledger digest/assertion contract drifted",
    )
    return ledger


def load_predecessor() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    require(
        sha256_file(PREDECESSOR_PRIVATE_PATH)
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        "frozen post-caller predecessor checkpoint hash drifted",
    )
    require(
        sha256_file(PREDECESSOR_PUBLIC_PATH)
        == EXPECTED_PREDECESSOR_PUBLIC_SHA256,
        "source-free predecessor checkpoint report hash drifted",
    )
    report = json.loads(PREDECESSOR_PUBLIC_PATH.read_text(encoding="utf-8"))
    result = report.get("result", {})
    require(
        report.get("status") == "PASS"
        and result.get("semantic_review_approved") == EXPECTED_PREDECESSOR_ROWS
        and result.get("runtime_review_pending") == EXPECTED_PREDECESSOR_PENDING
        and result.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and report.get("steam_write_performed") is False,
        "frozen post-caller predecessor report drifted",
    )
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    with PREDECESSOR_PRIVATE_PATH.open(
        "r",
        encoding="utf-8",
        errors="strict",
        newline="",
    ) as stream:
        for line_number, line in enumerate(stream, start=1):
            require(line.endswith("\n"), f"predecessor line {line_number} lacks LF")
            row = json.loads(line)
            key = (str(row["resource"]), str(row["coordinate"]))
            require(key not in rows, f"duplicate predecessor row: {key}")
            rows[key] = row
    pending = sum(row.get("runtime_review") == "pending" for row in rows.values())
    require(
        len(rows) == EXPECTED_PREDECESSOR_ROWS
        and pending == EXPECTED_PREDECESSOR_PENDING,
        "frozen post-caller predecessor ledger drifted",
    )
    return rows, report


def site_set(values: Any) -> set[str]:
    iterable = values.keys() if isinstance(values, Mapping) else values
    result: set[str] = set()
    for value in iterable:
        site = value.get("site") if isinstance(value, Mapping) else value
        require(isinstance(site, str), "review site entry drifted")
        result.add(site)
    return result


def site_root(site: str) -> tuple[int, int]:
    parts = site.split(":")
    require(len(parts) == 4, f"invalid call site: {site}")
    return int(parts[0]), int(parts[1])


def build_override_map(
    first: Mapping[str, Any],
    second: Mapping[str, Any],
) -> dict[str, str]:
    first_map = first["union"]["exact_maps"]["rewrite"]
    second_map = second["exact_final_override_map"]
    require(
        isinstance(first_map, dict) and isinstance(second_map, dict),
        "private exact override maps drifted",
    )
    require(not (set(first_map) & set(second_map)), "override maps overlap")
    overrides = {str(key): str(value) for key, value in first_map.items()}
    overrides.update(
        {str(key): str(value) for key, value in second_map.items()}
    )
    compact = json.dumps(
        overrides,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    require(
        len(overrides) == EXPECTED_OVERRIDE_ROWS
        and coordinate_digest(overrides) == EXPECTED_OVERRIDE_COORDINATE_SHA256
        and sha256_bytes(compact) == EXPECTED_OVERRIDE_MAP_SHA256,
        "combined exact override map drifted",
    )
    return overrides


def build_candidate(
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    overrides: Mapping[str, str],
) -> tuple[
    bytes,
    dict[tuple[int, int], Any],
    bytes,
    dict[tuple[int, int], Any],
]:
    replacements = {
        parse_coordinate(coordinate): str(row["translation"])
        for (resource, coordinate), row in predecessor_rows.items()
        if resource == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    predecessor_blob = BASE_AUDIT.rebuild_packed_with_literals(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        replacements,
    )
    predecessor_records = BASE_AUDIT.records_from_blob(predecessor_blob)
    replacements.update(
        {
            parse_coordinate(coordinate): text
            for coordinate, text in overrides.items()
        }
    )
    candidate_blob = BASE_AUDIT.rebuild_packed_with_literals(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        replacements,
    )
    candidate_records = BASE_AUDIT.records_from_blob(candidate_blob)
    require(
        sha256_bytes(predecessor_blob)
        == EXPECTED_PREDECESSOR_CANDIDATE_SHA256
        and sha256_bytes(candidate_blob) == EXPECTED_CANDIDATE_SHA256,
        "predecessor/final candidate packed hash drifted",
    )
    override_roots = {
        parse_coordinate(coordinate)[:2] for coordinate in overrides
    }
    HONORIFIC.changed_record_guard(
        predecessor_records=predecessor_records,
        candidate_records=candidate_records,
        expected_changed=override_roots,
    )
    return (
        predecessor_blob,
        predecessor_records,
        candidate_blob,
        candidate_records,
    )


def grouped_coordinates(
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    status: str,
) -> dict[tuple[int, int], list[str]]:
    result: defaultdict[tuple[int, int], list[str]] = defaultdict(list)
    for (resource, coordinate), row in predecessor_rows.items():
        if resource == "pk_msggame" and row.get("runtime_review") == status:
            result[parse_coordinate(coordinate)[:2]].append(coordinate)
    for coordinates in result.values():
        coordinates.sort(key=parse_coordinate)
    return dict(result)


def digest_summary(
    roots: set[tuple[int, int]],
    by_root: Mapping[tuple[int, int], Sequence[str]],
) -> dict[str, Any]:
    coordinates = [
        coordinate
        for root in sorted(roots)
        for coordinate in by_root[root]
    ]
    return {
        "rows": len(coordinates),
        "roots": len(roots),
        "coordinate_sha256": coordinate_digest(coordinates),
        "root_sha256": record_digest(roots),
    }


def build_analysis(
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    first: Mapping[str, Any],
    second: Mapping[str, Any],
    overrides: Mapping[str, str],
) -> dict[str, Any]:
    (
        predecessor_blob,
        predecessor_records,
        candidate_blob,
        candidate_records,
    ) = build_candidate(predecessor_rows, overrides)
    source_records = BASE_AUDIT.archive_records(
        BASE_AUDIT.DEFAULT_PK_PRISTINE
    )[0]
    current_records = BASE_AUDIT.records_from_blob(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes()
    )
    inputs = dataclasses.make_dataclass(
        "BoundTerminal2546CandidateInputs",
        [
            ("pk_source_records", object),
            ("pk_current_records", object),
            ("pk_candidate_records", object),
        ],
    )(source_records, current_records, candidate_records)
    profiles, candidate_edges = CROSS.RESIDUAL_AUDIT.build_record_profiles(
        inputs=inputs
    )
    source_edges = HONORIFIC.graph_edges(
        source_records,
        conservative_operand_scan=True,
    )
    terminal_roots = {(0, record_id) for record_id in range(2546, 2553)}
    candidate_affected = HONORIFIC.reverse_ancestors(
        edges=candidate_edges,
        targets=tuple(terminal_roots),
    )
    source_affected = HONORIFIC.reverse_ancestors(
        edges=source_edges,
        targets=tuple(terminal_roots),
    )
    pending_by_root = grouped_coordinates(predecessor_rows, "pending")
    verified_by_root = grouped_coordinates(predecessor_rows, "verified")
    candidate_pending_roots = set(pending_by_root) & candidate_affected
    renewal_roots = set(verified_by_root) & (
        candidate_affected | source_affected
    )

    full_sites = set(CALLER.call_sites(candidate_records, SELECTOR))
    accepted_sites = (
        site_set(first["union"]["site_lists"]["accepted"])
        | site_set(second["accepted_sites"])
    )
    blocker_sites = (
        site_set(first["union"]["site_lists"]["reject"])
        | site_set(second["rejected_sites"])
    )
    require(
        accepted_sites <= full_sites
        and blocker_sites <= full_sites
        and not (accepted_sites & blocker_sites),
        "reviewed selector site classification drifted",
    )
    carry_sites = full_sites - accepted_sites - blocker_sites
    require(
        len(full_sites) == EXPECTED_CALL_SITES
        and len(accepted_sites) == EXPECTED_REVIEWED_ACCEPTED_SITES
        and len(carry_sites) == EXPECTED_CARRY_SITES
        and len(blocker_sites) == EXPECTED_BLOCKER_SITES,
        "selector site coverage is not total",
    )
    blocker_roots = {site_root(site) for site in blocker_sites}
    rejected_roots = candidate_pending_roots & blocker_roots
    promotion_roots = candidate_pending_roots - rejected_roots
    promotion_summary = digest_summary(promotion_roots, pending_by_root)
    renewal_summary = digest_summary(renewal_roots, verified_by_root)
    rejected_summary = digest_summary(rejected_roots, pending_by_root)
    require(
        promotion_summary
        == {
            "rows": EXPECTED_PROMOTION_ROWS,
            "roots": EXPECTED_PROMOTION_ROOTS,
            "coordinate_sha256": EXPECTED_PROMOTION_COORDINATE_SHA256,
            "root_sha256": EXPECTED_PROMOTION_ROOT_SHA256,
        }
        and renewal_summary
        == {
            "rows": EXPECTED_RENEWAL_ROWS,
            "roots": EXPECTED_RENEWAL_ROOTS,
            "coordinate_sha256": EXPECTED_RENEWAL_COORDINATE_SHA256,
            "root_sha256": EXPECTED_RENEWAL_ROOT_SHA256,
        }
        and rejected_summary
        == {
            "rows": EXPECTED_REJECTED_ROWS,
            "roots": EXPECTED_REJECTED_ROOTS,
            "coordinate_sha256": EXPECTED_REJECTED_COORDINATE_SHA256,
            "root_sha256": EXPECTED_REJECTED_ROOT_SHA256,
        },
        "promotion/renewal/rejection universe drifted",
    )
    update_coordinates = {
        coordinate
        for root in promotion_roots
        for coordinate in pending_by_root[root]
    } | {
        coordinate
        for root in renewal_roots
        for coordinate in verified_by_root[root]
    }
    require(
        len(update_coordinates) == EXPECTED_DECISION_ROWS
        and coordinate_digest(update_coordinates)
        == EXPECTED_DECISION_COORDINATE_SHA256
        and set(overrides) <= update_coordinates,
        "decision/evidence delta universe drifted",
    )
    candidate_site_assembly_manifest = [
        [
            site,
            terminal[1],
            ENGINE.sha256_text(
                CALLER.adjacent_literals(candidate_records, site)[0]
                + BASE_AUDIT.parse_record_literals(candidate_records[terminal])[
                    0
                ].text
                + CALLER.adjacent_literals(candidate_records, site)[1]
            ),
        ]
        for site in sorted(full_sites)
        for terminal in sorted(terminal_roots)
    ]
    return {
        "predecessor_blob": predecessor_blob,
        "predecessor_records": predecessor_records,
        "candidate_blob": candidate_blob,
        "candidate_records": candidate_records,
        "profiles": profiles,
        "candidate_edges": candidate_edges,
        "source_edges": source_edges,
        "candidate_affected": candidate_affected,
        "source_affected": source_affected,
        "pending_by_root": pending_by_root,
        "verified_by_root": verified_by_root,
        "promotion_roots": promotion_roots,
        "renewal_roots": renewal_roots,
        "rejected_roots": rejected_roots,
        "promotion_summary": promotion_summary,
        "renewal_summary": renewal_summary,
        "rejected_summary": rejected_summary,
        "full_sites": full_sites,
        "accepted_sites": accepted_sites,
        "carry_sites": carry_sites,
        "blocker_sites": blocker_sites,
        "update_coordinates": update_coordinates,
        "candidate_site_assembly_rows": len(candidate_site_assembly_manifest),
        "candidate_site_assembly_sha256": canonical_sha256(
            candidate_site_assembly_manifest
        ),
    }


def coordinate_set_for_roots(
    roots: Iterable[tuple[int, int]],
    by_root: Mapping[tuple[int, int], Sequence[str]],
) -> set[str]:
    return {
        coordinate
        for root in roots
        for coordinate in by_root[root]
    }


def root_strings(roots: Iterable[tuple[int, int]]) -> set[str]:
    return {f"{root[0]}:{root[1]}" for root in roots}


def validate_residual_ledger_against_analysis(
    *,
    ledger: Mapping[str, Any],
    analysis: Mapping[str, Any],
    overrides: Mapping[str, str],
) -> None:
    promotion_coordinates = coordinate_set_for_roots(
        analysis["promotion_roots"],
        analysis["pending_by_root"],
    )
    renewal_coordinates = coordinate_set_for_roots(
        analysis["renewal_roots"],
        analysis["verified_by_root"],
    )
    rejected_coordinates = coordinate_set_for_roots(
        analysis["rejected_roots"],
        analysis["pending_by_root"],
    )
    expected_sets = {
        "promotion": (
            promotion_coordinates,
            analysis["promotion_roots"],
        ),
        "verified_renewal": (
            renewal_coordinates,
            analysis["renewal_roots"],
        ),
        "rejected_pending": (
            rejected_coordinates,
            analysis["rejected_roots"],
        ),
        "decision_evidence_delta": (
            analysis["update_coordinates"],
            {
                parse_coordinate(coordinate)[:2]
                for coordinate in analysis["update_coordinates"]
            },
        ),
        "ledger_translation_overrides": (
            set(overrides),
            {
                parse_coordinate(coordinate)[:2]
                for coordinate in overrides
            },
        ),
        "candidate_affected_pending": (
            coordinate_set_for_roots(
                (
                    set(analysis["pending_by_root"])
                    & analysis["candidate_affected"]
                ),
                analysis["pending_by_root"],
            ),
            (
                set(analysis["pending_by_root"])
                & analysis["candidate_affected"]
            ),
        ),
    }
    ledger_sets = ledger.get("sets", {})
    for name, (coordinates, roots) in expected_sets.items():
        entry = ledger_sets.get(name, {})
        require(
            set(entry.get("coordinates", ())) == coordinates
            and set(entry.get("roots", ())) == root_strings(roots),
            f"residual ledger exact set drifted: {name}",
        )
    graph = ledger.get("graph", {})
    require(
        set(graph.get("candidate_affected", {}).get("roots", ()))
        == root_strings(analysis["candidate_affected"])
        and set(graph.get("source_affected", {}).get("roots", ()))
        == root_strings(analysis["source_affected"]),
        "residual ledger graph root universe drifted",
    )
    expected_actions = {
        "runtime_promotion": promotion_coordinates - set(overrides),
        "translation_override_and_runtime_promotion":
        promotion_coordinates & set(overrides),
        "verification_renewal": renewal_coordinates - set(overrides),
        "translation_override_and_verification_renewal":
        renewal_coordinates & set(overrides),
    }
    require(
        all(
            set(ledger.get("actions", {}).get(action, {}).get(
                "coordinates",
                (),
            ))
            == coordinates
            for action, coordinates in expected_actions.items()
        ),
        "residual ledger exact action partition drifted",
    )


def build_audit(
    *,
    analysis: Mapping[str, Any],
    predecessor_report: Mapping[str, Any],
    residual_ledger: Mapping[str, Any],
) -> dict[str, Any]:
    proof_references = residual_ledger["proof_references"]
    report = {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "scope": {
            "selector": SELECTOR,
            "terminal_records": 7,
            "predecessor_rows": EXPECTED_PREDECESSOR_ROWS,
            "predecessor_pending_rows": EXPECTED_PREDECESSOR_PENDING,
            "exact_override_rows": EXPECTED_OVERRIDE_ROWS,
            "full_selector_sites": EXPECTED_CALL_SITES,
            "reviewed_accepted_sites": EXPECTED_REVIEWED_ACCEPTED_SITES,
            "proof_carry_sites": EXPECTED_CARRY_SITES,
            "blocker_sites": EXPECTED_BLOCKER_SITES,
            "runtime_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "runtime_promotion_roots": EXPECTED_PROMOTION_ROOTS,
            "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
            "verification_renewal_roots": EXPECTED_RENEWAL_ROOTS,
            "rejected_pending_rows": EXPECTED_REJECTED_ROWS,
            "rejected_pending_roots": EXPECTED_REJECTED_ROOTS,
            "post_layer_pending_rows": EXPECTED_PENDING_AFTER,
        },
        "proof": {
            "unknown_selector_sites": 0,
            "candidate_affected_records": len(
                analysis["candidate_affected"]
            ),
            "source_affected_records": len(analysis["source_affected"]),
            "candidate_site_assembly_rows": analysis[
                "candidate_site_assembly_rows"
            ],
            "candidate_site_assembly_sha256": analysis[
                "candidate_site_assembly_sha256"
            ],
            "independent_combined_candidate_full_assembly_rows": 4_004,
            "independent_combined_candidate_full_assembly_sha256":
            proof_references[
                "combined_candidate_full_4004_assembly_sha256"
            ],
            "independent_direct_transitive_proof_sha256":
            proof_references["direct_transitive_proof_sha256"],
            "automatic_space_inserted": False,
            "control_bytes_preserved": True,
            "all_accepted_register_branches_proven": True,
            "all_accepted_width_branches_nonexpanding": True,
            "source_and_candidate_graphs_audited": True,
            "all_affected_preexisting_verified_rows_renewed": True,
            "uncertain_roots_remain_rejected": True,
        },
        "guards": {
            "predecessor_private_sha256":
            EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "predecessor_public_sha256": EXPECTED_PREDECESSOR_PUBLIC_SHA256,
            "predecessor_report_payload_sha256": predecessor_report.get(
                "guards", {}
            ).get("report_payload_sha256"),
            "handoff_ord000_151_sha256":
            EXPECTED_HANDOFF_000_151_SHA256,
            "handoff_ord152_303_sha256":
            EXPECTED_HANDOFF_152_303_SHA256,
            "independent_residual_ledger_sha256":
            EXPECTED_RESIDUAL_LEDGER_SHA256,
            "independent_residual_ledger_payload_sha256":
            residual_ledger["guards"]["payload_canonical_sha256"],
            "predecessor_candidate_sha256":
            EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "override_coordinate_sha256":
            EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "override_map_canonical_sha256": EXPECTED_OVERRIDE_MAP_SHA256,
            "promotion_coordinate_sha256":
            EXPECTED_PROMOTION_COORDINATE_SHA256,
            "promotion_root_sha256": EXPECTED_PROMOTION_ROOT_SHA256,
            "renewal_coordinate_sha256": EXPECTED_RENEWAL_COORDINATE_SHA256,
            "renewal_root_sha256": EXPECTED_RENEWAL_ROOT_SHA256,
            "rejected_coordinate_sha256":
            EXPECTED_REJECTED_COORDINATE_SHA256,
            "rejected_root_sha256": EXPECTED_REJECTED_ROOT_SHA256,
            "decision_coordinate_sha256":
            EXPECTED_DECISION_COORDINATE_SHA256,
            "source_affected_root_sha256": record_digest(
                analysis["source_affected"]
            ),
            "candidate_affected_root_sha256": record_digest(
                analysis["candidate_affected"]
            ),
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_translation_map_keys": False,
            "private_handoffs_stay_below_tmp": True,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_dialogue_bodies": False,
        },
        "steam_write_performed": False,
    }
    return HONORIFIC.seal_report(report)


def build_updated_rows(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    overrides: Mapping[str, str],
    analysis: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    promotion_coordinates = {
        coordinate
        for root in analysis["promotion_roots"]
        for coordinate in analysis["pending_by_root"][root]
    }
    renewal_coordinates = {
        coordinate
        for root in analysis["renewal_roots"]
        for coordinate in analysis["verified_by_root"][root]
    }
    updated_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    for coordinate in sorted(
        analysis["update_coordinates"],
        key=parse_coordinate,
    ):
        predecessor = predecessor_rows[("pk_msggame", coordinate)]
        updated = copy.deepcopy(dict(predecessor))
        is_override = coordinate in overrides
        is_promotion = coordinate in promotion_coordinates
        if is_override:
            updated["translation"] = overrides[coordinate]
            CALLER.PREDECESSOR.repair_hard_risks(updated)
            updated["bound_terminal_2546_exact_override_evidence"] = {
                "schema":
                "nobu16.kr.pk-bound-terminal-2546-exact-override.v1",
                "private_handoff_hash_bound": True,
                "control_bytes_preserved": True,
                "automatic_space_inserted": False,
                "translation_utf16le_sha256": ENGINE.sha256_text(
                    str(updated["translation"])
                ),
            }
        if is_promotion:
            require(
                coordinate in promotion_coordinates
                and predecessor.get("runtime_review") == "pending",
                f"promotion predecessor drifted: {coordinate}",
            )
            updated["runtime_review"] = "verified"
            updated["scope_classification"] = "retranslated"
            updated["layout_review"] = "runtime_verified"
            action = (
                "translation_override_and_runtime_promotion"
                if is_override
                else "runtime_promotion"
            )
        else:
            require(
                coordinate in renewal_coordinates
                and predecessor.get("runtime_review") == "verified",
                f"renewal predecessor drifted: {coordinate}",
            )
            action = (
                "translation_override_and_verification_renewal"
                if is_override
                else "verification_renewal"
            )
        evidence = {
            "schema": EVIDENCE_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "status": "verified",
            "method": METHOD,
            "action": action,
            "translation_utf16le_sha256": ENGINE.sha256_text(
                str(updated["translation"])
            ),
            "predecessor_binding": {
                "row_sha256": canonical_sha256(predecessor),
                "checkpoint_sha256": EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            },
            "closure_binding": {
                "selector": SELECTOR,
                "terminal_coordinate_sha256": coordinate_digest(
                    EXPECTED_TERMINALS
                ),
                "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
                "decision_coordinate_sha256":
                EXPECTED_DECISION_COORDINATE_SHA256,
                "audit_report_file_sha256": audit_file_sha256,
                "audit_report_payload_sha256": audit["guards"][
                    "report_payload_sha256"
                ],
                "handoff_ord000_151_sha256":
                EXPECTED_HANDOFF_000_151_SHA256,
                "handoff_ord152_303_sha256":
                EXPECTED_HANDOFF_152_303_SHA256,
                "independent_residual_ledger_sha256":
                EXPECTED_RESIDUAL_LEDGER_SHA256,
            },
            "preexisting_verified_evidence_renewed": not is_promotion,
            "per_row_game_playback_required": False,
        }
        updated[UPDATE_ACTION_FIELD] = action
        updated["runtime_vm_verification"] = evidence
        updated_rows.append(updated)
        evidence_rows.append(evidence)
    updated_rows.sort(key=row_sort_key)
    evidence_rows.sort(key=lambda row: parse_coordinate(str(row["coordinate"])))
    actions = Counter(str(row["action"]) for row in evidence_rows)
    require(
        dict(actions) == EXPECTED_ACTION_COUNTS,
        "final action counts drifted",
    )
    return updated_rows, evidence_rows


def build_promotion(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    decision_content: str,
    evidence_content: str,
    evidence_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    actions = Counter(str(row["action"]) for row in evidence_rows)
    report = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "result": {
            "runtime_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "runtime_promotion_roots": EXPECTED_PROMOTION_ROOTS,
            "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
            "verification_renewal_roots": EXPECTED_RENEWAL_ROOTS,
            "rejected_pending_rows": EXPECTED_REJECTED_ROWS,
            "rejected_pending_roots": EXPECTED_REJECTED_ROOTS,
            "pending_rows_before": EXPECTED_PREDECESSOR_PENDING,
            "pending_rows_after": EXPECTED_PENDING_AFTER,
            "exact_override_rows": EXPECTED_OVERRIDE_ROWS,
            "decision_delta_rows": EXPECTED_DECISION_ROWS,
            "private_evidence_rows": EXPECTED_DECISION_ROWS,
            "private_decision_delta_sha256": sha256_bytes(
                decision_content.encode("utf-8")
            ),
            "private_evidence_sha256": sha256_bytes(
                evidence_content.encode("utf-8")
            ),
        },
        "action_counts": dict(sorted(actions.items())),
        "evidence": {
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
            "predecessor_checkpoint_sha256":
            EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "decision_coordinate_sha256":
            EXPECTED_DECISION_COORDINATE_SHA256,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_translation_map_keys": False,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_dialogue_bodies": False,
        },
        "steam_write_performed": False,
    }
    return HONORIFIC.seal_report(report)


SOURCE_TEXT_RE = re.compile(
    r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7a3]"
)
SENSITIVE_BODY_KEYS = {
    "translation",
    "source_text",
    "current_text",
    "candidate_text",
    "assembly",
    "exact_maps",
    "records",
    "site_lists",
    "exact_final_override_map",
    "accepted_sites",
    "rejected_sites",
}


def assert_source_free_report(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            require(
                key not in SENSITIVE_BODY_KEYS,
                f"tracked report contains a private body/map key: {key}",
            )
            assert_source_free_report(child)
    elif isinstance(value, list):
        for child in value:
            assert_source_free_report(child)
    elif isinstance(value, str):
        require(
            SOURCE_TEXT_RE.search(value) is None,
            "tracked report contains source/translated dialogue text",
        )


def contains_body_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            key in SENSITIVE_BODY_KEYS or contains_body_key(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(contains_body_key(child) for child in value)
    return False


def build_outputs() -> tuple[
    str,
    str,
    str,
    str,
    dict[str, Any],
    dict[str, Any],
]:
    steam_before = {
        "base": HONORIFIC.live_hash(LIVE_STEAM_BASE),
        "pk": HONORIFIC.live_hash(LIVE_STEAM_PK),
    }
    first, second = load_handoffs()
    residual_ledger = load_residual_ledger()
    predecessor_rows, predecessor_report = load_predecessor()
    overrides = build_override_map(first, second)
    analysis = build_analysis(
        predecessor_rows,
        first,
        second,
        overrides,
    )
    validate_residual_ledger_against_analysis(
        ledger=residual_ledger,
        analysis=analysis,
        overrides=overrides,
    )
    audit = build_audit(
        analysis=analysis,
        predecessor_report=predecessor_report,
        residual_ledger=residual_ledger,
    )
    HONORIFIC.validate_seal(audit)
    audit_content = canonical_json(audit)
    audit_file_sha256 = sha256_bytes(audit_content.encode("utf-8"))
    updated_rows, evidence_rows = build_updated_rows(
        predecessor_rows=predecessor_rows,
        overrides=overrides,
        analysis=analysis,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    decision_content = canonical_jsonl(updated_rows)
    evidence_content = canonical_jsonl(evidence_rows)
    promotion = build_promotion(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        decision_content=decision_content,
        evidence_content=evidence_content,
        evidence_rows=evidence_rows,
    )
    HONORIFIC.validate_seal(promotion)
    promotion_content = canonical_json(promotion)
    steam_after = {
        "base": HONORIFIC.live_hash(LIVE_STEAM_BASE),
        "pk": HONORIFIC.live_hash(LIVE_STEAM_PK),
    }
    require(
        steam_before == steam_after,
        "live Steam msggame changed during closure build",
    )
    return (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        {
            "predecessor_rows": predecessor_rows,
            "residual_ledger": residual_ledger,
            "overrides": overrides,
            "analysis": analysis,
            "updated_rows": updated_rows,
            "evidence_rows": evidence_rows,
            "promotion": promotion,
            "steam_before": steam_before,
            "steam_after": steam_after,
        },
    )


def validate_outputs(
    *,
    decision_content: str,
    evidence_content: str,
    audit_content: str,
    promotion_content: str,
    audit: Mapping[str, Any],
    bundle: Mapping[str, Any],
    require_frozen_hashes: bool = True,
) -> None:
    promotion = bundle["promotion"]
    require(
        decision_content == canonical_jsonl(bundle["updated_rows"])
        and evidence_content == canonical_jsonl(bundle["evidence_rows"])
        and audit_content == canonical_json(audit)
        and promotion_content == canonical_json(promotion),
        "serialized output drifted",
    )
    frozen = (
        EXPECTED_AUDIT_FILE_SHA256,
        EXPECTED_PROMOTION_FILE_SHA256,
        EXPECTED_DECISION_FILE_SHA256,
        EXPECTED_EVIDENCE_FILE_SHA256,
    )
    if require_frozen_hashes:
        require(all(frozen), "output hashes have not been frozen")
        actual = (
            sha256_bytes(audit_content.encode("utf-8")),
            sha256_bytes(promotion_content.encode("utf-8")),
            sha256_bytes(decision_content.encode("utf-8")),
            sha256_bytes(evidence_content.encode("utf-8")),
        )
        require(actual == frozen, f"frozen output file hash drifted: {actual}")
    HONORIFIC.validate_seal(audit)
    HONORIFIC.validate_seal(promotion)
    assert_source_free_report(audit)
    assert_source_free_report(promotion)
    require(
        not any(contains_body_key(row) for row in bundle["evidence_rows"]),
        "private evidence contains a dialogue body/map key",
    )
    updated_by_key = {
        ("pk_msggame", str(row["coordinate"])): row
        for row in bundle["updated_rows"]
    }
    require(
        len(updated_by_key) == EXPECTED_DECISION_ROWS
        and len(bundle["evidence_rows"]) == EXPECTED_DECISION_ROWS,
        "private output row count drifted",
    )
    merged = {
        key: copy.deepcopy(dict(row))
        for key, row in bundle["predecessor_rows"].items()
    }
    merged.update(updated_by_key)
    pending_after = sum(
        row.get("runtime_review") == "pending" for row in merged.values()
    )
    actions = Counter(
        str(row[UPDATE_ACTION_FIELD]) for row in bundle["updated_rows"]
    )
    require(
        pending_after == EXPECTED_PENDING_AFTER
        and dict(actions) == EXPECTED_ACTION_COUNTS
        and audit["scope"]["post_layer_pending_rows"]
        == EXPECTED_PENDING_AFTER
        and promotion["result"]["pending_rows_after"]
        == EXPECTED_PENDING_AFTER
        and audit.get("steam_write_performed") is False
        and promotion.get("steam_write_performed") is False
        and bundle["steam_before"] == bundle["steam_after"],
        "final closure result drifted",
    )
    for coordinate, text in bundle["overrides"].items():
        require(
            merged[("pk_msggame", coordinate)].get("translation") == text,
            f"merged private override drifted: {coordinate}",
        )


def validate_output_paths(args: argparse.Namespace) -> None:
    private_root = DIALOGUE_TMP.resolve(strict=False)
    steam_paths = {
        LIVE_STEAM_BASE.resolve(strict=False),
        LIVE_STEAM_PK.resolve(strict=False),
    }
    for path in (args.decision_output, args.evidence_output):
        resolved = path.resolve(strict=False)
        require(
            resolved not in steam_paths,
            "private output may not target live Steam",
        )
        require(
            private_root in resolved.parents,
            f"private output must remain below {private_root}",
        )
    require(
        args.audit_output.resolve(strict=False)
        == DEFAULT_AUDIT_OUTPUT.resolve(strict=False)
        and args.promotion_output.resolve(strict=False)
        == DEFAULT_PROMOTION_OUTPUT.resolve(strict=False),
        "public reports must use their fixed tracked source-free paths",
    )
    output_paths = {
        args.audit_output.resolve(strict=False),
        args.promotion_output.resolve(strict=False),
        args.decision_output.resolve(strict=False),
        args.evidence_output.resolve(strict=False),
    }
    require(len(output_paths) == 4, "closure output paths must be distinct")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT_OUTPUT)
    parser.add_argument(
        "--promotion-output",
        type=Path,
        default=DEFAULT_PROMOTION_OUTPUT,
    )
    parser.add_argument(
        "--decision-output",
        type=Path,
        default=DEFAULT_DECISION_OUTPUT,
    )
    parser.add_argument(
        "--evidence-output",
        type=Path,
        default=DEFAULT_EVIDENCE_OUTPUT,
    )
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    validate_output_paths(args)
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = build_outputs()
    validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
        require_frozen_hashes=True,
    )
    outputs = {
        args.audit_output: audit_content,
        args.promotion_output: promotion_content,
        args.decision_output: decision_content,
        args.evidence_output: evidence_content,
    }
    if args.check:
        for path, expected_content in outputs.items():
            require(path.is_file(), f"output missing: {path}")
            require(
                path.read_text(encoding="utf-8") == expected_content,
                f"output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    print(
        "PASS "
        f"overrides={EXPECTED_OVERRIDE_ROWS} "
        f"renewed={EXPECTED_RENEWAL_ROWS} "
        f"promoted={EXPECTED_PROMOTION_ROWS} "
        f"pending={EXPECTED_PENDING_AFTER} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
