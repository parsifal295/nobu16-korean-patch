#!/usr/bin/env python3
"""Consolidate selector-568 chunks 0..2 on the current 81B4 ledger.

The standalone chunks share 261 renewal coordinates.  This builder freezes
their inputs, assigns every exact translation override one owner, keeps the
current official translation otherwise, and jointly replays all accepted
caller assemblies.  Dialogue-bearing decisions and the two selector-1096 /
selector-568 sequential-call proofs stay below ``tmp``.
"""

from __future__ import annotations

import argparse
import copy
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
DIALOGUE_WORKSTREAM = REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
UTILITY_PATH = WORKSTREAM / "build_pk_selector538_family_consolidated_closure_v1.py"
CHUNK_BUILDER_PATHS = tuple(
    WORKSTREAM / f"build_pk_selector568_chunk{chunk}_closure_v1.py"
    for chunk in range(3)
)
OFFICIAL_PRIVATE_PATH = DIALOGUE_TMP / "runtime_vm_integrated.private.v1.jsonl"
OFFICIAL_PUBLIC_PATH = DIALOGUE_WORKSTREAM / "runtime_vm_integration.source_free.v1.json"
SELECTOR538_DECISION_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector538_family_consolidated_closure_decisions.private.v1.jsonl"
)
SELECTOR538_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector538_family_consolidated_closure_evidence.private.v1.jsonl"
)
GHIDRA_CONTRACT_PATH = WORKSTREAM / "ghidra_pk_vm_contract.v1.json"

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector568_family_consolidated_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector568_family_consolidated_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector568_family_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector568_family_consolidated_closure_evidence.private.v1.jsonl"
)
DEFAULT_CROSS_OUTPUT = (
    DIALOGUE_TMP / "selector568_cross1096_family_consolidated.private.v1.json"
)

AUDIT_SCHEMA = "nobu16.kr.pk-selector568-family-consolidated-closure-coverage.v1"
PROMOTION_SCHEMA = "nobu16.kr.pk-selector568-family-consolidated-closure-promotion.v1"
EVIDENCE_SCHEMA = "nobu16.kr.pk-selector568-family-consolidated-closure-evidence-row.v1"
OVERRIDE_SCHEMA = "nobu16.kr.pk-selector568-family-consolidated-exact-override.v1"
CROSS_SCHEMA = "nobu16.kr.pk-selector568-cross1096-family-consolidated.private.v1"
METHOD = "reversed_vm_pk_selector568_chunks_0_2_current81b4_consolidated"
UPDATE_ACTION_FIELD = "selector568_family_update_action"
OVERRIDE_FIELD = "selector568_family_exact_override_evidence"
SELECTOR = 568

