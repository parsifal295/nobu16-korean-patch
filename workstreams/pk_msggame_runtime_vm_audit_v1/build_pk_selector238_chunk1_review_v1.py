#!/usr/bin/env python3
"""Validate selector-238 chunk 1 and emit its source-free checkpoint."""

from __future__ import annotations

import argparse
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
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector238_assignment_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector238_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector238_assignment_coverage.v1.json"
)
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector238_chunk1_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector238_chunk1_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector238_chunk1_review.source_free.v1.json"
)

CHUNK_ID = 1
SELECTOR = 238
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector238-chunk1-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector238-chunk1-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector238-chunk1-review.source-free.v1"
METHOD = (
    "post_selector730_selector238_chunk1_single_pass_semantic_and_"
    "runtime_review"
)

EXPECTED_SHA256 = {
    "assignment_builder":
        "4C09CA6AAC9DBE0EBB83E8A855C20724721AAF1875BE0C12B45ACDA9D1AEFE40",
    "assignment_private":
        "3B8629AC3DF5E18FEA92D82EB97D0E6D87870509E1C986BEFC3069050FF6D0C8",
    "assignment_public":
        "B44358FE6CC6EAD85972255F8D360EF5B6A0B1AB2D935DBCA4CC7F4D490ACE30",
    "official_ledger":
        "9F6BD587F6EC92CD00A2E2AF9FD9E07A8B6A71405272F0D79A515C3405617C5C",
    "private_decisions":
        "DA564E5EDE7122F53035E3FF9720E447332306F6B46AA0BDD8D9657C03B85449",
    "private_evidence":
        "7C63668279BEFA32853C916480D5AAF4785455CAD4418B2E6B0B3FC39005D5C5",
    "official_candidate":
        "5D4CDF1CEB8C733B0E22C7AA6185D9FF6C5C4C500176E99A6AACB3D89F7E0140",
    "reviewed_candidate":
        "498FCF1FD84EFA5AFD67FC02C34B6F567DE4C84E65FD7AC0CBE8D02E6B12127C",
    "live_steam":
        "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
    "terminal_candidate":
        "464E10C8A1DCFEF1B73492494A92601C01AC45FADE7F9D63D9691A931208F706",
    "terminal_current":
        "EED5D974C2CCA3E2C2186AEDC0DF3A480C95062942D55ECC3E966B8B94207B5E",
    "terminal_source":
        "E7D01ED5F17258F69B7A74858EC5D442FF39E9F2551426F903AAF83E1D6AA8ED",
}
EXPECTED_DIGESTS = {
    "site_disposition":
        "61D19A297F175721A5135D9EE403C8FD538B1BD3FE71F6D20E1073E25334EF35",
    "decision":
        "5C4BB91E19F2470FF19BF836D97C52888F0FEF4803F800822690203368DFE4C4",
    "downstream":
        "7FFF8EC20E0526130041E0DFF6588E94ACC7CE77DD372C15BBEE1F776D59F0BE",
    "override":
        "630C3AC8D1E3A8FDEB9D03BB899D2A6BDD5FE074F76893683B96D0FFA8DF5C05",
    "promoted":
        "5C4BB91E19F2470FF19BF836D97C52888F0FEF4803F800822690203368DFE4C4",
    "selector_branches":
        "C1D1458EB80C6D11D789640A976AD940EA184BD07A9DC09A8A4A93C62CD1EEDD",
}
EXPECTED_COUNTS = {
    "accepted_pending_roots": 5,
    "accepted_pending_rows": 16,
    "accepted_sites": 5,
    "assigned_roots": 13,
    "assigned_sites": 13,
    "blocked_pending_roots": 3,
    "blocked_pending_rows": 6,
    "blocked_sites": 3,
    "decision_rows": 16,
    "downstream_cartesian_branches": 49,
    "non_display_actions": 0,
    "owned_overlap_roots": 4,
    "prior_assembly_evidence_pending_rows": 17,
    "prior_assembly_evidence_roots": 8,
    "promoted_pending_rows": 16,
    "read_only_nonpending_roots": 5,
    "read_only_nonpending_sites": 5,
    "rewrite_attempt_roots": 5,
    "selector238_accepted_branches": 35,
    "selector238_all_current_relative_pass_branches": 70,
    "selector238_blocked_pending_branches": 21,
    "selector238_read_only_nonpending_branches": 35,
    "selector238_total_branches": 91,
    "source_only_actions": 0,
    "source_only_sites": 1,
    "template_roots": 0,
    "terminal_decision_rows": 0,
    "terminal_read_only_rows": 7,
    "translation_overrides": 12,
}
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 4,
    "translation_override_and_runtime_promotion": 12,
}
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "ED15DDD1F1373476DF8407AA0A0DBC276D4923388D4C4CFDE428ED8FA3DAF1AE"
)


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


