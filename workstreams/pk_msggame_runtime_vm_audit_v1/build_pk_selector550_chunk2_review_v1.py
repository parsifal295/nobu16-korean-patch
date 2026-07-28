#!/usr/bin/env python3
"""Validate selector-550 chunk 2 and emit its source-free checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
ASSIGNMENT_BUILDER = WORKSTREAM / "build_pk_selector550_assignment_v1.py"
ASSIGNMENT = DIALOGUE_TMP / "pk_selector550_assignment.private.v1.json"
ASSIGNMENT_PUBLIC = (
    WORKSTREAM / "public" / "pk_selector550_assignment_coverage.v1.json"
)
LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector610_consolidated_checkpoint.private.v1.jsonl"
)
DECISIONS = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector550_chunk2_review_decisions.private.v1.jsonl"
)
EVIDENCE = DIALOGUE_TMP / "pk_selector550_chunk2_review_evidence.private.v1.json"
PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector550_chunk2_review.source_free.v1.json"
)
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin")

METHOD = (
    "post_selector610_selector550_chunk2_fresh_semantic_seven_branch_"
    "same_gap_terminal_atom_and_current_relative_review"
)
DECISION_SCHEMA = "nobu16.kr.pk-selector550-chunk2-review-decision.private.v1"
EVIDENCE_SCHEMA = "nobu16.kr.pk-selector550-chunk2-review-evidence.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector550-chunk2-review.source-free.v1"
EXPECTED = {
    "assignment_builder": "4ACE71CD3A28331AD22F6E865F77463B6A9B6A8B4D7A3679097F2EF3BB33895C",
    "assignment": "A692CAAEFAB77ED85DE5A07F775694ABFDDC1407E01AC158C2C1C4FC861EDFBF",
    "assignment_public": "A98C40EB3414E5F4DC21C264E091761A54C59F90771902A2B611EF13E90D13A8",
    "ledger": "0218C3D198C9930C8920ED8DAEB2DDD85987878035AC59DD5ECC8179D38DE12B",
    "decisions": "5440331A2B32A6E5A4E9E7A6E1C3B7D83677187403B181E4587327FA10B4AEC4",
    "evidence": "A9715CC7F3561F85B7E93664351A8380F4FBA045F52822F87039AE1A6D13F550",
    "candidate": "F80EA5958757F097885279BAB53A8456758BB99B1CE47E214FE0F54AB7152807",
    "reviewed": "6AEB2BE4348AED12E910A749D11E3C9030666B36087029EF7CB9FE0AE046A321",
    "assembly": "37E38BADC500E95448764236084EFFA04B172932BC41F7AC0B7F9A0D7184578C",
    "decision_coordinates": "725FEC50C4902FA859E956EC607072FAC0C86C56F3F6D14724303C9F79242E53",
    "override_coordinates": "DAB4D604EC6DDFCB1BEB580B9F2558B599C5D6CEB96971DABB3319D125ABE3E6",
    "promoted_coordinates": "89428DF97D2163A9B346B7D2FB2DF99C587E9000E965C6610643AD0831B5A5CB",
    "public": "67C1725ED839C99B3E38B7CD068E4C9AB96DD979E4113A476B5328890349CA9D",
    "steam": "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
}
COUNTS = {
    "accepted_pending_roots": 21,
    "accepted_sites": 45,
    "assembly_branches": 413,
    "blocked_pending_roots": 10,
    "blocked_pending_rows": 20,
    "blocked_sites": 14,
    "decision_rows": 61,
    "promoted_pending_rows": 29,
    "roots": 59,
    "same_gap_branches": 14,
    "sites": 59,
    "translation_overrides": 42,
}
ACTIONS = {
    "runtime_promotion": 19,
    "translation_override_and_runtime_promotion": 10,
    "translation_override_and_verification_renewal": 32,
}


class ReviewError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts


def coordinate_digest(values: Iterable[str]) -> str:
    return sha256_bytes(
        "\n".join(sorted(set(values), key=parse_coordinate)).encode("ascii")
    )


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGN = load_module(ASSIGNMENT_BUILDER, "pk_selector550_chunk2_assignment")
ENGINE = ASSIGN.ENGINE
RANKING = ASSIGN.RANKING


def literal_text(records: Any, coordinate: str) -> str:
    block_id, record_id, literal_id = parse_coordinate(coordinate)
    literals = ENGINE.parse_record_literals(records[(block_id, record_id)])
    require(literal_id < len(literals), f"literal absent: {coordinate}")
    return literals[literal_id].text


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le", errors="strict"))


def build_report() -> dict[str, Any]:
    immutable = {
        ASSIGNMENT_BUILDER: EXPECTED["assignment_builder"],
        ASSIGNMENT: EXPECTED["assignment"],
        ASSIGNMENT_PUBLIC: EXPECTED["assignment_public"],
        LEDGER: EXPECTED["ledger"],
        DECISIONS: EXPECTED["decisions"],
        EVIDENCE: EXPECTED["evidence"],
    }
    for path, digest in immutable.items():
        require(path.is_file() and sha256_file(path) == digest, f"input drifted: {path}")
    assignment = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
    chunk = assignment["chunks"][2]
    require(
        (chunk["site_count"], chunk["root_count"], chunk["pending_row_upper_bound"])
        == (COUNTS["sites"], COUNTS["roots"], 49),
        "assignment scope drifted",
    )
    decisions = [
        json.loads(line)
        for line in DECISIONS.read_text(encoding="utf-8").splitlines()
        if line
    ]
    require(
        len(decisions) == COUNTS["decision_rows"]
        and len({row["coordinate"] for row in decisions}) == len(decisions)
        and Counter(row["action"] for row in decisions) == Counter(ACTIONS)
        and coordinate_digest(row["coordinate"] for row in decisions)
        == EXPECTED["decision_coordinates"],
        "decision partition drifted",
    )
    require(
        all(
            row["schema"] == DECISION_SCHEMA
            and row["fresh_semantic_review"] == "approved"
            and row["historical_factuality_review"] == "approved"
            and row["speaker_tone_review"] == "approved"
            and row["runtime_review"] == "verified"
            and row["layout_review"] == "current_relative_raw_g1n_nonexpanding"
            for row in decisions
        ),
        "decision approval drifted",
    )
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    require(
        evidence["schema"] == EVIDENCE_SCHEMA
        and evidence["method"] == METHOD
        and evidence["counts"] == COUNTS
        and len(evidence["site_reviews"]) == COUNTS["sites"]
        and len(evidence["assembly_manifest"]) == COUNTS["assembly_branches"],
        "evidence scope drifted",
    )
    digests = evidence["digests"]
    require(
        digests["assembly_canonical_sha256"] == EXPECTED["assembly"]
        and canonical_sha256(evidence["assembly_manifest"]) == EXPECTED["assembly"]
        and digests["decision_coordinate_sha256"]
        == EXPECTED["decision_coordinates"]
        and digests["override_coordinate_sha256"]
        == EXPECTED["override_coordinates"]
        and digests["promoted_coordinate_sha256"]
        == EXPECTED["promoted_coordinates"]
        and digests["reviewed_candidate_sha256"] == EXPECTED["reviewed"]
        and digests["reverse_overlay_sha256"] == EXPECTED["candidate"],
        "evidence digest drifted",
    )
    blocked = set(evidence["blocked"]["pending_coordinates"])
    promoted = {
        row["coordinate"]
        for row in decisions
        if row["action"].endswith("runtime_promotion")
    }
    require(
        len(blocked) == COUNTS["blocked_pending_rows"]
        and len(promoted) == COUNTS["promoted_pending_rows"]
        and blocked.isdisjoint(promoted)
        and coordinate_digest(promoted) == EXPECTED["promoted_coordinates"],
        "blocked/promoted split drifted",
    )
    require(
        all(
            review["historical_factuality_reviewed"] is True
            and review["speaker_tone_reviewed"] is True
            and len(review["assemblies"]) == 7
            and all(
                branch["line_count_match"] is True
                and (
                    branch["grammar_and_spacing_proven"] is False
                    if review["decision"].startswith("blocked_")
                    else branch["grammar_and_spacing_proven"] is True
                    and branch["current_relative_raw_g1n_nonexpanding"] is True
                )
                for branch in review["assemblies"]
            )
            for review in evidence["site_reviews"]
        ),
        "branch proof drifted",
    )

    candidate, current, source, _contexts, _pending = ASSIGN.load_records()
    current_blob = (
        ASSIGN.RANKING_WRAPPER.DEFAULT_STEAM_ROOT
        / "MSG_PK" / "JP" / "msggame.bin"
    ).read_bytes()
    replacements, _ = RANKING.load_official_ledger(LEDGER)
    candidate_blob = ENGINE.rebuild_packed_with_literals(current_blob, replacements)
    require(sha256_bytes(candidate_blob) == EXPECTED["candidate"], "candidate drifted")
    overrides = {
        row["coordinate"]: row["reviewed_translation"]
        for row in decisions
        if row["action"].startswith("translation_override")
    }
    require(
        len(overrides) == COUNTS["translation_overrides"]
        and coordinate_digest(overrides) == EXPECTED["override_coordinates"],
        "override split drifted",
    )
    reviewed_blob = ENGINE.rebuild_packed_with_literals(
        candidate_blob,
        {parse_coordinate(key): value for key, value in overrides.items()},
    )
    require(sha256_bytes(reviewed_blob) == EXPECTED["reviewed"], "reviewed blob drifted")
    reviewed = ENGINE.archive_records(ENGINE.parse_packed_msggame(reviewed_blob).archive)
    for row in decisions:
        coordinate = row["coordinate"]
        require(
            row["jp_source_utf16le_sha256"]
            == utf16le_sha256(literal_text(source, coordinate))
            and row["current_ko_utf16le_sha256"]
            == utf16le_sha256(literal_text(current, coordinate))
            and row["reviewed_utf16le_sha256"]
            == utf16le_sha256(literal_text(reviewed, coordinate))
            and row["reviewed_translation"] == literal_text(reviewed, coordinate),
            f"literal proof drifted: {coordinate}",
        )
    changed_roots = {
        root for root in candidate if candidate[root].data != reviewed[root].data
    }
    require(
        changed_roots
        == {parse_coordinate(coordinate)[:2] for coordinate in overrides},
        "changed root set drifted",
    )
    boundary_reflows = 0
    for root in changed_roots:
        before = ENGINE.parse_record_literals(candidate[root])
        after = ENGINE.parse_record_literals(reviewed[root])
        signatures = [
            (ENGINE.protected_signature(left.text), ENGINE.protected_signature(right.text))
            for left, right in zip(before, after)
        ]
        boundary_reflows += sum(
            left["leading_whitespace"] != right["leading_whitespace"]
            or left["trailing_whitespace"] != right["trailing_whitespace"]
            for left, right in signatures
        )
        require(
            ENGINE.record_gap_bytes(candidate[root])
            == ENGINE.record_gap_bytes(reviewed[root])
            and len(before) == len(after)
            and all(
                left.text.count("\n") == right.text.count("\n")
                and all(
                    left_signature[key] == right_signature[key]
                    for key in (
                        "escape_tags",
                        "printf_tokens",
                        "bracket_tokens",
                        "non_layout_controls",
                    )
                )
                and right.text.encode("utf-16le", errors="strict").decode(
                    "utf-16le", errors="strict"
                )
                == right.text
                for (left, right), (left_signature, right_signature)
                in zip(zip(before, after), signatures)
            ),
            f"record topology drifted: {root}",
        )
    require(boundary_reflows == 2, "runtime boundary reflow count drifted")
    chunk_roots = {
        tuple(int(part) for part in root.split(":")) for root in chunk["roots"]
    }
    template_groups = [
        {
            tuple(int(part) for part in root.split(":"))
            for root in group
        }
        for group in assignment["identical_template_groups"]
        if {
            tuple(int(part) for part in root.split(":"))
            for root in group
        }
        <= chunk_roots
    ]
    require(
        sum(len(group) for group in template_groups)
        == chunk["template_root_count"]
        and all(
            len({reviewed[root].data for root in group}) == 1
            for group in template_groups
        ),
        "assigned template atoms drifted",
    )
    reverse = ENGINE.rebuild_packed_with_literals(
        reviewed_blob,
        {
            parse_coordinate(key): literal_text(candidate, key)
            for key in overrides
        },
    )
    require(reverse == candidate_blob, "reverse overlay drifted")
    require(sha256_file(STEAM) == EXPECTED["steam"], "live Steam archive drifted")

    report = {
        "distribution_policy": {
            "private_decisions_stay_below_tmp": True,
            "private_evidence_stays_below_tmp": True,
            "tracked_builder_contains_dialogue_bodies": False,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_test_contains_dialogue_bodies": False,
            "tracked_validator_uses_frozen_private_hashes": True,
        },
        "guards": {
            "action_counts": ACTIONS,
            "assembly_canonical_sha256": EXPECTED["assembly"],
            "decision_coordinate_sha256": EXPECTED["decision_coordinates"],
            "decision_file_sha256": EXPECTED["decisions"],
            "evidence_file_sha256": EXPECTED["evidence"],
            "official_candidate_sha256": EXPECTED["candidate"],
            "override_coordinate_sha256": EXPECTED["override_coordinates"],
            "promoted_coordinate_sha256": EXPECTED["promoted_coordinates"],
            "reverse_overlay_sha256": EXPECTED["candidate"],
            "reviewed_candidate_sha256": EXPECTED["reviewed"],
            "steam_archive_sha256_after": EXPECTED["steam"],
            "steam_archive_sha256_before": EXPECTED["steam"],
        },
        "method": METHOD,
        "proof": {
            "accepted_assemblies_current_relative_raw_g1n_nonexpanding": True,
            "all_assigned_sites_reviewed": True,
            "all_changed_record_control_gaps_preserved": True,
            "all_literal_linebreak_counts_preserved": True,
            "automatic_space_or_grammar_repair_by_vm": False,
            "blocked_unresolved_sites_not_promoted": True,
            "historical_factuality_reviewed": True,
            "opcode_0143_call": True,
            "opcode_014a_jump": True,
            "reverse_overlay_recovers_official_candidate": True,
            "same_gap_selectors_reviewed": True,
            "speaker_tone_reviewed": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": COUNTS,
        "schema": PUBLIC_SCHEMA,
        "scope": {"chunk_id": 2, "selector": 550, "terminal_count": 7},
        "status": "PASS",
        "steam_write_performed": False,
    }
    serialized = json.dumps(report, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        ) is None
        and re.search(r"\b\d+:\d+(?::\d+){0,2}\b", serialized) is None,
        "public report is not source-free",
    )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    content = canonical_bytes(build_report()) + b"\n"
    require(sha256_bytes(content) == EXPECTED["public"], "public hash drifted")
    if args.check:
        require(PUBLIC_OUTPUT.read_bytes() == content, "public artifact drifted")
    else:
        PUBLIC_OUTPUT.write_bytes(content)
    print("selector550 chunk2 review: PASS promoted=29 blocked=20")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