EXPECTED_OFFICIAL_PRIVATE_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_OFFICIAL_PUBLIC_SHA256 = (
    "46270F70A019484EFB1F99851D436467C8FD2DE32EB222BDC048DA1B5BC080FA"
)
EXPECTED_SELECTOR538_DECISION_SHA256 = (
    "5640EB7FB7E4EA9B32309B7FA280637DA9F26F96CA500BCD4FA9847D997456C0"
)
EXPECTED_SELECTOR538_EVIDENCE_SHA256 = (
    "910C0A59823C2B6B083F58257D6203053738EFEFC2E49E6271D553FF44CAB940"
)
EXPECTED_GHIDRA_CONTRACT_SHA256 = (
    "21DAF83330F278484BFB2462188804947A6C457F4B072DA80D7ADFBD3D13F461"
)
EXPECTED_ROWS = 52_803
EXPECTED_OFFICIAL_PENDING = 7_896
EXPECTED_PENDING_AFTER = 7_671
EXPECTED_DECISION_ROWS = 503
EXPECTED_PROMOTION_ROWS = 242
EXPECTED_ACTUAL_PROMOTION_ROWS = 225
EXPECTED_SUPERSEDED_PROMOTION_ROWS = 17
EXPECTED_RENEWAL_ROWS = 261
EXPECTED_OVERRIDE_ROWS = 156
EXPECTED_ACCEPTED_ASSEMBLIES = 1_183
EXPECTED_SELECTOR538_SUPERSESSION_ROWS = 36
EXPECTED_SELECTOR538_PROMOTION_SUPERSESSION_ROWS = 17
EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_ROWS = 19
EXPECTED_CHUNK_DECISION_ROWS = (353, 361, 311)
EXPECTED_CHUNK_PROMOTION_ROWS = (92, 100, 50)
EXPECTED_CHUNK_OVERRIDE_ROWS = (59, 46, 51)
EXPECTED_CHUNK_ACCEPTED_ASSEMBLIES = (434, 329, 420)
EXPECTED_CHUNK_AUDIT_SHA256 = (
    "3302BB2766462FC1A304CD23C1188A1C40D01C7DD3A2396EAB92492A81D73365",
    "DE5053AF4C11EFB2987BA139376789ED8B694E4B3323EF65E521966765A612A9",
    "15E5D3F4606A6C08A0F48FC481B7AF78686205DAC6DDAEA2E43C0234D395880D",
)
EXPECTED_CHUNK_PROMOTION_SHA256 = (
    "E0D783536EEE92A600CF73E59C34B3E426A3C3864F5F828C8277F600A85E1835",
    "C5A5F2B8B9EAEE8F14E02C66B02EE1B44F9F776BE7153AF49F02A0D5166163E5",
    "52D6B7B482A02699956D65A015A12BD750F33958B6CD58B1601F3856404107C2",
)
EXPECTED_CHUNK_DECISION_SHA256 = (
    "0196222A0460783741CA8F75B88208F30556B80B5B2C76DFDCBC39D099F3801E",
    "B35247D0B6BBC3F392394F9DF3051F8D66E82CDAF71BE1F3235F6260DD310501",
    "35CDC04F0C93247DFC406BB71AB87714E42619A9CDD22192782458220DD98FB9",
)
EXPECTED_CHUNK_EVIDENCE_SHA256 = (
    "C9499F989A0D9AC1DCD1BFF705771AD6D87F02CE038E92B0F7EF78FD28298856",
    "764BCC8A0E10D1B5FC560917260C2C3027BA79DC94F9D5CBB3994906FC7BD58D",
    "E65EA5FAAAA9524555F1D14267CD1716404CEF6E7CA69833DB31A496CFE8387A",
)
EXPECTED_CHUNK_DECISION_COORDINATE_SHA256 = (
    "CB94D51D3522071B9C9BEE37028B584C9EF34EC99AB8E96E01FCACD3A6B8ABAF",
    "A9435F74580D74A63DE4BA185FF2998597FB0629C421746A5DE91CC319AAFFEF",
    "777B7A43F11BEC0494430679FD2F0DA5C2450CE136D2988399514D7086BD891C",
)
EXPECTED_PAIRWISE_TRANSLATION_DIFF_ROWS = (59, 79, 50)
EXPECTED_PAIRWISE_TRANSLATION_DIFF_SHA256 = (
    "3306F2272644A66CDE377592D7CA73324DFD7C3F4E76BC14A02C4278133E194B",
    "A73B818368226E951F6D173122ED2F0010F72CEFD3441DA2333DB7E944B48161",
    "5C7EE86D8733A48F7F9A35109747B5EDAF774B1DDD7DAC829AF036926203BFB6",
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "4827FEA5E4E2FC7E9448CE7635A2A8487A72CAEBE3A2F863422FD586C4C093CD"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "3202ECEF12B3302FDBF8D189162A47A228453B80F3903F66EA4E7BEE8C12FCEF"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "B9020FDF90392ACD95869EA9553FB77286A6B7E373403443DB5444D10116DE6C"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "284FF03D067BD5D3AE60427DF66B05B4B35EC63C5581A093761928859755A6AC"
)
EXPECTED_ACTUAL_PROMOTION_COORDINATE_SHA256 = (
    "D195EACD60A3F1583D8936AC4CA009069CC2BB9CE92E4708705B28221F5FC09E"
)
EXPECTED_SUPERSEDED_PROMOTION_COORDINATE_SHA256 = (
    "6582123A978134EC5E714F722E7476B06B8609687497E7BCB5D2D578C6D41E5E"
)
EXPECTED_OVERRIDE_MAP_SHA256 = (
    "234009C02F915124EC113A29624040C38D4B9AA683D60BF66FE6CCF529A75336"
)
EXPECTED_OVERRIDE_OWNER_MAP_SHA256 = (
    "767B21B65A0F8B0B21A76C8576216288CFB3EA0FAC39EFD85B2A9F4DB856AFFB"
)
EXPECTED_SELECTOR538_SUPERSESSION_COORDINATE_SHA256 = (
    "1962FEE3F341F4DE85FBA93300F7A476A6D9D5FF179E50A701C8A0A83576ED46"
)
EXPECTED_EXTERNAL1096_COORDINATE_SHA256 = (
    "6DC7963E2A1AAB3838D5E0092449B4D6D327C1578FB4A63767FA91984CE5DE4E"
)
EXPECTED_SELECTOR568_CROSS_COORDINATE_SHA256 = (
    "EDB70BCB62D0BF716B17A8DFCD46079B58F116A2579F8D79DB1F91920F8F68B7"
)
EXPECTED_ACTION_COUNTS = {
    "evidence_supersession": 13,
    "runtime_promotion": 163,
    "translation_override_and_evidence_supersession": 4,
    "translation_override_and_runtime_promotion": 62,
    "translation_override_and_verification_renewal": 90,
    "verification_renewal": 171,
}
EXPECTED_ACTION_COORDINATE_SHA256 = {
    "evidence_supersession":
        "EFE72BEEC001C33BA7B7575C0942A13AE7D52132D06B7C6574D24EEEAED30ED7",
    "runtime_promotion":
        "D2619B78771E0F0BC57205118F1F1B1EB57C239F470D166F993C82A0FE25B80A",
    "translation_override_and_evidence_supersession":
        "52A2E2A8B4586F9B51F6E4F70387B7ED5A2A57B228F7A63A7A091103AEF56F49",
    "translation_override_and_runtime_promotion":
        "95A0E0B4B9FEDFB7F1B8F9D7F519F87D3CCF5C751C3E26AEB28BAEA13386317E",
    "translation_override_and_verification_renewal":
        "9EC69FB4E7567A40898CA48C25A4ACA3C337118BF58277C987BAB05CF2E227D0",
    "verification_renewal":
        "0D2F4026BEB61500BBBED230D7A365D335FF137CCD9CB50BC9F19CA963331280",
}
EXPECTED_DISPATCH_SHAPE_SHA256 = {
    "root": "82A12356B7B6FC6167B3EE0905DDACF3E40CCF55B24908535D64F18B289093D6",
    "binary_terminal": "AAEDDC8790E9C3B66229F0DC154F4A94D6B42A19EEE3773D4DE4000F531AB6D3",
    "personality_cascade": "DF501F4F946688362160BFD77E9DBDC98C204933059ACDD5B5F9E561C492059C",
}

# Frozen after the first independent write/check cycle.
EXPECTED_OFFICIAL_CANDIDATE_SHA256: str | None = (
    "DCB19B0D85422F7C0EA5888F9A0C47667D75A88D100BABAE11DDAF4A8DD2000E"
)
EXPECTED_FAMILY_CANDIDATE_SHA256: str | None = (
    "12D3625EA4312B0B1E4BC2F649C4DE30860C60C23BBC6ED53988590773B69C46"
)
EXPECTED_ACCEPTED_ASSEMBLY_SHA256: str | None = (
    "C76C02B66F69CB14A36E9D39AB19E152E72A1E974E634F73772A777589B42897"
)
EXPECTED_CROSS_PRIVATE_SHA256: str | None = (
    "8D9692005821153180CAE18755BE835951988AF0BBD48AAA21EDC3AA94855EB8"
)
EXPECTED_CROSS_BRANCH_SHA256: str | None = (
    "EDF9A28E404C3293634B2EAD8A9F430ABDE6594BAC5383F4BB0132CD0A32662E"
)
EXPECTED_AUDIT_OUTPUT_SHA256: str | None = (
    "2855D1EB21BE4ACF0C62B0AC86613F006D5E6AD163863AB3B0315A27E5821D96"
)
EXPECTED_PROMOTION_OUTPUT_SHA256: str | None = (
    "4646EFA2D32D582BA3A43C85144156E058A30619861390C19E09998B23533300"
)
EXPECTED_DECISION_OUTPUT_SHA256: str | None = (
    "500A3E36AA434819D75917E35AD60D8576C1B8CE8B2E4F408DDBAF2E2D800CCE"
)
EXPECTED_EVIDENCE_OUTPUT_SHA256: str | None = (
    "954B8FF81D8B11233DBF38B8E3B5B6C771F9B94C13A9F913D38C17546FC55CDF"
)


class FamilyError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FamilyError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


UTIL = load_module(UTILITY_PATH, "pk_selector568_family_util_v1")
sha256_bytes = UTIL.sha256_bytes
sha256_file = UTIL.sha256_file
sha256_text = UTIL.sha256_text
canonical_sha256 = UTIL.canonical_sha256
canonical_json = UTIL.canonical_json
canonical_jsonl = UTIL.canonical_jsonl
parse_coordinate = UTIL.parse_coordinate
coordinate_digest = UTIL.coordinate_digest
row_sort_key = UTIL.row_sort_key
load_json = UTIL.load_json
load_jsonl = UTIL.load_jsonl
seal_report = UTIL.seal_report
assert_source_free_report = UTIL.assert_source_free_report