WRAPPER = load_module(
    ASSIGNMENT_BUILDER_PATH, "selector238_chunk1_review_assignment"
)
ASSIGNMENT = WRAPPER.ASSIGNMENT
RANKING = WRAPPER.RANKING
ENGINE = WRAPPER.ENGINE
OFFICIAL_LEDGER_PATH = WRAPPER.RANKING_WRAPPER.DEFAULT_LEDGER
TERMINALS = tuple(WRAPPER.TERMINALS)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def serialized(value: Any) -> bytes:
    return canonical_bytes(value) + b"\n"


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts


def parse_root(value: str) -> tuple[int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    require(len(parts) == 2, f"invalid root: {value}")
    return parts


def coordinate_digest(values: Iterable[str]) -> str:
    return sha256_bytes(
        "\n".join(sorted(set(values), key=parse_coordinate)).encode("ascii")
    )


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


def literal_text(
    records: Mapping[tuple[int, int], Any], coordinate: str
) -> str:
    block_id, record_id, literal_id = parse_coordinate(coordinate)
    literals = ENGINE.parse_record_literals(records[(block_id, record_id)])
    require(literal_id < len(literals), f"literal absent: {coordinate}")
    return literals[literal_id].text


def terminal_text(
    records: Mapping[tuple[int, int], Any], root: tuple[int, int]
) -> str:
    literals = ENGINE.parse_record_literals(records[root])
    require(len(literals) == 1, f"terminal shape drifted: {root}")
    return literals[0].text


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le", errors="strict"))


def current_relative_pass(
    reviewed_widths: Sequence[int], current_widths: Sequence[int]
) -> bool:
    return (
        len(reviewed_widths) == len(current_widths)
        and all(
            reviewed <= current
            for reviewed, current in zip(reviewed_widths, current_widths)
        )
    )


def site_assembly(
    records: Mapping[tuple[int, int], Any],
    root: tuple[int, int],
    gap_id: int,
    terminal: tuple[int, int],
) -> str:
    literals = ENGINE.parse_record_literals(records[root])
    require(0 < gap_id <= len(literals), f"gap shape drifted: {root}")
    result = literals[gap_id - 1].text + terminal_text(records, terminal)
    if gap_id < len(literals):
        result += literals[gap_id].text
    return result


def validate_source_free(value: Any) -> None:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True)
    cjk = re.compile(
        r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
        r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
    )
    require(cjk.search(encoded) is None, "public report contains CJK text")
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", encoded) is None,
        "public report contains exact coordinates",
    )


