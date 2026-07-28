#!/usr/bin/env python3
"""Consolidate the two selector-226 reviews on the post-selector1168 state."""

from __future__ import annotations

import argparse
import importlib.util
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

SCAFFOLD_BASE_PATH = (
    WORKSTREAM / "build_pk_selector364_consolidated_closure_v1.py"
)
EXPECTED_SCAFFOLD_BASE_SHA256 = (
    "024A7A1946808584EB9C52F28A80F6804CDF727D2A50636C6541485A4AD64596"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector226_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector226_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector226_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1168_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector1168_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector226_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector226_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector226_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector226_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector226_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector226_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector226_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector226_consolidated_closure_promotion.v1.json"
)

# Filled and frozen after the first deterministic in-memory build.
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "B8957E12245FDAA02CDAB3690E4DE4FE4601D2B92F8185D5734DBAB909C87D7F",
    "assignment_private":
        "223EBD7D1C0C0D6E78DCD97D0189C1E5099DBB917DD2498CC659BEDEBFAEE050",
    "assignment_public":
        "BFD1F9D8A813C2ADA7D8C065B4F7C1963F8704A7538C306C9EF6DE203F414215",
    "official_ledger":
        "56FBAF8FB54CCFA7EAF10355F66FE6A730374804F48FB4CD9F8F15A99AEE9A91",
    "predecessor_decisions":
        "37402EE773B331D48C957C8C2AA3EED55FA582726BC98EA5F9BECBF87AD153AE",
    "chunk0_builder":
        "0E59178582C92DF6BE635EB402DF1C06402D4A7FC2F3E62BDA257F0754467345",
    "chunk0_public":
        "A5F078515256725FB25637F59FD1E0672CFE81333A69D2D165EB70052C02E8AD",
    "chunk0_decisions":
        "FC7FA52ED723BAE5D55DCDBCCE3B68BD4E1A71BEE3AB745830541E65E5F452DD",
    "chunk0_evidence":
        "1B4F0568039DBF5659E7536B22268E7534A79C86D5357014E813C5D55B1E7EE8",
    "chunk1_builder":
        "D63509BC23A79C09A1D966A9B7FC02E81A5E6C08461A8D6A80BEB2D85C63FDBE",
    "chunk1_public":
        "66B9A2D4B2BD4ACAEE18AB82855F6A9F4C352568985749889AFC85AEAC75CC62",
    "chunk1_decisions":
        "0EB986AA79D4E1C8195440877754B434C338A4E3FED3A7BB365B5905F93FE533",
    "chunk1_evidence":
        "49D8E1A3F47EDA254C3F923C304BDF67932BA9500B9CC058FF0084E3AF5E2979",
}
EXPECTED_CHUNK_ROWS = (20, 17)
EXPECTED_CHUNK_SITES = (35, 35)
EXPECTED_DECISION_ROWS = 37
EXPECTED_DECISION_ROOTS = 28
EXPECTED_PROMOTIONS = 37
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 3
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 34,
    "translation_override_and_runtime_promotion": 3,
}
EXPECTED_PENDING_BEFORE = 6_283
EXPECTED_PENDING_AFTER = 6_246
EXPECTED_REVIEWED_SITES = 70
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "CE5792EDBBE944E7FBF687177F65DEE5D3158123C4E291D5BA6A80EB33C9F391"
)
EXPECTED_SOURCE_SITES = 75
EXPECTED_SOURCE_SITE_SHA256 = (
    "9105E9793B777CD40A160071623F55656FB8CFE4F5B38F8532E7F1AF7E08BDB9"
)
EXPECTED_SOURCE_ONLY_SITES = 5
EXPECTED_SOURCE_ONLY_SHA256 = (
    "AD94EB5D6589B6F0004C623B08D526C37E30AA4A62B83D1FD1772F92FC185AD6"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "EF84A8B8A18C1F2F1F72D3A650C01DC7B058F32A3536C130809C4FCB31C837C7"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "9A04C999B850A1024BBB9AE57F509CA1C879A5DC4D59BF717873FD17E609545F"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "E84F2CF9B57C34F9C40F357BFC0469E2A7FAB5C49E33DC1734447F6C9F069E62"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "0FBD6CD0D4C3C5CB6C3CF17B62D061ADDAF0A6117FC4B6A6C70353B50A6A0419"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "DB8801176872E89F4109D2AECA4A0B60A51E76CB0A3EAF5FE6EA6E04966E3511"
)
EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "C01523FE952E960CEF95DB8F9469BA388211C2B8F228CA269C9C32127599D5EB",
    "private_evidence":
        "822B75980067F6D9BCA1D575021350727B5067C3D647B30581F2D3FF3AD47322",
    "public_coverage":
        "3213267FFB7624FEA010B69A3542C542BFC906FA1DB8646CE3197015069CA246",
    "public_promotion":
        "EDCAA78F69EE1BB844F2543BB4F9BCFE5A204816DD596B56691130FC269349E4",
    "final_candidate":
        "FEE99844339C291F6950BEB2193AB5FDD8D25B6F6117AD52F81DCBF7F0CC9B66",
    "decision_coordinates":
        "428270DFDCFCB67D700B397D5DB3E903B1FE0545A0DBE7F452A878A7D95A1BE4",
    "promotion_coordinates":
        "428270DFDCFCB67D700B397D5DB3E903B1FE0545A0DBE7F452A878A7D95A1BE4",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "ECF77DD71638F1E0EF1892C63A1530590D4ABC48CF5C67106C53ED49EC8C75BC",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "8D498318785CFA4C423C9519DBF2B038DC29DBEFD9724CF2DE3E01E48A6D5496",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCAFFOLD_BASE = load_module(
    SCAFFOLD_BASE_PATH, "selector226_closure_scaffold_base"
)
WRAPPER = SCAFFOLD_BASE.WRAPPER
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector226_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = SCAFFOLD_BASE.ORIGINAL_CONFIGURE_BASE


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector1168_selector226_two_chunk_single_coordinate_union_"
        "with_targeted_source_only_zero_actions"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector226-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector226-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector226-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector226-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector226_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-selector226-assignment.private.v1"
    )


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
        and tuple(row["target"]) == (0, 226)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-226 site drifted: {site}")


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
    proof["all_70_candidate_sites_reviewed"] = True
    proof["confirmed_non_display_rows_untouched"] = True
    proof["seven_terminal_records_unchanged"] = True
    proof["terminal_register_multiplicity_preserved"] = True
    proof["terminal_connective_and_space_preserved"] = True
    proof["terminal_records_absent_from_decisions"] = True
    proof["source_only_5_absent_from_current_and_candidate"] = True
    proof["source_only_action_count_zero"] = True
    proof["non_display_candidate_action_count_zero"] = True
    proof["owned_overlap_rows_require_fresh_exact_review"] = True
    coverage["guards"].pop("payload_without_guard_sha256", None)
    coverage["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        coverage
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def terminal_values(records: Mapping[tuple[int, int], Any]) -> list[str]:
    values = []
    for record_id in range(1538, 1545):
        literals = ASSIGNMENT.ASSIGNMENT.ENGINE.parse_record_literals(
            records[(0, record_id)]
        )
        BASE.require(
            len(literals) == 1,
            f"selector226 terminal literal shape drifted: {record_id}",
        )
        values.append(literals[0].text)
    return values


def terminal_digest(records: Mapping[tuple[int, int], Any]) -> str:
    return BASE.sha256_bytes(
        "\0".join(terminal_values(records)).encode("utf-8")
    )


def validate_wrapper_invariants(outputs: Mapping[Path, bytes]) -> None:
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
    chunk_decisions = [
        json.loads(line)
        for path in CHUNK_DECISIONS
        for line in path.read_text(encoding="utf-8").splitlines()
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
    terminal_roots = {(0, record_id) for record_id in range(1538, 1545)}
    decision_roots = {
        tuple(map(int, coordinate.split(":")[:2]))
        for _resource, coordinate in decision_keys
    }
    candidate, current, source, contexts, _pending = (
        ASSIGNMENT.ASSIGNMENT.RECORDS.load_records()
    )
    assignment = json.loads(
        ASSIGNMENT_PRIVATE_PATH.read_text(encoding="utf-8")
    )
    prior_evidence = {
        ":".join(str(row["coordinate"]).split(":")[:2])
        for line in (
            DIALOGUE_TMP
            / "decisions"
            / "runtime_verification_overlays"
            / "pk_thought_predicate_family_exact_closure_evidence.private.v1.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        if line
        for row in (json.loads(line),)
        if row.get("resource") == "pk_msggame"
    }
    candidate_roots = {
        ":".join(str(site).split(":")[:2])
        for site in assignment["scope"]["candidate_call_sites"]
    }
    non_display_roots = candidate_roots - prior_evidence
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed,
        "selector226 touched the confirmed-non-display universe",
    )
    BASE.require(
        not decision_roots & terminal_roots,
        "selector226 decision union changed a shared terminal",
    )
    BASE.require(
        len(non_display_roots) == 1
        and not {
            ":".join(coordinate.split(":")[:2])
            for _resource, coordinate in decision_keys
        }
        & non_display_roots,
        "selector226 non-display candidate received an action",
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
        and sorted(Counter(terminal_values(candidate)).values())
        == [1, 1, 2, 3],
        "selector226 terminal register contract drifted",
    )
    BASE.require(
        all(
            row.get("fresh_semantic_review") == "approved"
            and row.get("runtime_review") == "verified"
            for row in decisions
        ),
        "selector226 closure decisions lack fresh exact review",
    )
    BASE.require(
        all(
            row.get("fresh_semantic_review") == "approved"
            and row.get("runtime_review") == "verified"
            and row.get("predecessor_candidate_sha256")
            == EXPECTED_OFFICIAL_CANDIDATE_SHA256
            and "auto" not in str(row.get("action", "")).lower()
            for row in chunk_decisions
        ),
        "selector226 chunk decisions lack exact predecessor-state review",
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


def unresolved_placeholders() -> list[str]:
    return [
        key for key, value in EXPECTED_OUTPUT_SHA256.items() if value is None
    ]


def is_frozen() -> bool:
    return not unresolved_placeholders()


def build_outputs() -> dict[Path, bytes]:
    BASE.require(
        BASE.sha256_file(SCAFFOLD_BASE_PATH) == EXPECTED_SCAFFOLD_BASE_SHA256,
        "selector364 closure scaffold base drifted",
    )
    BASE.require(
        is_frozen(),
        "selector226 closure output pins are not frozen: "
        + ",".join(unresolved_placeholders()),
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
                f"selector226 closure output drifted: {path}",
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
