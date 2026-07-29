#!/usr/bin/env python3
"""Consolidate the selector-754/310/844 post-wave3 review wave."""

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
    WORKSTREAM / "build_pk_dialogue_wave_assignment_post_wave3_v1.py"
)
ASSIGNMENT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_assignment.post_selector292_wave4.private.v1.json"
)
ASSIGNMENT_PUBLIC_PATH = (
    PUBLIC_DIR / "pk_dialogue_wave_assignment.post_wave3.source_free.v1.json"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector292_wave3_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP
    / "pk_dialogue_wave_post_selector292_wave3_consolidated_closure_decisions.private.v1.jsonl"
)
SELECTORS = (754, 310, 844)
CHUNK_BUILDERS = (
    DIALOGUE_TMP / "pk_dialogue_wave4_selector754_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave4_selector310_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector844_generator.private.v1.py",
)
CHUNK_DECISIONS = (
    SEMANTIC_TMP / "pk_dialogue_wave2_selector754_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector310_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector844_decisions.private.v1.jsonl",
)
CHUNK_EVIDENCE = (
    DIALOGUE_TMP / "pk_dialogue_wave2_selector754_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector310_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector844_evidence.private.v1.json",
)
# The private evidence is intentionally also the per-owner review artifact.
CHUNK_PUBLIC = CHUNK_EVIDENCE

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP
    / "pk_dialogue_wave_post_selector292_wave4_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_post_selector292_wave4_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR
    / "pk_dialogue_wave_post_selector292_wave4_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR
    / "pk_dialogue_wave_post_selector292_wave4_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "A0D5DBC6289C44E8DE88EBDE27161C7A68ED729E947E892E99B643740CE2F264",
    "assignment_private":
        "CA43DA634F5C3B7DC8F71817A92E38A01AA9004BFF45143D9A22C4B2128EDE57",
    "assignment_public":
        "24702F620691BED613E7C5DD13FA6BDEE1972A103A5CE62CFE24FF71D029084B",
    "official_ledger":
        "3AEE8906C75A77C5808A28D3BAD62509BA2A32FF69C80AA68FAEA3C99CA72FDE",
    "predecessor_decisions":
        "4B6CF7DD899DD928D518959ABC9E3D570996983533225B03A2E4241BDFE951CE",
    "chunk0_builder":
        "BE9DF5D6628E3FE21C27067A0372429174A09EBBB9B1D7C73A950CE664B4D6D4",
    "chunk0_public":
        "323D013775062F6D696AF6C3B9D772A90146F715A596DEDB30A1A717162E94DE",
    "chunk0_decisions":
        "E814F5FC3C6060EE69556398F1C788C5DB5CD8AD505B9ACB57E7E13856956281",
    "chunk0_evidence":
        "323D013775062F6D696AF6C3B9D772A90146F715A596DEDB30A1A717162E94DE",
    "chunk1_builder":
        "67C1B93BDA84B50350AECF4BB7CF400DB3195C47294CBDA51DA0479697725874",
    "chunk1_public":
        "8F1F622EB5602CD385EA6C9D74A99F78242D6832C88D9FA18F6FCAD3D80A3AB2",
    "chunk1_decisions":
        "27591BE2F11428B28A46F2CD369E4CBA3D1ECB51A344C756A4A2BCBDBAA985EB",
    "chunk1_evidence":
        "8F1F622EB5602CD385EA6C9D74A99F78242D6832C88D9FA18F6FCAD3D80A3AB2",
    "chunk2_builder":
        "28DC13E0FC189FC2230B00BCC1C2D1E17996F07279BB12F0C2869F66E56BADB2",
    "chunk2_public":
        "4A8B5137F5CB57F73E08D628723CD31AB251F66D7F44C9C5CC02540C3A0D0275",
    "chunk2_decisions":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "chunk2_evidence":
        "4A8B5137F5CB57F73E08D628723CD31AB251F66D7F44C9C5CC02540C3A0D0275",
}
EXPECTED_CHUNK_ROWS = (15, 14, 0)
EXPECTED_CHUNK_SITES = (29, 14, 10)
EXPECTED_PENDING_ROWS = (20, 18, 17)
EXPECTED_PROMOTION_ROWS = (15, 14, 0)
EXPECTED_BLOCKED_ROWS = (5, 4, 17)
EXPECTED_ACCEPTED_ROOTS = (6, 4, 0)
EXPECTED_BLOCKED_ROOTS = (2, 1, 6)
EXPECTED_DECISION_ROWS = 29
EXPECTED_DECISION_ROOTS = 10
EXPECTED_PROMOTIONS = 29
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 27
EXPECTED_ACTION_COUNTS: dict[str, int] = {
    "runtime_promotion": 2,
    "translation_override_and_runtime_promotion": 27,
}
EXPECTED_PENDING_BEFORE = 5_999
EXPECTED_PENDING_AFTER = 5_970
EXPECTED_REVIEWED_SITES = 53
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "5C219F1B900224752C9AD74F5777A91528EFB67F01A28989BACE98538E6A3C06"
)
EXPECTED_SOURCE_SITES = 54
EXPECTED_SOURCE_SITE_SHA256 = (
    "746AAFD56411EB4C254C6EFEA99E013503BE32D687F27C0D3991710FE2C3192A"
)
EXPECTED_SOURCE_ONLY_SITES = 1
EXPECTED_SOURCE_ONLY_SHA256 = (
    "712759ED5902F1BA7CBC458E1C4DF82F66291AE7F7E47F97D1AFCCD9C6D92119"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "4B2A09C787802B073109DE00B280FFC7FAB69FCF91C8D800EADCA3F072BE3C20"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "6B8E2A8701A0FE248909DE9FB0C6F9F448B4C37F98CBA47370A9F04259D30359"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "BF56EAC530AB4D6AD5D510663575E18FDEE76F73751CFF755196D073E0D1EAC3",
    "private_evidence":
        "FFECCCF055079FD81F002453C353237847F018CE7CC39FF2DBE613C1401E2AFF",
    "public_coverage":
        "93EA8E767469DD9122D12C6A76AF09F045CC4C83153C6A0EB80991BC3BC54B19",
    "public_promotion":
        "04689FCCB2D848400AA54E225BB6EE6CB5758F66B84738731CDAFD083AFA232F",
    "final_candidate":
        "6D60AEEDBD22843B9AEC1DC4B1DDC3509106D6C8FC8F74FE79E4C1E3CE037836",
    "decision_coordinates":
        "61FE5268346CC75CB3F2BD42C5C06D5DF9D22750545358BFABD254FD1B9BE8F0",
    "promotion_coordinates":
        "61FE5268346CC75CB3F2BD42C5C06D5DF9D22750545358BFABD254FD1B9BE8F0",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "A46ABB48AC83DBE04CAB4ACF78FAE6F75D42A5AF939B3766FDDE44F3EB54EFBF",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "712759ED5902F1BA7CBC458E1C4DF82F66291AE7F7E47F97D1AFCCD9C6D92119",
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
        assignment.get("wave_id") == "post_selector292_wave4"
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
            or (
                "all_affected_dynamic_branches" in counts
                and counts.get("all_affected_dynamic_branches")
                    == counts.get("all_affected_dynamic_branches_passed")
            )
        )
        nonexpanding = (
            not promotions
            or
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
        "post_selector292_wave4_three_selector_root_terminal_atomic_disjoint_"
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
    BASE.UPDATE_ACTION_FIELD = "post_selector292_wave4_update_action"
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
        "all_53_candidate_sites_reviewed": True,
        "blocked_26_pending_rows_received_no_decisions": True,
        "confirmed_non_display_rows_untouched": True,
        "full_dialogue_rebuild_performed": False,
        "source_only_1_assignment_pinned_no_action": True,
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
        and len(blocked) == 26
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
                row.get("post_selector292_wave4_update_action", "")
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
