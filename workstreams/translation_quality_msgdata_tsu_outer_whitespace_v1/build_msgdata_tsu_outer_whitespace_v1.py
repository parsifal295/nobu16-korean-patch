#!/usr/bin/env python3
"""Generate PC-only msgdata name corrections while preserving outer spaces.

This is an isolated review generator, not an applicator.  It accepts a row
only if all of the following are true:

* its Japanese source is the pinned pristine PC source;
* the current PC Korean target has at least one Korean ``tsu`` syllable;
* replacing every such syllable with ``ssu`` is the only text delta;
* the exact same pristine PC Japanese static label has a current PC strdata
  Korean anchor with the same *visible* spelling; and
* the candidate preserves every token, control, line-break, and outer-space
  invariant of its current target.

The committed PC-only correction overlay is read solely to virtualize active
coordinates and exclude duplicates.  Switch Korean resources are never opened
or used.  Output is private review JSONL below ``tmp``; no game file is
written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(REPO / "workstreams" / "strdata"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata  # noqa: E402


STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_ROOT = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
MSGDATA_RELATIVE = Path("MSG_PK/JP/msgdata.bin")
STRDATA_RELATIVE = Path("MSG/JP/strdata.bin")
GENERIC_OVERLAY = (
    REPO
    / "workstreams"
    / "translation_quality_corrections_v1"
    / "public"
    / "translation_quality_corrections.v1.json"
)
OUTPUT_ROOT = REPO / "tmp" / "translation_quality_msgdata_tsu_outer_whitespace_v1"
PRIVATE_CANDIDATES = OUTPUT_ROOT / "msgdata_tsu_outer_whitespace_candidates.v1.jsonl"
VALIDATION = WORKSTREAM / "validation.v1.json"

EXPECTED_HASHES = {
    "msgdata_jp": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E",
    "msgdata_ko": "7EAA33BC80C021A028660DF1A7934886591A1DA36DB7BC53146749C3A4AEF040",
    "strdata_jp": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
    "strdata_ko": "D518A91E36B9A59EAD0B5ED1FDD067941E4BF72E43AFCB19C296C8AD77C8C128",
}
EXPECTED_CANDIDATE_COUNT = 49
EXPECTED_SOURCE_GROUP_COUNT = 42

OVERLAY_SCHEMA = "nobu16.kr.msgdata-tsu-outer-whitespace-review.v1"
VALIDATION_SCHEMA = "nobu16.kr.msgdata-tsu-outer-whitespace-validation.v1"
TSU = chr(0xCE20)
SSU = chr(0xC4F0)
OUTER_WS = " \t\r\n"
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
KANA_OR_HAN_RE = re.compile(
    r"[\u3041-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
STATIC_JP_NAME_RE = re.compile(r"^[\u3041-\u30ff\u3400-\u9fff\u3005\uf900-\ufaff]+$")
STATIC_KO_NAME_RE = re.compile(r"^[\uac00-\ud7a3\u00b7]+$")
HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")


class ReviewError(ValueError):
    """Raised when a proposed row lacks the narrow PC-only proof contract."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_hash(value: object) -> str:
    return sha256_bytes(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def pretty_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write_bytes(path: Path, blob: bytes, root: Path) -> None:
    allowed = root.resolve()
    resolved = path.resolve(strict=False)
    if resolved != allowed and allowed not in resolved.parents:
        raise ReviewError(f"output escapes allowed root: {resolved}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_common(path: Path) -> dict[str, str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    table = parse_message_table(raw)
    return {str(index): text for index, text in enumerate(table.texts)}


def parse_strdata(path: Path) -> dict[str, str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    archive = parse_raw_strdata(raw)
    return {f"{block}:{slot}": text for (block, slot), text in coordinate_texts(archive).items()}


def language_path(relative: Path, language: str) -> Path:
    parts = list(relative.parts)
    try:
        index = parts.index("JP")
    except ValueError as exc:
        raise ReviewError(f"resource route lacks JP segment: {relative}") from exc
    parts[index] = language
    return Path(*parts)


def profile(value: str) -> dict[str, Any]:
    escape_offsets = {
        offset
        for match in ESC_RE.finditer(value)
        for offset in range(match.start(), match.end())
    }
    return {
        "escape_tags": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "linebreaks": LINEBREAK_RE.findall(value),
        "leading_outer_whitespace": value[: len(value) - len(value.lstrip(OUTER_WS))],
        "trailing_outer_whitespace": value[len(value.rstrip(OUTER_WS)) :],
        "non_escape_controls": [
            f"U+{ord(char):04X}"
            for index, char in enumerate(value)
            if unicodedata.category(char) == "Cc"
            and char not in ("\r", "\n")
            and index not in escape_offsets
        ],
    }


def visible_core(value: str) -> str:
    return value.strip(OUTER_WS)


def only_tsu_to_ssu(current: str, proposed: str) -> bool:
    if len(current) != len(proposed):
        return False
    changes = [(before, after) for before, after in zip(current, proposed) if before != after]
    return bool(changes) and all(before == TSU and after == SSU for before, after in changes)


def require_hash(value: object, expected: str, label: str) -> None:
    if not isinstance(value, str) or not HEX64_RE.fullmatch(value.upper()) or value.upper() != expected:
        raise ReviewError(f"hash differs for {label}")


def load_committed_overlay() -> tuple[dict[str, dict[str, str]], dict[str, set[str]], str]:
    if not GENERIC_OVERLAY.is_file():
        raise ReviewError(f"committed PC-only overlay is absent: {GENERIC_OVERLAY}")
    overlay = json.loads(GENERIC_OVERLAY.read_text(encoding="utf-8"))
    if not isinstance(overlay, dict) or overlay.get("overlay_id") != "translation_quality_corrections.v1":
        raise ReviewError("unexpected committed overlay identity")
    policy = overlay.get("distribution_policy")
    if not isinstance(policy, Mapping) or policy.get("switch_korean_translation_used") is not False:
        raise ReviewError("committed overlay does not declare Switch Korean exclusion")
    resources = overlay.get("resources")
    if not isinstance(resources, list):
        raise ReviewError("committed overlay resources are invalid")
    values: dict[str, dict[str, str]] = {}
    active_coordinates: dict[str, set[str]] = {}
    for name, relative in (("msgdata", MSGDATA_RELATIVE.as_posix()), ("strdata", STRDATA_RELATIVE.as_posix())):
        matches = [item for item in resources if isinstance(item, Mapping) and item.get("name") == name]
        if len(matches) != 1:
            raise ReviewError(f"committed overlay lacks unique {name} resource")
        resource = matches[0]
        baseline = resource.get("baseline")
        entries = resource.get("entries")
        if (
            not isinstance(baseline, Mapping)
            or baseline.get("relative_path") != relative
            or not isinstance(entries, list)
            or resource.get("entry_count") != len(entries)
        ):
            raise ReviewError(f"committed overlay {name} resource is malformed")
        mapped: dict[str, str] = {}
        for entry in entries:
            if not isinstance(entry, Mapping):
                raise ReviewError(f"committed overlay {name} entry is malformed")
            coordinate = entry.get("coordinate")
            korean = entry.get("ko")
            if not isinstance(coordinate, str) or not coordinate or not isinstance(korean, str) or not korean:
                raise ReviewError(f"committed overlay {name} entry lacks coordinate or Korean target")
            if coordinate in mapped:
                raise ReviewError(f"committed overlay {name} duplicates {coordinate}")
            mapped[coordinate] = korean
        values[name] = mapped
        active_coordinates[name] = set(mapped)
    return values, active_coordinates, sha256_file(GENERIC_OVERLAY)


def apply_overlay(
    name: str,
    base: Mapping[str, str],
    entries: Mapping[str, str],
    expected_source_hashes: Mapping[str, Mapping[str, Any]],
) -> dict[str, str]:
    result = dict(base)
    for coordinate, replacement in entries.items():
        if coordinate not in result:
            raise ReviewError(f"committed overlay {name}:{coordinate} is absent from current PC target")
        entry = expected_source_hashes[coordinate]
        require_hash(entry.get("source_current_utf16le_sha256"), text_hash(result[coordinate]), f"{name}:{coordinate}")
        result[coordinate] = replacement
    return result


def load_inputs() -> tuple[dict[str, dict[str, str]], dict[str, str], dict[str, Any]]:
    paths = {
        "msgdata_jp": PRISTINE_ROOT / MSGDATA_RELATIVE,
        "msgdata_ko": STEAM_ROOT / MSGDATA_RELATIVE,
        "msgdata_en": STEAM_ROOT / language_path(MSGDATA_RELATIVE, "EN"),
        "msgdata_sc": STEAM_ROOT / language_path(MSGDATA_RELATIVE, "SC"),
        "msgdata_tc": STEAM_ROOT / language_path(MSGDATA_RELATIVE, "TC"),
        "strdata_jp": PRISTINE_ROOT / STRDATA_RELATIVE,
        "strdata_ko": STEAM_ROOT / STRDATA_RELATIVE,
    }
    if any(not path.is_file() for path in paths.values()):
        missing = [name for name, path in paths.items() if not path.is_file()]
        raise ReviewError(f"required PC-only input is absent: {missing}")
    hashes = {name: sha256_file(path) for name, path in paths.items()}
    for name, expected in EXPECTED_HASHES.items():
        if hashes[name] != expected:
            raise ReviewError(f"pinned PC input hash differs for {name}")

    tables = {
        "msgdata_jp": parse_common(paths["msgdata_jp"]),
        "msgdata_ko": parse_common(paths["msgdata_ko"]),
        "msgdata_en": parse_common(paths["msgdata_en"]),
        "msgdata_sc": parse_common(paths["msgdata_sc"]),
        "msgdata_tc": parse_common(paths["msgdata_tc"]),
        "strdata_jp": parse_strdata(paths["strdata_jp"]),
        "strdata_ko": parse_strdata(paths["strdata_ko"]),
    }
    msgdata_coordinates = set(tables["msgdata_jp"])
    if any(set(tables[name]) != msgdata_coordinates for name in ("msgdata_ko", "msgdata_en", "msgdata_sc", "msgdata_tc")):
        raise ReviewError("PC msgdata language coordinate sets differ")
    if set(tables["strdata_jp"]) != set(tables["strdata_ko"]):
        raise ReviewError("PC strdata Japanese/Korean coordinate sets differ")

    overlay_values, active_coordinates, overlay_sha256 = load_committed_overlay()
    overlay_data = json.loads(GENERIC_OVERLAY.read_text(encoding="utf-8"))
    resource_entries = {
        item["name"]: {entry["coordinate"]: entry for entry in item["entries"]}
        for item in overlay_data["resources"]
        if isinstance(item, Mapping) and item.get("name") in {"msgdata", "strdata"}
    }
    tables["msgdata_virtual_ko"] = apply_overlay(
        "msgdata", tables["msgdata_ko"], overlay_values["msgdata"], resource_entries["msgdata"]
    )
    tables["strdata_virtual_ko"] = apply_overlay(
        "strdata", tables["strdata_ko"], overlay_values["strdata"], resource_entries["strdata"]
    )
    metadata = {
        "committed_overlay_sha256": overlay_sha256,
        "committed_active_coordinate_counts": {name: len(value) for name, value in active_coordinates.items()},
        "active_coordinates": active_coordinates,
    }
    return tables, hashes, metadata


def static_anchors(
    strdata_jp: Mapping[str, str], strdata_virtual_ko: Mapping[str, str], active_coordinates: set[str]
) -> dict[str, list[dict[str, Any]]]:
    anchors: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for coordinate, japanese in strdata_jp.items():
        korean = strdata_virtual_ko[coordinate]
        core = visible_core(korean)
        if (
            not STATIC_JP_NAME_RE.fullmatch(japanese)
            or not STATIC_KO_NAME_RE.fullmatch(core)
            or KANA_OR_HAN_RE.search(core)
            or not core
        ):
            continue
        anchors[japanese].append(
            {
                "coordinate": coordinate,
                "korean": korean,
                "visible_korean": core,
                "overlay_active": coordinate in active_coordinates,
            }
        )
    return anchors


def coordinate_key(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split(":"))


def canonical_jsonl(rows: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    ).encode("utf-8")


def assert_public_source_free(value: bytes) -> None:
    text = value.decode("utf-8")
    if KANA_OR_HAN_RE.search(text):
        raise ReviewError("public validation unexpectedly contains Japanese/CJK source text")


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    tables, hashes, metadata = load_inputs()
    active_msgdata = metadata["active_coordinates"]["msgdata"]
    anchors_by_source = static_anchors(
        tables["strdata_jp"], tables["strdata_virtual_ko"], metadata["active_coordinates"]["strdata"]
    )
    rows: list[dict[str, Any]] = []
    source_groups: set[str] = set()
    candidate_ids: set[int] = set()
    for coordinate in sorted(tables["msgdata_jp"], key=int):
        japanese = tables["msgdata_jp"][coordinate]
        current = tables["msgdata_ko"][coordinate]
        virtual_current = tables["msgdata_virtual_ko"][coordinate]
        if virtual_current != current:
            continue
        if TSU not in current:
            continue
        proposed = current.replace(TSU, SSU)
        if not only_tsu_to_ssu(current, proposed):
            raise ReviewError(f"candidate text delta is not tsu-to-ssu only: {coordinate}")
        if profile(current) != profile(proposed):
            raise ReviewError(f"candidate profile differs: {coordinate}")
        if coordinate in active_msgdata:
            raise ReviewError(f"candidate overlaps committed msgdata correction: {coordinate}")
        core_current = visible_core(current)
        core_proposed = visible_core(proposed)
        matching_anchors = [
            anchor
            for anchor in anchors_by_source.get(japanese, [])
            if anchor["visible_korean"] == core_proposed
        ]
        # This scan intentionally sees every live ``tsu`` spelling first.
        # Only rows with an exact same-source static PC anchor advance to the
        # strict name-label contract below; prose and unrelated labels are not
        # failures merely because they contain that syllable.
        if not matching_anchors:
            continue
        if (
            not STATIC_JP_NAME_RE.fullmatch(japanese)
            or not STATIC_KO_NAME_RE.fullmatch(core_current)
            or not STATIC_KO_NAME_RE.fullmatch(core_proposed)
            or KANA_OR_HAN_RE.search(core_proposed)
        ):
            raise ReviewError(f"candidate is not a static PC name-label shape: {coordinate}")
        identifier = int(coordinate)
        if identifier in candidate_ids:
            raise ReviewError(f"duplicate candidate id: {identifier}")
        candidate_ids.add(identifier)
        source_groups.add(japanese)
        anchors = [
            {
                "coordinate": anchor["coordinate"],
                "current_pc_ko_utf16le_sha256": text_hash(anchor["korean"]),
                "overlay_active": anchor["overlay_active"],
                "pristine_jp_utf16le_sha256": text_hash(japanese),
                "resource": "MSG/JP/strdata.bin",
                "visible_korean": anchor["visible_korean"],
            }
            for anchor in sorted(matching_anchors, key=lambda item: coordinate_key(item["coordinate"]))
        ]
        rows.append(
            {
                "allowed_format_delta": [],
                "confidence": "high",
                "current_hash": text_hash(current),
                "current_korean": current,
                "format_contract": profile(current),
                "id": identifier,
                "input_file_sha256": {
                    "committed_pc_quality_overlay": metadata["committed_overlay_sha256"],
                    "msgdata_en": hashes["msgdata_en"],
                    "msgdata_jp": hashes["msgdata_jp"],
                    "msgdata_ko": hashes["msgdata_ko"],
                    "msgdata_sc": hashes["msgdata_sc"],
                    "msgdata_tc": hashes["msgdata_tc"],
                    "strdata_jp": hashes["strdata_jp"],
                    "strdata_ko": hashes["strdata_ko"],
                },
                "issue_type": "pc_static_name_tsu_reading_outer_whitespace_inconsistency",
                "ko": current,
                "pc_context_utf16le_sha256": {
                    language.upper(): text_hash(tables[f"msgdata_{language}"][coordinate])
                    for language in ("en", "sc", "tc")
                },
                "pristine_jp_utf16le_sha256": text_hash(japanese),
                "proposed_ko": proposed,
                "proposed_ko_utf16le_sha256": text_hash(proposed),
                "reference_rule": "same_pristine_pc_jp_static_label_and_visible_pc_strdata_ko_anchor_exact_after_tsu_to_ssu_with_outer_whitespace_preserved",
                "reference_static_anchors": anchors,
                "resource": "msgdata",
                "source_current_utf16le_sha256": text_hash(current),
                "source_japanese": japanese,
                "switch_korean_translation_used": False,
            }
        )

    if len(rows) != EXPECTED_CANDIDATE_COUNT:
        raise ReviewError(f"candidate count drift: {len(rows)}")
    if len(source_groups) != EXPECTED_SOURCE_GROUP_COUNT:
        raise ReviewError(f"source-group count drift: {len(source_groups)}")
    if len(candidate_ids) != len(rows):
        raise ReviewError("candidate identifiers are not unique")
    if candidate_ids.intersection({int(value) for value in active_msgdata}):
        raise ReviewError("candidate identifiers overlap committed msgdata corrections")
    summary = {
        "candidate_count": len(rows),
        "committed_active_msgdata_coordinate_count": metadata["committed_active_coordinate_counts"]["msgdata"],
        "committed_active_strdata_coordinate_count": metadata["committed_active_coordinate_counts"]["strdata"],
        "committed_pc_quality_overlay_sha256": metadata["committed_overlay_sha256"],
        "expected_candidate_count": EXPECTED_CANDIDATE_COUNT,
        "expected_source_group_count": EXPECTED_SOURCE_GROUP_COUNT,
        "game_files_written": False,
        "private_candidate_path": PRIVATE_CANDIDATES.relative_to(REPO).as_posix(),
        "source_group_count": len(source_groups),
        "source_policy": "pristine_pc_japanese_and_current_pc_static_korean_anchors_with_pc_en_sc_tc_context_only",
        "switch_korean_translation_used": False,
    }
    return rows, summary


def validation_payload(rows: list[dict[str, Any]], summary: Mapping[str, Any], candidate_sha256: str) -> dict[str, Any]:
    payload = {
        "candidate_count": len(rows),
        "candidate_jsonl_sha256": candidate_sha256,
        "checks": {
            "all_deltas_are_tsu_to_ssu_only": "OK",
            "candidate_coordinates_disjoint_from_committed_msgdata_overlay": "OK",
            "exact_pristine_pc_jp_to_pc_strdata_anchor": "OK",
            "outer_whitespace_and_format_tokens_preserved": "OK",
            "pc_en_sc_tc_context_hashes_recorded": "OK",
            "steam_installation_written": False,
        },
        "contains_commercial_source_text": False,
        "game_files_written": False,
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "source_group_count": summary["source_group_count"],
        "switch_korean_translation_used": False,
    }
    blob = pretty_json(payload)
    assert_public_source_free(blob)
    return payload


def write_artifacts(rows: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    candidate_blob = canonical_jsonl(rows)
    atomic_write_bytes(PRIVATE_CANDIDATES, candidate_blob, OUTPUT_ROOT)
    candidate_sha256 = sha256_file(PRIVATE_CANDIDATES)
    validation = validation_payload(rows, summary, candidate_sha256)
    atomic_write_bytes(VALIDATION, pretty_json(validation), WORKSTREAM)
    summary = dict(summary)
    summary["candidate_jsonl_sha256"] = candidate_sha256
    summary["validation_path"] = VALIDATION.relative_to(REPO).as_posix()
    summary["validation_sha256"] = sha256_file(VALIDATION)
    return summary


def validate_artifacts(rows: list[dict[str, Any]], summary: Mapping[str, Any]) -> dict[str, Any]:
    if not PRIVATE_CANDIDATES.is_file() or not VALIDATION.is_file():
        raise ReviewError("write the private candidates and validation before validating")
    candidate_blob = canonical_jsonl(rows)
    actual_candidate = PRIVATE_CANDIDATES.read_bytes()
    if actual_candidate != candidate_blob:
        raise ReviewError("private candidate JSONL differs from deterministic PC-only rebuild")
    candidate_sha256 = sha256_file(PRIVATE_CANDIDATES)
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    expected_validation = validation_payload(rows, summary, candidate_sha256)
    if validation != expected_validation:
        raise ReviewError("source-free validation summary differs from deterministic rebuild")
    assert_public_source_free(VALIDATION.read_bytes())
    return {
        "candidate_count": len(rows),
        "candidate_jsonl_sha256": candidate_sha256,
        "checks": "OK",
        "game_files_written": False,
        "switch_korean_translation_used": False,
        "validation_sha256": sha256_file(VALIDATION),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true", help="write private PC-only candidates and source-free validation")
    action.add_argument("--validate", action="store_true", help="rebuild and verify the written candidates without applying them")
    args = parser.parse_args()
    rows, summary = build_rows()
    result = write_artifacts(rows, summary) if args.write else validate_artifacts(rows, summary)
    print(json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
