#!/usr/bin/env python3
"""Consolidate the two selector-730 reviews on the post-selector562 state."""

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

SCAFFOLD_PATH = WORKSTREAM / "build_pk_selector562_consolidated_closure_v1.py"
EXPECTED_SCAFFOLD_SHA256 = (
    "138AE0E57F61A577715634BB9856F5EB33B69718E3EE8F9158C72BAAD6409817"
)
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector730_assignment_v1.py"
ASSIGNMENT_PRIVATE_PATH = DIALOGUE_TMP / "pk_selector730_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC_DIR / "pk_selector730_assignment_coverage.v1.json"
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector562_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_DECISIONS_PATH = (
    SEMANTIC_TMP / "pk_selector562_consolidated_closure_decisions.private.v1.jsonl"
)
CHUNK_BUILDERS = tuple(
    WORKSTREAM / f"build_pk_selector730_chunk{chunk}_review_v1.py"
    for chunk in range(2)
)
CHUNK_PUBLIC = tuple(
    PUBLIC_DIR / f"pk_selector730_chunk{chunk}_review.source_free.v1.json"
    for chunk in range(2)
)
CHUNK_DECISIONS = tuple(
    SEMANTIC_TMP / f"pk_selector730_chunk{chunk}_review_decisions.private.v1.jsonl"
    for chunk in range(2)
)
CHUNK_EVIDENCE = tuple(
    DIALOGUE_TMP / f"pk_selector730_chunk{chunk}_review_evidence.private.v1.json"
    for chunk in range(2)
)
SHARED_CARTESIAN_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector730_shared_cartesian_manifest_v1.py"
)
SHARED_CARTESIAN_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "pk_selector730_shared_cartesian_assembly_manifest.private.v1.json"
)
SHARED_CARTESIAN_PUBLIC_PATH = (
    PUBLIC_DIR / "pk_selector730_shared_cartesian_assembly_coverage.v1.json"
)

PRIVATE_DECISIONS_OUTPUT = (
    SEMANTIC_TMP / "pk_selector730_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP / "pk_selector730_consolidated_closure_evidence.private.v1.json"
)
PUBLIC_COVERAGE_OUTPUT = (
    PUBLIC_DIR / "pk_selector730_consolidated_closure_coverage.v1.json"
)
PUBLIC_PROMOTION_OUTPUT = (
    PUBLIC_DIR / "pk_selector730_consolidated_closure_promotion.v1.json"
)

EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "assignment_builder":
        "94E9846279014E431832E232509B1C495BEE3D9EFEF01B8D8EBAB687D0968AA8",
    "assignment_private":
        "D9554CC8E6BED91EB9141CFC11F142E389868565AFC7B82B230FC9F931DB4781",
    "assignment_public":
        "07EA6FE891F17C7E4CF22C6C42625D1E224FF606524A2683ED0CA58C767CD454",
    "official_ledger":
        "8E31995689359D5F8DD1F23FC7A894C07AC8BBB3C08EF2B87651E6E3E8B1086A",
    "predecessor_decisions":
        "51CA681BCE819F41B1D7B69BE6AD906BFCD519BC463BF8EEBAA08DACA5C5BD26",
    "chunk0_builder":
        "C35CC0B6201EB67F8EA7EEBAB4FA16D3377F55C3D89F2999EF5CB33CF839D78F",
    "chunk0_public":
        "FBBE5314BF89B94EC41F1BA102C1DA02DCA4E7AD000D5996F55FA5C0A6F0673C",
    "chunk0_decisions":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "chunk0_evidence":
        "E9E0D6F66B630C89DF5741809D4452AE3D6A41DC95FA8F66ED7D4715EE5999BF",
    "chunk1_builder":
        "81D2B63B385C38159BB8E6C1407E06B8B5AB2B09500676ECF4C2B561B5147185",
    "chunk1_public":
        "F13FF98456662B6AAE56D0B7022E4C089191D1FBEF8B97060EF2B50E65993D38",
    "chunk1_decisions":
        "9569A9658FE235C60327A01F957EA79B4A3151AA1346242B7DCFEF5C4A780702",
    "chunk1_evidence":
        "6F3A8F0D96B70D101416796C23E9BF42EEFE5552C03E242C23022950247A4BFD",
}
EXPECTED_SHARED_CARTESIAN_SHA256 = {
    "builder":
        "0F0FF85083A76AF97AF6DA6ECFD5991A1681CBC28FA46C4E847C01D38DB39C32",
    "private":
        "BB00FFACC84CE778AFCEFB5E531B23BDA8BB03CFEE06E42DC885BC164314C173",
    "public":
        "F9F2F82231DD417F397EE05B23C4AFF7FB60056865ABF22B87B99CCFD58A4DE1",
}
EXPECTED_SHARED_CARTESIAN_GUARDS = {
    "cartesian_roots":
        "E49EE9068EA4F6F0958182750D260108ABBF563F091EFB83D469D3EC6993A9EF",
    "terminal_families":
        "4515B68AF73D7CF272376F21768E4939514A61CE00642F452E64A57466A4D107",
}
EXPECTED_CHUNK_ROWS = (0, 3)
EXPECTED_CHUNK_SITES = (21, 20)
EXPECTED_CHUNK_SAME_GAP_ROOTS = (19, 18)
EXPECTED_CHUNK_CARTESIAN_BRANCHES = (931, 882)
EXPECTED_CHUNK_BLOCKED_ROOTS = (8, 9)
EXPECTED_CHUNK_BLOCKED_ROWS = (12, 22)
EXPECTED_DECISION_ROWS = 3
EXPECTED_DECISION_ROOTS = 1
EXPECTED_PROMOTIONS = 3
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 1
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 2,
    "translation_override_and_runtime_promotion": 1,
}
EXPECTED_PENDING_BEFORE = 6_181
EXPECTED_PENDING_AFTER = 6_178
EXPECTED_REVIEWED_SITES = 41
EXPECTED_CANDIDATE_SITE_SHA256 = (
    "97C3B98B672FF969B99680AB35AA80D77A82726196BC53C1C02BD1813BC3C877"
)
EXPECTED_SOURCE_SITES = 46
EXPECTED_SOURCE_SITE_SHA256 = (
    "A859360269D58C7B7FF77E44BB33AF739BBBE59E2E2592981598C1AB62ED8481"
)
EXPECTED_SOURCE_ONLY_SITES = 5
EXPECTED_SOURCE_ONLY_SHA256 = (
    "AFF05F3C748B8B3A4044013477DAEC82615EAAC0CBF4526450BA0F38B3D0A586"
)
EXPECTED_PREDECESSOR_OVERLAPS = 0
EXPECTED_PREDECESSOR_SUPERSESSIONS = 0
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "B7CBFA388BDD50F60CD5EEF88A63B62D357475925A0A3AA6D7DCA1A191607815"
)
EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256 = (
    "5445CD4A9C9515A8732446DA397D0FF0BB66E657A17C14BEDC374CCC745CDF76"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "B5B654EB01F84F558645B732B7E7A11DCA0B770887050E718B301A30AD78E6A5"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "0601646BF63BA7CED310F7913DCC3BFFDDE26F9124FB459B99C8604F8147D07F"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "BE3648C0B9ABD158FB4ADFCACECF53AE3B340174A818EC580B953D3121AA088B"
)
EXPECTED_EMPTY_CONTEXT_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_OUTPUT_SHA256: dict[str, str | None] = {
    "private_decisions":
        "A56DA1B7C3465EF9CA1640A059F7EE46EC73B0C4C95B2849551CDA34A91A8DDE",
    "private_evidence":
        "070FA56F5F230A46B0A1A9BC1544FE676A5D93886A94686A5D2463D134399BDD",
    "public_coverage":
        "E10A7B7E20F3259966F10B9787907124E3F72D910AA1D9E5FDCDC57616898186",
    "public_promotion":
        "55B523C11A66EB8BB393FD562C22DE1F1DE80F723E84FF128EC14EC858A05FBD",
    "final_candidate":
        "5D4CDF1CEB8C733B0E22C7AA6185D9FF6C5C4C500176E99A6AACB3D89F7E0140",
    "decision_coordinates":
        "A7AA97F0E5BE83EF88CE8F20387BBE589AC4AA3D2D08ED3A5260F2ED528B8D0E",
    "promotion_coordinates":
        "A7AA97F0E5BE83EF88CE8F20387BBE589AC4AA3D2D08ED3A5260F2ED528B8D0E",
    "renewal_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override_coordinates":
        "EF6126175171237F1995DB709FD27ABFC7FB7583D1F250F6011CDB9AD094BC95",
    "predecessor_overlap_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "predecessor_supersession_coordinates":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "source_only_proof":
        "880F933EBDE834C2A459973B36FB00F027B9F067774A683D592FA692D6E0BDEC",
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCAFFOLD = load_module(SCAFFOLD_PATH, "selector730_closure_scaffold")
WRAPPER = SCAFFOLD.WRAPPER
ASSIGNMENT = load_module(ASSIGNMENT_BUILDER_PATH, "selector730_closure_input")
BASE = WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = SCAFFOLD.configure_base


def validate_chunk_evidence(
    assignment: Mapping[str, Any],
    chunk_rows: Sequence[Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    evidence = [BASE.load_json(path) for path in CHUNK_EVIDENCE]
    assigned_chunks = assignment["chunks"]
    same_gap_roots = {
        str(row["root"]) for row in assignment["same_gap_root_atoms"]
    }
    all_sites: set[str] = set()
    all_blocked_roots: set[str] = set()
    for chunk_id, rows in enumerate(chunk_rows):
        assigned = assigned_chunks[chunk_id]
        chunk_evidence = evidence[chunk_id]
        assigned_sites = set(map(str, assigned["sites"]))
        assigned_roots = set(map(str, assigned["roots"]))
        decision_coordinates = {str(row["coordinate"]) for row in rows}
        decision_roots = {
            BASE.coordinate_root(coordinate)
            for coordinate in decision_coordinates
        }
        counts = chunk_evidence["counts"]
        proof = chunk_evidence["proof"]
        BASE.require(
            len(rows) == EXPECTED_CHUNK_ROWS[chunk_id]
            and len(decision_coordinates) == len(rows),
            f"chunk{chunk_id} decision count drifted",
        )
        BASE.require(
            len(assigned_sites) == EXPECTED_CHUNK_SITES[chunk_id]
            and len(assigned_roots) == EXPECTED_CHUNK_SITES[chunk_id]
            and (
                (
                    chunk_id == 0
                    and chunk_evidence["assignment"]["chunk_id"] == chunk_id
                    and chunk_evidence["assignment"]["site_count"]
                        == EXPECTED_CHUNK_SITES[chunk_id]
                    and counts["assigned_sites"]
                        == EXPECTED_CHUNK_SITES[chunk_id]
                    and counts["assigned_roots"]
                        == EXPECTED_CHUNK_SITES[chunk_id]
                )
                or (
                    chunk_id == 1
                    and counts["chunk_sites"]
                        == EXPECTED_CHUNK_SITES[chunk_id]
                    and counts["chunk_roots"]
                        == EXPECTED_CHUNK_SITES[chunk_id]
                )
            ),
            f"chunk{chunk_id} assignment coverage drifted",
        )
        BASE.require(
            decision_roots <= assigned_roots
            and not decision_roots & same_gap_roots,
            f"chunk{chunk_id} decision escaped or split a same-gap root",
        )
        if chunk_id == 0:
            references = chunk_evidence["chunk_cartesian_references"]
            reference_roots = {str(row["root"]) for row in references}
            blocked = chunk_evidence["root_reviews"]
            blocked_roots = {str(row["root"]) for row in blocked}
            blocked_coordinates = {
                str(coordinate)
                for row in blocked
                for coordinate in row["blocked_pending_coordinates"]
            }
            BASE.require(
                reference_roots == assigned_roots & same_gap_roots
                and len(reference_roots)
                    == EXPECTED_CHUNK_SAME_GAP_ROOTS[chunk_id]
                and sum(int(row["branch_count"]) for row in references)
                    == EXPECTED_CHUNK_CARTESIAN_BRANCHES[chunk_id]
                and all(int(row["branch_count"]) == 49 for row in references),
                f"chunk{chunk_id} Cartesian reference drifted",
            )
            BASE.require(
                blocked_roots <= reference_roots
                and len(blocked_roots)
                    == EXPECTED_CHUNK_BLOCKED_ROOTS[chunk_id]
                and len(blocked_coordinates)
                    == EXPECTED_CHUNK_BLOCKED_ROWS[chunk_id]
                and all(
                    row["disposition"] == "blocked_atomic_root"
                    and row["shared_manifest_reused"]
                    and int(row["branch_count"]) == 49
                    for row in blocked
                ),
                f"chunk{chunk_id} atomic block disposition drifted",
            )
            BASE.require(
                counts["decision_rows"] == EXPECTED_CHUNK_ROWS[chunk_id]
                and counts["source_only_action_count"] == 0
                and counts["terminal_decision_rows"] == 0
                and counts["terminal_pending_rows"] == 7
                and counts["shared_cartesian_roots"]
                    == EXPECTED_CHUNK_SAME_GAP_ROOTS[chunk_id]
                and counts["shared_cartesian_branches_reused"]
                    == EXPECTED_CHUNK_CARTESIAN_BRANCHES[chunk_id]
                and proof["cartesian_branches_recomputed"] == 0
                and proof[
                    "owned_or_prior_evidence_automatic_promotion_count"
                ] == 0
                and proof["same_gap_partial_pass_authorized"] is False
                and proof["shared_manifest_reused"] is True
                and proof["terminal_rows_read_only"] is True,
                f"chunk{chunk_id} automatic or read-only guard drifted",
            )
        else:
            pending_reviews = chunk_evidence["pending_root_reviews"]
            blocked = [
                row for row in pending_reviews
                if str(row["decision"]).startswith("blocked_")
            ]
            blocked_roots = {str(row["root"]) for row in blocked}
            BASE.require(
                assigned_roots & same_gap_roots >= blocked_roots
                and len(assigned_roots & same_gap_roots)
                    == EXPECTED_CHUNK_SAME_GAP_ROOTS[chunk_id]
                and len(blocked_roots)
                    == EXPECTED_CHUNK_BLOCKED_ROOTS[chunk_id]
                and len(chunk_evidence["blocked_pending_coordinates"])
                    == EXPECTED_CHUNK_BLOCKED_ROWS[chunk_id]
                and counts["decision_rows"] == EXPECTED_CHUNK_ROWS[chunk_id]
                and counts["source_only_actions"] == 0
                and counts["terminal_read_only_rows"] == 7
                and counts["same_gap_total_roots"]
                    == EXPECTED_CHUNK_SAME_GAP_ROOTS[chunk_id]
                and counts["same_gap_total_branches_reused"]
                    == EXPECTED_CHUNK_CARTESIAN_BRANCHES[chunk_id]
                and proof["cartesian_branches_recomputed"] == 0
                and proof["owned_overlap_automatic_promotion_count"] == 0
                and proof[
                    "prior_pending_evidence_automatic_promotion_count"
                ] == 0
                and proof["template_evidence_automatic_promotion_count"] == 0
                and proof["same_gap_root_atomicity_preserved"] is True
                and proof["cartesian_evidence_reused"] is True
                and proof["terminal_records_read_only"] is True,
                f"chunk{chunk_id} atomic or automatic guard drifted",
            )
        BASE.require(not all_sites & assigned_sites, "chunk sites overlap")
        all_sites.update(assigned_sites)
        all_blocked_roots.update(blocked_roots)
    BASE.require(
        len(all_sites) == EXPECTED_REVIEWED_SITES
        and BASE.site_digest(all_sites) == EXPECTED_CANDIDATE_SITE_SHA256
        and len(all_blocked_roots) == sum(EXPECTED_CHUNK_BLOCKED_ROOTS),
        "selector730 review or blocked-root union drifted",
    )
    return evidence


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.METHOD = (
        "post_selector562_selector730_two_chunk_single_coordinate_union_"
        "with_shared_cartesian_atomic_block_and_read_only_terminal_guards"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector730-consolidated-closure-decision.private.v1"
    )
    BASE.PRIVATE_EVIDENCE_SCHEMA = (
        "nobu16.kr.pk-selector730-consolidated-closure-evidence.private.v1"
    )
    BASE.PUBLIC_COVERAGE_SCHEMA = (
        "nobu16.kr.pk-selector730-consolidated-closure-coverage.v1"
    )
    BASE.PUBLIC_PROMOTION_SCHEMA = (
        "nobu16.kr.pk-selector730-consolidated-closure-promotion.v1"
    )
    BASE.UPDATE_ACTION_FIELD = "selector730_consolidated_update_action"
    BASE.ASSIGNMENT_PRIVATE_SCHEMA = (
        "nobu16.kr.pk-selector730-assignment.private.v1"
    )
    BASE.validate_chunk_evidence = validate_chunk_evidence


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
        and tuple(row["target"]) == (0, 730)
        and int(row["gap_id"]) == gap_id
        and int(row["offset"]) == offset
    ]
    BASE.require(bool(rows) is expected, f"selector-730 site drifted: {site}")


def transform_outputs(outputs: dict[Path, bytes]) -> dict[Path, bytes]:
    for path in (PUBLIC_COVERAGE_OUTPUT, PUBLIC_PROMOTION_OUTPUT):
        payload = json.loads(outputs[path].decode("utf-8"))
        payload["inputs"].update({
            "shared_cartesian_builder_sha256":
                EXPECTED_SHARED_CARTESIAN_SHA256["builder"],
            "shared_cartesian_private_sha256":
                EXPECTED_SHARED_CARTESIAN_SHA256["private"],
            "shared_cartesian_public_sha256":
                EXPECTED_SHARED_CARTESIAN_SHA256["public"],
        })
        payload["guards"].update({
            "shared_cartesian_roots_sha256":
                EXPECTED_SHARED_CARTESIAN_GUARDS["cartesian_roots"],
            "shared_terminal_families_sha256":
                EXPECTED_SHARED_CARTESIAN_GUARDS["terminal_families"],
        })
        payload["guards"].pop("payload_without_guard_sha256", None)
        payload["guards"]["payload_without_guard_sha256"] = (
            BASE.canonical_sha256(payload)
        )
        BASE.assert_source_free(payload)
        outputs[path] = BASE.serialized_json(payload)

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
        "all_41_candidate_sites_reviewed": True,
        "confirmed_non_display_rows_untouched": True,
        "prior_owned_and_template_automatic_promotion_count_zero": True,
        "same_gap_37_roots_atomic": True,
        "same_gap_17_pending_roots_blocked": True,
        "shared_cartesian_1813_branches_reused": True,
        "shared_cartesian_branches_recomputed_zero": True,
        "source_only_5_absent_from_current_and_candidate": True,
        "source_only_action_count_zero": True,
        "terminal_records_absent_from_decisions": True,
        "terminal_rows_pending_and_read_only": True,
    })
    coverage["result"].update({
        "blocked_same_gap_pending_roots": 17,
        "blocked_same_gap_pending_rows": 34,
        "shared_cartesian_branches": 1_813,
        "shared_cartesian_roots": 37,
    })
    coverage["guards"].pop("payload_without_guard_sha256", None)
    coverage["guards"]["payload_without_guard_sha256"] = (
        BASE.canonical_sha256(coverage)
    )
    BASE.assert_source_free(coverage)
    outputs[PUBLIC_COVERAGE_OUTPUT] = BASE.serialized_json(coverage)
    return outputs