def load_official() -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    require(
        sha256_file(OFFICIAL_PRIVATE_PATH) == EXPECTED_OFFICIAL_PRIVATE_SHA256,
        "official 81B4 ledger drifted",
    )
    require(
        sha256_file(OFFICIAL_PUBLIC_PATH) == EXPECTED_OFFICIAL_PUBLIC_SHA256,
        "official source-free progress report drifted",
    )
    rows = load_jsonl(OFFICIAL_PRIVATE_PATH)
    index = {(str(row["resource"]), str(row["coordinate"])): row for row in rows}
    public = load_json(OFFICIAL_PUBLIC_PATH)
    require(
        len(rows) == len(index) == EXPECTED_ROWS
        and sum(row.get("runtime_review") == "pending" for row in rows)
        == EXPECTED_OFFICIAL_PENDING
        and public["result"]["runtime_review_pending"] == EXPECTED_OFFICIAL_PENDING
        and public["result"]["private_integrated_decision_sha256"]
        == EXPECTED_OFFICIAL_PRIVATE_SHA256,
        "official 81B4 universe/count drifted",
    )
    return rows, index


def load_selector538_supersession() -> dict[str, dict[str, Any]]:
    require(
        sha256_file(SELECTOR538_DECISION_PATH)
        == EXPECTED_SELECTOR538_DECISION_SHA256
        and sha256_file(SELECTOR538_EVIDENCE_PATH)
        == EXPECTED_SELECTOR538_EVIDENCE_SHA256,
        "selector538 family evidence drifted",
    )
    decisions = {str(row["coordinate"]): row for row in load_jsonl(SELECTOR538_DECISION_PATH)}
    evidence = {str(row["coordinate"]): row for row in load_jsonl(SELECTOR538_EVIDENCE_PATH)}
    require(set(decisions) == set(evidence), "selector538 decision/evidence universe drifted")
    return evidence


def load_chunks() -> dict[str, Any]:
    chunks: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    for chunk_id, builder_path in enumerate(CHUNK_BUILDER_PATHS):
        module = load_module(builder_path, f"pk_selector568_family_chunk{chunk_id}")
        paths = (
            Path(module.DEFAULT_AUDIT_OUTPUT),
            Path(module.DEFAULT_PROMOTION_OUTPUT),
            Path(module.DEFAULT_DECISION_OUTPUT),
            Path(module.DEFAULT_EVIDENCE_OUTPUT),
        )
        expected = (
            EXPECTED_CHUNK_AUDIT_SHA256[chunk_id],
            EXPECTED_CHUNK_PROMOTION_SHA256[chunk_id],
            EXPECTED_CHUNK_DECISION_SHA256[chunk_id],
            EXPECTED_CHUNK_EVIDENCE_SHA256[chunk_id],
        )
        for kind, path, digest in zip(
            ("audit", "promotion", "decision", "evidence"), paths, expected
        ):
            require(sha256_file(path) == digest, f"chunk{chunk_id} {kind} drifted")
            artifacts.append({"chunk": chunk_id, "kind": kind, "sha256": digest})
        audit = load_json(paths[0])
        promotion = load_json(paths[1])
        assert_source_free_report(audit)
        assert_source_free_report(promotion)
        decision_rows = load_jsonl(paths[2])
        evidence_rows = load_jsonl(paths[3])
        decisions = {str(row["coordinate"]): row for row in decision_rows}
        evidence = {str(row["coordinate"]): row for row in evidence_rows}
        action_field = str(module.UPDATE_ACTION_FIELD)
        promotions = {
            coordinate
            for coordinate, row in decisions.items()
            if "runtime_promotion" in str(row[action_field])
            or "evidence_supersession" in str(row[action_field])
        }
        renewals = {
            coordinate
            for coordinate, row in decisions.items()
            if "verification_renewal" in str(row[action_field])
        }
        overrides = {
            coordinate
            for coordinate, row in decisions.items()
            if "translation_override" in str(row[action_field])
        }
        require(
            len(decisions) == len(decision_rows) == EXPECTED_CHUNK_DECISION_ROWS[chunk_id]
            and set(decisions) == set(evidence)
            and coordinate_digest(decisions)
            == EXPECTED_CHUNK_DECISION_COORDINATE_SHA256[chunk_id]
            and len(promotions) == EXPECTED_CHUNK_PROMOTION_ROWS[chunk_id]
            and len(renewals) == EXPECTED_RENEWAL_ROWS
            and len(overrides) == EXPECTED_CHUNK_OVERRIDE_ROWS[chunk_id]
            and promotions | renewals == set(decisions)
            and not promotions & renewals,
            f"chunk{chunk_id} action universe drifted",
        )
        for coordinate, row in decisions.items():
            require(
                row.get("runtime_vm_verification") == evidence[coordinate],
                f"chunk{chunk_id} evidence binding drifted: {coordinate}",
            )
        handoff, review_public, world, validated = module.load_review()
        accepted_manifest = [
            branch for branch in validated["assembly_manifest"] if branch[3] != "reject"
        ]
        require(
            len(accepted_manifest) == EXPECTED_CHUNK_ACCEPTED_ASSEMBLIES[chunk_id]
            and review_public["proof"]["all_accepted_register_branches_proven"] is True
            and review_public["proof"][
                "all_accepted_current_relative_raw_g1n_nonexpanding"
            ]
            is True
            and int(audit["proof"]["accepted_assembly_rows"])
            == EXPECTED_CHUNK_ACCEPTED_ASSEMBLIES[chunk_id],
            f"chunk{chunk_id} accepted assembly proof drifted",
        )
        chunks.append(
            {
                "audit": audit,
                "decisions": decisions,
                "evidence": evidence,
                "handoff": handoff,
                "module": module,
                "overrides": overrides,
                "promotions": promotions,
                "renewals": renewals,
                "validated": validated,
                "world": world,
            }
        )
    return {"artifacts": artifacts, "chunks": chunks}


