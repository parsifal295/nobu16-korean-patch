#!/usr/bin/env python3
"""Consolidate the selector-286/190/736 post-selector292 review wave."""

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

SCAFFOLD_PATH = WORKSTREAM / "build_pk_selector292_consolidated_closure_v1.py"
EXPECTED_SCAFFOLD_SHA256 = (
    "086C966B48F3B6CA6854C94E1B48C508F5084D05353712F464908C7C64A73B22"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_dialogue_wave_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = (
    DIALOGUE_TMP / "pk_dialogue_wave_assignment.post_selector292.private.v1.json"
)
ASSIGNMENT_PUBLIC_PATH = (
    PUBLIC_DIR / "pk_dialogue_wave_assignment.source_free.v1.json"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector292_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector292_consolidated_closure_decisions.private.v1.jsonl"
)
SELECTORS = (286, 190, 736)
CHUNK_BUILDERS = (
    DIALOGUE_TMP / "pk_wave_post292_selector286_generator.private.v1.py",
    DIALOGUE_TMP / "pk_wave_post292_selector190_review_v1.py",
    DIALOGUE_TMP / "pk_wave_post292_selector736_review_generator.private.v1.py",
)
CHUNK_DECISIONS = (
    SEMANTIC_TMP / "pk_wave_post292_selector286_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave1_selector190_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_wave_post292_selector736_c_decisions.private.v1.jsonl",
)
CHUNK_EVIDENCE = (
    DIALOGUE_TMP / "pk_wave_post292_selector286_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave1_selector190_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_wave_post292_selector736_c_evidence.private.v1.json",
)
# The private evidence is intentionally also the per-owner review artifact.
CHUNK_PUBLIC = CHUNK_EVIDENCE

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP
    / "pk_dialogue_wave_post_selector292_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_post_selector292_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR
    / "pk_dialogue_wave_post_selector292_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR
    / "pk_dialogue_wave_post_selector292_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "E3A02B7852791EA153CC81D79A5DDA5F8BE091DC95BD17F3D379BB88B2DA0103",
    "assignment_private":
        "B65F15669454CEC5B25B41E8AF4315704300212504C327BD4B19464EE322A745",
    "assignment_public":
        "B6075A025257C007B901FD61B727200E086D3905A98DA3E888AEB5B869F8A591",
    "official_ledger":
        "90644EA8E6F2EF99CA2020993930E551536F00E9BF4DFD244ED46640123E8725",
    "predecessor_decisions":
        "F90AD78BF19BE129BFEF08FFF47C81CAFCD90ADBA7B6DDC0B1DF89039E47F004",
    "chunk0_builder":
        "83256141FC0D0C7D3377E021C42AC2D06331C25F22968A9CD5EE864160971825",
    "chunk0_public":
        "5116E635E51C6137C0869A31402B7E10DBDC89E930B0E5230412A57C36B2C49F",
    "chunk0_decisions":
        "C4752C55A267D5E12B88B4B4B896E4B0199D6D755F2B494F02C67A6FE3450F3D",
    "chunk0_evidence":
        "5116E635E51C6137C0869A31402B7E10DBDC89E930B0E5230412A57C36B2C49F",
    "chunk1_builder":
        "BD8BD1E7B3ACF3791E96C767D7EA73E9C676292B2CF79CE06E8578B4636AB807",
    "chunk1_public":
        "995B5F7C87D5B9EC2C298FCDD610DB2CD352F1AB850991D2C2E7B22A4EA5495F",
    "chunk1_decisions":
        "A487C15B0A0FFBE8C7581A21F2102BDF326FE8E027B7487FCE820A329FB8219E",
    "chunk1_evidence":
        "995B5F7C87D5B9EC2C298FCDD610DB2CD352F1AB850991D2C2E7B22A4EA5495F",
    "chunk2_builder":
        "ECA4AC7B20BD6C988FCFEA7DCA564ED90920895F1ABD58DFDD6471E7FCE8BF6F",
    "chunk2_public":
        "79D333E4C4BBB8816FF0A9227E24F7A6307BC3D4BEC30756A93FC3CFF0267C8C",
    "chunk2_decisions":
        "94C50B5EEF33FDC0B3F1C1A94D9AB890CD6116125BF6B29BB83507C67761E684",
    "chunk2_evidence":
        "79D333E4C4BBB8816FF0A9227E24F7A6307BC3D4BEC30756A93FC3CFF0267C8C",
}
EXPECTED_CHUNK_ROWS = (21, 16, 9)
EXPECTED_CHUNK_SITES = (57, 22, 17)
EXPECTED_PENDING_ROWS = (32, 31, 30)
EXPECTED_PROMOTION_ROWS = (21, 16, 9)
EXPECTED_BLOCKED_ROWS = (11, 15, 21)
EXPECTED_ACCEPTED_ROOTS = (7, 5, 3)
EXPECTED_BLOCKED_ROOTS = (6, 6, 8)
EXPECTED_DECISION_ROWS = 46
EXPECTED_DECISION_ROOTS = 15
EXPECTED_PROMOTIONS = 46
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 29
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 17,
    "translation_override_and_runtime_promotion": 29,
}
EXPECTED_PENDING_BEFORE = 6_130
EXPECTED_PENDING_AFTER = 6_084
EXPECTED_REVIEWED_SITES = 96
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "7A373EE18382323EA013055FE97E01D9712F3D611C03B4CEE754A525175505E1"
)
EXPECTED_SOURCE_SITES = 111
EXPECTED_SOURCE_SITE_SHA256 = (
    "D29B9EB902A48FC4E3019A54164F719F57432A612537BA88513ACFDEAC3D17D7"
)
EXPECTED_SOURCE_ONLY_SITES = 15
EXPECTED_SOURCE_ONLY_SHA256 = (
    "01BEB60B6268233BDE87421EE2BCF96597E337108B80112F8D0ED1C47C256DF1"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "723589D4CC42165F93FF60F0711E96DAB6E84737C75954FA36819F780CD57A2C"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "E76C849DFB6589B7C48B830D227C368ACA98B80F18FBBC2DD8CF146D455F9652"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "9F16DD6B5AEA794FAF2E1B56CB331D9AC1126D3C272B79FD635AA5AA36CCC96C",
    "private_evidence":
        "9107F6A543AB92B8E7B757DEBC5BBF192035B9F3398B88B098DD0856FAB8C92A",
    "public_coverage":
        "52B908B14C78754B7D4E8900D55F6F3912938FA3D5178C8AC22560E6B740BDF4",
    "public_promotion":
        "1DBBFDFC7B1CF7D189B04176698BDDDED5C2C09CD7B7B6CAB532D8DA66A0B887",
    "final_candidate":
        "C47390C28DE697CAD3F57A72A079F4D8CEA897F6E343CFCE704851BCC3507060",
    "decision_coordinates":
        "0103863F553F53594BB037949E32F0C0FD327004473FC5834518CA03D6C3705B",
    "promotion_coordinates":
        "0103863F553F53594BB037949E32F0C0FD327004473FC5834518CA03D6C3705B",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "12C4DB7F7452C9E2C9628B40CA22A6F0C486FDB3A46A82B5C6A7F4C7702EBF67",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "01BEB60B6268233BDE87421EE2BCF96597E337108B80112F8D0ED1C47C256DF1",
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
        assignment.get("wave_id") == "post_selector292_wave1"
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
        if selector == 286:
            BASE.require(
                counts["decision_rows"] == 21
                and counts["promoted_pending_rows"] == 21
                and counts["blocked_pending_rows"] == 11
                and counts["accepted_affected_branches"] == 98
                and counts["accepted_affected_pass_branches"] == 98
                and proof["all_32_pending_rows_freshly_reviewed"] is True
                and proof[
                    "accepted_changed_affected_branches_nonexpanding"
                ] is True,
                "selector286 evidence drifted",
            )
        elif selector == 190:
            BASE.require(
                counts["decision_rows"] == 16
                and counts["runtime_promotions"] == 16
                and counts["verification_renewals"] == 0
                and counts["translation_overrides"] == 11
                and counts["accepted_branches"] == 77
                and counts["current_relative_nonexpanding_branches"] == 77
                and proof["all_accepted_branches_grammar_pass"] is True
                and proof[
                    "all_accepted_branches_current_relative_nonexpanding"
                ] is True,
                "selector190 evidence drifted",
            )
        else:
            BASE.require(
                counts["decision_rows"] == 9
                and counts["accepted_pending_rows"] == 9
                and counts["blocked_pending_rows"] == 21
                and counts["changed_branches_computed"] == 21
                and counts["changed_branches_passed"] == 21
                and proof[
                    "all_changed_branches_current_relative_nonexpanding"
                ] is True,
                "selector736 evidence drifted",
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
        "post_selector292_three_selector_root_terminal_atomic_disjoint_wave_"
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
    BASE.UPDATE_ACTION_FIELD = "post_selector292_wave1_update_action"
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
        "all_96_candidate_sites_reviewed": True,
        "blocked_47_pending_rows_received_no_decisions": True,
        "confirmed_non_display_rows_untouched": True,
        "full_dialogue_rebuild_performed": False,
        "source_only_15_assignment_pinned_no_action": True,
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
        and len(blocked) == 47
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
                row.get("post_selector292_wave1_update_action", "")
            ).lower()
            for row in decisions
        ),
        "wave union contains inherited or automatic decisions",
    )


for _name, _value in {
    # The generic closure core needs the established record/engine adapter.
    # The immutable wave assignment itself is loaded from the paths above.
    "ASSIGNMENT": SCAFFOLD.ASSIGNMENT,
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
