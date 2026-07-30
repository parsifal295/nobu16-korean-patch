#!/usr/bin/env python3
"""Validate selector-610 chunk 2 and emit its source-free report."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
ASSIGNMENT_BUILDER = WORKSTREAM / "build_pk_selector610_assignment_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector610_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector610_assignment_coverage.v1.json"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector568_1096_1174_consolidated_checkpoint.private.v1.jsonl"
)
SELECTOR538_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector538_family_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector610_chunk2_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector610_chunk2_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector610_chunk2_review.source_free.v1.json"
)

CHUNK_ID = 2
SELECTOR = 610
METHOD = (
    "fc157a_selector610_chunk2_uniform_template_cross_family_"
    "review_with_selector538_companion_renewal"
)
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector610-chunk2-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector610-chunk2-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector610-chunk2-review.source-free.v1"

EXPECTED_SHA256 = {
    "assignment_builder":
        "C0BC64F37C288E23F0C8E7437775BA4534A44F05C500A8B4E70E5965BCF9D5EA",
    "assignment":
        "50A4234CC7207FFF4BCC3049532EC78502E1E8F14565CF1FBFC5399A88D4D036",
    "assignment_public":
        "FD98F9289C6F1D429BF03B53252E9C1846262A29419E97ECDCE26695D91E9C2F",
    "ledger":
        "FC157A9907686D0EA6DC6C61C7785E81AC7F750100F2E1CDDE02DBF4F09F2DCA",
    "selector538_decisions":
        "5640EB7FB7E4EA9B32309B7FA280637DA9F26F96CA500BCD4FA9847D997456C0",
    "private_decisions":
        "56C31683AF3CB6FBABA3127453A9B17C9F7487A7E28667F4B454199E78E93720",
    "private_evidence":
        "13CE2F94A82D40ADE6B25F15D612028854D0727DD784F76614FCCEFF74D41FA9",
    "current":
        "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
    "candidate":
        "07E65E6338D32C1FD13F17408F82A4133E55541C722874632948C7B36C909805",
    "reviewed":
        "8220DC12397D21FD7979052D002A4768797A14129DB1F0CDD015F6EE7234A3FC",
    "public":
        "FBFEB8A18D1CD65EE20E06CF68A7EEB321F984D43BE21C1D2373E4BF688755EC",
}
EXPECTED_DIGESTS = {
    "accepted_pending_coordinate_sha256":
        "5136F02BC97A22E39E90C5AE6C192EF6DD82B2D936EB200FA950C00ECCC0F09A",
    "accepted_site_sha256":
        "3868A05B62D839AE6EA22DE11DA1C3DBB997A53FB10A85044910D81BBCD09236",
    "blocked_site_sha256":
        "4A1DE6B869684C82A7EE4270D5A02681202B016EFA0840F6089892DC273E2B2B",
    "decision_coordinate_sha256":
        "7AC2E57CB6C8B4A4895169F31377370DA336E95C3BD45C24135E8AA9690ACB51",
    "override_coordinate_sha256":
        "EF11DC6ED5F2D42D22479D06AA332DE70F34F0C19E0D4DD0151D2707DE60AC5A",
    "selector538_companion_coordinate_sha256":
        "331AFCF4E3E3E875B2B42A03A8DBBA1F053187810649A2C3CA12DB7D9E12ACE8",
    "selector610_site_manifest_sha256":
        "F35015C38FED197AEDF6CCC18009076AE596F671EEF10DBF1807E89698942BA1",
    "template_correlated_manifest_sha256":
        "F9AA45CDD81191A97FB59F721F1D7E6B39883D7646BD6AB239EEB4594FFFD0DB",
    "template_cross_product_manifest_sha256":
        "C037D7D253DD8404127F50D91FC30B2B376DBEDC7E4CD58C5E0A1DBDE94981E1",
    "template_root_sha256":
        "78EBE0E08F36AE9A41BA47F3AABB5A5A4471F11295B2F8712DAF399D3348E6E0",
}
EXPECTED_COUNTS = {
    "accepted_pending_rows": 48,
    "accepted_sites": 49,
    "blocked_pending_rows": 0,
    "blocked_sites": 27,
    "decision_rows": 140,
    "selector538_companion_renewals": 72,
    "selector610_site_branches": 532,
    "template_correlated_branches": 7,
    "template_cross_product_branches": 343,
    "template_roots": 24,
    "translation_overrides": 92,
}
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 48,
    "translation_override_and_verification_renewal": 92,
}


class ReviewError(ValueError):
    """Raised when a frozen review invariant drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGN = load_module(ASSIGNMENT_BUILDER, "selector610_chunk2_assignment")
