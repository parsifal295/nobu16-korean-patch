#!/usr/bin/env python3
"""Generate conservative msgdata surname/given-name translations.

The private full-name catalog is aligned by officer id, while ``msgdata.bin``
stores reusable surname and given-name fragments at unrelated ids.  A fragment
pair is accepted only when its Simplified-Chinese, Japanese, and English text
all match an exact prefix/suffix decomposition of the same full name.  English
text alone is never a key, so homophones such as ``小田`` and ``織田`` remain
separate.

The tool writes a private ``nobu16.kr.translation.v1`` catalog, exports a
source-text-free public overlay through the existing exporter, and proves a
deterministic build plus public-recipe replay against an isolated stock copy.
It never writes to an installed game resource.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import build_common_message_overlay as common
import build_file_only_msg_recipe as recipe_core
import export_common_message_overlay as common_export
from nobu16_lz4 import LZ4Error, decompress_wrapper
from nobu16_msg_table import MessageTableError, parse_message_table, rebuild_message_table


PRIVATE_SCHEMA = "nobu16.kr.translation.v1"
FULL_REPORT_SCHEMA = "nobu16.kr.officer-name-generation-report.v1"
COMPONENT_REPORT_SCHEMA = "nobu16.kr.officer-name-component-report.v1"
RESOURCE_NAME = "msgdata.bin"
RESOURCE_SC = "MSG_PK/SC/msgdata.bin"
LANGUAGES = ("SC", "EN", "JP")
DEFAULT_OVERLAY_ID = "msgdata-officer-names-0000-2399-v0.1"

# Representative famous officers plus the three longest Korean names in the
# current 0..2206 catalog.  These are validation gates only: the matcher still
# has to discover the exact aligned triples without consulting this table.
REGRESSION_EXPECTATIONS: dict[int, dict[str, Any]] = {
    47: {"ko": "아케치 미츠히데", "surname_ids": [4], "given_ids": [1337, 7691]},
    216: {"ko": "이시다 미츠나리", "surname_ids": [688, 11235], "given_ids": [1487, 7599]},
    558: {"ko": "오다 노부나가", "surname_ids": [84], "given_ids": [1266]},
    826: {"ko": "구로다 간베에", "surname_ids": [143], "given_ids": [1615]},
    994: {"ko": "사나다 유키무라", "surname_ids": [653], "given_ids": [1395]},
    1059: {"ko": "시마즈 요시히로", "surname_ids": [189], "given_ids": [1126, 7886]},
    1255: {"ko": "다케나카 한베에", "surname_ids": [745], "given_ids": [1346]},
    1272: {"ko": "다테 마사무네", "surname_ids": [228, 10061], "given_ids": [1063, 7289]},
    1315: {"ko": "조소카베 모토치카", "surname_ids": [760], "given_ids": [1640, 7716]},
    1817: {"ko": "혼다 다다카츠", "surname_ids": [319], "given_ids": [1237, 7150]},
    1830: {"ko": "마에다 케이지", "surname_ids": [323], "given_ids": [1287]},
    2013: {"ko": "모리 모토나리", "surname_ids": [905], "given_ids": [1642]},
    239: {"ko": "이타베오카 고세츠사이", "surname_ids": [845], "given_ids": [1203]},
    1681: {"ko": "히토츠야나기 나오모리", "surname_ids": [409], "given_ids": [1957, 7072]},
    1885: {"ko": "마츠다이라 다다아키라", "surname_ids": [329], "given_ids": [2661]},
}

FULL_ROOT_KEYS = {
    "schema",
    "scope",
    "version",
    "base_languages",
    "source_files",
    "entries",
}
FULL_ENTRY_REQUIRED_KEYS = {"id", "source", "ko"}
FULL_ENTRY_ALLOWED_KEYS = FULL_ENTRY_REQUIRED_KEYS | {"status"}
SOURCE_DESCRIPTOR_KEYS = {"path", "sha256"}


class OfficerComponentError(ValueError):
    """Raised when an input or a component mapping is unsafe or inconsistent."""


Triple = tuple[str, str, str]


@dataclass(frozen=True)
class StockTable:
    language: str
    stock_path: Path
    stock_blob: bytes
    raw: bytes
    texts: tuple[str, ...]


@dataclass(frozen=True)
class ComponentCandidate:
    surname_key: Triple
    given_key: Triple
    surname_ids: tuple[int, ...]
    given_ids: tuple[int, ...]
    english_orders: tuple[str, ...]


@dataclass(frozen=True)
class OfficerMatch:
    officer_id: int
    surname_ko: str
    given_ko: str
    candidate: ComponentCandidate
    source: dict[str, str]
    method: str


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def count_cjk_unified(text: str) -> int:
    ranges = (
        (0x3400, 0x4DBF),
        (0x4E00, 0x9FFF),
        (0x20000, 0x2EBEF),
        (0x30000, 0x323AF),
    )
    return sum(
        1
        for character in text
        if any(start <= ord(character) <= end for start, end in ranges)
    )


def contains_source_original_fields(value: Any) -> bool:
    forbidden = {"source", "source_sc", "source_en", "source_jp", "SC", "EN", "JP", "text"}
    if isinstance(value, dict):
        return any(
            key in forbidden
            or contains_source_original_fields(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(contains_source_original_fields(child) for child in value)
    return False


def contains_commercial_text_fields(value: Any) -> bool:
    forbidden = {
        "text",
        "source_text",
        "source_sc",
        "source_en",
        "source_jp",
        "original",
        "original_text",
        "SC",
        "EN",
        "JP",
    }
    if isinstance(value, dict):
        return any(
            key in forbidden or contains_commercial_text_fields(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(contains_commercial_text_fields(child) for child in value)
    return False


def _strict_json(path: Path) -> dict[str, Any]:
    value, _ = common.load_json_strict(path)
    return value


def _read_jsonl(path: Path) -> tuple[str, ...]:
    rows: list[str] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise OfficerComponentError(
                f"invalid JSONL at {path}:{line_number}: {exc}"
            ) from exc
        if not isinstance(row, dict) or set(row) != {"id", "text", "translation"}:
            raise OfficerComponentError(
                f"unexpected JSONL row shape at {path}:{line_number}"
            )
        if type(row["id"]) is not int or row["id"] != len(rows):
            raise OfficerComponentError(
                f"unaligned JSONL id at {path}:{line_number}"
            )
        if not isinstance(row["text"], str) or row["translation"] != "":
            raise OfficerComponentError(
                f"JSONL must contain stock text and an empty translation at "
                f"{path}:{line_number}"
            )
        rows.append(row["text"])
    if not rows:
        raise OfficerComponentError(f"empty message JSONL: {path}")
    return tuple(rows)


def _parse_stock(path: Path) -> tuple[bytes, bytes, tuple[str, ...]]:
    blob = path.read_bytes()
    _, raw = decompress_wrapper(blob)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise OfficerComponentError(
            f"stock message table is not byte-exact on rebuild: {path}"
        )
    return blob, raw, table.texts


def load_stock_table(
    language: str,
    table_input: Path,
    stock_path: Path | None,
) -> StockTable:
    table_input = table_input.resolve()
    if stock_path is None:
        if table_input.suffix.lower() in {".jsonl", ".ndjson"}:
            raise OfficerComponentError(
                f"{language} JSONL input requires a matching --stock-{language.lower()}"
            )
        stock_path = table_input
    stock_path = stock_path.resolve()
    stock_blob, raw, stock_texts = _parse_stock(stock_path)

    if table_input.suffix.lower() in {".jsonl", ".ndjson"}:
        input_texts = _read_jsonl(table_input)
    elif table_input == stock_path:
        input_texts = stock_texts
    else:
        _, _, input_texts = _parse_stock(table_input)
    if input_texts != stock_texts:
        raise OfficerComponentError(
            f"{language} table input does not match the pinned stock resource"
        )
    return StockTable(
        language=language,
        stock_path=stock_path,
        stock_blob=stock_blob,
        raw=raw,
        texts=stock_texts,
    )


def load_full_catalog(
    catalog_path: Path,
    report_path: Path,
    expected_officer_count: int,
) -> tuple[list[dict[str, Any]], dict[int, str], dict[str, Any]]:
    catalog = _strict_json(catalog_path)
    common.require_exact_keys(catalog, FULL_ROOT_KEYS, "full-name catalog")
    if catalog["schema"] != PRIVATE_SCHEMA:
        raise OfficerComponentError("unsupported full-name catalog schema")
    if catalog["base_languages"] != ["SC", "EN", "JP"]:
        raise OfficerComponentError(
            "full-name catalog base_languages must be exactly SC, EN, JP"
        )
    source_files = catalog["source_files"]
    common.require_exact_keys(source_files, set(LANGUAGES), "full-name source_files")
    for language in LANGUAGES:
        descriptor = source_files[language]
        common.require_exact_keys(
            descriptor, SOURCE_DESCRIPTOR_KEYS, f"full-name source_files.{language}"
        )
        expected_path = f"MSG_PK/{language}/msgev.bin"
        if descriptor["path"] != expected_path:
            raise OfficerComponentError(
                f"full-name source_files.{language}.path must be {expected_path!r}"
            )
        common.require_hash(
            descriptor["sha256"], f"full-name source_files.{language}.sha256"
        )

    raw_entries = catalog["entries"]
    if not isinstance(raw_entries, list):
        raise OfficerComponentError("full-name entries must be an array")
    entries: list[dict[str, Any]] = []
    ids: list[int] = []
    for index, entry in enumerate(raw_entries):
        label = f"full-name entries[{index}]"
        if not isinstance(entry, dict):
            raise OfficerComponentError(f"{label} must be an object")
        actual_keys = set(entry)
        if (
            not FULL_ENTRY_REQUIRED_KEYS <= actual_keys
            or not actual_keys <= FULL_ENTRY_ALLOWED_KEYS
        ):
            raise OfficerComponentError(
                f"{label} has invalid keys: {sorted(actual_keys)!r}"
            )
        entry_id = common.require_int(entry["id"], f"{label}.id")
        source = entry["source"]
        common.require_exact_keys(source, set(LANGUAGES), f"{label}.source")
        normalized_source: dict[str, str] = {}
        for language in LANGUAGES:
            text = source[language]
            if not isinstance(text, str) or not text or "\x00" in text:
                raise OfficerComponentError(
                    f"{label}.source.{language} must be non-empty NUL-free text"
                )
            normalized_source[language] = text
        korean = entry["ko"]
        if (
            not isinstance(korean, str)
            or "\x00" in korean
            or not common.has_semantic_text(korean)
        ):
            raise OfficerComponentError(f"{label}.ko is invalid")
        status = entry.get("status", "translated")
        if status not in common.BUILDABLE_STATUSES:
            raise OfficerComponentError(f"{label}.status is not buildable")
        ids.append(entry_id)
        entries.append(
            {
                "id": entry_id,
                "source": normalized_source,
                "ko": korean,
                "status": status,
            }
        )
    if ids != list(range(expected_officer_count)):
        raise OfficerComponentError(
            f"full-name ids must be contiguous 0..{expected_officer_count - 1}"
        )

    report = _strict_json(report_path)
    if report.get("schema") != FULL_REPORT_SCHEMA:
        raise OfficerComponentError("unsupported full-name generation report schema")
    if int(report.get("officer_count", -1)) != expected_officer_count:
        raise OfficerComponentError("full-name generation report officer_count differs")
    if int(report.get("generated_count", -1)) != expected_officer_count:
        raise OfficerComponentError("full-name generation report is not complete")
    if int(report.get("unresolved_count", -1)) != 0:
        raise OfficerComponentError("full-name generation report has unresolved rows")
    report_rows = report.get("rows")
    if not isinstance(report_rows, list) or len(report_rows) != expected_officer_count:
        raise OfficerComponentError("full-name generation report rows differ")
    methods: dict[int, str] = {}
    for expected_id, (entry, row) in enumerate(zip(entries, report_rows)):
        if not isinstance(row, dict) or row.get("id") != expected_id:
            raise OfficerComponentError(
                f"unaligned full-name generation report row {expected_id}"
            )
        if (
            row.get("jp") != entry["source"]["JP"]
            or row.get("en") != entry["source"]["EN"]
            or row.get("ko") != entry["ko"]
        ):
            raise OfficerComponentError(
                f"full-name catalog/report mismatch at id {expected_id}"
            )
        method = row.get("method")
        if not isinstance(method, str) or not method:
            raise OfficerComponentError(
                f"missing full-name generation method at id {expected_id}"
            )
        methods[expected_id] = method
    return entries, methods, report


def build_triple_index(tables: dict[str, StockTable]) -> dict[Triple, tuple[int, ...]]:
    counts = {len(table.texts) for table in tables.values()}
    if len(counts) != 1:
        raise OfficerComponentError("SC/EN/JP msgdata tables are not id-aligned")
    index: dict[Triple, list[int]] = defaultdict(list)
    row_count = next(iter(counts))
    for entry_id in range(row_count):
        key = tuple(tables[language].texts[entry_id] for language in LANGUAGES)
        if all(key):
            index[key].append(entry_id)  # type: ignore[arg-type]
    return {key: tuple(ids) for key, ids in index.items()}


def find_exact_candidates(
    source: dict[str, str],
    index: dict[Triple, tuple[int, ...]],
) -> list[ComponentCandidate]:
    sc = source["SC"]
    jp = source["JP"]
    en = source["EN"]
    english_words = en.split(" ")
    if len(english_words) != 2 or " ".join(english_words) != en:
        return []
    left, right = english_words

    candidates: dict[
        tuple[Triple, Triple], dict[str, Any]
    ] = {}
    for sc_boundary in range(1, len(sc)):
        for jp_boundary in range(1, len(jp)):
            for order, surname_en, given_en in (
                ("given_surname", right, left),
                ("surname_given", left, right),
            ):
                surname_key: Triple = (
                    sc[:sc_boundary],
                    surname_en,
                    jp[:jp_boundary],
                )
                given_key: Triple = (
                    sc[sc_boundary:],
                    given_en,
                    jp[jp_boundary:],
                )
                # Triple storage follows LANGUAGES (SC, EN, JP).
                surname_ids = index.get(surname_key)
                given_ids = index.get(given_key)
                if surname_ids is None or given_ids is None:
                    continue
                pair = (surname_key, given_key)
                found = candidates.setdefault(
                    pair,
                    {
                        "surname_ids": surname_ids,
                        "given_ids": given_ids,
                        "orders": set(),
                    },
                )
                found["orders"].add(order)

    result: list[ComponentCandidate] = []
    for (surname_key, given_key), value in sorted(candidates.items()):
        result.append(
            ComponentCandidate(
                surname_key=surname_key,
                given_key=given_key,
                surname_ids=tuple(value["surname_ids"]),
                given_ids=tuple(value["given_ids"]),
                english_orders=tuple(sorted(value["orders"])),
            )
        )
    return result


def _candidate_report(candidate: ComponentCandidate) -> dict[str, Any]:
    return {
        "surname_ids": list(candidate.surname_ids),
        "given_ids": list(candidate.given_ids),
        "english_orders": list(candidate.english_orders),
        "surname_source": {
            language: candidate.surname_key[index]
            for index, language in enumerate(LANGUAGES)
        },
        "given_source": {
            language: candidate.given_key[index]
            for index, language in enumerate(LANGUAGES)
        },
    }


def analyze_components(
    full_entries: Sequence[dict[str, Any]],
    methods: dict[int, str],
    tables: dict[str, StockTable],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    index = build_triple_index(tables)
    provisional: list[OfficerMatch] = []
    unresolved: list[dict[str, Any]] = []

    for entry in full_entries:
        officer_id = int(entry["id"])
        korean = str(entry["ko"])
        parts = korean.split(" ")
        if len(parts) != 2 or not all(parts) or any(
            any(character.isspace() for character in part) for part in parts
        ):
            unresolved.append(
                {
                    "id": officer_id,
                    "reason": "korean_name_is_not_two_components",
                    "ko": korean,
                    "source": entry["source"],
                    "method": methods[officer_id],
                    "candidates": [],
                }
            )
            continue
        surname_ko, given_ko = parts
        candidates = find_exact_candidates(entry["source"], index)
        if len(candidates) != 1:
            unresolved.append(
                {
                    "id": officer_id,
                    "reason": (
                        "no_exact_component_pair"
                        if not candidates
                        else "ambiguous_exact_component_pairs"
                    ),
                    "ko": korean,
                    "source": entry["source"],
                    "method": methods[officer_id],
                    "candidates": [
                        _candidate_report(candidate) for candidate in candidates
                    ],
                }
            )
            continue
        candidate = candidates[0]
        if set(candidate.surname_ids) & set(candidate.given_ids):
            unresolved.append(
                {
                    "id": officer_id,
                    "reason": "surname_given_id_overlap",
                    "ko": korean,
                    "source": entry["source"],
                    "method": methods[officer_id],
                    "candidates": [_candidate_report(candidate)],
                }
            )
            continue
        provisional.append(
            OfficerMatch(
                officer_id=officer_id,
                surname_ko=surname_ko,
                given_ko=given_ko,
                candidate=candidate,
                source=entry["source"],
                method=methods[officer_id],
            )
        )

    assignments: dict[int, list[tuple[int, str, str]]] = defaultdict(list)
    for match in provisional:
        for component_id in match.candidate.surname_ids:
            assignments[component_id].append(
                (match.officer_id, "surname", match.surname_ko)
            )
        for component_id in match.candidate.given_ids:
            assignments[component_id].append(
                (match.officer_id, "given", match.given_ko)
            )
    conflicted_ids = {
        component_id
        for component_id, values in assignments.items()
        if len({(role, korean) for _, role, korean in values}) != 1
    }
    conflict_officer_ids = {
        officer_id
        for component_id in conflicted_ids
        for officer_id, _, _ in assignments[component_id]
    }
    accepted = [
        match for match in provisional if match.officer_id not in conflict_officer_ids
    ]
    for match in provisional:
        if match.officer_id not in conflict_officer_ids:
            continue
        related_conflicts = sorted(
            (set(match.candidate.surname_ids) | set(match.candidate.given_ids))
            & conflicted_ids
        )
        unresolved.append(
            {
                "id": match.officer_id,
                "reason": "component_translation_conflict",
                "ko": f"{match.surname_ko} {match.given_ko}",
                "source": match.source,
                "method": match.method,
                "conflicted_component_ids": related_conflicts,
                "candidates": [_candidate_report(match.candidate)],
            }
        )

    final_assignments: dict[int, set[tuple[str, str]]] = defaultdict(set)
    matched_rows: list[dict[str, Any]] = []
    for match in accepted:
        for component_id in match.candidate.surname_ids:
            final_assignments[component_id].add(("surname", match.surname_ko))
        for component_id in match.candidate.given_ids:
            final_assignments[component_id].add(("given", match.given_ko))
        matched_rows.append(
            {
                "id": match.officer_id,
                "ko": f"{match.surname_ko} {match.given_ko}",
                "method": match.method,
                "surname_ids": list(match.candidate.surname_ids),
                "given_ids": list(match.candidate.given_ids),
                "english_orders": list(match.candidate.english_orders),
            }
        )

    private_entries: list[dict[str, Any]] = []
    role_counts: Counter[str] = Counter()
    for component_id in sorted(final_assignments):
        values = final_assignments[component_id]
        if len(values) != 1:
            raise OfficerComponentError(
                f"internal unresolved assignment conflict at msgdata id {component_id}"
            )
        role, korean = next(iter(values))
        if role == "surname":
            replacement = korean + " "
            if not replacement.endswith(" ") or replacement.endswith("  "):
                raise OfficerComponentError(
                    f"surname spacing invariant failed at msgdata id {component_id}"
                )
        else:
            replacement = korean
            if any(character.isspace() for character in replacement):
                raise OfficerComponentError(
                    f"given name contains whitespace at msgdata id {component_id}"
                )
        source = {
            language: tables[language].texts[component_id]
            for language in LANGUAGES
        }
        private_entry: dict[str, Any] = {
            "id": component_id,
            "source": source,
            "ko": replacement,
            "status": "translated",
        }
        if role == "surname":
            private_entry["allow_edge_whitespace_change"] = True
        private_entries.append(private_entry)
        role_counts[role] += 1

    unresolved.sort(key=lambda row: int(row["id"]))
    matched_rows.sort(key=lambda row: int(row["id"]))
    reason_counts = Counter(str(row["reason"]) for row in unresolved)
    conflicts = [
        {
            "msgdata_id": component_id,
            "assignments": [
                {"officer_id": officer_id, "role": role, "ko": korean}
                for officer_id, role, korean in sorted(assignments[component_id])
            ],
        }
        for component_id in sorted(conflicted_ids)
    ]
    analysis_report = {
        "full_officer_count": len(full_entries),
        "provisional_exact_match_count": len(provisional),
        "matched_officer_count": len(accepted),
        "unresolved_officer_count": len(unresolved),
        "unresolved_reason_counts": dict(sorted(reason_counts.items())),
        "component_entry_count": len(private_entries),
        "surname_component_count": role_counts["surname"],
        "given_component_count": role_counts["given"],
        "conflicted_component_count": len(conflicted_ids),
        "matched_rows": matched_rows,
        "unresolved_rows": unresolved,
        "component_conflicts": conflicts,
    }
    return private_entries, analysis_report


def make_private_catalog(
    entries: Sequence[dict[str, Any]],
    tables: dict[str, StockTable],
    version: str,
) -> dict[str, Any]:
    return {
        "schema": PRIVATE_SCHEMA,
        "scope": "msgdata_officer_names_0000_2399",
        "version": version,
        "base_languages": ["SC", "EN", "JP"],
        "source_files": {
            language: {
                "path": f"MSG_PK/{language}/{RESOURCE_NAME}",
                "sha256": common.sha256_bytes(tables[language].stock_blob),
            }
            for language in LANGUAGES
        },
        "entries": list(entries),
    }


def validate_regression_expectations(
    full_entries: Sequence[dict[str, Any]],
    analysis: dict[str, Any],
    private_entries: Sequence[dict[str, Any]],
    tables: dict[str, StockTable],
    expectations: dict[int, dict[str, Any]] = REGRESSION_EXPECTATIONS,
) -> list[dict[str, Any]]:
    """Require exact component ids and source recomposition for pinned officers."""
    matched_by_id = {int(row["id"]): row for row in analysis["matched_rows"]}
    private_by_id = {int(entry["id"]): entry for entry in private_entries}
    checks: list[dict[str, Any]] = []
    for officer_id in sorted(expectations):
        # Synthetic/unit-test catalogs may be shorter than the production
        # catalog. Production has all 2,207 rows and therefore runs every gate.
        if officer_id >= len(full_entries):
            continue
        expected = expectations[officer_id]
        row = matched_by_id.get(officer_id)
        if row is None:
            raise OfficerComponentError(
                f"regression officer id {officer_id} was not conservatively matched"
            )
        for field in ("ko", "surname_ids", "given_ids"):
            if row[field] != expected[field]:
                raise OfficerComponentError(
                    f"regression officer id {officer_id} {field} differs: "
                    f"{row[field]!r} != {expected[field]!r}"
                )

        surname_id = int(row["surname_ids"][0])
        given_id = int(row["given_ids"][0])
        full_source = full_entries[officer_id]["source"]
        recomposed = {
            "SC": tables["SC"].texts[surname_id] + tables["SC"].texts[given_id],
            "JP": tables["JP"].texts[surname_id] + tables["JP"].texts[given_id],
        }
        if recomposed["SC"] != full_source["SC"] or recomposed["JP"] != full_source["JP"]:
            raise OfficerComponentError(
                f"regression officer id {officer_id} SC/JP recomposition differs"
            )
        normal_en = (
            tables["EN"].texts[given_id]
            + " "
            + tables["EN"].texts[surname_id]
        )
        forward_en = (
            tables["EN"].texts[surname_id]
            + " "
            + tables["EN"].texts[given_id]
        )
        if full_source["EN"] not in (normal_en, forward_en):
            raise OfficerComponentError(
                f"regression officer id {officer_id} EN recomposition differs"
            )

        surname_ko, given_ko = str(expected["ko"]).split(" ", 1)
        for component_id in expected["surname_ids"]:
            entry = private_by_id.get(int(component_id))
            if (
                entry is None
                or entry["ko"] != surname_ko + " "
                or entry.get("allow_edge_whitespace_change") is not True
            ):
                raise OfficerComponentError(
                    f"regression surname component differs at msgdata id {component_id}"
                )
        for component_id in expected["given_ids"]:
            entry = private_by_id.get(int(component_id))
            if (
                entry is None
                or entry["ko"] != given_ko
                or "allow_edge_whitespace_change" in entry
            ):
                raise OfficerComponentError(
                    f"regression given component differs at msgdata id {component_id}"
                )
        checks.append(
            {
                "id": officer_id,
                "ko": expected["ko"],
                "surname_ids": list(expected["surname_ids"]),
                "given_ids": list(expected["given_ids"]),
                "sc_jp_en_recomposition": "OK",
                "surname_spacing": "OK",
                "given_spacing": "OK",
            }
        )
    return checks


def verify_build_and_replay(
    private_catalog_path: Path,
    public_stage_path: Path,
    verification_root: Path,
    tables: dict[str, StockTable],
    overlay_id: str,
) -> dict[str, Any]:
    stock_paths = {
        language: tables[language].stock_path for language in LANGUAGES
    }
    exported = common_export.export_overlay(
        private_catalog_path,
        stock_paths,
        public_stage_path,
        overlay_id,
    )
    overlay = _strict_json(public_stage_path)
    common.validate_overlay_shape(overlay)
    if overlay["distribution_policy"] != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }:
        raise OfficerComponentError("public overlay distribution flags are unsafe")

    isolated_game = verification_root / "isolated_game"
    isolated_stock = isolated_game / Path(RESOURCE_SC)
    for original in tables.values():
        if isolated_stock.resolve() == original.stock_path.resolve():
            raise OfficerComponentError("isolated stock path aliases a source stock file")
    common.atomic_write(isolated_stock, tables["SC"].stock_blob)
    isolated_hash_before = common.sha256_file(isolated_stock)

    first = common.build_overlay(
        isolated_game, public_stage_path, verification_root / "build_a"
    )
    second = common.build_overlay(
        isolated_game, public_stage_path, verification_root / "build_b"
    )
    for key in ("target_path", "manifest_path", "recipe_path"):
        if Path(first[key]).read_bytes() != Path(second[key]).read_bytes():
            raise OfficerComponentError(f"non-deterministic common-message build: {key}")

    recipe = recipe_core.load_recipe(Path(first["recipe_path"]))
    replayed, replayed_raw = recipe_core.apply_operations(
        tables["SC"].stock_blob,
        recipe["operations"],
        int(recipe["source"]["string_count"]),
    )
    target_blob = Path(first["target_path"]).read_bytes()
    if replayed != target_blob:
        raise OfficerComponentError("public recipe replay differs from the built target")
    if (
        common.sha256_bytes(replayed) != recipe["target"]["sha256"]
        or common.sha256_bytes(replayed_raw) != recipe["target"]["raw_sha256"]
    ):
        raise OfficerComponentError("public recipe target hashes differ")
    if common.sha256_file(isolated_stock) != isolated_hash_before:
        raise OfficerComponentError("isolated stock changed during verification")
    for table in tables.values():
        if common.sha256_file(table.stock_path) != common.sha256_bytes(table.stock_blob):
            raise OfficerComponentError(
                f"{table.language} source stock changed during verification"
            )

    return {
        "public_overlay_entry_count": int(exported["entry_count"]),
        "public_overlay_sha256": str(exported["output_sha256"]),
        "target_sha256": str(first["target_sha256"]),
        "manifest_sha256": str(first["manifest_sha256"]),
        "recipe_sha256": str(first["recipe_sha256"]),
        "recipe_replay_exact": True,
        "build_a_b_byte_identical": True,
        "isolated_stock_unchanged": True,
        "source_stock_unchanged": True,
    }


def export_public_build_artifacts(
    verification_root: Path,
    output_root: Path,
    tables: dict[str, StockTable],
) -> dict[str, Any]:
    """Atomically publish source-free manifest/recipe and replay the published recipe."""
    source_root = verification_root / "build_a"
    source_manifest = source_root / "msgdata.build-manifest.json"
    source_recipe = source_root / "msgdata_sc.recipe.json"
    source_target = source_root / Path(RESOURCE_SC)
    manifest_blob = source_manifest.read_bytes()
    recipe_blob = source_recipe.read_bytes()
    target_blob = source_target.read_bytes()
    manifest = json.loads(manifest_blob.decode("utf-8"))
    recipe = json.loads(recipe_blob.decode("utf-8"))

    if manifest.get("schema") != common.BUILD_SCHEMA:
        raise OfficerComponentError("unexpected public msgdata manifest schema")
    if manifest.get("commercial_source_text_included") is not False:
        raise OfficerComponentError("msgdata manifest is not source-text-free")
    if manifest.get("installed_game_files_modified") is not False:
        raise OfficerComponentError("msgdata manifest reports an installed-file write")
    payload_policy = recipe.get("payload_policy")
    if (
        recipe.get("schema") != recipe_core.SCHEMA
        or not isinstance(payload_policy, dict)
        or payload_policy.get("contains_complete_source") is not False
        or payload_policy.get("source_text_is_stored_as_hash_only") is not True
        or payload_policy.get("development_catalog_included") is not False
    ):
        raise OfficerComponentError("msgdata recipe payload policy is unsafe")
    if contains_commercial_text_fields(manifest) or contains_commercial_text_fields(recipe):
        raise OfficerComponentError("msgdata public build artifact has a commercial-text field")
    manifest_cjk_count = count_cjk_unified(manifest_blob.decode("utf-8"))
    recipe_cjk_count = count_cjk_unified(recipe_blob.decode("utf-8"))
    if manifest_cjk_count or recipe_cjk_count:
        raise OfficerComponentError(
            "msgdata public build artifacts contain CJK unified ideographs"
        )
    if common.sha256_bytes(target_blob) != manifest["target"]["sha256"]:
        raise OfficerComponentError("tmp msgdata target differs from its manifest")

    output_root = output_root.resolve()
    manifest_path = output_root / "msgdata.build-manifest.json"
    recipe_path = output_root / "msgdata_sc.recipe.json"
    if manifest_path in (source_manifest.resolve(), source_recipe.resolve(), source_target.resolve()):
        raise OfficerComponentError("public msgdata manifest aliases a verification input")
    if recipe_path in (source_manifest.resolve(), source_recipe.resolve(), source_target.resolve()):
        raise OfficerComponentError("public msgdata recipe aliases a verification input")
    common.atomic_write(manifest_path, manifest_blob)
    common.atomic_write(recipe_path, recipe_blob)

    published_manifest_blob = manifest_path.read_bytes()
    published_recipe_blob = recipe_path.read_bytes()
    if published_manifest_blob != manifest_blob or published_recipe_blob != recipe_blob:
        raise OfficerComponentError("published msgdata artifacts differ after atomic write")
    published_recipe = recipe_core.load_recipe(recipe_path)
    replayed, replayed_raw = recipe_core.apply_operations(
        tables["SC"].stock_blob,
        published_recipe["operations"],
        int(published_recipe["source"]["string_count"]),
    )
    if replayed != target_blob:
        raise OfficerComponentError(
            "published msgdata recipe does not reproduce the tmp build target"
        )
    if common.sha256_bytes(replayed_raw) != published_recipe["target"]["raw_sha256"]:
        raise OfficerComponentError("published msgdata recipe raw target hash differs")
    manifest_hash = common.sha256_bytes(published_manifest_blob)
    recipe_hash = common.sha256_bytes(published_recipe_blob)
    if published_recipe["export_verification"]["build_manifest_sha256"] != manifest_hash:
        raise OfficerComponentError("published recipe does not pin the published manifest")
    return {
        "manifest_sha256": manifest_hash,
        "recipe_sha256": recipe_hash,
        "target_sha256": common.sha256_bytes(target_blob),
        "recipe_replays_tmp_target_exact": True,
        "manifest_cjk_unified_ideograph_count": manifest_cjk_count,
        "recipe_cjk_unified_ideograph_count": recipe_cjk_count,
        "commercial_source_text_included": False,
        "complete_game_resource_published": False,
        "atomic_write_verified": True,
    }
def generate_components(args: argparse.Namespace) -> dict[str, Any]:
    if type(args.expected_officer_count) is not int or args.expected_officer_count <= 0:
        raise OfficerComponentError("expected_officer_count must be positive")
    if not isinstance(args.version, str) or not args.version.strip():
        raise OfficerComponentError("version must be non-empty")

    output_paths = {
        args.private_output.resolve(),
        args.public_output.resolve(),
        args.report_output.resolve(),
    }
    input_paths = {args.full_catalog.resolve(), args.full_report.resolve()}
    if output_paths & input_paths:
        raise OfficerComponentError("refusing to overwrite an input catalog/report")
    if len(output_paths) != 3:
        raise OfficerComponentError("private, public, and report outputs must differ")

    tables = {
        "SC": load_stock_table("SC", args.msgdata_sc, args.stock_sc),
        "EN": load_stock_table("EN", args.msgdata_en, args.stock_en),
        "JP": load_stock_table("JP", args.msgdata_jp, args.stock_jp),
    }
    full_entries, methods, full_report = load_full_catalog(
        args.full_catalog,
        args.full_report,
        args.expected_officer_count,
    )
    private_entries, analysis = analyze_components(full_entries, methods, tables)
    if not private_entries:
        raise OfficerComponentError("no conservative msgdata component mappings were found")
    regression_checks = validate_regression_expectations(
        full_entries, analysis, private_entries, tables
    )
    private_catalog = make_private_catalog(private_entries, tables, args.version)
    private_blob = encode_json(private_catalog)

    verification_root = args.verification_root.resolve()
    stage_root = verification_root / "stage"
    private_stage = stage_root / "msgdata_officer_names.private.json"
    public_stage = stage_root / "msgdata_officer_names.public.json"
    common.atomic_write(private_stage, private_blob)
    verification = verify_build_and_replay(
        private_stage,
        public_stage,
        verification_root,
        tables,
        args.overlay_id,
    )
    public_build_output_root = getattr(args, "public_build_output_root", None)
    public_build_artifacts = None
    if public_build_output_root is not None:
        public_build_artifacts = export_public_build_artifacts(
            verification_root,
            public_build_output_root,
            tables,
        )

    public_blob = public_stage.read_bytes()
    public_overlay = json.loads(public_blob.decode("utf-8"))
    if int(public_overlay["entry_count"]) != len(private_entries):
        raise OfficerComponentError("public/private component entry counts differ")
    public_cjk_count = count_cjk_unified(public_blob.decode("utf-8"))
    if public_cjk_count != 0:
        raise OfficerComponentError(
            f"public overlay contains {public_cjk_count} CJK unified ideographs"
        )
    if contains_source_original_fields(public_overlay):
        raise OfficerComponentError("public overlay contains an original-source field")

    report = {
        "schema": COMPONENT_REPORT_SCHEMA,
        "version": args.version,
        "overlay_id": args.overlay_id,
        "source_full_catalog_sha256": common.sha256_file(args.full_catalog),
        "source_full_report_sha256": common.sha256_file(args.full_report),
        "source_full_method_counts": full_report.get("method_counts", {}),
        "full_msgev_translated_officer_count": len(full_entries),
        "full_msgev_unresolved_officer_count": 0,
        "msgdata_split_matched_officer_count": analysis["matched_officer_count"],
        "msgdata_split_excluded_officer_count": analysis["unresolved_officer_count"],
        "msgdata_split_exclusions_leave_full_msgev_translation_intact": True,
        "msgdata_stock": {
            language: {
                "size": len(tables[language].stock_blob),
                "packed_sha256": common.sha256_bytes(tables[language].stock_blob),
                "raw_size": len(tables[language].raw),
                "raw_sha256": common.sha256_bytes(tables[language].raw),
                "string_count": len(tables[language].texts),
            }
            for language in LANGUAGES
        },
        **analysis,
        "regression_check_count": len(regression_checks),
        "regression_checks": regression_checks,
        "private_catalog_sha256": common.sha256_bytes(private_blob),
        "public_overlay": {
            "entry_count": int(public_overlay["entry_count"]),
            "sha256": common.sha256_bytes(public_blob),
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "source_original_fields_present": False,
            "cjk_unified_ideograph_count": public_cjk_count,
        },
        "verification": verification,
    }
    if public_build_artifacts is not None:
        report["public_build_artifacts"] = public_build_artifacts
    report_blob = encode_json(report)

    # Publish only after the isolated deterministic build and replay succeed.
    common.atomic_write(args.private_output.resolve(), private_blob)
    common.atomic_write(args.public_output.resolve(), public_blob)
    common.atomic_write(args.report_output.resolve(), report_blob)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-catalog", type=Path, required=True)
    parser.add_argument("--full-report", type=Path, required=True)
    parser.add_argument("--msgdata-sc", type=Path, required=True)
    parser.add_argument("--msgdata-en", type=Path, required=True)
    parser.add_argument("--msgdata-jp", type=Path, required=True)
    parser.add_argument("--stock-sc", type=Path)
    parser.add_argument("--stock-en", type=Path)
    parser.add_argument("--stock-jp", type=Path)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--public-output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    parser.add_argument("--verification-root", type=Path, required=True)
    parser.add_argument("--public-build-output-root", type=Path)
    parser.add_argument("--overlay-id", default=DEFAULT_OVERLAY_ID)
    parser.add_argument("--version", default="0.1")
    parser.add_argument("--expected-officer-count", type=int, default=2207)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = generate_components(args)
    except (
        OSError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        LZ4Error,
        MessageTableError,
        common.CommonMessageOverlayError,
        OfficerComponentError,
    ) as exc:
        parser.exit(2, f"error: {exc}\n")
    summary = {
        key: report[key]
        for key in (
            "full_officer_count",
            "matched_officer_count",
            "unresolved_officer_count",
            "component_entry_count",
            "surname_component_count",
            "given_component_count",
        )
    }
    summary["public_overlay_sha256"] = report["public_overlay"]["sha256"]
    summary["target_sha256"] = report["verification"]["target_sha256"]
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
