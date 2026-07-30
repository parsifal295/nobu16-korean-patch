#!/usr/bin/env python3
"""Build the selector-178 two-chunk closure on frozen post-selector1198."""

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

BASE_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector514_consolidated_closure_core_v1.py"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector178_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector178_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector178_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1198_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector1198_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector178_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector178_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector178_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector178_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector178_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector178_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector178_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector178_consolidated_closure_promotion.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "AE64FFC67F3B8424E78026DE82D32D8A176051A4FF8B45C1FDDBB750155DE4A3"
)
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "83B8B3FAD9E37A891F2E896504DD2555FE840C4AA8CB2A099217A122E07B771A",
    "assignment_private":
        "C1DE0528BF795DEF68C914A32F9583C2CD084F55491C181329BAE39AE631FACC",
    "assignment_public":
        "230A9679566C5D8BD7821F0A4D148CC00A820A16EDFD22C7C5EF2567695C92A8",
    "official_ledger":
        "A3B6AE01A30C4EC6EFCE171345EFEB81F7FDB9EDFDCAECD90AA4A78AB3296F4F",
    "predecessor_decisions":
        "933552574FBFC2322CC17DD35ED106BF24326A006EB85F057E4136C720B6E1B4",
    "chunk0_builder":
        "0F44B163C372DA261C93DEED23ADCEF11C027F8F31AFF8CCA06E1BAD32D4371C",
    "chunk0_public":
        "6408617D0DFAEC1A652DE8655A6A3AE0CB1CF49B828DF775CC4D21093CECD365",
    "chunk0_decisions":
        "FE6FF50CC1E975480C20AA5D5D5AF86D50EF312C090118D3A311EE3D784CF48E",
    "chunk0_evidence":
        "6FC94BAAF6ADCC929F3342612095C14161F04A4AB5183B0AB0DC3775417B2BA2",
    "chunk1_builder":
        "E20382027AC741EBB99BB9842F884F19C7BD1823D4749424D1AB82C2BA477F68",
    "chunk1_public":
        "0ACA9CA2E78B24E5E1CDE78A6625CA9FF7821BF330DF0A3A17529214FEDAF650",
    "chunk1_decisions":
        "F32D97D3BB21B5E092811A6E145BC5E133B592108CE35C1C1E0559DD262D3ED6",
    "chunk1_evidence":
        "8E79424B276B3112D92EE4397069FF870525E917443D02C415A6CE86FFE2DEC2",
}

EXPECTED_CHUNK_ROWS = (22, 48)
EXPECTED_CHUNK_SITES = (77, 76)
EXPECTED_DECISION_ROWS = 70
EXPECTED_DECISION_ROOTS = 48
EXPECTED_PROMOTIONS = 32
EXPECTED_RENEWALS = 38
EXPECTED_OVERRIDES = 47
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 23,
    "translation_override_and_runtime_promotion": 9,
    "translation_override_and_verification_renewal": 38,
}
EXPECTED_PENDING_BEFORE = 6_464
EXPECTED_PENDING_AFTER = 6_432
EXPECTED_REVIEWED_SITES = 153
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "20DEFAEEC547AC566E2B1D74E0C3CB47EF2B7477AB01E06A3DA5CA890ADCC0D7"
)
EXPECTED_SOURCE_SITES = 163
EXPECTED_SOURCE_SITE_SHA256 = (
    "5A035A095F1B9A0214915477B2192F39EE207FF447545489A853F45D5DD90A9E"
)
EXPECTED_SOURCE_ONLY_SITES = 10
EXPECTED_SOURCE_ONLY_SHA256 = (
    "87DD78E9FC339A62810B94DE2FCCB39FEAE1A5C5E583454B7C6F11A5C5A08D05"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "74E30E798B82129565518FA04F35DC73220974CFC6E1E7E61BCEC2D8008671DA"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "DAD1BCD22AAE11BDD5D10669BC052240FDDAFD634AE5B6A32353BF11CE563B2C"
)

EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "2F81E5E455F613A8B6550787FFB278282002B7BC487B60B29E05DCB09CB4C093",
    "private_evidence":
        "E8C5E9E78CD585183E9D4C38A1C3A116494CCD25D2577B2D381920F7F386A407",
    "public_coverage":
        "3263178FBA9FAC322472CDC0599234AD27EF56B1EB78A4AA24DEA3B9D00462FF",
    "public_promotion":
        "4D3CE8E47126BCFC20B068DB4163319C2AECA37C95655BE52A03CEC1D7E7D147",
    "final_candidate":
        "D89D47866F7FA9D34F68814219A00840921C130E062EA5DE80F95063B9E96E7F",
    "decision_coordinates":
        "C3A8A1832CDA66D290005900E9609896ED59043F2507EAFE68E4E2566D7048E1",
    "promotion_coordinates":
        "DA73EC0BD42C63F5F7EC5956EC76813014DF2A88E0DF7EF60C29FA89B904E032",
    "renewal_coordinates":
        "97F00C5ED8CD8C5936E45911F24F777E20AD21F30B7C836A05F4593D21E8365B",
    "override_coordinates":
        "E79D24DC9E99ECFF9ED88357223370038C17A6CB5EFF5D63503C6D05471A67F1",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "482370EF7F0AAAC276EAB4147FF38DD0B2BD7C7C469C9C410601B31D4A1D9C49",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_BUILDER_PATH, "selector178_closure_base")
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector178_closure_input")


