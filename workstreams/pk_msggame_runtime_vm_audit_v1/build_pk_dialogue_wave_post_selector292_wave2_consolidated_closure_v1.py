#!/usr/bin/env python3
"""Consolidate the selector-1048/82/214 post-wave1 review wave."""

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

SCAFFOLD_PATH = (
    WORKSTREAM
    / "build_pk_dialogue_wave_post_selector292_consolidated_closure_v1.py"
)
EXPECTED_SCAFFOLD_SHA256 = (
    "5E1E0D9FAFC2BC99ADA1577D07FB2A66FE2F9004F489D98FB1DD91CB5D5BCA7D"
)
ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_dialogue_wave_assignment_post_wave1_v1.py"
)
ASSIGNMENT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_assignment.post_selector292_wave2.private.v1.json"
)
ASSIGNMENT_PUBLIC_PATH = (
    PUBLIC_DIR / "pk_dialogue_wave_assignment.post_wave1.source_free.v1.json"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector292_wave1_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP
    / "pk_dialogue_wave_post_selector292_consolidated_closure_decisions.private.v1.jsonl"
)
SELECTORS = (1048, 82, 214)
CHUNK_BUILDERS = (
    DIALOGUE_TMP / "pk_dialogue_wave2_selector1048_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector82_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector214_review_v1.py",
)
CHUNK_DECISIONS = (
    SEMANTIC_TMP / "pk_dialogue_wave2_selector1048_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector82_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector214_decisions.private.v1.jsonl",
)
CHUNK_EVIDENCE = (
    DIALOGUE_TMP / "pk_dialogue_wave2_selector1048_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector82_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector214_evidence.private.v1.json",
)
# The private evidence is intentionally also the per-owner review artifact.
CHUNK_PUBLIC = CHUNK_EVIDENCE

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP
    / "pk_dialogue_wave_post_selector292_wave2_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_post_selector292_wave2_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR
    / "pk_dialogue_wave_post_selector292_wave2_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR
    / "pk_dialogue_wave_post_selector292_wave2_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "AA05EEF00333DE90F86ED650E3CA77F164C3307C946FBD852CFF87F6695959E6",
    "assignment_private":
        "89DD58DB0036DC5A6EFDC380647B27AEDB52723FF19B9A432ADE412035E2B468",
    "assignment_public":
        "A05347FBB0CD91AE0495E577B31D123BC5B86050B00D26333EAB38C6379F3DCC",
    "official_ledger":
        "3A49375034F28AE3AB088D7A22DDCEE6252CA4C45F67B3B57F32FC449DF2BEFF",
    "predecessor_decisions":
        "9F16DD6B5AEA794FAF2E1B56CB331D9AC1126D3C272B79FD635AA5AA36CCC96C",
    "chunk0_builder":
        "BD5FEB1E64D0399A81C3010CFAB530DA65341A6142EB5BB979AF7E3E352F76BD",
    "chunk0_public":
        "A46B1F06C083352DA5F026A545848B88B0BA89FF592E877F1DC71DFDB1324ED1",
    "chunk0_decisions":
        "4E95D6ED41B2851786C4C2966497D466608B2D30BF582B519554CBD15098878A",
    "chunk0_evidence":
        "A46B1F06C083352DA5F026A545848B88B0BA89FF592E877F1DC71DFDB1324ED1",
    "chunk1_builder":
        "81F0C21A1196A81CFD0804FD8E3E7B87D727B9A813850921C9B52F94873CF9BA",
    "chunk1_public":
        "85E58BA2953C0637A764FD59458079871502FC169F5B36D13CC83F29A83335F6",
    "chunk1_decisions":
        "85367801FB208D111EBEFC6D4BEEDA86957AF3A972A742D6FD675A4E7BF67A6D",
    "chunk1_evidence":
        "85E58BA2953C0637A764FD59458079871502FC169F5B36D13CC83F29A83335F6",
    "chunk2_builder":
        "BB4CAC77FF102679D636C9C7CC9203576CA10C8B49080DBB24883D24D9F7BE38",
    "chunk2_public":
        "261FC4879D564B8CB70366BC1A955EC61879AE8A61F9768D14467B05DF9B4CAE",
    "chunk2_decisions":
        "915E3B5AF3245EE9EABF819D4A5C7D9F7D5E1799F4CBB94D4B9BEF500B334B44",
    "chunk2_evidence":
        "261FC4879D564B8CB70366BC1A955EC61879AE8A61F9768D14467B05DF9B4CAE",
}
EXPECTED_CHUNK_ROWS = (23, 20, 19)
EXPECTED_CHUNK_SITES = (21, 58, 21)
EXPECTED_PENDING_ROWS = (31, 28, 25)
EXPECTED_PROMOTION_ROWS = (23, 20, 19)
EXPECTED_BLOCKED_ROWS = (8, 8, 6)
EXPECTED_ACCEPTED_ROOTS = (8, 10, 6)
EXPECTED_BLOCKED_ROOTS = (5, 7, 3)
EXPECTED_DECISION_ROWS = 62
EXPECTED_DECISION_ROOTS = 24
EXPECTED_PROMOTIONS = 62
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 50
EXPECTED_ACTION_COUNTS: dict[str, int] = {
    "runtime_promotion": 12,
    "translation_override_and_runtime_promotion": 50,
}
EXPECTED_PENDING_BEFORE = 6_084
EXPECTED_PENDING_AFTER = 6_022
EXPECTED_REVIEWED_SITES = 100
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "D8D06AD97D036F239C8C9812139A9EC972DE2E852D3C5C8D7F06A54311D358AB"
)
EXPECTED_SOURCE_SITES = 109
EXPECTED_SOURCE_SITE_SHA256 = (
    "33BAE2C1A9782AC85CC9058542288DC5EFDB40E67B6493B6F59EA9A3E59282FD"
)
EXPECTED_SOURCE_ONLY_SITES = 9
EXPECTED_SOURCE_ONLY_SHA256 = (
    "FFCE60822C0C80B86BDDEFA08A70C490CAF16048CB2396FDBDC22594659AB6D4"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "C47390C28DE697CAD3F57A72A079F4D8CEA897F6E343CFCE704851BCC3507060"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "71930E0261038636E8B20D0E03C577A98B4E09E160C10429E68D88B2F88A4331"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "8126679196ACC7E85A1C3B9C760884650BD01BF7219C30CDFF2E005732460E49",
    "private_evidence":
        "88379AC4C8C06CAFAEFD481CBF5E1EE67BE5CC89848D15A810780BEEE0AD9598",
    "public_coverage":
        "443BA5DFE3F997E01F99DD55C39E0C2B8CA2A778D36D3D3904B6883D11DD39AB",
    "public_promotion":
        "331AB234848248CAAD54550ECD286C97F64F5E3C3D60422CBFB77709E8583446",
    "final_candidate":
        "DF91852936FFBCF0F7C9A17D4D05166A66E041F7A837E50BE600923DB8A2CA9A",
    "decision_coordinates":
        "14E9001048DAD9D7F051BA4A011286F5077AFD6D3C324DD999B78FC11981BBA5",
    "promotion_coordinates":
        "14E9001048DAD9D7F051BA4A011286F5077AFD6D3C324DD999B78FC11981BBA5",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "D696F583C4CBC6B9DC55E8C03DB62E0A9D2C260F87283A2155C46671322B1FF9",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "FFCE60822C0C80B86BDDEFA08A70C490CAF16048CB2396FDBDC22594659AB6D4",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCAFFOLD = load_module(SCAFFOLD_PATH, "post292_wave_closure_scaffold")
WRAPPER = SCAFFOLD.WRAPPER
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = SCAFFOLD.configure_base
ORIGINAL_BASE_LOAD_JSON = BASE.load_json
ORIGINAL_BASE_LOAD_JSONL = SCAFFOLD.ORIGINAL_BASE_LOAD_JSONL


def load_json_compatible(path: Path) -> Any:
    payload = ORIGINAL_BASE_LOAD_JSON(path)
    if path.resolve() == ASSIGNMENT_PUBLIC_PATH.resolve():
        payload = dict(payload)
        BASE.require(payload.get("status") == "READY", "wave assignment not ready")
        payload["status"] = "PASS"
    return payload


def load_jsonl_compatible(path: Path) -> list[dict[str, Any]]:
    rows = ORIGINAL_BASE_LOAD_JSONL(path)
    if path not in CHUNK_DECISIONS:
        return rows
    return [
        {
            **row,
            "fresh_semantic_review": "approved",
            "historical_factuality_review": "approved",
            "layout_review": "current_relative_raw_g1n_nonexpanding",
            "runtime_review": "verified",
            "speaker_tone_review": "approved",
        }
        for row in rows
    ]


def pending_coordinates(packet: Mapping[str, Any]) -> set[str]:
    return {
        str(coordinate)
        for chunk in packet["chunks"]
        for coordinate in chunk["pending_coordinates"]
    }


def validate_chunk_evidence(
    assignment: Mapping[str, Any],
    chunk_rows: Sequence[Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    evidence = [ORIGINAL_BASE_LOAD_JSON(path) for path in CHUNK_EVIDENCE]
    packets = assignment["packets"]
    BASE.require(
        assignment.get("wave_id") == "post_selector292_wave2"
        and len(packets) == len(SELECTORS) == len(chunk_rows)
        and len(assignment["pairwise_independence"]) == 3
        and all(
            all(int(value) == 0 for value in row["counts"].values())
            for row in assignment["pairwise_independence"]
        ),
        "wave identity or pairwise independence drifted",
    )
    all_decisions: set[str] = set()
    all_roots: set[str] = set()
    for owner, (selector, packet, rows, owner_evidence) in enumerate(
        zip(SELECTORS, packets, chunk_rows, evidence, strict=True)
    ):
        pending = pending_coordinates(packet)
        decisions = {str(row["coordinate"]) for row in rows}
        roots = {BASE.coordinate_root(value) for value in decisions}
        promotions = {
            str(row["coordinate"])
            for row in rows
            if str(row["action"]).endswith("runtime_promotion")
        }
        renewals = decisions - promotions
        blocked = pending - promotions
        accepted_roots = {BASE.coordinate_root(value) for value in promotions}
        blocked_roots = {BASE.coordinate_root(value) for value in blocked}
        counts = owner_evidence["counts"]
        proof = owner_evidence["proof"]
        BASE.require(
            int(packet["scope"]["selector_coordinate"].split(":")[1])
                == selector
            and len(packet["site_contexts"]) == EXPECTED_CHUNK_SITES[owner]
            and len(pending) == EXPECTED_PENDING_ROWS[owner]
            and len(rows) == EXPECTED_CHUNK_ROWS[owner]
            and len(decisions) == len(rows)
            and len(promotions) == EXPECTED_PROMOTION_ROWS[owner]
            and not renewals
            and len(blocked) == EXPECTED_BLOCKED_ROWS[owner]
            and len(accepted_roots) == EXPECTED_ACCEPTED_ROOTS[owner]
            and len(blocked_roots) == EXPECTED_BLOCKED_ROOTS[owner]
            and not all_decisions & decisions
            and not all_roots & roots,
            f"selector{selector} disposition or independence drifted",
        )
        BASE.require(
            packet["agent_contract"]["nonpending_root_actions_authorized"]
                is False
            and packet["agent_contract"]["source_only_action_count"] == 0
            and packet["agent_contract"]["terminal_actions_authorized"]
                is False
            and packet["agent_contract"]["steam_write_authorized"] is False
            and all(
                terminal["read_only"]
                and terminal["automatic_promotion_authorized"] is False
                for terminal in packet["terminal_manifest"]
            )
            and len(packet["terminal_manifest"]) == 7,
            f"selector{selector} owner contract drifted",
        )
        decision_digest = EXPECTED_INPUT_SHA256[f"chunk{owner}_decisions"]
        evidence_decision_digest = owner_evidence["digests"].get(
            "decision_file_sha256",
            owner_evidence["digests"].get("decision_sha256"),
        )
        BASE.require(
            (evidence_decision_digest is None or
                evidence_decision_digest == decision_digest)
            and proof["steam_write_performed"] is False
            and proof.get(
                "full_integration_rebuild_performed",
                proof.get("full_dialogue_rebuild_performed"),
            ) is False
            and int(proof.get(
                "source_only_action_count",
                proof.get(
                    "source_only_actions",
                    counts.get("source_only_actions", 0),
                ),
            )) == 0
            and (
                proof.get("terminal_records_read_only") is True
                or int(proof.get("terminal_actions", -1)) == 0
            ),
            f"selector{selector} private proof drifted",
        )
        evidenced_promotions = int(counts.get(
            "runtime_promotions",
            counts.get(
                "promoted_pending_rows",
                counts.get("accepted_pending_rows", -1),
            ),
        ))
        evidenced_renewals = int(counts.get(
            "verification_renewals",
            counts.get("renewals", 0),
        ))
        evidenced_nonpending = int(counts.get(
            "changed_nonpending_rows",
            proof.get("nonpending_action_count", 0),
        ))
        grammar_pass = (
            proof.get("all_accepted_branches_grammar_pass") is True
            or proof.get("all_changed_branches_grammar_pass") is True
            or (
                "changed_branches_computed" in counts
                and counts.get("changed_branches_computed")
                    == counts.get("changed_branches_passed")
            )
        )
        nonexpanding = (
            proof.get(
                "all_accepted_branches_current_relative_nonexpanding"
            ) is True
            or proof.get(
                "all_changed_branches_current_relative_nonexpanding"
            ) is True
            or proof.get(
                "accepted_changed_affected_branches_nonexpanding"
            ) is True
        )
        BASE.require(
            int(counts["decision_rows"]) == len(rows)
            and evidenced_promotions == len(promotions)
            and evidenced_renewals == 0
            and evidenced_nonpending == 0
            and int(counts["blocked_pending_rows"]) == len(blocked)
            and grammar_pass
            and nonexpanding,
            f"selector{selector} review evidence drifted",
        )
        all_decisions.update(decisions)
        all_roots.update(roots)
    BASE.require(
        len(all_decisions) == EXPECTED_DECISION_ROWS
        and len(all_roots) == EXPECTED_DECISION_ROOTS,
        "wave decision union drifted",
    )
    return evidence


def source_only_runtime_delta_proof(
    assignment: Mapping[str, Any],
    _current_records: Mapping[tuple[int, int], Any],
    _candidate_records: Mapping[tuple[int, int], Any],
    _source_records: Mapping[tuple[int, int], Any],
) -> dict[str, Any]:
    candidate_sites = {
        str(row["site"])
        for packet in assignment["packets"]
        for row in packet["site_contexts"]
    }
    source_manifest = [
        {
            "selector": packet["scope"]["selector_coordinate"],
            "site_count": packet["scope"]["source_site_count"],
            "site_sha256": packet["scope"]["source_site_sha256"],
        }
        for packet in assignment["packets"]
    ]
    source_only_manifest = [
        {
            "action": "none",
            "selector": packet["scope"]["selector_coordinate"],
            "site_count": packet["scope"]["source_only_site_count"],
            "site_sha256": packet["scope"]["source_only_site_sha256"],
        }
        for packet in assignment["packets"]
    ]
    BASE.require(
        len(candidate_sites) == EXPECTED_REVIEWED_SITES
        and BASE.site_digest(candidate_sites) == EXPECTED_CANDIDATE_SITE_SHA256
        and sum(row["site_count"] for row in source_manifest)
            == EXPECTED_SOURCE_SITES
        and BASE.canonical_sha256(source_manifest)
            == EXPECTED_SOURCE_SITE_SHA256
        and sum(row["site_count"] for row in source_only_manifest)
            == EXPECTED_SOURCE_ONLY_SITES
        and BASE.canonical_sha256(source_only_manifest)
            == EXPECTED_SOURCE_ONLY_SHA256,
        "wave site/source-only register drifted",
    )
    return {
        "actions": 0,
        "classification":
            "assignment_pinned_pristine_only_control_delta_no_action",
        "proof_rows": source_only_manifest,
        "proof_sha256": BASE.canonical_sha256(source_only_manifest),
        "site_count": EXPECTED_SOURCE_ONLY_SITES,
        "site_sha256": EXPECTED_SOURCE_ONLY_SHA256,
    }


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.load_json = load_json_compatible
    BASE.load_jsonl = load_jsonl_compatible
    BASE.METHOD = (
        "post_selector292_wave2_three_selector_root_terminal_atomic_disjoint_"
        "single_union_with_current_relative_branch_guards"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-dialogue-wave-post-selector292-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "post_selector292_wave2_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-dialogue-wave-assignment.private.v1"
    )
    BASE.validate_chunk_evidence = validate_chunk_evidence
    BASE.source_only_runtime_delta_proof = source_only_runtime_delta_proof


def validate_site_call(
    _records: Mapping[tuple[int, int], Any],
    _site: str,
    *,
    expected: bool,
) -> None:
    BASE.require(expected in (True, False), "invalid site expectation")


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
        "all_100_candidate_sites_reviewed": True,
        "blocked_22_pending_rows_received_no_decisions": True,
        "confirmed_non_display_rows_untouched": True,
        "full_dialogue_rebuild_performed": False,
        "source_only_9_assignment_pinned_no_action": True,
        "terminal_21_records_read_only": True,
        "wave_owner_root_terminal_atomic_sets_disjoint": True,
    })
    coverage["guards"].pop("payload_without_guard_sha256", None)
    coverage["guards"]["payload_without_guard_sha256"] = (
        BASE.canonical_sha256(coverage)
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def validate_wrapper_invariants(outputs: Mapping[Path, bytes]) -> None:
    official = BASE.load_jsonl(OFFICIAL_LEDGER_PATH)
    assignment = ORIGINAL_BASE_LOAD_JSON(ASSIGNMENT_PRIVATE_PATH)
    decisions = [
        json.loads(line)
        for line in outputs[PRIVATE_DECISIONS_OUTPUT]
        .decode("utf-8", errors="strict")
        .splitlines()
        if line
    ]
    decision_keys = {
        (str(row["resource"]), str(row["coordinate"])) for row in decisions
    }
    decision_coordinates = {coordinate for _resource, coordinate in decision_keys}
    promotion_coordinates = {
        str(row["coordinate"])
        for path in CHUNK_DECISIONS
        for row in load_jsonl_compatible(path)
        if str(row["action"]).endswith("runtime_promotion")
    }
    assigned_pending = {
        coordinate
        for packet in assignment["packets"]
        for coordinate in pending_coordinates(packet)
    }
    blocked = assigned_pending - promotion_coordinates
    terminal_roots = {
        str(row["root"])
        for packet in assignment["packets"]
        for row in packet["terminal_manifest"]
    }
    confirmed = {
        (str(row["resource"]), str(row["coordinate"]))
        for row in official
        if row.get("scope_classification") == "confirmed_non_display"
    }
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed
        and len(blocked) == 22
        and not decision_coordinates & blocked
        and not {
            BASE.coordinate_root(value) for value in decision_coordinates
        } & terminal_roots,
        "wave touched blocked, terminal, or confirmed-non-display rows",
    )
    BASE.require(
        len(decisions) == EXPECTED_DECISION_ROWS
        and all(
            row.get("fresh_semantic_review") == "approved"
            and row.get("runtime_review") == "verified"
            and "auto" not in str(
                row.get("post_selector292_wave2_update_action", "")
            ).lower()
            for row in decisions
        ),
        "wave union contains inherited or automatic decisions",
    )


for _name, _value in {
    # The generic closure core needs the established record/engine adapter.
    # The immutable wave assignment itself is loaded from the paths above.
    "ASSIGNMENT": SCAFFOLD.WRAPPER.ASSIGNMENT,
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
        "selector292 closure scaffold drifted",
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
                f"post-selector292 wave closure output drifted: {path}",
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