def validate_inputs() -> tuple[
    dict[str, Any], dict[str, Any], list[dict[str, Any]]
]:
    immutable = {
        ASSIGNMENT_BUILDER_PATH: EXPECTED_SHA256["assignment_builder"],
        ASSIGNMENT_PATH: EXPECTED_SHA256["assignment_private"],
        ASSIGNMENT_PUBLIC_PATH: EXPECTED_SHA256["assignment_public"],
        OFFICIAL_LEDGER_PATH: EXPECTED_SHA256["official_ledger"],
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
    assignment: Mapping[str, Any], evidence: Mapping[str, Any]
) -> tuple[
    Mapping[str, Any],
    set[tuple[int, int]],
    set[tuple[int, int]],
    set[tuple[int, int]],
]:
    chunk = assignment["chunks"][CHUNK_ID]
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
        ) == (13, 13, 8, 22, 4, 8, 17, 0, 261),
        "chunk assignment metrics drifted",
    )
    accepted_coordinates = set(evidence["accepted_pending_coordinates"])
    blocked_coordinates = set(evidence["blocked_pending_coordinates"])
    require(
        accepted_coordinates | blocked_coordinates
        == set(chunk["pending_coordinates"])
        and not accepted_coordinates & blocked_coordinates,
        "pending row partition drifted",
    )
    accepted_roots = {
        parse_coordinate(coordinate)[:2] for coordinate in accepted_coordinates
    }
    blocked_roots = {
        parse_coordinate(coordinate)[:2] for coordinate in blocked_coordinates
    }
    read_only_roots = {
        parse_root(root) for root in evidence["read_only_nonpending_roots"]
    }
    chunk_roots = {parse_root(root) for root in chunk["roots"]}
    require(
        len(accepted_roots) == 5
        and len(blocked_roots) == 3
        and len(read_only_roots) == 5
        and accepted_roots | blocked_roots | read_only_roots == chunk_roots
        and not accepted_roots & blocked_roots
        and not accepted_roots & read_only_roots
        and not blocked_roots & read_only_roots,
        "root disposition partition drifted",
    )
    reviews = evidence["pending_root_reviews"]
    require(
        len(reviews) == 8
        and {
            parse_root(str(row["root"]))
            for row in reviews
            if str(row["decision"]).startswith("accepted_")
        } == accepted_roots
        and {
            parse_root(str(row["root"]))
            for row in reviews
            if str(row["decision"]).startswith("blocked_")
        } == blocked_roots,
        "root review disposition drifted",
    )
    require(
        assignment["prior_pending_evidence"][
            "automatic_status_promotion_authorized"
        ] is False
        and assignment["shared_terminal_ownership"][
            "automatic_status_promotion_authorized"
        ] is False
        and assignment["source_only_repair"]["action_count"] == 0
        and len(assignment["source_only_repair"]["sites"]) == 1,
        "assignment protection guard drifted",
    )
    return chunk, accepted_roots, blocked_roots, read_only_roots


def validate_decisions(
    decisions: Sequence[Mapping[str, Any]],
    evidence: Mapping[str, Any],
    accepted_roots: set[tuple[int, int]],
    blocked_roots: set[tuple[int, int]],
) -> tuple[dict[str, str], set[str]]:
    require(
        len(decisions) == EXPECTED_COUNTS["decision_rows"]
        and Counter(str(row["action"]) for row in decisions)
        == Counter(EXPECTED_ACTION_COUNTS),
        "decision action partition drifted",
    )
    coordinates = {str(row["coordinate"]) for row in decisions}
    require(
        coordinates == set(evidence["accepted_pending_coordinates"])
        and coordinate_digest(coordinates) == EXPECTED_DIGESTS["decision"]
        and not {
            parse_coordinate(coordinate)[:2] for coordinate in coordinates
        } & blocked_roots,
        "decision coordinate partition drifted",
    )
    for row in decisions:
        body = str(row["reviewed_translation"])
        require(
            row.get("schema") == PRIVATE_DECISION_SCHEMA
            and row.get("resource") == "pk_msggame"
            and row.get("fresh_semantic_review") == "approved"
            and row.get("historical_factuality_review") == "approved"
            and row.get("speaker_tone_review") == "approved"
            and row.get("runtime_review") == "verified"
            and row.get("layout_review")
            == "current_relative_raw_g1n_nonexpanding"
            and row.get("root_rewrite_attempt_count") == 1
            and utf16le_sha256(body) == row.get("reviewed_utf16le_sha256")
            and parse_coordinate(str(row["coordinate"]))[:2]
            in accepted_roots,
            "decision semantic or layout proof drifted",
        )
    overrides = {
        str(row["coordinate"]): str(row["reviewed_translation"])
        for row in decisions
        if str(row["action"]).startswith("translation_override")
    }
    promoted = {
        str(row["coordinate"])
        for row in decisions
        if str(row["action"]).endswith("runtime_promotion")
    }
    require(
        len(overrides) == 12
        and coordinate_digest(overrides) == EXPECTED_DIGESTS["override"]
        and len(promoted) == 16
        and coordinate_digest(promoted) == EXPECTED_DIGESTS["promoted"],
        "override or promotion partition drifted",
    )
    return overrides, promoted


