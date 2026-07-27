#!/usr/bin/env python3
"""Build the independent selector-538 chunk-0 runtime closure layer.

The frozen post-selector-1066 checkpoint is the predecessor.  Dialogue bodies
and exact overrides remain private below ``tmp``; only source-free coverage
and promotion reports are tracked.  Shared integration code and Steam remain
read only.
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
REVIEW_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector538_chunk0_review_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_bound_terminal_2546_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_bound_terminal_2546_checkpoint.source_free.v1.json"
)
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family538_chunk0_analysis.private.v1.json"
)
REVIEW_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk0_review_proposal.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk0_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk0_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector538_chunk0_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector538_chunk0_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = "nobu16.kr.pk-selector538-chunk0-closure-coverage.v1"
PROMOTION_SCHEMA = "nobu16.kr.pk-selector538-chunk0-closure-promotion.v1"
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector538-chunk0-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = (
    "nobu16.kr.pk-selector538-chunk0-exact-override.v1"
)
METHOD = "reversed_vm_pk_selector538_chunk0_independent_closure"
UPDATE_ACTION_FIELD = "selector538_chunk0_update_action"
SELECTOR = 538
TERMINALS = tuple(range(1916, 1923))

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_HANDOFF_SHA256 = (
    "9A8CE09CCA100FCA9C5F9C148EDA38C043D8737218F2B4A11F3CDF2B7A7A92BF"
)
EXPECTED_REVIEW_PUBLIC_SHA256 = (
    "55D558207B2C26E9292BF1D204E81F29E124D72EFB8A029870B051EF1A953041"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_PENDING_AFTER = 8_148
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "583E53881F3099163F4E43E955C9363EDD597F82CA5B280BA96231A02A7673B4"
)
EXPECTED_REWRITE_ROWS = 33
EXPECTED_KEEP_ROWS = 2
EXPECTED_REJECTED_SITES = 30
EXPECTED_ACCEPTED_SITES = 35
EXPECTED_ACCEPTED_ASSEMBLIES = 245
EXPECTED_PROMOTION_ROWS = 65
EXPECTED_PROMOTION_ROOTS = 33
EXPECTED_REJECTED_PENDING_ROWS = 79
EXPECTED_REJECTED_ROOTS = 30
EXPECTED_REJECTED_PENDING_ROOTS = 27
EXPECTED_RENEWAL_ROWS = 420
EXPECTED_RENEWAL_ROOTS = 204
EXPECTED_DECISION_ROWS = 485
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 340
EXPECTED_SOURCE_AFFECTED_ROOTS = 405
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 48,
    "translation_override_and_runtime_promotion": 17,
    "translation_override_and_verification_renewal": 16,
    "verification_renewal": 404,
}

EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "7010E3B363FD8786E9B92D5F74C023DE47F96F0F9F4771F67E216D9A7E78E1A0"
)
EXPECTED_REWRITE_MAP_SHA256 = (
    "15BBE17FF1A6217E59719E34544A94D2391F5431E0CF1D5E6F1CDB23EB0EF47D"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "4A51986D3BE5FA499C62825052DD49AF39D350062E6B1685C85A6FF878583B4B"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "CB2B58B7D51FBB6B94025E47BC83F587B7549F0235BAE61D747264E152C29FE1"
)
EXPECTED_ACCEPTED_ROOT_SHA256 = (
    "6ABC8E35F2FD16D90DBECC7BA9A75E97B6DEDB862F4320488A50269F9ADB18F6"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "FCF5CAD181AA01E190336B0CD206E7D0F518AA5227BBB8693F05E4284A5E66BF"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "F1853D25D9F7BA6BF03F3BA613C8317675188A0E66AC558EE520FB56DF8CDA32"
)
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "42343A8FB2DCE2967AE8D3CB6373D5F3DFA8FD10C47D9387E01001DEA5AA7706"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "EF0B0A6AA45372F626DC4BF042231FB84A17664153164D8092E03D2ED44448CB"
)
EXPECTED_REJECTED_PENDING_ROOT_SHA256 = (
    "D7267569DFE96A3A838A979BAEF1A026F61709C6558932CC7B4E4D20A5AB005F"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "36058C249C73F5B42C0DC7426FA68879F4BDC515F40F9C50B6CFEC07C7FD4D59"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "65AB478BEE4C7F7102084ACDD7D1268C33F5FE93DDA278F69DEB7D59C502AE92"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "96AC18FD76014A9B6E52EA8CCB435C3FFFB218DB51B49B11BA50290E4DC0CA13"
)
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "8EF7B4ED0FF43FACAB1B4D393D0198CAE3E2C7057A9D29EF3F22E21DB176BC50"
)
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "1958C5972B0E9F1F7606DDD39F41FDCD05CE7A80AC1A7B63E357E3EA51358A64"
)

# Frozen after the independently reproducible outputs are generated.
EXPECTED_ACCEPTED_ASSEMBLY_SHA256: str | None = (
    "CE61D0BB690C5983A967981647352ED04528512D13753A48E09119E2461EBDBF"
)
EXPECTED_AUDIT_FILE_SHA256: str | None = (
    "BD5BCE9A82BCE6D38B5D4175253D8C0D025F464B9D6FA01ACBC0675B0841C43C"
)
EXPECTED_PROMOTION_FILE_SHA256: str | None = (
    "E08B23BAEB01C6EA3DA61AA9C2C85B6E5CBC981A646ED3DD494F90A7B230771D"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "6B002FF3565B1BAAED58064BA2351232B443A3B43350BD7BE9ADAFD1ED117BBF"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "AA38C99D83D42733BA8E271D26F9EB711FE0F1B626B9F9C266E8045FFBBF5F54"
)


class ClosureError(ValueError):
    """Raised when a selector-538 chunk-0 closure contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ClosureError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


