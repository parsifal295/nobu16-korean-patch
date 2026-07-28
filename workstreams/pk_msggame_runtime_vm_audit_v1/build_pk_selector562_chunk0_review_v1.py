#!/usr/bin/env python3
"""Validate selector-562 chunk 0 and emit its source-free checkpoint."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(
    WORKSTREAM / "build_pk_selector466_chunk0_review_v1.py",
    "selector562_chunk0_review_predecessor",
)
BASE = PREDECESSOR.BASE
CORE_BUILD_REPORT = PREDECESSOR.CORE_BUILD_REPORT
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector562_assignment_v1.py",
    "selector562_chunk0_review_assignment",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector562_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector562_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector562_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector466_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector562_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector562_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector562_chunk0_review.source_free.v1.json"
)
PRIVATE_PLAN_PATH = (
    DIALOGUE_TMP / "pk_selector562_chunk0_review_plan.private.v1.json"
)
PRIVATE_GENERATOR_PATH = (
    DIALOGUE_TMP / "build_pk_selector562_chunk0_private_review_v1.py"
)
BASE.SELECTOR = 562
BASE.TERMINALS = tuple(range(1944, 1951))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector562-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector562-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector562-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector466_consolidated_selector562_chunk0_exact_one_rewrite_"
    "attempt_atomic_neighbor_multilingual_historical_register_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "FEBE7891BE6CA37EF8C2708F7E73F3F8647E2A1BCD55B85CD00F87FEF08F7395"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "9F0DF230231732B1345B80FC6F159F9D18DAD56F87D707971193658C895B1067"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "42AC1603E4F599BC36BF9B58BB766390388660050650101EC22DF41C043EED3A"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "99450F568D8EDED40C7A7332F52DADA184EE6F11FB129CFDBCC758C7880DC197"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "773B63D3427CDF9D0DA9246FB1618CBAABED46BC90CF53B8EBDC863E9631C911"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "29E569E3BD5ADA74A6EBCE6448FDCC5E0F1C28FCDF4FDCCAEEBCAFED0D650BFF"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "E2283160520383E455C9C26112E80E5DB5EDB89161A9842FF3BD8F4C7FFCAD45"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "BF4CDE7F3C55FFF631A7F06228E9958FB46A757752AEDE7585B5DE6CC87243EC"
)
BASE.EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "673BBA243E381ED0579FB0CEE2688181087D7FBBA49095F4FDA6F46DFB05BDFC"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 2,
    "accepted_sites": 2,
    "assembly_branches": 196,
    "atomic_neighbor_assembly_branches": 84,
    "atomic_non_seven_way_gap_count": 4,
    "blocked_pending_roots": 7,
    "blocked_pending_rows": 8,
    "blocked_sites": 26,
    "decision_rows": 5,
    "non_display_candidate_sites": 0,
    "prior_assembly_pending_roots": 9,
    "prior_assembly_pending_rows": 13,
    "promoted_pending_rows": 5,
    "rewrite_attempt_roots": 9,
    "roots": 28,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 28,
    "source_only_action_count": 0,
    "terminal_decision_rows": 0,
    "translation_overrides": 4,
    "verification_renewals": 0,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 1,
    "translation_override_and_runtime_promotion": 4,
}
BASE.EXPECTED_DIGESTS = {
    "assembly":
        "1DFCBC918303496F54A91EC31335C08BDB06E33713998472F6E88699E5F7798F",
    "decision":
        "96B21184E4AEC3BC3355D596FA389169CE204627C82FE7416EAAB545B265FB8E",
    "override":
        "08820062DDBC2DDCA4DDA532217C466DD131623ECBB6C8F5A7A2A24F9467A996",
    "promoted":
        "96B21184E4AEC3BC3355D596FA389169CE204627C82FE7416EAAB545B265FB8E",
}
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

EXPECTED_PLAN_SHA256 = (
    "E03F411DF0FD032074DAB5680601B4BC8ACE2A4B1A10E2A197201B5956D29690"
)
EXPECTED_GENERATOR_SHA256 = (
    "C5F4071013BEE28F42B233FB16D6BDC861F614598F510EBFEBC047CF16BDB9E2"
)
EXPECTED_CANDIDATE_TERMINAL_SHA256 = (
    "31F899387108821947571F9085D8A7FD9919BD52B8BA349DC831E138740343D6"
)
EXPECTED_SOURCE_TERMINAL_SHA256 = (
    "DD32A4A1CB88CDA98B9B37CDC21CB43A7D2C5B00B7EE374A10A0F774FD26C073"
)
EXPECTED_EMPTY_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_ATOMIC_NEIGHBOR_SHA256 = (
    "9D923EFEB4C9DE3A9FA5701E888B51351F71D76BBF018D6D5ADCC91AEF5ABFE7"
)


def terminal_values(records):
    return [
        BASE.first_literal(records, (0, record_id))
        for record_id in BASE.TERMINALS
    ]


def terminal_digest(records) -> str:
    return BASE.sha256_bytes(
        "\0".join(terminal_values(records)).encode("utf-8")
    )


def validate_selector562_guards() -> None:
    BASE.require(
        BASE.sha256_file(PRIVATE_PLAN_PATH) == EXPECTED_PLAN_SHA256
        and BASE.sha256_file(PRIVATE_GENERATOR_PATH)
            == EXPECTED_GENERATOR_SHA256,
        "private review inputs drifted",
    )
    candidate, current, source, contexts, _pending = ASSIGN.load_records()
    decisions = BASE.load_decisions()
    assignment = json.loads(
        BASE.ASSIGNMENT_PATH.read_text(encoding="utf-8")
    )
    chunk = assignment["chunks"][BASE.CHUNK_ID]
    evidence = json.loads(
        BASE.PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    decision_coordinates = {str(row["coordinate"]) for row in decisions}
    terminal_roots = {(0, record_id) for record_id in BASE.TERMINALS}
    BASE.require(
        terminal_digest(candidate) == EXPECTED_CANDIDATE_TERMINAL_SHA256
        and terminal_digest(current) == EXPECTED_CANDIDATE_TERMINAL_SHA256
        and terminal_digest(source) == EXPECTED_SOURCE_TERMINAL_SHA256
        and all(
            terminal_digest(contexts[language])
                == EXPECTED_EMPTY_TERMINAL_SHA256
            for language in ("en", "sc", "tc")
        )
        and sorted(Counter(terminal_values(candidate)).values())
            == [1, 2, 2, 2]
        and not terminal_roots & {
            BASE.parse_coordinate(coordinate)[:2]
            for coordinate in decision_coordinates
        },
        "selector562 terminal register/read-only drifted",
    )

    completed = assignment["completed_selector_overlap"]
    BASE.require(
        (
            chunk["site_count"],
            chunk["root_count"],
            chunk["pending_root_count"],
            chunk["pending_row_upper_bound"],
            chunk["owned_overlap_root_count"],
            chunk["workload_weight"],
        ) == (28, 28, 9, 13, 3, 589)
        and (
            completed["root_count"],
            completed["relation_count"],
            completed["pending_row_count"],
        ) == (3, 3, 6)
        and sorted(map(len, assignment["identical_template_atoms"]))
            == [2, 2, 3, 4, 8]
        and len(assignment["assignment_atom_union"]["roots"]) == 22
        and len(assignment["assignment_atom_union"]["pending_coordinates"])
            == 10,
        "assignment exact metrics drifted",
    )

    owned: dict[str, list[int]] = {}
    for relation in completed["relations"]:
        owned.setdefault(str(relation["root"]), []).append(
            int(relation["selector"])
        )
    BASE.require(
        all(
            row.get("overlap_owner") == owned.get(
                ":".join(str(row["coordinate"]).split(":")[:2])
            )
            and "auto" not in str(row["action"]).lower()
            for row in decisions
        )
        and evidence["owned_overlap_review"] == {
            "automatic_promotion_count": 0,
            "freshly_accepted_pending_rows": 5,
            "freshly_accepted_root_count": 2,
            "freshly_blocked_pending_rows": 1,
            "freshly_blocked_root_count": 1,
        },
        "owned overlap fresh-review guard drifted",
    )

    pending_rows = evidence["pending_semantic_rows"]
    neighbor_rows = evidence["atomic_neighbor_assembly_manifest"]
    BASE.require(
        len(pending_rows) == 13
        and len(evidence["rewrite_attempt_roots"]) == 9
        and all(
            row["fresh_semantic_review"] == "approved"
            and row["historical_factuality_review"] == "approved"
            and row["speaker_tone_review"] == "approved"
            and row["rewrite_attempt_count"] == 1
            and not row["prior_assembly_evidence_used_for_semantics"]
            and set(row["context_utf8_sha256"]) == {"jp", "en", "sc", "tc"}
            for row in pending_rows
        )
        and len(neighbor_rows) == 84
        and all(
            row["current_relative_raw_g1n_nonexpanding"]
            for row in neighbor_rows
            if row["review_disposition"] == "approved_atomic_root"
        )
        and evidence["digests"][
            "atomic_neighbor_assembly_canonical_sha256"
        ] == EXPECTED_ATOMIC_NEIGHBOR_SHA256
        and evidence["prior_evidence"]["overlap_is_subset"]
        and not evidence["prior_evidence"][
            "automatic_status_promotion_authorized"
        ]
        and evidence["terminal_register_review"]["ordered_registers"]
            == [
                "formal", "plain", "archaic", "archaic",
                "formal", "archaic", "plain",
            ]
        and not evidence["terminal_register_review"][
            "context_terminals_authoritative"
        ],
        "fresh atomic multilingual review drifted",
    )
    BASE.require(
        evidence["nominal_stem_review"] == {
            "accepted_selector562_branch_count": 14,
            "all_seven_registers_grammatical": True,
            "approved_vowel_final_stem_root_count": 2,
            "blocked_consonant_stem_root_count": 6,
            "width_blocked_vowel_stem_root_count": 1,
        }
        and evidence["width_block"][
            "current_relative_raw_g1n_expansion_px"
        ] == 72,
        "nominal-stem grammar/width disposition drifted",
    )

    template_roots = {
        root for atom in assignment["identical_template_atoms"] for root in atom
    }
    site_dispositions = {
        str(row["root"]): str(row["decision"])
        for row in evidence["site_reviews"]
    }
    BASE.require(
        len(template_roots) == 19
        and all(
            not (set(atom) & set(chunk["roots"]))
            or set(atom) <= set(chunk["roots"])
            for atom in assignment["identical_template_atoms"]
        )
        and len({
            site_dispositions[root]
            for root in template_roots & set(chunk["roots"])
        }) == 1
        and evidence["template_atomic_review"] == {
            "atom_sizes": [2, 2, 3, 4, 8],
            "partial_rewrite_count": 0,
            "pending_root_count": 4,
            "pending_row_count": 4,
            "root_count": 19,
            "single_disposition": "blocked_after_single_pass",
        },
        "repeated-template atomic disposition drifted",
    )
    BASE.require(
        evidence["exclusions"] == {
            "candidate_non_display_action_count": 0,
            "source_only_action_count": 0,
            "source_only_site_count": 6,
        }
        and evidence["counts"]["same_gap_branches"] == 0
        and evidence["counts"]["terminal_decision_rows"] == 0,
        "selector562 exclusion drifted",
    )
    ledger = {
        str(row["coordinate"]): row
        for row in (
            json.loads(line)
            for line in BASE.OFFICIAL_LEDGER_PATH.read_text(
                encoding="utf-8"
            ).splitlines()
            if line
        )
        if row.get("resource") == "pk_msggame"
    }
    BASE.require(
        all(
            ledger[coordinate].get("runtime_assembly_evidence")
            and ledger[coordinate].get("runtime_review") == "verified"
            for coordinate in assignment["scope"]["terminal_coordinates"]
        ),
        "terminal verified/read-only state drifted",
    )


def build_report():
    validate_selector562_guards()
    report = CORE_BUILD_REPORT()
    report["proof"].update({
        "all_atomic_neighbor_alternatives_reviewed": True,
        "completed_selector_overlap_freshly_reviewed": True,
        "historical_register_exact_reviewed": True,
        "nominal_stem_all_seven_registers_reviewed": True,
        "non_display_candidate_action_count_zero": True,
        "one_rewrite_attempt_per_pending_root": True,
        "pending_assembly_evidence_did_not_auto_promote": True,
        "pending_multilingual_semantics_fresh": True,
        "repeated_template_atom_partial_rewrite_count_zero": True,
        "repeated_template_atom_single_disposition": True,
        "same_gap_candidate_site_count_zero": True,
        "source_only_action_count_zero": True,
        "terminal_context_languages_non_authoritative": True,
        "terminal_register_order_preserved": True,
        "terminal_rows_verified_read_only": True,
    })
    return report


BASE.build_report = build_report
coordinate_digest = BASE.coordinate_digest
load_decisions = BASE.load_decisions
serialized = BASE.serialized
sha256_file = BASE.sha256_file
ReviewError = BASE.ReviewError
DEFAULT_PUBLIC_OUTPUT = BASE.DEFAULT_PUBLIC_OUTPUT
EXPECTED_ACTION_COUNTS = BASE.EXPECTED_ACTION_COUNTS
EXPECTED_DIGESTS = BASE.EXPECTED_DIGESTS
EXPECTED_PUBLIC_FILE_SHA256 = BASE.EXPECTED_PUBLIC_FILE_SHA256


def main(argv: Sequence[str] | None = None) -> int:
    args = BASE.parse_args(argv)
    BASE.require(
        args.output.resolve() == DEFAULT_PUBLIC_OUTPUT.resolve(),
        "public output path is fixed",
    )
    report = build_report()
    content = serialized(report)
    output_sha256 = BASE.sha256_bytes(content)
    if EXPECTED_PUBLIC_FILE_SHA256 is not None:
        BASE.require(
            output_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
            f"public output hash drifted: {output_sha256}",
        )
    if args.check:
        BASE.require(
            args.output.is_file() and args.output.read_bytes() == content,
            "public artifact drifted",
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)
    print(json.dumps({
        "accepted_pending": BASE.EXPECTED_COUNTS["promoted_pending_rows"],
        "blocked_pending": BASE.EXPECTED_COUNTS["blocked_pending_rows"],
        "output_sha256": output_sha256,
        "reviewed_candidate_sha256":
            BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256,
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