def terminal_digest(
    records: Mapping[tuple[int, int], Any],
    terminal_roots: Sequence[tuple[int, int]],
) -> str:
    return sha256_bytes(
        "\0".join(
            terminal_text(records, terminal) for terminal in terminal_roots
        ).encode("utf-8")
    )


def build_selector_manifest(
    *,
    chunk: Mapping[str, Any],
    accepted_roots: set[tuple[int, int]],
    blocked_roots: set[tuple[int, int]],
    read_only_roots: set[tuple[int, int]],
    candidate: Mapping[tuple[int, int], Any],
    reviewed: Mapping[tuple[int, int], Any],
    current: Mapping[tuple[int, int], Any],
    graph: Mapping[tuple[int, int], Sequence[Mapping[str, Any]]],
    terminal_roots: Sequence[tuple[int, int]],
) -> list[list[Any]]:
    manifest: list[list[Any]] = []
    for site in chunk["sites"]:
        block_id, record_id, gap_id, _offset = RANKING.site_key(site)
        root = (block_id, record_id)
        edges = [
            edge
            for edge in graph[root]
            if int(edge["gap_id"]) == gap_id
        ]
        require(
            len(edges) == 1
            and tuple(edges[0]["target"]) == (0, SELECTOR),
            "selector branch site shape drifted",
        )
        if root in accepted_roots:
            kind = "accepted"
            selected = reviewed
        elif root in blocked_roots:
            kind = "blocked_pending"
            selected = candidate
        else:
            require(root in read_only_roots, "unclassified site root")
            kind = "read_only_nonpending"
            selected = candidate
        for ordinal, terminal in enumerate(terminal_roots):
            reviewed_assembly = site_assembly(
                selected, root, gap_id, terminal
            )
            current_assembly = site_assembly(
                current, root, gap_id, terminal
            )
            reviewed_widths = list(
                ASSIGNMENT.HELPER.LEGACY.line_widths(reviewed_assembly)
            )
            current_widths = list(
                ASSIGNMENT.HELPER.LEGACY.line_widths(current_assembly)
            )
            manifest.append([
                site,
                ordinal,
                sha256_bytes(reviewed_assembly.encode("utf-8")),
                sha256_bytes(current_assembly.encode("utf-8")),
                reviewed_widths,
                current_widths,
                current_relative_pass(reviewed_widths, current_widths),
                kind,
            ])
    return manifest


def family_leaves(
    candidate_edges: Mapping[
        tuple[int, int], Sequence[Mapping[str, Any]]
    ],
    source_edges: Mapping[
        tuple[int, int], Sequence[Mapping[str, Any]]
    ],
    selector: int,
) -> tuple[tuple[int, int], ...]:
    shape = RANKING.family_shape(
        candidate_edges, source_edges, (0, selector)
    )
    leaves = tuple(sorted(shape["candidate_leaves"]))
    require(len(leaves) == 7, "downstream selector shape drifted")
    return leaves


