#!/usr/bin/env python3
"""Validate PK selector-610 chunk 1 and emit a source-free checkpoint."""

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
ASSIGNMENT_BUILDER = WORKSTREAM / "build_pk_selector610_assignment_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector610_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector610_assignment_coverage.v1.json"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector568_1096_1174_consolidated_checkpoint.private.v1.jsonl"
)
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector610_chunk1_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector610_chunk1_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector610_chunk1_review.source_free.v1.json"
)

PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector610-chunk1-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector610-chunk1-review.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector610-chunk1-review.source-free.v1"
METHOD = (
    "official_fc157a_selector610_chunk1_fresh_semantic_"
    "seven_branch_and_owned1174_cross_product_review"
)
CHUNK_ID = 1
SELECTOR = 610
TERMINALS = tuple(range(2000, 2007))
DEPENDENCY_TERMINALS = tuple(range(2644, 2651))

EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "C0BC64F37C288E23F0C8E7437775BA4534A44F05C500A8B4E70E5965BCF9D5EA"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "50A4234CC7207FFF4BCC3049532EC78502E1E8F14565CF1FBFC5399A88D4D036"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "FD98F9289C6F1D429BF03B53252E9C1846262A29419E97ECDCE26695D91E9C2F"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "FC157A9907686D0EA6DC6C61C7785E81AC7F750100F2E1CDDE02DBF4F09F2DCA"
)
EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "940D7082F3289252C8C5EDEC134B4E70E540B951DFBCFBA081860CA248239B34"
)
EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "02FA41E288D8B302B87DB83142F216B5D3A7BF26449AA533471282C39B436224"
)
EXPECTED_CURRENT_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_CANDIDATE_SHA256 = (
    "07E65E6338D32C1FD13F17408F82A4133E55541C722874632948C7B36C909805"
)
EXPECTED_PROPOSAL_CANDIDATE_SHA256 = (
    "DBD3B0920E36CFE21FBAD038EB7B7EB4927983B305F59799FE07EF4084BECCCF"
)

EXPECTED_SITE_COUNT = 77
EXPECTED_ROOT_COUNT = 77
EXPECTED_PENDING_ROOTS = 29
EXPECTED_PENDING_ROWS = 53
EXPECTED_OWNED_ROOTS = 1
EXPECTED_ACCEPTED_SITES = 33
EXPECTED_REJECTED_SITES = 44
EXPECTED_ACCEPTED_PENDING = 53
EXPECTED_BLOCKED_PENDING = 0
EXPECTED_ACCEPTED_OWNED_PENDING = 1
EXPECTED_BLOCKED_OWNED_PENDING = 0
EXPECTED_ASSEMBLIES = 539
EXPECTED_DEPENDENCY_ASSEMBLIES = 49
EXPECTED_DECISIONS = 70
EXPECTED_OVERRIDES = 40
EXPECTED_KEEPS = 5

EXPECTED_SITE_SHA256 = (
    "5474E57EE4272EEE3E92CA45B5737352EC37DDF9FBB39B7DD7799DA1734E5B0C"
)
EXPECTED_ROOT_SHA256 = (
    "2E4047A673902834E475014AC6E6D72902492744637CB34072194A3E7C0FFDBB"
)
EXPECTED_PENDING_SHA256 = (
    "33602D1C44ECCD3C3A95A8E64A87593962FFEDDA728DE1A884B6EB64EB78D7D6"
)
EXPECTED_OWNED_ROOT_SHA256 = (
    "18BC8CC93F56BB7B352BD833045C7B002AB63B84339B17783C6A3D1F3DFA1A5F"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "90CA5FC881387633AF5BDBB901BBC7ED002A6C8949B89A9C85D0C3FC91B20855"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "6E4FB88B17F91060E7E6FE78B60059325C500ABA076DD3AA668C8869E29843E1"
)
EXPECTED_ACCEPTED_OWNED_PENDING_SHA256 = (
    "740BCBC7566C8BFF489D9D44842CABDBC51D8261B8DFA3E43460C3F27EF8846D"
)
EXPECTED_EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "1E0D042299E2FC005FF7B5B3688A91AA21F9FA7499DF0A04CE2CC254EEF36A6B"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "14B98775200AAEA64E93BD96C1B27B7C7275C79EF487BBB695CE33870499AD2E"
)
EXPECTED_KEEP_COORDINATE_SHA256 = (
    "7F122146A9DCC41C08867B3734C03356808AB7D428F130F062417874A686A609"
)
EXPECTED_ASSEMBLY_SHA256 = (
    "1620C1007E0B69432AA31BDDDAEEF8DD2E7CC0AF6295324985108E4FE720AF72"
)
EXPECTED_DEPENDENCY_SHA256 = (
    "A20089D1F1411137BB6243028FBE16B722B3AF33DA42B20F6CE5BF8B09DEF206"
)
EXPECTED_EVIDENCE_PAYLOAD_SHA256 = (
    "E8401C5BE90A5E1D228D61981AF137A6FD44480DCF766A8325A1B108433591F3"
)
EXPECTED_ACTION_COUNTS = {
    "hold": 44,
    "owned_overlap_translation_override_and_verification_renewal": 1,
    "translation_override": 27,
    "verification_renewal": 5,
}
EXPECTED_DECISION_ACTION_COUNTS = {
    "runtime_promotion": 30,
    "translation_override_and_runtime_promotion": 23,
    "translation_override_and_verification_renewal": 17,
}
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "2EAF65919343C560D4289715FB1D5792B07D6616B64498855FAB95D985346143"
)


