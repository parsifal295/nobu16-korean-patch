#!/usr/bin/env python3
"""Consolidate the two selector-268 reviews on the post-selector226 state."""

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

SCAFFOLD_PATH = (
    WORKSTREAM / "build_pk_selector226_consolidated_closure_v1.py"
)
EXPECTED_SCAFFOLD_SHA256 = (
    "2925F268AC098096F94F4E4D91F14EC89C6CF06C14E8F7DF9CD85153DC2523C3"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector268_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector268_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector268_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector226_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector226_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector268_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector268_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector268_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector268_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector268_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector268_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector268_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector268_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "8D0B1F1156ABD01697502DEA809B15C483F3D9EC1AA3D16AF6509423A72FC1E1",
    "assignment_private":
        "91ED0510E5783DDA7B6894CA8A5144FB4D2FA9300A71BD2EC1B2F4699022C315",
    "assignment_public":
        "5F0C6B1935B7EC8568DC7C52EFB67D90BEF96398A8977DFEA70B23B3FA71053B",
    "official_ledger":
        "33B635E1409B290202A98719A9CD58F356551BB54703B7F287FC45250134623D",
    "predecessor_decisions":
        "C01523FE952E960CEF95DB8F9469BA388211C2B8F228CA269C9C32127599D5EB",
    "chunk0_builder":
        "D0224BC83436F1E752A1F85674E41273BA2445CB9111604A745C6EFD85633CC7",
    "chunk0_public":
        "16E4EBED73904001F5FD160FD41BF6EE3D23629B0F000C4C6D549D0721FAB7CB",
    "chunk0_decisions":
        "5941B268BEE074B6C8B168F09CB2F78C26EE769C29E6B6C10F1739BC57BA5FD3",
    "chunk0_evidence":
        "AF95272CED53A341445A8060F309F3AF96FC39BCB11EA96F8EC774BBF5ACD107",
    "chunk1_builder":
        "0E204C1C166E8CC49784BE6940242CBDD00EA9C96885BD1F74296B38A6A4BCC8",
    "chunk1_public":
        "67812DFAEDBDA6400A729583CC05D30A8BBD238117088A5142E110DA7779978E",
    "chunk1_decisions":
        "5971BC8E14E713173EBCFFFD214BD0F6CE4A77BCD5613CB23BCC8A0D4961E23C",
    "chunk1_evidence":
        "E1C76FF7F38290F0BF517CA64590D946AB3F6EA0BE7D381F370B92B883F2C3AD",
}
EXPECTED_CHUNK_ROWS = (10, 4)
EXPECTED_CHUNK_SITES = (13, 13)
EXPECTED_DECISION_ROWS = 14
EXPECTED_DECISION_ROOTS = 5
EXPECTED_PROMOTIONS = 14
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 4
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 10,
    "translation_override_and_runtime_promotion": 4,
}
EXPECTED_PENDING_BEFORE = 6_246
EXPECTED_PENDING_AFTER = 6_232
EXPECTED_REVIEWED_SITES = 26
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "3FDB6788D4670F06997A40BC31275AA56EC7E775FCEFDC397B54D5741F651142"
)
EXPECTED_SOURCE_SITES = 27
EXPECTED_SOURCE_SITE_SHA256 = (
    "AFB26D744F1B6ABB625B6CA45085A5B8C024155E91B5FAD4C86B0F9D3AEE5DE9"
)
EXPECTED_SOURCE_ONLY_SITES = 1
EXPECTED_SOURCE_ONLY_SHA256 = (
    "47A042EFCBA796AEB1E3DB210F0E145E2009C0FB9FA2D3AD1301EA410B791A9C"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "FEE99844339C291F6950BEB2193AB5FDD8D25B6F6117AD52F81DCBF7F0CC9B66"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "8526C4C53B87ED529D6C9EC44FF00FC9B77703EB6D4369DB83F4B916BAE37337"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "4B8A084ECCE354B2B0201FD5A7490CE5FEE18E0A7EBDD40C3908CB2E6EED04D1"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "5A9B895D4F1D91B2BA58C6607ED672C28F256DD3D2C1A114E2097D041A9B2F6D"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "3151D392EC13DFEA77F2972C31CEBD28D120C117C484E43C386DCB71FCB3160F"
)
EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "127BA2D9B9F443AA4DF5030643F476CBB943C971300020F249461A3745F6D93F",
    "private_evidence":
        "7905F468ACDC3216D0576B4AA80C2BAC6ACECC3F28C2BE53E19F626207B43E80",
    "public_coverage":
        "651CA4CC1D9D7DBE22E85224B5FE7E2FB2BF8E26488AB7DBF4BD349B098810CE",
    "public_promotion":
        "7D7213A113F4F5A743025AE2628FAA0007EE0290F8D3784A6D609C07B3B53FE1",
    "final_candidate":
        "92B86808931C1FD34320BC5A9BFD05B7AD704FA9392534FF8DE8F6293F413DAD",
    "decision_coordinates":
        "F2DCA4787227A6B6CB90FA491122DE500AA6E514594B16143248AB582371F23A",
    "promotion_coordinates":
        "F2DCA4787227A6B6CB90FA491122DE500AA6E514594B16143248AB582371F23A",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "2F8B60F09D5C3A02DD99127291E9A796D4CFB89AEB9B303A234400130984E9E5",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "283CFE4F8CC508E745CBD06ED7B87FFF07E1AC05F3A3A061263082AD5C421C9E",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCAFFOLD = load_module(SCAFFOLD_PATH, "selector268_closure_scaffold")