def build_downstream_manifest(
    *,
    blocked_roots: set[tuple[int, int]],
    candidate: Mapping[tuple[int, int], Any],
    current: Mapping[tuple[int, int], Any],
    source: Mapping[tuple[int, int], Any],
    candidate_edges: Mapping[
        tuple[int, int], Sequence[Mapping[str, Any]]
    ],
) -> list[list[Any]]:
    target_selectors = {772, 730}
    matches: list[
        tuple[
            tuple[int, int],
            int,
            list[Mapping[str, Any]],
        ]
    ] = []
    for root in blocked_roots:
        literal_count = len(ENGINE.parse_record_literals(candidate[root]))
        for gap_id in range(1, literal_count + 1):
            edges = sorted(
                (
                    edge
                    for edge in candidate_edges[root]
                    if int(edge["gap_id"]) == gap_id
                ),
                key=lambda row: int(row["offset"]),
            )
            if (
                len(edges) == 2
                and {int(edge["target"][1]) for edge in edges}
                == target_selectors
            ):
                matches.append((root, gap_id, edges))
    require(len(matches) == 1, "downstream two-selector gap drifted")
    root, gap_id, edges = matches[0]
    source_edges = RANKING.graph_edges(source)
    leaf_map = {
        selector: family_leaves(candidate_edges, source_edges, selector)
        for selector in target_selectors
    }

    def assembly(
        records: Mapping[tuple[int, int], Any],
        ordinals: Mapping[int, int],
    ) -> str:
        literals = ENGINE.parse_record_literals(records[root])
        result = literals[gap_id - 1].text
        for edge in edges:
            selector = int(edge["target"][1])
            result += terminal_text(
                records, leaf_map[selector][ordinals[selector]]
            )
        if gap_id < len(literals):
            result += literals[gap_id].text
        return result

    manifest: list[list[Any]] = []
    first, second = sorted(target_selectors, reverse=True)
    for first_ordinal in range(7):
        for second_ordinal in range(7):
            ordinals = {
                first: first_ordinal,
                second: second_ordinal,
            }
            reviewed_assembly = assembly(candidate, ordinals)
            current_assembly = assembly(current, ordinals)
            manifest.append([
                first_ordinal,
                second_ordinal,
                sha256_bytes(reviewed_assembly.encode("utf-8")),
                sha256_bytes(current_assembly.encode("utf-8")),
                list(
                    ASSIGNMENT.HELPER.LEGACY.line_widths(reviewed_assembly)
                ),
                list(
                    ASSIGNMENT.HELPER.LEGACY.line_widths(current_assembly)
                ),
            ])
    return manifest


