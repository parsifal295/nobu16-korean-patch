#!/usr/bin/env python3
"""Consolidate selector-568 and selector-1096 families on current 81B4.

Both family builders are direct rebases, so applying their private decisions
sequentially would give eight shared coordinates two owners.  This builder
loads both frozen family layers, creates one union directly from the official
81B4 ledger, and resolves the two sequential multi-selector records with the
private correlated-branch proof.  It never writes a game archive.
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
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"

FAMILY568_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector568_family_consolidated_closure_v1.py"
)
FAMILY1096_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector1096_family_consolidated_closure_v1.py"
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
CROSS_DEFERRED_PATH = (
    DIALOGUE_TMP / "selector1096_cross568_deferred.private.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector568_1096_cross_family_consolidated_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector568_1096_cross_family_consolidated_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector568_1096_cross_family_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector568_1096_cross_family_consolidated_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-selector568-1096-cross-family-consolidated-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-selector568-1096-cross-family-consolidated-closure-promotion.v1"
)
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector568-1096-cross-family-consolidated-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = (
    "nobu16.kr.pk-selector568-1096-cross-family-exact-override.v1"
)
METHOD = "reversed_vm_pk_selector568_1096_current81b4_cross_family_consolidated"
UPDATE_ACTION_FIELD = "selector568_1096_cross_family_update_action"
OVERRIDE_FIELD = "selector568_1096_cross_family_exact_override_evidence"

EXPECTED_OFFICIAL_PRIVATE_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_OFFICIAL_PUBLIC_SHA256 = (
    "46270F70A019484EFB1F99851D436467C8FD2DE32EB222BDC048DA1B5BC080FA"
)
EXPECTED_CROSS_DEFERRED_SHA256 = (
    "99BD8D08ACE41CE296C8B3EC36FE25A27713B9293CFC06E680BF56FECEAB362E"
)
EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_FAMILY568_BUILDER_SHA256 = (
    "269955D894026F40AA0606F528C8400491827A2066A9ECBBD9B42788A1516391"
)
EXPECTED_FAMILY1096_BUILDER_SHA256 = (
    "32C84BE916DFE9BDB0F563759DE97A05904D0711D9A220223516CCF207877196"
)

EXPECTED_ROWS = 52_803
EXPECTED_PENDING_BEFORE = 7_896
EXPECTED_PENDING_AFTER = 7_465
EXPECTED_FAMILY568_ROWS = 503
EXPECTED_FAMILY1096_ROWS = 425
EXPECTED_DECISION_ROWS = 920
EXPECTED_FAMILY_OVERLAP_ROWS = 8
EXPECTED_FAMILY_TRANSLATION_DIFF_ROWS = 2
EXPECTED_ACTUAL_PROMOTION_ROWS = 431
EXPECTED_VERIFICATION_RENEWAL_ROWS = 489
EXPECTED_ACCEPTED_ASSEMBLY_ROWS = 2_114
EXPECTED_CROSS_RECORD_ROWS = 2
EXPECTED_CROSS_COORDINATE_ROWS = 4
EXPECTED_CROSS_BRANCH_ROWS = 14

EXPECTED_FAMILY_OVERLAP_SHA256 = (
    "19BF772C7852031143C06A174940B993C9FA88743FE3B30AF199337902C87851"
)
EXPECTED_FAMILY_TRANSLATION_DIFF_SHA256 = (
    "1A9F42D9DD02EE4FA19D65F8101D4015F059A8D96222D32CBCAE8891C254A3FC"
)
EXPECTED_DECISION_SHA256 = (
    "F247BBFBAC913F6726C51592934582910B3E6DB4A2E88C617F4B655002A8CF0F"
)
EXPECTED_ACTUAL_PROMOTION_SHA256 = (
    "AFC6000F066EB80129A240A7132C7351182F1C17D911732792F49E616700632D"
)
EXPECTED_VERIFICATION_RENEWAL_SHA256 = (
    "CEECEA07171A5CAA95464A3508145107C275463B344AD9B374125737D00C7758"
)
EXPECTED_OVERRIDE_ROWS = 285
EXPECTED_OVERRIDE_SHA256 = (
    "FEC84F6BBE95591921203E01528D0D3C7FE38C4D986CCA59878F6EFF5909A9C7"
)
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 310,
    "translation_override_and_runtime_promotion": 121,
    "translation_override_and_verification_renewal": 164,
    "verification_renewal": 325,
}
EXPECTED_ACCEPTED_ASSEMBLY_SHA256 = (
    "CF1E913421B067D01BE226421C42BA37F4DB95C32DDA58E20902C2A20D10E67C"
)
EXPECTED_CROSS_BRANCH_SHA256 = (
    "FC56801E6C71D46464BDC3265B028C0DF281632D6E42DB889AED5E2EF9FCDC22"
)
EXPECTED_CROSS_COORDINATE_SHA256 = (
    "09FFC277537C85AE45B60A5FCEFB82CC114B660901ABE4EC861520E1CB495502"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "FF424B8C66BECD398E7617EA95904BFBEBFADEA581870CE5A142CD9BF3CA4845"
)
EXPECTED_AUDIT_OUTPUT_SHA256 = (
    "2F3D7A91874B373568AE38BDB0C8202A7AF46ACFB36BE8236BD4D61BA3018F36"
)
EXPECTED_PROMOTION_OUTPUT_SHA256 = (
    "FC08FCA8A03B2D5BC10C113AED16D76E1A0463165F20047E80BBF554DCCF7CF3"
)
EXPECTED_DECISION_OUTPUT_SHA256 = (
    "E3C97823C70FBD441D420722AE306E2DEBE62CB8919FBA5426A91BC00DCBA5ED"
)
EXPECTED_EVIDENCE_OUTPUT_SHA256 = (
    "7CBCDC7D541EECD3B0946A61535B0030A288292F0C3C1C3DF750908BB4510799"
)


class CrossFamilyError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CrossFamilyError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CrossFamilyError(f"cannot import {path}")
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


def coordinate_digest(values: Iterable[str]) -> str:
    return canonical_sha256(sorted(set(values), key=parse_coordinate))


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int]:
    return parse_coordinate(str(row["coordinate"]))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


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
        "tracked report contains dialogue coordinate",
    )
    for forbidden in (
        "translation",
        "current_assembly",
        "reviewed_assembly",
        "jp_authority",
    ):
        require(
            f'"{forbidden}"' not in serialized,
            f"tracked report contains forbidden body key: {forbidden}",
        )


def load_families() -> dict[str, Any]:
    if EXPECTED_FAMILY568_BUILDER_SHA256 is not None:
        require(
            sha256_file(FAMILY568_BUILDER_PATH)
            == EXPECTED_FAMILY568_BUILDER_SHA256,
            "selector568 family builder drifted",
        )
    require(
        sha256_file(FAMILY1096_BUILDER_PATH)
        == EXPECTED_FAMILY1096_BUILDER_SHA256,
        "selector1096 family builder drifted",
    )
    family568_module = load_module(
        FAMILY568_BUILDER_PATH,
        "pk_selector568_cross_family_input_v1",
    )
    family1096_module = load_module(
        FAMILY1096_BUILDER_PATH,
        "pk_selector1096_cross_family_input_v1",
    )
    family568 = family568_module.build_outputs()
    family1096 = family1096_module.build_outputs()
    family568_module.validate_frozen(family568)
    family1096_module.validate_frozen(family1096)
    for module, bundle in (
        (family568_module, family568),
        (family1096_module, family1096),
    ):
        for path, content in (
            (module.DEFAULT_AUDIT_OUTPUT, bundle["audit_content"]),
            (module.DEFAULT_PROMOTION_OUTPUT, bundle["promotion_content"]),
            (module.DEFAULT_DECISION_OUTPUT, bundle["decision_content"]),
            (module.DEFAULT_EVIDENCE_OUTPUT, bundle["evidence_content"]),
        ):
            require(
                path.is_file()
                and path.read_text(encoding="utf-8") == content,
                f"family output is not frozen: {path}",
            )
    return {
        "family568": family568,
        "family568_module": family568_module,
        "family1096": family1096,
        "family1096_module": family1096_module,
    }


def load_official(
    family1096_module: Any,
) -> tuple[
    list[dict[str, Any]],
    dict[tuple[str, str], dict[str, Any]],
]:
    require(
        sha256_file(OFFICIAL_PRIVATE_PATH)
        == EXPECTED_OFFICIAL_PRIVATE_SHA256,
        "official private predecessor drifted",
    )
    require(
        sha256_file(OFFICIAL_PUBLIC_PATH)
        == EXPECTED_OFFICIAL_PUBLIC_SHA256,
        "official public predecessor drifted",
    )
    rows, mapping, public = family1096_module.load_official()
    require(
        len(rows) == EXPECTED_ROWS
        and public["result"]["runtime_review_pending"]
        == EXPECTED_PENDING_BEFORE,
        "official predecessor count drifted",
    )
    return rows, mapping


def load_cross_deferred(family1096_module: Any) -> dict[str, Any]:
    require(
        sha256_file(CROSS_DEFERRED_PATH)
        == EXPECTED_CROSS_DEFERRED_SHA256,
        "cross-family deferred proof drifted",
    )
    value = family1096_module.load_cross568_deferred()
    require(
        value["case_count"] == EXPECTED_CROSS_RECORD_ROWS
        and sum(len(case["branches"]) for case in value["cases"])
        == EXPECTED_CROSS_BRANCH_ROWS
        and value["correlation_proof"][
            "control_flow_and_selector_components_identical"
        ]
        is True
        and value["correlation_proof"][
            "selector_expression_source_identical"
        ]
        is True
        and value["correlation_proof"][
            "ordinal_branch_correlation_proven"
        ]
        is True,
        "cross-family branch correlation proof drifted",
    )
    return value


def analyze_union(
    *,
    official: Mapping[tuple[str, str], Mapping[str, Any]],
    family568: Mapping[str, Any],
    family1096: Mapping[str, Any],
    cross: Mapping[str, Any],
) -> dict[str, Any]:
    decisions568 = set(family568["family"]["decisions"])
    decisions1096 = set(family1096["family"]["decisions"])
    overlap = decisions568 & decisions1096
    union = decisions568 | decisions1096
    rows568 = {
        str(row["coordinate"]): row for row in family568["updated_rows"]
    }
    rows1096 = {
        str(row["coordinate"]): row for row in family1096["updated_rows"]
    }
    require(
        len(decisions568) == EXPECTED_FAMILY568_ROWS
        and len(decisions1096) == EXPECTED_FAMILY1096_ROWS
        and len(overlap) == EXPECTED_FAMILY_OVERLAP_ROWS
        and len(union) == EXPECTED_DECISION_ROWS
        and set(rows568) == decisions568
        and set(rows1096) == decisions1096,
        "family union count drifted",
    )
    translation_differences = {
        coordinate
        for coordinate in overlap
        if rows568[coordinate]["translation"]
        != rows1096[coordinate]["translation"]
    }
    selector568_owned = {
        str(case["coordinate568"]) for case in cross["cases"]
    }
    external1096_owned = {
        str(case["coordinate1096"]) for case in cross["cases"]
    }
    cross_coordinates = selector568_owned | external1096_owned
    require(
        len(translation_differences)
        == EXPECTED_FAMILY_TRANSLATION_DIFF_ROWS
        and translation_differences == selector568_owned
        and len(cross_coordinates) == EXPECTED_CROSS_COORDINATE_ROWS
        and cross_coordinates <= overlap,
        "cross-family translation conflict set drifted",
    )
    final_cross_map: dict[str, str] = {}
    for case in cross["cases"]:
        coordinate1096 = str(case["coordinate1096"])
        coordinate568 = str(case["coordinate568"])
        final_cross_map[coordinate1096] = str(
            case["candidate_left1096"]
        )
        final_cross_map[coordinate568] = str(case["candidate_left568"])
        require(
            rows568[coordinate568]["translation"]
            == final_cross_map[coordinate568],
            f"selector568 family did not own cross middle: {coordinate568}",
        )
    final_translation: dict[str, str] = {}
    preferred_rows: dict[str, Mapping[str, Any]] = {}
    for coordinate in union:
        if coordinate in rows568:
            preferred = rows568[coordinate]
        else:
            preferred = rows1096[coordinate]
        preferred_rows[coordinate] = preferred
        final_translation[coordinate] = str(preferred["translation"])
    final_translation.update(final_cross_map)
    actual_promotions = (
        set(family568["family"]["actual_promotions"])
        | set(family1096["family"]["actual_promotions"])
    )
    require(
        not (
            set(family568["family"]["actual_promotions"])
            & set(family1096["family"]["actual_promotions"])
        )
        and len(actual_promotions) == EXPECTED_ACTUAL_PROMOTION_ROWS,
        "cross-family actual-promotion union drifted",
    )
    renewals = union - actual_promotions
    require(
        len(renewals) == EXPECTED_VERIFICATION_RENEWAL_ROWS,
        "cross-family renewal count drifted",
    )
    overrides = {
        coordinate
        for coordinate, translation in final_translation.items()
        if translation
        != official[("pk_msggame", coordinate)].get("translation")
    }
    action_by_coordinate = {}
    for coordinate in union:
        if coordinate in actual_promotions:
            action = (
                "translation_override_and_runtime_promotion"
                if coordinate in overrides
                else "runtime_promotion"
            )
        else:
            action = (
                "translation_override_and_verification_renewal"
                if coordinate in overrides
                else "verification_renewal"
            )
        action_by_coordinate[coordinate] = action
    action_counts = dict(Counter(action_by_coordinate.values()))
    frozen_checks = (
        (EXPECTED_FAMILY_OVERLAP_SHA256, coordinate_digest(overlap),
         "family overlap"),
        (EXPECTED_FAMILY_TRANSLATION_DIFF_SHA256,
         coordinate_digest(translation_differences),
         "family translation conflict"),
        (EXPECTED_DECISION_SHA256, coordinate_digest(union),
         "decision union"),
        (EXPECTED_ACTUAL_PROMOTION_SHA256,
         coordinate_digest(actual_promotions), "actual promotion"),
        (EXPECTED_VERIFICATION_RENEWAL_SHA256,
         coordinate_digest(renewals), "renewal"),
        (EXPECTED_OVERRIDE_SHA256, coordinate_digest(overrides),
         "override"),
        (EXPECTED_CROSS_COORDINATE_SHA256,
         coordinate_digest(cross_coordinates), "cross coordinate"),
    )
    for expected, actual, label in frozen_checks:
        if expected is not None:
            require(actual == expected, f"{label} digest drifted")
    if EXPECTED_OVERRIDE_ROWS is not None:
        require(
            len(overrides) == EXPECTED_OVERRIDE_ROWS,
            "translation override count drifted",
        )
    if EXPECTED_ACTION_COUNTS is not None:
        require(
            action_counts == EXPECTED_ACTION_COUNTS,
            "cross-family action partition drifted",
        )
    return {
        "action_by_coordinate": action_by_coordinate,
        "action_counts": action_counts,
        "actual_promotions": actual_promotions,
        "cross_coordinates": cross_coordinates,
        "external1096_owned": external1096_owned,
        "final_cross_map": final_cross_map,
        "final_translation": final_translation,
        "overlap": overlap,
        "overrides": overrides,
        "preferred_rows": preferred_rows,
        "renewals": renewals,
        "selector568_owned": selector568_owned,
        "translation_differences": translation_differences,
        "union": union,
    }


def verify_family_assemblies(
    *,
    label: str,
    bundle: Mapping[str, Any],
    candidate_records: Mapping[tuple[int, int], Any],
    current_records: Mapping[tuple[int, int], Any],
    terminal_start: int,
) -> list[list[Any]]:
    chunks = bundle["chunks"]
    review0 = chunks[0]["module"].REVIEW
    terminal_candidate = review0.terminal_literals(candidate_records)
    terminal_current = review0.terminal_literals(current_records)
    manifest = []
    for chunk_id, chunk in enumerate(chunks):
        review = chunk["module"].REVIEW
        handoff = chunk.get("handoff")
        if handoff is None:
            handoff = load_json(chunk["module"].PRIVATE_HANDOFF_PATH)
        for row in handoff["site_reviews"]:
            if row["decision"] == "reject":
                continue
            site = str(row["site"])
            reviewed_left, reviewed_right = review.adjacent_literals(
                candidate_records, site
            )
            current_left, current_right = review.adjacent_literals(
                current_records, site
            )
            require(
                reviewed_left == row["reviewed_left_translation"],
                f"final union changed accepted caller: {label}/{site}",
            )
            for terminal in range(terminal_start, terminal_start + 7):
                reviewed = (
                    reviewed_left
                    + terminal_candidate[terminal]
                    + reviewed_right
                )
                current = (
                    current_left
                    + terminal_current[terminal]
                    + current_right
                )
                reviewed_lines = review.line_metrics(reviewed)
                current_lines = review.line_metrics(current)
                require(
                    len(reviewed_lines) == len(current_lines)
                    and review.current_relative_nonexpanding(
                        reviewed_lines, current_lines
                    ),
                    f"final union assembly expansion: "
                    f"{label}/{site}/{terminal}",
                )
                manifest.append(
                    [
                        label,
                        chunk_id,
                        site,
                        terminal,
                        sha256_bytes(reviewed.encode("utf-8")),
                        sha256_bytes(current.encode("utf-8")),
                        [
                            line["raw_g1n_width_px"]
                            for line in reviewed_lines
                        ],
                        [
                            line["raw_g1n_width_px"]
                            for line in current_lines
                        ],
                    ]
                )
    return manifest


def rebuild_and_verify(
    *,
    official_rows: Sequence[Mapping[str, Any]],
    union: Mapping[str, Any],
    family568: Mapping[str, Any],
    family1096: Mapping[str, Any],
    cross: Mapping[str, Any],
) -> dict[str, Any]:
    chunk_module = family1096["chunks"][0]["module"]
    base = chunk_module.BASE_AUDIT
    replacements = {
        chunk_module.parse_coordinate(str(row["coordinate"])):
            str(row["translation"])
        for row in official_rows
        if row.get("resource") == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    original = base.DEFAULT_PK_CURRENT.read_bytes()
    official_blob = base.rebuild_packed_with_literals(
        original, replacements
    )
    require(
        sha256_bytes(official_blob)
        == family1096["family1096_module"].EXPECTED_OFFICIAL_CANDIDATE_SHA256
        if "family1096_module" in family1096 else True,
        "official candidate drifted",
    )
    replacements.update(
        {
            chunk_module.parse_coordinate(coordinate): translation
            for coordinate, translation
            in union["final_translation"].items()
        }
    )
    final_blob = base.rebuild_packed_with_literals(original, replacements)
    final_sha = sha256_bytes(final_blob)
    if EXPECTED_FINAL_CANDIDATE_SHA256 is not None:
        require(
            final_sha == EXPECTED_FINAL_CANDIDATE_SHA256,
            "final cross-family candidate drifted",
        )
    candidate_records = base.records_from_blob(final_blob)
    current_records = family568["chunks"][0]["world"]["current_records"]
    manifest = verify_family_assemblies(
        label="selector568",
        bundle=family568,
        candidate_records=candidate_records,
        current_records=current_records,
        terminal_start=1951,
    )
    manifest.extend(
        verify_family_assemblies(
            label="selector1096",
            bundle=family1096,
            candidate_records=candidate_records,
            current_records=current_records,
            terminal_start=2581,
        )
    )
    require(
        len(manifest) == EXPECTED_ACCEPTED_ASSEMBLY_ROWS,
        "combined accepted assembly count drifted",
    )
    assembly_sha = canonical_sha256(manifest)
    if EXPECTED_ACCEPTED_ASSEMBLY_SHA256 is not None:
        require(
            assembly_sha == EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
            "combined accepted assembly digest drifted",
        )
    review = family1096["chunks"][0]["module"].REVIEW
    terminal1096_candidate = review.terminal_literals(candidate_records)
    terminal1096_current = review.terminal_literals(current_records)
    review568 = family568["chunks"][0]["module"].REVIEW
    terminal568_candidate = review568.terminal_literals(candidate_records)
    terminal568_current = review568.terminal_literals(current_records)
    cross_manifest = []
    for case in cross["cases"]:
        coordinate1096 = str(case["coordinate1096"])
        coordinate568 = str(case["coordinate568"])
        block1096, record1096, slot1096 = parse_coordinate(
            coordinate1096
        )
        block568, record568, slot568 = parse_coordinate(coordinate568)
        require(
            (block1096, record1096) == (block568, record568),
            "cross-family fragments must share one caller record",
        )
        current_literals = base.parse_record_literals(
            current_records[(block1096, record1096)]
        )
        current1096 = current_literals[slot1096].text
        current568 = current_literals[slot568].text
        for ordinal, branch in enumerate(case["branches"]):
            terminal1096 = 2581 + ordinal
            terminal568 = 1951 + ordinal
            reviewed = (
                union["final_translation"][coordinate1096]
                + terminal1096_candidate[terminal1096]
                + union["final_translation"][coordinate568]
                + terminal568_candidate[terminal568]
            )
            current = (
                current1096
                + terminal1096_current[terminal1096]
                + current568
                + terminal568_current[terminal568]
            )
            reviewed_lines = review.line_metrics(reviewed)
            current_lines = review.line_metrics(current)
            branch_checks = {
                "reviewed_body":
                    reviewed == branch["reviewed_assembly"],
                "current_body": current == branch["current_assembly"],
                "reviewed_metrics":
                    reviewed_lines == branch["reviewed_lines"],
                "current_metrics":
                    current_lines == branch["current_lines"],
                "line_count":
                    len(reviewed_lines) == len(current_lines),
                "nonexpanding":
                    review.current_relative_nonexpanding(
                        reviewed_lines, current_lines
                    ),
            }
            require(
                all(branch_checks.values()),
                f"cross-family full-record proof drifted: "
                f"{coordinate568}/{ordinal}/{branch_checks}/"
                f"reviewed={sha256_bytes(reviewed.encode('utf-8'))}/"
                f"expected={sha256_bytes(str(branch['reviewed_assembly']).encode('utf-8'))}/"
                f"current={sha256_bytes(current.encode('utf-8'))}/"
                f"expected_current={sha256_bytes(str(branch['current_assembly']).encode('utf-8'))}",
            )
            cross_manifest.append(
                [
                    coordinate1096,
                    coordinate568,
                    ordinal,
                    sha256_bytes(reviewed.encode("utf-8")),
                    sha256_bytes(current.encode("utf-8")),
                    [
                        line["raw_g1n_width_px"]
                        for line in reviewed_lines
                    ],
                    [
                        line["raw_g1n_width_px"]
                        for line in current_lines
                    ],
                ]
            )
    require(
        len(cross_manifest) == EXPECTED_CROSS_BRANCH_ROWS,
        "cross-family branch count drifted",
    )
    cross_branch_sha = canonical_sha256(cross_manifest)
    if EXPECTED_CROSS_BRANCH_SHA256 is not None:
        require(
            cross_branch_sha == EXPECTED_CROSS_BRANCH_SHA256,
            "cross-family branch digest drifted",
        )
    return {
        "accepted_assembly_manifest": manifest,
        "accepted_assembly_sha256": assembly_sha,
        "cross_branch_manifest": cross_manifest,
        "cross_branch_sha256": cross_branch_sha,
        "final_blob": final_blob,
        "final_sha256": final_sha,
        "official_blob": official_blob,
    }


def build_rows(
    *,
    official: Mapping[tuple[str, str], Mapping[str, Any]],
    union: Mapping[str, Any],
    candidate: Mapping[str, Any],
    audit_payload_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = []
    evidence_rows = []
    for coordinate in sorted(union["union"], key=parse_coordinate):
        predecessor = official[("pk_msggame", coordinate)]
        preferred = union["preferred_rows"][coordinate]
        translation = union["final_translation"][coordinate]
        family_membership = []
        if coordinate in union["family568_decisions"]:
            family_membership.append("selector568")
        if coordinate in union["family1096_decisions"]:
            family_membership.append("selector1096")
        evidence: dict[str, Any] = {
            "action": union["action_by_coordinate"][coordinate],
            "closure_binding": {
                "accepted_assembly_sha256":
                    candidate["accepted_assembly_sha256"],
                "audit_report_payload_sha256": audit_payload_sha256,
                "cross_branch_sha256":
                    candidate["cross_branch_sha256"],
                "decision_coordinate_sha256":
                    coordinate_digest(union["union"]),
                "final_candidate_sha256":
                    candidate["final_sha256"],
                "official_predecessor_sha256":
                    EXPECTED_OFFICIAL_PRIVATE_SHA256,
            },
            "coordinate": coordinate,
            "current81b4_rebase": {
                "actual_runtime_promotion":
                    coordinate in union["actual_promotions"],
                "official_runtime_review_before":
                    predecessor["runtime_review"],
            },
            "family_membership": family_membership,
            "method": METHOD,
            "per_row_game_playback_required": False,
            "predecessor_binding": {
                "checkpoint_sha256": EXPECTED_OFFICIAL_PRIVATE_SHA256,
                "row_sha256": canonical_sha256(predecessor),
            },
            "resource": "pk_msggame",
            "schema": EVIDENCE_SCHEMA,
            "source_family_row_sha256": canonical_sha256(preferred),
            "status": "verified",
            "translation_utf16le_sha256": sha256_text(translation),
        }
        if coordinate in union["cross_coordinates"]:
            role = (
                "selector1096_left"
                if coordinate in union["external1096_owned"]
                else "selector568_left"
            )
            evidence["sequential_multi_selector_resolution"] = {
                "cartesian_branch_matrix_required": False,
                "candidate_utf16le_sha256": sha256_text(translation),
                "cross_record_role": role,
                "ordinal_branch_correlation_proven": True,
                "selector_expression_source_identical": True,
                "seven_corresponding_register_branches_nonexpanding":
                    True,
            }
        row = copy.deepcopy(dict(preferred))
        is_runtime_promotion = (
            coordinate in union["actual_promotions"]
        )
        row["layout_review"] = (
            "runtime_verified"
            if (
                is_runtime_promotion
                or coordinate in union["cross_coordinates"]
            )
            else row.get("layout_review", "runtime_verified")
        )
        row["runtime_review"] = "verified"
        if is_runtime_promotion:
            row["scope_classification"] = "retranslated"
        row["semantic_review"] = "approved"
        row["translation"] = translation
        row[UPDATE_ACTION_FIELD] = union[
            "action_by_coordinate"
        ][coordinate]
        row["runtime_vm_verification"] = evidence
        if coordinate in union["overrides"]:
            row[OVERRIDE_FIELD] = {
                "schema": OVERRIDE_SCHEMA,
                "translation_utf16le_sha256": sha256_text(translation),
                "cross_full_record_owner":
                    coordinate in union["cross_coordinates"],
            }
        rows.append(row)
        evidence_rows.append(evidence)
    return rows, evidence_rows


def build_outputs() -> dict[str, Any]:
    inputs = load_families()
    family568 = inputs["family568"]
    family1096 = inputs["family1096"]
    family1096_module = inputs["family1096_module"]
    steam_path = Path(
        family568["chunks"][0]["module"].LIVE_STEAM_PK
    )
    steam_before = sha256_file(steam_path)
    require(
        steam_before == EXPECTED_STEAM_PK_SHA256,
        "live Steam PK archive drifted before build",
    )
    official_rows, official = load_official(family1096_module)
    cross = load_cross_deferred(family1096_module)
    union = analyze_union(
        official=official,
        family568=family568,
        family1096=family1096,
        cross=cross,
    )
    union["family568_decisions"] = set(
        family568["family"]["decisions"]
    )
    union["family1096_decisions"] = set(
        family1096["family"]["decisions"]
    )
    family1096_view = dict(family1096)
    family1096_view["family1096_official"] = official
    family1096_view["family1096_module"] = family1096_module
    candidate = rebuild_and_verify(
        official_rows=official_rows,
        union=union,
        family568=family568,
        family1096=family1096_view,
        cross=cross,
    )
    audit = seal_report(
        {
            "distribution_policy": {
                "private_decisions_stay_below_tmp": True,
                "private_dialogue_proof_stays_below_tmp": True,
                "tracked_report_contains_commercial_source_text": False,
                "tracked_report_contains_translated_dialogue_text": False,
            },
            "guards": {
                "cross_deferred_private_sha256":
                    EXPECTED_CROSS_DEFERRED_SHA256,
                "family1096_audit_sha256":
                    sha256_file(family1096_module.DEFAULT_AUDIT_OUTPUT),
                "family1096_decision_sha256":
                    sha256_file(family1096_module.DEFAULT_DECISION_OUTPUT),
                "family568_audit_sha256":
                    sha256_file(
                        inputs["family568_module"].DEFAULT_AUDIT_OUTPUT
                    ),
                "family568_decision_sha256":
                    sha256_file(
                        inputs["family568_module"].DEFAULT_DECISION_OUTPUT
                    ),
                "official_predecessor_private_sha256":
                    EXPECTED_OFFICIAL_PRIVATE_SHA256,
                "official_predecessor_public_sha256":
                    EXPECTED_OFFICIAL_PUBLIC_SHA256,
                "steam_archive_sha256_after": steam_before,
                "steam_archive_sha256_before": steam_before,
            },
            "method": METHOD,
            "proof": {
                "accepted_family_assembly_rows":
                    EXPECTED_ACCEPTED_ASSEMBLY_ROWS,
                "accepted_family_assembly_sha256":
                    candidate["accepted_assembly_sha256"],
                "all_family_assemblies_current_relative_raw_g1n_nonexpanding":
                    True,
                "cross_family_overlap_rows":
                    EXPECTED_FAMILY_OVERLAP_ROWS,
                "cross_family_overlap_sha256":
                    coordinate_digest(union["overlap"]),
                "cross_family_translation_difference_rows":
                    EXPECTED_FAMILY_TRANSLATION_DIFF_ROWS,
                "cross_family_translation_difference_sha256":
                    coordinate_digest(union["translation_differences"]),
                "sequential_multi_selector_resolution": {
                    "cartesian_branch_matrix_required": False,
                    "coordinate_rows": EXPECTED_CROSS_COORDINATE_ROWS,
                    "coordinate_sha256":
                        coordinate_digest(union["cross_coordinates"]),
                    "full_record_rows": EXPECTED_CROSS_RECORD_ROWS,
                    "ordinal_correlated_branch_rows":
                        EXPECTED_CROSS_BRANCH_ROWS,
                    "ordinal_correlated_branch_sha256":
                        candidate["cross_branch_sha256"],
                    "ordinal_correlated_branches_nonexpanding": True,
                    "selector_expression_source_identical": True,
                },
            },
            "result": {
                "actual_promotion_rows":
                    EXPECTED_ACTUAL_PROMOTION_ROWS,
                "actual_promotion_sha256":
                    coordinate_digest(union["actual_promotions"]),
                "decision_rows": EXPECTED_DECISION_ROWS,
                "decision_sha256":
                    coordinate_digest(union["union"]),
                "final_candidate_sha256":
                    candidate["final_sha256"],
                "pending_rows_after": EXPECTED_PENDING_AFTER,
                "pending_rows_before": EXPECTED_PENDING_BEFORE,
                "translation_override_rows": len(union["overrides"]),
                "translation_override_sha256":
                    coordinate_digest(union["overrides"]),
                "verification_renewal_rows":
                    EXPECTED_VERIFICATION_RENEWAL_ROWS,
                "verification_renewal_sha256":
                    coordinate_digest(union["renewals"]),
            },
            "schema": AUDIT_SCHEMA,
            "status": "PASS",
            "steam_write_performed": False,
        }
    )
    updated_rows, evidence_rows = build_rows(
        official=official,
        union=union,
        candidate=candidate,
        audit_payload_sha256=audit["guards"][
            "report_payload_sha256"
        ],
    )
    decision_content = canonical_jsonl(
        sorted(updated_rows, key=row_sort_key)
    )
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
                "final_candidate_sha256":
                    candidate["final_sha256"],
                "official_predecessor_private_sha256":
                    EXPECTED_OFFICIAL_PRIVATE_SHA256,
            },
            "guards": {
                "steam_archive_sha256_after": steam_before,
                "steam_archive_sha256_before": steam_before,
            },
            "method": METHOD,
            "result": {
                "actual_promotion_rows":
                    EXPECTED_ACTUAL_PROMOTION_ROWS,
                "pending_rows_after": EXPECTED_PENDING_AFTER,
                "pending_rows_before": EXPECTED_PENDING_BEFORE,
                "private_decision_rows": EXPECTED_DECISION_ROWS,
                "private_evidence_rows": EXPECTED_DECISION_ROWS,
                "translation_override_rows": len(union["overrides"]),
                "verification_renewal_rows":
                    EXPECTED_VERIFICATION_RENEWAL_ROWS,
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
    require(
        steam_after == steam_before == EXPECTED_STEAM_PK_SHA256,
        "live Steam PK archive changed during build",
    )
    return {
        "audit": audit,
        "audit_content": audit_content,
        "candidate": candidate,
        "cross": cross,
        "decision_content": decision_content,
        "evidence_content": evidence_content,
        "evidence_rows": evidence_rows,
        "family1096": family1096,
        "family568": family568,
        "promotion": promotion,
        "promotion_content": promotion_content,
        "steam_after": steam_after,
        "steam_before": steam_before,
        "union": union,
        "updated_rows": updated_rows,
    }


def output_hashes(
    bundle: Mapping[str, Any],
) -> tuple[str, str, str, str]:
    return (
        sha256_bytes(str(bundle["audit_content"]).encode("utf-8")),
        sha256_bytes(
            str(bundle["promotion_content"]).encode("utf-8")
        ),
        sha256_bytes(
            str(bundle["decision_content"]).encode("utf-8")
        ),
        sha256_bytes(
            str(bundle["evidence_content"]).encode("utf-8")
        ),
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
            "frozen cross-family output drifted",
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
            require(
                path.is_file(), f"missing frozen output: {path}"
            )
            require(
                path.read_text(encoding="utf-8") == content,
                f"cross-family output drifted: {path}",
            )
    else:
        for path, content in outputs:
            write_exact(path, str(content))
    print(
        "PASS "
        f"promoted={EXPECTED_ACTUAL_PROMOTION_ROWS} "
        f"renewed={EXPECTED_VERIFICATION_RENEWAL_ROWS} "
        f"overrides={len(bundle['union']['overrides'])} "
        f"pending={EXPECTED_PENDING_AFTER} "
        f"hashes={output_hashes(bundle)} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
