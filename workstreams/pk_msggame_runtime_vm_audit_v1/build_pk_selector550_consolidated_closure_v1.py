#!/usr/bin/env python3
"""Build the selector-550 single-union closure on frozen post-selector610."""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
SEMANTIC_TMP = DIALOGUE_TMP / "semantic_overrides"
PUBLIC_DIR = WORKSTREAM / "public"

GENERIC_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector610_consolidated_closure_v1.py"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector550_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector550_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector550_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector610_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector610_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector550_chunk{chunk}_review_v1.py"
    for chunk in range(3)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector550_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(3)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP
    / f"pk_selector550_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(3)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector550_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(3)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector550_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector550_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector550_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector550_consolidated_closure_promotion.v1.json"
)

EXPECTED_GENERIC_BUILDER_SHA256 = (
    "3AD24E14E63526AA550B4CCCF3E35F0F8D1C3DFF6388D042A4AB258A54DF1588"
)
EXPECTED_INPUT_SHA256 = {
    "assignment_builder":
        "4ACE71CD3A28331AD22F6E865F77463B6A9B6A8B4D7A3679097F2EF3BB33895C",
    "assignment_private":
        "A692CAAEFAB77ED85DE5A07F775694ABFDDC1407E01AC158C2C1C4FC861EDFBF",
    "assignment_public":
        "A98C40EB3414E5F4DC21C264E091761A54C59F90771902A2B611EF13E90D13A8",
    "official_ledger":
        "0218C3D198C9930C8920ED8DAEB2DDD85987878035AC59DD5ECC8179D38DE12B",
    "predecessor_decisions":
        "CFEF7B6B8410397DED1FA10AF9C5AAF94D0C1B9C0D0CF1B593527A3A06D15357",
    "chunk0_builder":
        "8D2D84D5EAD4014C614A60788E89612DA5467A3F52F916F35CD60BF9CFC5D413",
    "chunk0_public":
        "80DB68BCE758BE1B7154E2CC9EB0ADC67BDE5BDD0602C18A642B21984CBFBD13",
    "chunk0_decisions":
        "1CDA6791443B9097D71430ADDB1BD16875C7F9895887C598C8A911D528B79E6D",
    "chunk0_evidence":
        "EB4A89FC716E2D896C4FD870281ECE7A8F035ECEB8D32CA9B64E55A4BCDC0DE7",
    "chunk1_builder":
        "165692DD5945FA0FAD2F9818518278CA6168A3103EEE733D02690FB739FA0CA6",
    "chunk1_public":
        "9E5A603F6B9E0FB8B93F7EBEDBDC8F55C6F99A517D5BF490E1A4CB486076AF8B",
    "chunk1_decisions":
        "A719F73ECFFD5299DD4FA8B35D2A49D4E4325F050D740E1EBFE9222F73784B06",
    "chunk1_evidence":
        "C64109153CD26F3A920065E0E2A5358C40A77D1D93A4E91E9226AC0489C42A45",
    "chunk2_builder":
        "89EA7DB9F16955C73D7E97A88ED4046ABEC4CCFBD08620AEDC1116E90D165C22",
    "chunk2_public":
        "67C1725ED839C99B3E38B7CD068E4C9AB96DD979E4113A476B5328890349CA9D",
    "chunk2_decisions":
        "5440331A2B32A6E5A4E9E7A6E1C3B7D83677187403B181E4587327FA10B4AEC4",
    "chunk2_evidence":
        "A9715CC7F3561F85B7E93664351A8380F4FBA045F52822F87039AE1A6D13F550",
}

