#!/usr/bin/env python3
"""Build a PC-only, source-free validation record for msggame residual fixes.

This builder deliberately reads only the pinned Steam PC resources listed below.
It never opens a Switch resource, historic Korean resource, or generic Korean
overlay.  It emits review candidates only; it does not rebuild or write a game
resource.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any


WORKSTREAM = Path(__file__).resolve().parent
REPO_ROOT = WORKSTREAM.parents[1]
PARSER_PATH = REPO_ROOT / "workstreams" / "msggame" / "msggame_format.py"
SEED_PATH = WORKSTREAM / "private" / "manual_proposals.v1.json"
PRIVATE_OUTPUT = WORKSTREAM / "private" / "candidates.v1.jsonl"
PRIVATE_HOLD_OUTPUT = WORKSTREAM / "private" / "holds.v1.jsonl"
PRIVATE_REJECTION_OUTPUT = WORKSTREAM / "private" / "rejections.v1.jsonl"
VALIDATION_OUTPUT = WORKSTREAM / "validation.v1.json"
NORMALIZED_OUTPUT = (
    REPO_ROOT
    / "tmp"
    / "translation_quality_pc_msggame_residuals_v1"
    / "pk_msggame_candidates.v1.jsonl"
)
NORMALIZED_FIELD_ORDER = (
    "resource",
    "coordinate",
    "current_ko",
    "proposed_ko",
    "current_ko_utf16le_sha256",
    "proposed_ko_utf16le_sha256",
    "allowed_format_delta",
)


# Independent runtime-literal-composition review.  These coordinates remain in
# the private seed for traceability, but must not feed a generic overlay until
# a record-level composition-safe replacement is reviewed.
MANUAL_RUNTIME_REVIEW_HOLDS = {
    (17, 715, 0): "hold_runtime_literal_combination_requires_record_review",
    (17, 822, 0): "hold_runtime_literal_combination_requires_record_review",
}
MANUAL_RUNTIME_REVIEW_REJECTIONS = {
    (17, 943, 2): "reject_runtime_literal_combination_unsafe",
    (17, 944, 2): "reject_runtime_literal_combination_unsafe",
    (17, 1004, 1): "reject_runtime_literal_combination_unsafe",
}
AUTOMATIC_RUNTIME_BOUNDARY_HOLDS = {
    (6, 3778, 0): "hold_runtime_opcode_boundary_not_static_provable",
}


PC_PATHS = {
    "base_jp": Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
        r"\steam-jp-1.1.7-v0.8.0\originals\MSG\JP\msggame.bin"
    ),
    "base_current_ko": Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin"
    ),
    "pk_jp": Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
        r"\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msggame.bin"
    ),
    "pk_current_ko": Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
    ),
    "pk_en": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msggame.bin"),
    "pk_sc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msggame.bin"),
    "pk_tc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msggame.bin"),
}


EXPECTED_PACKED_SHA256 = {
    "base_jp": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    "base_current_ko": "8DBFCDB21BBDAAD4FE3928AD5B7AAA0D51E56D01F206DFE4D129E354FA5DEDE2",
    "pk_jp": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "pk_current_ko": "DE606E50C9A6241BD0B85D17A000394007952093984F75DB56E296E0CCDE6B01",
    "pk_en": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "pk_sc": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "pk_tc": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


RUNTIME_MARKER_RE = re.compile(r"Color\.(?:Blue|Default|Red|Green)")


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-16-le"))


def coordinate_key(coordinate: tuple[int, int, int]) -> str:
    return ":".join(str(value) for value in coordinate)


def visible_letter_count(text: str) -> int:
    return sum(character.isalpha() for character in text)


def normalized_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def edge_whitespace(line: str) -> tuple[str, str]:
    left_index = 0
    while left_index < len(line) and line[left_index].isspace():
        left_index += 1
    right_index = len(line)
    while right_index > left_index and line[right_index - 1].isspace():
        right_index -= 1
    return line[:left_index], line[right_index:]


def whitespace_codepoints(value: str) -> list[str]:
    return [f"U+{ord(character):04X}" for character in value]


def format_signature(text: str) -> dict[str, Any]:
    lines = text.split("\n")
    line_edges = [edge_whitespace(line) for line in lines]
    controls = [
        f"U+{ord(character):04X}"
        for character in text
        if character not in "\n\r\t" and unicodedata.category(character) in {"Cc", "Co"}
    ]
    return {
        "newline_count": text.count("\n"),
        "line_count": len(lines),
        "line_leading_whitespace": [
            whitespace_codepoints(leading) for leading, _trailing in line_edges
        ],
        "line_trailing_whitespace": [
            whitespace_codepoints(trailing) for _leading, trailing in line_edges
        ],
        "runtime_marker_tokens": RUNTIME_MARKER_RE.findall(text),
        "runtime_control_codepoints": controls,
    }


def load_msggame_module():
    if not PARSER_PATH.is_file():
        raise FileNotFoundError(f"msggame parser is missing: {PARSER_PATH}")
    spec = importlib.util.spec_from_file_location("pc_msggame_format", PARSER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load msggame parser: {PARSER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_literal_maps(
    parser: Any,
) -> tuple[
    dict[str, dict[tuple[int, int, int], str]],
    dict[str, dict[tuple[int, int], str]],
    dict[str, Any],
]:
    maps: dict[str, dict[tuple[int, int, int], str]] = {}
    record_maps: dict[str, dict[tuple[int, int], str]] = {}
    metadata: dict[str, Any] = {}
    for label, path in PC_PATHS.items():
        packed = path.read_bytes()
        actual_sha256 = sha256_bytes(packed)
        expected_sha256 = EXPECTED_PACKED_SHA256[label]
        if actual_sha256 != expected_sha256:
            raise ValueError(
                f"{label} SHA-256 changed: expected {expected_sha256}, got {actual_sha256}"
            )
        archive = parser.parse_packed_msggame(packed).archive
        literals = {
            (literal.block_id, literal.record_id, literal.literal_id): literal.text
            for literal in parser.iter_literals(archive)
        }
        maps[label] = literals
        record_maps[label] = {
            (record.block_id, record.record_id): "".join(
                literal.text for literal in parser.parse_record_literals(record)
            )
            for block in archive.blocks
            for record in block.records
        }
        metadata[label] = {
            "packed_sha256": actual_sha256,
            "literal_slot_count": len(literals),
        }
    if set(maps["base_jp"]) != set(maps["base_current_ko"]):
        raise ValueError("base JP and current KO literal coordinates differ")
    if set(maps["pk_jp"]) != set(maps["pk_current_ko"]):
        raise ValueError("PK JP and current KO literal coordinates differ")
    return maps, record_maps, metadata


def load_manual_seed() -> list[dict[str, Any]]:
    if not SEED_PATH.is_file():
        raise FileNotFoundError(f"private manual proposal seed is missing: {SEED_PATH}")
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    if seed.get("schema") != "pc-msggame-manual-proposals-v1":
        raise ValueError("unexpected private manual proposal seed schema")
    candidates = seed.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("private manual proposal seed has no candidates")
    seen: set[tuple[int, int, int]] = set()
    for item in candidates:
        coordinate = tuple(item.get("coordinate", ()))
        if len(coordinate) != 3 or not all(isinstance(value, int) for value in coordinate):
            raise ValueError(f"invalid manual coordinate: {item.get('coordinate')!r}")
        if coordinate in seen:
            raise ValueError(f"duplicate manual coordinate: {coordinate_key(coordinate)}")
        seen.add(coordinate)
        if not isinstance(item.get("proposed_ko"), str) or not item["proposed_ko"]:
            raise ValueError(f"missing proposed_ko at {coordinate_key(coordinate)}")
        if not isinstance(item.get("reason_code"), str) or not item["reason_code"]:
            raise ValueError(f"missing reason_code at {coordinate_key(coordinate)}")
    return candidates


def exact_pc_anchor_candidates(
    maps: dict[str, dict[tuple[int, int, int], str]],
) -> list[dict[str, Any]]:
    """Return only source-proven, visibly truncated PK strings.

    A different Korean wording for the same JP text is deliberately insufficient.
    This narrow detector requires the PK string to have two or fewer letters while
    the same JP PC base string has a complete, format-compatible Korean text.
    """

    base_by_jp: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
    for coordinate, jp_text in maps["base_jp"].items():
        base_by_jp[jp_text].append(coordinate)

    results: list[dict[str, Any]] = []
    for coordinate in sorted(maps["pk_jp"]):
        jp_text = maps["pk_jp"][coordinate]
        current_ko = maps["pk_current_ko"][coordinate]
        if visible_letter_count(jp_text) < 5 or visible_letter_count(current_ko) > 2:
            continue

        compatible_anchors: list[tuple[tuple[int, int, int], str]] = []
        for base_coordinate in base_by_jp.get(jp_text, []):
            base_ko = maps["base_current_ko"][base_coordinate]
            if normalized_text(base_ko) == normalized_text(current_ko):
                continue
            if visible_letter_count(base_ko) < visible_letter_count(current_ko) + 3:
                continue
            if format_signature(base_ko) != format_signature(current_ko):
                continue
            compatible_anchors.append((base_coordinate, base_ko))

        unique_texts = {text for _coordinate, text in compatible_anchors}
        if len(unique_texts) > 1:
            raise ValueError(
                "ambiguous exact-PC anchor proposals at " + coordinate_key(coordinate)
            )
        if not compatible_anchors:
            continue
        base_coordinate, proposed_ko = compatible_anchors[0]
        results.append(
            {
                "coordinate": coordinate,
                "proposed_ko": proposed_ko,
                "reason_code": "pc_exact_jp_anchor_target_truncated",
                "base_anchor_coordinate": base_coordinate,
            }
        )
    return results


def ascii_ellipsis_accounting(
    maps: dict[str, dict[tuple[int, int, int], str]],
    manual_items: list[dict[str, Any]],
) -> dict[str, int]:
    """Account for the initial machine-translation signal without over-fixing base."""

    pk_signal_coordinates = {
        coordinate
        for coordinate, text in maps["pk_current_ko"].items()
        if "..." in text
    }
    base_signal_coordinates = {
        coordinate
        for coordinate, text in maps["base_current_ko"].items()
        if "..." in text
    }
    manual_coordinates = {tuple(item["coordinate"]) for item in manual_items}
    manual_signal_coordinates = pk_signal_coordinates & manual_coordinates
    if pk_signal_coordinates != manual_signal_coordinates:
        missing = sorted(pk_signal_coordinates - manual_signal_coordinates)
        unexpected = sorted(manual_signal_coordinates - pk_signal_coordinates)
        raise ValueError(
            "ASCII ellipsis review drift; missing="
            + repr(missing)
            + " unexpected="
            + repr(unexpected)
        )
    return {
        "pk_ascii_ellipsis_detected": len(pk_signal_coordinates),
        "pk_ascii_ellipsis_direct_semantic_pass": len(manual_signal_coordinates),
        "base_ascii_ellipsis_detected": len(base_signal_coordinates),
        "base_ascii_ellipsis_included": 0,
        "base_ascii_ellipsis_excluded_after_direct_review": len(base_signal_coordinates),
    }


def pc_reference_texts(
    maps: dict[str, dict[tuple[int, int, int], str]], coordinate: tuple[int, int, int]
) -> dict[str, str | None]:
    return {
        "pc_jp": maps["pk_jp"].get(coordinate),
        "pc_en": maps["pk_en"].get(coordinate),
        "pc_sc": maps["pk_sc"].get(coordinate),
        "pc_tc": maps["pk_tc"].get(coordinate),
    }


def semantic_reference_coordinate(
    maps: dict[str, dict[tuple[int, int, int], str]],
    record_maps: dict[str, dict[tuple[int, int], str]],
    coordinate: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Find a PC EN/SC/TC-complete record for exactly the same PC JP literal.

    Some repeated strings are present at coordinates whose non-JP language
    variants intentionally omit that record.  A repeated PK coordinate may be
    used only when its JP literal is byte-for-byte identical, which lets the
    multilingual record context verify the same semantic unit without treating
    a different Korean translation as authority.
    """

    jp_text = maps["pk_jp"][coordinate]
    options = []
    for option, option_jp_text in maps["pk_jp"].items():
        if option_jp_text != jp_text:
            continue
        record_key = option[:2]
        if all(record_maps[label].get(record_key, "") for label in ("pk_en", "pk_sc", "pk_tc")):
            options.append(option)
    if not options:
        raise ValueError(
            "no PC EN/SC/TC-complete exact-JP semantic reference for "
            + coordinate_key(coordinate)
        )
    return min(options, key=lambda option: (option != coordinate, option))