def analyze_family(
    chunks: Sequence[Mapping[str, Any]],
    official: Mapping[tuple[str, str], Mapping[str, Any]],
    selector538_evidence: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    decision_sets = [set(chunk["decisions"]) for chunk in chunks]
    promotion_sets = [set(chunk["promotions"]) for chunk in chunks]
    renewal_sets = [set(chunk["renewals"]) for chunk in chunks]
    override_sets = [set(chunk["overrides"]) for chunk in chunks]
    pairwise = []
    pair_id = 0
    for left in range(3):
        for right in range(left + 1, 3):
            overlap = decision_sets[left] & decision_sets[right]
            promotion_overlap = promotion_sets[left] & promotion_sets[right]
            override_overlap = override_sets[left] & override_sets[right]
            translation_diff = {
                coordinate
                for coordinate in overlap
                if chunks[left]["decisions"][coordinate]["translation"]
                != chunks[right]["decisions"][coordinate]["translation"]
            }
            require(
                len(overlap) == EXPECTED_RENEWAL_ROWS
                and overlap == renewal_sets[left] == renewal_sets[right]
                and not promotion_overlap
                and not override_overlap
                and len(translation_diff)
                == EXPECTED_PAIRWISE_TRANSLATION_DIFF_ROWS[pair_id]
                and coordinate_digest(translation_diff)
                == EXPECTED_PAIRWISE_TRANSLATION_DIFF_SHA256[pair_id],
                f"chunk{left}/{right} overlap drifted",
            )
            pairwise.append(
                {
                    "decision_overlap_rows": len(overlap),
                    "decision_overlap_sha256": coordinate_digest(overlap),
                    "left_chunk": left,
                    "override_overlap_rows": 0,
                    "override_overlap_sha256": coordinate_digest(override_overlap),
                    "promotion_overlap_rows": 0,
                    "promotion_overlap_sha256": coordinate_digest(promotion_overlap),
                    "right_chunk": right,
                    "translation_difference_rows": len(translation_diff),
                    "translation_difference_sha256": coordinate_digest(translation_diff),
                }
            )
            pair_id += 1
    decisions = set().union(*decision_sets)
    promotions = set().union(*promotion_sets)
    renewals = set(renewal_sets[0])
    overrides = set().union(*override_sets)
    require(
        len(decisions) == EXPECTED_DECISION_ROWS
        and len(promotions) == EXPECTED_PROMOTION_ROWS
        and len(renewals) == EXPECTED_RENEWAL_ROWS
        and len(overrides) == EXPECTED_OVERRIDE_ROWS
        and decisions == promotions | renewals
        and not promotions & renewals
        and coordinate_digest(decisions) == EXPECTED_DECISION_COORDINATE_SHA256
        and coordinate_digest(promotions) == EXPECTED_PROMOTION_COORDINATE_SHA256
        and coordinate_digest(renewals) == EXPECTED_RENEWAL_COORDINATE_SHA256
        and coordinate_digest(overrides) == EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "selector568 family union drifted",
    )
    override_owner: dict[str, int] = {}
    override_map: dict[str, str] = {}
    promotion_owner: dict[str, int] = {}
    for chunk_id, chunk in enumerate(chunks):
        for coordinate in chunk["promotions"]:
            require(coordinate not in promotion_owner, f"duplicate promotion owner: {coordinate}")
            promotion_owner[coordinate] = chunk_id
        for coordinate in chunk["overrides"]:
            require(coordinate not in override_owner, f"duplicate override owner: {coordinate}")
            override_owner[coordinate] = chunk_id
            override_map[coordinate] = str(chunk["decisions"][coordinate]["translation"])
    ordered_override_map = dict(
        sorted(override_map.items(), key=lambda item: parse_coordinate(item[0]))
    )
    ordered_owner_map = dict(
        sorted(override_owner.items(), key=lambda item: parse_coordinate(item[0]))
    )
    require(
        canonical_sha256(ordered_override_map) == EXPECTED_OVERRIDE_MAP_SHA256
        and canonical_sha256(ordered_owner_map) == EXPECTED_OVERRIDE_OWNER_MAP_SHA256,
        "selector568 exact override owner/map drifted",
    )
    actual_promotions = {
        coordinate
        for coordinate in promotions
        if official[("pk_msggame", coordinate)]["runtime_review"] == "pending"
    }
    superseded_promotions = promotions - actual_promotions
    require(
        len(actual_promotions) == EXPECTED_ACTUAL_PROMOTION_ROWS
        and coordinate_digest(actual_promotions)
        == EXPECTED_ACTUAL_PROMOTION_COORDINATE_SHA256
        and len(superseded_promotions) == EXPECTED_SUPERSEDED_PROMOTION_ROWS
        and coordinate_digest(superseded_promotions)
        == EXPECTED_SUPERSEDED_PROMOTION_COORDINATE_SHA256,
        "selector568 current81b4 promotion rebase drifted",
    )
    action_by_coordinate = {}
    for coordinate in decisions:
        if coordinate in actual_promotions:
            action = (
                "translation_override_and_runtime_promotion"
                if coordinate in overrides
                else "runtime_promotion"
            )
        elif coordinate in superseded_promotions:
            action = (
                "translation_override_and_evidence_supersession"
                if coordinate in overrides
                else "evidence_supersession"
            )
        else:
            action = (
                "translation_override_and_verification_renewal"
                if coordinate in overrides
                else "verification_renewal"
            )
        action_by_coordinate[coordinate] = action
    require(
        dict(Counter(action_by_coordinate.values())) == EXPECTED_ACTION_COUNTS,
        "selector568 current81b4 action partition drifted",
    )
    for action, digest in EXPECTED_ACTION_COORDINATE_SHA256.items():
        require(
            coordinate_digest(
                coordinate
                for coordinate, value in action_by_coordinate.items()
                if value == action
            )
            == digest,
            f"selector568 action digest drifted: {action}",
        )
    selector538_overlap = decisions & set(selector538_evidence)
    require(
        len(selector538_overlap) == EXPECTED_SELECTOR538_SUPERSESSION_ROWS
        and len(selector538_overlap & promotions)
        == EXPECTED_SELECTOR538_PROMOTION_SUPERSESSION_ROWS
        and len(selector538_overlap & renewals)
        == EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_ROWS
        and coordinate_digest(selector538_overlap)
        == EXPECTED_SELECTOR538_SUPERSESSION_COORDINATE_SHA256
        and all(
            official[("pk_msggame", coordinate)].get("runtime_vm_verification")
            == selector538_evidence[coordinate]
            for coordinate in selector538_overlap
        ),
        "selector538 family supersession binding drifted",
    )
    external1096 = {"6:4197:0", "15:1863:1"}
    selector568_cross = {"6:4197:1", "15:1863:2"}
    require(
        coordinate_digest(external1096) == EXPECTED_EXTERNAL1096_COORDINATE_SHA256
        and coordinate_digest(selector568_cross)
        == EXPECTED_SELECTOR568_CROSS_COORDINATE_SHA256
        and external1096 <= renewals
        and not external1096 & overrides
        and selector568_cross <= overrides,
        "cross-family coordinate ownership drifted",
    )
    return {
        "action_by_coordinate": action_by_coordinate,
        "actual_promotions": actual_promotions,
        "decisions": decisions,
        "external1096": external1096,
        "override_map": override_map,
        "override_owner": override_owner,
        "overrides": overrides,
        "pairwise": pairwise,
        "promotion_owner": promotion_owner,
        "promotions": promotions,
        "renewals": renewals,
        "selector538_overlap": selector538_overlap,
        "selector568_cross": selector568_cross,
        "superseded_promotions": superseded_promotions,
    }


def rebuild_candidates(
    official_rows: Sequence[Mapping[str, Any]],
    chunks: Sequence[Mapping[str, Any]],
    family: Mapping[str, Any],
) -> dict[str, Any]:
    base_audit = chunks[0]["module"].BASE_AUDIT
    replacements = {
        base_audit.parse_literal_coordinate(str(row["coordinate"])):
            str(row["translation"])
        for row in official_rows
        if row.get("resource") == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    original = base_audit.DEFAULT_PK_CURRENT.read_bytes()
    official_blob = base_audit.rebuild_packed_with_literals(original, replacements)
    replacements.update(
        {
            parse_coordinate(coordinate): translation
            for coordinate, translation in family["override_map"].items()
        }
    )
    family_blob = base_audit.rebuild_packed_with_literals(original, replacements)
    official_sha = sha256_bytes(official_blob)
    family_sha = sha256_bytes(family_blob)
    if EXPECTED_OFFICIAL_CANDIDATE_SHA256 is not None:
        require(official_sha == EXPECTED_OFFICIAL_CANDIDATE_SHA256, "official candidate drifted")
    if EXPECTED_FAMILY_CANDIDATE_SHA256 is not None:
        require(family_sha == EXPECTED_FAMILY_CANDIDATE_SHA256, "family candidate drifted")
    records = base_audit.records_from_blob(family_blob)
    current_records = chunks[0]["world"]["current_records"]
    terminal_candidate = chunks[0]["module"].REVIEW.terminal_literals(records)
    terminal_current = chunks[0]["module"].REVIEW.terminal_literals(current_records)
    manifest = []
    for chunk_id, chunk in enumerate(chunks):
        review = chunk["module"].REVIEW
        for row in chunk["handoff"]["site_reviews"]:
            if row["decision"] == "reject":
                continue
            site = str(row["site"])
            reviewed_left, reviewed_right = review.adjacent_literals(records, site)
            current_left, current_right = review.adjacent_literals(current_records, site)
            require(
                reviewed_left == row["reviewed_left_translation"],
                f"family translation winner changed accepted caller: {site}",
            )
            for terminal in range(1951, 1958):
                reviewed = reviewed_left + terminal_candidate[terminal] + reviewed_right
                current = current_left + terminal_current[terminal] + current_right
                reviewed_lines = review.line_metrics(reviewed)
                current_lines = review.line_metrics(current)
                require(
                    len(reviewed_lines) == len(current_lines)
                    and review.current_relative_nonexpanding(reviewed_lines, current_lines),
                    f"family accepted assembly expansion: {site}/{terminal}",
                )
                manifest.append(
                    [
                        chunk_id,
                        site,
                        terminal,
                        sha256_bytes(reviewed.encode("utf-8")),
                        sha256_bytes(current.encode("utf-8")),
                        [line["raw_g1n_width_px"] for line in reviewed_lines],
                        [line["raw_g1n_width_px"] for line in current_lines],
                    ]
                )
    assembly_sha = canonical_sha256(manifest)
    require(len(manifest) == EXPECTED_ACCEPTED_ASSEMBLIES, "accepted assembly count drifted")
    if EXPECTED_ACCEPTED_ASSEMBLY_SHA256 is not None:
        require(assembly_sha == EXPECTED_ACCEPTED_ASSEMBLY_SHA256, "accepted assembly digest drifted")
    return {
        "accepted_assembly_manifest": manifest,
        "accepted_assembly_sha256": assembly_sha,
        "family_blob": family_blob,
        "family_records": records,
        "family_sha256": family_sha,
        "official_blob": official_blob,
        "official_sha256": official_sha,
    }


CALL_TARGET_RE = re.compile(b"\x01([\x43\x4A]).{4}", re.DOTALL)


def normalized_dispatch_bytes(data: bytes) -> bytes:
    return CALL_TARGET_RE.sub(
        lambda match: b"\x01" + match.group(1) + b"\x00\x00\x00\x00",
        data,
    )


def build_cross_proof(
    *,
    chunks: Sequence[Mapping[str, Any]],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        sha256_file(GHIDRA_CONTRACT_PATH) == EXPECTED_GHIDRA_CONTRACT_SHA256,
        "Ghidra VM contract drifted",
    )
    contract = load_json(GHIDRA_CONTRACT_PATH)
    require(
        contract["opcode_contract"]["0143"]["semantics"]
        == "push_return_address_then_call_record"
        and contract["opcode_contract"]["014A"]["semantics"] == "jump_to_record",
        "Ghidra static record dispatch contract drifted",
    )
    records = candidate["family_records"]
    current_records = chunks[0]["world"]["current_records"]
    base_audit = chunks[0]["module"].BASE_AUDIT
    review = chunks[0]["module"].REVIEW
    node_pairs = tuple(zip(range(568, 574), range(1096, 1102)))
    shape_classes = {
        568: "root",
        569: "binary_terminal",
        570: "personality_cascade",
        571: "personality_cascade",
        572: "binary_terminal",
        573: "binary_terminal",
    }
    node_manifest = []
    for selector568, selector1096 in node_pairs:
        left = normalized_dispatch_bytes(records[(0, selector568)].data)
        right = normalized_dispatch_bytes(records[(0, selector1096)].data)
        shape = shape_classes[selector568]
        digest = sha256_bytes(left)
        require(
            left == right and digest == EXPECTED_DISPATCH_SHAPE_SHA256[shape],
            f"selector dispatch shape correlation drifted: {selector568}/{selector1096}",
        )
        node_manifest.append(
            {
                "selector1096_record": selector1096,
                "selector568_record": selector568,
                "shape_class": shape,
                "zero_normalized_bytecode_sha256": digest,
            }
        )
    graph = review.CALLER.HONORIFIC.graph_edges(
        records, conservative_operand_scan=True
    )
    expected568 = {
        (568, 569), (568, 570), (568, 571), (569, 1951), (569, 1952),
        (570, 572), (570, 573), (571, 569), (571, 1957),
        (572, 1953), (572, 1954), (573, 1955), (573, 1956),
    }
    expected1096 = {
        (1096, 1097), (1096, 1098), (1096, 1099), (1097, 2581),
        (1097, 2582), (1098, 1100), (1098, 1101), (1099, 1097),
        (1099, 2587), (1100, 2583), (1100, 2584), (1101, 2585),
        (1101, 2586),
    }
    actual568 = {
        (source[1], target[1])
        for source in {(0, value) for value in range(568, 574)}
        for target in graph.get(source, set())
    }
    actual1096 = {
        (source[1], target[1])
        for source in {(0, value) for value in range(1096, 1102)}
        for target in graph.get(source, set())
    }
    mapped568 = {
        (
            source + 528,
            target + (630 if 1951 <= target <= 1957 else 528),
        )
        for source, target in actual568
    }
    require(
        actual568 == expected568
        and actual1096 == expected1096
        and mapped568 == actual1096,
        "selector568/1096 ordinal edge correlation drifted",
    )
    terminal1096_candidate = {
        terminal: base_audit.parse_record_literals(records[(0, terminal)])[0].text
        for terminal in range(2581, 2588)
    }
    terminal568_candidate = {
        terminal: base_audit.parse_record_literals(records[(0, terminal)])[0].text
        for terminal in range(1951, 1958)
    }
    terminal1096_current = {
        terminal: base_audit.parse_record_literals(current_records[(0, terminal)])[0].text
        for terminal in range(2581, 2588)
    }
    terminal568_current = {
        terminal: base_audit.parse_record_literals(current_records[(0, terminal)])[0].text
        for terminal in range(1951, 1958)
    }
    cross_specs = (
        {
            "candidate_external1096": "의 출진에 응",
            "external1096_coordinate": "6:4197:0",
            "root": (6, 4197),
            "selector568_coordinate": "6:4197:1",
        },
        {
            "candidate_external1096": "이(가)\n전황은 아군 우세로 판단",
            "external1096_coordinate": "15:1863:1",
            "root": (15, 1863),
            "selector568_coordinate": "15:1863:2",
        },
    )
    language_jp = chunks[0]["world"]["language_records"]["jp"]
    cross_records = []
    all_branches = []
    for spec in cross_specs:
        root = spec["root"]
        family_literals = base_audit.parse_record_literals(records[root])
        current_literals = base_audit.parse_record_literals(current_records[root])
        jp_literals = base_audit.parse_record_literals(language_jp[root])
        external_slot = parse_coordinate(spec["external1096_coordinate"])[2]
        selector568_slot = parse_coordinate(spec["selector568_coordinate"])[2]
        candidate_external = str(spec["candidate_external1096"])
        candidate568 = family_literals[selector568_slot].text
        current_external = current_literals[external_slot].text
        current568 = current_literals[selector568_slot].text
        branches = []
        for ordinal in range(7):
            terminal1096 = 2581 + ordinal
            terminal568 = 1951 + ordinal
            reviewed = (
                candidate_external
                + terminal1096_candidate[terminal1096]
                + candidate568
                + terminal568_candidate[terminal568]
            )
            current = (
                current_external
                + terminal1096_current[terminal1096]
                + current568
                + terminal568_current[terminal568]
            )
            reviewed_lines = review.line_metrics(reviewed)
            current_lines = review.line_metrics(current)
            line_deltas = [
                reviewed_line["raw_g1n_width_px"] - current_line["raw_g1n_width_px"]
                for reviewed_line, current_line in zip(reviewed_lines, current_lines)
            ]
            nonexpanding = (
                len(reviewed_lines) == len(current_lines)
                and review.current_relative_nonexpanding(reviewed_lines, current_lines)
            )
            require(nonexpanding, f"cross-family assembly expansion: {root}/{ordinal}")
            branch = {
                "current_assembly": current,
                "current_lines": current_lines,
                "current_relative_raw_g1n_nonexpanding": nonexpanding,
                "line_deltas_px": line_deltas,
                "ordinal": ordinal,
                "reviewed_assembly": reviewed,
                "reviewed_lines": reviewed_lines,
                "selector1096_terminal_coordinate": f"0:{terminal1096}:0",
                "selector568_terminal_coordinate": f"0:{terminal568}:0",
            }
            branches.append(branch)
            all_branches.append([f"{root[0]}:{root[1]}", branch])
        cross_records.append(
            {
                "branches": branches,
                "candidate_external1096": candidate_external,
                "candidate_selector568": candidate568,
                "external1096_coordinate": spec["external1096_coordinate"],
                "external1096_not_overridden_by_selector568_family": True,
                "jp_authority": {
                    "external1096": jp_literals[external_slot].text,
                    "selector568": jp_literals[selector568_slot].text,
                },
                "record_coordinate": f"{root[0]}:{root[1]}",
                "selector568_coordinate": spec["selector568_coordinate"],
            }
        )
    branch_sha = canonical_sha256(all_branches)
    if EXPECTED_CROSS_BRANCH_SHA256 is not None:
        require(branch_sha == EXPECTED_CROSS_BRANCH_SHA256, "cross branch proof drifted")
    value = {
        "branch_count": len(all_branches),
        "correlation_guard": {
            "ghidra_vm_contract_sha256": EXPECTED_GHIDRA_CONTRACT_SHA256,
            "node_pairs": node_manifest,
            "operand_normalization": "zero four-byte 0143/014A packed targets only",
            "ordinal_correlated_pairs_authoritative": True,
            "paired_edge_manifest_sha256": canonical_sha256(
                {
                    "selector1096": sorted(actual1096),
                    "selector568": sorted(actual568),
                }
            ),
            "selector_expression_bytecode_shapes_identical": True,
        },
        "cross_family_resolution_required": True,
        "privacy": {
            "classification": "private",
            "contains_dialogue_bodies": True,
            "public": False,
            "tracked": False,
        },
        "records": cross_records,
        "schema": CROSS_SCHEMA,
        "status": "PASS",
    }
    content = canonical_json(value)
    digest = sha256_bytes(content.encode("utf-8"))
    if EXPECTED_CROSS_PRIVATE_SHA256 is not None:
        require(digest == EXPECTED_CROSS_PRIVATE_SHA256, "cross private artifact drifted")
    return {
        "branch_sha256": branch_sha,
        "content": content,
        "file_sha256": digest,
        "value": value,
    }


def build_rows(
    *,
    official: Mapping[tuple[str, str], Mapping[str, Any]],
    chunks: Sequence[Mapping[str, Any]],
    family: Mapping[str, Any],
    selector538_evidence: Mapping[str, Mapping[str, Any]],
    audit_payload_sha256: str,
    candidate: Mapping[str, Any],
    cross: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    repair_hard_risks = chunks[0]["module"].BASE.CALLER.PREDECESSOR.repair_hard_risks
    rows = []
    evidence_rows = []
    for coordinate in sorted(family["decisions"], key=parse_coordinate):
        predecessor = official[("pk_msggame", coordinate)]
        override_owner = family["override_owner"].get(coordinate)
        promotion_owner = family["promotion_owner"].get(coordinate)
        translation = (
            family["override_map"][coordinate]
            if override_owner is not None
            else predecessor.get("translation")
        )
        require(isinstance(translation, str), f"missing translation: {coordinate}")
        evidence: dict[str, Any] = {
            "action": family["action_by_coordinate"][coordinate],
            "closure_binding": {
                "accepted_assembly_sha256": candidate["accepted_assembly_sha256"],
                "audit_report_payload_sha256": audit_payload_sha256,
                "cross_family_branch_sha256": cross["branch_sha256"],
                "decision_coordinate_sha256": EXPECTED_DECISION_COORDINATE_SHA256,
                "family_candidate_sha256": candidate["family_sha256"],
                "official_predecessor_sha256": EXPECTED_OFFICIAL_PRIVATE_SHA256,
                "override_coordinate_sha256": EXPECTED_OVERRIDE_COORDINATE_SHA256,
                "selector": SELECTOR,
            },
            "coordinate": coordinate,
            "current81b4_rebase": {
                "actual_runtime_promotion": coordinate in family["actual_promotions"],
                "evidence_supersession":
                    coordinate in family["superseded_promotions"],
                "official_runtime_review_before": predecessor["runtime_review"],
            },
            "method": METHOD,
            "per_row_game_playback_required": False,
            "predecessor_binding": {
                "checkpoint_sha256": EXPECTED_OFFICIAL_PRIVATE_SHA256,
                "row_sha256": canonical_sha256(predecessor),
            },
            "resource": "pk_msggame",
            "schema": EVIDENCE_SCHEMA,
            "status": "verified",
            "translation_utf16le_sha256": sha256_text(translation),
            "winner": {
                "decision_owner": (
                    f"chunk{override_owner}"
                    if override_owner is not None
                    else (
                        f"chunk{promotion_owner}"
                        if promotion_owner is not None
                        else "official81b4"
                    )
                ),
                "evidence_owner": (
                    f"chunk{override_owner}"
                    if override_owner is not None
                    else "official81b4"
                ),
                "exact_override_owner": (
                    f"chunk{override_owner}" if override_owner is not None else "none"
                ),
                "translation_owner": (
                    f"chunk{override_owner}" if override_owner is not None else "official81b4"
                ),
            },
        }
        if coordinate in family["selector538_overlap"]:
            prior = selector538_evidence[coordinate]
            evidence["selector538_family_evidence_supersession"] = {
                "decision_file_sha256": EXPECTED_SELECTOR538_DECISION_SHA256,
                "evidence_file_sha256": EXPECTED_SELECTOR538_EVIDENCE_SHA256,
                "prior_evidence_row_sha256": canonical_sha256(prior),
                "prior_runtime_vm_verification_exact_match": True,
            }
        if coordinate in family["external1096"] | family["selector568_cross"]:
            evidence["sequential_selector1096_selector568_resolution"] = {
                "branch_manifest_sha256": cross["branch_sha256"],
                "cross_private_file_sha256": cross["file_sha256"],
                "external1096_coordinate_not_overridden":
                    coordinate in family["external1096"],
                "ordinal_correlated_seven_pairs_nonexpanding": True,
                "selector568_owned_coordinate":
                    coordinate in family["selector568_cross"],
            }
        row = copy.deepcopy(dict(predecessor))
        row["runtime_review"] = "verified"
        row["semantic_review"] = "approved"
        row["translation"] = translation
        row[UPDATE_ACTION_FIELD] = family["action_by_coordinate"][coordinate]
        row["runtime_vm_verification"] = evidence
        if coordinate in family["actual_promotions"]:
            row["scope_classification"] = "retranslated"
            row["layout_review"] = "runtime_verified"
        if override_owner is not None:
            owner_row = chunks[override_owner]["decisions"][coordinate]
            repair_hard_risks(row)
            row["layout_review"] = owner_row["layout_review"]
            row[OVERRIDE_FIELD] = {
                "owner_chunk": override_owner,
                "owner_decision_sha256": canonical_sha256(owner_row),
                "schema": OVERRIDE_SCHEMA,
                "translation_utf16le_sha256": sha256_text(translation),
            }
            if "runtime_assembly_evidence" in owner_row:
                row["runtime_assembly_evidence"] = copy.deepcopy(
                    owner_row["runtime_assembly_evidence"]
                )
        rows.append(row)
        evidence_rows.append(evidence)
    require(
        Counter(str(row["action"]) for row in evidence_rows)
        == Counter(EXPECTED_ACTION_COUNTS),
        "emitted family action counts drifted",
    )
    return rows, evidence_rows


def build_outputs() -> dict[str, Any]:
    frozen = load_chunks()
    chunks = frozen["chunks"]
    steam_path = Path(chunks[0]["module"].LIVE_STEAM_PK)
    steam_before = sha256_file(steam_path)
    official_rows, official = load_official()
    selector538_evidence = load_selector538_supersession()
    family = analyze_family(chunks, official, selector538_evidence)
    candidate = rebuild_candidates(official_rows, chunks, family)
    cross = build_cross_proof(chunks=chunks, candidate=candidate)
    audit = seal_report(
        {
            "action_counts": EXPECTED_ACTION_COUNTS,
            "distribution_policy": {
                "private_cross_family_dialogue_stays_below_tmp": True,
                "private_decisions_stay_below_tmp": True,
                "tracked_report_contains_commercial_source_text": False,
                "tracked_report_contains_translated_dialogue_text": False,
                "tracked_report_contains_translation_map_keys": False,
            },
            "guards": {
                "chunk_artifact_manifest_sha256":
                    canonical_sha256(frozen["artifacts"]),
                "ghidra_vm_contract_sha256": EXPECTED_GHIDRA_CONTRACT_SHA256,
                "official_predecessor_private_sha256":
                    EXPECTED_OFFICIAL_PRIVATE_SHA256,
                "official_predecessor_public_sha256":
                    EXPECTED_OFFICIAL_PUBLIC_SHA256,
                "override_map_sha256": EXPECTED_OVERRIDE_MAP_SHA256,
                "selector538_evidence_sha256":
                    EXPECTED_SELECTOR538_EVIDENCE_SHA256,
                "steam_archive_sha256_after": steam_before,
                "steam_archive_sha256_before": steam_before,
            },
            "method": METHOD,
            "proof": {
                "accepted_assembly_rows": EXPECTED_ACCEPTED_ASSEMBLIES,
                "accepted_assembly_sha256": candidate["accepted_assembly_sha256"],
                "all_accepted_current_relative_raw_g1n_nonexpanding": True,
                "all_common_renewals_have_one_evidence_owner": True,
                "all_common_renewals_have_one_translation_owner": True,
                "all_exact_overrides_have_one_owner": True,
                "cross_selector1096_sequential_resolution": {
                    "correlation_guard": "zero-normalized dispatch trees and ordinal edge mapping",
                    "external_coordinate_count": 2,
                    "external_coordinate_sha256":
                        EXPECTED_EXTERNAL1096_COORDINATE_SHA256,
                    "ordinal_correlated_branch_rows": 14,
                    "ordinal_correlated_branches_nonexpanding": True,
                    "selector568_owned_coordinate_count": 2,
                    "selector568_owned_coordinate_sha256":
                        EXPECTED_SELECTOR568_CROSS_COORDINATE_SHA256,
                    "selector1096_owned_fields_not_overridden": True,
                },
                "pairwise_chunk_comparison": family["pairwise"],
                "selector538_family_evidence_supersession_rows":
                    EXPECTED_SELECTOR538_SUPERSESSION_ROWS,
                "selector538_family_evidence_supersession_sha256":
                    EXPECTED_SELECTOR538_SUPERSESSION_COORDINATE_SHA256,
            },
            "result": {
                "actual_promotion_rows": EXPECTED_ACTUAL_PROMOTION_ROWS,
                "actual_promotion_sha256":
                    EXPECTED_ACTUAL_PROMOTION_COORDINATE_SHA256,
                "decision_rows": EXPECTED_DECISION_ROWS,
                "decision_sha256": EXPECTED_DECISION_COORDINATE_SHA256,
                "family_candidate_sha256": candidate["family_sha256"],
                "official_candidate_sha256": candidate["official_sha256"],
                "override_rows": EXPECTED_OVERRIDE_ROWS,
                "override_sha256": EXPECTED_OVERRIDE_COORDINATE_SHA256,
                "pending_rows_after": EXPECTED_PENDING_AFTER,
                "pending_rows_before": EXPECTED_OFFICIAL_PENDING,
                "standalone_promotion_rows": EXPECTED_PROMOTION_ROWS,
                "standalone_promotion_sha256":
                    EXPECTED_PROMOTION_COORDINATE_SHA256,
                "superseded_promotion_rows": EXPECTED_SUPERSEDED_PROMOTION_ROWS,
                "superseded_promotion_sha256":
                    EXPECTED_SUPERSEDED_PROMOTION_COORDINATE_SHA256,
                "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
            },
            "schema": AUDIT_SCHEMA,
            "status": "PASS",
            "steam_write_performed": False,
        }
    )
    audit_payload_sha256 = audit["guards"]["report_payload_sha256"]
    updated_rows, evidence_rows = build_rows(
        official=official,
        chunks=chunks,
        family=family,
        selector538_evidence=selector538_evidence,
        audit_payload_sha256=audit_payload_sha256,
        candidate=candidate,
        cross=cross,
    )
    decision_content = canonical_jsonl(sorted(updated_rows, key=row_sort_key))
    evidence_content = canonical_jsonl(sorted(evidence_rows, key=row_sort_key))
    promotion = seal_report(
        {
            "evidence": {
                "action_counts": EXPECTED_ACTION_COUNTS,
                "audit_report_payload_sha256": audit_payload_sha256,
                "cross_private_sha256": cross["file_sha256"],
                "decision_private_sha256":
                    sha256_bytes(decision_content.encode("utf-8")),
                "evidence_private_sha256":
                    sha256_bytes(evidence_content.encode("utf-8")),
                "family_candidate_sha256": candidate["family_sha256"],
                "official_predecessor_private_sha256":
                    EXPECTED_OFFICIAL_PRIVATE_SHA256,
            },
            "guards": {
                "steam_archive_sha256_after": steam_before,
                "steam_archive_sha256_before": steam_before,
            },
            "method": METHOD,
            "result": {
                "actual_promotion_rows": EXPECTED_ACTUAL_PROMOTION_ROWS,
                "evidence_supersession_rows": EXPECTED_SUPERSEDED_PROMOTION_ROWS,
                "pending_rows_after": EXPECTED_PENDING_AFTER,
                "pending_rows_before": EXPECTED_OFFICIAL_PENDING,
                "private_decision_rows": EXPECTED_DECISION_ROWS,
                "private_evidence_rows": EXPECTED_DECISION_ROWS,
                "translation_override_rows": EXPECTED_OVERRIDE_ROWS,
                "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
            },
            "schema": PROMOTION_SCHEMA,
            "status": "PASS",
            "steam_write_performed": False,
        }
    )
    audit_content = canonical_json(audit)
    promotion_content = canonical_json(promotion)
    assert_source_free_report(audit)
    assert_source_free_report(promotion)
    steam_after = sha256_file(steam_path)
    require(steam_before == steam_after, "live Steam archive changed during family build")
    return {
        "audit": audit,
        "audit_content": audit_content,
        "candidate": candidate,
        "chunks": chunks,
        "cross": cross,
        "decision_content": decision_content,
        "evidence_content": evidence_content,
        "evidence_rows": evidence_rows,
        "family": family,
        "promotion": promotion,
        "promotion_content": promotion_content,
        "steam_after": steam_after,
        "steam_before": steam_before,
        "updated_rows": updated_rows,
    }


def output_hashes(bundle: Mapping[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        sha256_bytes(str(bundle["audit_content"]).encode("utf-8")),
        sha256_bytes(str(bundle["promotion_content"]).encode("utf-8")),
        sha256_bytes(str(bundle["decision_content"]).encode("utf-8")),
        sha256_bytes(str(bundle["evidence_content"]).encode("utf-8")),
        sha256_bytes(str(bundle["cross"]["content"]).encode("utf-8")),
    )


def validate_frozen(bundle: Mapping[str, Any]) -> None:
    expected = (
        EXPECTED_AUDIT_OUTPUT_SHA256,
        EXPECTED_PROMOTION_OUTPUT_SHA256,
        EXPECTED_DECISION_OUTPUT_SHA256,
        EXPECTED_EVIDENCE_OUTPUT_SHA256,
        EXPECTED_CROSS_PRIVATE_SHA256,
    )
    if all(value is not None for value in expected):
        require(output_hashes(bundle) == expected, "frozen family output drifted")


def write_exact(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    bundle = build_outputs()
    validate_frozen(bundle)
    outputs = (
        (DEFAULT_AUDIT_OUTPUT, bundle["audit_content"]),
        (DEFAULT_PROMOTION_OUTPUT, bundle["promotion_content"]),
        (DEFAULT_DECISION_OUTPUT, bundle["decision_content"]),
        (DEFAULT_EVIDENCE_OUTPUT, bundle["evidence_content"]),
        (DEFAULT_CROSS_OUTPUT, bundle["cross"]["content"]),
    )
    if args.check:
        for path, content in outputs:
            require(path.is_file(), f"missing frozen family output: {path}")
            require(
                path.read_text(encoding="utf-8") == content,
                f"family output drifted: {path}",
            )
    else:
        for path, content in outputs:
            write_exact(path, str(content))
    print(
        "PASS "
        f"promoted={EXPECTED_ACTUAL_PROMOTION_ROWS} "
        f"renewed={EXPECTED_RENEWAL_ROWS} "
        f"superseded={EXPECTED_SUPERSEDED_PROMOTION_ROWS} "
        f"overrides={EXPECTED_OVERRIDE_ROWS} "
        f"pending={EXPECTED_PENDING_AFTER} "
        f"hashes={output_hashes(bundle)} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
