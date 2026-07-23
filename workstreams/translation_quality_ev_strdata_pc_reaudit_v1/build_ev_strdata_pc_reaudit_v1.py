#!/usr/bin/env python3
"""Build a private, PC-only semantic re-audit for all ``ev_strdata`` rows.

The audit deliberately has a narrow write surface.  It reads only pristine PC
Japanese, current PC Korean, and current PC Simplified/Traditional Chinese
``ev_strdata`` tables.  A separate source-free coordinate ledger is read only
to avoid proposing coordinates already owned by an existing workstream; no
generic-overlay Korean text, Switch Korean text, historic Korean text, Steam
game resource, or generic builder is opened.

The full 17,868-coordinate ledger is source-free.  The private candidate file
contains only five independently adjudicated, equal-width proper-name-reading
fixes.  Every candidate keeps the current line-break vector, ESC tags,
runtime/printf tokens, controls, PUA, and outer whitespace byte-for-byte at
the string-structure level.  No candidate moves a manual line break.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp"
VALIDATION_PATH = WORKSTREAM / "validation.v1.json"

if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))

DEFAULT_PRISTINE_ROOT = Path(r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root")
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "translation_quality_ev_strdata_pc_reaudit_v1"
SOURCE_FREE_LEDGER = TMP_ROOT / "translation_quality_pc_coverage_manifest_v1" / "merged_pc_only_coordinate_dispositions.v1.jsonl"

RESOURCE = Path("MSG") / "JP" / "ev_strdata.bin"
SC_RESOURCE = Path("MSG") / "SC" / "ev_strdata.bin"
TC_RESOURCE = Path("MSG") / "TC" / "ev_strdata.bin"

EXPECTED_STRING_COUNT = 17_868
EXPECTED_FILE_SHA256 = {
    "pristine_pc_jp": "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
    "current_pc_ko": "6A7D90C1A95AD42DCAE2D3C3719508EDD00588288659A1D192B680CF70EAE6E4",
    "pc_sc": "77E87C6FEC67859543FCB4134660A7274A2374F6881B956421B561E61BD7B685",
    "pc_tc": "9E9346B942CAFA99432D675F6BA74DD04D48F56095F35F46392697011D9CFEF3",
    "source_free_coordinate_ledger": "43187327477634855B8D057AC1CE56E54692D2330ADF4C40395C67415B2C9931",
}

SCHEMA = "nobu16.kr.ev-strdata-pc-reaudit.v1"
CANDIDATE_SCHEMA = "nobu16.kr.ev-strdata-pc-reaudit-candidate.v1"
HOLD_SCHEMA = "nobu16.kr.ev-strdata-pc-reaudit-hold.v1"
LEDGER_SCHEMA = "nobu16.kr.ev-strdata-pc-reaudit-coordinate.v1"

ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[([A-Za-z]{1,16})(\d+)\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")

# These source-side categories are triage metadata only.  They contain no
# commercial source text in the emitted source-free ledger.
RISK_MARKERS: Mapping[str, tuple[str, ...]] = {
    "historical_office": ("公方", "管領", "守護", "守護代", "関白"),
    "inheritance": ("家督", "相続", "養子", "廃嫡", "隠居"),
    "war_outcome": ("討死", "戦死", "自害", "落城", "降伏", "滅亡"),
    "intrigue": ("調略", "内応", "寝返り", "謀反", "離反"),
    "captivity": ("捕縛", "捕虜", "人質", "幽閉", "追放"),
}


@dataclass(frozen=True)
class Candidate:
    identifier: int
    old: str
    new: str
    issue_type: str
    rationale: str
    jp_markers: tuple[str, ...]
    sc_markers: tuple[str, ...]
    tc_markers: tuple[str, ...]
    phonetic_source_ids: tuple[tuple[int, str], ...] = ()
    pc_ko_consistency_ids: tuple[tuple[int, str, str], ...] = ()


# The only automatic edits are independently rechecked reading repairs.  They
# replace Hangul with the same number of Hangul code points on the same line;
# no line break is removed, inserted, or moved.
CANDIDATES: tuple[Candidate, ...] = (
    Candidate(
        4261,
        "도키 요리아키",
        "도키 요리나리",
        "proper_name_reading",
        "土岐頼芸 is rendered inconsistently in the current PC Korean table; the same PC resource has the verified reading 요리나리 at coordinate 9469.",
        ("土岐頼芸",),
        ("土岐赖艺",),
        ("土岐賴藝",),
        pc_ko_consistency_ids=((9469, "土岐頼芸", "도키 요리나리"),),
    ),
    Candidate(
        6900,
        "시마즈 짓신사이",
        "시마즈 닛신사이",
        "proper_name_reading",
        "PC JP phonetic companion coordinate 14510 spells the name シマヅニッシンサイ; current PC Korean at 7033 independently matches 닛신사이.",
        ("島津日新斎",),
        ("岛津日新斋",),
        ("島津日新齋",),
        phonetic_source_ids=((14510, "シマヅニッシンサイ"),),
    ),
    Candidate(
        6926,
        "시마즈 짓신사이",
        "시마즈 닛신사이",
        "proper_name_reading",
        "PC JP phonetic companion coordinate 14510 spells the name シマヅニッシンサイ; current PC Korean at 7033 independently matches 닛신사이.",
        ("島津日新斎",),
        ("岛津日新斋",),
        ("島津日新齋",),
        phonetic_source_ids=((14510, "シマヅニッシンサイ"),),
    ),
    Candidate(
        9148,
        "마스히데",
        "야스히데",
        "proper_name_reading",
        "PC JP phonetic companion coordinates 14276 and 14487 spell ガモウヤスヒデ; current PC Korean at 5567 and 9146 independently uses 야스히데.",
        ("賦秀", "蒲生家"),
        ("赋秀", "蒲生家"),
        ("賦秀", "蒲生家"),
        phonetic_source_ids=((14276, "ガモウヤスヒデ"), (14487, "ガモウヤスヒデ")),
        pc_ko_consistency_ids=((5567, "賦秀", "야스히데"), (9146, "賦秀", "야스히데")),
    ),
    Candidate(
        9470,
        "도키 요리아키",
        "도키 요리나리",
        "proper_name_reading",
        "土岐頼芸 is rendered inconsistently in the current PC Korean table; the same PC resource has the verified reading 요리나리 at coordinate 9469.",
        ("土岐頼芸",),
        ("土岐赖艺",),
        ("土岐賴藝",),
        pc_ko_consistency_ids=((9469, "土岐頼芸", "도키 요리나리"),),
    ),
)


class AuditError(ValueError):
    """Raised when a pinned input or a candidate safety gate diverges."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16-le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    lines = [json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for row in rows]
    return (("\n".join(lines) + "\n") if lines else "").encode("utf-8")


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise AuditError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def id_hash(ids: Iterable[int]) -> str:
    return sha256(json.dumps(sorted(ids), separators=(",", ":")).encode("ascii"))