REVIEW = load_module(
    REVIEW_BUILDER_PATH,
    "pk_selector538_chunk0_closure_review_helpers_v1",
)
CALLER = REVIEW.CALLER
HONORIFIC = CALLER.HONORIFIC
CROSS = CALLER.CROSS
BASE_AUDIT = REVIEW.BASE_AUDIT
ENGINE = REVIEW.ENGINE
LIVE_STEAM_BASE = Path(CALLER.LIVE_STEAM_BASE)
LIVE_STEAM_PK = Path(CALLER.LIVE_STEAM_PK)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    require(path.is_file(), f"required file is absent: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_json(value: Any) -> str:
    return canonical_bytes(value).decode("ascii") + "\n"


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(canonical_json(row) for row in rows)


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def parse_coordinate(value: str) -> tuple[int, int, int]:
    return REVIEW.parse_coordinate(value)


def coordinate_digest(values: Iterable[str]) -> str:
    return REVIEW.coordinate_digest(values)


def root_digest(values: Iterable[tuple[int, int]]) -> str:
    return REVIEW.root_digest(values)


def site_digest(values: Iterable[str]) -> str:
    return REVIEW.site_digest(values)


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    return HONORIFIC.row_sort_key(row)


def root_strings(values: Iterable[tuple[int, int]]) -> set[str]:
    return {f"{block_id}:{record_id}" for block_id, record_id in values}


def load_json_exact(path: Path, expected_sha256: str) -> dict[str, Any]:
    require(sha256_file(path) == expected_sha256, f"hash drifted: {path}")
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM rejected: {path}")
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClosureError(f"invalid strict UTF-8 JSON: {path}") from exc
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def load_predecessor() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    require(
        sha256_file(PREDECESSOR_PRIVATE_PATH)
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        "frozen post-2546 private checkpoint drifted",
    )
    report = load_json_exact(
        PREDECESSOR_PUBLIC_PATH,
        EXPECTED_PREDECESSOR_PUBLIC_SHA256,
    )
    result = report.get("result", {})
    layer = (
        report.get("promotions", {})
        .get("pk_msggame", {})
        .get("bound_terminal_2546_full_caller", {})
    )
    require(
        result.get("semantic_review_approved") == EXPECTED_PREDECESSOR_ROWS
        and result.get("runtime_review_pending") == EXPECTED_PREDECESSOR_PENDING
        and result.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and layer.get("pk_candidate_packed_sha256")
        == EXPECTED_BASELINE_CANDIDATE_SHA256
        and report.get("steam_write_performed") is False,
        "frozen post-2546 public checkpoint drifted",
    )
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    with PREDECESSOR_PRIVATE_PATH.open(
        "r",
        encoding="utf-8",
        errors="strict",
        newline="",
    ) as stream:
        for line_number, line in enumerate(stream, start=1):
            require(
                line.endswith("\n"),
                f"predecessor line {line_number} lacks LF",
            )
            row = json.loads(line)
            key = (str(row["resource"]), str(row["coordinate"]))
            require(key not in rows, f"duplicate predecessor row: {key}")
            rows[key] = row
    require(
        len(rows) == EXPECTED_PREDECESSOR_ROWS
        and sum(
            row.get("runtime_review") == "pending"
            for row in rows.values()
        )
        == EXPECTED_PREDECESSOR_PENDING,
        "frozen predecessor row universe drifted",
    )
    return rows, report


def load_review() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    require(
        sha256_file(PRIVATE_HANDOFF_PATH) == EXPECTED_HANDOFF_SHA256,
        "private chunk-0 handoff drifted",
    )
    public = load_json_exact(
        REVIEW_PUBLIC_PATH,
        EXPECTED_REVIEW_PUBLIC_SHA256,
    )
    assignment, chunk = REVIEW.load_assignment()
    world = REVIEW.load_world()
    handoff = REVIEW.load_json_exact(PRIVATE_HANDOFF_PATH)
    validated = REVIEW.validate_private_handoff(
        handoff,
        assignment=assignment,
        chunk=chunk,
        world=world,
    )
    result = public.get("result", {})
    proof = public.get("proof", {})
    require(
        public.get("schema") == REVIEW.PUBLIC_SCHEMA
        and public.get("status") == "PASS"
        and result.get("accepted_site_count") == EXPECTED_ACCEPTED_SITES
        and result.get("rewrite_coordinate_count") == EXPECTED_REWRITE_ROWS
        and result.get("keep_coordinate_count") == EXPECTED_KEEP_ROWS
        and result.get("reject_coordinate_count") == EXPECTED_REJECTED_SITES
        and result.get("proposal_candidate_sha256")
        == EXPECTED_CANDIDATE_SHA256
        and result.get("potential_promotion_coordinate_count")
        == EXPECTED_PROMOTION_ROWS
        and result.get("blocked_pending_coordinate_count")
        == EXPECTED_REJECTED_PENDING_ROWS
        and proof.get("assembly_branches_recorded") == 455
        and proof.get(
            "all_accepted_current_relative_raw_g1n_nonexpanding"
        )
        is True
        and proof.get("all_accepted_register_branches_proven") is True
        and public.get("steam_write_performed") is False,
        "source-free chunk-0 proposal drifted",
    )
    return handoff, public, world, validated


def grouped_coordinates(
    rows: Mapping[tuple[str, str], Mapping[str, Any]],
    status: str,
) -> dict[tuple[int, int], list[str]]:
    result: defaultdict[tuple[int, int], list[str]] = defaultdict(list)
    for (resource, coordinate), row in rows.items():
        if resource == "pk_msggame" and row.get("runtime_review") == status:
            result[parse_coordinate(coordinate)[:2]].append(coordinate)
    for coordinates in result.values():
        coordinates.sort(key=parse_coordinate)
    return dict(result)


def build_candidate(
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    rewrite_map: Mapping[str, str],
    keep_map: Mapping[str, str],
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
    baseline_blob = BASE_AUDIT.rebuild_packed_with_literals(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        replacements,
    )
    baseline_records = BASE_AUDIT.records_from_blob(baseline_blob)
    require(
        sha256_bytes(baseline_blob) == EXPECTED_BASELINE_CANDIDATE_SHA256,
        "predecessor translation overlay does not reproduce D5F7",
    )
    for coordinate, text in keep_map.items():
        record = baseline_records[parse_coordinate(coordinate)[:2]]
        literal_id = parse_coordinate(coordinate)[2]
        require(
            BASE_AUDIT.parse_record_literals(record)[literal_id].text == text,
            f"keep coordinate drifted: {coordinate}",
        )
    replacements.update(
        {
            parse_coordinate(coordinate): str(text)
            for coordinate, text in rewrite_map.items()
        }
    )
    candidate_blob = BASE_AUDIT.rebuild_packed_with_literals(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        replacements,
    )
    candidate_records = BASE_AUDIT.records_from_blob(candidate_blob)
    require(
        sha256_bytes(candidate_blob) == EXPECTED_CANDIDATE_SHA256,
        "chunk-0 proposal candidate does not reproduce 583E",
    )
    changed_roots = {
        root
        for root in baseline_records
        if baseline_records[root].data != candidate_records[root].data
    }
    expected_changed_roots = {
        parse_coordinate(coordinate)[:2] for coordinate in rewrite_map
    }
    require(
        changed_roots == expected_changed_roots,
        "chunk-0 candidate changed-record universe drifted",
    )
    for root in changed_roots:
        require(
            REVIEW.record_gap_sha256(baseline_records[root])
            == REVIEW.record_gap_sha256(candidate_records[root]),
            f"candidate control gaps changed at {root}",
        )
    return baseline_blob, baseline_records, candidate_blob, candidate_records


def coordinates_for_roots(
    roots: Iterable[tuple[int, int]],
    grouped: Mapping[tuple[int, int], Sequence[str]],
) -> set[str]:
    return {
        coordinate
        for root in roots
        for coordinate in grouped.get(root, ())
    }


def build_analysis(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    world: Mapping[str, Any],
    handoff: Mapping[str, Any],
    validated: Mapping[str, Any],
) -> dict[str, Any]:
    rewrite_map = {
        str(coordinate): str(text)
        for coordinate, text in validated["rewrite_map"].items()
    }
    keep_map = {
        str(coordinate): str(text)
        for coordinate, text in validated["keep_map"].items()
    }
    require(
        len(rewrite_map) == EXPECTED_REWRITE_ROWS
        and coordinate_digest(rewrite_map)
        == EXPECTED_REWRITE_COORDINATE_SHA256
        and canonical_sha256(rewrite_map) == EXPECTED_REWRITE_MAP_SHA256
        and len(keep_map) == EXPECTED_KEEP_ROWS,
        "private exact rewrite/keep map drifted",
    )
    (
        baseline_blob,
        baseline_records,
        candidate_blob,
        candidate_records,
    ) = build_candidate(predecessor_rows, rewrite_map, keep_map)

    source_records = world["language_records"]["jp"]
    current_records = world["current_records"]
    inputs = dataclasses.make_dataclass(
        "Selector538Chunk0CandidateInputs",
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
    terminal_roots = {(0, terminal) for terminal in TERMINALS}
    candidate_affected = HONORIFIC.reverse_ancestors(
        edges=candidate_edges,
        targets=tuple(terminal_roots),
    )
    source_affected = HONORIFIC.reverse_ancestors(
        edges=source_edges,
        targets=tuple(terminal_roots),
    )
    require(
        len(candidate_affected) == EXPECTED_CANDIDATE_AFFECTED_ROOTS
        and root_digest(candidate_affected)
        == EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256
        and len(source_affected) == EXPECTED_SOURCE_AFFECTED_ROOTS
        and root_digest(source_affected)
        == EXPECTED_SOURCE_AFFECTED_ROOT_SHA256,
        "candidate/source reverse-ancestor universe drifted",
    )

    pending_by_root = grouped_coordinates(predecessor_rows, "pending")
    verified_by_root = grouped_coordinates(predecessor_rows, "verified")
    accepted_sites = set(validated["accepted_sites"])
    rejected_sites = set(validated["rejected_sites"])
    accepted_roots = {REVIEW.site_root(site) for site in accepted_sites}
    rejected_roots = {REVIEW.site_root(site) for site in rejected_sites}
    require(
        len(accepted_sites) == EXPECTED_ACCEPTED_SITES
        and site_digest(sorted(accepted_sites))
        == EXPECTED_ACCEPTED_SITE_SHA256
        and len(rejected_sites) == EXPECTED_REJECTED_SITES
        and site_digest(sorted(rejected_sites))
        == EXPECTED_REJECTED_SITE_SHA256
        and root_digest(accepted_roots) == EXPECTED_ACCEPTED_ROOT_SHA256
        and len(rejected_roots) == EXPECTED_REJECTED_ROOTS
        and root_digest(rejected_roots) == EXPECTED_REJECTED_ROOT_SHA256
        and accepted_roots <= candidate_affected
        and accepted_roots <= source_affected
        and rejected_roots <= candidate_affected
        and rejected_roots <= source_affected,
        "reviewed site/root graph binding drifted",
    )

    promotion_roots = accepted_roots & set(pending_by_root)
    promotion_coordinates = coordinates_for_roots(
        promotion_roots, pending_by_root
    )
    rejected_pending_roots = rejected_roots & set(pending_by_root)
    rejected_pending_coordinates = coordinates_for_roots(
        rejected_pending_roots, pending_by_root
    )
    renewal_roots = set(verified_by_root) & (
        candidate_affected | source_affected
    )
    renewal_coordinates = coordinates_for_roots(
        renewal_roots, verified_by_root
    )
    update_coordinates = promotion_coordinates | renewal_coordinates
    require(
        len(promotion_roots) == EXPECTED_PROMOTION_ROOTS
        and len(promotion_coordinates) == EXPECTED_PROMOTION_ROWS
        and root_digest(promotion_roots) == EXPECTED_PROMOTION_ROOT_SHA256
        and coordinate_digest(promotion_coordinates)
        == EXPECTED_PROMOTION_COORDINATE_SHA256
        and len(rejected_pending_roots) == EXPECTED_REJECTED_PENDING_ROOTS
        and len(rejected_pending_coordinates)
        == EXPECTED_REJECTED_PENDING_ROWS
        and root_digest(rejected_pending_roots)
        == EXPECTED_REJECTED_PENDING_ROOT_SHA256
        and coordinate_digest(rejected_pending_coordinates)
        == EXPECTED_REJECTED_COORDINATE_SHA256
        and len(renewal_roots) == EXPECTED_RENEWAL_ROOTS
        and len(renewal_coordinates) == EXPECTED_RENEWAL_ROWS
        and root_digest(renewal_roots) == EXPECTED_RENEWAL_ROOT_SHA256
        and coordinate_digest(renewal_coordinates)
        == EXPECTED_RENEWAL_COORDINATE_SHA256
        and len(update_coordinates) == EXPECTED_DECISION_ROWS
        and coordinate_digest(update_coordinates)
        == EXPECTED_DECISION_COORDINATE_SHA256
        and set(rewrite_map) <= update_coordinates,
        "promotion/renewal/rejection closure partition drifted",
    )

    review_by_site = {
        str(row["site"]): row for row in handoff["site_reviews"]
    }
    terminal_candidate = REVIEW.terminal_literals(candidate_records)
    terminal_current = REVIEW.terminal_literals(current_records)
    accepted_assembly_manifest: list[list[Any]] = []
    for site in sorted(accepted_sites):
        row = review_by_site[site]
        reviewed_left, reviewed_right = REVIEW.adjacent_literals(
            candidate_records, site
        )
        current_left, current_right = REVIEW.adjacent_literals(
            current_records, site
        )
        require(
            reviewed_left == row["reviewed_left_translation"]
            and reviewed_right == row["baseline_candidate_right"],
            f"accepted candidate literal drifted at {site}",
        )
        branches = {
            str(branch["terminal_coordinate"]): branch
            for branch in row["assemblies"]
        }
        for terminal in TERMINALS:
            reviewed_assembly = (
                reviewed_left
                + terminal_candidate[terminal]
                + reviewed_right
            )
            current_assembly = (
                current_left + terminal_current[terminal] + current_right
            )
            reviewed_lines = REVIEW.line_metrics(reviewed_assembly)
            current_lines = REVIEW.line_metrics(current_assembly)
            nonexpanding = REVIEW.current_relative_nonexpanding(
                reviewed_lines, current_lines
            )
            branch = branches[f"0:{terminal}:0"]
            require(
                branch["reviewed_assembly"] == reviewed_assembly
                and branch["current_assembly"] == current_assembly
                and branch["reviewed_lines"] == reviewed_lines
                and branch["current_lines"] == current_lines
                and branch["register_and_grammar_proven"] is True
                and branch["current_relative_raw_g1n_nonexpanding"] is True
                and nonexpanding,
                f"accepted assembly proof drifted at {site}/0:{terminal}:0",
            )
            accepted_assembly_manifest.append(
                [
                    site,
                    terminal,
                    sha256_bytes(reviewed_assembly.encode("utf-8")),
                    sha256_bytes(current_assembly.encode("utf-8")),
                    [line["raw_g1n_width_px"] for line in reviewed_lines],
                    [line["raw_g1n_width_px"] for line in current_lines],
                ]
            )
    require(
        len(accepted_assembly_manifest) == EXPECTED_ACCEPTED_ASSEMBLIES,
        "accepted assembly cardinality drifted",
    )

    affected_pending_roots = set(pending_by_root) & (
        candidate_affected | source_affected
    )
    held_unreviewed_roots = (
        affected_pending_roots
        - promotion_roots
        - rejected_pending_roots
    )
    held_unreviewed_coordinates = coordinates_for_roots(
        held_unreviewed_roots, pending_by_root
    )
    return {
        "accepted_assembly_manifest": accepted_assembly_manifest,
        "accepted_roots": accepted_roots,
        "accepted_sites": accepted_sites,
        "baseline_blob": baseline_blob,
        "baseline_records": baseline_records,
        "candidate_affected": candidate_affected,
        "candidate_blob": candidate_blob,
        "candidate_edges": candidate_edges,
        "candidate_records": candidate_records,
        "current_records": current_records,
        "held_unreviewed_coordinates": held_unreviewed_coordinates,
        "held_unreviewed_roots": held_unreviewed_roots,
        "keep_map": keep_map,
        "pending_by_root": pending_by_root,
        "profiles": profiles,
        "promotion_coordinates": promotion_coordinates,
        "promotion_roots": promotion_roots,
        "rejected_pending_coordinates": rejected_pending_coordinates,
        "rejected_pending_roots": rejected_pending_roots,
        "rejected_roots": rejected_roots,
        "rejected_sites": rejected_sites,
        "renewal_coordinates": renewal_coordinates,
        "renewal_roots": renewal_roots,
        "rewrite_map": rewrite_map,
        "source_affected": source_affected,
        "source_edges": source_edges,
        "update_coordinates": update_coordinates,
        "verified_by_root": verified_by_root,
    }


def build_audit(
    *,
    analysis: Mapping[str, Any],
    predecessor_report: Mapping[str, Any],
    review_public: Mapping[str, Any],
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "distribution_policy": {
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_dialogue_bodies": False,
            "private_handoff_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_translation_map_keys": False,
        },
        "guards": {
            "accepted_assembly_sha256": canonical_sha256(
                analysis["accepted_assembly_manifest"]
            ),
            "accepted_root_sha256": root_digest(analysis["accepted_roots"]),
            "accepted_site_sha256": site_digest(
                sorted(analysis["accepted_sites"])
            ),
            "baseline_candidate_sha256":
                EXPECTED_BASELINE_CANDIDATE_SHA256,
            "candidate_affected_root_sha256": root_digest(
                analysis["candidate_affected"]
            ),
            "candidate_sha256": sha256_bytes(analysis["candidate_blob"]),
            "decision_coordinate_sha256": coordinate_digest(
                analysis["update_coordinates"]
            ),
            "handoff_sha256": EXPECTED_HANDOFF_SHA256,
            "predecessor_private_sha256":
                EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "predecessor_public_sha256":
                EXPECTED_PREDECESSOR_PUBLIC_SHA256,
            "promotion_coordinate_sha256": coordinate_digest(
                analysis["promotion_coordinates"]
            ),
            "promotion_root_sha256": root_digest(
                analysis["promotion_roots"]
            ),
            "rejected_coordinate_sha256": coordinate_digest(
                analysis["rejected_pending_coordinates"]
            ),
            "rejected_root_sha256": root_digest(
                analysis["rejected_roots"]
            ),
            "rejected_pending_root_sha256": root_digest(
                analysis["rejected_pending_roots"]
            ),
            "renewal_coordinate_sha256": coordinate_digest(
                analysis["renewal_coordinates"]
            ),
            "renewal_root_sha256": root_digest(analysis["renewal_roots"]),
            "review_public_sha256": EXPECTED_REVIEW_PUBLIC_SHA256,
            "rewrite_coordinate_sha256": coordinate_digest(
                analysis["rewrite_map"]
            ),
            "rewrite_map_canonical_sha256": canonical_sha256(
                analysis["rewrite_map"]
            ),
            "source_affected_root_sha256": root_digest(
                analysis["source_affected"]
            ),
        },
        "method": METHOD,
        "proof": {
            "accepted_assembly_rows": EXPECTED_ACCEPTED_ASSEMBLIES,
            "all_exact_overrides_applied": True,
            "all_keep_rows_preserved": True,
            "all_accepted_register_branches_proven": True,
            "all_accepted_width_branches_nonexpanding": True,
            "all_affected_preexisting_verified_rows_renewed": True,
            "all_changed_record_control_gaps_preserved": True,
            "all_outer_whitespace_and_linebreaks_preserved": True,
            "automatic_space_inserted": False,
            "candidate_affected_records": len(
                analysis["candidate_affected"]
            ),
            "candidate_and_source_reverse_ancestors_audited": True,
            "held_unreviewed_pending_roots": len(
                analysis["held_unreviewed_roots"]
            ),
            "held_unreviewed_pending_rows": len(
                analysis["held_unreviewed_coordinates"]
            ),
            "rejected_chunk0_pending_rows_unchanged": True,
            "source_affected_records": len(analysis["source_affected"]),
            "unknown_accepted_sites": 0,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "schema": AUDIT_SCHEMA,
        "scope": {
            "accepted_site_count": EXPECTED_ACCEPTED_SITES,
            "chunk_id": 0,
            "exact_override_rows": EXPECTED_REWRITE_ROWS,
            "keep_rows": EXPECTED_KEEP_ROWS,
            "post_layer_pending_rows": EXPECTED_PENDING_AFTER,
            "predecessor_pending_rows": EXPECTED_PREDECESSOR_PENDING,
            "predecessor_rows": EXPECTED_PREDECESSOR_ROWS,
            "rejected_roots": EXPECTED_REJECTED_ROOTS,
            "rejected_pending_roots": EXPECTED_REJECTED_PENDING_ROOTS,
            "rejected_pending_rows": EXPECTED_REJECTED_PENDING_ROWS,
            "rejected_site_count": EXPECTED_REJECTED_SITES,
            "runtime_promotion_roots": EXPECTED_PROMOTION_ROOTS,
            "runtime_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "selector": SELECTOR,
            "terminal_records": len(TERMINALS),
            "verification_renewal_roots": EXPECTED_RENEWAL_ROOTS,
            "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    require(
        predecessor_report["result"]["runtime_review_pending"]
        == EXPECTED_PREDECESSOR_PENDING
        and review_public["result"]["proposal_candidate_sha256"]
        == EXPECTED_CANDIDATE_SHA256,
        "audit input report binding drifted",
    )
    return HONORIFIC.seal_report(report)


def build_updated_rows(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    analysis: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rewrite_map = analysis["rewrite_map"]
    promotion_coordinates = analysis["promotion_coordinates"]
    renewal_coordinates = analysis["renewal_coordinates"]
    updated_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    for coordinate in sorted(
        analysis["update_coordinates"], key=parse_coordinate
    ):
        predecessor = predecessor_rows[("pk_msggame", coordinate)]
        updated = copy.deepcopy(dict(predecessor))
        is_override = coordinate in rewrite_map
        is_promotion = coordinate in promotion_coordinates
        if is_override:
            updated["translation"] = rewrite_map[coordinate]
            CALLER.PREDECESSOR.repair_hard_risks(updated)
            updated["selector538_chunk0_exact_override_evidence"] = {
                "automatic_space_inserted": False,
                "control_bytes_preserved": True,
                "private_handoff_hash_bound": True,
                "schema": OVERRIDE_SCHEMA,
                "translation_utf16le_sha256": ENGINE.sha256_text(
                    str(updated["translation"])
                ),
            }
        if is_promotion:
            require(
                predecessor.get("runtime_review") == "pending",
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
            "action": action,
            "closure_binding": {
                "accepted_assembly_sha256": audit["guards"][
                    "accepted_assembly_sha256"
                ],
                "audit_report_file_sha256": audit_file_sha256,
                "audit_report_payload_sha256": audit["guards"][
                    "report_payload_sha256"
                ],
                "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
                "decision_coordinate_sha256":
                    EXPECTED_DECISION_COORDINATE_SHA256,
                "handoff_sha256": EXPECTED_HANDOFF_SHA256,
                "review_public_sha256": EXPECTED_REVIEW_PUBLIC_SHA256,
                "selector": SELECTOR,
                "terminal_coordinate_sha256": coordinate_digest(
                    f"0:{terminal}:0" for terminal in TERMINALS
                ),
            },
            "coordinate": coordinate,
            "method": METHOD,
            "per_row_game_playback_required": False,
            "predecessor_binding": {
                "checkpoint_sha256": EXPECTED_PREDECESSOR_PRIVATE_SHA256,
                "row_sha256": canonical_sha256(predecessor),
            },
            "preexisting_verified_evidence_renewed": not is_promotion,
            "resource": "pk_msggame",
            "schema": EVIDENCE_SCHEMA,
            "status": "verified",
            "translation_utf16le_sha256": ENGINE.sha256_text(
                str(updated["translation"])
            ),
        }
        updated[UPDATE_ACTION_FIELD] = action
        updated["runtime_vm_verification"] = evidence
        updated_rows.append(updated)
        evidence_rows.append(evidence)
    updated_rows.sort(key=row_sort_key)
    evidence_rows.sort(
        key=lambda row: parse_coordinate(str(row["coordinate"]))
    )
    actions = Counter(str(row["action"]) for row in evidence_rows)
    require(
        dict(actions) == EXPECTED_ACTION_COUNTS,
        "closure action counts drifted",
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
    report: dict[str, Any] = {
        "action_counts": dict(sorted(actions.items())),
        "distribution_policy": {
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_dialogue_bodies": False,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_translation_map_keys": False,
        },
        "evidence": {
            "accepted_assembly_sha256": audit["guards"][
                "accepted_assembly_sha256"
            ],
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "decision_coordinate_sha256":
                EXPECTED_DECISION_COORDINATE_SHA256,
            "handoff_sha256": EXPECTED_HANDOFF_SHA256,
            "predecessor_checkpoint_sha256":
                EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "review_public_sha256": EXPECTED_REVIEW_PUBLIC_SHA256,
        },
        "method": METHOD,
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": {
            "decision_delta_rows": EXPECTED_DECISION_ROWS,
            "exact_override_rows": EXPECTED_REWRITE_ROWS,
            "pending_rows_after": EXPECTED_PENDING_AFTER,
            "pending_rows_before": EXPECTED_PREDECESSOR_PENDING,
            "private_decision_delta_sha256": sha256_bytes(
                decision_content.encode("utf-8")
            ),
            "private_evidence_rows": EXPECTED_DECISION_ROWS,
            "private_evidence_sha256": sha256_bytes(
                evidence_content.encode("utf-8")
            ),
            "rejected_pending_roots": EXPECTED_REJECTED_PENDING_ROOTS,
            "rejected_pending_rows": EXPECTED_REJECTED_PENDING_ROWS,
            "rejected_roots": EXPECTED_REJECTED_ROOTS,
            "runtime_promotion_roots": EXPECTED_PROMOTION_ROOTS,
            "runtime_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "verification_renewal_roots": EXPECTED_RENEWAL_ROOTS,
            "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
        },
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "steam_write_performed": False,
    }
    return HONORIFIC.seal_report(report)


SOURCE_TEXT_RE = re.compile(
    r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7a3]"
)
SENSITIVE_BODY_KEYS = {
    "accepted_sites",
    "assembly",
    "candidate_text",
    "current_text",
    "exact_maps",
    "records",
    "rejected_sites",
    "source_text",
    "translation",
}


def assert_source_free_report(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            require(
                key not in SENSITIVE_BODY_KEYS,
                f"tracked report contains private body/map key: {key}",
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
    predecessor_rows, predecessor_report = load_predecessor()
    handoff, review_public, world, validated = load_review()
    analysis = build_analysis(
        predecessor_rows=predecessor_rows,
        world=world,
        handoff=handoff,
        validated=validated,
    )
    audit = build_audit(
        analysis=analysis,
        predecessor_report=predecessor_report,
        review_public=review_public,
    )
    HONORIFIC.validate_seal(audit)
    audit_content = canonical_json(audit)
    audit_file_sha256 = sha256_bytes(audit_content.encode("utf-8"))
    updated_rows, evidence_rows = build_updated_rows(
        predecessor_rows=predecessor_rows,
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
            "analysis": analysis,
            "evidence_rows": evidence_rows,
            "predecessor_rows": predecessor_rows,
            "promotion": promotion,
            "steam_after": steam_after,
            "steam_before": steam_before,
            "updated_rows": updated_rows,
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
        "serialized closure output drifted",
    )
    actual_hashes = (
        sha256_bytes(audit_content.encode("utf-8")),
        sha256_bytes(promotion_content.encode("utf-8")),
        sha256_bytes(decision_content.encode("utf-8")),
        sha256_bytes(evidence_content.encode("utf-8")),
    )
    expected_hashes = (
        EXPECTED_AUDIT_FILE_SHA256,
        EXPECTED_PROMOTION_FILE_SHA256,
        EXPECTED_DECISION_FILE_SHA256,
        EXPECTED_EVIDENCE_FILE_SHA256,
    )
    if require_frozen_hashes:
        require(
            all(expected_hashes) and actual_hashes == expected_hashes,
            f"frozen closure output hash drifted: {actual_hashes}",
        )
    if EXPECTED_ACCEPTED_ASSEMBLY_SHA256 is not None:
        require(
            audit["guards"]["accepted_assembly_sha256"]
            == EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
            "accepted assembly digest drifted",
        )
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
        "private closure output row count drifted",
    )
    merged = {
        key: copy.deepcopy(dict(row))
        for key, row in bundle["predecessor_rows"].items()
    }
    merged.update(updated_by_key)
    analysis = bundle["analysis"]
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
        and bundle["steam_before"] == bundle["steam_after"]
        and audit.get("steam_write_performed") is False
        and promotion.get("steam_write_performed") is False,
        "final closure result drifted",
    )
    for coordinate in analysis["promotion_coordinates"]:
        require(
            merged[("pk_msggame", coordinate)]["runtime_review"]
            == "verified",
            f"promotion was not applied: {coordinate}",
        )
    for coordinate in analysis["rejected_pending_coordinates"]:
        require(
            merged[("pk_msggame", coordinate)]
            == bundle["predecessor_rows"][("pk_msggame", coordinate)]
            and merged[("pk_msggame", coordinate)]["runtime_review"]
            == "pending",
            f"rejected pending row changed: {coordinate}",
        )
    for coordinate, text in analysis["rewrite_map"].items():
        require(
            merged[("pk_msggame", coordinate)].get("translation") == text,
            f"merged exact override drifted: {coordinate}",
        )
    for coordinate, text in analysis["keep_map"].items():
        require(
            merged[("pk_msggame", coordinate)].get("translation") == text,
            f"merged keep row drifted: {coordinate}",
        )
    merged_replacements = {
        parse_coordinate(coordinate): str(row["translation"])
        for (resource, coordinate), row in merged.items()
        if resource == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    merged_candidate = BASE_AUDIT.rebuild_packed_with_literals(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        merged_replacements,
    )
    require(
        sha256_bytes(merged_candidate) == EXPECTED_CANDIDATE_SHA256,
        "merged closure rows do not reproduce candidate 583E",
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
        "public reports must use fixed tracked source-free paths",
    )
    paths = {
        args.audit_output.resolve(strict=False),
        args.promotion_output.resolve(strict=False),
        args.decision_output.resolve(strict=False),
        args.evidence_output.resolve(strict=False),
    }
    require(len(paths) == 4, "closure output paths must be distinct")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-output", type=Path, default=DEFAULT_AUDIT_OUTPUT
    )
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
        for path, content in outputs.items():
            require(path.is_file(), f"output missing: {path}")
            require(
                path.read_text(encoding="utf-8") == content,
                f"output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    print(
        "PASS "
        f"overrides={EXPECTED_REWRITE_ROWS} "
        f"renewed={EXPECTED_RENEWAL_ROWS} "
        f"promoted={EXPECTED_PROMOTION_ROWS} "
        f"pending={EXPECTED_PENDING_AFTER} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