def build_report() -> dict[str, Any]:
    assignment, evidence, decisions = validate_inputs()
    require(
        evidence["schema"] == PRIVATE_EVIDENCE_SCHEMA
        and evidence["method"] == METHOD
        and evidence["counts"] == EXPECTED_COUNTS,
        "private evidence header drifted",
    )
    chunk, accepted_roots, blocked_roots, read_only_roots = (
        validate_assignment(assignment, evidence)
    )
    overrides, promoted = validate_decisions(
        decisions, evidence, accepted_roots, blocked_roots
    )
    digests = evidence["digests"]
    require(
        digests["chunk_site_disposition_canonical_sha256"]
        == EXPECTED_DIGESTS["site_disposition"]
        and digests["decision_coordinate_sha256"]
        == EXPECTED_DIGESTS["decision"]
        and digests["override_coordinate_sha256"]
        == EXPECTED_DIGESTS["override"]
        and digests["promoted_coordinate_sha256"]
        == EXPECTED_DIGESTS["promoted"]
        and digests["selector238_branch_canonical_sha256"]
        == EXPECTED_DIGESTS["selector_branches"]
        and digests["downstream_cartesian_canonical_sha256"]
        == EXPECTED_DIGESTS["downstream"]
        and digests["reviewed_candidate_sha256"]
        == EXPECTED_SHA256["reviewed_candidate"]
        and digests["reverse_overlay_sha256"]
        == EXPECTED_SHA256["official_candidate"],
        "private evidence digest drifted",
    )
    proof = evidence["proof"]
    require(
        proof["all_pending_rows_freshly_reviewed"]
        and proof["fresh_semantic_review_limited_to_pending_rows"]
        and proof["historical_factuality_reviewed"]
        and proof["speaker_tone_reviewed"]
        and proof["maximum_rewrite_attempts_per_root"] == 1
        and proof["owned_overlap_automatic_promotion_count"] == 0
        and proof["prior_pending_evidence_automatic_promotion_count"] == 0
        and proof["terminal_automatic_promotion_count"] == 0
        and proof["terminal_records_read_only"]
        and not proof["shared_terminal_modified"]
        and proof["source_only_action_count"] == 0
        and proof["non_display_action_count"] == 0
        and not proof["steam_write_performed"],
        "private evidence proof drifted",
    )

    candidate, current, source, contexts, _pending = (
        ASSIGNMENT.RECORDS.load_records()
    )
    live_path = (
        WRAPPER.RANKING_WRAPPER.DEFAULT_STEAM_ROOT
        / "MSG_PK" / "JP" / "msggame.bin"
    )
    steam_before = sha256_file(live_path)
    require(
        steam_before == EXPECTED_SHA256["live_steam"],
        "live Steam archive drifted",
    )
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
            parse_coordinate(coordinate): translation
            for coordinate, translation in overrides.items()
        },
    )
    require(
        sha256_bytes(reviewed_blob) == EXPECTED_SHA256["reviewed_candidate"],
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
            and row["reviewed_utf16le_sha256"]
            == utf16le_sha256(literal_text(reviewed, coordinate))
            and row["reviewed_translation"]
            == literal_text(reviewed, coordinate),
            "decision text hash proof drifted",
        )
    changed_roots = {
        root for root in candidate if candidate[root].data != reviewed[root].data
    }
    require(
        changed_roots == accepted_roots and len(changed_roots) == 5,
        "changed root set drifted",
    )
    for root in changed_roots:
        before = ENGINE.parse_record_literals(candidate[root])
        after = ENGINE.parse_record_literals(reviewed[root])
        require(
            ENGINE.record_gap_bytes(candidate[root])
            == ENGINE.record_gap_bytes(reviewed[root])
            and len(before) == len(after)
            and all(
                old.text.count("\n") == new.text.count("\n")
                for old, new in zip(before, after)
            ),
            "record control or linebreak drifted",
        )
    reverse_blob = ENGINE.rebuild_packed_with_literals(
        reviewed_blob,
        {
            parse_coordinate(coordinate): literal_text(candidate, coordinate)
            for coordinate in overrides
        },
    )
    require(
        reverse_blob == candidate_blob
        and sha256_bytes(reverse_blob)
        == EXPECTED_SHA256["official_candidate"],
        "reverse overlay drifted",
    )

    terminal_roots = tuple((0, terminal) for terminal in TERMINALS)
    require(
        len(terminal_roots) == 7
        and terminal_digest(candidate, terminal_roots)
        == EXPECTED_SHA256["terminal_candidate"]
        and terminal_digest(current, terminal_roots)
        == EXPECTED_SHA256["terminal_current"]
        and terminal_digest(source, terminal_roots)
        == EXPECTED_SHA256["terminal_source"]
        and all(
            terminal_text(contexts[language], terminal) == ""
            for language in ("en", "sc", "tc")
            for terminal in terminal_roots
        ),
        "read-only terminal text guard drifted",
    )
    terminal_coordinates = {
        f"0:{terminal}:0" for terminal in TERMINALS
    }
    require(
        not terminal_coordinates
        & {str(row["coordinate"]) for row in decisions},
        "terminal decision detected",
    )
    official_rows = load_jsonl(OFFICIAL_LEDGER_PATH)
    terminal_rows = [
        row
        for row in official_rows
        if row.get("resource") == "pk_msggame"
        and str(row.get("coordinate")) in terminal_coordinates
    ]
    require(
        len(terminal_rows) == 7
        and all(
            row.get("runtime_review") == "pending"
            and row.get("scope_classification")
            == "runtime_fragment_pending"
            for row in terminal_rows
        ),
        "terminal ledger state drifted",
    )

    candidate_edges = RANKING.graph_edges(candidate)
    selector_manifest = build_selector_manifest(
        chunk=chunk,
        accepted_roots=accepted_roots,
        blocked_roots=blocked_roots,
        read_only_roots=read_only_roots,
        candidate=candidate,
        reviewed=reviewed,
        current=current,
        graph=candidate_edges,
        terminal_roots=terminal_roots,
    )
    kind_counts = Counter(str(row[-1]) for row in selector_manifest)
    require(
        len(selector_manifest) == 91
        and kind_counts
        == Counter({
            "accepted": 35,
            "blocked_pending": 21,
            "read_only_nonpending": 35,
        })
        and sum(bool(row[-2]) for row in selector_manifest) == 70
        and all(row[-2] for row in selector_manifest if row[-1] == "accepted")
        and canonical_sha256(selector_manifest)
        == EXPECTED_DIGESTS["selector_branches"],
        "selector branch manifest drifted",
    )
    downstream_manifest = build_downstream_manifest(
        blocked_roots=blocked_roots,
        candidate=candidate,
        current=current,
        source=source,
        candidate_edges=candidate_edges,
    )
    require(
        len(downstream_manifest) == 49
        and canonical_sha256(downstream_manifest)
        == EXPECTED_DIGESTS["downstream"],
        "downstream Cartesian manifest drifted",
    )
    require(
        len(promoted) == EXPECTED_COUNTS["promoted_pending_rows"]
        and sha256_file(live_path) == steam_before,
        "promotion count or Steam immutability drifted",
    )

    report = {
        "distribution_policy": {
            "private_decisions_stay_below_tmp": True,
            "private_evidence_stays_below_tmp": True,
            "tracked_builder_contains_dialogue_bodies": False,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_test_contains_dialogue_bodies": False,
            "tracked_validator_uses_frozen_private_hashes": True,
        },
        "guards": {
            "action_counts": EXPECTED_ACTION_COUNTS,
            "assignment_private_sha256":
                EXPECTED_SHA256["assignment_private"],
            "decision_coordinate_sha256": EXPECTED_DIGESTS["decision"],
            "decision_file_sha256": EXPECTED_SHA256["private_decisions"],
            "downstream_cartesian_sha256": EXPECTED_DIGESTS["downstream"],
            "evidence_file_sha256": EXPECTED_SHA256["private_evidence"],
            "official_candidate_sha256":
                EXPECTED_SHA256["official_candidate"],
            "official_ledger_sha256": EXPECTED_SHA256["official_ledger"],
            "override_coordinate_sha256": EXPECTED_DIGESTS["override"],
            "promoted_coordinate_sha256": EXPECTED_DIGESTS["promoted"],
            "reverse_overlay_sha256":
                EXPECTED_SHA256["official_candidate"],
            "reviewed_candidate_sha256":
                EXPECTED_SHA256["reviewed_candidate"],
            "selector_branch_manifest_sha256":
                EXPECTED_DIGESTS["selector_branches"],
            "steam_archive_sha256_after": sha256_file(live_path),
            "steam_archive_sha256_before": steam_before,
            "terminal_candidate_sha256":
                EXPECTED_SHA256["terminal_candidate"],
            "terminal_current_sha256": EXPECTED_SHA256["terminal_current"],
            "terminal_source_sha256": EXPECTED_SHA256["terminal_source"],
        },
        "method": METHOD,
        "proof": {
            "accepted_assemblies_current_relative_raw_g1n_nonexpanding":
                True,
            "all_changed_record_control_gaps_preserved": True,
            "all_literal_linebreak_counts_preserved": True,
            "all_pending_rows_freshly_reviewed": True,
            "blocked_roots_received_no_decisions": True,
            "downstream_cartesian_branches_computed_once": True,
            "historical_factuality_reviewed": True,
            "maximum_rewrite_attempts_per_root": 1,
            "non_display_action_count": 0,
            "owned_overlap_automatic_promotion_count": 0,
            "prior_pending_evidence_automatic_promotion_count": 0,
            "reverse_overlay_recovers_official_candidate": True,
            "root_independence_preserved": True,
            "selector_branches_computed_once": True,
            "source_only_action_count": 0,
            "speaker_tone_reviewed": True,
            "terminal_automatic_promotion_count": 0,
            "terminal_rows_pending_read_only": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": EXPECTED_COUNTS,
        "schema": PUBLIC_SCHEMA,
        "scope": {
            "chunk_id": CHUNK_ID,
            "selector": SELECTOR,
            "terminal_count": len(TERMINALS),
            "workload_weight": 261,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    validate_source_free(report)
    return report


def build_output() -> bytes:
    return serialized(build_report())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bootstrap-public", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    content = build_output()
    output_sha256 = sha256_bytes(content)
    if not args.bootstrap_public:
        require(
            EXPECTED_PUBLIC_FILE_SHA256 is not None
            and output_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
            f"public output hash drifted: {output_sha256}",
        )
        require(
            DEFAULT_PUBLIC_OUTPUT.is_file()
            and DEFAULT_PUBLIC_OUTPUT.read_bytes() == content,
            "public artifact drifted",
        )
    print(json.dumps({
        "accepted_pending": EXPECTED_COUNTS["accepted_pending_rows"],
        "blocked_pending": EXPECTED_COUNTS["blocked_pending_rows"],
        "output_sha256": output_sha256,
        "reviewed_candidate_sha256":
            EXPECTED_SHA256["reviewed_candidate"],
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
