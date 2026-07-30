#!/usr/bin/env python3
"""Validate selector-238 chunk 0 and emit its source-free checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
PUBLIC = WORKSTREAM / "public"

ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector238_assignment_v1.py"
ASSIGNMENT_PATH = TMP / "pk_selector238_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC / "pk_selector238_assignment_coverage.v1.json"
PRIVATE_GENERATOR_PATH = (
    TMP / "build_pk_selector238_chunk0_private_review_v1.py"
)
PRIVATE_DECISIONS_PATH = (
    TMP / "semantic_overrides"
    / "pk_selector238_chunk0_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    TMP / "pk_selector238_chunk0_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    PUBLIC / "pk_selector238_chunk0_review.source_free.v1.json"
)

SCHEMA = "nobu16.kr.pk-selector238-chunk0-review.source-free.v1"
METHOD = "post_selector730_selector238_chunk0_one_pass_semantic_review"
EXPECTED_SHA256 = {
    "assignment_builder":
        "4C09CA6AAC9DBE0EBB83E8A855C20724721AAF1875BE0C12B45ACDA9D1AEFE40",
    "assignment_private":
        "3B8629AC3DF5E18FEA92D82EB97D0E6D87870509E1C986BEFC3069050FF6D0C8",
    "assignment_public":
        "B44358FE6CC6EAD85972255F8D360EF5B6A0B1AB2D935DBCA4CC7F4D490ACE30",
    "official_ledger":
        "9F6BD587F6EC92CD00A2E2AF9FD9E07A8B6A71405272F0D79A515C3405617C5C",
    "private_generator":
        "41EAA59E6A34A7F2C9438B6A76C3F1B975634D2D0D5A863E7866158C3CCAC1B1",
    "private_decisions":
        "86EC96ED24C66CD970A697C9E41E5495FEC7043A22867D11D92F772820CFCBDB",
    "private_evidence":
        "BE00AE4080DB005BF4C5D78320288A618473EA126789ACBF517D0DF500A9576B",
    "official_candidate":
        "5D4CDF1CEB8C733B0E22C7AA6185D9FF6C5C4C500176E99A6AACB3D89F7E0140",
    "reviewed_candidate":
        "B3BDD6CA1A992AAB31A68EEF20EE8A89B0F66C2F453F4F52292AE0B8DD8C36CC",
    "live_steam":
        "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
    "terminal_candidate":
        "464E10C8A1DCFEF1B73492494A92601C01AC45FADE7F9D63D9691A931208F706",
    "terminal_current":
        "EED5D974C2CCA3E2C2186AEDC0DF3A480C95062942D55ECC3E966B8B94207B5E",
    "terminal_source":
        "E7D01ED5F17258F69B7A74858EC5D442FF39E9F2551426F903AAF83E1D6AA8ED",
}
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 1,
    "translation_override_and_runtime_promotion": 10,
}
EXPECTED_PUBLIC_SHA256 = (
    "D22CEFEB47215C6F8F8AF48665DB13C89F94D9AFAD9430F010B27177FC99461B"
)


class ReviewError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


WRAPPER = load_module(
    ASSIGNMENT_BUILDER_PATH, "selector238_chunk0_review_assignment"
)
WRAPPER.configure()
ASSIGNMENT = WRAPPER.ASSIGNMENT
RANKING = WRAPPER.RANKING
ENGINE = WRAPPER.ASSIGNMENT.ENGINE
OFFICIAL_LEDGER_PATH = WRAPPER.RANKING_WRAPPER.DEFAULT_LEDGER
TERMINALS = tuple(WRAPPER.TERMINALS)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le", errors="strict"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def serialized(value: Any) -> bytes:
    return canonical_bytes(value) + b"\n"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"object expected: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    require(all(isinstance(row, dict) for row in rows), "JSONL shape drifted")
    return rows


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 3, f"bad coordinate: {value}")
    return parts  # type: ignore[return-value]


def literal_text(
    records: Mapping[tuple[int, int], Any],
    coordinate: str,
) -> str:
    block_id, record_id, literal_id = parse_coordinate(coordinate)
    values = ENGINE.parse_record_literals(records[(block_id, record_id)])
    require(literal_id < len(values), f"literal absent: {coordinate}")
    return values[literal_id].text


def terminal_digest(
    records: Mapping[tuple[int, int], Any],
) -> str:
    values = []
    for record_id in TERMINALS:
        literals = ENGINE.parse_record_literals(records[(0, record_id)])
        require(len(literals) == 1, "terminal shape drifted")
        values.append(literals[0].text)
    return sha256_bytes("\0".join(values).encode("utf-8"))


def assert_source_free(value: Any) -> None:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            encoded,
        ) is None,
        "public report contains CJK",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", encoded) is None,
        "public report contains coordinates",
    )


def validate_inputs() -> tuple[
    dict[str, Any], dict[str, Any], list[dict[str, Any]]
]:
    immutable = {
        ASSIGNMENT_BUILDER_PATH: EXPECTED_SHA256["assignment_builder"],
        ASSIGNMENT_PATH: EXPECTED_SHA256["assignment_private"],
        ASSIGNMENT_PUBLIC_PATH: EXPECTED_SHA256["assignment_public"],
        OFFICIAL_LEDGER_PATH: EXPECTED_SHA256["official_ledger"],
        PRIVATE_GENERATOR_PATH: EXPECTED_SHA256["private_generator"],
        PRIVATE_DECISIONS_PATH: EXPECTED_SHA256["private_decisions"],
        PRIVATE_EVIDENCE_PATH: EXPECTED_SHA256["private_evidence"],
    }
    for path, expected in immutable.items():
        require(
            path.is_file() and sha256_file(path) == expected,
            f"immutable input drifted: {path}",
        )
    return (
        load_json(ASSIGNMENT_PATH),
        load_json(PRIVATE_EVIDENCE_PATH),
        load_jsonl(PRIVATE_DECISIONS_PATH),
    )


def validate_assignment(
    assignment: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> tuple[set[str], set[str]]:
    chunk = assignment["chunks"][0]
    require(
        (
            chunk["site_count"],
            chunk["root_count"],
            chunk["pending_root_count"],
            chunk["pending_row_upper_bound"],
            chunk["owned_overlap_root_count"],
            chunk["prior_assembly_evidence_root_count"],
            chunk["prior_assembly_evidence_pending_row_count"],
            chunk["template_root_count"],
            chunk["workload_weight"],
        ) == (14, 14, 7, 14, 4, 6, 9, 0, 271),
        "chunk assignment metrics drifted",
    )
    accepted = {
        str(row["coordinate"])
        for row in load_jsonl(PRIVATE_DECISIONS_PATH)
    }
    blocked = {
        coordinate
        for coordinate in chunk["pending_coordinates"]
        if coordinate not in accepted
    }
    require(
        len(accepted) == 11
        and len(blocked) == 3
        and evidence["counts"]["accepted_pending_rows"] == 11
        and evidence["counts"]["blocked_pending_rows"] == 3
        and assignment["source_only_repair"]["action_count"] == 0
        and len(assignment["source_only_repair"]["sites"]) == 1
        and not assignment["prior_pending_evidence"][
            "automatic_status_promotion_authorized"
        ]
        and not assignment["shared_terminal_ownership"][
            "automatic_status_promotion_authorized"
        ],
        "pending partition or protection guard drifted",
    )
    return accepted, blocked


def validate_decisions(
    decisions: Sequence[Mapping[str, Any]],
    accepted: set[str],
) -> dict[str, str]:
    require(
        len(decisions) == 11
        and {str(row["coordinate"]) for row in decisions} == accepted
        and Counter(str(row["action"]) for row in decisions)
        == Counter(EXPECTED_ACTION_COUNTS),
        "decision partition drifted",
    )
    overrides = {}
    for row in decisions:
        body = str(row["reviewed_translation"])
        require(
            row.get("resource") == "pk_msggame"
            and row.get("fresh_semantic_review") == "approved"
            and row.get("historical_factuality_review") == "approved"
            and row.get("speaker_tone_review") == "approved"
            and row.get("runtime_review") == "verified"
            and row.get("layout_review")
            == "current_relative_raw_g1n_nonexpanding"
            and row.get("root_rewrite_attempt_count") == 1
            and utf16le_sha256(body) == row.get("reviewed_utf16le_sha256"),
            "decision semantic/layout contract drifted",
        )
        if str(row["action"]).startswith("translation_override"):
            overrides[str(row["coordinate"])] = body
    require(len(overrides) == 10, "override count drifted")
    return overrides


def build_report() -> dict[str, Any]:
    assignment, evidence, decisions = validate_inputs()
    require(
        evidence["schema"]
        == "nobu16.kr.pk-selector238-chunk0-review-evidence.private.v1"
        and evidence["method"] == METHOD
        and evidence["proof"][
            "conservative_runtime_assembly_superset_nonexpanding"
        ]
        and evidence["proof"]["maximum_rewrite_attempts_per_root"] == 1
        and evidence["proof"]["automatic_promotion_count"] == 0,
        "private evidence header/proof drifted",
    )
    accepted, _blocked = validate_assignment(assignment, evidence)
    overrides = validate_decisions(decisions, accepted)

    candidate, current, source, contexts, _pending = (
        ASSIGNMENT.RECORDS.load_records()
    )
    require(
        terminal_digest(candidate) == EXPECTED_SHA256["terminal_candidate"]
        and terminal_digest(current) == EXPECTED_SHA256["terminal_current"]
        and terminal_digest(source) == EXPECTED_SHA256["terminal_source"]
        and all(
            terminal_digest(contexts[language])
            == "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
            for language in ("en", "sc", "tc")
        ),
        "terminal register drifted",
    )
    terminal_coordinates = {
        f"0:{record_id}:0" for record_id in TERMINALS
    }
    require(not accepted & terminal_coordinates, "terminal decision leaked")

    live_path = (
        WRAPPER.RANKING_WRAPPER.DEFAULT_STEAM_ROOT
        / "MSG_PK" / "JP" / "msggame.bin"
    )
    steam_before = sha256_file(live_path)
    require(steam_before == EXPECTED_SHA256["live_steam"], "Steam drifted")
    replacements, _ = RANKING.load_official_ledger(OFFICIAL_LEDGER_PATH)
    candidate_blob = ENGINE.rebuild_packed_with_literals(
        live_path.read_bytes(), replacements
    )
    require(
        sha256_bytes(candidate_blob) == EXPECTED_SHA256["official_candidate"],
        "official candidate reconstruction drifted",
    )
    reviewed_blob = ENGINE.rebuild_packed_with_literals(
        candidate_blob,
        {
            parse_coordinate(coordinate): body
            for coordinate, body in overrides.items()
        },
    )
    reviewed_sha256 = sha256_bytes(reviewed_blob)
    if EXPECTED_SHA256["reviewed_candidate"] is not None:
        require(
            reviewed_sha256 == EXPECTED_SHA256["reviewed_candidate"],
            "reviewed candidate drifted",
        )
    reviewed = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(reviewed_blob).archive
    )
    for row in decisions:
        coordinate = str(row["coordinate"])
        require(
            row["jp_source_utf16le_sha256"]
            == utf16le_sha256(literal_text(source, coordinate))
            and row["current_ko_utf16le_sha256"]
            == utf16le_sha256(literal_text(current, coordinate))
            and row["reviewed_translation"]
            == literal_text(reviewed, coordinate),
            "decision text lineage drifted",
        )
    changed_roots = {
        root for root in candidate if candidate[root].data != reviewed[root].data
    }
    require(
        len(changed_roots) == 4
        and changed_roots
        == {parse_coordinate(coordinate)[:2] for coordinate in overrides},
        "changed root set drifted",
    )
    reverse_blob = ENGINE.rebuild_packed_with_literals(
        reviewed_blob,
        {
            parse_coordinate(coordinate):
                literal_text(candidate, coordinate)
            for coordinate in overrides
        },
    )
    require(
        sha256_bytes(reverse_blob) == EXPECTED_SHA256["official_candidate"]
        and sha256_file(live_path) == steam_before,
        "reverse overlay or Steam immutability drifted",
    )

    counts = evidence["counts"]
    report = {
        "distribution_policy": {
            "private_decisions_stay_below_tmp": True,
            "private_evidence_stays_below_tmp": True,
            "tracked_builder_contains_dialogue_bodies": False,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_test_contains_dialogue_bodies": False,
        },
        "guards": {
            "assignment_private_sha256": EXPECTED_SHA256["assignment_private"],
            "decision_file_sha256": EXPECTED_SHA256["private_decisions"],
            "evidence_file_sha256": EXPECTED_SHA256["private_evidence"],
            "official_candidate_sha256":
                EXPECTED_SHA256["official_candidate"],
            "reviewed_candidate_sha256": reviewed_sha256,
            "reverse_overlay_sha256": EXPECTED_SHA256["official_candidate"],
        },
        "method": METHOD,
        "proof": {
            "all_pending_rows_freshly_reviewed": True,
            "automatic_promotion_count_zero": True,
            "conservative_runtime_assembly_superset_nonexpanding": True,
            "controls_tags_and_linebreaks_preserved": True,
            "current_relative_raw_g1n_gate_applied": True,
            "historical_factuality_reviewed": True,
            "maximum_rewrite_attempts_per_root": 1,
            "source_only_action_count_zero": True,
            "speaker_tone_reviewed": True,
            "terminal_rows_pending_read_only": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": counts,
        "schema": SCHEMA,
        "scope": {
            "chunk_id": 0,
            "selector": 238,
            "workload_weight": 271,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    assert_source_free(report)
    return report


def build_output() -> bytes:
    content = serialized(build_report())
    if EXPECTED_PUBLIC_SHA256 is not None:
        require(
            sha256_bytes(content) == EXPECTED_PUBLIC_SHA256,
            "public output drifted",
        )
    return content


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    content = build_output()
    if args.write:
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PUBLIC_OUTPUT.write_bytes(content)
    else:
        require(
            DEFAULT_PUBLIC_OUTPUT.is_file()
            and DEFAULT_PUBLIC_OUTPUT.read_bytes() == content,
            "public output is not frozen",
        )
    print(json.dumps({
        "accepted_pending": 11,
        "blocked_pending": 3,
        "output_sha256": sha256_bytes(content),
        "reviewed_candidate_sha256":
            build_report()["guards"]["reviewed_candidate_sha256"],
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
