#!/usr/bin/env python3
"""Validate the private selector-1174 chunk-0 review without embedding text."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector1174_assignment_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector1174_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1174_assignment_coverage.v1.json"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector538_family_checkpoint.private.v1.jsonl"
)
CROSS_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector568_1096_cross_family_consolidated_closure_decisions.private.v1.jsonl"
)
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1174_chunk0_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1174_chunk0_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1174_chunk0_review.source_free.v1.json"
)
LIVE_STEAM_PATH = (
    Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)

PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1174-chunk0-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1174-chunk0-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector1174-chunk0-review.source-free.v1"
METHOD = (
    "corrected_cross_predecessor_selector1174_chunk0_full_semantic_"
    "seven_branch_runtime_review"
)

SELECTOR = 1174
CHUNK_ID = 0
TERMINALS = tuple(range(2644, 2651))
EXPECTED_SITE_COUNT = 55
EXPECTED_ROOT_COUNT = 54
EXPECTED_PENDING_COUNT = 107
EXPECTED_CROSS_OVERLAP_COUNT = 5
EXPECTED_DISJOINT_PENDING_COUNT = 102
EXPECTED_ASSEMBLY_COUNT = 385
EXPECTED_DECISION_COUNT = 152
EXPECTED_OVERRIDE_COUNT = 116
EXPECTED_REWRITE_COUNT = 54
EXPECTED_KEEP_COUNT = 1

EXPECTED_ASSIGNMENT_SHA256 = (
    "07B892C55CAB031BDE414726FD301F03441E181C228D970003A834612ACABC10"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "6979EE31FB6AE4C046892E0785A61CC1D57F58415EB3B3D55601944F148A2CB2"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_CROSS_DECISIONS_SHA256 = (
    "E3C97823C70FBD441D420722AE306E2DEBE62CB8919FBA5426A91BC00DCBA5ED"
)
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "DCB19B0D85422F7C0EA5888F9A0C47667D75A88D100BABAE11DDAF4A8DD2000E"
)
EXPECTED_CROSS_CANDIDATE_SHA256 = (
    "FF424B8C66BECD398E7617EA95904BFBEBFADEA581870CE5A142CD9BF3CA4845"
)
EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "21319B72C07E425EA1838D3764508E98CC06EAF5238CA84B6AD88C6F0498C088"
)
EXPECTED_REVERSE_OVERLAY_SHA256 = EXPECTED_CROSS_CANDIDATE_SHA256
EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_CHUNK_SITE_SHA256 = (
    "B209F2D61F4EA472EBC9976E3E5A66DD3E9A64FDB9E4C542ED4E7E176139A1CE"
)
EXPECTED_CHUNK_ROOT_SHA256 = (
    "3726B2B2E64C04571A8D3C72B4FE7A2DA18FCF0AFC44DF1A7D33E811D2819AB1"
)
EXPECTED_PENDING_SHA256 = (
    "157CE5D411445A37B46875072FF7B84086BDDC6F8FAEB1D7EC264FFA7BB8C4E3"
)
EXPECTED_CROSS_OVERLAP_SHA256 = (
    "F5506073717E937EA1F551ED9EC9B928F1D6E2F50F05D0D9F223B0970E1C92BA"
)
EXPECTED_DISJOINT_PENDING_SHA256 = (
    "F29A8B46ACC38C5646F6513271A283AC0B7817ADAF1A1BDAA69BEB1DEAE680B7"
)
EXPECTED_DECISION_FILE_SHA256 = (
    "3188012B484E7A3A7A39A679A6B0B551DFD1F903BF0BE9EBCF3BC195CEFEA33B"
)
EXPECTED_EVIDENCE_FILE_SHA256 = (
    "D442C6224729AC5FF6CD75D087A886B7059D8A220A152728C2C106FB5C2643C5"
)
EXPECTED_PUBLIC_FILE_SHA256 = (
    "6DDF9C9CC84EC65A007230FB97477CACBD559C794341EC416F74DA2FFB65BD3F"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "50D20D87784197B6C6EEBC7B54E3F03C3046AF0DCB26C1E9FFBBDF255624E7B2"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "732D06C9B42FA993D6C908A632D5E9DDE8F6BE43278AF1EDE87574FE9DF0CB15"
)
EXPECTED_ASSEMBLY_SHA256 = (
    "421DBF64BC4C13501BBFAB74CB39C7EC3DD36F13151FAC63ABD46042191D0D93"
)
EXPECTED_ACTION_COUNTS = {
    "cross_translation_override_and_verification_renewal": 2,
    "cross_verification_renewal": 3,
    "runtime_promotion": 33,
    "translation_override_and_runtime_promotion": 69,
    "translation_override_and_verification_renewal": 45,
}


class ReviewError(ValueError):
    """Raised when a frozen review invariant drifts."""


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


ASSIGN = load_module(
    ASSIGNMENT_BUILDER_PATH,
    "pk_selector1174_chunk0_review_assignment_validator_v1",
)
ENGINE = ASSIGN.ENGINE
RANKING = ASSIGN.RANKING
ASSIGN.OFFICIAL_LEDGER_PATH = OFFICIAL_LEDGER_PATH


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def coordinate_digest(values: Iterable[str]) -> str:
    return sha256_bytes(
        "\n".join(sorted(set(values), key=parse_coordinate)).encode("ascii")
    )


def parse_coordinate(value: str) -> tuple[int, int, int]:
    return tuple(map(int, value.split(":")))  # type: ignore[return-value]


def utf16le_sha256(value: str) -> str:
    value.encode("utf-16le", errors="strict")
    return sha256_bytes(value.encode("utf-16le"))


def record_gap_sha256(record: Any) -> str:
    framed = b"".join(
        len(gap).to_bytes(4, "little") + gap
        for gap in ENGINE.record_gap_bytes(record)
    )
    return sha256_bytes(framed)


def literal_text(
    records: Mapping[tuple[int, int], Any],
    coordinate: str,
) -> str:
    block_id, record_id, literal_id = parse_coordinate(coordinate)
    literals = ENGINE.parse_record_literals(records[(block_id, record_id)])
    require(literal_id < len(literals), f"literal is absent: {coordinate}")
    return literals[literal_id].text


def adjacent_literals(
    records: Mapping[tuple[int, int], Any],
    site: str,
) -> tuple[str, str]:
    return ASSIGN.adjacent_literals(records, site)


def line_metrics(value: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line in value.split("\n"):
        full = 0
        half = 0
        for character in line:
            if unicodedata.category(character) == "Cc":
                continue
            if unicodedata.east_asian_width(character) in {"W", "F", "A"}:
                full += 1
            else:
                half += 1
        result.append(
            {
                "full_width_count": full,
                "half_width_count": half,
                "raw_g1n_width_px": 48 * full + 24 * half,
                "visible": line,
            }
        )
    return result


def current_relative_nonexpanding(
    reviewed: Sequence[Mapping[str, Any]],
    current: Sequence[Mapping[str, Any]],
) -> bool:
    return len(reviewed) == len(current) and all(
        int(candidate["raw_g1n_width_px"]) <= int(baseline["raw_g1n_width_px"])
        for candidate, baseline in zip(reviewed, current)
    )


def load_json_exact(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM rejected: {path}")
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReviewError(f"invalid strict UTF-8 JSON: {path}") from exc
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def load_decisions_exact(raw: bytes) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line in raw.splitlines():
        if not line:
            continue
        try:
            value = json.loads(line.decode("utf-8", errors="strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ReviewError("invalid strict UTF-8 decision stream") from exc
        require(isinstance(value, dict), "decision row must be an object")
        result.append(value)
    return result


def load_assignment() -> tuple[dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(ASSIGNMENT_PATH) == EXPECTED_ASSIGNMENT_SHA256,
        "selector assignment hash drifted",
    )
    require(
        sha256_file(ASSIGNMENT_PUBLIC_PATH) == EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        "selector assignment public hash drifted",
    )
    assignment = load_json_exact(ASSIGNMENT_PATH)
    require(
        assignment.get("schema") == ASSIGN.PRIVATE_SCHEMA,
        "selector assignment schema drifted",
    )
    chunk = assignment["chunks"][CHUNK_ID]
    require(
        chunk.get("chunk_id") == CHUNK_ID
        and chunk.get("site_count") == EXPECTED_SITE_COUNT
        and chunk.get("root_count") == EXPECTED_ROOT_COUNT
        and chunk.get("pending_row_upper_bound") == EXPECTED_PENDING_COUNT
        and chunk.get("cross_family_overlap_row_count")
        == EXPECTED_CROSS_OVERLAP_COUNT
        and chunk.get("disjoint_pending_row_count")
        == EXPECTED_DISJOINT_PENDING_COUNT
        and chunk.get("site_sha256") == EXPECTED_CHUNK_SITE_SHA256
        and chunk.get("root_sha256") == EXPECTED_CHUNK_ROOT_SHA256
        and chunk.get("pending_sha256") == EXPECTED_PENDING_SHA256
        and chunk.get("cross_family_overlap_sha256")
        == EXPECTED_CROSS_OVERLAP_SHA256
        and chunk.get("disjoint_pending_sha256")
        == EXPECTED_DISJOINT_PENDING_SHA256,
        "selector assignment chunk drifted",
    )
    return assignment, chunk


def load_cross_map() -> dict[tuple[int, int, int], str]:
    require(
        sha256_file(CROSS_DECISIONS_PATH) == EXPECTED_CROSS_DECISIONS_SHA256,
        "cross-family decisions hash drifted",
    )
    result: dict[tuple[int, int, int], str] = {}
    for line in CROSS_DECISIONS_PATH.read_bytes().splitlines():
        if not line:
            continue
        row = json.loads(line.decode("utf-8", errors="strict"))
        coordinate = parse_coordinate(str(row["coordinate"]))
        translation = row.get("translation")
        require(
            coordinate not in result and isinstance(translation, str),
            "cross-family row drifted",
        )
        result[coordinate] = translation
    require(len(result) == 920, "cross-family row universe drifted")
    return result


def load_world() -> dict[str, Any]:
    candidate, current, source, contexts, _pending = ASSIGN.load_records()
    current_path = RANKING.DEFAULT_STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin"
    official, _pending_by_root, _rows = RANKING.load_official_ledger(
        OFFICIAL_LEDGER_PATH
    )
    official_blob = ENGINE.rebuild_packed_with_literals(
        current_path.read_bytes(), official
    )
    require(
        sha256_bytes(official_blob) == EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        "official predecessor reconstruction drifted",
    )
    cross_blob = ENGINE.rebuild_packed_with_literals(
        official_blob, load_cross_map()
    )
    require(
        sha256_bytes(cross_blob) == EXPECTED_CROSS_CANDIDATE_SHA256,
        "cross predecessor reconstruction drifted",
    )
    cross = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(cross_blob).archive
    )
    require(set(cross) == set(candidate), "record universe drifted")
    return {
        "cross_blob": cross_blob,
        "cross": cross,
        "current": current,
        "source": source,
        "contexts": contexts,
    }


def decision_action(
    coordinate: str,
    *,
    overlap: set[str],
    pending: set[str],
    changed: set[str],
) -> str:
    if coordinate in overlap:
        return (
            "cross_translation_override_and_verification_renewal"
            if coordinate in changed
            else "cross_verification_renewal"
        )
    if coordinate in pending:
        return (
            "translation_override_and_runtime_promotion"
            if coordinate in changed
            else "runtime_promotion"
        )
    require(coordinate in changed, f"unexpected nonpending row: {coordinate}")
    return "translation_override_and_verification_renewal"


def validate_decision_bytes(actual: bytes, expected: bytes) -> None:
    require(actual == expected, "private selector-1174 decision bytes drifted")


def validate_decisions(
    rows: Sequence[Mapping[str, Any]],
    *,
    chunk: Mapping[str, Any],
    world: Mapping[str, Any],
) -> dict[str, Any]:
    require(len(rows) == EXPECTED_DECISION_COUNT, "decision count drifted")
    cross = world["cross"]
    current = world["current"]
    source = world["source"]
    pending = set(map(str, chunk["pending_coordinates"]))
    overlap = set(map(str, chunk["cross_family_overlap_coordinates"]))
    disjoint = set(map(str, chunk["disjoint_pending_coordinates"]))
    require(
        len(pending) == EXPECTED_PENDING_COUNT
        and len(overlap) == EXPECTED_CROSS_OVERLAP_COUNT
        and len(disjoint) == EXPECTED_DISJOINT_PENDING_COUNT
        and pending == overlap | disjoint
        and overlap.isdisjoint(disjoint),
        "pending partition drifted",
    )

    coordinates: set[str] = set()
    reviewed_by_coordinate: dict[str, str] = {}
    action_counts: Counter[str] = Counter()
    for row in rows:
        coordinate = str(row.get("coordinate"))
        require(coordinate not in coordinates, "duplicate decision coordinate")
        parse_coordinate(coordinate)
        coordinates.add(coordinate)
        reviewed = row.get("reviewed_translation")
        require(isinstance(reviewed, str), "reviewed body absent")
        cross_text = literal_text(cross, coordinate)
        current_text = literal_text(current, coordinate)
        source_text = literal_text(source, coordinate)
        require(
            row.get("schema") == PRIVATE_DECISION_SCHEMA
            and row.get("resource") == "pk_msggame"
            and row.get("runtime_review") == "verified"
            and row.get("fresh_semantic_review") == "approved"
            and row.get("historical_factuality_review") == "approved"
            and row.get("speaker_tone_review") == "approved"
            and row.get("layout_review")
            == "current_relative_raw_g1n_nonexpanding",
            f"decision approval drifted at {coordinate}",
        )
        require(
            row.get("cross_predecessor_translation") == cross_text
            and row.get("cross_predecessor_utf16le_sha256")
            == utf16le_sha256(cross_text)
            and row.get("current_ko_utf16le_sha256")
            == utf16le_sha256(current_text)
            and row.get("jp_source_utf16le_sha256")
            == utf16le_sha256(source_text)
            and row.get("reviewed_utf16le_sha256") == utf16le_sha256(reviewed),
            f"decision body/hash drifted at {coordinate}",
        )
        predecessor = row.get("predecessor", {})
        require(
            predecessor.get("assignment_sha256") == EXPECTED_ASSIGNMENT_SHA256
            and predecessor.get("cross_candidate_sha256")
            == EXPECTED_CROSS_CANDIDATE_SHA256
            and predecessor.get("cross_decisions_sha256")
            == EXPECTED_CROSS_DECISIONS_SHA256,
            f"decision predecessor drifted at {coordinate}",
        )
        reviewed_by_coordinate[coordinate] = reviewed

    changed = {
        coordinate
        for coordinate, reviewed in reviewed_by_coordinate.items()
        if reviewed != literal_text(cross, coordinate)
    }
    require(len(changed) == EXPECTED_OVERRIDE_COUNT, "override count drifted")
    require(coordinates == pending | changed, "decision universe drifted")
    for row in rows:
        coordinate = str(row["coordinate"])
        expected_action = decision_action(
            coordinate,
            overlap=overlap,
            pending=pending,
            changed=changed,
        )
        require(row.get("action") == expected_action, "decision action drifted")
        expected_owner = (
            "selector568_1096_cross_family" if coordinate in overlap else None
        )
        require(row.get("overlap_owner") == expected_owner, "owner drifted")
        action_counts[expected_action] += 1
    require(
        dict(sorted(action_counts.items())) == EXPECTED_ACTION_COUNTS,
        "decision action counts drifted",
    )
    require(
        coordinate_digest(coordinates) == EXPECTED_DECISION_COORDINATE_SHA256
        and coordinate_digest(changed) == EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "decision coordinate digest drifted",
    )

    reviewed_blob = ENGINE.rebuild_packed_with_literals(
        world["cross_blob"],
        {
            parse_coordinate(coordinate): reviewed_by_coordinate[coordinate]
            for coordinate in changed
        },
    )
    require(
        sha256_bytes(reviewed_blob) == EXPECTED_REVIEWED_CANDIDATE_SHA256,
        "reviewed candidate drifted",
    )
    reviewed_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(reviewed_blob).archive
    )
    reverse_blob = ENGINE.rebuild_packed_with_literals(
        reviewed_blob,
        {
            parse_coordinate(coordinate): literal_text(cross, coordinate)
            for coordinate in changed
        },
    )
    require(
        reverse_blob == world["cross_blob"]
        and sha256_bytes(reverse_blob) == EXPECTED_REVERSE_OVERLAY_SHA256,
        "reverse overlay drifted",
    )
    changed_roots = {
        parse_coordinate(coordinate)[:2] for coordinate in changed
    }
    for root in changed_roots:
        require(
            record_gap_sha256(cross[root])
            == record_gap_sha256(reviewed_records[root]),
            f"record controls drifted at {root}",
        )
    return {
        "action_counts": dict(sorted(action_counts.items())),
        "changed": changed,
        "coordinates": coordinates,
        "reviewed_blob": reviewed_blob,
        "reviewed_records": reviewed_records,
    }


def validate_context(
    recorded: Mapping[str, Any],
    *,
    records: Mapping[tuple[int, int], Any],
    site: str,
    available: bool,
) -> None:
    left, right = adjacent_literals(records, site)
    require(
        recorded.get("available") is available
        and recorded.get("left") == left
        and recorded.get("right") == right
        and recorded.get("joined_utf8_sha256")
        == sha256_bytes((left + right).encode("utf-8")),
        f"multilingual context drifted at {site}",
    )


def validate_evidence(
    evidence: Mapping[str, Any],
    *,
    assignment: Mapping[str, Any],
    chunk: Mapping[str, Any],
    world: Mapping[str, Any],
    decisions: Mapping[str, Any],
) -> None:
    require(
        evidence.get("schema") == PRIVATE_EVIDENCE_SCHEMA
        and evidence.get("method") == METHOD,
        "private evidence schema/method drifted",
    )
    require(
        evidence.get("privacy")
        == {
            "classification": "private",
            "contains_dialogue_bodies": True,
            "contains_exact_coordinates": True,
            "public": False,
            "shared_integration_mutated": False,
            "steam_write_performed": False,
        },
        "private evidence policy drifted",
    )
    require(
        evidence.get("counts")
        == {
            "accepted_sites": EXPECTED_SITE_COUNT,
            "assembly_branches": EXPECTED_ASSEMBLY_COUNT,
            "cross_owned_renewals": EXPECTED_CROSS_OVERLAP_COUNT,
            "decision_rows": EXPECTED_DECISION_COUNT,
            "disjoint_runtime_promotions": EXPECTED_DISJOINT_PENDING_COUNT,
            "holds": 0,
            "keep_sites": EXPECTED_KEEP_COUNT,
            "rewrite_sites": EXPECTED_REWRITE_COUNT,
            "roots": EXPECTED_ROOT_COUNT,
            "sites": EXPECTED_SITE_COUNT,
            "translation_overrides": EXPECTED_OVERRIDE_COUNT,
        },
        "private evidence counts drifted",
    )
    scope = evidence.get("scope", {})
    require(
        scope.get("chunk_id") == CHUNK_ID
        and scope.get("selector") == SELECTOR
        and scope.get("site_sha256") == EXPECTED_CHUNK_SITE_SHA256
        and scope.get("root_sha256") == EXPECTED_CHUNK_ROOT_SHA256
        and scope.get("pending_sha256") == EXPECTED_PENDING_SHA256
        and scope.get("cross_overlap_sha256")
        == EXPECTED_CROSS_OVERLAP_SHA256
        and scope.get("disjoint_pending_sha256")
        == EXPECTED_DISJOINT_PENDING_SHA256
        and tuple(scope.get("terminal_coordinates", ()))
        == tuple(f"0:{terminal}:0" for terminal in TERMINALS),
        "private evidence scope drifted",
    )
    inputs = evidence.get("inputs", {})
    require(
        inputs.get("assignment_sha256") == EXPECTED_ASSIGNMENT_SHA256
        and inputs.get("assignment_public_sha256")
        == EXPECTED_ASSIGNMENT_PUBLIC_SHA256
        and inputs.get("official_ledger_sha256")
        == EXPECTED_OFFICIAL_LEDGER_SHA256
        and inputs.get("corrected_cross_candidate_sha256")
        == EXPECTED_CROSS_CANDIDATE_SHA256
        and inputs.get("corrected_cross_decisions_sha256")
        == EXPECTED_CROSS_DECISIONS_SHA256,
        "private evidence inputs drifted",
    )
    digests = evidence.get("digests", {})
    require(
        digests.get("assembly_canonical_sha256") == EXPECTED_ASSEMBLY_SHA256
        and digests.get("decision_coordinate_sha256")
        == EXPECTED_DECISION_COORDINATE_SHA256
        and digests.get("override_coordinate_sha256")
        == EXPECTED_OVERRIDE_COORDINATE_SHA256
        and digests.get("reviewed_candidate_sha256")
        == EXPECTED_REVIEWED_CANDIDATE_SHA256
        and digests.get("reverse_overlay_sha256")
        == EXPECTED_REVERSE_OVERLAY_SHA256,
        "private evidence digests drifted",
    )

    cross = world["cross"]
    current = world["current"]
    source = world["source"]
    contexts = world["contexts"]
    reviewed = decisions["reviewed_records"]
    terminal_review = evidence.get("terminal_review", {})
    require(
        terminal_review.get("all_korean_terminals_zero_width") is True
        and terminal_review.get("automatic_space_inserted") is False
        and terminal_review.get("jp_honorific_prefix_semantics_reviewed")
        is True
        and terminal_review.get("korean_spacing_owned_by_callers") is True,
        "terminal proof drifted",
    )
    terminal_cross = {
        terminal: literal_text(cross, f"0:{terminal}:0")
        for terminal in TERMINALS
    }
    terminal_current = {
        terminal: literal_text(current, f"0:{terminal}:0")
        for terminal in TERMINALS
    }
    terminal_source = {
        terminal: literal_text(source, f"0:{terminal}:0")
        for terminal in TERMINALS
    }
    for key, expected in (
        ("terminal_reviewed", terminal_cross),
        ("terminal_current", terminal_current),
        ("terminal_jp", terminal_source),
    ):
        recorded = terminal_review.get(key, {})
        require(
            recorded == {str(index): value for index, value in expected.items()},
            f"{key} drifted",
        )
    require(
        all(not value for value in terminal_cross.values()),
        "reviewed terminal is not zero-width",
    )

    site_rows = evidence.get("site_reviews")
    require(
        isinstance(site_rows, list) and len(site_rows) == EXPECTED_SITE_COUNT,
        "site review count drifted",
    )
    assignment_rows = assignment["site_assignments"][
        int(chunk["ordinal_start"]) : int(chunk["ordinal_end"]) + 1
    ]
    assembly_manifest: list[list[Any]] = []
    decisions_by_kind: Counter[str] = Counter()
    for expected_assignment, row in zip(assignment_rows, site_rows):
        site = str(expected_assignment["site"])
        ordinal = int(expected_assignment["ordinal"])
        block_id, record_id, gap_id, _offset = RANKING.site_key(site)
        root = (block_id, record_id)
        cross_left, cross_right = adjacent_literals(cross, site)
        current_left, current_right = adjacent_literals(current, site)
        reviewed_left, reviewed_right = adjacent_literals(reviewed, site)
        expected_decision = (
            "rewrite"
            if (cross_left, cross_right) != (reviewed_left, reviewed_right)
            else "keep"
        )
        decisions_by_kind[expected_decision] += 1
        require(
            row.get("site") == site
            and row.get("ordinal") == ordinal
            and row.get("root") == f"{block_id}:{record_id}"
            and row.get("left_coordinate")
            == f"{block_id}:{record_id}:{gap_id - 1}"
            and row.get("right_coordinate")
            == f"{block_id}:{record_id}:{gap_id}"
            and row.get("reviewed_left_translation") == reviewed_left
            and row.get("reviewed_right_translation") == reviewed_right
            and row.get("decision") == expected_decision,
            f"site identity/body drifted at ordinal {ordinal}",
        )
        require(
            row.get("all_seven_grammar_and_spacing_branches_proven") is True
            and row.get("all_seven_width_branches_nonexpanding") is True,
            f"site proof drifted at ordinal {ordinal}",
        )
        authority = row.get("multilingual_authority", {})
        require(
            authority.get("fresh_review_completed") is True
            and authority.get("historical_factuality_reviewed") is True
            and authority.get("jp_is_semantic_authority") is True
            and authority.get("speaker_tone_reviewed") is True,
            f"authority proof drifted at ordinal {ordinal}",
        )
        language_records = {"jp": source, **contexts}
        for language in ("jp", "sc", "tc", "en"):
            validate_context(
                authority.get(language, {}),
                records=language_records[language],
                site=site,
                available=bool(
                    expected_assignment["language_available"][language]
                ),
            )
        historical = row.get("historical_terms_reviewed")
        require(
            isinstance(historical, list),
            f"historical review list drifted at ordinal {ordinal}",
        )
        control = row.get("control_and_encoding_proof", {})
        cross_gap = record_gap_sha256(cross[root])
        reviewed_gap = record_gap_sha256(reviewed[root])
        require(
            control.get("cross_record_gap_sha256") == cross_gap
            and control.get("reviewed_record_gap_sha256") == reviewed_gap
            and control.get("record_control_gaps_preserved") is True
            and cross_gap == reviewed_gap
            and control.get("literal_linebreak_counts_preserved") is True
            and cross_left.count("\n") == reviewed_left.count("\n")
            and cross_right.count("\n") == reviewed_right.count("\n")
            and control.get("reviewed_utf16le_encodable") is True,
            f"control proof drifted at ordinal {ordinal}",
        )
        reviewed_left.encode("utf-16le", errors="strict")
        reviewed_right.encode("utf-16le", errors="strict")

        branches = row.get("assemblies")
        require(
            isinstance(branches, list) and len(branches) == len(TERMINALS),
            f"branch count drifted at ordinal {ordinal}",
        )
        for terminal, branch in zip(TERMINALS, branches):
            reviewed_assembly = (
                reviewed_left + terminal_cross[terminal] + reviewed_right
            )
            current_assembly = (
                current_left + terminal_current[terminal] + current_right
            )
            reviewed_lines = line_metrics(reviewed_assembly)
            current_lines = line_metrics(current_assembly)
            nonexpanding = current_relative_nonexpanding(
                reviewed_lines, current_lines
            )
            require(
                branch.get("terminal_coordinate") == f"0:{terminal}:0"
                and branch.get("reviewed_terminal") == terminal_cross[terminal]
                and branch.get("current_terminal")
                == terminal_current[terminal]
                and branch.get("source_terminal") == terminal_source[terminal]
                and branch.get("reviewed_assembly") == reviewed_assembly
                and branch.get("current_assembly") == current_assembly
                and branch.get("reviewed_lines") == reviewed_lines
                and branch.get("current_lines") == current_lines
                and branch.get("line_count_match") is True
                and len(reviewed_lines) == len(current_lines)
                and branch.get("current_relative_raw_g1n_nonexpanding")
                is True
                and nonexpanding
                and branch.get("grammar_and_spacing_proven") is True
                and branch.get("terminal_semantic")
                == "korean_zero_width_honorific_prefix",
                f"runtime branch drifted at ordinal {ordinal}",
            )
            assembly_manifest.append(
                [
                    ordinal,
                    site,
                    terminal,
                    sha256_bytes(reviewed_assembly.encode("utf-8")),
                    sha256_bytes(current_assembly.encode("utf-8")),
                    nonexpanding,
                    True,
                ]
            )
    require(
        decisions_by_kind
        == Counter({"rewrite": EXPECTED_REWRITE_COUNT, "keep": EXPECTED_KEEP_COUNT}),
        "site decision counts drifted",
    )
    require(
        evidence.get("assembly_manifest") == assembly_manifest
        and len(assembly_manifest) == EXPECTED_ASSEMBLY_COUNT
        and canonical_sha256(assembly_manifest) == EXPECTED_ASSEMBLY_SHA256,
        "assembly manifest drifted",
    )


def assert_source_free(value: Any) -> None:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        )
        is None,
        "public report contains source-bearing text",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", serialized) is None,
        "public report contains an exact coordinate",
    )


def build_public(
    *,
    action_counts: Mapping[str, int],
    steam_before: str,
    steam_after: str,
) -> dict[str, Any]:
    public: dict[str, Any] = {
        "distribution_policy": {
            "private_decisions_stay_below_tmp": True,
            "private_evidence_stays_below_tmp": True,
            "tracked_builder_contains_dialogue_bodies": False,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_translation_map_keys": False,
            "tracked_test_contains_dialogue_bodies": False,
            "tracked_validator_uses_frozen_private_hashes": True,
        },
        "inputs": {
            "assignment_public_sha256": EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
            "assignment_sha256": EXPECTED_ASSIGNMENT_SHA256,
            "corrected_cross_candidate_sha256":
            EXPECTED_CROSS_CANDIDATE_SHA256,
            "corrected_cross_decisions_sha256":
            EXPECTED_CROSS_DECISIONS_SHA256,
            "official_ledger_sha256": EXPECTED_OFFICIAL_LEDGER_SHA256,
        },
        "method": METHOD,
        "proof": {
            "all_55_sites_freshly_semantically_reviewed": True,
            "all_385_selected_runtime_branches_recorded": True,
            "all_accepted_branches_current_relative_raw_g1n_nonexpanding": True,
            "all_changed_record_control_gaps_preserved": True,
            "all_jp_honorific_prefix_variants_neutralized_for_korean": True,
            "all_literal_linebreak_counts_preserved": True,
            "automatic_space_inserted_by_vm": False,
            "historical_factuality_reviewed": True,
            "reverse_overlay_recovers_corrected_cross_predecessor": True,
            "speaker_tone_reviewed": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": {
            "accepted_site_count": EXPECTED_SITE_COUNT,
            "assembly_branch_count": EXPECTED_ASSEMBLY_COUNT,
            "assembly_canonical_sha256": EXPECTED_ASSEMBLY_SHA256,
            "cross_owned_coordinate_count": EXPECTED_CROSS_OVERLAP_COUNT,
            "cross_owned_coordinate_sha256": EXPECTED_CROSS_OVERLAP_SHA256,
            "decision_coordinate_count": EXPECTED_DECISION_COUNT,
            "decision_coordinate_sha256": EXPECTED_DECISION_COORDINATE_SHA256,
            "decision_file_sha256": EXPECTED_DECISION_FILE_SHA256,
            "disjoint_runtime_promotion_count":
            EXPECTED_DISJOINT_PENDING_COUNT,
            "disjoint_runtime_promotion_sha256":
            EXPECTED_DISJOINT_PENDING_SHA256,
            "evidence_file_sha256": EXPECTED_EVIDENCE_FILE_SHA256,
            "hold_count": 0,
            "keep_site_count": EXPECTED_KEEP_COUNT,
            "override_coordinate_count": EXPECTED_OVERRIDE_COUNT,
            "override_coordinate_sha256": EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "reviewed_candidate_sha256": EXPECTED_REVIEWED_CANDIDATE_SHA256,
            "reverse_overlay_sha256": EXPECTED_REVERSE_OVERLAY_SHA256,
            "rewrite_site_count": EXPECTED_REWRITE_COUNT,
        },
        "schema": PUBLIC_SCHEMA,
        "scope": {
            "chunk_id": CHUNK_ID,
            "pending_coordinate_count": EXPECTED_PENDING_COUNT,
            "pending_coordinate_sha256": EXPECTED_PENDING_SHA256,
            "root_count": EXPECTED_ROOT_COUNT,
            "root_sha256": EXPECTED_CHUNK_ROOT_SHA256,
            "selector": SELECTOR,
            "site_count": EXPECTED_SITE_COUNT,
            "site_sha256": EXPECTED_CHUNK_SITE_SHA256,
            "terminal_count": len(TERMINALS),
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    public["guards"] = {
        "action_counts": dict(sorted(action_counts.items())),
        "report_payload_sha256": canonical_sha256(public),
        "steam_archive_sha256_after": steam_after,
        "steam_archive_sha256_before": steam_before,
    }
    assert_source_free(public)
    return public


def build_outputs(
    *,
    decisions_content: bytes | None = None,
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    require(
        sha256_file(OFFICIAL_LEDGER_PATH) == EXPECTED_OFFICIAL_LEDGER_SHA256,
        "official ledger hash drifted",
    )
    frozen_decisions = PRIVATE_DECISIONS_PATH.read_bytes()
    frozen_evidence = PRIVATE_EVIDENCE_PATH.read_bytes()
    require(
        sha256_bytes(frozen_decisions) == EXPECTED_DECISION_FILE_SHA256
        and sha256_bytes(frozen_evidence) == EXPECTED_EVIDENCE_FILE_SHA256,
        "private artifact hash drifted",
    )
    if decisions_content is None:
        decisions_content = frozen_decisions
    if evidence is None:
        evidence = load_json_exact(PRIVATE_EVIDENCE_PATH)
    rows = load_decisions_exact(decisions_content)
    assignment, chunk = load_assignment()
    steam_before = sha256_file(LIVE_STEAM_PATH)
    require(
        steam_before == EXPECTED_LIVE_STEAM_SHA256,
        "live Steam archive drifted before validation",
    )
    world = load_world()
    validated_decisions = validate_decisions(
        rows, chunk=chunk, world=world
    )
    validate_evidence(
        evidence,
        assignment=assignment,
        chunk=chunk,
        world=world,
        decisions=validated_decisions,
    )
    evidence_content = canonical_bytes(evidence) + b"\n"
    require(
        sha256_bytes(evidence_content) == EXPECTED_EVIDENCE_FILE_SHA256,
        "private evidence canonical bytes drifted",
    )
    steam_after = sha256_file(LIVE_STEAM_PATH)
    require(steam_before == steam_after, "live Steam archive changed")
    public = build_public(
        action_counts=validated_decisions["action_counts"],
        steam_before=steam_before,
        steam_after=steam_after,
    )
    public_content = canonical_bytes(public) + b"\n"
    require(
        sha256_bytes(public_content) == EXPECTED_PUBLIC_FILE_SHA256,
        "public report bytes drifted",
    )
    return {
        "decision_rows": rows,
        "decisions_content": decisions_content,
        "evidence": evidence,
        "evidence_content": evidence_content,
        "public": public,
        "public_content": public_content,
        "validated": validated_decisions,
    }


def validate_frozen(outputs: Mapping[str, Any]) -> None:
    require(
        sha256_file(PRIVATE_DECISIONS_PATH) == EXPECTED_DECISION_FILE_SHA256
        and sha256_file(PRIVATE_EVIDENCE_PATH) == EXPECTED_EVIDENCE_FILE_SHA256
        and sha256_file(DEFAULT_PUBLIC_OUTPUT) == EXPECTED_PUBLIC_FILE_SHA256,
        "frozen artifact hash drifted",
    )
    validate_decision_bytes(
        PRIVATE_DECISIONS_PATH.read_bytes(),
        outputs["decisions_content"],
    )
    require(
        PRIVATE_EVIDENCE_PATH.read_bytes() == outputs["evidence_content"]
        and DEFAULT_PUBLIC_OUTPUT.read_bytes() == outputs["public_content"],
        "frozen artifact bytes drifted",
    )


def serialized_report() -> bytes:
    return build_outputs()["public_content"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--public-output",
        type=Path,
        default=DEFAULT_PUBLIC_OUTPUT,
    )
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(
        args.public_output.resolve() == DEFAULT_PUBLIC_OUTPUT.resolve(),
        "public output must use its fixed path",
    )
    outputs = build_outputs()
    if args.check:
        validate_frozen(outputs)
    else:
        args.public_output.write_bytes(outputs["public_content"])
    print(
        "selector1174 chunk0 review: PASS "
        f"sites={EXPECTED_SITE_COUNT} branches={EXPECTED_ASSEMBLY_COUNT} "
        f"decisions={EXPECTED_DECISION_COUNT} "
        f"overrides={EXPECTED_OVERRIDE_COUNT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