def semantic_evidence(
    maps: dict[str, dict[tuple[int, int, int], str]],
    record_maps: dict[str, dict[tuple[int, int], str]],
    coordinate: tuple[int, int, int],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return private and source-free proof for the PC multilingual review."""

    reference_coordinate = semantic_reference_coordinate(maps, record_maps, coordinate)
    if maps["pk_jp"][reference_coordinate] != maps["pk_jp"][coordinate]:
        raise ValueError("semantic reference JP mismatch")
    record_key = reference_coordinate[:2]
    private_context = {
        "candidate_pc_jp": maps["pk_jp"][coordinate],
        "exact_jp_reference_coordinate": list(reference_coordinate),
        "reference_record_context": {
            "pc_jp": record_maps["pk_jp"][record_key],
            "pc_en": record_maps["pk_en"][record_key],
            "pc_sc": record_maps["pk_sc"][record_key],
            "pc_tc": record_maps["pk_tc"][record_key],
        },
    }
    source_free_context = {
        "status": "PASS",
        "verdict": "exact_pc_jp_and_pc_en_sc_tc_record_context_reviewed",
        "exact_jp_reference_coordinate": list(reference_coordinate),
        "exact_jp_match": True,
        "reference_record_context_utf16le_sha256": {
            "pc_jp": sha256_text(record_maps["pk_jp"][record_key]),
            "pc_en": sha256_text(record_maps["pk_en"][record_key]),
            "pc_sc": sha256_text(record_maps["pk_sc"][record_key]),
            "pc_tc": sha256_text(record_maps["pk_tc"][record_key]),
        },
    }
    return private_context, source_free_context


def make_candidate(
    *,
    maps: dict[str, dict[tuple[int, int, int], str]],
    record_maps: dict[str, dict[tuple[int, int], str]],
    item: dict[str, Any],
    category: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    coordinate = tuple(item["coordinate"])
    if coordinate not in maps["pk_current_ko"]:
        raise ValueError(f"candidate coordinate is absent: {coordinate_key(coordinate)}")
    current_ko = maps["pk_current_ko"][coordinate]
    proposed_ko = item["proposed_ko"]
    current_signature = format_signature(current_ko)
    proposed_signature = format_signature(proposed_ko)
    if current_signature != proposed_signature:
        raise ValueError(
            "format/runtime signature changed at " + coordinate_key(coordinate)
        )

    candidate_id = f"pk_msggame:{coordinate_key(coordinate)}"
    private_semantic_evidence, source_free_semantic_evidence = semantic_evidence(
        maps, record_maps, coordinate
    )
    private_candidate: dict[str, Any] = {
        "schema": "pc-msggame-private-candidate-v1",
        "candidate_id": candidate_id,
        "resource": "MSG_PK/JP/msggame.bin",
        "coordinate": list(coordinate),
        "category": category,
        "reason_code": item["reason_code"],
        "current_ko": current_ko,
        "proposed_ko": proposed_ko,
        "pc_reference_texts": pc_reference_texts(maps, coordinate),
        "current_ko_utf16le_sha256": sha256_text(current_ko),
        "proposed_ko_utf16le_sha256": sha256_text(proposed_ko),
        "format_signature": current_signature,
        "pc_multilingual_semantic_evidence": private_semantic_evidence,
    }
    if "base_anchor_coordinate" in item:
        base_coordinate = tuple(item["base_anchor_coordinate"])
        private_candidate["exact_pc_base_anchor"] = {
            "coordinate": list(base_coordinate),
            "base_jp": maps["base_jp"][base_coordinate],
            "base_current_ko": maps["base_current_ko"][base_coordinate],
        }

    source_free_candidate: dict[str, Any] = {
        "candidate_id": candidate_id,
        "resource": "MSG_PK/JP/msggame.bin",
        "coordinate": list(coordinate),
        "category": category,
        "reason_code": item["reason_code"],
        "pc_jp_utf16le_sha256": sha256_text(maps["pk_jp"][coordinate]),
        "current_ko_utf16le_sha256": sha256_text(current_ko),
        "proposed_ko_utf16le_sha256": sha256_text(proposed_ko),
        "format_signature": current_signature,
        "format_runtime_preserved": True,
        "pc_multilingual_semantic_verdict": source_free_semantic_evidence,
        "pc_reference_presence": {
            label: text is not None
            for label, text in pc_reference_texts(maps, coordinate).items()
            if label != "pc_jp"
        },
    }
    if "base_anchor_coordinate" in item:
        source_free_candidate["exact_pc_base_anchor_coordinate"] = list(
            item["base_anchor_coordinate"]
        )
        source_free_candidate["exact_pc_base_anchor_ko_utf16le_sha256"] = sha256_text(
            maps["base_current_ko"][tuple(item["base_anchor_coordinate"])]
        )
    return private_candidate, source_free_candidate


def make_hold(
    *,
    maps: dict[str, dict[tuple[int, int, int], str]],
    record_maps: dict[str, dict[tuple[int, int], str]],
    item: dict[str, Any],
    hold_reason_code: str = "hold_missing_full_pc_en_sc_tc_exact_jp_context",
    hold_verdict: str = "missing_full_pc_en_sc_tc_exact_jp_record_context",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Record an otherwise clear exact-anchor candidate excluded from generic use."""

    coordinate = tuple(item["coordinate"])
    current_ko = maps["pk_current_ko"][coordinate]
    proposed_ko = item["proposed_ko"]
    signature = format_signature(current_ko)
    if signature != format_signature(proposed_ko):
        raise ValueError("format/runtime signature changed at hold " + coordinate_key(coordinate))
    record_key = coordinate[:2]
    availability = {
        label: bool(record_maps[label].get(record_key, ""))
        for label in ("pk_en", "pk_sc", "pk_tc")
    }
    private_hold = {
        "schema": "pc-msggame-private-hold-v1",
        "resource": "MSG_PK/JP/msggame.bin",
        "coordinate": list(coordinate),
        "reason_code": hold_reason_code,
        "current_ko": current_ko,
        "proposed_ko": proposed_ko,
        "pc_reference_texts": pc_reference_texts(maps, coordinate),
        "exact_pc_base_anchor": {
            "coordinate": list(item["base_anchor_coordinate"]),
            "base_jp": maps["base_jp"][tuple(item["base_anchor_coordinate"])],
            "base_current_ko": maps["base_current_ko"][tuple(item["base_anchor_coordinate"])],
        },
        "current_ko_utf16le_sha256": sha256_text(current_ko),
        "proposed_ko_utf16le_sha256": sha256_text(proposed_ko),
        "format_signature": signature,
        "pc_multilingual_semantic_evidence_status": "HOLD",
        "pc_multilingual_record_context_availability": availability,
        "generic_overlay_eligible": False,
        "review_disposition": "HOLD",
    }
    source_free_hold = {
        "resource": "MSG_PK/JP/msggame.bin",
        "coordinate": list(coordinate),
        "reason_code": hold_reason_code,
        "pc_jp_utf16le_sha256": sha256_text(maps["pk_jp"][coordinate]),
        "current_ko_utf16le_sha256": sha256_text(current_ko),
        "proposed_ko_utf16le_sha256": sha256_text(proposed_ko),
        "format_signature": signature,
        "format_runtime_preserved": True,
        "generic_overlay_eligible": False,
        "pc_multilingual_semantic_verdict": {
            "status": "HOLD",
            "verdict": hold_verdict,
            "pc_record_context_availability": availability,
        },
    }
    return private_hold, source_free_hold


def make_manual_runtime_disposition(
    *,
    maps: dict[str, dict[tuple[int, int, int], str]],
    record_maps: dict[str, dict[tuple[int, int], str]],
    item: dict[str, Any],
    disposition: str,
    review_reason_code: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Record a manual candidate withheld after full literal-composition review."""

    if disposition not in {"HOLD", "REJECT"}:
        raise ValueError(f"unsupported manual review disposition: {disposition}")
    private_record, source_free_record = make_candidate(
        maps=maps,
        record_maps=record_maps,
        item=item,
        category="manual_runtime_literal_composition_review",
    )
    private_record["schema"] = "pc-msggame-private-runtime-review-v1"
    private_record["review_disposition"] = disposition
    private_record["review_reason_code"] = review_reason_code
    source_free_record["review_disposition"] = disposition
    source_free_record["review_reason_code"] = review_reason_code
    source_free_record["generic_overlay_eligible"] = False
    return private_record, source_free_record


def build() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
]:
    parser = load_msggame_module()
    maps, record_maps, metadata = load_literal_maps(parser)
    manual_items_all = load_manual_seed()
    ellipsis_summary = ascii_ellipsis_accounting(maps, manual_items_all)
    manual_by_coordinate = {
        tuple(item["coordinate"]): item for item in manual_items_all
    }
    review_coordinates = (
        set(MANUAL_RUNTIME_REVIEW_HOLDS) | set(MANUAL_RUNTIME_REVIEW_REJECTIONS)
    )
    if set(MANUAL_RUNTIME_REVIEW_HOLDS) & set(MANUAL_RUNTIME_REVIEW_REJECTIONS):
        raise ValueError("manual runtime review HOLD/REJECT coordinates overlap")
    unknown_review_coordinates = sorted(review_coordinates - set(manual_by_coordinate))
    if unknown_review_coordinates:
        raise ValueError(
            "manual runtime review coordinate is absent from seed: "
            + ", ".join(coordinate_key(coordinate) for coordinate in unknown_review_coordinates)
        )
    manual_items = [
        item
        for item in manual_items_all
        if tuple(item["coordinate"]) not in review_coordinates
    ]
    manual_hold_items = [
        manual_by_coordinate[coordinate]
        for coordinate in sorted(MANUAL_RUNTIME_REVIEW_HOLDS)
    ]
    manual_rejection_items = [
        manual_by_coordinate[coordinate]
        for coordinate in sorted(MANUAL_RUNTIME_REVIEW_REJECTIONS)
    ]
    automatic_items_all = exact_pc_anchor_candidates(maps)
    automatic_items: list[dict[str, Any]] = []
    automatic_multilingual_hold_items: list[dict[str, Any]] = []
    automatic_runtime_boundary_hold_items: list[dict[str, Any]] = []
    automatic_by_coordinate = {
        tuple(item["coordinate"]): item for item in automatic_items_all
    }
    unknown_automatic_runtime_holds = sorted(
        set(AUTOMATIC_RUNTIME_BOUNDARY_HOLDS) - set(automatic_by_coordinate)
    )
    if unknown_automatic_runtime_holds:
        raise ValueError(
            "automatic runtime boundary HOLD is absent from exact-anchor set: "
            + ", ".join(
                coordinate_key(coordinate)
                for coordinate in unknown_automatic_runtime_holds
            )
        )
    for item in automatic_items_all:
        coordinate = tuple(item["coordinate"])
        if coordinate in AUTOMATIC_RUNTIME_BOUNDARY_HOLDS:
            automatic_runtime_boundary_hold_items.append(item)
            continue
        try:
            semantic_reference_coordinate(maps, record_maps, coordinate)
        except ValueError:
            automatic_multilingual_hold_items.append(item)
        else:
            automatic_items.append(item)

    manual_coordinates = {tuple(item["coordinate"]) for item in manual_items_all}
    automatic_coordinates = {tuple(item["coordinate"]) for item in automatic_items}
    overlap = sorted(manual_coordinates & automatic_coordinates)
    if overlap:
        raise ValueError(
            "manual and exact-PC anchor candidates overlap: "
            + ", ".join(coordinate_key(coordinate) for coordinate in overlap)
        )

    private_candidates: list[dict[str, Any]] = []
    source_free_candidates: list[dict[str, Any]] = []
    private_holds: list[dict[str, Any]] = []
    source_free_holds: list[dict[str, Any]] = []
    private_rejections: list[dict[str, Any]] = []
    source_free_rejections: list[dict[str, Any]] = []
    for category, items in (
        ("manual_direct_pc_multilingual", manual_items),
        ("pc_exact_jp_anchor_recovery", automatic_items),
    ):
        for item in items:
            private_candidate, source_free_candidate = make_candidate(
                maps=maps, record_maps=record_maps, item=item, category=category
            )
            private_candidates.append(private_candidate)
            source_free_candidates.append(source_free_candidate)
    for item in automatic_multilingual_hold_items:
        private_hold, source_free_hold = make_hold(
            maps=maps, record_maps=record_maps, item=item
        )
        private_holds.append(private_hold)
        source_free_holds.append(source_free_hold)
    for item in automatic_runtime_boundary_hold_items:
        coordinate = tuple(item["coordinate"])
        private_hold, source_free_hold = make_hold(
            maps=maps,
            record_maps=record_maps,
            item=item,
            hold_reason_code=AUTOMATIC_RUNTIME_BOUNDARY_HOLDS[coordinate],
            hold_verdict="runtime_opcode_boundary_not_static_provable",
        )
        private_holds.append(private_hold)
        source_free_holds.append(source_free_hold)
    for item in manual_hold_items:
        coordinate = tuple(item["coordinate"])
        private_hold, source_free_hold = make_manual_runtime_disposition(
            maps=maps,
            record_maps=record_maps,
            item=item,
            disposition="HOLD",
            review_reason_code=MANUAL_RUNTIME_REVIEW_HOLDS[coordinate],
        )
        private_holds.append(private_hold)
        source_free_holds.append(source_free_hold)
    for item in manual_rejection_items:
        coordinate = tuple(item["coordinate"])
        private_rejection, source_free_rejection = make_manual_runtime_disposition(
            maps=maps,
            record_maps=record_maps,
            item=item,
            disposition="REJECT",
            review_reason_code=MANUAL_RUNTIME_REVIEW_REJECTIONS[coordinate],
        )
        private_rejections.append(private_rejection)
        source_free_rejections.append(source_free_rejection)

    private_candidates.sort(key=lambda item: tuple(item["coordinate"]))
    source_free_candidates.sort(key=lambda item: tuple(item["coordinate"]))
    private_holds.sort(key=lambda item: tuple(item["coordinate"]))
    source_free_holds.sort(key=lambda item: tuple(item["coordinate"]))
    private_rejections.sort(key=lambda item: tuple(item["coordinate"]))
    source_free_rejections.sort(key=lambda item: tuple(item["coordinate"]))
    validation = {
        "schema": "pc-msggame-residuals-validation-v1",
        "scope": {
            "resource": "MSG_PK/JP/msggame.bin",
            "allowed_evidence": [
                "pristine Steam PC JP",
                "current Steam PC Korean",
                "Steam PC EN",
                "Steam PC SC",
                "Steam PC TC",
                "current Steam PC base Korean exact-JP anchors only for visibly truncated PK targets",
            ],
            "explicitly_excluded": [
                "Nintendo Switch Korean",
                "historic Korean outputs",
                "generic Korean overlays",
            ],
        },
        "input_contract": metadata,
        "candidate_counts": {
            "manual_direct_pc_multilingual_detected": len(manual_items_all),
            "manual_direct_pc_multilingual": len(manual_items),
            "manual_runtime_literal_combination_hold": len(manual_hold_items),
            "manual_runtime_literal_combination_rejected": len(manual_rejection_items),
            "pc_exact_jp_anchor_detected": len(automatic_items_all),
            "pc_exact_jp_anchor_recovery": len(automatic_items),
            "hold_missing_full_pc_en_sc_tc_context": len(
                automatic_multilingual_hold_items
            ),
            "pc_exact_jp_anchor_runtime_boundary_hold": len(
                automatic_runtime_boundary_hold_items
            ),
            "hold_total": len(source_free_holds),
            "rejection_total": len(source_free_rejections),
            "total": len(source_free_candidates),
        },
        "ascii_ellipsis_signal_review": ellipsis_summary,
        "candidates": source_free_candidates,
        "holds": source_free_holds,
        "rejections": source_free_rejections,
        "game_resource_written": False,
    }
    return private_candidates, private_holds, private_rejections, validation


def write_outputs(
    private_candidates: list[dict[str, Any]],
    private_holds: list[dict[str, Any]],
    private_rejections: list[dict[str, Any]],
    validation: dict[str, Any],
) -> None:
    PRIVATE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PRIVATE_OUTPUT.write_text(
        "".join(
            json.dumps(candidate, ensure_ascii=False, sort_keys=True) + "\n"
            for candidate in private_candidates
        ),
        encoding="utf-8",
    )
    PRIVATE_HOLD_OUTPUT.write_text(
        "".join(
            json.dumps(hold, ensure_ascii=False, sort_keys=True) + "\n"
            for hold in private_holds
        ),
        encoding="utf-8",
    )
    PRIVATE_REJECTION_OUTPUT.write_text(
        "".join(
            json.dumps(rejection, ensure_ascii=False, sort_keys=True) + "\n"
            for rejection in private_rejections
        ),
        encoding="utf-8",
    )
    normalized_metadata = write_normalized_payload_from_private()
    validation["normalized_payload"] = normalized_metadata
    VALIDATION_OUTPUT.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_normalized_payload_from_private() -> dict[str, Any]:
    """Emit the minimal generic-builder input from private PASS candidates only.

    The payload contains Korean current/proposed strings but no commercial JP,
    EN, SC, or TC source text.  It is intentionally derived by reading the
    already-written private candidate JSONL, rather than by writing Steam or an
    overlay resource.
    """

    if not PRIVATE_OUTPUT.is_file():
        raise FileNotFoundError(f"private PASS candidate file is missing: {PRIVATE_OUTPUT}")
    private_candidates = [
        json.loads(line)
        for line in PRIVATE_OUTPUT.read_text(encoding="utf-8").splitlines()
        if line
    ]
    rows: list[dict[str, Any]] = []
    seen_coordinates: set[str] = set()
    for candidate in private_candidates:
        coordinate_values = candidate.get("coordinate")
        if (
            not isinstance(coordinate_values, list)
            or len(coordinate_values) != 3
            or not all(isinstance(value, int) for value in coordinate_values)
        ):
            raise ValueError(f"invalid private candidate coordinate: {coordinate_values!r}")
        coordinate = coordinate_key(tuple(coordinate_values))
        if coordinate in seen_coordinates:
            raise ValueError(f"duplicate normalized coordinate: {coordinate}")
        seen_coordinates.add(coordinate)
        current_ko = candidate.get("current_ko")
        proposed_ko = candidate.get("proposed_ko")
        if not isinstance(current_ko, str) or not isinstance(proposed_ko, str):
            raise ValueError(f"missing Korean payload text at {coordinate}")
        if sha256_text(current_ko) != candidate.get("current_ko_utf16le_sha256"):
            raise ValueError(f"current Korean hash mismatch at {coordinate}")
        if sha256_text(proposed_ko) != candidate.get("proposed_ko_utf16le_sha256"):
            raise ValueError(f"proposed Korean hash mismatch at {coordinate}")
        if format_signature(current_ko) != format_signature(proposed_ko):
            raise ValueError(f"format delta is not empty at {coordinate}")
        row = {
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "current_ko": current_ko,
            "proposed_ko": proposed_ko,
            "current_ko_utf16le_sha256": candidate["current_ko_utf16le_sha256"],
            "proposed_ko_utf16le_sha256": candidate["proposed_ko_utf16le_sha256"],
            "allowed_format_delta": [],
        }
        if tuple(row) != NORMALIZED_FIELD_ORDER:
            raise AssertionError("normalized row field order changed")
        rows.append(row)
    rows.sort(key=lambda row: tuple(int(value) for value in row["coordinate"].split(":")))
    payload = "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows
    )
    NORMALIZED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    NORMALIZED_OUTPUT.write_text(payload, encoding="utf-8")
    payload_sha256 = sha256_bytes(NORMALIZED_OUTPUT.read_bytes())
    return {
        "path": NORMALIZED_OUTPUT.relative_to(REPO_ROOT).as_posix(),
        "sha256": payload_sha256,
        "candidate_count": len(rows),
        "field_order": list(NORMALIZED_FIELD_ORDER),
        "commercial_source_text_included": False,
        "steam_or_overlay_written": False,
    }


def refresh_normalized_payload_from_private() -> dict[str, Any]:
    """Refresh only the generic payload and source-free metadata.

    This path intentionally does not call ``build()``: it reads the existing
    private PASS JSONL and source-free validation file, then writes only the
    ignored ``tmp`` payload and this workstream's validation record.
    """

    if not VALIDATION_OUTPUT.is_file():
        raise FileNotFoundError(f"source-free validation file is missing: {VALIDATION_OUTPUT}")
    validation = json.loads(VALIDATION_OUTPUT.read_text(encoding="utf-8"))
    metadata = write_normalized_payload_from_private()
    expected_count = validation.get("candidate_counts", {}).get("total")
    if metadata["candidate_count"] != expected_count:
        raise ValueError(
            "private PASS count does not match source-free validation: "
            f"{metadata['candidate_count']} != {expected_count}"
        )
    validation["normalized_payload"] = metadata
    VALIDATION_OUTPUT.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--write",
        action="store_true",
        help="write private candidate details and the source-free validation record",
    )
    modes.add_argument(
        "--write-normalized",
        action="store_true",
        help="read private PASS candidates only and refresh the generic input payload",
    )
    args = parser.parse_args()
    if args.write_normalized:
        metadata = refresh_normalized_payload_from_private()
        print(
            "normalized_private_candidates={count} sha256={sha256} wrote=yes".format(
                count=metadata["candidate_count"], sha256=metadata["sha256"]
            )
        )
        return 0
    private_candidates, private_holds, private_rejections, validation = build()
    if args.write:
        write_outputs(
            private_candidates,
            private_holds,
            private_rejections,
            validation,
        )
    counts = validation["candidate_counts"]
    print(
        "manual_direct_pc_multilingual={manual} "
        "pc_exact_jp_anchor_recovery={automatic} holds={holds} rejections={rejections} total={total} wrote={wrote}".format(
            manual=counts["manual_direct_pc_multilingual"],
            automatic=counts["pc_exact_jp_anchor_recovery"],
            holds=counts["hold_total"],
            rejections=counts["rejection_total"],
            total=counts["total"],
            wrote="yes" if args.write else "no",
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