def configure_base() -> None:
    """Bind the generic two-chunk core to the immutable selector-178 inputs."""
    # The selector-178 assignment is itself a wrapper. Expose the generic
    # digest helpers expected by the closure core and bind its exact engine.
    ASSIGNMENT.coordinate_digest = ASSIGNMENT.ASSIGNMENT.coordinate_digest
    ASSIGNMENT.site_digest = ASSIGNMENT.ASSIGNMENT.site_digest
    values = {
        "ASSIGNMENT": ASSIGNMENT,
        "ENGINE": ASSIGNMENT.ENGINE,
        "RANKING": ASSIGNMENT.RANKING,
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
        "EXPECTED_OFFICIAL_CANDIDATE_SHA256":
            EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        "EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256":
            EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256,
        "EXPECTED_OUTPUT_SHA256": {
            key: (
                None
                if key in {"public_coverage", "public_promotion"}
                else value
            )
            for key, value in EXPECTED_OUTPUT_SHA256.items()
        },
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.METHOD = (
        "post_selector1198_selector178_two_chunk_single_coordinate_union_"
        "with_targeted_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector178-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector178-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector178-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector178-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector178_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = "nobu16.kr.pk-selector178-assignment.private.v1"


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
        and tuple(row["target"]) == (0, 178)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-178 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("utf-8"))
    proof = coverage["proof"]
    proof.pop("all_230_candidate_sites_reviewed", None)
    proof.pop("source_only_13_absent_from_current_and_candidate", None)
    proof["all_153_candidate_sites_reviewed"] = True
    proof["confirmed_non_display_rows_untouched"] = True
    proof["seven_terminal_records_unchanged"] = True
    proof["source_only_10_absent_from_current_and_candidate"] = True
    coverage["guards"].pop("payload_without_guard_sha256")
    coverage["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        coverage
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def validate_wrapper_invariants(outputs: Mapping[Path, bytes]) -> None:
    """Recheck selector-specific state that the generic union core cannot name."""
    official = [
        json.loads(line)
        for line in OFFICIAL_LEDGER_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]
    decisions = [
        json.loads(line)
        for line in outputs[PRIVATE_DECISIONS_OUTPUT]
        .decode("utf-8", errors="strict")
        .splitlines()
        if line
    ]
    confirmed = {
        (str(row["resource"]), str(row["coordinate"]))
        for row in official
        if row.get("scope_classification") == "confirmed_non_display"
    }
    decision_keys = {
        (str(row["resource"]), str(row["coordinate"])) for row in decisions
    }
    terminal_roots = {(0, record_id) for record_id in range(1482, 1489)}
    decision_roots = {
        tuple(map(int, coordinate.split(":")[:2]))
        for _resource, coordinate in decision_keys
    }
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed,
        "selector178 touched the confirmed-non-display universe",
    )
    BASE.require(
        not decision_roots & terminal_roots,
        "selector178 decision union changed one of its seven terminals",
    )


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector closure base drifted",
    )
    BASE.require(
        all(value is not None for value in EXPECTED_INPUT_SHA256.values()),
        "selector178 chunk inputs are not frozen yet",
    )
    BASE.require(
        EXPECTED_DECISION_ROWS >= 0
        and EXPECTED_DECISION_ROOTS >= 0
        and EXPECTED_PROMOTIONS >= 0
        and EXPECTED_RENEWALS >= 0
        and EXPECTED_OVERRIDES >= 0
        and EXPECTED_PENDING_AFTER >= 0
        and EXPECTED_PREDECESSOR_OVERLAPS >= 0
        and EXPECTED_PREDECESSOR_SUPERSESSIONS >= 0,
        "selector178 exact union constants are not frozen yet",
    )
    configure_base()
    BASE.validate_site_call = validate_site_call
    outputs = BASE.build_outputs()
    validate_wrapper_invariants(outputs)
    outputs = transform_outputs(outputs)
    labels = {
        PRIVATE_DECISIONS_OUTPUT: "private_decisions",
        PRIVATE_EVIDENCE_OUTPUT: "private_evidence",
        PUBLIC_COVERAGE_OUTPUT: "public_coverage",
        PUBLIC_PROMOTION_OUTPUT: "public_promotion",
    }
    for path, label in labels.items():
        expected = EXPECTED_OUTPUT_SHA256[label]
        BASE.require(
            expected is None or BASE.sha256_bytes(outputs[path]) == expected,
            f"frozen {label} drifted",
        )
    return outputs


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
                f"selector178 closure output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(
        json.dumps(
            {
                "decision_rows": EXPECTED_DECISION_ROWS,
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
