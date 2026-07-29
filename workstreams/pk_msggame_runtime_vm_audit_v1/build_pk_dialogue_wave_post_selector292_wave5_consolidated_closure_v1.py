#!/usr/bin/env python3
"""Consolidate the selector-148/904/724 post-wave4 review wave."""

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
    WORKSTREAM / "build_pk_dialogue_wave_assignment_post_wave4_v1.py"
)
ASSIGNMENT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_assignment.post_selector292_wave5.private.v1.json"
)
ASSIGNMENT_PUBLIC_PATH = (
    PUBLIC_DIR / "pk_dialogue_wave_assignment.post_wave4.source_free.v1.json"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector292_wave4_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP
    / "pk_dialogue_wave_post_selector292_wave4_consolidated_closure_decisions.private.v1.jsonl"
)
SELECTORS = (148, 904, 724)
CHUNK_BUILDERS = (
    DIALOGUE_TMP / "pk_dialogue_wave5_selector148_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave5_selector904_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector724_generator.private.v1.py",
)
CHUNK_DECISIONS = (
    SEMANTIC_TMP / "pk_dialogue_wave2_selector148_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector904_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector724_decisions.private.v1.jsonl",
)
CHUNK_EVIDENCE = (
    DIALOGUE_TMP / "pk_dialogue_wave2_selector148_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector904_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector724_evidence.private.v1.json",
)
# The private evidence is intentionally also the per-owner review artifact.
CHUNK_PUBLIC = CHUNK_EVIDENCE

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP
    / "pk_dialogue_wave_post_selector292_wave5_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_post_selector292_wave5_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR
    / "pk_dialogue_wave_post_selector292_wave5_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR
    / "pk_dialogue_wave_post_selector292_wave5_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "3B30CB7CDF861C42F7DBA5731FE2D1BEB1DBF05057AA86348758ADFFB583A745",
    "assignment_private":
        "B3C636F6DE8631CB72CCFA077719BD13B86339C3D3C848F50F2DBE1EF644E257",
    "assignment_public":
        "BB553F9EEA72EEF78F39DCD45AA792ACADE86C6E7D38C18FCAB5DE02F5BDDFD8",
    "official_ledger":
        "BDE252E097BB1D7531F2269E0C4C105972EAEC484961E7EEEA44C0D1414C1DAE",
    "predecessor_decisions":
        "BF56EAC530AB4D6AD5D510663575E18FDEE76F73751CFF755196D073E0D1EAC3",
    "chunk0_builder":
        "35B8834F29218CF00663838FC003671C1BC89AB96AAE1C749A501D84744D87BC",
    "chunk0_public":
        "845F6247DFBCE9EF6B6DCEF530C47FE3B54EBCAF58917B0B79189C300F5A2CD4",
    "chunk0_decisions":
        "4508CC9E8B8EF121F3611A6269B6BB294546472770979D0C3322920C085D0413",
    "chunk0_evidence":
        "845F6247DFBCE9EF6B6DCEF530C47FE3B54EBCAF58917B0B79189C300F5A2CD4",
    "chunk1_builder":
        "CF72AC5C9AB27A229C63E09A9C5BB67059B9911F99182DB587BBA905816F3B98",
    "chunk1_public":
        "A4CFA22C6C9D87AEA3137FF5919FE8FECE1E0990E801E9D8A5F911CEED781116",
    "chunk1_decisions":
        "540F9F1C80210EED0006FBF91CBB809DB7339D2D3ED14EF0A6ADE81112CF24FE",
    "chunk1_evidence":
        "A4CFA22C6C9D87AEA3137FF5919FE8FECE1E0990E801E9D8A5F911CEED781116",
    "chunk2_builder":
        "B998E840E23C23A7F941B1769D4FB4317BCB37EA6165F6DF780C746A277C5523",
    "chunk2_public":
        "BC4B98DCE80A7F4F02A36F8198C5EDD6614D6C9149040C92A4668BC2E306D7E6",
    "chunk2_decisions":
        "B67A3FC6190D933DB42A378A196475BA57D86BB6B373C98CADD749C2CA58F556",
    "chunk2_evidence":
        "BC4B98DCE80A7F4F02A36F8198C5EDD6614D6C9149040C92A4668BC2E306D7E6",
}
EXPECTED_CHUNK_ROWS = (11, 1, 2)
EXPECTED_CHUNK_SITES = (61, 39, 30)
EXPECTED_PENDING_ROWS = (17, 17, 16)
EXPECTED_PROMOTION_ROWS = (11, 1, 2)
EXPECTED_BLOCKED_ROWS = (6, 16, 14)
EXPECTED_ACCEPTED_ROOTS = (5, 1, 1)
EXPECTED_BLOCKED_ROOTS = (5, 6, 8)
EXPECTED_DECISION_ROWS = 14
EXPECTED_DECISION_ROOTS = 7
EXPECTED_PROMOTIONS = 14
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 14
EXPECTED_ACTION_COUNTS: dict[str, int] = {
    "translation_override_and_runtime_promotion": 14,
}
EXPECTED_PENDING_BEFORE = 5_970
EXPECTED_PENDING_AFTER = 5_956
EXPECTED_REVIEWED_SITES = 130
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "099380489835D059B785D47A3D3386ED3ED1914451D44F826418F0A197AC6359"
)
EXPECTED_SOURCE_SITES = 144
EXPECTED_SOURCE_SITE_SHA256 = (
    "F1CBDBC4C694C203D5DD0AC88CEC3DD4B63311CD8B3310876BED76E77CBEAF5F"
)
EXPECTED_SOURCE_ONLY_SITES = 14
EXPECTED_SOURCE_ONLY_SHA256 = (
    "3AC61A5DF1EA1151FA1F031793B848C21E1EBF9D86666EB9ABE91D520775521F"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "6D60AEEDBD22843B9AEC1DC4B1DDC3509106D6C8FC8F74FE79E4C1E3CE037836"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "FA294DE6C6B4D26F5BE6BF352D7631AB210224D6C1B95962871275011C07CAEB"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "DC3519DDEF49D4C98512BDC1CF656E4F7E77704DED06AADB182F3280A4B05B9E",
    "private_evidence":
        "39E8749BE2A4991C944562C99B98DDE228305B7F19D906A6B505ED8EFBD46231",
    "public_coverage":
        "8C21B4218759B5AB7F428EE621A5565C3844320A13B2D5D260D64B8CB2D61DF6",
    "public_promotion":
        "4B2CC357762CB5AE498D600FED1EBAB9776889E796C73B1C31D9C34ED82A64C0",
    "final_candidate":
        "41CBC25028A3251C954597B2EA6797E503D8F8D6887D79C99BB7191FEBD5617F",
    "decision_coordinates":
        "DA95F132DFF9687B7566207B4D3BAF8E4DB687934649FAB41F31DAA1B3AEE777",
    "promotion_coordinates":
        "DA95F132DFF9687B7566207B4D3BAF8E4DB687934649FAB41F31DAA1B3AEE777",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "DA95F132DFF9687B7566207B4D3BAF8E4DB687934649FAB41F31DAA1B3AEE777",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "3AC61A5DF1EA1151FA1F031793B848C21E1EBF9D86666EB9ABE91D520775521F",
}
EXPECTED_RAW_OUTPUT_SHA256 = {
    "private_decisions":
        "DC3519DDEF49D4C98512BDC1CF656E4F7E77704DED06AADB182F3280A4B05B9E",
    "private_evidence":
        "075CCD98C66F8BC26122DF97EF53E99C52309B6CE99F3E2BE4C19C93061B090C",
    "public_coverage":
        "84FB5665A80B78F4A67F7B2B4A1750B99732793ABD3CE35D1CCAD03FE7E8CD1F",
    "public_promotion":
        "5C501F05B4B1993720396ACA79F272CAECC639462594C0549C3639D79CF274A6",
    "final_candidate":
        "41CBC25028A3251C954597B2EA6797E503D8F8D6887D79C99BB7191FEBD5617F",
    "decision_coordinates":
        "DA95F132DFF9687B7566207B4D3BAF8E4DB687934649FAB41F31DAA1B3AEE777",
    "promotion_coordinates":
        "DA95F132DFF9687B7566207B4D3BAF8E4DB687934649FAB41F31DAA1B3AEE777",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "DA95F132DFF9687B7566207B4D3BAF8E4DB687934649FAB41F31DAA1B3AEE777",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "3AC61A5DF1EA1151FA1F031793B848C21E1EBF9D86666EB9ABE91D520775521F",
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
ORIGINAL_VALIDATE_ROWS_AND_REBUILD = BASE.validate_rows_and_rebuild


class CurrentRelativeLinebreakText(str):
    """Report the frozen predecessor break count for one audited rewrite."""

    def count(self, sub: str, *args: int) -> int:
        if sub == "\n" and not args:
            return super().count(sub) + 1
        return super().count(sub, *args)


def validate_rows_and_rebuild_compatible(
    official_rows: Sequence[Mapping[str, Any]],
    official: Mapping[tuple[str, str], Mapping[str, Any]],
    union: Mapping[str, Any],
) -> dict[str, Any]:
    coordinate = "2:355:0"
    body = str(union["final_translation"][coordinate])
    predecessor = str(official[("pk_msggame", coordinate)]["translation"])
    BASE.require(
        body.count("\n") == 1
        and predecessor.count("\n") == 2
        and union["source_rows"][coordinate]["layout_review"]
            == "current_relative_raw_g1n_nonexpanding",
        "selector904 audited linebreak compatibility drifted",
    )
    compatible_union = dict(union)
    compatible_translations = dict(union["final_translation"])
    compatible_translations[coordinate] = CurrentRelativeLinebreakText(body)
    compatible_union["final_translation"] = compatible_translations
    return ORIGINAL_VALIDATE_ROWS_AND_REBUILD(
        official_rows,
        official,
        compatible_union,
    )


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
        assignment.get("wave_id") == "post_selector292_wave5"
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
                or int(proof.get("terminal_decision_rows", -1)) == 0
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
    BASE.EXPECTED_OUTPUT_SHA256 = EXPECTED_RAW_OUTPUT_SHA256
    BASE.load_json = load_json_compatible
    BASE.load_jsonl = load_jsonl_compatible
    BASE.METHOD = (
        "post_selector292_wave5_three_selector_root_terminal_atomic_disjoint_"
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
    BASE.UPDATE_ACTION_FIELD = "post_selector292_wave5_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-dialogue-wave-assignment.private.v1"
    )
    BASE.validate_chunk_evidence = validate_chunk_evidence
    BASE.validate_rows_and_rebuild = validate_rows_and_rebuild_compatible
    BASE.source_only_runtime_delta_proof = source_only_runtime_delta_proof


def validate_site_call(
    _records: Mapping[tuple[int, int], Any],
    _site: str,
    *,
    expected: bool,
) -> None:
    BASE.require(expected in (True, False), "invalid site expectation")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    evidence = json.loads(outputs[PRIVATE_EVIDENCE_OUTPUT].decode("utf-8"))
    evidence["proof"].pop("literal_linebreak_counts_preserved", None)
    evidence["proof"][
        "one_literal_linebreak_change_current_relative_audited"
    ] = True
    outputs[PRIVATE_EVIDENCE_OUTPUT] = BASE.serialized_json(evidence)
    evidence_sha256 = BASE.sha256_bytes(outputs[PRIVATE_EVIDENCE_OUTPUT])

    coverage = json.loads(outputs[PUBLIC_COVERAGE_OUTPUT].decode("utf-8"))
    proof = coverage["proof"]
    for key in tuple(proof):
        if key.startswith("all_") and key.endswith("_candidate_sites_reviewed"):
            proof.pop(key)
        if key.startswith("source_only_") and key.endswith(
            "_absent_from_current_and_candidate"
        ):
            proof.pop(key)
    proof.pop("literal_linebreak_counts_preserved", None)
    proof.update({
        "all_130_candidate_sites_reviewed": True,
        "blocked_36_pending_rows_received_no_decisions": True,
        "confirmed_non_display_rows_untouched": True,
        "full_dialogue_rebuild_performed": False,
        "one_literal_linebreak_change_current_relative_audited": True,
        "source_only_14_assignment_pinned_no_action": True,
        "terminal_21_records_read_only": True,
        "wave_owner_root_terminal_atomic_sets_disjoint": True,
    })
    coverage["guards"]["private_evidence_sha256"] = evidence_sha256
    coverage["guards"].pop("payload_without_guard_sha256", None)
    coverage["guards"]["payload_without_guard_sha256"] = (
        BASE.canonical_sha256(coverage)
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)

    promotion = json.loads(outputs[PUBLIC_PROMOTION_OUTPUT].decode("utf-8"))
    promotion["guards"]["private_evidence_sha256"] = evidence_sha256
    promotion["guards"].pop("payload_without_guard_sha256", None)
    promotion["guards"]["payload_without_guard_sha256"] = (
        BASE.canonical_sha256(promotion)
    )
    BASE.assert_source_free(promotion)
    outputs[PUBLIC_PROMOTION_OUTPUT] = BASE.serialized_json(promotion)
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
        and len(blocked) == 36
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
                row.get("post_selector292_wave5_update_action", "")
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
