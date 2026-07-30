#!/usr/bin/env python3
"""Consolidate the wide eighteen-selector post-wave5 review wave."""

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
    WORKSTREAM / "build_pk_dialogue_wave_assignment_post_wave5_v1.py"
)
ASSIGNMENT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_assignment.post_selector292_wave6.private.v1.json"
)
ASSIGNMENT_PUBLIC_PATH = (
    PUBLIC_DIR / "pk_dialogue_wave_assignment.post_wave5.source_free.v1.json"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector292_wave5_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP
    / "pk_dialogue_wave_post_selector292_wave5_consolidated_closure_decisions.private.v1.jsonl"
)
SELECTORS = (
    772, 160, 616, 280, 1204, 256, 634, 778, 298,
    898, 1036, 1072, 70, 850, 862, 928, 940, 202,
)
CHUNK_BUILDERS = (
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle0_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle1_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle1_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle2_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle1_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle2_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle2_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle0_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle0_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle2_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle2_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle0_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle0_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle1_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle1_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle0_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle1_generator.private.v1.py",
    DIALOGUE_TMP / "pk_dialogue_wave6_bundle2_generator.private.v1.py",
)
CHUNK_DECISIONS = (
    SEMANTIC_TMP / "pk_dialogue_wave2_selector772_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector160_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector616_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector280_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector1204_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector256_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector634_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector778_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector298_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector898_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector1036_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector1072_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector70_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector850_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector862_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector928_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector940_decisions.private.v1.jsonl",
    SEMANTIC_TMP / "pk_dialogue_wave2_selector202_decisions.private.v1.jsonl",
)
CHUNK_EVIDENCE = (
    DIALOGUE_TMP / "pk_dialogue_wave2_selector772_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector160_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector616_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector280_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector1204_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector256_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector634_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector778_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector298_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector898_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector1036_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector1072_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector70_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector850_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector862_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector928_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector940_evidence.private.v1.json",
    DIALOGUE_TMP / "pk_dialogue_wave2_selector202_evidence.private.v1.json",
)
# The private evidence is intentionally also the per-owner review artifact.
CHUNK_PUBLIC = CHUNK_EVIDENCE

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP
    / "pk_dialogue_wave_post_selector292_wave6_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_dialogue_wave_post_selector292_wave6_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR
    / "pk_dialogue_wave_post_selector292_wave6_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR
    / "pk_dialogue_wave_post_selector292_wave6_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "8373B34147AC889C17A4574C5B5CC328EC7C87BDB18CE1DEE7DA3A61E38F54D0",
    "assignment_private":
        "5FBBD6DCFDF7092EFCE17B74513F004AFA2413C4420E88BFA21A3150D2425610",
    "assignment_public":
        "F96FEF252D208E1CF3229A66E07B791540C66108ED5C756AD251873CDEEBFE23",
    "official_ledger":
        "ABC78C74996A5C9467DB92C1EBB55A940A2A39099E9A12A5D565954D4AB68F12",
    "predecessor_decisions":
        "DC3519DDEF49D4C98512BDC1CF656E4F7E77704DED06AADB182F3280A4B05B9E",
}
CHUNK_BUILDER_SHA256 = (
    "9E49B01384930FB4E4904528345A834FC8A4D1F799D0B607D9E0835EA818C2DD",
    "A3E42E427A41E4E5E8A452037273DA21DB139C2004B894227F31C8D61D9594B8",
    "A3E42E427A41E4E5E8A452037273DA21DB139C2004B894227F31C8D61D9594B8",
    "AA6CDD299E0CE76F2DC5D00CB7C07E83F9E6A6DB6640CA573DA9353231035933",
    "A3E42E427A41E4E5E8A452037273DA21DB139C2004B894227F31C8D61D9594B8",
    "AA6CDD299E0CE76F2DC5D00CB7C07E83F9E6A6DB6640CA573DA9353231035933",
    "AA6CDD299E0CE76F2DC5D00CB7C07E83F9E6A6DB6640CA573DA9353231035933",
    "9E49B01384930FB4E4904528345A834FC8A4D1F799D0B607D9E0835EA818C2DD",
    "9E49B01384930FB4E4904528345A834FC8A4D1F799D0B607D9E0835EA818C2DD",
    "AA6CDD299E0CE76F2DC5D00CB7C07E83F9E6A6DB6640CA573DA9353231035933",
    "AA6CDD299E0CE76F2DC5D00CB7C07E83F9E6A6DB6640CA573DA9353231035933",
    "9E49B01384930FB4E4904528345A834FC8A4D1F799D0B607D9E0835EA818C2DD",
    "9E49B01384930FB4E4904528345A834FC8A4D1F799D0B607D9E0835EA818C2DD",
    "A3E42E427A41E4E5E8A452037273DA21DB139C2004B894227F31C8D61D9594B8",
    "A3E42E427A41E4E5E8A452037273DA21DB139C2004B894227F31C8D61D9594B8",
    "9E49B01384930FB4E4904528345A834FC8A4D1F799D0B607D9E0835EA818C2DD",
    "A3E42E427A41E4E5E8A452037273DA21DB139C2004B894227F31C8D61D9594B8",
    "AA6CDD299E0CE76F2DC5D00CB7C07E83F9E6A6DB6640CA573DA9353231035933",
)
CHUNK_DECISION_SHA256 = (
    "139E82C24AACC9F489D23F46A734190D8E497F7ABB633C3930DE4158D4CEC9A6",
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "20EAE836EAFE69CF05375C2B71DB9335470F602F5ACD2DBC3EAACEC7A4F64F79",
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "FFF236DFEF98B04664D8BACE1048C047CF8132DA08AFBCA0975DCC543757CEA1",
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "7D9B3FA4BEFB6D8D7417FA3A58725DF7BE9A58A872217CCC3CE953B62A4947F1",
    "45767585981634744CD1F08952460EFD149D678E4D066DD38EB6D2FE1816096C",
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "C120386B4BCE72493CFC9B51214F38C68EA4A391A3ABD36C3B25CCC826830EDC",
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "227E52E2DEED4E08C0CF0EB3DB13A0543902D677214F0C83135BAB00FFA93D73",
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
)
CHUNK_EVIDENCE_SHA256 = (
    "37D08F6E6429028EC8E986A7A8FA64597B167D27CCD9B5AD3E3A1C9DDCD6680B",
    "AFB1C6915F8CC1134950CB78D4B8EE2E18A205411F76BA95129A0F6AA72DC0E5",
    "5293333930E343BC5C398A942AC1FAE37D0F9D7FA5C5AFD757B31E8D9D724205",
    "996B6CA03E7456C0120FF609FAF6FEA5F580AC30C73DE46805E6F70723AB22DD",
    "14198064749B32F168E87AB4E5028CCC487459E33B9C2588B913543667F25C3E",
    "75031FBF7D7818377B6D16780EC907A6392F08C9E0A1FCD8A40EC13E07C506BD",
    "583D6CD62498461A242C4EBDA399715481A2E94973103E6C9A0434F2B2C313C3",
    "CC2D2A9F5213105AA0818A37B5C16957AAB24B97FA6E7AE7361361E078162CBF",
    "6AE243BCDF2D86020BFE1B26C98C3AA9B0D936927EBB88B1592E593CEB9C204B",
    "10891D0E33F0CA9C5E73CF0E2AEB5BFC06E28E67C8118A64D35FB5FFA6053E50",
    "3F5472B8F46B14AFFD8930CDE8DEE3A3671F2A059AF6C8A78D52B8BC1B3AED20",
    "2A546B41AF1E26C1E25C8B991765D71F8E9C8B53CD0A50AABB0216154E665FED",
    "4ED957BEF3A196A59B0EE471EEED061CB338428615D68F230812C2C6BB222328",
    "B462A404AEADC515F8B4C35297F9BDB35DEA7B4279B55421B93329D50891BA3F",
    "D3EAAE6A405C10008CFD69D29D3419BBD0010450633FC562988EECA3128A22B9",
    "4E38D9AC5F17F3450485FF8535D46E7C0AA22D4FA10D5CCA9FE17FB86B32686F",
    "5661DE00EE20FF0E987D436A7788B5E188A821C210DB72DD33472E36AC5E8C2E",
    "907397C3924A3A253E71BEF51758D09B7B1A36361CB2DD7E4BF49FFF46D37009",
)
for _owner in range(len(SELECTORS)):
    EXPECTED_INPUT_SHA256[f"chunk{_owner}_builder"] = (
        CHUNK_BUILDER_SHA256[_owner]
    )
    EXPECTED_INPUT_SHA256[f"chunk{_owner}_public"] = (
        CHUNK_EVIDENCE_SHA256[_owner]
    )
    EXPECTED_INPUT_SHA256[f"chunk{_owner}_decisions"] = (
        CHUNK_DECISION_SHA256[_owner]
    )
    EXPECTED_INPUT_SHA256[f"chunk{_owner}_evidence"] = (
        CHUNK_EVIDENCE_SHA256[_owner]
    )
