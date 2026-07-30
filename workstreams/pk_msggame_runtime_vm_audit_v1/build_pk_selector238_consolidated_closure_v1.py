#!/usr/bin/env python3
"""Consolidate the two selector-238 reviews on the post-selector730 state."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
SEMANTIC_TMP = DIALOGUE_TMP / "semantic_overrides"
PUBLIC_DIR = WORKSTREAM / "public"

SCAFFOLD_PATH = WORKSTREAM / "build_pk_selector730_consolidated_closure_v1.py"
EXPECTED_SCAFFOLD_SHA256 = (
    "36203E94751006C6AD2E03642C448A235AE9C1EFB08B274A050F8E6A84E01F61"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector238_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector238_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector238_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector730_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector730_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector238_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector238_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector238_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector238_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector238_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector238_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector238_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector238_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "4C09CA6AAC9DBE0EBB83E8A855C20724721AAF1875BE0C12B45ACDA9D1AEFE40",
    "assignment_private":
        "3B8629AC3DF5E18FEA92D82EB97D0E6D87870509E1C986BEFC3069050FF6D0C8",
    "assignment_public":
        "B44358FE6CC6EAD85972255F8D360EF5B6A0B1AB2D935DBCA4CC7F4D490ACE30",
    "official_ledger":
        "9F6BD587F6EC92CD00A2E2AF9FD9E07A8B6A71405272F0D79A515C3405617C5C",
    "predecessor_decisions":
        "A56DA1B7C3465EF9CA1640A059F7EE46EC73B0C4C95B2849551CDA34A91A8DDE",
    "chunk0_builder":
        "D12BF1F2001E0D2DB5CD8A0C59C1E9028C3505C8565A359B7FBC9CD59B71C622",
    "chunk0_public":
        "D22CEFEB47215C6F8F8AF48665DB13C89F94D9AFAD9430F010B27177FC99461B",
    "chunk0_decisions":
        "86EC96ED24C66CD970A697C9E41E5495FEC7043A22867D11D92F772820CFCBDB",
    "chunk0_evidence":
        "BE00AE4080DB005BF4C5D78320288A618473EA126789ACBF517D0DF500A9576B",
    "chunk1_builder":
        "286300DB0A1296BE6DF4663337FD5E8604E328F1E91F1CB25FA189AE46F05955",
    "chunk1_public":
        "ED15DDD1F1373476DF8407AA0A0DBC276D4923388D4C4CFDE428ED8FA3DAF1AE",
    "chunk1_decisions":
        "DA564E5EDE7122F53035E3FF9720E447332306F6B46AA0BDD8D9657C03B85449",
    "chunk1_evidence":
        "7C63668279BEFA32853C916480D5AAF4785455CAD4418B2E6B0B3FC39005D5C5",
}
EXPECTED_CHUNK_ROWS = (11, 16)
EXPECTED_CHUNK_SITES = (14, 13)
EXPECTED_CHUNK_PENDING_ROOTS = (7, 8)
EXPECTED_CHUNK_PENDING_ROWS = (14, 22)
EXPECTED_DECISION_ROWS = 27
EXPECTED_DECISION_ROOTS = 9
EXPECTED_PROMOTIONS = 27
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 22
EXPECTED_ACTION_COUNTS: dict[str, int] = {
    "runtime_promotion": 5,
    "translation_override_and_runtime_promotion": 22,
}
EXPECTED_PENDING_BEFORE = 6_178
EXPECTED_PENDING_AFTER = 6_151
EXPECTED_REVIEWED_SITES = 27
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "78636E8D087334417D0B8AC41BB9CA63BC609CF36782E969BAF7E046E4B5C0AE"
)
EXPECTED_SOURCE_SITES = 28
EXPECTED_SOURCE_SITE_SHA256 = (
    "43813ECB4936E1D31A7D705AC8847D0302197A340E075844A0D94A78CAB8A39D"
)
EXPECTED_SOURCE_ONLY_SITES = 1
EXPECTED_SOURCE_ONLY_SHA256 = (
    "52B8160BA78B19CEB6727EDC82F1D93599D79C0D3777EA849456B52397A51CFE"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "5D4CDF1CEB8C733B0E22C7AA6185D9FF6C5C4C500176E99A6AACB3D89F7E0140"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "311DD27E8C260B7438EDF90FFB944EAEC25C3462C2C8E6BDA196BCF89DEDF362"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "464E10C8A1DCFEF1B73492494A92601C01AC45FADE7F9D63D9691A931208F706"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "EED5D974C2CCA3E2C2186AEDC0DF3A480C95062942D55ECC3E966B8B94207B5E"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "E7D01ED5F17258F69B7A74858EC5D442FF39E9F2551426F903AAF83E1D6AA8ED"
)
EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_DIRECT_BRANCHES = 105
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "6C06A0C6702109D17663270FB6946155D28B805F6D81A71CFC522A12F9B75B58",
    "private_evidence":
        "2EB97D4A69E93FE9E61FD3121E964079EB9F565B9A26E268BFC38E4901D711D6",
    "public_coverage":
        "2F282F7D2A1959762B5F596F4BC50483950E796324AB0C162377BF7A36F02F22",
    "public_promotion":
        "E035169C0348DD03ABCBF6056EF392F4381D36ABE1B31634F2A3544D1DF0E381",
    "final_candidate":
        "9E5C60A451DB7CCA7B046AFD8CFF199CB3665E003CB0C751120478F693D20C24",
    "decision_coordinates":
        "C1631DC50708C28E6353DE1EF570F43FC65CF920A1626D1F7DB941C7BF69784A",
    "promotion_coordinates":
        "C1631DC50708C28E6353DE1EF570F43FC65CF920A1626D1F7DB941C7BF69784A",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "9B3A621F577D2AF8FCA011FCF7F9400BC63D583DB59E53FDAF3AD86EE28B59AC",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "72E1DB0AA8BF1695970847D4EC103E00E88F2FD0715859A287FB4AC018B7FAF3",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCAFFOLD = load_module(SCAFFOLD_PATH, "selector238_closure_scaffold")
WRAPPER = SCAFFOLD.WRAPPER
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector238_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = SCAFFOLD.configure_base


def validate_chunk_evidence(
    assignment: Mapping[str, Any],
    chunk_rows: Sequence[Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    evidence = [BASE.load_json(path) for path in CHUNK_EVIDENCE]
    assigned_chunks = assignment["chunks"]
    all_sites: set[str] = set()
    all_pending_roots: set[str] = set()
    all_pending_coordinates: set[str] = set()
    all_decision_coordinates: set[str] = set()
    for chunk_id, rows in enumerate(chunk_rows):
        assigned = assigned_chunks[chunk_id]
        chunk_evidence = evidence[chunk_id]
        assigned_sites = set(map(str, assigned["sites"]))
        assigned_roots = set(map(str, assigned["roots"]))
        pending_coordinates = set(map(str, assigned["pending_coordinates"]))
        pending_roots = {
            BASE.coordinate_root(coordinate)
            for coordinate in pending_coordinates
        }
        decision_coordinates = {str(row["coordinate"]) for row in rows}
        decision_roots = {
            BASE.coordinate_root(coordinate)
            for coordinate in decision_coordinates
        }
        counts = chunk_evidence["counts"]
        proof = chunk_evidence["proof"]
        if chunk_id == 0:
            accepted_coordinates = decision_coordinates
            blocked_coordinates = pending_coordinates - decision_coordinates
            blocked_roots = {
                str(row["root"])
                for row in chunk_evidence["blocked_root_reasons"]
            }
            read_only_roots = assigned_roots - pending_roots
        else:
            accepted_coordinates = set(
                map(str, chunk_evidence["accepted_pending_coordinates"])
            )
            blocked_coordinates = set(
                map(str, chunk_evidence["blocked_pending_coordinates"])
            )
            blocked_roots = {
                BASE.coordinate_root(coordinate)
                for coordinate in blocked_coordinates
            }
            review_by_root = {
                str(row["root"]): str(row["decision"])
                for row in chunk_evidence["pending_root_reviews"]
            }
            read_only_roots = set(
                map(str, chunk_evidence["read_only_nonpending_roots"])
            )
        BASE.require(
            len(rows) == EXPECTED_CHUNK_ROWS[chunk_id]
            and len(decision_coordinates) == len(rows)
            and accepted_coordinates == decision_coordinates,
            f"chunk{chunk_id} decision count or accepted union drifted",
        )
        BASE.require(
            len(assigned_sites) == EXPECTED_CHUNK_SITES[chunk_id]
            and len(assigned_roots) == EXPECTED_CHUNK_SITES[chunk_id]
            and int(assigned["pending_root_count"])
                == EXPECTED_CHUNK_PENDING_ROOTS[chunk_id]
            and int(assigned["pending_row_upper_bound"])
                == EXPECTED_CHUNK_PENDING_ROWS[chunk_id]
            and len(pending_roots) == EXPECTED_CHUNK_PENDING_ROOTS[chunk_id]
            and len(pending_coordinates)
                == EXPECTED_CHUNK_PENDING_ROWS[chunk_id],
            f"chunk{chunk_id} assignment coverage drifted",
        )
        BASE.require(
            pending_roots <= assigned_roots
            and decision_roots <= pending_roots
            and blocked_roots <= pending_roots
            and accepted_coordinates | blocked_coordinates
                == pending_coordinates
            and not accepted_coordinates & blocked_coordinates
            and {
                BASE.coordinate_root(coordinate)
                for coordinate in blocked_coordinates
            } == blocked_roots
            and read_only_roots == assigned_roots - pending_roots,
            f"chunk{chunk_id} pending root disposition drifted",
        )
        if chunk_id == 1:
            BASE.require(
                set(review_by_root) == pending_roots
                and {
                    root
                    for root, decision in review_by_root.items()
                    if decision.startswith("accepted_")
                } == decision_roots
                and {
                    root
                    for root, decision in review_by_root.items()
                    if decision.startswith("blocked_")
                } == blocked_roots,
                "chunk1 pending review register drifted",
            )
        BASE.require(
            counts["decision_rows"] == EXPECTED_CHUNK_ROWS[chunk_id]
            and counts["accepted_pending_rows"]
                == EXPECTED_CHUNK_ROWS[chunk_id]
            and counts["promoted_pending_rows"]
                == EXPECTED_CHUNK_ROWS[chunk_id]
            and counts["accepted_pending_roots"] == len(decision_roots)
            and counts["accepted_sites"] == len(decision_roots)
            and counts["blocked_pending_roots"] == len(blocked_roots)
            and counts["blocked_pending_rows"] == len(blocked_coordinates)
            and counts["blocked_sites"] == len(blocked_roots)
            and counts["read_only_nonpending_roots"]
                == len(read_only_roots)
            and counts["read_only_nonpending_sites"]
                == len(read_only_roots)
            and counts["selector238_accepted_branches"]
                == len(decision_roots) * 7
            and counts["selector238_blocked_pending_branches"]
                == len(blocked_roots) * 7
            and counts["selector238_read_only_nonpending_branches"]
                == len(read_only_roots) * 7
            and counts["selector238_total_branches"]
                == EXPECTED_CHUNK_SITES[chunk_id] * 7
            and counts.get(
                "selector238_all_current_relative_pass_branches",
                (len(decision_roots) + len(read_only_roots)) * 7,
            )
                == (len(decision_roots) + len(read_only_roots)) * 7
            and counts["owned_overlap_roots"]
                == int(assigned["owned_overlap_root_count"])
            and counts["prior_assembly_evidence_roots"]
                == int(assigned["prior_assembly_evidence_root_count"])
            and counts["prior_assembly_evidence_pending_rows"]
                == (10, 17)[chunk_id]
            and counts["source_only_actions"] == 0
            and counts["terminal_decision_rows"] == 0
            and counts["terminal_read_only_rows"] == 7
            and counts["non_display_actions"] == 0,
            f"chunk{chunk_id} evidence counts drifted",
        )
        if chunk_id == 0:
            manifest = chunk_evidence["assembly_manifest"]
            BASE.require(
                counts["sites"] == EXPECTED_CHUNK_SITES[chunk_id]
                and counts["roots"] == EXPECTED_CHUNK_SITES[chunk_id]
                and counts["direct_selector238_ordinal_branches"]
                    == len(decision_roots) * 7
                and counts["same_gap_branches"] == 0
                and {
                    str(row["root"]) for row in manifest
                } == decision_roots
                and sum(int(row["branch_count"]) for row in manifest)
                    == counts["conservative_assembly_branches"]
                and all(
                    int(row["line_topology_change_count"]) == 0
                    and int(row["maximum_raw_g1n_line_delta_px"]) <= 0
                    and int(row["positive_line_delta_count"]) == 0
                    for row in manifest
                )
                and proof["all_pending_rows_freshly_reviewed"] is True
                and proof["automatic_promotion_count"] == 0
                and proof[
                    "conservative_runtime_assembly_superset_nonexpanding"
                ] is True
                and proof["controls_tags_and_linebreaks_preserved"] is True
                and proof["full_dialogue_rebuild_performed"] is False
                and proof["maximum_rewrite_attempts_per_root"] == 1
                and proof["non_display_action_count"] == 0
                and proof["owned_overlap_automatic_promotion_count"] == 0
                and proof[
                    "prior_pending_evidence_automatic_promotion_count"
                ] == 0
                and proof["same_gap_branch_count"] == 0
                and proof["shared_terminal_modified"] is False
                and proof["source_only_action_count"] == 0
                and proof["steam_write_performed"] is False
                and proof["terminal_automatic_promotion_count"] == 0
                and proof["terminal_records_read_only"] is True,
                "chunk0 runtime assembly or read-only proof drifted",
            )
        else:
            BASE.require(
                counts["assigned_sites"] == EXPECTED_CHUNK_SITES[chunk_id]
                and counts["assigned_roots"]
                    == EXPECTED_CHUNK_SITES[chunk_id]
                and counts["template_roots"] == 0
                and counts["source_only_sites"]
                    == EXPECTED_SOURCE_ONLY_SITES
                and proof[
                    "accepted_assemblies_current_relative_raw_g1n_"
                    "nonexpanding"
                ] is True
                and proof["all_pending_rows_freshly_reviewed"] is True
                and proof["automatic_space_or_grammar_repair_by_vm"]
                    is False
                and proof["blocked_roots_received_no_decisions"] is True
                and proof["control_tag_change_count"] == 0
                and proof[
                    "downstream_cartesian_branches_computed_once"
                ] is True
                and proof["full_dialogue_rebuild_performed"] is False
                and proof["historical_factuality_reviewed"] is True
                and proof["linebreak_change_count"] == 0
                and proof["maximum_rewrite_attempts_per_root"] == 1
                and proof["non_display_action_count"] == 0
                and proof["owned_overlap_automatic_promotion_count"] == 0
                and proof[
                    "prior_pending_evidence_automatic_promotion_count"
                ] == 0
                and proof[
                    "reverse_overlay_recovers_official_candidate"
                ] is True
                and proof["root_independence_preserved"] is True
                and proof["selector238_branches_computed_once"] is True
                and proof["shared_terminal_modified"] is False
                and proof["source_only_action_count"] == 0
                and proof["speaker_tone_reviewed"] is True
                and proof["steam_write_performed"] is False
                and proof["terminal_automatic_promotion_count"] == 0
                and proof["terminal_records_read_only"] is True,
                "chunk1 automatic or read-only proof drifted",
            )
        BASE.require(not all_sites & assigned_sites, "chunk sites overlap")
        BASE.require(
            not all_pending_roots & pending_roots,
            "chunk pending roots overlap",
        )
        BASE.require(
            not all_pending_coordinates & pending_coordinates,
            "chunk pending coordinates overlap",
        )
        BASE.require(
            not all_decision_coordinates & decision_coordinates,
            "chunk decision coordinates overlap",
        )
        all_sites.update(assigned_sites)
        all_pending_roots.update(pending_roots)
        all_pending_coordinates.update(pending_coordinates)
        all_decision_coordinates.update(decision_coordinates)
    BASE.require(
        len(all_sites) == EXPECTED_REVIEWED_SITES
        and BASE.site_digest(all_sites) == EXPECTED_CANDIDATE_SITE_SHA256
        and len(all_pending_roots) == sum(EXPECTED_CHUNK_PENDING_ROOTS)
        and len(all_pending_coordinates) == sum(EXPECTED_CHUNK_PENDING_ROWS)
        and len(all_pending_roots) * 7 == EXPECTED_DIRECT_BRANCHES,
        "selector238 reviewed or direct-branch union drifted",
    )
    return evidence


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector730_selector238_two_chunk_single_coordinate_union_"
        "with_ordinary_branch_and_read_only_terminal_guards"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector238-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector238-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector238-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector238-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector238_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-selector238-assignment.private.v1"
    )
    BASE.validate_chunk_evidence = validate_chunk_evidence


def validate_site_call(
    records: Mapping[tuple[int, int], Any],
    site: str,
    *,
    expected: bool,
) -> None:
    block_id, record_id, gap_id, offset = map(int, site.split(":"))
    rows = [
        row
        for row in BASE.RANKING.LEGACY.record_edges(records[(block_id, record_id)])
        if row["kind"] == "C"
        and tuple(row["target"]) == (0, 238)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-238 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("utf-8"))
    proof = coverage["proof"]
    for key in tuple(proof):
        if key.startswith("all_") and key.endswith("_candidate_sites_reviewed"):
            proof.pop(key)
        if key.startswith("source_only_") and key.endswith(
            "_absent_from_current_and_candidate"
        ):
            proof.pop(key)
    proof.update({
        "all_27_candidate_sites_reviewed": True,
        "confirmed_non_display_rows_untouched": True,
        "direct_ordinary_terminal_branches_reviewed": EXPECTED_DIRECT_BRANCHES,
        "same_gap_and_multi_control_atoms_absent": True,
        "source_only_1_absent_from_current_and_candidate": True,
        "source_only_action_count_zero": True,
        "terminal_records_absent_from_decisions": True,
        "terminal_rows_pending_and_read_only": True,
    })
    coverage["guards"].pop("payload_without_guard_sha256", None)
    coverage["guards"]["payload_without_guard_sha256"] = (
        BASE.canonical_sha256(coverage)
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def terminal_values(records: Mapping[tuple[int, int], Any]) -> list[str]:
    values = []
    for record_id in range(1552, 1559):
        literals = ASSIGNMENT.ASSIGNMENT.ENGINE.parse_record_literals(
            records[(0, record_id)]
        )
        BASE.require(len(literals) == 1, "terminal literal shape drifted")
        values.append(literals[0].text)
    return values


def terminal_digest(records: Mapping[tuple[int, int], Any]) -> str:
    return BASE.sha256_bytes(
        "\0".join(terminal_values(records)).encode("utf-8")
    )


def validate_wrapper_invariants(outputs: Mapping[Path, bytes]) -> None:
    official = BASE.load_jsonl(OFFICIAL_LEDGER_PATH)
    decisions = [
        json.loads(line)
        for line in outputs[PRIVATE_DECISIONS_OUTPUT]
        .decode("utf-8", errors="strict")
        .splitlines()
        if line
    ]
    assignment = BASE.load_json(ASSIGNMENT_PRIVATE_PATH)
    decision_keys = {
        (str(row["resource"]), str(row["coordinate"])) for row in decisions
    }
    decision_roots = {
        BASE.coordinate_root(str(row["coordinate"])) for row in decisions
    }
    terminal_roots = {f"0:{record_id}" for record_id in range(1552, 1559)}
    confirmed = {
        (str(row["resource"]), str(row["coordinate"]))
        for row in official
        if row.get("scope_classification") == "confirmed_non_display"
    }
    candidate, current, source, contexts, _pending = (
        ASSIGNMENT.ASSIGNMENT.RECORDS.load_records()
    )
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed,
        "selector238 touched confirmed-non-display rows",
    )
    BASE.require(
        not decision_roots & terminal_roots
        and not assignment["same_gap_root_atoms"],
        "terminal or unexpected same-gap root entered the decision union",
    )
    BASE.require(
        terminal_digest(candidate) == EXPECTED_TERMINAL_CANDIDATE_SHA256
        and terminal_digest(current) == EXPECTED_TERMINAL_CURRENT_SHA256
        and terminal_digest(source) == EXPECTED_TERMINAL_SOURCE_SHA256
        and all(
            terminal_digest(contexts[language])
                == EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256
            for language in ("en", "sc", "tc")
        )
        and all(
            row["runtime_review"] == "pending"
            for row in assignment["shared_terminal_ownership"][
                "terminal_manifest"
            ]
        )
        and assignment["shared_terminal_ownership"][
            "automatic_status_promotion_authorized"
        ] is False,
        "selector238 terminal contract drifted",
    )
    BASE.require(
        len(decisions) == EXPECTED_DECISION_ROWS
        and all(
            row.get("fresh_semantic_review") == "approved"
            and row.get("runtime_review") == "verified"
            and "auto" not in str(row.get("action", "")).lower()
            for row in decisions
        ),
        "union contains an inherited or automatic decision",
    )


for _name, _value in {
    "ASSIGNMENT": ASSIGNMENT,
    "ASSIGNMENT_BUILDER_PATH": ASSIGNMENT_BUILDER_PATH,
    "ASSIGNMENT_PRIVATE_PATH": ASSIGNMENT_PRIVATE_PATH,
    "ASSIGNMENT_PUBLIC_PATH": ASSIGNMENT_PUBLIC_PATH,
    "OFFICIAL_LEDGER_PATH": OFFICIAL_LEDGER_PATH,
    "PREDECESSOR_DECISIONS_PATH": PREDECESSOR_DECISIONS_PATH,
    "CHUNK_BUILDERS": CHUNK_BUILDERS,
    "CHUNK_PUBLIC": CHUNK_PUBLIC,
    "CHUNK_DECISIONS": CHUNK_DECISIONS,
    "CHUNK_EVIDENCE": CHUNK_EVIDENCE,
    "PRIVATE_DECISIONS_OUTPUT": PRIVATE_DECISIONS_OUTPUT,
    "PRIVATE_EVIDENCE_OUTPUT": PRIVATE_EVIDENCE_OUTPUT,
    "PUBLIC_COVERAGE_OUTPUT": PUBLIC_COVERAGE_OUTPUT,
    "PUBLIC_PROMOTION_OUTPUT": PUBLIC_PROMOTION_OUTPUT,
    "EXPECTED_INPUT_SHA256": EXPECTED_INPUT_SHA256,
    "EXPECTED_CHUNK_ROWS": EXPECTED_CHUNK_ROWS,
    "EXPECTED_CHUNK_SITES": EXPECTED_CHUNK_SITES,
    "EXPECTED_DECISION_ROWS": EXPECTED_DECISION_ROWS,
    "EXPECTED_DECISION_ROOTS": EXPECTED_DECISION_ROOTS,
    "EXPECTED_PROMOTIONS": EXPECTED_PROMOTIONS,
    "EXPECTED_RENEWALS": EXPECTED_RENEWALS,
    "EXPECTED_OVERRIDES": EXPECTED_OVERRIDES,
    "EXPECTED_ACTION_COUNTS": EXPECTED_ACTION_COUNTS,
    "EXPECTED_PENDING_BEFORE": EXPECTED_PENDING_BEFORE,
    "EXPECTED_PENDING_AFTER": EXPECTED_PENDING_AFTER,
    "EXPECTED_REVIEWED_SITES": EXPECTED_REVIEWED_SITES,
    "EXPECTED_CANDIDATE_SITE_SHA256": EXPECTED_CANDIDATE_SITE_SHA256,
    "EXPECTED_SOURCE_SITES": EXPECTED_SOURCE_SITES,
    "EXPECTED_SOURCE_SITE_SHA256": EXPECTED_SOURCE_SITE_SHA256,
    "EXPECTED_SOURCE_ONLY_SITES": EXPECTED_SOURCE_ONLY_SITES,
    "EXPECTED_SOURCE_ONLY_SHA256": EXPECTED_SOURCE_ONLY_SHA256,
    "EXPECTED_PREDECESSOR_OVERLAPS": EXPECTED_PREDECESSOR_OVERLAPS,
    "EXPECTED_PREDECESSOR_SUPERSESSIONS":
        EXPECTED_PREDECESSOR_SUPERSESSIONS,
    "EXPECTED_CONFIRMED_NON_DISPLAY": EXPECTED_CONFIRMED_NON_DISPLAY,
    "EXPECTED_OFFICIAL_CANDIDATE_SHA256": EXPECTED_OFFICIAL_CANDIDATE_SHA256,
    "EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256":
        EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256,
    "EXPECTED_OUTPUT_SHA256": EXPECTED_OUTPUT_SHA256,
    "configure_base": configure_base,
    "validate_site_call": validate_site_call,
    "transform_outputs": transform_outputs,
    "validate_wrapper_invariants": validate_wrapper_invariants,
}.items():
    setattr(WRAPPER, _name, _value)


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(SCAFFOLD_PATH) == EXPECTED_SCAFFOLD_SHA256,
        "selector730 closure scaffold drifted",
    )
    return WRAPPER.build_outputs()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    outputs = build_outputs()
    if args.check:
        for path, content in outputs.items():
            BASE.require(
                path.is_file() and path.read_bytes() == content,
                f"selector238 closure output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(json.dumps({
        "decision_rows": EXPECTED_DECISION_ROWS,
        "pending_after": EXPECTED_PENDING_AFTER,
        "promotions": EXPECTED_PROMOTIONS,
        "source_only_actions": 0,
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