def terminal_values(records: Mapping[tuple[int, int], Any]) -> list[str]:
    values = []
    for record_id in range(2140, 2147):
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


def validate_shared_cartesian() -> dict[str, Any]:
    for label, path in {
        "builder": SHARED_CARTESIAN_BUILDER_PATH,
        "private": SHARED_CARTESIAN_PRIVATE_PATH,
        "public": SHARED_CARTESIAN_PUBLIC_PATH,
    }.items():
        BASE.require(
            path.is_file()
            and BASE.sha256_file(path) == EXPECTED_SHARED_CARTESIAN_SHA256[label],
            f"shared Cartesian input drifted: {label}",
        )
    private = BASE.load_json(SHARED_CARTESIAN_PRIVATE_PATH)
    public = BASE.load_json(SHARED_CARTESIAN_PUBLIC_PATH)
    rows = private["cartesian_roots"]
    BASE.require(
        len(rows) == 37
        and sum(int(row["branch_count"]) for row in rows) == 1_813
        and all(
            int(row["branch_count"]) == 49
            and int(row["control_count"]) == 2
            for row in rows
        )
        and len(private["scope"]["pending_same_gap_coordinates"]) == 34
        and private["guards"]["cartesian_roots_canonical_sha256"]
            == EXPECTED_SHARED_CARTESIAN_GUARDS["cartesian_roots"]
        and private["guards"]["terminal_families_canonical_sha256"]
            == EXPECTED_SHARED_CARTESIAN_GUARDS["terminal_families"]
        and public["scope"]["pending_same_gap_roots"] == 17
        and public["assignment_partition"]["status"] == "validated"
        and public["proof"]["semantic_decision_rows"] == 0
        and public["proof"]["terminal_records_read_only"] is True,
        "shared Cartesian contract drifted",
    )
    return private