EXPECTED_OWNER_ROWS = 225
EXPECTED_UNION_ROWS = 224
EXPECTED_DECISION_ROOTS = 123
EXPECTED_CHANGED_ROOTS = 113
EXPECTED_PROMOTIONS = 121
EXPECTED_UNION_RENEWALS = 103
EXPECTED_OWNER_RENEWALS = 104
EXPECTED_UNION_OVERRIDES = 131
EXPECTED_OWNER_OVERRIDES = 132
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 93,
    "translation_override_and_runtime_promotion": 28,
    "translation_override_and_verification_renewal": 103,
}
EXPECTED_OWNER_ACTION_COUNTS = {
    "runtime_promotion": 93,
    "translation_override_and_runtime_promotion": 28,
    "translation_override_and_verification_renewal": 104,
}
EXPECTED_CHUNK_ROWS = (84, 80, 61)
EXPECTED_CHUNK_SITES = (54, 56, 59)
EXPECTED_REVIEWED_SITES = 169
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "C192D4C89E340FF974BB38DC57039AA28626976597B12DA976AC9D9BA0C49741"
)
EXPECTED_SOURCE_SITES = 177
EXPECTED_SOURCE_SITE_SHA256 = (
    "FE4BDBC8203D9888F40CEA8735508D5FC031D7652DDA44B4AF682C62DAC61B46"
)
EXPECTED_SOURCE_ONLY_SITES = 8
EXPECTED_SOURCE_ONLY_SHA256 = (
    "D621F264506A41110B53B8D83022C4D73AE331EB2BFFF662ADBD81352A7E5308"
)
EXPECTED_OWNER_OVERLAPS = 1
EXPECTED_OWNER_OVERLAP_SHA256 = (
    "0EF1FEFAF84B1320F2CB11E1FC15D5167FF474FC9820CF4A92C721499A9AAD29"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_PENDING_BEFORE = 7_101
EXPECTED_PENDING_AFTER = 6_980
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "F80EA5958757F097885279BAB53A8456758BB99B1CE47E214FE0F54AB7152807"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "15C3BF1B4CC2E29020E5A8A6F40669555B54EEE57B04C3F7F77DF3AC680CFB93"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "42BB33CD2F7553EE3E251DDD78933F85D181F140AA133C5843F6DBDF379B53D3"
)

# Frozen after deterministic bootstrap.
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "EAA8AB5A7B71532AC5E95C0C772C990AD05A9B9DFA0D2CCFDB3A813469F0F600",
    "private_evidence":
        "A3FD969E350F80D2653E1142540ED6FC20B56683EAD1E06A82E237CBAF604B4C",
    "public_coverage":
        "42B456C6B3CA425B173366E092BDD5CD8FBDAD147DAB45EBBA6724464498B520",
    "public_promotion":
        "756397FC3F228DF36F8544E6914782BE3A7C4361F36C395134BEB675CB4F7B55",
    "decision_coordinates":
        "6F483AF06164F922C590F8FC7933E130AFE6CEF453A2D55901954975067DBF5E",
    "promotion_coordinates":
        "F8C2CF55D1BA2BC4774BED272102DD34E513D324BEC98B2DBA2822EC61E4B644",
    "renewal_coordinates":
        "1A3F07E583A179D622921643BA018A516F0FE1F6AEEEE7C85C0272E8D9DF504B",
    "override_coordinates":
        "E9948002912296EFF51065967A19A70809FBCB00E352A49F4308796A23D2EF90",
    "owner_overlap_coordinates": EXPECTED_OWNER_OVERLAP_SHA256,
    "source_only_proof": "56243B0D8041249B5852D85FC580B18D4252CE03D6D343B32CAD2EFC8AF16AFB",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(GENERIC_BUILDER_PATH, "selector550_generic_closure_v1")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector550_closure_input_v1")
BASE.ASSIGNMENT = ASSIGNMENT
BASE.ENGINE = ASSIGNMENT.ENGINE
BASE.RANKING = ASSIGNMENT.RANKING


