"""Freeze the 25 exact-PC-anchor Korean repairs as private generic-builder rows.

Only direct PC inputs are read: pristine PC Japanese, current Steam PC Korean,
and Steam PC EN/SC/TC where present.  Switch Korean, historical Korean,
generic-overlay payloads, and the contaminated non-Steam SC path are excluded.

The output contains commercial source text and Korean payload, so it is
private below ``tmp``.  The committed README and validation JSON remain
source-free.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any, Mapping


WORKSTREAM = Path(__file__).resolve().parent
WORK = WORKSTREAM.parents[1]
PRIVATE_OUTPUT = WORK / "tmp" / "pc_translation_residuals_pc_only_v1" / "pc_exact_anchor_candidates.v1.jsonl"


def load_audit_module() -> Any:
    path = WORKSTREAM / "build_private_findings_v1.py"
    spec = importlib.util.spec_from_file_location("pc_translation_residuals_private_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load private audit module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUDIT = load_audit_module()


EXPECTED_COORDINATES = {
    ("strdata", (0, 18387)),
    ("strdata", (0, 18388)),
    ("strdata", (0, 20708)),
    ("strdata", (0, 20709)),
    ("strdata", (0, 20710)),
    ("strdata", (0, 20711)),
    ("strdata", (0, 23194)),
    ("msgdata", 18707),
    ("msgdata", 23996),
    ("msgdata", 24553),
    ("msgdata", 25301),
    ("msgdata", 25308),
    ("msgdata", 25309),
    ("msgdata", 25310),
    ("msgdata", 25311),
    ("msgdata", 25312),
    ("msgdata", 25313),
    ("msgdata", 25315),
    ("msgdata", 25318),
    ("msgdata", 25319),
    ("msgdata", 25554),
    ("msgdata", 25563),
    ("msgdata", 25564),
    ("msgdata", 25568),
    ("msgdata", 25573),
}


# These codes record the human semantic comparison of the private PC-language
# evidence stored per candidate.  They contain no game source or Korean text.
SEMANTIC_REVIEW_CODES = {
    "strdata:0:18387": "jp_exact_anchor_pc_term_confirmation",
    "strdata:0:18388": "jp_exact_anchor_pc_term_confirmation",
    "strdata:0:20708": "jp_exact_anchor_pc_term_confirmation",
    "strdata:0:20709": "jp_exact_anchor_pc_term_confirmation",
    "strdata:0:20710": "jp_exact_anchor_pc_term_confirmation",
    "strdata:0:20711": "jp_exact_anchor_pc_term_confirmation",
    "strdata:0:23194": "jp_exact_anchor_target_sc_tc_contextual_superset",
    "msgdata:18707": "jp_en_sc_tc_exact",
    "msgdata:23996": "jp_exact_anchor_en_direct_target_sc_tc_contextual_superset",
    "msgdata:24553": "jp_sc_tc_exact_en_synonymous",
    "msgdata:25301": "jp_en_tc_exact_target_sc_contextual_suffix",
    "msgdata:25308": "jp_en_sc_tc_exact",
    "msgdata:25309": "jp_en_tc_exact_sc_word_order_variant",
    "msgdata:25310": "jp_sc_tc_exact_target_en_direct_anchor_en_placeholder",
    "msgdata:25311": "jp_sc_tc_exact_target_en_direct_anchor_en_placeholder",
    "msgdata:25312": "jp_en_sc_tc_exact",
    "msgdata:25313": "jp_sc_tc_exact_target_en_direct_anchor_en_placeholder",
    "msgdata:25315": "jp_en_sc_tc_exact",
    "msgdata:25318": "jp_sc_tc_exact_target_en_direct_anchor_en_placeholder",
    "msgdata:25319": "jp_en_sc_tc_exact",
    "msgdata:25554": "jp_exact_anchor_pc_anchor_languages_direct_target_locale_placeholders",
    "msgdata:25563": "jp_en_sc_tc_exact",
    "msgdata:25564": "jp_tc_exact_en_sc_grammatical_variant",
    "msgdata:25568": "jp_en_sc_tc_exact",
    "msgdata:25573": "jp_en_sc_tc_exact",
}


RUNTIME_TOKEN = re.compile(r"<[^<>\r\n]+>")
PRINTF_TOKEN = re.compile(r"%(?:\+?\d+)?[A-Za-z%]")
ESCAPE_TAG = re.compile(r"\x1b.{2}")


def sha256_utf16le(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16le")).hexdigest().upper()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def coordinate_key(resource: str, coordinate: Any) -> str:
    if resource == "strdata":
        block, entry_id = coordinate
        return f"{block}:{entry_id}"
    return str(coordinate)


def source_free_coordinate(resource: str, coordinate: Any) -> str:
    return f"{resource}:{coordinate_key(resource, coordinate)}"


def format_profile(text: str) -> dict[str, Any]:
    escape_offsets = {
        index
        for match in ESCAPE_TAG.finditer(text)
        for index in range(match.start(), match.end())
    }
    controls = [
        f"U+{ord(char):04X}"
        for index, char in enumerate(text)
        if ord(char) < 0x20 and char not in {"\r", "\n"} and index not in escape_offsets
    ]
    return {
        "runtime_tokens": RUNTIME_TOKEN.findall(text),
        "printf_tokens": PRINTF_TOKEN.findall(text),
        "escape_tags": ESCAPE_TAG.findall(text),
        "line_breaks": re.findall(r"\r\n|\n|\r", text),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "control_codepoints": controls,
        "fullwidth_percent_count": text.count("\uff05"),
    }


def as_coordinate(resource: str, value: Any) -> Any:
    if resource == "strdata":
        if not isinstance(value, list) or len(value) != 2 or any(isinstance(part, bool) or not isinstance(part, int) for part in value):
            raise ValueError(f"invalid strdata coordinate: {value!r}")
        return (value[0], value[1])
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"invalid msgdata coordinate: {value!r}")
    return value


def tables_and_meta() -> tuple[dict[str, dict[str, dict[Any, str]]], dict[str, dict[str, dict[str, str]]]]:
    tables: dict[str, dict[str, dict[Any, str]]] = {}
    metadata: dict[str, dict[str, dict[str, str]]] = {}
    for resource, language_paths in AUDIT.PATHS.items():
        tables[resource] = {}
        metadata[resource] = {}
        for language, path in language_paths.items():
            table, meta = AUDIT.load_strdata(path) if resource == "strdata" else AUDIT.load_msgdata(path)
            expected = AUDIT.PINNED_WRAPPED_SHA256[resource][language]
            if meta["wrapped_sha256"] != expected:
                raise ValueError(f"unexpected pinned PC source: {resource}/{language}")
            tables[resource][language] = table
            metadata[resource][language] = meta
    return tables, metadata


def private_languages(table: Mapping[str, Mapping[Any, str]], coordinate: Any) -> dict[str, str | None]:
    return {language: texts.get(coordinate) for language, texts in table.items()}


def candidate_record(
    finding: Mapping[str, Any],
    tables: Mapping[str, Mapping[str, Mapping[Any, str]]],
    metadata: Mapping[str, Mapping[str, Mapping[str, str]]],
) -> dict[str, Any]:
    resource = finding["resource"]
    coordinate = as_coordinate(resource, finding["coordinate"])
    anchor_values = finding["same_resource_exact_jp_anchor_coordinates"]
    if not isinstance(anchor_values, list) or not anchor_values:
        raise ValueError(f"missing exact PC anchor at {source_free_coordinate(resource, coordinate)}")
    anchor = as_coordinate(resource, anchor_values[0])
    table = tables[resource]
    current = table["current_ko"][coordinate]
    proposal = table["current_ko"][anchor]
    target_jp = table["jp"][coordinate]
    anchor_jp = table["jp"][anchor]
    if target_jp != anchor_jp:
        raise ValueError(f"JP source mismatch at {source_free_coordinate(resource, coordinate)}")
    if finding["current_ko"] != current or finding["same_resource_exact_jp_anchor_ko"][0] != proposal:
        raise ValueError(f"private finding drift at {source_free_coordinate(resource, coordinate)}")
    before_profile = format_profile(current)
    after_profile = format_profile(proposal)
    if before_profile != after_profile:
        raise ValueError(f"format profile differs at {source_free_coordinate(resource, coordinate)}")
    if AUDIT.JP_SCRIPT.search(proposal) or not AUDIT.HANGUL.search(proposal):
        raise ValueError(f"unsafe anchor proposal at {source_free_coordinate(resource, coordinate)}")
    code = SEMANTIC_REVIEW_CODES.get(source_free_coordinate(resource, coordinate))
    if code is None:
        raise ValueError(f"semantic review code missing at {source_free_coordinate(resource, coordinate)}")

    generic: dict[str, Any] = {
        "resource": resource,
        "current_ko": current,
        "proposed_ko": proposal,
        "current_ko_utf16le_sha256": sha256_utf16le(current),
        "proposed_ko_utf16le_sha256": sha256_utf16le(proposal),
        "allowed_format_delta": [],
        "canonical_anchor_coordinate": coordinate_key(resource, anchor),
        "canonical_anchor_jp_utf16le_sha256": sha256_utf16le(anchor_jp),
        "canonical_anchor_ko_utf16le_sha256": sha256_utf16le(proposal),
        "canonical_anchor_ko": proposal,
        "pc_jp_exact_anchor": True,
        "semantic_review_code": code,
        "format_proof": {
            "current": before_profile,
            "proposed": after_profile,
            "preserved": True,
        },
        "pc_multilingual_evidence": {
            "target": private_languages(table, coordinate),
            "canonical_anchor": private_languages(table, anchor),
            "resource_wrapped_sha256": {
                language: meta["wrapped_sha256"]
                for language, meta in metadata[resource].items()
            },
        },
    }
    generic["source_hashes"] = {
        "current_ko_utf16le_sha256": generic["current_ko_utf16le_sha256"],
        "canonical_anchor_jp_utf16le_sha256": generic["canonical_anchor_jp_utf16le_sha256"],
        "canonical_anchor_ko_utf16le_sha256": generic["canonical_anchor_ko_utf16le_sha256"],
    }
    if resource == "strdata":
        generic["block"] = coordinate[0]
        generic["id"] = coordinate[1]
    else:
        generic["id"] = coordinate
    return generic


def build() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings = AUDIT.build()[1:]
    auto = [row for row in findings if row.get("status") == "AUTO_ELIGIBLE_EXACT_PC_ANCHOR"]
    tables, metadata = tables_and_meta()
    rows = [candidate_record(row, tables, metadata) for row in auto]
    rows.sort(key=lambda row: (row["resource"], row.get("block", -1), row["id"]))
    coordinates = {
        (row["resource"], (row["block"], row["id"]) if row["resource"] == "strdata" else row["id"])
        for row in rows
    }
    if coordinates != EXPECTED_COORDINATES or len(rows) != 25:
        raise ValueError(f"unexpected candidate coordinate set: {len(rows)}")
    if set(SEMANTIC_REVIEW_CODES) != {source_free_coordinate(resource, coordinate) for resource, coordinate in EXPECTED_COORDINATES}:
        raise ValueError("semantic review coordinate set differs")
    if len({(row["resource"], row.get("block"), row["id"]) for row in rows}) != len(rows):
        raise ValueError("duplicate generic-builder coordinate")
    summary = {
        "entry_count": len(rows),
        "coordinate_set_sha256": sha256_bytes(
            json.dumps(
                [source_free_coordinate(row["resource"], (row["block"], row["id"]) if row["resource"] == "strdata" else row["id"]) for row in rows],
                separators=(",", ":"),
            ).encode("utf-8")
        ),
        "resource_counts": {
            resource: sum(row["resource"] == resource for row in rows)
            for resource in ("strdata", "msgdata")
        },
        "format_delta_free": all(row["allowed_format_delta"] == [] for row in rows),
        "exact_pc_jp_anchor": all(row["pc_jp_exact_anchor"] for row in rows),
        "semantic_reviewed": all(row["semantic_review_code"] for row in rows),
    }
    return rows, summary


def write(rows: list[dict[str, Any]], summary: Mapping[str, Any]) -> None:
    PRIVATE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    PRIVATE_OUTPUT.write_text(payload, encoding="utf-8", newline="\n")
    print(f"output={PRIVATE_OUTPUT}")
    print(f"entry_count={summary['entry_count']}")
    print(f"coordinate_set_sha256={summary['coordinate_set_sha256']}")
    print(f"payload_sha256={sha256_bytes(payload.encode('utf-8'))}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows, summary = build()
    if args.write:
        write(rows, summary)
    else:
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
