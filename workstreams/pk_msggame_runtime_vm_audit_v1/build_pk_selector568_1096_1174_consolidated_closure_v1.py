#!/usr/bin/env python3
"""Build one selector-568/1096/1174 closure directly on frozen 81B4.

The three reviewed inputs are ownership proposals, not sequential archive
overlays.  This builder resolves their coordinate union against the frozen
post-selector-538 ledger, rebuilds the PK archive once, and records the exact
resolution only below ``tmp``.  The tracked reports contain counts and
digests, never dialogue bodies or exact coordinates.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"

ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector1174_assignment_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector1174_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1174_assignment_coverage.v1.json"
)
OFFICIAL_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector538_family_checkpoint.private.v1.jsonl"
)
OFFICIAL_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_selector538_family_checkpoint.source_free.v1.json"
)
CROSS_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_selector568_1096_cross_family_consolidated_closure_v1.py"
)
CROSS_DECISION_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector568_1096_cross_family_consolidated_closure_decisions.private.v1.jsonl"
)
CROSS_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector568_1096_cross_family_consolidated_closure_evidence.private.v1.jsonl"
)
CROSS_COVERAGE_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector568_1096_cross_family_consolidated_closure_coverage.v1.json"
)
CROSS_PROMOTION_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector568_1096_cross_family_consolidated_closure_promotion.v1.json"
)
CHUNK0_BUILDER_PATH = WORKSTREAM / "build_pk_selector1174_chunk0_review_v1.py"
CHUNK0_DECISION_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1174_chunk0_review_decisions.private.v1.jsonl"
)
CHUNK0_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1174_chunk0_review_evidence.private.v1.json"
)
CHUNK0_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1174_chunk0_review.source_free.v1.json"
)
CHUNK1_BUILDER_PATH = WORKSTREAM / "build_pk_selector1174_chunk1_review_v1.py"
CHUNK1_PRIVATE_GENERATOR_PATH = (
    DIALOGUE_TMP / "build_pk_selector1174_chunk1_review_private_v1.py"
)
CHUNK1_PRIVATE_PATH = (
    DIALOGUE_TMP / "pk_selector1174_chunk1_review.private.v1.json"
)
CHUNK1_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1174_chunk1_review_proposal.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector568_1096_1174_consolidated_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector568_1096_1174_consolidated_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector568_1096_1174_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector568_1096_1174_consolidated_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-selector568-1096-1174-consolidated-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-selector568-1096-1174-consolidated-closure-promotion.v1"
)
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector568-1096-1174-consolidated-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = (
    "nobu16.kr.pk-selector568-1096-1174-exact-override.v1"
)
METHOD = "reversed_vm_pk_selector568_1096_1174_current81b4_coordinate_union"
UPDATE_ACTION_FIELD = "selector568_1096_1174_consolidated_update_action"
OVERRIDE_FIELD = "selector568_1096_1174_exact_override_evidence"

EXPECTED_OFFICIAL_PRIVATE_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_OFFICIAL_PUBLIC_SHA256 = (
    "46270F70A019484EFB1F99851D436467C8FD2DE32EB222BDC048DA1B5BC080FA"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "07B892C55CAB031BDE414726FD301F03441E181C228D970003A834612ACABC10"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "6979EE31FB6AE4C046892E0785A61CC1D57F58415EB3B3D55601944F148A2CB2"
)
EXPECTED_CROSS_DECISION_SHA256 = (
    "E3C97823C70FBD441D420722AE306E2DEBE62CB8919FBA5426A91BC00DCBA5ED"
)
EXPECTED_CROSS_EVIDENCE_SHA256 = (
    "7CBCDC7D541EECD3B0946A61535B0030A288292F0C3C1C3DF750908BB4510799"
)
EXPECTED_CROSS_COVERAGE_SHA256 = (
    "2F3D7A91874B373568AE38BDB0C8202A7AF46ACFB36BE8236BD4D61BA3018F36"
)
EXPECTED_CROSS_PROMOTION_SHA256 = (
    "FC08FCA8A03B2D5BC10C113AED16D76E1A0463165F20047E80BBF554DCCF7CF3"
)
EXPECTED_CHUNK0_BUILDER_SHA256 = (
    "D2F13F5BEE94A3FD0E04C214827BE009284325AB0DDCF78C9B77F7A0887EF4E2"
)
EXPECTED_CHUNK0_DECISION_SHA256 = (
    "3188012B484E7A3A7A39A679A6B0B551DFD1F903BF0BE9EBCF3BC195CEFEA33B"
)
EXPECTED_CHUNK0_EVIDENCE_SHA256 = (
    "D442C6224729AC5FF6CD75D087A886B7059D8A220A152728C2C106FB5C2643C5"
)
EXPECTED_CHUNK0_PUBLIC_SHA256 = (
    "6DDF9C9CC84EC65A007230FB97477CACBD559C794341EC416F74DA2FFB65BD3F"
)
EXPECTED_CHUNK1_BUILDER_SHA256 = (
    "24B219BD90748FC0A8DA9F9875BCFA0BC687400330A89370FC490F27C5AC357F"
)
EXPECTED_CHUNK1_PRIVATE_GENERATOR_SHA256 = (
    "1E6FE52B025F78090232CB10304085D6C271A1CAB1DE101227694B975AC38035"
)
EXPECTED_CHUNK1_PRIVATE_SHA256 = (
    "7FEACBC29E0C4F9F46670B0A7781620AE7F54639FF58CED00D3C0453166C86EF"
)
EXPECTED_CHUNK1_PUBLIC_SHA256 = (
    "00BCA825E39953B1E0A6DD86842F78BAD32CF7EC0166BFC8F41F594EC50B82CC"
)
EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)

EXPECTED_ROWS = 52_803
EXPECTED_PENDING_BEFORE = 7_896
EXPECTED_PENDING_AFTER = 7_268
EXPECTED_CROSS_ROWS = 920
EXPECTED_CROSS_PROMOTIONS = 431
EXPECTED_CROSS_ASSEMBLIES = 2_114
EXPECTED_CHUNK0_DECISIONS = 152
EXPECTED_CHUNK0_OVERLAP = 5
EXPECTED_CHUNK0_OWNER_OVERLAP = 6
EXPECTED_CHUNK0_PROMOTIONS = 102
EXPECTED_CHUNK0_ASSEMBLIES = 385
EXPECTED_CHUNK0_OVERLAP_BRANCHES = 14
EXPECTED_CHUNK1_ACCEPTED_PENDING = 108
EXPECTED_CHUNK1_CROSS_RENEWALS = 13
EXPECTED_CHUNK1_OWNER_OVERLAP = 17
EXPECTED_CHUNK1_PROMOTIONS = 95
EXPECTED_CHUNK1_BLOCKED_CROSS = 0
EXPECTED_CHUNK1_OVERRIDES = 39
EXPECTED_CHUNK1_ASSEMBLIES = 420
EXPECTED_SELECTOR1174_ASSEMBLIES = 805
EXPECTED_REPAIR_ROOTS = 2
EXPECTED_REPAIR_COORDINATES = 10
EXPECTED_REPAIR_OVERRIDES = 4
EXPECTED_REPAIR_SELECTOR1174_BRANCHES = 14
EXPECTED_REPAIR_SELECTOR1096_BRANCHES = 7
EXPECTED_REQUIRED_CROSS_OVERRIDES = 7
EXPECTED_PENDING_OVERLAP = 18
EXPECTED_OWNER_OVERLAP = 23
EXPECTED_DECISION_ROWS = 1_173
EXPECTED_ACTUAL_PROMOTIONS = 628
EXPECTED_RENEWALS = 545
EXPECTED_FOUR_REPAIR_ONLY_CANDIDATE_SHA256 = (
    "9681A11B89FAA93E18F4C100537D0B29DF18974CF75085099024D876D6A43784"
)
EXPECTED_CHUNK1_PROPOSAL_CANDIDATE_SHA256 = (
    "8A982B3FE79CA7EC16899AF7E58339C81EEA9179675AE788C89CC65457614BCE"
)
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "DCB19B0D85422F7C0EA5888F9A0C47667D75A88D100BABAE11DDAF4A8DD2000E"
)
EXPECTED_CROSS_CANDIDATE_SHA256 = (
    "FF424B8C66BECD398E7617EA95904BFBEBFADEA581870CE5A142CD9BF3CA4845"
)
EXPECTED_CROSS_ASSEMBLY_SHA256 = (
    "CF1E913421B067D01BE226421C42BA37F4DB95C32DDA58E20902C2A20D10E67C"
)
EXPECTED_CHUNK0_ASSEMBLY_SHA256 = (
    "421DBF64BC4C13501BBFAB74CB39C7EC3DD36F13151FAC63ABD46042191D0D93"
)
EXPECTED_CHUNK1_ASSEMBLY_SHA256 = (
    "8BEB5BCFA5CC36BAB14A421BD0459C5F575753F190CB87CD71F67E7FE8221DBE"
)
EXPECTED_DEPENDENCY_ASSEMBLY_SHA256 = (
    "9F3D7E45118D3759A7B10E5F1D45D9089177ADFE88F46B66F472B0400FB2A9AE"
)

EXPECTED_DECISION_SHA256 = (
    "87ABCD0EE44FA7A020D8EE210452956DEA10A362EEA355F3A32523E90F97F794"
)
EXPECTED_PROMOTION_SHA256 = (
    "68C1F1020153F158E416DDD8500563F3701AE14497791F06806B7F61B27C0FAF"
)
EXPECTED_RENEWAL_SHA256 = (
    "56BFC0325D9EF5C975FC0836374F1BA3B705FB4ED7BEEA75FC91850E43A88E62"
)
EXPECTED_OVERRIDE_ROWS = 440
EXPECTED_OVERRIDE_SHA256 = (
    "44DE6C534744440519CB4A8B427E33D3B8B1ECF263B722E2702DCD9BEC6624A7"
)
EXPECTED_CONFLICT_ROWS = 12
EXPECTED_CONFLICT_SHA256 = (
    "1432F79D87F0F518E561495082827D3D9919A7B2DB8637256F80ECF265C39B6A"
)
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 413,
    "translation_override_and_runtime_promotion": 215,
    "translation_override_and_verification_renewal": 225,
    "verification_renewal": 320,
}
EXPECTED_SELECTOR1174_ASSEMBLY_SHA256 = (
    "5B3D42EF8F0B2B9D4C72AB783ECB7FBA40ABE3906E84DC14FE751CC129489C45"
)
EXPECTED_REPAIR_COORDINATE_SHA256 = (
    "50823D1FD202901C73E69143B7C84ED0FB3C420A02A245B05D585AEC88D79716"
)
EXPECTED_REPAIR_OVERRIDE_SHA256 = (
    "3B63D42531EF0C89D25953E58CA8FF7E037500ED688F2D259532502B8D207FC9"
)
EXPECTED_CHUNK0_OVERLAP_BRANCH_SHA256 = (
    "5DC19DB412FC4B4BECFA5245418B5F2D8E312D80D47A8AF831FDC4F82F3AE702"
)
EXPECTED_REPAIR_SELECTOR1174_BRANCH_SHA256 = (
    "41FD197B143561B43DB4BD20AC425BE71D4C7A282645EF6C5CE8C35D2637CF76"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "07E65E6338D32C1FD13F17408F82A4133E55541C722874632948C7B36C909805"
)
EXPECTED_AUDIT_OUTPUT_SHA256 = (
    "1C70A12C107DB79B1402F5879364F5AAEA31F34B3933F4C53524C89B570F9990"
)
EXPECTED_PROMOTION_OUTPUT_SHA256 = (
    "E16B597EF856822350D3FD0E0FAB7A9737E3D40D6FE156ED39EA778E5DE85AA0"
)
EXPECTED_DECISION_OUTPUT_SHA256 = (
    "3260FCF12561EE116228907E1619FDB368DBDF9D0BA8565C03CD014440669B38"
)
EXPECTED_EVIDENCE_OUTPUT_SHA256 = (
    "3AA3CB05106CA921F22B96D26B8FA74A4F7C7D15A4D3AE122738F92E10A34C25"
)


class ConsolidatedError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ConsolidatedError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ConsolidatedError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(canonical_json(dict(row)) for row in rows)


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = value.split(":")
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int]:
    return parse_coordinate(str(row["coordinate"]))


def coordinate_digest(values: Iterable[str]) -> str:
    return canonical_sha256(sorted(set(values), key=parse_coordinate))


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON object required: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def check_hash(path: Path, expected: str | None, label: str) -> None:
    require(path.is_file(), f"missing {label}: {path}")
    if expected is not None:
        require(sha256_file(path) == expected, f"{label} drifted")


def seal_report(value: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(value))
    guards = result.setdefault("guards", {})
    require(isinstance(guards, dict), "report guards must be an object")
    guards.pop("report_payload_sha256", None)
    guards["report_payload_sha256"] = canonical_sha256(result)
    return result


def assert_source_free_report(value: Any) -> None:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        )
        is None,
        "tracked report contains CJK dialogue",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+)?\b", serialized) is None,
        "tracked report contains an exact coordinate",
    )
    for forbidden in (
        '"translation"',
        '"current_assembly"',
        '"reviewed_assembly"',
        '"site_reviews"',
        '"exact_maps"',
    ):
        require(
            forbidden not in serialized,
            f"tracked report contains private body key: {forbidden}",
        )


def load_inputs() -> dict[str, Any]:
    immutable = (
        (OFFICIAL_PRIVATE_PATH, EXPECTED_OFFICIAL_PRIVATE_SHA256,
         "official private predecessor"),
        (OFFICIAL_PUBLIC_PATH, EXPECTED_OFFICIAL_PUBLIC_SHA256,
         "official public predecessor"),
        (ASSIGNMENT_PATH, EXPECTED_ASSIGNMENT_SHA256, "assignment private"),
        (ASSIGNMENT_PUBLIC_PATH, EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
         "assignment public"),
        (CROSS_DECISION_PATH, EXPECTED_CROSS_DECISION_SHA256,
         "cross decision"),
        (CROSS_EVIDENCE_PATH, EXPECTED_CROSS_EVIDENCE_SHA256,
         "cross evidence"),
        (CROSS_COVERAGE_PATH, EXPECTED_CROSS_COVERAGE_SHA256,
         "cross coverage"),
        (CROSS_PROMOTION_PATH, EXPECTED_CROSS_PROMOTION_SHA256,
         "cross promotion"),
        (CHUNK0_BUILDER_PATH, EXPECTED_CHUNK0_BUILDER_SHA256,
         "chunk0 builder"),
        (CHUNK0_DECISION_PATH, EXPECTED_CHUNK0_DECISION_SHA256,
         "chunk0 decisions"),
        (CHUNK0_EVIDENCE_PATH, EXPECTED_CHUNK0_EVIDENCE_SHA256,
         "chunk0 evidence"),
        (CHUNK0_PUBLIC_PATH, EXPECTED_CHUNK0_PUBLIC_SHA256,
         "chunk0 public"),
        (CHUNK1_BUILDER_PATH, EXPECTED_CHUNK1_BUILDER_SHA256,
         "chunk1 builder"),
        (CHUNK1_PRIVATE_GENERATOR_PATH,
         EXPECTED_CHUNK1_PRIVATE_GENERATOR_SHA256,
         "chunk1 private generator"),
        (CHUNK1_PRIVATE_PATH, EXPECTED_CHUNK1_PRIVATE_SHA256,
         "chunk1 private"),
        (CHUNK1_PUBLIC_PATH, EXPECTED_CHUNK1_PUBLIC_SHA256,
         "chunk1 public"),
    )
    for path, expected, label in immutable:
        check_hash(path, expected, label)

    official_rows = load_jsonl(OFFICIAL_PRIVATE_PATH)
    require(len(official_rows) == EXPECTED_ROWS, "official row count drifted")
    official = {
        (str(row["resource"]), str(row["coordinate"])): row
        for row in official_rows
    }
    require(len(official) == EXPECTED_ROWS, "official coordinate collision")
    pending = {
        str(row["coordinate"])
        for row in official_rows
        if row.get("resource") == "pk_msggame"
        and row.get("runtime_review") == "pending"
    }
    all_pending = sum(
        row.get("runtime_review") == "pending" for row in official_rows
    )
    require(all_pending == EXPECTED_PENDING_BEFORE, "pending count drifted")

    cross_rows = load_jsonl(CROSS_DECISION_PATH)
    cross_evidence = load_jsonl(CROSS_EVIDENCE_PATH)
    require(
        len(cross_rows) == len(cross_evidence) == EXPECTED_CROSS_ROWS,
        "cross private row count drifted",
    )
    cross_map = {
        str(row["coordinate"]): str(row["translation"])
        for row in cross_rows
    }
    require(len(cross_map) == EXPECTED_CROSS_ROWS, "cross coordinate collision")

    chunk0_rows = load_jsonl(CHUNK0_DECISION_PATH)
    require(
        len(chunk0_rows) == EXPECTED_CHUNK0_DECISIONS,
        "chunk0 decision count drifted",
    )
    chunk0_map = {
        str(row["coordinate"]): str(row["reviewed_translation"])
        for row in chunk0_rows
    }
    require(
        len(chunk0_map) == EXPECTED_CHUNK0_DECISIONS,
        "chunk0 coordinate collision",
    )

    assignment = load_json(ASSIGNMENT_PATH)
    chunks = assignment["chunks"]
    require(len(chunks) == 2, "selector1174 chunk partition drifted")
    chunk0 = chunks[0]
    chunk1 = chunks[1]
    chunk0_overlap = set(chunk0["cross_family_overlap_coordinates"])
    chunk0_disjoint = set(chunk0["disjoint_pending_coordinates"])
    require(
        len(chunk0_overlap) == EXPECTED_CHUNK0_OVERLAP
        and len(chunk0_disjoint) == EXPECTED_CHUNK0_PROMOTIONS,
        "chunk0 overlap/promotion partition drifted",
    )

    chunk1_private = load_json(CHUNK1_PRIVATE_PATH)
    exact = chunk1_private["exact_maps"]
    accepted_pending = set(exact["accepted_pending_coordinates"])
    cross_renewals = set(exact["cross_overlap_renewal_coordinates"])
    blocked_cross = set(exact["cross_overlap_blocked_coordinates"])
    disjoint_promotions = set(exact["disjoint_potential_promotion_coordinates"])
    overrides = {
        str(coordinate): str(body)
        for coordinate, body in exact["translation_overrides"].items()
    }
    required_cross_overrides = set(
        exact["cross_renewal_required_override_coordinates"]
    )
    require(
        len(accepted_pending) == EXPECTED_CHUNK1_ACCEPTED_PENDING
        and len(cross_renewals) == EXPECTED_CHUNK1_CROSS_RENEWALS
        and len(blocked_cross) == EXPECTED_CHUNK1_BLOCKED_CROSS
        and len(disjoint_promotions) == EXPECTED_CHUNK1_PROMOTIONS
        and len(overrides) == EXPECTED_CHUNK1_OVERRIDES
        and len(required_cross_overrides)
        == EXPECTED_REQUIRED_CROSS_OVERRIDES
        and accepted_pending == cross_renewals | disjoint_promotions
        and cross_renewals.isdisjoint(disjoint_promotions),
        "chunk1 corrected disposition drifted",
    )
    chunk1_decisions = accepted_pending | set(overrides)
    chunk1_map = {}
    for coordinate in chunk1_decisions:
        predecessor = cross_map.get(
            coordinate,
            str(official[("pk_msggame", coordinate)]["translation"]),
        )
        chunk1_map[coordinate] = overrides.get(coordinate, predecessor)

    return {
        "accepted_pending1": accepted_pending,
        "assignment": assignment,
        "blocked_cross1": blocked_cross,
        "chunk0": chunk0,
        "chunk0_disjoint": chunk0_disjoint,
        "chunk0_evidence": load_json(CHUNK0_EVIDENCE_PATH),
        "chunk0_map": chunk0_map,
        "chunk0_overlap": chunk0_overlap,
        "chunk0_rows": chunk0_rows,
        "chunk1": chunk1,
        "chunk1_map": chunk1_map,
        "chunk1_private": chunk1_private,
        "cross_evidence": cross_evidence,
        "cross_map": cross_map,
        "cross_renewals1": cross_renewals,
        "cross_rows": cross_rows,
        "disjoint_promotions1": disjoint_promotions,
        "official": official,
        "official_rows": official_rows,
        "overrides1": overrides,
        "pending": pending,
        "required_cross_overrides1": required_cross_overrides,
    }


def resolve_union(
    inputs: Mapping[str, Any],
    owner_order: Sequence[str] = ("cross", "chunk0", "chunk1"),
) -> dict[str, Any]:
    require(
        set(owner_order) == {"cross", "chunk0", "chunk1"}
        and len(owner_order) == 3,
        "owner order must be one permutation of the three inputs",
    )
    owner_maps = {
        "cross": inputs["cross_map"],
        "chunk0": inputs["chunk0_map"],
        "chunk1": inputs["chunk1_map"],
    }
    memberships: dict[str, dict[str, str]] = defaultdict(dict)
    for owner in owner_order:
        for coordinate, body in owner_maps[owner].items():
            memberships[coordinate][owner] = body

    union = set(memberships)
    cross = set(inputs["cross_map"])
    chunk0 = set(inputs["chunk0_map"])
    chunk1 = set(inputs["chunk1_map"])
    require(
        len(union) == EXPECTED_DECISION_ROWS,
        "consolidated decision-union count drifted",
    )
    require(
        len(cross & chunk0) == EXPECTED_CHUNK0_OWNER_OVERLAP
        and len(cross & chunk1) == EXPECTED_CHUNK1_OWNER_OVERLAP
        and not (chunk0 & chunk1),
        "owner overlap topology drifted",
    )

    final_translation: dict[str, str] = {}
    conflicts: set[str] = set()
    for coordinate in union:
        owners = memberships[coordinate]
        if len(set(owners.values())) > 1:
            conflicts.add(coordinate)
        if "chunk1" in owners:
            require(
                coordinate in inputs["accepted_pending1"]
                or coordinate in inputs["overrides1"],
                "chunk1 owner lacks accepted/override proof",
            )
            final_translation[coordinate] = owners["chunk1"]
        elif "chunk0" in owners:
            final_translation[coordinate] = owners["chunk0"]
        else:
            final_translation[coordinate] = owners["cross"]

    cross_promotions = cross & inputs["pending"]
    promotions = (
        cross_promotions
        | set(inputs["chunk0_disjoint"])
        | set(inputs["disjoint_promotions1"])
    )
    require(
        len(cross_promotions) == EXPECTED_CROSS_PROMOTIONS
        and len(promotions) == EXPECTED_ACTUAL_PROMOTIONS
        and promotions <= union
        and promotions <= inputs["pending"],
        "actual promotion union drifted",
    )
    renewals = union - promotions
    require(len(renewals) == EXPECTED_RENEWALS, "renewal count drifted")
    overrides = {
        coordinate
        for coordinate, body in final_translation.items()
        if body
        != inputs["official"][("pk_msggame", coordinate)]["translation"]
    }
    action_by_coordinate = {}
    for coordinate in union:
        promoted = coordinate in promotions
        changed = coordinate in overrides
        if promoted:
            action = (
                "translation_override_and_runtime_promotion"
                if changed else "runtime_promotion"
            )
        else:
            action = (
                "translation_override_and_verification_renewal"
                if changed else "verification_renewal"
            )
        action_by_coordinate[coordinate] = action
    action_counts = dict(sorted(Counter(action_by_coordinate.values()).items()))

    frozen = (
        (EXPECTED_DECISION_SHA256, coordinate_digest(union), "decision"),
        (EXPECTED_PROMOTION_SHA256, coordinate_digest(promotions), "promotion"),
        (EXPECTED_RENEWAL_SHA256, coordinate_digest(renewals), "renewal"),
        (EXPECTED_OVERRIDE_SHA256, coordinate_digest(overrides), "override"),
    )
    for expected, actual, label in frozen:
        if expected is not None:
            require(expected == actual, f"{label} digest drifted")
    if EXPECTED_OVERRIDE_ROWS is not None:
        require(len(overrides) == EXPECTED_OVERRIDE_ROWS, "override count drifted")
    if EXPECTED_ACTION_COUNTS is not None:
        require(action_counts == EXPECTED_ACTION_COUNTS, "action count drifted")
    require(
        len(conflicts) == EXPECTED_CONFLICT_ROWS
        and coordinate_digest(conflicts) == EXPECTED_CONFLICT_SHA256,
        "owner conflict set drifted",
    )
    return {
        "action_by_coordinate": action_by_coordinate,
        "action_counts": action_counts,
        "conflicts": conflicts,
        "final_translation": final_translation,
        "memberships": memberships,
        "overrides": overrides,
        "promotions": promotions,
        "renewals": renewals,
        "union": union,
    }


def verify_order_independence(
    inputs: Mapping[str, Any],
    reference: Mapping[str, Any],
) -> str:
    manifest = []
    for order in itertools.permutations(("cross", "chunk0", "chunk1")):
        resolved = resolve_union(inputs, order)
        require(
            resolved["final_translation"] == reference["final_translation"]
            and resolved["promotions"] == reference["promotions"]
            and resolved["renewals"] == reference["renewals"],
            f"owner-order dependence detected: {order}",
        )
        manifest.append(
            [
                list(order),
                coordinate_digest(resolved["union"]),
                canonical_sha256(resolved["final_translation"]),
            ]
        )
    return canonical_sha256(manifest)


def verify_assemblies(inputs: Mapping[str, Any]) -> dict[str, Any]:
    cross_public = load_json(CROSS_COVERAGE_PATH)
    cross_result = cross_public["result"]
    cross_proof = cross_public["proof"]
    require(
        cross_proof["accepted_family_assembly_rows"]
        == EXPECTED_CROSS_ASSEMBLIES
        and cross_proof["accepted_family_assembly_sha256"]
        == EXPECTED_CROSS_ASSEMBLY_SHA256
        and cross_proof[
            "all_family_assemblies_current_relative_raw_g1n_nonexpanding"
        ]
        is True,
        "cross accepted-assembly proof drifted",
    )

    chunk0_evidence = inputs["chunk0_evidence"]
    manifest0 = chunk0_evidence["assembly_manifest"]
    require(
        len(manifest0) == EXPECTED_CHUNK0_ASSEMBLIES
        and canonical_sha256(manifest0) == EXPECTED_CHUNK0_ASSEMBLY_SHA256,
        "chunk0 assembly proof drifted",
    )

    manifest1 = []
    for row in inputs["chunk1_private"]["site_reviews"]:
        accepted = row["decision"] != "reject"
        for branch in row["assemblies"]:
            terminal = int(str(branch["terminal_coordinate"]).split(":")[1])
            nonexpanding = bool(
                branch["current_relative_raw_g1n_nonexpanding"]
            )
            require(
                branch["register_and_grammar_proven"] is accepted
                and (not accepted or nonexpanding),
                "chunk1 branch verdict drifted",
            )
            manifest1.append(
                [
                    int(row["ordinal"]),
                    str(row["site"]),
                    terminal,
                    sha256_bytes(str(branch["reviewed_assembly"]).encode("utf-8")),
                    sha256_bytes(str(branch["current_assembly"]).encode("utf-8")),
                    nonexpanding,
                    accepted,
                ]
            )
    require(
        len(manifest1) == EXPECTED_CHUNK1_ASSEMBLIES
        and canonical_sha256(manifest1) == EXPECTED_CHUNK1_ASSEMBLY_SHA256,
        "chunk1 assembly proof drifted",
    )
    selector1174_manifest = (
        [["chunk0", *row] for row in manifest0]
        + [["chunk1", *row] for row in manifest1]
    )
    selector1174_sha = canonical_sha256(selector1174_manifest)
    require(
        len(selector1174_manifest) == EXPECTED_SELECTOR1174_ASSEMBLIES,
        "selector1174 combined branch count drifted",
    )
    if EXPECTED_SELECTOR1174_ASSEMBLY_SHA256 is not None:
        require(
            selector1174_sha == EXPECTED_SELECTOR1174_ASSEMBLY_SHA256,
            "selector1174 combined branch digest drifted",
        )

    overlap0_roots = {
        parse_coordinate(coordinate)[:2]
        for coordinate in inputs["chunk0_overlap"]
    }
    overlap0_sites = {
        str(row["site"])
        for row in chunk0_evidence["site_reviews"]
        if tuple(int(part) for part in str(row["root"]).split(":"))
        in overlap0_roots
    }
    overlap0_manifest = [
        row for row in manifest0 if str(row[1]) in overlap0_sites
    ]
    require(
        len(overlap0_manifest) == EXPECTED_CHUNK0_OVERLAP_BRANCHES
        and all(row[-2:] == [True, True] for row in overlap0_manifest),
        "chunk0 overlap branch proof drifted",
    )
    overlap0_sha = canonical_sha256(overlap0_manifest)
    if EXPECTED_CHUNK0_OVERLAP_BRANCH_SHA256 is not None:
        require(
            overlap0_sha == EXPECTED_CHUNK0_OVERLAP_BRANCH_SHA256,
            "chunk0 overlap branch digest drifted",
        )

    repair_rows = [
        row
        for row in inputs["chunk1_private"]["site_reviews"]
        if int(row["ordinal"]) in {57, 76}
    ]
    require(
        len(repair_rows) == EXPECTED_REPAIR_ROOTS
        and all(row["decision"] == "rewrite" for row in repair_rows),
        "repair site identity drifted",
    )
    repair_roots = {
        tuple(int(part) for part in str(row["root"]).split(":"))
        for row in repair_rows
    }
    repair_coordinates = {
        coordinate
        for coordinate in inputs["cross_renewals1"]
        if parse_coordinate(coordinate)[:2] in repair_roots
    }
    repair_overrides = set(inputs["overrides1"]) & repair_coordinates
    require(
        len(repair_roots) == EXPECTED_REPAIR_ROOTS
        and len(repair_coordinates) == EXPECTED_REPAIR_COORDINATES
        and len(repair_overrides) == EXPECTED_REPAIR_OVERRIDES
        and repair_overrides <= inputs["required_cross_overrides1"],
        "repair coordinate/override proof drifted",
    )
    repair1174_manifest = [
        row
        for row in manifest1
        if int(row[0]) in {57, 76}
    ]
    require(
        len(repair1174_manifest) == EXPECTED_REPAIR_SELECTOR1174_BRANCHES
        and all(row[-2:] == [True, True] for row in repair1174_manifest),
        "repair selector1174 branch proof drifted",
    )
    repair1174_sha = canonical_sha256(repair1174_manifest)
    if EXPECTED_REPAIR_SELECTOR1174_BRANCH_SHA256 is not None:
        require(
            repair1174_sha == EXPECTED_REPAIR_SELECTOR1174_BRANCH_SHA256,
            "repair selector1174 digest drifted",
        )

    dependency_manifest = []
    for row in repair_rows:
        for branch in row["dependency_assemblies"]:
            terminal = int(str(branch["terminal_coordinate"]).split(":")[1])
            require(
                branch["selector"] == 1096
                and branch["current_relative_raw_g1n_nonexpanding"] is True,
                "repair dependency branch drifted",
            )
            dependency_manifest.append(
                [
                    str(row["site"]),
                    terminal,
                    sha256_bytes(str(branch["reviewed_assembly"]).encode("utf-8")),
                    sha256_bytes(str(branch["current_assembly"]).encode("utf-8")),
                    True,
                ]
            )
    require(
        len(dependency_manifest) == EXPECTED_REPAIR_SELECTOR1096_BRANCHES
        and canonical_sha256(dependency_manifest)
        == EXPECTED_DEPENDENCY_ASSEMBLY_SHA256,
        "repair selector1096 dependency proof drifted",
    )

    repair_coordinate_sha = coordinate_digest(repair_coordinates)
    repair_override_sha = coordinate_digest(repair_overrides)
    if EXPECTED_REPAIR_COORDINATE_SHA256 is not None:
        require(
            repair_coordinate_sha == EXPECTED_REPAIR_COORDINATE_SHA256,
            "repair coordinate digest drifted",
        )
    if EXPECTED_REPAIR_OVERRIDE_SHA256 is not None:
        require(
            repair_override_sha == EXPECTED_REPAIR_OVERRIDE_SHA256,
            "repair override digest drifted",
        )
    return {
        "chunk0_overlap_branch_manifest": overlap0_manifest,
        "chunk0_overlap_branch_sha256": overlap0_sha,
        "dependency_manifest": dependency_manifest,
        "repair_coordinate_sha256": repair_coordinate_sha,
        "repair_coordinates": repair_coordinates,
        "repair_override_sha256": repair_override_sha,
        "repair_overrides": repair_overrides,
        "repair_roots": repair_roots,
        "repair_selector1174_manifest": repair1174_manifest,
        "repair_selector1174_sha256": repair1174_sha,
        "selector1174_manifest": selector1174_manifest,
        "selector1174_sha256": selector1174_sha,
    }


def rebuild_candidate(
    inputs: Mapping[str, Any],
    union: Mapping[str, Any],
    assemblies: Mapping[str, Any],
) -> dict[str, Any]:
    assignment_module = load_module(
        ASSIGNMENT_BUILDER_PATH,
        "pk_selector568_1096_1174_assignment_input_v1",
    )
    engine = assignment_module.ENGINE
    archive_path = (
        assignment_module.RANKING.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "JP"
        / "msggame.bin"
    )
    live_path = Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
    )
    require(archive_path.is_file(), "development PK archive is absent")
    require(
        archive_path.resolve() != live_path.resolve(),
        "consolidated closure refuses the live Steam archive as input",
    )
    original = archive_path.read_bytes()
    official_replacements = {
        parse_coordinate(str(row["coordinate"])): str(row["translation"])
        for row in inputs["official_rows"]
        if row.get("resource") == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    official_blob = engine.rebuild_packed_with_literals(
        original, official_replacements
    )
    require(
        sha256_bytes(official_blob) == EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        "official candidate drifted",
    )
    cross_replacements = dict(official_replacements)
    cross_replacements.update(
        {
            parse_coordinate(coordinate): body
            for coordinate, body in inputs["cross_map"].items()
        }
    )
    cross_blob = engine.rebuild_packed_with_literals(original, cross_replacements)
    require(
        sha256_bytes(cross_blob) == EXPECTED_CROSS_CANDIDATE_SHA256,
        "cross candidate drifted",
    )

    repair_replacements = dict(cross_replacements)
    repair_replacements.update(
        {
            parse_coordinate(coordinate): inputs["overrides1"][coordinate]
            for coordinate in assemblies["repair_overrides"]
        }
    )
    repair_blob = engine.rebuild_packed_with_literals(
        original, repair_replacements
    )
    require(
        sha256_bytes(repair_blob)
        == EXPECTED_FOUR_REPAIR_ONLY_CANDIDATE_SHA256,
        "four-repair-only candidate drifted",
    )

    chunk1_replacements = dict(cross_replacements)
    chunk1_replacements.update(
        {
            parse_coordinate(coordinate): body
            for coordinate, body in inputs["overrides1"].items()
        }
    )
    chunk1_blob = engine.rebuild_packed_with_literals(
        original, chunk1_replacements
    )
    require(
        sha256_bytes(chunk1_blob)
        == EXPECTED_CHUNK1_PROPOSAL_CANDIDATE_SHA256,
        "chunk1 proposal candidate drifted",
    )

    final_replacements = dict(official_replacements)
    final_replacements.update(
        {
            parse_coordinate(coordinate): body
            for coordinate, body in union["final_translation"].items()
        }
    )
    final_blob = engine.rebuild_packed_with_literals(
        original, final_replacements
    )
    final_sha = sha256_bytes(final_blob)
    if EXPECTED_FINAL_CANDIDATE_SHA256 is not None:
        require(
            final_sha == EXPECTED_FINAL_CANDIDATE_SHA256,
            "final consolidated candidate drifted",
        )

    reverse_replacements = {
        parse_coordinate(coordinate): str(
            inputs["official"][("pk_msggame", coordinate)]["translation"]
        )
        for coordinate in union["union"]
    }
    reverse_blob = engine.rebuild_packed_with_literals(
        final_blob, reverse_replacements
    )
    require(
        reverse_blob == official_blob,
        "reverse overlay did not recover frozen 81B4 candidate",
    )

    official_records = engine.archive_records(
        engine.parse_packed_msggame(official_blob).archive
    )
    final_records = engine.archive_records(
        engine.parse_packed_msggame(final_blob).archive
    )
    changed_roots = {
        parse_coordinate(coordinate)[:2]
        for coordinate in union["overrides"]
    }
    actual_changed_roots = {
        root
        for root in official_records
        if official_records[root].data != final_records[root].data
    }
    require(
        actual_changed_roots == changed_roots,
        "candidate changed-root universe drifted",
    )
    for root in changed_roots:
        official_gaps = engine.record_gap_bytes(official_records[root])
        final_gaps = engine.record_gap_bytes(final_records[root])
        require(
            official_gaps == final_gaps,
            f"record control gaps changed at {root}",
        )
    return {
        "changed_root_count": len(changed_roots),
        "final_blob": final_blob,
        "final_sha256": final_sha,
        "official_blob": official_blob,
        "reverse_sha256": sha256_bytes(reverse_blob),
    }


def build_private_rows(
    inputs: Mapping[str, Any],
    union: Mapping[str, Any],
    candidate: Mapping[str, Any],
    assemblies: Mapping[str, Any],
    audit_payload_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cross_rows = {
        str(row["coordinate"]): row for row in inputs["cross_rows"]
    }
    rows = []
    evidence_rows = []
    decision_sha = coordinate_digest(union["union"])
    for coordinate in sorted(union["union"], key=parse_coordinate):
        predecessor = inputs["official"][("pk_msggame", coordinate)]
        preferred = cross_rows.get(coordinate, predecessor)
        translation = union["final_translation"][coordinate]
        owners = sorted(union["memberships"][coordinate])
        evidence = {
            "action": union["action_by_coordinate"][coordinate],
            "closure_binding": {
                "audit_report_payload_sha256": audit_payload_sha256,
                "cross_accepted_assembly_sha256":
                    EXPECTED_CROSS_ASSEMBLY_SHA256,
                "decision_coordinate_sha256": decision_sha,
                "final_candidate_sha256": candidate["final_sha256"],
                "official_predecessor_sha256":
                    EXPECTED_OFFICIAL_PRIVATE_SHA256,
                "selector1174_assembly_sha256":
                    assemblies["selector1174_sha256"],
            },
            "coordinate": coordinate,
            "current81b4_rebase": {
                "actual_runtime_promotion":
                    coordinate in union["promotions"],
                "official_runtime_review_before":
                    predecessor["runtime_review"],
            },
            "method": METHOD,
            "owners": owners,
            "per_row_game_playback_required": False,
            "predecessor_binding": {
                "checkpoint_sha256": EXPECTED_OFFICIAL_PRIVATE_SHA256,
                "row_sha256": canonical_sha256(predecessor),
            },
            "repair_binding": {
                "repair_coordinate_set_member":
                    coordinate in assemblies["repair_coordinates"],
                "repair_exact_override":
                    coordinate in assemblies["repair_overrides"],
                "selector1096_dependency_branch_sha256":
                    EXPECTED_DEPENDENCY_ASSEMBLY_SHA256,
                "selector1174_repair_branch_sha256":
                    assemblies["repair_selector1174_sha256"],
            },
            "resource": "pk_msggame",
            "schema": EVIDENCE_SCHEMA,
            "status": "verified",
            "translation_utf16le_sha256": sha256_text(translation),
        }
        row = copy.deepcopy(dict(preferred))
        row["coordinate"] = coordinate
        row["resource"] = "pk_msggame"
        row["translation"] = translation
        row["semantic_review"] = "approved"
        row["runtime_review"] = "verified"
        if coordinate in union["promotions"]:
            row["scope_classification"] = "retranslated"
            row["layout_review"] = "runtime_verified"
        row[UPDATE_ACTION_FIELD] = union["action_by_coordinate"][coordinate]
        row["runtime_vm_verification"] = evidence
        if coordinate in union["overrides"]:
            row[OVERRIDE_FIELD] = {
                "schema": OVERRIDE_SCHEMA,
                "translation_utf16le_sha256": sha256_text(translation),
            }
        rows.append(row)
        evidence_rows.append(evidence)
    promoted_rows = [
        row for row in rows if row["coordinate"] in union["promotions"]
    ]
    require(
        len(promoted_rows) == EXPECTED_ACTUAL_PROMOTIONS
        and all(
            row["scope_classification"] == "retranslated"
            and row["layout_review"] == "runtime_verified"
            and row["runtime_review"] == "verified"
            for row in promoted_rows
        ),
        "promoted-row contract drifted",
    )
    return rows, evidence_rows


def build_outputs() -> dict[str, Any]:
    inputs = load_inputs()
    live_path = Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
    )
    require(live_path.is_file(), "live Steam PK archive is absent")
    steam_before = sha256_file(live_path)
    require(
        steam_before == EXPECTED_STEAM_PK_SHA256,
        "live Steam PK archive drifted before closure",
    )
    union = resolve_union(inputs)
    order_independence_sha = verify_order_independence(inputs, union)
    assemblies = verify_assemblies(inputs)
    candidate = rebuild_candidate(inputs, union, assemblies)
    audit = seal_report(
        {
            "distribution_policy": {
                "private_decisions_stay_below_tmp": True,
                "private_dialogue_proof_stays_below_tmp": True,
                "tracked_report_contains_commercial_source_text": False,
                "tracked_report_contains_exact_coordinates": False,
                "tracked_report_contains_translated_dialogue_text": False,
            },
            "guards": {
                "chunk0_private_decision_sha256":
                    sha256_file(CHUNK0_DECISION_PATH),
                "chunk0_private_evidence_sha256":
                    sha256_file(CHUNK0_EVIDENCE_PATH),
                "chunk1_private_evidence_sha256":
                    EXPECTED_CHUNK1_PRIVATE_SHA256,
                "cross_private_decision_sha256":
                    EXPECTED_CROSS_DECISION_SHA256,
                "cross_private_evidence_sha256":
                    EXPECTED_CROSS_EVIDENCE_SHA256,
                "official_predecessor_sha256":
                    EXPECTED_OFFICIAL_PRIVATE_SHA256,
                "steam_archive_sha256_after": steam_before,
                "steam_archive_sha256_before": steam_before,
            },
            "method": METHOD,
            "proof": {
                "coordinate_union_built_directly_on_frozen_predecessor": True,
                "cross_accepted_assembly_rows": EXPECTED_CROSS_ASSEMBLIES,
                "cross_accepted_assembly_sha256":
                    EXPECTED_CROSS_ASSEMBLY_SHA256,
                "demotion_rows": 0,
                "event_dialogue_912px_rule_applied": False,
                "explicit_owner_conflict_rows": EXPECTED_CONFLICT_ROWS,
                "explicit_owner_conflict_sha256":
                    EXPECTED_CONFLICT_SHA256,
                "owner_overlap_rows": EXPECTED_OWNER_OVERLAP,
                "owner_order_permutation_count": 6,
                "owner_order_permutation_sha256": order_independence_sha,
                "pending_overlap_rows": EXPECTED_PENDING_OVERLAP,
                "record_control_gaps_preserved": True,
                "repair": {
                    "exact_override_rows": EXPECTED_REPAIR_OVERRIDES,
                    "exact_override_sha256":
                        assemblies["repair_override_sha256"],
                    "selector1096_dependency_branch_rows":
                        EXPECTED_REPAIR_SELECTOR1096_BRANCHES,
                    "selector1096_dependency_branch_sha256":
                        EXPECTED_DEPENDENCY_ASSEMBLY_SHA256,
                    "selector1174_branch_rows":
                        EXPECTED_REPAIR_SELECTOR1174_BRANCHES,
                    "selector1174_branch_sha256":
                        assemblies["repair_selector1174_sha256"],
                    "two_root_coordinate_rows":
                        EXPECTED_REPAIR_COORDINATES,
                    "two_root_coordinate_sha256":
                        assemblies["repair_coordinate_sha256"],
                },
                "selector1174": {
                    "branch_rows": EXPECTED_SELECTOR1174_ASSEMBLIES,
                    "branch_sha256": assemblies["selector1174_sha256"],
                    "chunk0_cross_overlap_branch_rows":
                        EXPECTED_CHUNK0_OVERLAP_BRANCHES,
                    "chunk0_cross_overlap_branch_sha256":
                        assemblies["chunk0_overlap_branch_sha256"],
                    "current_relative_raw_g1n_nonexpanding": True,
                },
                "single_archive_rebuild_from_resolved_coordinate_union": True,
            },
            "result": {
                "actual_promotion_rows": EXPECTED_ACTUAL_PROMOTIONS,
                "actual_promotion_sha256":
                    coordinate_digest(union["promotions"]),
                "decision_rows": EXPECTED_DECISION_ROWS,
                "decision_sha256": coordinate_digest(union["union"]),
                "final_candidate_sha256": candidate["final_sha256"],
                "pending_rows_after": EXPECTED_PENDING_AFTER,
                "pending_rows_before": EXPECTED_PENDING_BEFORE,
                "semantic_override_rows": len(union["overrides"]),
                "semantic_override_sha256":
                    coordinate_digest(union["overrides"]),
                "verification_renewal_rows": EXPECTED_RENEWALS,
                "verification_renewal_sha256":
                    coordinate_digest(union["renewals"]),
            },
            "schema": AUDIT_SCHEMA,
            "status": "PASS",
            "steam_write_performed": False,
        }
    )
    updated_rows, evidence_rows = build_private_rows(
        inputs,
        union,
        candidate,
        assemblies,
        audit["guards"]["report_payload_sha256"],
    )
    decision_content = canonical_jsonl(sorted(updated_rows, key=row_sort_key))
    evidence_content = canonical_jsonl(
        sorted(evidence_rows, key=row_sort_key)
    )
    promotion = seal_report(
        {
            "evidence": {
                "action_counts": union["action_counts"],
                "audit_report_payload_sha256":
                    audit["guards"]["report_payload_sha256"],
                "decision_private_sha256":
                    sha256_bytes(decision_content.encode("utf-8")),
                "evidence_private_sha256":
                    sha256_bytes(evidence_content.encode("utf-8")),
                "final_candidate_sha256": candidate["final_sha256"],
                "official_predecessor_sha256":
                    EXPECTED_OFFICIAL_PRIVATE_SHA256,
            },
            "guards": {
                "steam_archive_sha256_after": steam_before,
                "steam_archive_sha256_before": steam_before,
            },
            "method": METHOD,
            "result": {
                "actual_promotion_rows": EXPECTED_ACTUAL_PROMOTIONS,
                "demotion_rows": 0,
                "pending_rows_after": EXPECTED_PENDING_AFTER,
                "pending_rows_before": EXPECTED_PENDING_BEFORE,
                "private_decision_rows": EXPECTED_DECISION_ROWS,
                "private_evidence_rows": EXPECTED_DECISION_ROWS,
                "semantic_override_rows": len(union["overrides"]),
                "verification_renewal_rows": EXPECTED_RENEWALS,
            },
            "schema": PROMOTION_SCHEMA,
            "status": "PASS",
            "steam_write_performed": False,
        }
    )
    assert_source_free_report(audit)
    assert_source_free_report(promotion)
    steam_after = sha256_file(live_path)
    require(
        steam_after == steam_before == EXPECTED_STEAM_PK_SHA256,
        "live Steam PK archive changed during closure",
    )
    return {
        "assemblies": assemblies,
        "audit": audit,
        "audit_content": canonical_json(audit),
        "candidate": candidate,
        "decision_content": decision_content,
        "evidence_content": evidence_content,
        "evidence_rows": evidence_rows,
        "inputs": inputs,
        "promotion": promotion,
        "promotion_content": canonical_json(promotion),
        "steam_after": steam_after,
        "steam_before": steam_before,
        "union": union,
        "updated_rows": updated_rows,
    }


def output_hashes(bundle: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (
        sha256_bytes(str(bundle["audit_content"]).encode("utf-8")),
        sha256_bytes(str(bundle["promotion_content"]).encode("utf-8")),
        sha256_bytes(str(bundle["decision_content"]).encode("utf-8")),
        sha256_bytes(str(bundle["evidence_content"]).encode("utf-8")),
    )


def validate_frozen(bundle: Mapping[str, Any]) -> None:
    expected = (
        EXPECTED_AUDIT_OUTPUT_SHA256,
        EXPECTED_PROMOTION_OUTPUT_SHA256,
        EXPECTED_DECISION_OUTPUT_SHA256,
        EXPECTED_EVIDENCE_OUTPUT_SHA256,
    )
    if all(value is not None for value in expected):
        require(
            output_hashes(bundle) == expected,
            "frozen consolidated outputs drifted",
        )


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
    )
    if args.check:
        for path, content in outputs:
            require(path.is_file(), f"missing frozen output: {path}")
            require(
                path.read_text(encoding="utf-8") == content,
                f"consolidated output drifted: {path}",
            )
    else:
        for path, content in outputs:
            write_exact(path, str(content))
    print(
        "PASS "
        f"promoted={EXPECTED_ACTUAL_PROMOTIONS} "
        f"renewed={EXPECTED_RENEWALS} "
        f"overrides={len(bundle['union']['overrides'])} "
        f"pending={EXPECTED_PENDING_AFTER} "
        f"hashes={output_hashes(bundle)} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