ENGINE = ASSIGN.ENGINE
RANKING = ASSIGN.RANKING


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
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 3, "invalid private coordinate")
    return parts  # type: ignore[return-value]


def coordinate_digest(values: Iterable[str]) -> str:
    return ASSIGN.coordinate_digest(values)


def literal_text(
    records: Mapping[tuple[int, int], Any], coordinate: str
) -> str:
    block_id, record_id, literal_id = parse_coordinate(coordinate)
    literals = ENGINE.parse_record_literals(records[(block_id, record_id)])
    require(literal_id < len(literals), "private literal absent")
    return literals[literal_id].text


def record_gap_sha256(record: Any) -> str:
    framed = b"".join(
        len(gap).to_bytes(4, "little") + gap
        for gap in ENGINE.record_gap_bytes(record)
    )
    return sha256_bytes(framed)


def load_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), "BOM rejected")
    value = json.loads(raw.decode("utf-8", errors="strict"))
    require(isinstance(value, dict), "object required")
    return value


def load_decisions() -> list[dict[str, Any]]:
    result = []
    for line in PRIVATE_DECISIONS_PATH.read_bytes().splitlines():
        if line:
            row = json.loads(line.decode("utf-8", errors="strict"))
            require(isinstance(row, dict), "decision object required")
            result.append(row)
    return result


def assert_source_free(value: Any) -> None:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            content,
        )
        is None,
        "public report contains CJK",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", content) is None,
        "public report contains an exact coordinate",
    )
    require('"translation"' not in content, "public report contains a body")