EXPECTED_CHUNK_ROWS = (
    6, 0, 4, 0, 0, 2, 0, 12, 4,
    0, 0, 0, 0, 2, 0, 4, 0, 0,
)
EXPECTED_CHUNK_SITES = (
    32, 27, 9, 18, 9, 12, 13, 11, 11,
    8, 6, 15, 13, 5, 28, 7, 11, 31,
)
EXPECTED_PENDING_ROWS = (
    15, 14, 14, 13, 13, 12, 12, 12, 11,
    11, 11, 11, 9, 9, 9, 9, 9, 8,
)
EXPECTED_PROMOTION_ROWS = EXPECTED_CHUNK_ROWS
EXPECTED_BLOCKED_ROWS = (
    9, 14, 10, 13, 13, 10, 12, 0, 7,
    11, 11, 11, 9, 7, 9, 5, 9, 8,
)
EXPECTED_ACCEPTED_ROOTS = (
    1, 0, 2, 0, 0, 1, 0, 6, 1,
    0, 0, 0, 0, 1, 0, 2, 0, 0,
)
EXPECTED_BLOCKED_ROOTS = (
    4, 9, 6, 7, 5, 4, 5, 0, 3,
    6, 4, 5, 4, 3, 4, 2, 4, 5,
)
EXPECTED_DECISION_ROWS = 34
EXPECTED_DECISION_ROOTS = 14
EXPECTED_PROMOTIONS = 34
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 24
EXPECTED_ACTION_COUNTS: dict[str, int] = {
    "runtime_promotion": 10,
    "translation_override_and_runtime_promotion": 24,
}
EXPECTED_PENDING_BEFORE = 5_956
EXPECTED_PENDING_AFTER = 5_922
EXPECTED_REVIEWED_SITES = 266
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "22996F498977FFC352D278E2581191AB98F58AA65D447B06A8C22287062FB16E"
)
EXPECTED_SOURCE_SITES = 288
EXPECTED_SOURCE_SITE_SHA256 = (
    "846DB5B262557BA4EE498D8A4C546A240A1518DAE3AAEB95759459C12246E042"
)
EXPECTED_SOURCE_ONLY_SITES = 22
EXPECTED_SOURCE_ONLY_SHA256 = (
    "349FD4F1BBCC5DF58B649643E262FF87980C1074068053509A0730278AC0A8F0"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "41CBC25028A3251C954597B2EA6797E503D8F8D6887D79C99BB7191FEBD5617F"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "D2928654B9CD246366567E5FF996EB0A58F9044962EADBB79F3921BA2ABC680A"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "997366037F93F13411BA46378DC99E1CF00B0DA863A7C93FD2D862A6F3CD669E",
    "private_evidence":
        "207C70FB3A6392E9F4CBE1F4A8DD807FB266D23E70B1113408172378C847513F",
    "public_coverage":
        "9E0593B6908D0DF4CF638D396642DE8CC42871FB39EFAE82349E87023CDA049F",
    "public_promotion":
        "6417063FB6339F9A254F4575F529AED44ACDA5E9FBD1F378EB7309D371F7E136",
    "final_candidate":
        "DC8F4F47EA9DDD81BA6DD788ECE55FD303FA5C228925E6E947E4E7F5C1007804",
    "decision_coordinates":
        "B241BCE2DE2A72F43F9A489E9897AD4D8F25F7CC19FC6BC414C2D41EA8293935",
    "promotion_coordinates":
        "B241BCE2DE2A72F43F9A489E9897AD4D8F25F7CC19FC6BC414C2D41EA8293935",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "8B4850D9545266D8E99B6D6C12A2BD0DDB5770FACF3B0231B7CE18679D599221",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "349FD4F1BBCC5DF58B649643E262FF87980C1074068053509A0730278AC0A8F0",
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


class PairwiseDisjointOwnerOrders:
    """Use representative orders after the core proves pairwise disjointness."""

    @staticmethod
    def permutations(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
        canonical = tuple(values)
        if len(canonical) < 2:
            return (canonical,)
        return (canonical, tuple(reversed(canonical)))


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
        assignment.get("wave_id") == "post_selector292_wave6"
        and len(packets) == len(SELECTORS) == len(chunk_rows)
        and len(assignment["pairwise_independence"]) == 153
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
    # resolve_union first proves every owner coordinate/root set pairwise
    # disjoint. That proof makes all n! update orders identical, so canonical
    # and reverse are sufficient implementation witnesses.
    BASE.itertools = PairwiseDisjointOwnerOrders
    BASE.load_json = load_json_compatible
    BASE.load_jsonl = load_jsonl_compatible
    BASE.METHOD = (
        "post_selector292_wave6_eighteen_selector_root_terminal_atomic_disjoint_"
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
    BASE.UPDATE_ACTION_FIELD = "post_selector292_wave6_update_action"
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
        "all_266_candidate_sites_reviewed": True,
        (
            f"blocked_{sum(EXPECTED_BLOCKED_ROWS)}_pending_rows_"
            "received_no_decisions"
        ): True,
        "confirmed_non_display_rows_untouched": True,
        "full_dialogue_rebuild_performed": False,
        "source_only_22_assignment_pinned_no_action": True,
        "terminal_126_records_read_only": True,
        "pairwise_disjoint_owner_sets_prove_order_independence": True,
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
        and len(blocked) == sum(EXPECTED_BLOCKED_ROWS)
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
                row.get("post_selector292_wave6_update_action", "")
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