WRAPPER = SCAFFOLD.WRAPPER
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector268_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = SCAFFOLD.ORIGINAL_CONFIGURE_BASE


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector226_selector268_two_chunk_single_coordinate_union_"
        "with_question_and_same_gap_block_guards"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector268-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector268-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector268-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector268-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector268_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-selector268-assignment.private.v1"
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
        and tuple(row["target"]) == (0, 268)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-268 site drifted: {site}")


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
        "all_26_candidate_sites_reviewed": True,
        "completed_selector_overlaps_freshly_reviewed": True,
        "confirmed_non_display_rows_untouched": True,
        "non_display_candidate_action_count_zero": True,
        "pending_assembly_evidence_did_not_auto_promote": True,
        "same_gap_atom_blocked_as_one_unit": True,
        "seven_terminal_records_unchanged": True,
        "source_only_1_absent_from_current_and_candidate": True,
        "source_only_action_count_zero": True,
        "terminal_records_absent_from_decisions": True,
        "terminal_register_multiplicity_preserved": True,
    })
    coverage["guards"].pop("payload_without_guard_sha256", None)
    coverage["guards"]["payload_without_guard_sha256"] = BASE.canonical_sha256(
        coverage
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def terminal_values(records: Mapping[tuple[int, int], Any]) -> list[str]:
    values = []
    for record_id in range(1587, 1594):
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
    decisions = [
        json.loads(line)
        for line in outputs[PRIVATE_DECISIONS_OUTPUT]
        .decode("utf-8", errors="strict")
        .splitlines()
        if line
    ]
    assignment = json.loads(
        ASSIGNMENT_PRIVATE_PATH.read_text(encoding="utf-8")
    )
    decision_roots = {
        ":".join(str(row["coordinate"]).split(":")[:2])
        for row in decisions
    }
    terminal_roots = {
        f"0:{record_id}" for record_id in range(1587, 1594)
    }
    same_gap_roots = set(assignment["same_gap_control_atom"]["roots"])
    candidate, current, source, contexts, _pending = (
        ASSIGNMENT.ASSIGNMENT.RECORDS.load_records()
    )
    BASE.require(
        not decision_roots & terminal_roots
        and not decision_roots & same_gap_roots,
        "shared terminal or same-gap atom entered decision union",
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
        and sorted(Counter(terminal_values(candidate)).values()) == [1, 2, 4],
        "selector268 terminal contract drifted",
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
    chunk_evidence = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in CHUNK_EVIDENCE
    ]
    BASE.require(
        not chunk_evidence[0]["prior_evidence"][
            "automatic_status_promotion_authorized"
        ]
        and chunk_evidence[1]["counts"]["same_gap_atoms"] == 1
        and chunk_evidence[1]["counts"]["same_gap_blocked_rows"] == 1,
        "prior-evidence or same-gap rejection drifted",
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
        "selector226 closure scaffold drifted",
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
                f"selector268 closure output drifted: {path}",
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