def build_report() -> dict[str, Any]:
    for path, key in (
        (ASSIGNMENT_BUILDER, "assignment_builder"),
        (ASSIGNMENT_PATH, "assignment"),
        (ASSIGNMENT_PUBLIC_PATH, "assignment_public"),
        (OFFICIAL_LEDGER_PATH, "ledger"),
        (SELECTOR538_DECISIONS_PATH, "selector538_decisions"),
        (PRIVATE_DECISIONS_PATH, "private_decisions"),
        (PRIVATE_EVIDENCE_PATH, "private_evidence"),
    ):
        require(
            path.is_file() and sha256_file(path) == EXPECTED_SHA256[key],
            f"immutable input drifted: {key}",
        )

    assignment = load_json(ASSIGNMENT_PATH)
    chunk = assignment["chunks"][CHUNK_ID]
    require(
        chunk["site_count"] == 76
        and chunk["root_count"] == 76
        and chunk["pending_root_count"] == 24
        and chunk["pending_row_upper_bound"] == 48
        and chunk["owned_overlap_root_count"] == 24
        and chunk["template_root_count"] == 24,
        "assignment scope drifted",
    )
    evidence = load_json(PRIVATE_EVIDENCE_PATH)
    guards = evidence["guards"]
    evidence_without_guards = dict(evidence)
    evidence_without_guards.pop("guards")
    require(
        evidence["schema"] == PRIVATE_EVIDENCE_SCHEMA
        and evidence["method"] == METHOD
        and evidence["status"] == "PASS"
        and evidence["counts"] == EXPECTED_COUNTS
        and evidence["digests"].items() >= EXPECTED_DIGESTS.items()
        and guards["action_counts"] == EXPECTED_ACTION_COUNTS
        and guards["decision_file_sha256"]
        == EXPECTED_SHA256["private_decisions"]
        and guards["payload_without_guards_canonical_sha256"]
        == canonical_sha256(evidence_without_guards),
        "private evidence drifted",
    )
    exact = evidence["exact_maps"]
    accepted_pending = set(map(str, exact["accepted_pending_coordinates"]))
    accepted_sites = set(map(str, exact["accepted_sites"]))
    blocked_sites = set(map(str, exact["blocked_sites"]))
    companions = set(
        map(str, exact["selector538_companion_coordinates"])
    )
    overrides = {
        str(coordinate): str(translation)
        for coordinate, translation in exact["translation_overrides"].items()
    }
    require(
        accepted_pending == set(map(str, chunk["pending_coordinates"]))
        and len(accepted_sites) == 49
        and len(blocked_sites) == 27
        and accepted_sites | blocked_sites == set(map(str, chunk["sites"]))
        and not accepted_sites & blocked_sites
        and len(companions) == 72
        and len(overrides) == 92
        and coordinate_digest(accepted_pending)
        == EXPECTED_DIGESTS["accepted_pending_coordinate_sha256"]
        and coordinate_digest(companions)
        == EXPECTED_DIGESTS[
            "selector538_companion_coordinate_sha256"
        ]
        and coordinate_digest(overrides)
        == EXPECTED_DIGESTS["override_coordinate_sha256"],
        "private exact maps drifted",
    )

    candidate, current, source, _contexts, _pending = ASSIGN.load_records()
    current_path = (
        RANKING.DEFAULT_STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin"
    )
    require(
        sha256_file(current_path) == EXPECTED_SHA256["current"],
        "current input drifted",
    )
    replacements, _ = RANKING.load_official_ledger(OFFICIAL_LEDGER_PATH)
    candidate_blob = ENGINE.rebuild_packed_with_literals(
        current_path.read_bytes(), replacements
    )
    require(
        sha256_bytes(candidate_blob) == EXPECTED_SHA256["candidate"],
        "candidate reconstruction drifted",
    )
    reviewed_blob = ENGINE.rebuild_packed_with_literals(
        candidate_blob,
        {
            parse_coordinate(coordinate): translation
            for coordinate, translation in overrides.items()
        },
    )
    require(
        sha256_bytes(reviewed_blob) == EXPECTED_SHA256["reviewed"],
        "reviewed candidate drifted",
    )
    reviewed = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(reviewed_blob).archive
    )
    reverse_blob = ENGINE.rebuild_packed_with_literals(
        reviewed_blob,
        {
            parse_coordinate(coordinate): literal_text(candidate, coordinate)
            for coordinate in overrides
        },
    )
    require(reverse_blob == candidate_blob, "reverse overlay drifted")
    changed_roots = {
        root for root in candidate if candidate[root].data != reviewed[root].data
    }
    require(
        changed_roots
        == {parse_coordinate(coordinate)[:2] for coordinate in overrides},
        "changed-root set drifted",
    )
    for root in changed_roots:
        require(
            record_gap_sha256(candidate[root])
            == record_gap_sha256(reviewed[root]),
            "record controls drifted",
        )

    edges = RANKING.graph_edges(reviewed)
    recomputed_blocked = set()
    for site in chunk["sites"]:
        block_id, record_id, gap_id, _offset = RANKING.site_key(site)
        same_gap = [
            edge
            for edge in edges[(block_id, record_id)]
            if int(edge["gap_id"]) == gap_id
        ]
        if len(same_gap) > 1:
            recomputed_blocked.add(site)
    require(
        recomputed_blocked == blocked_sites,
        "same-gap block set drifted",
    )
    site_reviews = evidence["site_reviews"]
    require(len(site_reviews) == 76, "site review count drifted")
    for review in site_reviews:
        site = str(review["site"])
        expected_decision = (
            "blocked_same_gap_complete_ending_collision"
            if site in blocked_sites
            else "verified"
        )
        require(
            review["decision"] == expected_decision
            and len(review["branches"]) == 7
            and (
                site in blocked_sites
                or all(
                    branch["line_count_match"]
                    and branch["nonexpanding"]
                    for branch in review["branches"]
                )
            ),
            "site branch proof drifted",
        )

    decision_rows = load_decisions()
    require(len(decision_rows) == 140, "decision count drifted")
    action_counts: Counter[str] = Counter()
    decision_coordinates = set()
    for row in decision_rows:
        coordinate = str(row["coordinate"])
        require(coordinate not in decision_coordinates, "duplicate decision")
        decision_coordinates.add(coordinate)
        action_counts[str(row["action"])] += 1
        translation = str(row["translation"])
        translation.encode("utf-16le", errors="strict")
        expected_translation = overrides.get(
            coordinate, literal_text(candidate, coordinate)
        )
        require(
            row["schema"] == PRIVATE_DECISION_SCHEMA
            and row["runtime_review"] == "verified"
            and row["fresh_semantic_review"] == "approved"
            and row["historical_factuality_review"] == "approved"
            and row["speaker_tone_review"] == "approved"
            and row["layout_review"]
            == "current_relative_raw_g1n_nonexpanding"
            and translation == expected_translation
            and translation == literal_text(reviewed, coordinate)
            and translation.count("\n")
            == literal_text(candidate, coordinate).count("\n"),
            "decision row drifted",
        )
        expected_action = (
            "runtime_promotion"
            if coordinate in accepted_pending
            else "translation_override_and_verification_renewal"
        )
        require(row["action"] == expected_action, "decision action drifted")
    require(
        action_counts == Counter(EXPECTED_ACTION_COUNTS)
        and coordinate_digest(decision_coordinates)
        == EXPECTED_DIGESTS["decision_coordinate_sha256"],
        "decision union drifted",
    )

    template_roots = {
        parse_coordinate(coordinate)[:2]
        for coordinate in accepted_pending
    }
    require(
        len(template_roots) == 24
        and len({candidate[root].data for root in template_roots}) == 1
        and len({current[root].data for root in template_roots}) == 1
        and len({source[root].data for root in template_roots}) == 1
        and len({reviewed[root].data for root in template_roots}) == 1,
        "uniform template identity drifted",
    )
    for root in template_roots:
        targets = [
            int(edge["target"][1])
            for edge in edges[root]
            if int(edge["target"][0]) == 0
        ]
        require(
            len(targets) == 4
            and targets[-1] == SELECTOR
            and len(set(targets)) == 4,
            "template call composition drifted",
        )

    report: dict[str, Any] = {
        "guards": {
            "action_counts": EXPECTED_ACTION_COUNTS,
            "decision_coordinate_sha256":
            EXPECTED_DIGESTS["decision_coordinate_sha256"],
            "decision_file_sha256": EXPECTED_SHA256["private_decisions"],
            "evidence_file_sha256": EXPECTED_SHA256["private_evidence"],
            "official_candidate_sha256": EXPECTED_SHA256["candidate"],
            "reviewed_candidate_sha256": EXPECTED_SHA256["reviewed"],
        },
        "method": METHOD,
        "privacy": {
            "contains_commercial_source_text": False,
            "contains_dialogue_bodies": False,
            "contains_exact_coordinates": False,
            "private_artifacts_stay_below_tmp": True,
            "shared_integration_mutated": False,
        },
        "proof": {
            "all_template_cross_product_branches_nonexpanding": True,
            "all_template_records_byte_identical": True,
            "ghidra_contract_reused": True,
            "runtime_grammar_repair": False,
            "same_gap_complete_ending_collisions_blocked": True,
            "selector538_verified_companions_renewed": True,
            "template_uniform_rule_indivisible": True,
        },
        "result": EXPECTED_COUNTS,
        "schema": PUBLIC_SCHEMA,
        "scope": {
            "chunk_id": CHUNK_ID,
            "owned_overlap_roots": 24,
            "pending_rows": 48,
            "roots": 76,
            "selector": SELECTOR,
            "sites": 76,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    report["guards"]["payload_without_guard_sha256"] = canonical_sha256(
        report
    )
    assert_source_free(report)
    return report


def serialized(value: Any) -> bytes:
    return canonical_bytes(value) + b"\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_PUBLIC_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(
        args.output.resolve() == DEFAULT_PUBLIC_OUTPUT.resolve(),
        "public output path is fixed",
    )
    report = build_report()
    content = serialized(report)
    require(
        sha256_bytes(content) == EXPECTED_SHA256["public"],
        "public hash drifted",
    )
    if args.check:
        require(
            args.output.is_file() and args.output.read_bytes() == content,
            "public artifact drifted",
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)
    print(
        json.dumps(
            {
                "accepted_pending": 48,
                "blocked_sites": 27,
                "public_sha256": EXPECTED_SHA256["public"],
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