class ReviewError(ValueError):
    """Raised when a frozen selector-610 review invariant drifts."""


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


ASSIGN = load_module(ASSIGNMENT_BUILDER, "selector610_chunk1_review_assignment")
ENGINE = ASSIGN.ENGINE


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


def parse_coordinate(value: str) -> tuple[int, int, int]:
    return tuple(map(int, value.split(":")))  # type: ignore[return-value]


def coordinate_digest(values: Iterable[str]) -> str:
    return ASSIGN.coordinate_digest(values)


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


def nonexpanding(
    reviewed: Sequence[Mapping[str, Any]],
    current: Sequence[Mapping[str, Any]],
) -> bool:
    return len(reviewed) == len(current) and all(
        int(left["raw_g1n_width_px"]) <= int(right["raw_g1n_width_px"])
        for left, right in zip(reviewed, current)
    )


def literal_text(
    records: Mapping[tuple[int, int], Any],
    coordinate: str,
) -> str:
    block_id, record_id, literal_id = parse_coordinate(coordinate)
    literals = ENGINE.parse_record_literals(records[(block_id, record_id)])
    require(literal_id < len(literals), f"literal absent: {coordinate}")
    return literals[literal_id].text


def record_gap_sha256(record: Any) -> str:
    framed = b"".join(
        len(gap).to_bytes(4, "little") + gap
        for gap in ENGINE.record_gap_bytes(record)
    )
    return sha256_bytes(framed)


def load_json_exact(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"BOM rejected: {path}")
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReviewError(f"invalid strict JSON: {path}") from exc
    require(isinstance(value, dict), f"JSON object required: {path}")
    return value


def load_decisions() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line in PRIVATE_DECISIONS_PATH.read_bytes().splitlines():
        if not line:
            continue
        try:
            row = json.loads(line.decode("utf-8", errors="strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ReviewError("invalid decision JSONL") from exc
        require(isinstance(row, dict), "decision row must be an object")
        result.append(row)
    return result


def adjacent(
    records: Mapping[tuple[int, int], Any],
    site: str,
) -> tuple[str, str]:
    return ASSIGN.LEGACY_ASSIGNMENT.adjacent_literals(records, site)


def validate_context(
    recorded: Mapping[str, Any],
    records: Mapping[tuple[int, int], Any],
    site: str,
    available: bool,
) -> None:
    left, right = adjacent(records, site)
    require(
        recorded.get("available") is available
        and recorded.get("left") == left
        and recorded.get("right") == right
        and recorded.get("joined_utf8_sha256")
        == sha256_bytes((left + right).encode("utf-8")),
        f"context drifted at {site}",
    )


def assert_source_free(value: Any) -> None:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            content,
        )
        is None,
        "public report contains CJK",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", content) is None,
        "public report contains an exact coordinate",
    )
    require('"translation"' not in content, "public report contains a body")


