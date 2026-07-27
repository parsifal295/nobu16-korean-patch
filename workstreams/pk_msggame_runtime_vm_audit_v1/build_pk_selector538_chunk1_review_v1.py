#!/usr/bin/env python3
"""Validate selector 538 chunk 1 and build its source-free proposal report.

Dialogue bodies and exact translation maps are read only from private handoffs
below ``tmp``.  This builder neither mutates a shared decision ledger nor
writes to the Steam installation.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import types
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
BASE_BUILDER = WORKSTREAM / "build_pk_selector538_chunk0_review_v1.py"
CLOSURE_BUILDER = WORKSTREAM / "build_pk_selector538_chunk0_closure_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "family538_assignment.private.v1.json"
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family538_chunk1_analysis.private.v1.json"
)
CHUNK0_PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family538_chunk0_analysis.private.v1.json"
)
DEFAULT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk1_review_proposal.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector538-chunk1-analysis.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector538-chunk1-review-proposal.v1"
METHOD = "reversed_vm_pk_selector538_chunk1_full_caller_review"
SELECTOR = 538
TERMINALS = tuple(range(1916, 1923))
ORDINAL_START = 65
ORDINAL_END = 135
EXPECTED_SITE_COUNT = 71
EXPECTED_ROOT_COUNT = 70
EXPECTED_ASSEMBLY_COUNT = 497
EXPECTED_ACCEPTED = 45
EXPECTED_REWRITE = 42
EXPECTED_KEEP = 3
EXPECTED_REJECT = 26
EXPECTED_ACCEPTED_ROOTS = 44
EXPECTED_REJECTED_ROOTS = 26
EXPECTED_ACCEPTED_ASSEMBLIES = 315
EXPECTED_REJECTED_ASSEMBLIES = 182
EXPECTED_POTENTIAL_PROMOTION_COUNT = 79
EXPECTED_BLOCKED_PENDING_COUNT = 15
EXPECTED_PROMOTION_ROOTS = 34
EXPECTED_REJECTED_PENDING_ROOTS = 7
EXPECTED_RENEWAL_ROWS = 420
EXPECTED_RENEWAL_ROOTS = 204
EXPECTED_DECISION_ROWS = 499
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_PENDING_AFTER = 8_134
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 340
EXPECTED_SOURCE_AFFECTED_ROOTS = 405
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 66,
    "translation_override_and_runtime_promotion": 13,
    "translation_override_and_verification_renewal": 29,
    "verification_renewal": 391,
}

EXPECTED_ASSIGNMENT_SHA256 = (
    "57FBEE8EEC3551DAD8A7F1BB77CD7B2E2CF08109CB3A912452BE8244BB0FAACF"
)
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_LEDGER_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_CHUNK_SITE_SHA256 = (
    "99B41DDE32CF5BD53F748D830060022C7936A799D6627F6E092D3019A322F9CF"
)
EXPECTED_CHUNK_ROOT_SHA256 = (
    "44F41ABD203A8FD15A8A43295F84F0DA53FA5D70FF77F4D62E7A4A51E967D368"
)
EXPECTED_PENDING_COORDINATE_SHA256 = (
    "90B1D6AA0CF88113E222640927EA955E53ECAD1A04E307326430C006BA1FF7F1"
)
EXPECTED_PENDING_ROW_UPPER_BOUND = 94
EXPECTED_CHUNK0_PRIVATE_HANDOFF_SHA256 = (
    "9A8CE09CCA100FCA9C5F9C148EDA38C043D8737218F2B4A11F3CDF2B7A7A92BF"
)

# Frozen after the private handoff and public proposal are independently
# reproduced.
EXPECTED_PRIVATE_HANDOFF_SHA256: str | None = (
    "E598C36F210BF91D02C09C6FE0BABD995212A542CACCAD60AA89CE6F91AE3E8F"
)
EXPECTED_PROPOSAL_CANDIDATE_SHA256: str | None = (
    "A8CDBB1CBD15E53BF77606C4E05425B861D28B80C6E8C327A219AE76FEFA6427"
)
EXPECTED_REWRITE_COORDINATE_SHA256: str | None = (
    "BA3630B6AA76665ACD2018BADD5439C3C14D3D0F01D8A5241FB5DB220F885780"
)
EXPECTED_KEEP_COORDINATE_SHA256: str | None = (
    "AF86477C791A6A9184C2CAA3758ED3B48F1A15445F70F90235EAF4BD1614101F"
)
EXPECTED_REJECT_COORDINATE_SHA256: str | None = (
    "CAA612E12CB1313EB078150A140C417ED4D1389D0D53B11EDD4D1FD416E74E4C"
)
EXPECTED_ACCEPTED_SITE_SHA256: str | None = (
    "3869A52B0B9426C54E406AB5A763353046B9B27C3261E415CF8CD958331A82A7"
)
EXPECTED_REJECTED_SITE_SHA256: str | None = (
    "7A9D19FCF78D0CB81D47F09948BCDFDD3E12F47429F25DC4A971E00E65DE4355"
)
EXPECTED_ASSEMBLY_SHA256: str | None = (
    "C3E5301F51DA0C7A6904A955E916BFC8A9578E32566C7E3764D314679C7E7756"
)
EXPECTED_ACCEPTED_ROOT_SHA256: str | None = (
    "57DCA1F009604A61CD579FF8239D93A6AB4F58CAA211D8CE3AED811249C61924"
)
EXPECTED_REJECTED_ROOT_SHA256: str | None = (
    "DCBD4146BCDDA3946A11DB16203768A0A812F3715CF59FDDD82E5F5F2C29D185"
)
EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256: str | None = (
    "3BCA0D28A86BBACA0732614473B45B5C72A9669BB080DF772188E6478287DEF8"
)
EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256: str | None = (
    "588A99104D245BDC13639A9E9BAFD85E55405DE79C59F8E89D90D9D02DD641DE"
)
EXPECTED_CHUNK0_OVERLAP_SHA256: str | None = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_ACCEPTED_ASSEMBLY_SHA256: str | None = (
    "DB2374E43B66811D33986EA5D6B12AC0AC46C77FC7237C53613CB1A2E52B0EA2"
)
EXPECTED_PROMOTION_ROOT_SHA256: str | None = (
    "09F4132381ADB06DBC8F11CD13B439CCAA573A235F1659B3508BB524139DF536"
)
EXPECTED_REJECTED_PENDING_ROOT_SHA256: str | None = (
    "8AA5842A0C24C70AEA5C92C3A49E66B7B8B6ADD959EB3DC2469107383B858D80"
)
EXPECTED_RENEWAL_COORDINATE_SHA256: str | None = (
    "36058C249C73F5B42C0DC7426FA68879F4BDC515F40F9C50B6CFEC07C7FD4D59"
)
EXPECTED_RENEWAL_ROOT_SHA256: str | None = (
    "65AB478BEE4C7F7102084ACDD7D1268C33F5FE93DDA278F69DEB7D59C502AE92"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "876D5F6B96D0C50D245F7E176E0AE038BBB4BC0D4D4A9EB29F48B76AD89DF829"
)
EXPECTED_ACTION_SHA256: str | None = (
    "0667C765F8FBD2E72D37D92FE27C1FCF5BA376CC30F5B52858CE4668187D2691"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "772622A0A474F5FC3388B49F78FEE2ADDCD297785A5C97CE4EB4285FAAD96502"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_BUILDER, "pk_selector538_chunk1_base_v1")
CLOSURE = load_module(CLOSURE_BUILDER, "pk_selector538_chunk1_closure_base_v1")
ReviewError = BASE.ReviewError
require = BASE.require
sha256_bytes = BASE.sha256_bytes
sha256_file = BASE.sha256_file
canonical_bytes = BASE.canonical_bytes
canonical_sha256 = BASE.canonical_sha256
coordinate_digest = BASE.coordinate_digest
site_digest = BASE.site_digest
root_digest = BASE.root_digest
parse_coordinate = BASE.parse_coordinate
site_root = BASE.site_root
line_metrics = BASE.line_metrics
current_relative_nonexpanding = BASE.current_relative_nonexpanding
outer_whitespace_signature = BASE.outer_whitespace_signature
record_gap_sha256 = BASE.record_gap_sha256
adjacent_literals = BASE.adjacent_literals
terminal_literals = BASE.terminal_literals
load_json_exact = BASE.load_json_exact
ASSIGN = BASE.ASSIGN
CALLER = BASE.CALLER
BASE_AUDIT = BASE.BASE_AUDIT


def load_assignment() -> tuple[dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(ASSIGNMENT_PATH) == EXPECTED_ASSIGNMENT_SHA256,
        "selector 538 assignment hash drifted",
    )
    assignment = load_json_exact(ASSIGNMENT_PATH)
    require(
        assignment.get("schema") == ASSIGN.SCHEMA,
        "selector 538 assignment schema drifted",
    )
    chunk = assignment["chunks"][1]
    require(
        chunk.get("chunk_id") == 1
        and chunk.get("ordinal_start") == ORDINAL_START
        and chunk.get("ordinal_end") == ORDINAL_END
        and chunk.get("site_count") == EXPECTED_SITE_COUNT
        and chunk.get("root_count") == EXPECTED_ROOT_COUNT
        and chunk.get("site_sha256") == EXPECTED_CHUNK_SITE_SHA256
        and chunk.get("root_sha256") == EXPECTED_CHUNK_ROOT_SHA256
        and chunk.get("pending_coordinate_sha256")
        == EXPECTED_PENDING_COORDINATE_SHA256
        and chunk.get("pending_row_upper_bound")
        == EXPECTED_PENDING_ROW_UPPER_BOUND,
        "selector 538 chunk-1 assignment drifted",
    )
    return assignment, chunk


def load_world() -> dict[str, Any]:
    return BASE.load_world()


def validate_context(
    recorded: Mapping[str, Any],
    *,
    records: Mapping[tuple[int, int], Any],
    site: str,
) -> None:
    left, right = adjacent_literals(records, site)
    require(
        recorded.get("left") == left
        and recorded.get("right") == right
        and recorded.get("joined_utf8_sha256")
        == sha256_bytes((left + right).encode("utf-8")),
        f"private multilingual context drifted at {site}",
    )


def validate_chunk0_overlap(
    reviewed_map: Mapping[str, str],
    recorded: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        sha256_file(CHUNK0_PRIVATE_HANDOFF_PATH)
        == EXPECTED_CHUNK0_PRIVATE_HANDOFF_SHA256,
        "chunk-0 private handoff drifted",
    )
    chunk0 = load_json_exact(CHUNK0_PRIVATE_HANDOFF_PATH)
    chunk0_reviewed = chunk0.get("exact_maps", {}).get("reviewed")
    require(isinstance(chunk0_reviewed, dict), "chunk-0 reviewed map is absent")
    overlap = sorted(set(reviewed_map) & set(chunk0_reviewed), key=parse_coordinate)
    identical = all(
        reviewed_map[coordinate] == chunk0_reviewed[coordinate]
        for coordinate in overlap
    )
    manifest = [
        [
            coordinate,
            sha256_bytes(str(reviewed_map[coordinate]).encode("utf-8")),
        ]
        for coordinate in overlap
    ]
    digest = canonical_sha256(manifest)
    require(
        identical
        and recorded.get("coordinate_count") == len(overlap)
        and recorded.get("all_overlapping_values_identical") is True
        and recorded.get("canonical_sha256") == digest,
        "chunk-0 exact-map overlap contract drifted",
    )
    return {
        "all_overlapping_values_identical": identical,
        "canonical_sha256": digest,
        "coordinate_count": len(overlap),
    }


def validate_private_handoff(
    handoff: Mapping[str, Any],
    *,
    assignment: Mapping[str, Any],
    chunk: Mapping[str, Any],
    world: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        handoff.get("schema") == PRIVATE_SCHEMA,
        "private handoff schema drifted",
    )
    privacy = handoff.get("privacy", {})
    scope = handoff.get("scope", {})
    counts = handoff.get("counts", {})
    require(
        privacy.get("classification") == "private"
        and privacy.get("contains_dialogue_bodies") is True
        and privacy.get("public") is False
        and privacy.get("shared_integration_mutated") is False
        and privacy.get("steam_write_performed") is False,
        "private handoff privacy contract drifted",
    )
    require(
        scope.get("assignment_sha256") == EXPECTED_ASSIGNMENT_SHA256
        and scope.get("baseline_candidate_sha256")
        == EXPECTED_BASELINE_CANDIDATE_SHA256
        and scope.get("integrated_ledger_sha256") == EXPECTED_LEDGER_SHA256
        and scope.get("chunk0_private_handoff_sha256")
        == EXPECTED_CHUNK0_PRIVATE_HANDOFF_SHA256
        and scope.get("selector_coordinate") == f"0:{SELECTOR}:0"
        and scope.get("ordinal_start") == ORDINAL_START
        and scope.get("ordinal_end") == ORDINAL_END
        and scope.get("site_sha256") == EXPECTED_CHUNK_SITE_SHA256
        and tuple(scope.get("terminal_coordinates", ()))
        == tuple(f"0:{terminal}:0" for terminal in TERMINALS),
        "private handoff scope drifted",
    )
    require(
        counts
        == {
            "accepted": EXPECTED_ACCEPTED,
            "accepted_assemblies": EXPECTED_ACCEPTED_ASSEMBLIES,
            "assemblies": EXPECTED_ASSEMBLY_COUNT,
            "keep": EXPECTED_KEEP,
            "reject": EXPECTED_REJECT,
            "rejected_assemblies": EXPECTED_REJECTED_ASSEMBLIES,
            "rewrite": EXPECTED_REWRITE,
            "sites": EXPECTED_SITE_COUNT,
        },
        "private handoff counts drifted",
    )

    site_rows = handoff.get("site_reviews")
    require(
        isinstance(site_rows, list) and len(site_rows) == EXPECTED_SITE_COUNT,
        "private site review cardinality drifted",
    )
    assignment_rows = assignment["site_assignments"][
        ORDINAL_START : ORDINAL_END + 1
    ]
    exact_maps = handoff.get("exact_maps", {})
    rewrite_map = exact_maps.get("rewrite")
    keep_map = exact_maps.get("keep")
    reject_map = exact_maps.get("reject")
    reviewed_map = exact_maps.get("reviewed")
    require(
        all(
            isinstance(value, dict)
            for value in (rewrite_map, keep_map, reject_map, reviewed_map)
        ),
        "private exact maps are absent",
    )
    overlap = validate_chunk0_overlap(
        reviewed_map,
        handoff.get("chunk0_exact_map_overlap", {}),
    )

    candidate_records = world["candidate_records"]
    current_records = world["current_records"]
    terminal_candidate = terminal_literals(candidate_records)
    terminal_current = terminal_literals(current_records)
    replacements = {
        parse_coordinate(coordinate): str(text)
        for coordinate, text in rewrite_map.items()
    }
    proposal_blob = BASE_AUDIT.rebuild_packed_with_literals(
        world["candidate_blob"],
        replacements,
    )
    proposal_records = BASE_AUDIT.records_from_blob(proposal_blob)

    decisions: Counter[str] = Counter()
    rewrite_coordinates: set[str] = set()
    keep_coordinates: set[str] = set()
    reject_coordinates: set[str] = set()
    accepted_sites: list[str] = []
    rejected_sites: list[str] = []
    assembly_manifest: list[list[Any]] = []
    accepted_assembly_manifest: list[list[Any]] = []

    for assignment_row, row in zip(assignment_rows, site_rows):
        ordinal = int(assignment_row["ordinal"])
        site = str(assignment_row["site"])
        coordinate = str(assignment_row["left_coordinate"])
        decision = str(row.get("decision"))
        reviewed_left = row.get("reviewed_left_translation")
        require(
            row.get("ordinal") == ordinal
            and row.get("site") == site
            and row.get("left_coordinate") == coordinate
            and decision in {"rewrite", "keep", "reject"}
            and isinstance(reviewed_left, str),
            f"private site identity/decision drifted at ordinal {ordinal}",
        )
        decisions[decision] += 1
        if decision == "rewrite":
            rewrite_coordinates.add(coordinate)
            accepted_sites.append(site)
        elif decision == "keep":
            keep_coordinates.add(coordinate)
            accepted_sites.append(site)
        else:
            reject_coordinates.add(coordinate)
            rejected_sites.append(site)

        baseline_left, baseline_right = adjacent_literals(
            candidate_records, site
        )
        proposal_left, proposal_right = adjacent_literals(proposal_records, site)
        current_left, current_right = adjacent_literals(current_records, site)
        require(
            row.get("baseline_candidate_left") == baseline_left
            and row.get("baseline_candidate_right") == baseline_right
            and row.get("reviewed_candidate_right") == proposal_right
            and row.get("current_left") == current_left
            and row.get("current_right") == current_right,
            f"private Korean context drifted at {site}",
        )
        require(
            reviewed_map.get(coordinate) == reviewed_left,
            f"private reviewed map drifted at {coordinate}",
        )
        if decision == "rewrite":
            require(
                rewrite_map.get(coordinate) == reviewed_left
                and reviewed_left != baseline_left
                and proposal_left == reviewed_left,
                f"private rewrite map drifted at {coordinate}",
            )
        elif decision == "keep":
            require(
                keep_map.get(coordinate) == reviewed_left
                and reviewed_left == baseline_left
                and proposal_left == baseline_left,
                f"private keep map drifted at {coordinate}",
            )
        else:
            require(
                isinstance(reject_map.get(coordinate), str)
                and reject_map.get(coordinate) == row.get("reject_reason")
                and proposal_left == baseline_left,
                f"private reject map drifted at {coordinate}",
            )

        authority = row.get("multilingual_authority", {})
        require(
            authority.get("jp_is_semantic_authority") is True
            and authority.get("fresh_review_completed") is True
            and authority.get("speaker_tone_reviewed") is True
            and authority.get("historical_terms_reviewed") is True,
            f"private semantic proof drifted at {site}",
        )
        for language in ("jp", "sc", "tc", "en"):
            context = authority.get(language)
            require(
                isinstance(context, dict),
                f"private {language} context absent at {site}",
            )
            validate_context(
                context,
                records=world["language_records"][language],
                site=site,
            )
            require(
                context.get("available")
                is bool(assignment_row["language_available"][language]),
                f"private {language} availability drifted at {site}",
            )

        root = site_root(site)
        control = row.get("control_and_protected_proof", {})
        require(
            control.get("baseline_record_gap_sha256")
            == record_gap_sha256(candidate_records[root])
            and control.get("proposal_record_gap_sha256")
            == record_gap_sha256(proposal_records[root])
            and control.get("reviewed_outer_whitespace_signature")
            == outer_whitespace_signature(reviewed_left)
            and control.get("baseline_outer_whitespace_signature")
            == outer_whitespace_signature(baseline_left)
            and control.get("outer_whitespace_preserved") is True
            and control.get("literal_linebreak_count_preserved") is True
            and control.get("record_control_gaps_preserved") is True
            and record_gap_sha256(candidate_records[root])
            == record_gap_sha256(proposal_records[root]),
            f"private control/protected proof drifted at {site}",
        )

        branches = row.get("assemblies")
        require(
            isinstance(branches, list) and len(branches) == len(TERMINALS),
            f"private assembly branch count drifted at {site}",
        )
        all_width = True
        all_register = True
        for terminal, branch in zip(TERMINALS, branches):
            reviewed_assembly = (
                reviewed_left + terminal_candidate[terminal] + proposal_right
            )
            current_assembly = (
                current_left + terminal_current[terminal] + current_right
            )
            reviewed_lines = line_metrics(reviewed_assembly)
            current_lines = line_metrics(current_assembly)
            nonexpanding = current_relative_nonexpanding(
                reviewed_lines, current_lines
            )
            grammar_compatible = bool(row.get("grammar_compatible"))
            register_proven = decision != "reject" and grammar_compatible
            require(
                branch.get("terminal_coordinate") == f"0:{terminal}:0"
                and branch.get("register")
                == ("plain" if terminal in {1917, 1922} else "polite")
                and branch.get("reviewed_terminal") == terminal_candidate[terminal]
                and branch.get("current_terminal") == terminal_current[terminal]
                and branch.get("reviewed_assembly") == reviewed_assembly
                and branch.get("current_assembly") == current_assembly
                and branch.get("reviewed_lines") == reviewed_lines
                and branch.get("current_lines") == current_lines
                and branch.get("line_count_match")
                is (len(reviewed_lines) == len(current_lines))
                and branch.get("current_relative_raw_g1n_nonexpanding")
                is nonexpanding
                and branch.get("register_and_grammar_proven")
                is register_proven,
                f"private assembly proof drifted at {site}/0:{terminal}:0",
            )
            all_width = all_width and nonexpanding
            all_register = all_register and register_proven
            assembly_manifest.append(
                [
                    ordinal,
                    site,
                    terminal,
                    decision,
                    sha256_bytes(reviewed_assembly.encode("utf-8")),
                    sha256_bytes(current_assembly.encode("utf-8")),
                    nonexpanding,
                    register_proven,
                ]
            )
            if decision != "reject":
                accepted_assembly_manifest.append(
                    [
                        site,
                        terminal,
                        sha256_bytes(reviewed_assembly.encode("utf-8")),
                        sha256_bytes(current_assembly.encode("utf-8")),
                        [
                            line["raw_g1n_width_px"]
                            for line in reviewed_lines
                        ],
                        [
                            line["raw_g1n_width_px"]
                            for line in current_lines
                        ],
                    ]
                )
        require(
            row.get("all_seven_width_branches_nonexpanding") is all_width
            and row.get("all_seven_register_branches_proven") is all_register,
            f"private seven-branch summary drifted at {site}",
        )
        if decision != "reject":
            require(
                all_width and all_register,
                f"accepted site lacks seven-branch proof: {site}",
            )
        else:
            require(
                not (all_width and all_register),
                f"rejected site has no blocker: {site}",
            )

    require(
        decisions
        == Counter(
            {
                "rewrite": EXPECTED_REWRITE,
                "keep": EXPECTED_KEEP,
                "reject": EXPECTED_REJECT,
            }
        )
        and set(rewrite_map) == rewrite_coordinates
        and set(keep_map) == keep_coordinates
        and set(reject_map) == reject_coordinates
        and set(reviewed_map)
        == rewrite_coordinates | keep_coordinates | reject_coordinates,
        "private decision/exact-map coverage drifted",
    )
    require(
        len(accepted_assembly_manifest) == EXPECTED_ACCEPTED_ASSEMBLIES,
        "accepted assembly cardinality drifted",
    )

    changed_roots = {
        root
        for root in candidate_records
        if candidate_records[root].data != proposal_records[root].data
    }
    expected_changed_roots = {
        parse_coordinate(coordinate)[:2] for coordinate in rewrite_map
    }
    require(
        changed_roots == expected_changed_roots,
        "proposal changed-record universe drifted",
    )
    proposal_candidate_sha256 = sha256_bytes(proposal_blob)
    require(
        handoff.get("digests", {}).get("proposal_candidate_sha256")
        == proposal_candidate_sha256
        and handoff.get("digests", {}).get("assembly_canonical_sha256")
        == canonical_sha256(assembly_manifest)
        and handoff.get("digests", {}).get("chunk0_overlap_canonical_sha256")
        == overlap["canonical_sha256"],
        "private proposal/assembly/overlap digest drifted",
    )
    return {
        "accepted_sites": accepted_sites,
        "accepted_assembly_manifest": accepted_assembly_manifest,
        "assembly_manifest": assembly_manifest,
        "chunk0_overlap": overlap,
        "keep_map": keep_map,
        "proposal_candidate_sha256": proposal_candidate_sha256,
        "reject_map": reject_map,
        "rejected_sites": rejected_sites,
        "rewrite_map": rewrite_map,
        "site_rows": site_rows,
        "proposal_records": proposal_records,
    }


def coordinates_for_roots(
    roots: Iterable[tuple[int, int]],
    grouped: Mapping[tuple[int, int], Sequence[str]],
) -> set[str]:
    return {
        coordinate
        for root in roots
        for coordinate in grouped.get(root, ())
    }


def build_runtime_classification(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    accepted_roots: set[tuple[int, int]],
    rejected_roots: set[tuple[int, int]],
    rewrite_map: Mapping[str, str],
    world: Mapping[str, Any],
    proposal_records: Mapping[tuple[int, int], Any],
) -> dict[str, Any]:
    pending_by_root = CLOSURE.grouped_coordinates(
        predecessor_rows, "pending"
    )
    verified_by_root = CLOSURE.grouped_coordinates(
        predecessor_rows, "verified"
    )
    promotion_roots = accepted_roots & set(pending_by_root)
    promotion_coordinates = coordinates_for_roots(
        promotion_roots, pending_by_root
    )
    rejected_pending_roots = rejected_roots & set(pending_by_root)
    rejected_pending_coordinates = coordinates_for_roots(
        rejected_pending_roots, pending_by_root
    )

    inputs = types.SimpleNamespace(
        pk_source_records=world["language_records"]["jp"],
        pk_current_records=world["current_records"],
        pk_candidate_records=proposal_records,
    )
    _profiles, candidate_edges = (
        CLOSURE.CROSS.RESIDUAL_AUDIT.build_record_profiles(inputs=inputs)
    )
    source_edges = CLOSURE.HONORIFIC.graph_edges(
        world["language_records"]["jp"],
        conservative_operand_scan=True,
    )
    terminal_roots = {(0, terminal) for terminal in TERMINALS}
    candidate_affected = CLOSURE.HONORIFIC.reverse_ancestors(
        edges=candidate_edges,
        targets=tuple(terminal_roots),
    )
    source_affected = CLOSURE.HONORIFIC.reverse_ancestors(
        edges=source_edges,
        targets=tuple(terminal_roots),
    )
    renewal_roots = set(verified_by_root) & (
        candidate_affected | source_affected
    )
    renewal_coordinates = coordinates_for_roots(
        renewal_roots, verified_by_root
    )
    decision_coordinates = promotion_coordinates | renewal_coordinates
    require(
        len(promotion_roots) == EXPECTED_PROMOTION_ROOTS
        and len(promotion_coordinates) == EXPECTED_POTENTIAL_PROMOTION_COUNT
        and len(rejected_pending_roots) == EXPECTED_REJECTED_PENDING_ROOTS
        and len(rejected_pending_coordinates)
        == EXPECTED_BLOCKED_PENDING_COUNT
        and len(candidate_affected) == EXPECTED_CANDIDATE_AFFECTED_ROOTS
        and len(source_affected) == EXPECTED_SOURCE_AFFECTED_ROOTS
        and len(renewal_roots) == EXPECTED_RENEWAL_ROOTS
        and len(renewal_coordinates) == EXPECTED_RENEWAL_ROWS
        and len(decision_coordinates) == EXPECTED_DECISION_ROWS
        and set(rewrite_map) <= decision_coordinates,
        "runtime promotion/renewal closure partition drifted",
    )

    action_manifest: list[list[str]] = []
    action_counts: Counter[str] = Counter()
    for coordinate in sorted(decision_coordinates, key=parse_coordinate):
        is_override = coordinate in rewrite_map
        is_promotion = coordinate in promotion_coordinates
        if is_promotion:
            action = (
                "translation_override_and_runtime_promotion"
                if is_override
                else "runtime_promotion"
            )
        else:
            action = (
                "translation_override_and_verification_renewal"
                if is_override
                else "verification_renewal"
            )
        action_counts[action] += 1
        action_manifest.append([coordinate, action])
    require(
        dict(action_counts) == EXPECTED_ACTION_COUNTS,
        "runtime closure action counts drifted",
    )
    return {
        "action_counts": dict(sorted(action_counts.items())),
        "action_manifest": action_manifest,
        "candidate_affected": candidate_affected,
        "decision_coordinates": decision_coordinates,
        "promotion_coordinates": promotion_coordinates,
        "promotion_roots": promotion_roots,
        "rejected_pending_coordinates": rejected_pending_coordinates,
        "rejected_pending_roots": rejected_pending_roots,
        "renewal_coordinates": renewal_coordinates,
        "renewal_roots": renewal_roots,
        "source_affected": source_affected,
    }


def build_report() -> tuple[dict[str, Any], dict[str, str]]:
    assignment, chunk = load_assignment()
    live_steam_path = Path(CALLER.LIVE_STEAM_PK)
    require(live_steam_path.is_file(), "live Steam PK msggame is absent")
    steam_before = sha256_file(live_steam_path)
    world = load_world()
    handoff = load_json_exact(PRIVATE_HANDOFF_PATH)
    private_sha256 = sha256_file(PRIVATE_HANDOFF_PATH)
    if EXPECTED_PRIVATE_HANDOFF_SHA256 is not None:
        require(
            private_sha256 == EXPECTED_PRIVATE_HANDOFF_SHA256,
            "private handoff hash drifted",
        )
    validated = validate_private_handoff(
        handoff,
        assignment=assignment,
        chunk=chunk,
        world=world,
    )
    steam_after = sha256_file(live_steam_path)
    require(steam_before == steam_after, "Steam archive changed during review")

    rewrite_coordinates = sorted(
        validated["rewrite_map"], key=parse_coordinate
    )
    keep_coordinates = sorted(validated["keep_map"], key=parse_coordinate)
    reject_coordinates = sorted(validated["reject_map"], key=parse_coordinate)
    accepted_sites = sorted(validated["accepted_sites"])
    rejected_sites = sorted(validated["rejected_sites"])
    accepted_roots = {site_root(site) for site in accepted_sites}
    rejected_roots = {site_root(site) for site in rejected_sites}
    require(
        accepted_roots.isdisjoint(rejected_roots),
        "chunk-1 accepted/rejected roots overlap",
    )
    pending_coordinates = list(chunk["pending_coordinates"])
    potential_promotion_coordinates = [
        coordinate
        for coordinate in pending_coordinates
        if parse_coordinate(coordinate)[:2] in accepted_roots
    ]
    blocked_pending_coordinates = [
        coordinate
        for coordinate in pending_coordinates
        if parse_coordinate(coordinate)[:2] in rejected_roots
    ]
    require(
        len(accepted_roots) == EXPECTED_ACCEPTED_ROOTS
        and len(rejected_roots) == EXPECTED_REJECTED_ROOTS
        and len(potential_promotion_coordinates)
        == EXPECTED_POTENTIAL_PROMOTION_COUNT
        and len(blocked_pending_coordinates)
        == EXPECTED_BLOCKED_PENDING_COUNT
        and len(potential_promotion_coordinates)
        + len(blocked_pending_coordinates)
        == EXPECTED_PENDING_ROW_UPPER_BOUND,
        "chunk-1 pending-root partition drifted",
    )
    predecessor_rows, predecessor_report = CLOSURE.load_predecessor()
    require(
        len(predecessor_rows) == EXPECTED_PREDECESSOR_ROWS
        and predecessor_report.get("result", {}).get(
            "runtime_review_pending"
        )
        == EXPECTED_PREDECESSOR_PENDING,
        "runtime classification predecessor drifted",
    )
    runtime = build_runtime_classification(
        predecessor_rows=predecessor_rows,
        accepted_roots=accepted_roots,
        rejected_roots=rejected_roots,
        rewrite_map=validated["rewrite_map"],
        world=world,
        proposal_records=validated["proposal_records"],
    )

    site_rows = validated["site_rows"]
    language_counts = {
        language: sum(
            bool(row["multilingual_authority"][language]["available"])
            for row in site_rows
        )
        for language in ("jp", "sc", "tc", "en")
    }
    blocker_counts = Counter(
        str(row["reject_reason"]) for row in site_rows
        if row["decision"] == "reject"
    )
    overlap = validated["chunk0_overlap"]

    report: dict[str, Any] = {
        "distribution_policy": {
            "private_handoff_contains_dialogue_bodies": True,
            "private_handoff_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_translation_map_keys": False,
        },
        "inputs": {
            "assignment_sha256": EXPECTED_ASSIGNMENT_SHA256,
            "baseline_candidate_sha256": EXPECTED_BASELINE_CANDIDATE_SHA256,
            "chunk0_private_handoff_sha256":
                EXPECTED_CHUNK0_PRIVATE_HANDOFF_SHA256,
            "integrated_ledger_sha256": EXPECTED_LEDGER_SHA256,
        },
        "method": METHOD,
        "proof": {
            "accepted_assembly_branches": EXPECTED_ACCEPTED_ASSEMBLIES,
            "accepted_assembly_canonical_sha256": canonical_sha256(
                validated["accepted_assembly_manifest"]
            ),
            "all_71_sites_classified": True,
            "all_accepted_current_relative_raw_g1n_nonexpanding": True,
            "all_accepted_register_branches_proven": True,
            "all_changed_record_control_gaps_preserved": True,
            "all_literal_linebreak_counts_preserved": True,
            "all_outer_whitespace_signatures_preserved": True,
            "assembly_branches_recorded": EXPECTED_ASSEMBLY_COUNT,
            "assembly_canonical_sha256": canonical_sha256(
                validated["assembly_manifest"]
            ),
            "auxiliary_language_available_counts": language_counts,
            "blocker_reason_counts": dict(sorted(blocker_counts.items())),
            "chunk0_exact_map_overlap": overlap,
            "candidate_affected_records": len(
                runtime["candidate_affected"]
            ),
            "fresh_semantic_review_sites": EXPECTED_SITE_COUNT,
            "historical_term_review_sites": EXPECTED_SITE_COUNT,
            "jp_authority_sites": EXPECTED_SITE_COUNT,
            "rejected_assembly_branches": EXPECTED_REJECTED_ASSEMBLIES,
            "runtime_action_counts": runtime["action_counts"],
            "runtime_action_manifest_canonical_sha256": canonical_sha256(
                runtime["action_manifest"]
            ),
            "speaker_tone_review_sites": EXPECTED_SITE_COUNT,
            "source_affected_records": len(runtime["source_affected"]),
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": {
            "accepted_root_count": len(accepted_roots),
            "accepted_root_sha256": root_digest(accepted_roots),
            "accepted_site_count": EXPECTED_ACCEPTED,
            "accepted_site_sha256": site_digest(accepted_sites),
            "decision_delta_coordinate_count": len(
                runtime["decision_coordinates"]
            ),
            "decision_delta_coordinate_sha256": coordinate_digest(
                runtime["decision_coordinates"]
            ),
            "exact_override_coordinate_count": len(
                validated["rewrite_map"]
            ),
            "exact_override_coordinate_sha256": coordinate_digest(
                validated["rewrite_map"]
            ),
            "blocked_pending_coordinate_count":
                len(blocked_pending_coordinates),
            "blocked_pending_coordinate_sha256": coordinate_digest(
                blocked_pending_coordinates
            ),
            "keep_coordinate_count": EXPECTED_KEEP,
            "keep_coordinate_sha256": coordinate_digest(keep_coordinates),
            "potential_promotion_coordinate_count":
                len(potential_promotion_coordinates),
            "potential_promotion_coordinate_sha256": coordinate_digest(
                potential_promotion_coordinates
            ),
            "rejected_pending_root_count": len(
                runtime["rejected_pending_roots"]
            ),
            "rejected_pending_root_sha256": root_digest(
                runtime["rejected_pending_roots"]
            ),
            "proposal_candidate_sha256":
                validated["proposal_candidate_sha256"],
            "reject_coordinate_count": EXPECTED_REJECT,
            "reject_coordinate_sha256": coordinate_digest(reject_coordinates),
            "rejected_root_count": len(rejected_roots),
            "rejected_root_sha256": root_digest(rejected_roots),
            "rejected_site_count": EXPECTED_REJECT,
            "rejected_site_sha256": site_digest(rejected_sites),
            "rewrite_coordinate_count": EXPECTED_REWRITE,
            "rewrite_coordinate_sha256": coordinate_digest(
                rewrite_coordinates
            ),
            "runtime_promotion_coordinate_count": len(
                runtime["promotion_coordinates"]
            ),
            "runtime_promotion_coordinate_sha256": coordinate_digest(
                runtime["promotion_coordinates"]
            ),
            "runtime_promotion_root_count": len(
                runtime["promotion_roots"]
            ),
            "runtime_promotion_root_sha256": root_digest(
                runtime["promotion_roots"]
            ),
            "runtime_review_pending_after": EXPECTED_PENDING_AFTER,
            "runtime_review_pending_before": EXPECTED_PREDECESSOR_PENDING,
            "verification_renewal_coordinate_count": len(
                runtime["renewal_coordinates"]
            ),
            "verification_renewal_coordinate_sha256": coordinate_digest(
                runtime["renewal_coordinates"]
            ),
            "verification_renewal_root_count": len(
                runtime["renewal_roots"]
            ),
            "verification_renewal_root_sha256": root_digest(
                runtime["renewal_roots"]
            ),
        },
        "schema": PUBLIC_SCHEMA,
        "scope": {
            "chunk_id": 1,
            "ordinal_end": ORDINAL_END,
            "ordinal_start": ORDINAL_START,
            "pending_coordinate_sha256":
                EXPECTED_PENDING_COORDINATE_SHA256,
            "pending_row_upper_bound": EXPECTED_PENDING_ROW_UPPER_BOUND,
            "root_count": EXPECTED_ROOT_COUNT,
            "root_sha256": EXPECTED_CHUNK_ROOT_SHA256,
            "selector": SELECTOR,
            "site_count": EXPECTED_SITE_COUNT,
            "site_sha256": EXPECTED_CHUNK_SITE_SHA256,
            "terminal_count": len(TERMINALS),
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    report["guards"] = {
        "private_handoff_sha256": private_sha256,
        "report_payload_sha256": canonical_sha256(report),
        "steam_archive_sha256_before": steam_before,
        "steam_archive_sha256_after": steam_after,
    }

    frozen = {
        "accepted_root_sha256": report["result"]["accepted_root_sha256"],
        "accepted_assembly_sha256": report["proof"][
            "accepted_assembly_canonical_sha256"
        ],
        "accepted_site_sha256": report["result"]["accepted_site_sha256"],
        "assembly_sha256": report["proof"]["assembly_canonical_sha256"],
        "blocked_pending_coordinate_sha256": report["result"][
            "blocked_pending_coordinate_sha256"
        ],
        "chunk0_overlap_sha256": overlap["canonical_sha256"],
        "action_sha256": report["proof"][
            "runtime_action_manifest_canonical_sha256"
        ],
        "decision_coordinate_sha256": report["result"][
            "decision_delta_coordinate_sha256"
        ],
        "keep_coordinate_sha256": report["result"][
            "keep_coordinate_sha256"
        ],
        "private_handoff_sha256": private_sha256,
        "proposal_candidate_sha256": report["result"][
            "proposal_candidate_sha256"
        ],
        "potential_promotion_coordinate_sha256": report["result"][
            "potential_promotion_coordinate_sha256"
        ],
        "promotion_root_sha256": report["result"][
            "runtime_promotion_root_sha256"
        ],
        "reject_coordinate_sha256": report["result"][
            "reject_coordinate_sha256"
        ],
        "rejected_root_sha256": report["result"]["rejected_root_sha256"],
        "rejected_pending_root_sha256": report["result"][
            "rejected_pending_root_sha256"
        ],
        "rejected_site_sha256": report["result"]["rejected_site_sha256"],
        "rewrite_coordinate_sha256": report["result"][
            "rewrite_coordinate_sha256"
        ],
        "renewal_coordinate_sha256": report["result"][
            "verification_renewal_coordinate_sha256"
        ],
        "renewal_root_sha256": report["result"][
            "verification_renewal_root_sha256"
        ],
    }
    return report, frozen


def validate_frozen(frozen: Mapping[str, str]) -> None:
    expected = {
        "accepted_assembly_sha256": EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
        "accepted_root_sha256": EXPECTED_ACCEPTED_ROOT_SHA256,
        "accepted_site_sha256": EXPECTED_ACCEPTED_SITE_SHA256,
        "assembly_sha256": EXPECTED_ASSEMBLY_SHA256,
        "blocked_pending_coordinate_sha256":
            EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256,
        "action_sha256": EXPECTED_ACTION_SHA256,
        "chunk0_overlap_sha256": EXPECTED_CHUNK0_OVERLAP_SHA256,
        "decision_coordinate_sha256": EXPECTED_DECISION_COORDINATE_SHA256,
        "keep_coordinate_sha256": EXPECTED_KEEP_COORDINATE_SHA256,
        "private_handoff_sha256": EXPECTED_PRIVATE_HANDOFF_SHA256,
        "proposal_candidate_sha256": EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        "potential_promotion_coordinate_sha256":
            EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256,
        "promotion_root_sha256": EXPECTED_PROMOTION_ROOT_SHA256,
        "reject_coordinate_sha256": EXPECTED_REJECT_COORDINATE_SHA256,
        "rejected_root_sha256": EXPECTED_REJECTED_ROOT_SHA256,
        "rejected_pending_root_sha256":
            EXPECTED_REJECTED_PENDING_ROOT_SHA256,
        "rejected_site_sha256": EXPECTED_REJECTED_SITE_SHA256,
        "rewrite_coordinate_sha256": EXPECTED_REWRITE_COORDINATE_SHA256,
        "renewal_coordinate_sha256": EXPECTED_RENEWAL_COORDINATE_SHA256,
        "renewal_root_sha256": EXPECTED_RENEWAL_ROOT_SHA256,
    }
    for key, value in expected.items():
        if value is not None:
            require(frozen[key] == value, f"frozen {key} drifted")


def serialized_report() -> tuple[bytes, dict[str, str]]:
    report, frozen = build_report()
    validate_frozen(frozen)
    return canonical_bytes(report) + b"\n", frozen


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    content, frozen = serialized_report()
    file_sha256 = sha256_bytes(content)
    if EXPECTED_PUBLIC_FILE_SHA256 is not None:
        require(
            file_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
            "public proposal file hash drifted",
        )
    if args.check:
        require(args.output.is_file(), f"proposal is absent: {args.output}")
        require(
            args.output.read_bytes() == content,
            "public proposal content drifted",
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)
    print(
        json.dumps(
            {
                "file_sha256": file_sha256,
                "frozen": frozen,
                "output": str(args.output),
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