def configure_base() -> None:
    BASE.ASSIGNMENT_BUILDER_PATH = ASSIGNMENT_BUILDER_PATH
    BASE.ASSIGNMENT_PRIVATE_PATH = ASSIGNMENT_PRIVATE_PATH
    BASE.ASSIGNMENT_PUBLIC_PATH = ASSIGNMENT_PUBLIC_PATH
    BASE.OFFICIAL_LEDGER_PATH = OFFICIAL_LEDGER_PATH
    BASE.PREDECESSOR_DECISIONS_PATH = PREDECESSOR_DECISIONS_PATH
    BASE.CHUNK_BUILDERS = CHUNK_BUILDERS
    BASE.CHUNK_PUBLIC = CHUNK_PUBLIC
    BASE.CHUNK_DECISIONS = CHUNK_DECISIONS
    BASE.CHUNK_EVIDENCE = CHUNK_EVIDENCE
    BASE.PRIVATE_DECISIONS_OUTPUT = PRIVATE_DECISIONS_OUTPUT
    BASE.PRIVATE_EVIDENCE_OUTPUT = PRIVATE_EVIDENCE_OUTPUT
    BASE.PUBLIC_COVERAGE_OUTPUT = PUBLIC_COVERAGE_OUTPUT
    BASE.PUBLIC_PROMOTION_OUTPUT = PUBLIC_PROMOTION_OUTPUT
    BASE.EXPECTED_INPUT_SHA256 = EXPECTED_INPUT_SHA256
    BASE.EXPECTED_OFFICIAL_CANDIDATE_SHA256 = EXPECTED_OFFICIAL_CANDIDATE_SHA256
    BASE.EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
        EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256
    )
    BASE.EXPECTED_CHUNK_ROWS = EXPECTED_CHUNK_ROWS
    BASE.EXPECTED_CHUNK_SITES = EXPECTED_CHUNK_SITES
    BASE.EXPECTED_DECISION_ROWS = EXPECTED_UNION_ROWS
    BASE.EXPECTED_DECISION_ROOTS = EXPECTED_DECISION_ROOTS
    BASE.EXPECTED_PROMOTIONS = EXPECTED_PROMOTIONS
    BASE.EXPECTED_RENEWALS = EXPECTED_UNION_RENEWALS
    BASE.EXPECTED_OVERRIDES = EXPECTED_UNION_OVERRIDES
    BASE.EXPECTED_ACTION_COUNTS = EXPECTED_ACTION_COUNTS
    BASE.EXPECTED_PENDING_BEFORE = EXPECTED_PENDING_BEFORE
    BASE.EXPECTED_PENDING_AFTER = EXPECTED_PENDING_AFTER
    BASE.EXPECTED_REVIEWED_SITES = EXPECTED_REVIEWED_SITES
    BASE.EXPECTED_CANDIDATE_SITE_SHA256 = EXPECTED_CANDIDATE_SITE_SHA256
    BASE.EXPECTED_SOURCE_SITES = EXPECTED_SOURCE_SITES
    BASE.EXPECTED_SOURCE_SITE_SHA256 = EXPECTED_SOURCE_SITE_SHA256
    BASE.EXPECTED_SOURCE_ONLY_SITES = EXPECTED_SOURCE_ONLY_SITES
    BASE.EXPECTED_SOURCE_ONLY_SHA256 = EXPECTED_SOURCE_ONLY_SHA256
    BASE.EXPECTED_PREDECESSOR_OVERLAPS = EXPECTED_PREDECESSOR_OVERLAPS
    BASE.EXPECTED_PREDECESSOR_SUPERSESSIONS = EXPECTED_PREDECESSOR_SUPERSESSIONS
    BASE.METHOD = (
        "post_selector610_selector550_three_chunk_single_coordinate_union_"
        "with_identical_terminal_owner_overlap_and_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector550-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector550-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector550-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector550-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector550_consolidated_update_action"
    BASE.EXPECTED_OUTPUT_SHA256 = {
        "private_decisions": EXPECTED_OUTPUT_SHA256["private_decisions"],
        "private_evidence": None,
        "public_coverage": None,
        "public_promotion": None,
        "final_candidate": EXPECTED_FINAL_CANDIDATE_SHA256,
        "decision_coordinates": EXPECTED_OUTPUT_SHA256["decision_coordinates"],
        "promotion_coordinates": EXPECTED_OUTPUT_SHA256["promotion_coordinates"],
        "renewal_coordinates": EXPECTED_OUTPUT_SHA256["renewal_coordinates"],
        "override_coordinates": EXPECTED_OUTPUT_SHA256["override_coordinates"],
        "predecessor_overlap_coordinates":
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        "predecessor_supersession_coordinates":
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        "source_only_proof": EXPECTED_OUTPUT_SHA256["source_only_proof"],
    }


ORIGINAL_LOAD_JSON = BASE.load_json


def load_json_compat(path: Path) -> dict[str, Any]:
    value = ORIGINAL_LOAD_JSON(path)
    if path.resolve() == ASSIGNMENT_PRIVATE_PATH.resolve():
        value = json.loads(json.dumps(value))
        value["schema"] = "nobu16.kr.pk-selector610-assignment.private.v1"
        scope = value["scope"]
        scope["source_call_sites"] = sorted(
            set(scope["candidate_call_sites"])
            | set(scope["source_only_repair_sites"]),
            key=BASE.RANKING.site_key,
        )
    return value


def validate_chunk_evidence(
    assignment: Mapping[str, Any],
    chunk_rows: Sequence[Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    evidence = [ORIGINAL_LOAD_JSON(path) for path in CHUNK_EVIDENCE]
    terminal_roots = {
        BASE.coordinate_root(value)
        for value in assignment["scope"]["terminal_coordinates"]
    }
    all_sites: set[str] = set()
    owner_maps: list[dict[str, str]] = []
    for chunk_id in range(3):
        rows = chunk_rows[chunk_id]
        assigned = assignment["chunks"][chunk_id]
        sites = {str(row["site"]) for row in evidence[chunk_id]["site_reviews"]}
        coordinates = {str(row["coordinate"]) for row in rows}
        roots = {BASE.coordinate_root(value) for value in coordinates}
        allowed_roots = set(map(str, assigned["roots"])) | terminal_roots
        BASE.require(
            len(rows) == EXPECTED_CHUNK_ROWS[chunk_id]
            and len(coordinates) == len(rows),
            f"chunk{chunk_id} decision count drifted",
        )
        BASE.require(
            sites == set(map(str, assigned["sites"]))
            and len(sites) == EXPECTED_CHUNK_SITES[chunk_id],
            f"chunk{chunk_id} site coverage drifted",
        )
        BASE.require(roots <= allowed_roots, "decision escaped assignment/terminals")
        BASE.require(not all_sites & sites, "assignment sites overlap across chunks")
        all_sites.update(sites)
        owner_maps.append(
            {
                str(row["coordinate"]): BASE.reviewed_translation(row)
                for row in rows
            }
        )
    overlaps = [
        set(owner_maps[left]) & set(owner_maps[right])
        for left in range(3)
        for right in range(left + 1, 3)
    ]
    owner_overlap = set().union(*overlaps)
    BASE.require(
        len(all_sites) == EXPECTED_REVIEWED_SITES
        and BASE.site_digest(all_sites) == EXPECTED_CANDIDATE_SITE_SHA256,
        "reviewed selector-550 site union drifted",
    )
    BASE.require(
        len(owner_overlap) == EXPECTED_OWNER_OVERLAPS
        and all(
            len({owner[coordinate] for owner in owner_maps if coordinate in owner})
            == 1
            for coordinate in owner_overlap
        ),
        "identical terminal owner overlap drifted",
    )
    return evidence


def validate_site_call(
    records: Mapping[tuple[int, int], Any],
    site: str,
    *,
    expected: bool,
) -> None:
    block_id, record_id, gap_id, offset = map(int, site.split(":"))
    rows = [
        row
        for row in BASE.RANKING.LEGACY.record_edges(
            records[(block_id, record_id)]
        )
        if row["kind"] == "C"
        and tuple(row["target"]) == (0, 550)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-550 site drifted: {site}")


def source_only_runtime_delta_proof(
    assignment: Mapping[str, Any],
    current_records: Mapping[tuple[int, int], Any],
    candidate_records: Mapping[tuple[int, int], Any],
    source_records: Mapping[tuple[int, int], Any],
) -> dict[str, Any]:
    candidate_sites = set(map(str, assignment["scope"]["candidate_call_sites"]))
    source_only = set(map(str, assignment["scope"]["source_only_repair_sites"]))
    source_sites = candidate_sites | source_only
    BASE.require(
        len(candidate_sites) == EXPECTED_REVIEWED_SITES
        and BASE.site_digest(candidate_sites) == EXPECTED_CANDIDATE_SITE_SHA256,
        "candidate site register drifted",
    )
    BASE.require(
        len(source_sites) == EXPECTED_SOURCE_SITES
        and BASE.site_digest(source_sites) == EXPECTED_SOURCE_SITE_SHA256
        and len(source_only) == EXPECTED_SOURCE_ONLY_SITES
        and BASE.site_digest(source_only) == EXPECTED_SOURCE_ONLY_SHA256,
        "source/source-only register drifted",
    )
    for site in sorted(candidate_sites, key=BASE.RANKING.site_key):
        for records in (current_records, candidate_records, source_records):
            validate_site_call(records, site, expected=True)
    proof_rows = []
    for site in sorted(source_only, key=BASE.RANKING.site_key):
        validate_site_call(source_records, site, expected=True)
        validate_site_call(current_records, site, expected=False)
        validate_site_call(candidate_records, site, expected=False)
        root = tuple(map(int, site.split(":")[:2]))
        for records in (current_records, candidate_records):
            calls = [
                row
                for row in BASE.RANKING.LEGACY.record_edges(records[root])
                if row["kind"] == "C" and tuple(row["target"]) == (0, 550)
            ]
            BASE.require(not calls, "source-only runtime root still calls selector550")
        proof_rows.append(
            {
                "site": site,
                "source_call_present": True,
                "current_call_absent": True,
                "candidate_call_absent": True,
                "action": "none",
            }
        )
    return {
        "actions": 0,
        "classification": "pristine_only_control_delta_absent_from_runtime",
        "proof_rows": proof_rows,
        "proof_sha256": BASE.canonical_sha256(proof_rows),
        "site_count": len(source_only),
        "site_sha256": BASE.site_digest(source_only),
    }


def resolve_union(
    chunk_rows: Sequence[Sequence[Mapping[str, Any]]],
    official: Mapping[tuple[str, str], Mapping[str, Any]],
    predecessor_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    owner_maps = [
        {str(row["coordinate"]): BASE.reviewed_translation(row) for row in rows}
        for rows in chunk_rows
    ]
    owner_actions = [
        {str(row["coordinate"]): str(row["action"]) for row in rows}
        for rows in chunk_rows
    ]
    owner_overlap = set().union(
        *(
            set(owner_maps[left]) & set(owner_maps[right])
            for left in range(3)
            for right in range(left + 1, 3)
        )
    )
    BASE.require(
        len(owner_overlap) == EXPECTED_OWNER_OVERLAPS
        and all(
            len({owner[c] for owner in owner_maps if c in owner}) == 1
            and len({owner[c] for owner in owner_actions if c in owner}) == 1
            for c in owner_overlap
        ),
        "owner overlap is not an identical terminal renewal",
    )
    reference: dict[str, str] | None = None
    for order in itertools.permutations(range(3)):
        resolved: dict[str, str] = {}
        for owner in order:
            resolved.update(owner_maps[owner])
        if reference is None:
            reference = resolved
        BASE.require(resolved == reference, "owner permutation changed the union")
    BASE.require(reference is not None, "empty owner union")
    union = reference
    BASE.require(
        sum(len(rows) for rows in chunk_rows) == EXPECTED_OWNER_ROWS
        and len(union) == EXPECTED_UNION_ROWS
        and len({BASE.coordinate_root(value) for value in union})
        == EXPECTED_DECISION_ROOTS,
        "owner/coordinate union count drifted",
    )
    source_rows = {
        str(row["coordinate"]): row for rows in chunk_rows for row in rows
    }
    promotions: set[str] = set()
    renewals: set[str] = set()
    overrides: set[str] = set()
    actions: dict[str, str] = {}
    for coordinate, body in union.items():
        row = source_rows[coordinate]
        predecessor = official[("pk_msggame", coordinate)]
        pending = predecessor.get("runtime_review") == "pending"
        changed = body != predecessor.get("translation")
        (promotions if pending else renewals).add(coordinate)
        if changed:
            overrides.add(coordinate)
        action = (
            "translation_override_and_runtime_promotion"
            if pending and changed
            else "runtime_promotion"
            if pending
            else "translation_override_and_verification_renewal"
            if changed
            else "verification_renewal"
        )
        BASE.require(action == row["action"], "owner action drifted")
        actions[coordinate] = action
    action_counts = dict(sorted(Counter(actions.values()).items()))
    predecessor = {
        str(row["coordinate"]): str(row["translation"])
        for row in predecessor_rows
    }
    overlap = set(union) & set(predecessor)
    supersession = {c for c in overlap if union[c] != predecessor[c]}
    BASE.require(
        len(promotions) == EXPECTED_PROMOTIONS
        and len(renewals) == EXPECTED_UNION_RENEWALS
        and len(overrides) == EXPECTED_UNION_OVERRIDES
        and action_counts == EXPECTED_ACTION_COUNTS
        and len(overlap) == EXPECTED_PREDECESSOR_OVERLAPS
        and len(supersession) == EXPECTED_PREDECESSOR_SUPERSESSIONS,
        "selector550 union disposition drifted",
    )
    return {
        "action_by_coordinate": actions,
        "action_counts": action_counts,
        "final_translation": union,
        "overrides": overrides,
        "owner_maps": owner_maps,
        "predecessor_overlap": overlap,
        "predecessor_supersession": supersession,
        "promotions": promotions,
        "renewals": renewals,
        "source_rows": source_rows,
        "union": set(union),
        "owner_overlap": owner_overlap,
    }


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    evidence = json.loads(outputs[PRIVATE_EVIDENCE_OUTPUT].decode("ascii"))
    evidence["counts"].update(
        {
            "changed_roots": EXPECTED_CHANGED_ROOTS,
            "owner_decision_rows": EXPECTED_OWNER_ROWS,
            "coordinate_union_rows": EXPECTED_UNION_ROWS,
            "owner_overlaps": EXPECTED_OWNER_OVERLAPS,
            "owner_action_counts": EXPECTED_OWNER_ACTION_COUNTS,
            "owner_renewals": EXPECTED_OWNER_RENEWALS,
            "owner_overrides": EXPECTED_OWNER_OVERRIDES,
        }
    )
    evidence["digests"]["owner_overlap_coordinate_sha256"] = (
        EXPECTED_OWNER_OVERLAP_SHA256
    )
    evidence["proof"].pop("chunk_coordinate_and_root_sets_disjoint")
    evidence["proof"][
        "chunk_assignments_disjoint_except_identical_terminal_owner_overlap"
    ] = True
    evidence["proof"]["identical_terminal_owner_overlap_deduplicated"] = True
    outputs[PRIVATE_EVIDENCE_OUTPUT] = BASE.serialized_json(evidence)

    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("ascii"))
    coverage["proof"].pop("all_230_candidate_sites_reviewed")
    coverage["proof"].pop("source_only_13_absent_from_current_and_candidate")
    coverage["proof"]["all_169_candidate_sites_reviewed"] = True
    coverage["proof"]["source_only_8_absent_from_current_and_candidate"] = True
    coverage["proof"].pop("chunk_coordinate_and_root_sets_disjoint")
    coverage["proof"][
        "chunk_assignments_disjoint_except_identical_terminal_owner_overlap"
    ] = True
    coverage["proof"]["identical_terminal_owner_overlap_deduplicated"] = True
    coverage["result"].update(
        {
            "owner_decision_rows": EXPECTED_OWNER_ROWS,
            "coordinate_union_rows": EXPECTED_UNION_ROWS,
            "owner_overlaps": EXPECTED_OWNER_OVERLAPS,
        }
    )
    coverage["guards"]["private_evidence_sha256"] = BASE.sha256_bytes(
        outputs[PRIVATE_EVIDENCE_OUTPUT]
    )
    coverage["guards"]["owner_overlap_coordinate_sha256"] = (
        EXPECTED_OWNER_OVERLAP_SHA256
    )
    coverage["guards"].pop("payload_without_guard_sha256")
    coverage["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        coverage
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)

    promotion = json.loads(outputs[PUBLIC_PROMOTION_OUTPUT].decode("ascii"))
    promotion["result"].update(
        {
            "decision_rows": EXPECTED_OWNER_ROWS,
            "coordinate_union_rows": EXPECTED_UNION_ROWS,
            "owner_action_counts": EXPECTED_OWNER_ACTION_COUNTS,
            "owner_renewals": EXPECTED_OWNER_RENEWALS,
            "owner_overrides": EXPECTED_OWNER_OVERRIDES,
            "effective_action_counts": EXPECTED_ACTION_COUNTS,
            "effective_renewals": EXPECTED_UNION_RENEWALS,
            "effective_overrides": EXPECTED_UNION_OVERRIDES,
        }
    )
    promotion["guards"]["private_evidence_sha256"] = BASE.sha256_bytes(
        outputs[PRIVATE_EVIDENCE_OUTPUT]
    )
    promotion["guards"]["owner_overlap_coordinate_sha256"] = (
        EXPECTED_OWNER_OVERLAP_SHA256
    )
    promotion["guards"].pop("payload_without_guard_sha256")
    promotion["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        promotion
    )
    BASE.assert_source_free(promotion)
    outputs[PUBLIC_PROMOTION_OUTPUT] = BASE.serialized_json(promotion)
    return outputs


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(GENERIC_BUILDER_PATH) == EXPECTED_GENERIC_BUILDER_SHA256,
        "generic closure builder drifted",
    )
    configure_base()
    BASE.load_json = load_json_compat
    BASE.validate_chunk_evidence = validate_chunk_evidence
    BASE.validate_site_call = validate_site_call
    BASE.source_only_runtime_delta_proof = source_only_runtime_delta_proof
    BASE.resolve_union = resolve_union
    outputs = transform_outputs(BASE.build_outputs())
    checks = {
        "private_decisions": BASE.sha256_bytes(outputs[PRIVATE_DECISIONS_OUTPUT]),
        "private_evidence": BASE.sha256_bytes(outputs[PRIVATE_EVIDENCE_OUTPUT]),
        "public_coverage": BASE.sha256_bytes(outputs[PUBLIC_COVERAGE_OUTPUT]),
        "public_promotion": BASE.sha256_bytes(outputs[PUBLIC_PROMOTION_OUTPUT]),
    }
    for label, actual in checks.items():
        expected = EXPECTED_OUTPUT_SHA256[label]
        if expected is not None:
            BASE.require(actual == expected, f"frozen output drifted: {label}")
    return outputs


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    outputs = build_outputs()
    if args.check:
        for path, content in outputs.items():
            BASE.require(
                path.is_file() and path.read_bytes() == content,
                f"selector550 closure output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(
        json.dumps(
            {
                "coordinate_union_rows": EXPECTED_UNION_ROWS,
                "owner_decision_rows": EXPECTED_OWNER_ROWS,
                "pending_after": EXPECTED_PENDING_AFTER,
                "promotions": EXPECTED_PROMOTIONS,
                "source_only_actions": 0,
                "status": "PASS",
                "steam_write_performed": False,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