def safe_input(root: Path, relative: Path) -> Path:
    base = root.resolve(strict=True)
    path = (base / relative).resolve(strict=True)
    try:
        path.relative_to(base)
    except ValueError as exc:
        raise AuditError(f"input escaped root: {relative}") from exc
    if not path.is_file():
        raise AuditError(f"required input is not a file: {path}")
    return path


def safe_private_path(path: Path) -> Path:
    resolved = path.resolve(strict=True)
    root = TMP_ROOT.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise AuditError("source-free coordinate ledger is outside repository tmp") from exc
    return resolved


def safe_output_root(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise AuditError("output root must remain below repository tmp") from exc
    if resolved == root:
        raise AuditError("repository tmp itself is not an output root")
    return resolved


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_message_table(path: Path, label: str) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    from nobu16_lz4 import decompress_wrapper
    from nobu16_msg_table import parse_message_table, rebuild_message_table

    packed = path.read_bytes()
    try:
        _header, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
    except Exception as exc:
        raise AuditError(f"cannot parse {label}: {path}") from exc
    require(table.string_count, EXPECTED_STRING_COUNT, f"{label} string count")
    require(rebuild_message_table(table, table.texts), raw, f"{label} parse/rebuild")
    return table, {"size": len(packed), "sha256": sha256(packed)}, {"size": len(raw), "sha256": sha256(raw)}


def load_sources(steam_root: Path, pristine_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    paths = {
        "pristine_pc_jp": safe_input(pristine_root, RESOURCE),
        "current_pc_ko": safe_input(steam_root, RESOURCE),
        "pc_sc": safe_input(steam_root, SC_RESOURCE),
        "pc_tc": safe_input(steam_root, TC_RESOURCE),
    }
    loaded: dict[str, Any] = {}
    specs: dict[str, Any] = {}
    for label, path in paths.items():
        table, packed, raw = load_message_table(path, label)
        require(packed["sha256"], EXPECTED_FILE_SHA256[label], f"{label} packed pin")
        loaded[label] = table
        specs[label] = {
            "resource": (
                RESOURCE.as_posix()
                if label in ("pristine_pc_jp", "current_pc_ko")
                else (SC_RESOURCE if label == "pc_sc" else TC_RESOURCE).as_posix()
            ),
            "packed": packed,
            "raw": raw,
        }
    specs["pc_en"] = {
        "resource": "MSG/EN/ev_strdata.bin",
        "available": False,
        "reason": "current PC installation has no EN ev_strdata resource",
    }
    return loaded, specs


def source_free_exclusions() -> tuple[dict[int, str], dict[str, Any]]:
    path = safe_private_path(SOURCE_FREE_LEDGER)
    raw = path.read_bytes()
    require(sha256(raw), EXPECTED_FILE_SHA256["source_free_coordinate_ledger"], "source-free coordinate ledger pin")
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuditError("source-free coordinate ledger is not UTF-8") from exc
    # Do not accept a ledger that starts carrying Korean/Japanese source text.
    if any(0x3040 <= ord(char) <= 0x30FF or 0x3400 <= ord(char) <= 0x9FFF or 0xAC00 <= ord(char) <= 0xD7A3 for char in decoded):
        raise AuditError("source-free coordinate ledger unexpectedly contains CJK/Hangul text")

    ev_rows: dict[int, str] = {}
    for line_number, line in enumerate(decoded.splitlines(), start=1):
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AuditError(f"source-free coordinate ledger JSON error at line {line_number}") from exc
        if row.get("resource") != "ev_strdata":
            continue
        try:
            identifier = int(row["coordinate"])
        except (KeyError, TypeError, ValueError) as exc:
            raise AuditError(f"invalid ev_strdata coordinate at source-free ledger line {line_number}") from exc
        disposition = row.get("input_disposition")
        if not isinstance(disposition, str):
            raise AuditError(f"missing source-free disposition at coordinate {identifier}")
        if identifier in ev_rows:
            raise AuditError(f"duplicate ev_strdata source-free coordinate {identifier}")
        ev_rows[identifier] = disposition
    require(set(ev_rows), set(range(EXPECTED_STRING_COUNT)), "source-free ev_strdata coordinate coverage")
    exclusions = {identifier: status for identifier, status in ev_rows.items() if status != "retained_after_pc_only_triage"}
    require(len(exclusions), 289, "source-free non-retained exclusion count")
    return exclusions, {
        "path": SOURCE_FREE_LEDGER.relative_to(REPO).as_posix(),
        "size": len(raw),
        "sha256": sha256(raw),
        "ev_strdata_coordinate_count": len(ev_rows),
        "excluded_coordinate_count": len(exclusions),
        "text_fields_read": False,
        "generic_overlay_read": False,
    }


def format_profile(value: str) -> dict[str, Any]:
    escapes = list(ESC_RE.finditer(value))
    escape_offsets = {
        offset for match in escapes for offset in range(match.start(), match.end())
    }
    printf = list(PRINTF_RE.finditer(value))
    printf_offsets = {
        offset
        for match in printf
        for offset in range(match.start(), match.end())
        if value[offset] == "%"
    }
    leading = re.match(r"^\s*", value)
    trailing = re.search(r"\s*$", value)
    return {
        "escape_tags": [match.group(0) for match in escapes],
        "runtime_tokens": [match.group(0) for match in RUNTIME_RE.finditer(value)],
        "printf": [match.group(0) for match in printf],
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in printf_offsets
        ),
        "controls": [
            f"U+{ord(character):04X}"
            for offset, character in enumerate(value)
            if ord(character) < 32 and character not in ("\r", "\n") and offset not in escape_offsets
        ],
        "pua": [f"U+{ord(character):04X}" for character in value if 0xE000 <= ord(character) <= 0xF8FF],
        "outer_leading_whitespace": leading.group(0) if leading is not None else "",
        "outer_trailing_whitespace": trailing.group(0) if trailing is not None else "",
        "linebreak_vector": LINEBREAK_RE.findall(value),
    }


def profile_hash(profile: Mapping[str, Any]) -> str:
    return sha256(json.dumps(profile, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii"))


def visible_text(value: str) -> str:
    return RUNTIME_RE.sub("", ESC_RE.sub("", value))


def visible_line_codepoint_counts(value: str) -> list[int]:
    return [len(line) for line in LINEBREAK_RE.sub("\n", visible_text(value)).split("\n")]


def require_equal_hangul_replacement(old: str, new: str, identifier: int) -> None:
    if len(old) != len(new):
        raise AuditError(f"id {identifier} replacement changes visible codepoint count")
    if not old or not new:
        raise AuditError(f"id {identifier} replacement is empty")
    for before, after in zip(old, new, strict=True):
        if before == after:
            continue
        if not ("가" <= before <= "힣" and "가" <= after <= "힣"):
            raise AuditError(f"id {identifier} replacement is not Hangul-to-Hangul")


def risk_categories(source: str) -> list[str]:
    return sorted(category for category, markers in RISK_MARKERS.items() if any(marker in source for marker in markers))


def candidate_by_id() -> dict[int, Candidate]:
    result = {candidate.identifier: candidate for candidate in CANDIDATES}
    require(len(result), len(CANDIDATES), "candidate coordinate uniqueness")
    return result


def evidence_rows(candidate: Candidate, tables: Mapping[str, Any]) -> dict[str, Any]:
    phonetic: list[dict[str, Any]] = []
    for identifier, marker in candidate.phonetic_source_ids:
        value = tables["pristine_pc_jp"].texts[identifier]
        if marker not in value:
            raise AuditError(f"id {candidate.identifier} PC JP phonetic evidence differs at {identifier}")
        phonetic.append({"id": identifier, "utf16le_sha256": text_hash(value), "marker_verified": True})
    consistency: list[dict[str, Any]] = []
    for identifier, jp_marker, ko_marker in candidate.pc_ko_consistency_ids:
        jp = tables["pristine_pc_jp"].texts[identifier]
        ko = tables["current_pc_ko"].texts[identifier]
        if jp_marker not in jp or ko_marker not in ko:
            raise AuditError(f"id {candidate.identifier} current-PC consistency evidence differs at {identifier}")
        consistency.append(
            {
                "id": identifier,
                "pristine_jp_utf16le_sha256": text_hash(jp),
                "current_ko_utf16le_sha256": text_hash(ko),
                "markers_verified": True,
            }
        )
    return {"pc_jp_phonetic_companions": phonetic, "current_pc_ko_consistency": consistency}


def build_documents(steam_root: Path, pristine_root: Path) -> tuple[bytes, bytes, bytes, bytes, dict[str, Any]]:
    tables, input_specs = load_sources(steam_root, pristine_root)
    exclusions, exclusion_spec = source_free_exclusions()
    candidates_by_id = candidate_by_id()
    overlap = set(candidates_by_id).intersection(exclusions)
    if overlap:
        raise AuditError(f"candidate overlaps prior source-free coordinate: {sorted(overlap)}")

    candidate_rows: list[dict[str, Any]] = []
    hold_rows: list[dict[str, Any]] = []
    ledger_rows: list[dict[str, Any]] = []

    for identifier in range(EXPECTED_STRING_COUNT):
        jp = tables["pristine_pc_jp"].texts[identifier]
        ko = tables["current_pc_ko"].texts[identifier]
        sc = tables["pc_sc"].texts[identifier]
        tc = tables["pc_tc"].texts[identifier]
        before_profile = format_profile(ko)

        disposition: str
        candidate = candidates_by_id.get(identifier)
        if identifier in exclusions:
            disposition = "excluded_prior_source_free_coordinate"
        elif candidate is None:
            disposition = "scanned_no_new_high_confidence_candidate"
        else:
            if ko.count(candidate.old) != 1:
                raise AuditError(f"id {identifier} current PC Korean candidate fragment differs")
            if not all(marker in jp for marker in candidate.jp_markers):
                raise AuditError(f"id {identifier} pristine JP evidence differs")
            if not all(marker in sc for marker in candidate.sc_markers):
                raise AuditError(f"id {identifier} PC SC evidence differs")
            if not all(marker in tc for marker in candidate.tc_markers):
                raise AuditError(f"id {identifier} PC TC evidence differs")
            require_equal_hangul_replacement(candidate.old, candidate.new, identifier)
            proposed = ko.replace(candidate.old, candidate.new)
            after_profile = format_profile(proposed)
            require(after_profile, before_profile, f"id {identifier} protected format profile")
            before_lines = visible_line_codepoint_counts(ko)
            after_lines = visible_line_codepoint_counts(proposed)
            require(after_lines, before_lines, f"id {identifier} visible per-line codepoint counts")
            if "\n" in candidate.old or "\n" in candidate.new or "\r" in candidate.old or "\r" in candidate.new:
                raise AuditError(f"id {identifier} candidate attempts a line-break edit")
            candidate_rows.append(
                {
                    "schema": CANDIDATE_SCHEMA,
                    "resource": "ev_strdata",
                    "id": identifier,
                    "current_ko": ko,
                    "proposed_ko": proposed,
                    "source_jp": jp,
                    "reference_contexts": {"SC": sc, "TC": tc},
                    "source_hashes": {
                        "current_ko_utf16le_sha256": text_hash(ko),
                        "pristine_jp_utf16le_sha256": text_hash(jp),
                        "pc_sc_utf16le_sha256": text_hash(sc),
                        "pc_tc_utf16le_sha256": text_hash(tc),
                        "proposed_ko_utf16le_sha256": text_hash(proposed),
                    },
                    "issue_type": candidate.issue_type,
                    "confidence": "high",
                    "rationale": candidate.rationale,
                    "format_gate": {
                        "before_profile": before_profile,
                        "after_profile": after_profile,
                        "preserved": True,
                        "visible_line_codepoint_counts": before_lines,
                        "manual_linebreak_moved": False,
                        "equal_width_proxy": "same-line Hangul-to-Hangul replacement with identical visible codepoint counts",
                    },
                    "pc_only_evidence": evidence_rows(candidate, tables),
                    "scope": {
                        "pristine_pc_jp_used": True,
                        "pc_sc_tc_used": True,
                        "current_pc_ko_used": True,
                        "generic_overlay_korean_text_read": False,
                        "switch_korean_translation_used": False,
                        "historic_korean_translation_used": False,
                        "steam_game_resource_written": False,
                    },
                }
            )
            disposition = "candidate_high_confidence"

        ledger_row: dict[str, Any] = {
            "schema": LEDGER_SCHEMA,
            "resource": "ev_strdata",
            "id": identifier,
            "disposition": disposition,
            "source_free_evidence": {
                "pristine_jp_utf16le_sha256": text_hash(jp),
                "current_ko_utf16le_sha256": text_hash(ko),
                "pc_sc_utf16le_sha256": text_hash(sc),
                "pc_tc_utf16le_sha256": text_hash(tc),
                "current_ko_format_profile_sha256": profile_hash(before_profile),
                "source_risk_categories": risk_categories(jp),
            },
        }
        if identifier in exclusions:
            ledger_row["prior_source_free_disposition"] = exclusions[identifier]
        if candidate is not None and identifier not in exclusions:
            ledger_row["issue_type"] = candidate.issue_type
        ledger_rows.append(ledger_row)

    candidate_blob = canonical_jsonl(candidate_rows)
    hold_blob = canonical_jsonl(hold_rows)
    ledger_blob = canonical_jsonl(ledger_rows)
    validation = {
        "schema": SCHEMA,
        "scope": {
            "translation_contexts": ["pristine_pc_jp", "pc_sc", "pc_tc", "current_pc_ko"],
            "generic_overlay_korean_text_read": False,
            "generic_builder_read": False,
            "historic_korean_translation_used": False,
            "switch_korean_translation_used": False,
            "steam_game_resource_written": False,
            "generic_builder_modified": False,
            "commit_created": False,
        },
        "inputs": input_specs,
        "source_free_overlap_exclusions": exclusion_spec,
        "selection": {
            "expected_coordinate_count": EXPECTED_STRING_COUNT,
            "ledger_coordinate_count": len(ledger_rows),
            "ledger_coordinate_ids_sha256": id_hash(row["id"] for row in ledger_rows),
            "excluded_prior_coordinate_count": len(exclusions),
            "excluded_prior_coordinate_ids_sha256": id_hash(exclusions),
            "new_high_confidence_candidate_count": len(candidate_rows),
            "new_high_confidence_candidate_ids": [row["id"] for row in candidate_rows],
            "new_high_confidence_candidate_ids_sha256": id_hash(row["id"] for row in candidate_rows),
            "new_hold_count": len(hold_rows),
            "manual_linebreak_edit_candidate_count": 0,
            "semantic_completion": False,
            "semantic_completion_reason": "A full PC-only coordinate scan and high-confidence correction pass do not prove exhaustive gameplay-context semantic completion.",
        },
        "checks": {
            "all_17868_coordinates_accounted_for": len(ledger_rows) == EXPECTED_STRING_COUNT,
            "source_file_pins": True,
            "source_free_overlap_ledger_pin": True,
            "source_free_overlap_ledger_contains_no_cjk_or_hangul_text": True,
            "existing_coordinates_excluded_without_generic_overlay_read": True,
            "candidate_source_preimages_pinned": True,
            "candidate_jp_sc_tc_evidence_pinned": True,
            "candidate_format_profiles_preserved": True,
            "candidate_manual_linebreak_vectors_preserved": True,
            "candidate_visible_per_line_codepoint_counts_preserved": True,
            "candidate_hangul_replacements_equal_count": True,
            "no_new_linebreak_move_candidate": True,
            "private_candidate_only": True,
        },
        "outputs": {
            "private_candidates": {
                "relative_path": "tmp/translation_quality_ev_strdata_pc_reaudit_v1/ev_strdata_pc_reaudit_candidates.v1.jsonl",
                "size": len(candidate_blob),
                "sha256": sha256(candidate_blob),
            },
            "private_holds": {
                "relative_path": "tmp/translation_quality_ev_strdata_pc_reaudit_v1/ev_strdata_pc_reaudit_holds.v1.jsonl",
                "size": len(hold_blob),
                "sha256": sha256(hold_blob),
            },
            "source_free_coordinate_ledger": {
                "relative_path": "tmp/translation_quality_ev_strdata_pc_reaudit_v1/ev_strdata_pc_reaudit_coordinate_ledger.source_free.v1.jsonl",
                "size": len(ledger_blob),
                "sha256": sha256(ledger_blob),
            },
        },
    }
    return candidate_blob, hold_blob, ledger_blob, canonical_json(validation), validation


def output_paths(root: Path) -> tuple[Path, Path, Path]:
    return (
        root / "ev_strdata_pc_reaudit_candidates.v1.jsonl",
        root / "ev_strdata_pc_reaudit_holds.v1.jsonl",
        root / "ev_strdata_pc_reaudit_coordinate_ledger.source_free.v1.jsonl",
    )


def write(steam_root: Path, pristine_root: Path, output_root: Path) -> dict[str, Any]:
    output = safe_output_root(output_root)
    candidate_blob, hold_blob, ledger_blob, validation_blob, validation = build_documents(steam_root, pristine_root)
    candidate_path, hold_path, ledger_path = output_paths(output)
    atomic_write(candidate_path, candidate_blob)
    atomic_write(hold_path, hold_blob)
    atomic_write(ledger_path, ledger_blob)
    atomic_write(VALIDATION_PATH, validation_blob)
    require(candidate_path.read_bytes(), candidate_blob, "written private candidates")
    require(hold_path.read_bytes(), hold_blob, "written private holds")
    require(ledger_path.read_bytes(), ledger_blob, "written source-free coordinate ledger")
    require(VALIDATION_PATH.read_bytes(), validation_blob, "written validation contract")
    return {
        "status": "OK",
        "new_high_confidence_candidate_count": validation["selection"]["new_high_confidence_candidate_count"],
        "new_hold_count": validation["selection"]["new_hold_count"],
        "excluded_prior_coordinate_count": validation["selection"]["excluded_prior_coordinate_count"],
        "candidate_sha256": validation["outputs"]["private_candidates"]["sha256"],
        "ledger_sha256": validation["outputs"]["source_free_coordinate_ledger"]["sha256"],
        "validation_sha256": sha256(validation_blob),
        "steam_game_resource_written": False,
    }


def validate(steam_root: Path, pristine_root: Path, output_root: Path) -> dict[str, Any]:
    output = safe_output_root(output_root)
    candidate_blob, hold_blob, ledger_blob, validation_blob, validation = build_documents(steam_root, pristine_root)
    candidate_path, hold_path, ledger_path = output_paths(output)
    for path, expected, label in (
        (candidate_path, candidate_blob, "private candidates"),
        (hold_path, hold_blob, "private holds"),
        (ledger_path, ledger_blob, "source-free coordinate ledger"),
        (VALIDATION_PATH, validation_blob, "validation contract"),
    ):
        if not path.is_file():
            raise AuditError("write must run before deterministic validation")
        require(path.read_bytes(), expected, f"deterministic {label}")
    return {
        "status": "OK",
        "all_17868_coordinates_accounted_for": "OK",
        "new_high_confidence_candidate_count": validation["selection"]["new_high_confidence_candidate_count"],
        "new_hold_count": validation["selection"]["new_hold_count"],
        "excluded_prior_coordinate_count": validation["selection"]["excluded_prior_coordinate_count"],
        "format_and_linebreak_gates": "OK",
        "source_free_overlap_exclusion": "OK",
        "deterministic_private_outputs": "OK",
        "steam_game_resource_written": False,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument("--write", action="store_true")
    command.add_argument("--validate", action="store_true")
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--pristine-root", type=Path, default=DEFAULT_PRISTINE_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = (
            write(args.steam_root, args.pristine_root, args.output_root)
            if args.write
            else validate(args.steam_root, args.pristine_root, args.output_root)
        )
    except AuditError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