def validate_wrapper_invariants(outputs: Mapping[Path, bytes]) -> None:
    official = BASE.load_jsonl(OFFICIAL_LEDGER_PATH)
    decisions = [
        json.loads(line)
        for line in outputs[PRIVATE_DECISIONS_OUTPUT]
        .decode("utf-8", errors="strict")
        .splitlines()
        if line
    ]
    assignment = BASE.load_json(ASSIGNMENT_PRIVATE_PATH)
    shared = validate_shared_cartesian()
    decision_keys = {
        (str(row["resource"]), str(row["coordinate"])) for row in decisions
    }
    decision_roots = {
        BASE.coordinate_root(str(row["coordinate"])) for row in decisions
    }
    terminal_roots = {f"0:{record_id}" for record_id in range(2140, 2147)}
    same_gap_roots = {
        str(row["root"]) for row in assignment["same_gap_root_atoms"]
    }
    confirmed = {
        (str(row["resource"]), str(row["coordinate"]))
        for row in official
        if row.get("scope_classification") == "confirmed_non_display"
    }
    candidate, current, source, contexts, _pending = (
        ASSIGNMENT.ASSIGNMENT.RECORDS.load_records()
    )
    BASE.require(
        len(official) == 52_803
        and len(confirmed) == EXPECTED_CONFIRMED_NON_DISPLAY
        and not decision_keys & confirmed,
        "selector730 touched confirmed-non-display rows",
    )
    BASE.require(
        not decision_roots & terminal_roots
        and not decision_roots & same_gap_roots
        and same_gap_roots
            == {str(row["root"]) for row in shared["cartesian_roots"]},
        "terminal or same-gap root entered the decision union",
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
        and all(
            row["runtime_review"] == "pending"
            for row in assignment["shared_terminal_ownership"][
                "terminal_manifest"
            ]
        )
        and assignment["shared_terminal_ownership"][
            "automatic_status_promotion_authorized"
        ] is False,
        "selector730 terminal contract drifted",
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
    chunk_evidence = [BASE.load_json(path) for path in CHUNK_EVIDENCE]
    BASE.require(
        int(chunk_evidence[0]["counts"][
            "shared_cartesian_branches_reused"
        ])
        + int(chunk_evidence[1]["counts"][
            "same_gap_total_branches_reused"
        ]) == 1_813
        and sum(
            int(row["proof"]["cartesian_branches_recomputed"])
            for row in chunk_evidence
        ) == 0
        and len(chunk_evidence[0]["terminal_manifest"]) == 7
        and all(
            terminal["runtime_review"] == "pending"
            and terminal["decision_authorized"] is False
            for terminal in chunk_evidence[0]["terminal_manifest"]
        ),
        "chunk Cartesian or terminal reuse drifted",
    )
    BASE.require(
        chunk_evidence[1]["counts"]["terminal_read_only_rows"] == 7
        and chunk_evidence[1]["proof"]["shared_terminal_modified"] is False
        and chunk_evidence[1]["proof"][
            "terminal_automatic_promotion_count"
        ] == 0
        and chunk_evidence[1]["proof"]["terminal_records_read_only"] is True,
        "chunk1 terminal read-only contract drifted",
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
        "selector562 closure scaffold drifted",
    )
    validate_shared_cartesian()
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
                f"selector730 closure output drifted: {path}",
            )
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(json.dumps({
        "decision_rows": EXPECTED_DECISION_ROWS,
        "pending_after": EXPECTED_PENDING_AFTER,
        "promotions": EXPECTED_PROMOTIONS,
        "shared_cartesian_branches_reused": 1_813,
        "source_only_actions": 0,
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