def build_report() -> dict[str, Any]:
    immutable = {
        ASSIGNMENT_BUILDER: EXPECTED_ASSIGNMENT_BUILDER_SHA256,
        ASSIGNMENT_PATH: EXPECTED_ASSIGNMENT_SHA256,
        ASSIGNMENT_PUBLIC_PATH: EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        OFFICIAL_LEDGER_PATH: EXPECTED_OFFICIAL_LEDGER_SHA256,
        PRIVATE_DECISIONS_PATH: EXPECTED_PRIVATE_DECISIONS_SHA256,
        PRIVATE_EVIDENCE_PATH: EXPECTED_PRIVATE_EVIDENCE_SHA256,
    }
    for path, expected in immutable.items():
        require(
            path.is_file() and sha256_file(path) == expected,
            f"immutable input drifted: {path}",
        )

    assignment = load_json_exact(ASSIGNMENT_PATH)
    chunk = assignment["chunks"][CHUNK_ID]
    require(
        chunk["chunk_id"] == CHUNK_ID
        and chunk["site_count"] == EXPECTED_SITE_COUNT
        and chunk["root_count"] == EXPECTED_ROOT_COUNT
        and chunk["pending_root_count"] == EXPECTED_PENDING_ROOTS
        and chunk["pending_row_upper_bound"] == EXPECTED_PENDING_ROWS
        and chunk["owned_overlap_root_count"] == EXPECTED_OWNED_ROOTS
        and chunk["site_sha256"] == EXPECTED_SITE_SHA256
        and chunk["root_sha256"] == EXPECTED_ROOT_SHA256
        and chunk["pending_sha256"] == EXPECTED_PENDING_SHA256
        and chunk["owned_overlap_root_sha256"] == EXPECTED_OWNED_ROOT_SHA256,
        "assignment chunk drifted",
    )
    candidate, current, source, contexts, _pending = ASSIGN.load_records()
    current_path = (
        ASSIGN.RANKING.DEFAULT_STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin"
    )
    require(
        sha256_file(current_path) == EXPECTED_CURRENT_SHA256,
        "current PK input drifted",
    )
    replacements, _pending_by_root = ASSIGN.RANKING.load_official_ledger(
        OFFICIAL_LEDGER_PATH
    )
    candidate_blob = ENGINE.rebuild_packed_with_literals(
        current_path.read_bytes(), replacements
    )
    require(
        sha256_bytes(candidate_blob) == EXPECTED_CANDIDATE_SHA256,
        "official candidate drifted",
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate_blob).archive
    )
    require(
        all(
            candidate_records[root].data == candidate[root].data
            for root in candidate
        ),
        "candidate record view drifted",
    )

    evidence = load_json_exact(PRIVATE_EVIDENCE_PATH)
    evidence_without_guards = dict(evidence)
    guards = evidence_without_guards.pop("guards")
    require(
        evidence.get("schema") == PRIVATE_EVIDENCE_SCHEMA
        and evidence.get("method") == METHOD
        and evidence.get("privacy")
        == {
            "classification": "private",
            "contains_dialogue_bodies": True,
            "public": False,
            "shared_integration_mutated": False,
            "steam_write_performed": False,
        }
        and guards.get("action_counts") == EXPECTED_ACTION_COUNTS
        and guards.get("payload_without_guards_canonical_sha256")
        == EXPECTED_EVIDENCE_PAYLOAD_SHA256
        and canonical_sha256(evidence_without_guards)
        == EXPECTED_EVIDENCE_PAYLOAD_SHA256,
        "private evidence header/guard drifted",
    )
    counts = evidence["counts"]
    require(
        counts
        == {
            "accepted_owned_overlap_pending":
                EXPECTED_ACCEPTED_OWNED_PENDING,
            "accepted_pending_coordinates": EXPECTED_ACCEPTED_PENDING,
            "accepted_roots": EXPECTED_ACCEPTED_SITES,
            "accepted_sites": EXPECTED_ACCEPTED_SITES,
            "assemblies": EXPECTED_ASSEMBLIES,
            "blocked_owned_overlap_pending":
                EXPECTED_BLOCKED_OWNED_PENDING,
            "blocked_pending_coordinates": EXPECTED_BLOCKED_PENDING,
            "blocked_roots": EXPECTED_REJECTED_SITES,
            "decision_coordinates": EXPECTED_DECISIONS,
            "dependency_cross_product_assemblies":
                EXPECTED_DEPENDENCY_ASSEMBLIES,
            "keep": EXPECTED_KEEPS,
            "reject": EXPECTED_REJECTED_SITES,
            "rewrite_coordinates": EXPECTED_OVERRIDES,
            "sites": EXPECTED_SITE_COUNT,
        },
        "private evidence counts drifted",
    )
    digests = evidence["digests"]
    require(
        digests.get("accepted_owned_overlap_pending_sha256")
        == EXPECTED_ACCEPTED_OWNED_PENDING_SHA256
        and digests.get("accepted_pending_coordinate_sha256")
        == EXPECTED_PENDING_SHA256
        and digests.get("accepted_site_sha256")
        == EXPECTED_ACCEPTED_SITE_SHA256
        and digests.get("assembly_canonical_sha256")
        == EXPECTED_ASSEMBLY_SHA256
        and digests.get("blocked_owned_overlap_pending_sha256")
        == EXPECTED_EMPTY_SHA256
        and digests.get("blocked_pending_coordinate_sha256")
        == EXPECTED_EMPTY_SHA256
        and digests.get("decision_coordinate_sha256")
        == EXPECTED_DECISION_COORDINATE_SHA256
        and digests.get("decision_file_sha256")
        == EXPECTED_PRIVATE_DECISIONS_SHA256
        and digests.get("dependency_cross_product_canonical_sha256")
        == EXPECTED_DEPENDENCY_SHA256
        and digests.get("keep_coordinate_sha256")
        == EXPECTED_KEEP_COORDINATE_SHA256
        and digests.get("proposal_candidate_sha256")
        == EXPECTED_PROPOSAL_CANDIDATE_SHA256
        and digests.get("rejected_site_sha256")
        == EXPECTED_REJECTED_SITE_SHA256
        and digests.get("translation_override_coordinate_sha256")
        == EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "private evidence digests drifted",
    )

    exact = evidence["exact_maps"]
    accepted_pending = list(map(str, exact["accepted_pending_coordinates"]))
    blocked_pending = list(map(str, exact["blocked_pending_coordinates"]))
    accepted_owned = list(
        map(str, exact["accepted_owned_overlap_pending_coordinates"])
    )
    blocked_owned = list(
        map(str, exact["blocked_owned_overlap_pending_coordinates"])
    )
    overrides = {
        str(coordinate): str(translation)
        for coordinate, translation
        in exact["translation_overrides"].items()
    }
    kept = list(map(str, exact["keep_coordinates"]))
    require(
        len(accepted_pending) == EXPECTED_ACCEPTED_PENDING
        and set(accepted_pending) == set(chunk["pending_coordinates"])
        and coordinate_digest(accepted_pending) == EXPECTED_PENDING_SHA256
        and not blocked_pending
        and len(accepted_owned) == EXPECTED_ACCEPTED_OWNED_PENDING
        and coordinate_digest(accepted_owned)
        == EXPECTED_ACCEPTED_OWNED_PENDING_SHA256
        and not blocked_owned
        and len(overrides) == EXPECTED_OVERRIDES
        and coordinate_digest(overrides) == EXPECTED_OVERRIDE_COORDINATE_SHA256
        and len(kept) == EXPECTED_KEEPS
        and coordinate_digest(kept) == EXPECTED_KEEP_COORDINATE_SHA256,
        "private exact maps drifted",
    )

    decision_rows = load_decisions()
    decision_by_coordinate: dict[str, dict[str, Any]] = {}
    decision_actions: Counter[str] = Counter()
    for row in decision_rows:
        coordinate = str(row.get("coordinate"))
        require(
            coordinate not in decision_by_coordinate,
            "duplicate decision coordinate",
        )
        parse_coordinate(coordinate)
        translation = row.get("translation")
        require(isinstance(translation, str), "decision body missing")
        translation.encode("utf-16le", errors="strict")
        predecessor = literal_text(candidate_records, coordinate)
        current_text = literal_text(current, coordinate)
        source_text = literal_text(source, coordinate)
        expected_translation = overrides.get(coordinate, predecessor)
        require(
            row.get("schema") == PRIVATE_DECISION_SCHEMA
            and row.get("method") == METHOD
            and row.get("resource") == "pk_msggame"
            and row.get("runtime_review") == "verified"
            and row.get("fresh_semantic_review") == "approved"
            and row.get("historical_factuality_review") == "approved"
            and row.get("speaker_tone_review") == "approved"
            and row.get("layout_review")
            == "current_relative_raw_g1n_nonexpanding"
            and translation == expected_translation
            and row.get("official_predecessor_translation") == predecessor
            and row.get("translation_utf16le_sha256")
            == sha256_bytes(translation.encode("utf-16le"))
            and row.get("official_predecessor_utf16le_sha256")
            == sha256_bytes(predecessor.encode("utf-16le"))
            and row.get("current_ko_utf16le_sha256")
            == sha256_bytes(current_text.encode("utf-16le"))
            and row.get("jp_source_utf16le_sha256")
            == sha256_bytes(source_text.encode("utf-16le"))
            and row.get("predecessor")
            == {
                "assignment_sha256": EXPECTED_ASSIGNMENT_SHA256,
                "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
                "ledger_sha256": EXPECTED_OFFICIAL_LEDGER_SHA256,
            },
            f"decision drifted: {coordinate}",
        )
        require(
            translation.count("\n") == predecessor.count("\n"),
            f"literal line breaks drifted: {coordinate}",
        )
        is_pending = coordinate in set(accepted_pending)
        is_override = coordinate in overrides
        expected_action = (
            "translation_override_and_runtime_promotion"
            if is_pending and is_override
            else "runtime_promotion"
            if is_pending
            else "translation_override_and_verification_renewal"
        )
        root = parse_coordinate(coordinate)[:2]
        owned_roots = {
            ASSIGN.RANKING.parse_root(value)
            for value in assignment["scope"]["owned_overlap_roots"]
        } & {
            ASSIGN.RANKING.parse_root(value) for value in chunk["roots"]
        }
        require(
            row.get("action") == expected_action
            and row.get("owned_overlap_root") is (root in owned_roots),
            f"decision action/owner drifted: {coordinate}",
        )
        decision_actions[expected_action] += 1
        decision_by_coordinate[coordinate] = row
    require(
        len(decision_rows) == EXPECTED_DECISIONS
        and set(decision_by_coordinate)
        == set(accepted_pending) | set(overrides)
        and coordinate_digest(decision_by_coordinate)
        == EXPECTED_DECISION_COORDINATE_SHA256
        and dict(sorted(decision_actions.items()))
        == EXPECTED_DECISION_ACTION_COUNTS,
        "decision universe/action counts drifted",
    )

    terminal_candidate = {
        terminal: ENGINE.parse_record_literals(
            candidate_records[(0, terminal)]
        )[0].text
        for terminal in TERMINALS
    }
    terminal_current = {
        terminal: ENGINE.parse_record_literals(current[(0, terminal)])[0].text
        for terminal in TERMINALS
    }
    terminal_source = {
        terminal: ENGINE.parse_record_literals(source[(0, terminal)])[0].text
        for terminal in TERMINALS
    }
    rows_by_site = {
        str(row["site"]): row for row in assignment["site_assignments"]
    }
    accepted_sites: list[str] = []
    rejected_sites: list[str] = []
    assembly_manifest: list[list[Any]] = []
    dependency_manifest: list[list[Any]] = []
    observed_actions: Counter[str] = Counter()
    for review in evidence["site_reviews"]:
        site = str(review.get("site"))
        assignment_row = rows_by_site.get(site)
        require(
            assignment_row is not None and site in chunk["sites"],
            f"review escaped assignment: {site}",
        )
        ordinal = int(assignment_row["ordinal"])
        require(
            review.get("ordinal") == ordinal
            and review.get("root") == assignment_row["root"]
            and review.get("coordinate") == assignment_row["left_coordinate"],
            f"review identity drifted: {site}",
        )
        root = ASSIGN.RANKING.parse_root(str(assignment_row["root"]))
        baseline_left, baseline_right = adjacent(candidate_records, site)
        current_left, current_right = adjacent(current, site)
        reviewed_left = review.get("reviewed_left_translation")
        reviewed_right = review.get("reviewed_right_translation")
        require(
            isinstance(reviewed_left, str)
            and isinstance(reviewed_right, str)
            and review.get("baseline_candidate_left") == baseline_left
            and review.get("baseline_candidate_right") == baseline_right,
            f"review body/baseline drifted: {site}",
        )
        authority = review["multilingual_authority"]
        require(
            authority.get("fresh_review_completed") is True
            and authority.get("historical_terms_reviewed") is True
            and authority.get("jp_is_semantic_authority") is True
            and authority.get("review_passes") == 2
            and authority.get("speaker_tone_reviewed") is True,
            f"semantic authority drifted: {site}",
        )
        validate_context(authority["jp"], source, site, True)
        for language in ("en", "sc", "tc"):
            validate_context(
                authority[language],
                contexts[language],
                site,
                bool(assignment_row["language_available"][language]),
            )

        decision = str(review.get("decision"))
        accepted = decision in {"keep", "rewrite"}
        require(
            accepted
            == bool(review.get("all_seven_register_branches_proven")),
            f"grammar disposition drifted: {site}",
        )
        if accepted:
            accepted_sites.append(site)
        else:
            require(
                decision == "reject"
                and isinstance(review.get("reject_reason"), str),
                f"reject reason absent: {site}",
            )
            rejected_sites.append(site)
        observed_actions[str(review.get("action"))] += 1
        branches = review.get("assemblies")
        require(
            isinstance(branches, list) and len(branches) == len(TERMINALS),
            f"branch cardinality drifted: {site}",
        )
        all_width = True
        for branch_index, terminal in enumerate(TERMINALS):
            branch = branches[branch_index]
            reviewed_assembly = (
                reviewed_left + terminal_candidate[terminal] + reviewed_right
            )
            current_assembly = (
                current_left + terminal_current[terminal] + current_right
            )
            reviewed_lines = line_metrics(reviewed_assembly)
            current_lines = line_metrics(current_assembly)
            width_pass = nonexpanding(reviewed_lines, current_lines)
            all_width = all_width and width_pass
            require(
                branch.get("branch_index") == branch_index
                and branch.get("terminal_coordinate")
                == f"0:{terminal}:0"
                and branch.get("reviewed_assembly") == reviewed_assembly
                and branch.get("current_assembly") == current_assembly
                and branch.get("reviewed_lines") == reviewed_lines
                and branch.get("current_lines") == current_lines
                and branch.get("current_terminal")
                == terminal_current[terminal]
                and branch.get("jp_terminal")
                == terminal_source[terminal]
                and branch.get("current_relative_raw_g1n_nonexpanding")
                is width_pass
                and branch.get("register_and_grammar_proven") is accepted,
                f"branch evidence drifted: {site}",
            )
            assembly_manifest.append(
                [
                    ordinal,
                    site,
                    terminal,
                    sha256_bytes(reviewed_assembly.encode("utf-8")),
                    sha256_bytes(current_assembly.encode("utf-8")),
                    width_pass,
                    accepted,
                ]
            )
        require(
            review.get("all_seven_width_branches_nonexpanding") is all_width
            and (not accepted or all_width),
            f"accepted width proof drifted: {site}",
        )
        control = review["control_and_boundary_proof"]
        require(
            control.get("baseline_record_gap_sha256")
            == record_gap_sha256(candidate_records[root])
            and control.get("literal_linebreak_count_preserved") is True
            and control.get("record_control_gaps_preserved") is True,
            f"control proof drifted: {site}",
        )

        dependency_rows = review.get("owned_dependency_assemblies")
        if root in owned_roots:
            require(
                review.get("owned_predecessor_root") is True
                and isinstance(dependency_rows, list)
                and len(dependency_rows) == EXPECTED_DEPENDENCY_ASSEMBLIES,
                "owned dependency review drifted",
            )
            candidate_literals = [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    candidate_records[root]
                )
            ]
            current_literals = [
                literal.text
                for literal in ENGINE.parse_record_literals(current[root])
            ]
            dependency_candidate = {
                terminal: ENGINE.parse_record_literals(
                    candidate_records[(0, terminal)]
                )[0].text
                for terminal in DEPENDENCY_TERMINALS
            }
            dependency_current = {
                terminal: ENGINE.parse_record_literals(
                    current[(0, terminal)]
                )[0].text
                for terminal in DEPENDENCY_TERMINALS
            }
            prefix_coordinate = f"{root[0]}:{root[1]}:0"
            prefix = str(decision_by_coordinate[prefix_coordinate]["translation"])
            index = 0
            for dependency_terminal in DEPENDENCY_TERMINALS:
                for terminal in TERMINALS:
                    branch = dependency_rows[index]
                    reviewed_assembly = (
                        prefix
                        + candidate_literals[1]
                        + dependency_candidate[dependency_terminal]
                        + reviewed_left
                        + terminal_candidate[terminal]
                    )
                    current_assembly = (
                        current_literals[0]
                        + current_literals[1]
                        + dependency_current[dependency_terminal]
                        + current_left
                        + terminal_current[terminal]
                    )
                    reviewed_lines = line_metrics(reviewed_assembly)
                    current_lines = line_metrics(current_assembly)
                    width_pass = nonexpanding(reviewed_lines, current_lines)
                    require(
                        width_pass
                        and branch.get(
                            "selector1174_terminal_coordinate"
                        )
                        == f"0:{dependency_terminal}:0"
                        and branch.get("selector610_terminal_coordinate")
                        == f"0:{terminal}:0"
                        and branch.get("reviewed_assembly")
                        == reviewed_assembly
                        and branch.get("current_assembly")
                        == current_assembly
                        and branch.get("reviewed_lines") == reviewed_lines
                        and branch.get("current_lines") == current_lines
                        and branch.get(
                            "current_relative_raw_g1n_nonexpanding"
                        )
                        is True,
                        "owned cross-product branch drifted",
                    )
                    dependency_manifest.append(
                        [
                            site,
                            dependency_terminal,
                            terminal,
                            sha256_bytes(reviewed_assembly.encode("utf-8")),
                            sha256_bytes(current_assembly.encode("utf-8")),
                            True,
                        ]
                    )
                    index += 1
        else:
            require(
                review.get("owned_predecessor_root") is False
                and dependency_rows == [],
                f"unexpected dependency rows: {site}",
            )

    require(
        len(accepted_sites) == EXPECTED_ACCEPTED_SITES
        and ASSIGN.site_digest(accepted_sites)
        == EXPECTED_ACCEPTED_SITE_SHA256
        and len(rejected_sites) == EXPECTED_REJECTED_SITES
        and ASSIGN.site_digest(rejected_sites)
        == EXPECTED_REJECTED_SITE_SHA256
        and len(assembly_manifest) == EXPECTED_ASSEMBLIES
        and canonical_sha256(assembly_manifest) == EXPECTED_ASSEMBLY_SHA256
        and len(dependency_manifest) == EXPECTED_DEPENDENCY_ASSEMBLIES
        and canonical_sha256(dependency_manifest)
        == EXPECTED_DEPENDENCY_SHA256
        and dict(sorted(observed_actions.items())) == EXPECTED_ACTION_COUNTS,
        "site/assembly disposition drifted",
    )

    proposal_blob = ENGINE.rebuild_packed_with_literals(
        candidate_blob,
        {
            parse_coordinate(coordinate): translation
            for coordinate, translation in overrides.items()
        },
    )
    require(
        sha256_bytes(proposal_blob) == EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        "proposal candidate drifted",
    )
    proposal_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(proposal_blob).archive
    )
    changed_roots = {
        root
        for root in candidate_records
        if candidate_records[root].data != proposal_records[root].data
    }
    require(
        changed_roots
        == {parse_coordinate(coordinate)[:2] for coordinate in overrides},
        "proposal changed roots drifted",
    )
    for root in changed_roots:
        require(
            record_gap_sha256(candidate_records[root])
            == record_gap_sha256(proposal_records[root]),
            f"proposal record controls drifted: {root}",
        )
    reverse_blob = ENGINE.rebuild_packed_with_literals(
        proposal_blob,
        {
            parse_coordinate(coordinate):
                literal_text(candidate_records, coordinate)
            for coordinate in overrides
        },
    )
    require(reverse_blob == candidate_blob, "reverse overlay drifted")

    report: dict[str, Any] = {
        "schema": PUBLIC_SCHEMA,
        "method": METHOD,
        "inputs": {
            "assignment_builder_sha256":
                EXPECTED_ASSIGNMENT_BUILDER_SHA256,
            "assignment_private_sha256": EXPECTED_ASSIGNMENT_SHA256,
            "assignment_public_sha256":
                EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
            "official_candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "official_integrated_ledger_sha256":
                EXPECTED_OFFICIAL_LEDGER_SHA256,
            "private_decisions_sha256":
                EXPECTED_PRIVATE_DECISIONS_SHA256,
            "private_evidence_sha256":
                EXPECTED_PRIVATE_EVIDENCE_SHA256,
        },
        "scope": {
            "chunk_id": CHUNK_ID,
            "owned_overlap_root_count": EXPECTED_OWNED_ROOTS,
            "owned_overlap_root_sha256": EXPECTED_OWNED_ROOT_SHA256,
            "pending_root_count": EXPECTED_PENDING_ROOTS,
            "pending_row_upper_bound": EXPECTED_PENDING_ROWS,
            "pending_sha256": EXPECTED_PENDING_SHA256,
            "resource": "MSG_PK/JP/msggame.bin",
            "root_count": EXPECTED_ROOT_COUNT,
            "root_sha256": EXPECTED_ROOT_SHA256,
            "selector": SELECTOR,
            "site_count": EXPECTED_SITE_COUNT,
            "site_sha256": EXPECTED_SITE_SHA256,
            "terminal_count": len(TERMINALS),
        },
        "review": {
            "accepted_root_count": EXPECTED_ACCEPTED_SITES,
            "accepted_site_count": EXPECTED_ACCEPTED_SITES,
            "accepted_site_sha256": EXPECTED_ACCEPTED_SITE_SHA256,
            "historical_factuality_review_sites": EXPECTED_SITE_COUNT,
            "jp_authority_sites": EXPECTED_SITE_COUNT,
            "rejected_root_count": EXPECTED_REJECTED_SITES,
            "rejected_site_count": EXPECTED_REJECTED_SITES,
            "rejected_site_sha256": EXPECTED_REJECTED_SITE_SHA256,
            "speaker_tone_review_sites": EXPECTED_SITE_COUNT,
        },
        "runtime_proof": {
            "all_accepted_branches_current_relative_nonexpanding": True,
            "assembly_branch_count": EXPECTED_ASSEMBLIES,
            "assembly_canonical_sha256": EXPECTED_ASSEMBLY_SHA256,
            "decision_action_counts": EXPECTED_DECISION_ACTION_COUNTS,
            "decision_coordinate_count": EXPECTED_DECISIONS,
            "decision_coordinate_sha256":
                EXPECTED_DECISION_COORDINATE_SHA256,
            "dependency_cross_product_branch_count":
                EXPECTED_DEPENDENCY_ASSEMBLIES,
            "dependency_cross_product_canonical_sha256":
                EXPECTED_DEPENDENCY_SHA256,
            "ghidra_contract_reused": True,
            "opcode_0143_call": True,
            "opcode_014a_jump": True,
            "runtime_grammar_repair": False,
            "selector_branch_count": len(TERMINALS),
        },
        "promotion": {
            "accepted_owned_overlap_pending_count":
                EXPECTED_ACCEPTED_OWNED_PENDING,
            "accepted_owned_overlap_pending_sha256":
                EXPECTED_ACCEPTED_OWNED_PENDING_SHA256,
            "accepted_pending_coordinate_count": EXPECTED_ACCEPTED_PENDING,
            "accepted_pending_coordinate_sha256": EXPECTED_PENDING_SHA256,
            "blocked_owned_overlap_pending_count":
                EXPECTED_BLOCKED_OWNED_PENDING,
            "blocked_owned_overlap_pending_sha256": EXPECTED_EMPTY_SHA256,
            "blocked_pending_coordinate_count": EXPECTED_BLOCKED_PENDING,
            "blocked_pending_coordinate_sha256": EXPECTED_EMPTY_SHA256,
            "keep_coordinate_count": EXPECTED_KEEPS,
            "keep_coordinate_sha256": EXPECTED_KEEP_COORDINATE_SHA256,
            "proposal_candidate_sha256":
                EXPECTED_PROPOSAL_CANDIDATE_SHA256,
            "translation_override_coordinate_count": EXPECTED_OVERRIDES,
            "translation_override_coordinate_sha256":
                EXPECTED_OVERRIDE_COORDINATE_SHA256,
        },
        "encoding_and_controls": {
            "all_changed_literals_strict_utf16le": True,
            "all_changed_literal_linebreak_counts_preserved": True,
            "all_changed_record_control_gaps_preserved": True,
            "reverse_overlay_exact": True,
        },
        "privacy": {
            "contains_commercial_source_text": False,
            "contains_dialogue_bodies": False,
            "contains_exact_coordinates": False,
            "contains_translations": False,
            "private_decisions_stay_below_tmp": True,
            "private_evidence_stays_below_tmp": True,
            "shared_integration_mutated": False,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    report["guards"] = {
        "payload_without_guards_canonical_sha256":
            canonical_sha256(report),
    }
    assert_source_free(report)
    return report


def serialized(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("ascii")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_PUBLIC_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(
        args.output.resolve() == DEFAULT_PUBLIC_OUTPUT.resolve(),
        "public output path is fixed",
    )
    report = build_report()
    content = serialized(report)
    output_sha256 = sha256_bytes(content)
    if EXPECTED_PUBLIC_FILE_SHA256 is not None:
        require(
            output_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
            f"public output hash drifted: {output_sha256}",
        )
    if args.check:
        require(
            args.output.is_file() and args.output.read_bytes() == content,
            "public artifact drifted",
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)
    print(
        json.dumps(
            {
                "accepted_pending": EXPECTED_ACCEPTED_PENDING,
                "dependency_branches": EXPECTED_DEPENDENCY_ASSEMBLIES,
                "output_sha256": output_sha256,
                "proposal_candidate_sha256":
                    EXPECTED_PROPOSAL_CANDIDATE_SHA256,
                "status": "PASS",
                "steam_write_performed": False,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
