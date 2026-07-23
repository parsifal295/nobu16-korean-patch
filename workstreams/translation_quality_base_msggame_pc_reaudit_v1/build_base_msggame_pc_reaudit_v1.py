#!/usr/bin/env python3
"""Build a private PC-only semantic re-audit for base ``msggame``.

This intentionally reads no Switch Korean or historic Korean translation.
The only textual evidence is pristine PC Japanese, current PC Korean, and
same-coordinate Steam PC Simplified/Traditional Chinese.  The pre-existing
generic-overlay work is consulted solely through a source-free coordinate
ledger; generic-overlay Korean text and its builder are never opened.

The generated candidate file is private under ``tmp``.  It is a review
artifact, not a game-resource writer.  It has no Steam, generic-builder, git,
commit, push, or release side effect.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
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

DEFAULT_PRISTINE_ROOT = Path(r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root")
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "translation_quality_base_msggame_pc_reaudit_v1"
SOURCE_FREE_LEDGER = (
    TMP_ROOT
    / "translation_quality_pc_coverage_manifest_v1"
    / "merged_pc_only_coordinate_dispositions.v1.jsonl"
)

KO_RESOURCE = Path("MSG") / "JP" / "msggame.bin"
SC_RESOURCE = Path("MSG") / "SC" / "msggame.bin"
TC_RESOURCE = Path("MSG") / "TC" / "msggame.bin"
EN_RESOURCE = Path("MSG") / "EN" / "msggame.bin"

EXPECTED_LITERAL_COUNT = 24_262
EXPECTED_FROZEN_COORDINATE_COUNT = 202
EXPECTED_FILE_SHA256 = {
    "pristine_pc_jp": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    "current_pc_ko": "8DBFCDB21BBDAAD4FE3928AD5B7AAA0D51E56D01F206DFE4D129E354FA5DEDE2",
    "pc_sc": "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7",
    "pc_tc": "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95",
    "source_free_coordinate_ledger": "43187327477634855B8D057AC1CE56E54692D2330ADF4C40395C67415B2C9931",
}

SCHEMA = "nobu16.kr.base-msggame-pc-reaudit.v1"
CANDIDATE_SCHEMA = "nobu16.kr.base-msggame-pc-reaudit-candidate.v1"
HOLD_SCHEMA = "nobu16.kr.base-msggame-pc-reaudit-hold.v1"
LEDGER_SCHEMA = "nobu16.kr.base-msggame-pc-reaudit-coordinate.v1"

ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[([A-Za-z]{1,16})(\d+)\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")


@dataclass(frozen=True)
class Candidate:
    coordinate: str
    current_ko: str
    proposed_ko: str
    source_jp: str
    pc_sc: str
    pc_tc: str
    issue_type: str
    rationale: str


# Each correction is one final Hangul syllable (U+C788 -> U+C5C6).  It keeps
# the literal length, every newline, and per-line visual codepoint count.
CANDIDATES: tuple[Candidate, ...] = (
    Candidate(
        coordinate="7:2436:0",
        current_ko=(
            "\ub77c\uba74\n"
            "\ubcd1\uc0ac\uac00 \uc5b4\ub290 \uc815\ub3c4 \ud544\uc694\ud55c\uc9c0 \ud310\ub2e8\ud560 \uc218 \uc788"
        ),
        proposed_ko=(
            "\ub77c\uba74\n"
            "\ubcd1\uc0ac\uac00 \uc5b4\ub290 \uc815\ub3c4 \ud544\uc694\ud55c\uc9c0 \ud310\ub2e8\ud560 \uc218 \uc5c6"
        ),
        source_jp="\u3067\u306f\n\u5175\u304c\u3069\u306e\u7a0b\u5ea6\u5fc5\u8981\u304b\u5224\u65ad\u3067\u304d",
        pc_sc="\u65e0\u6cd5\u5224\u65ad\u9700\u8981\u591a\u5c11\u5175\u529b\uff0c\n\u8bf7\u76f4\u63a5\u7ed9\u4e88\u6307\u793a\u3002",
        pc_tc="\u7121\u6cd5\u5224\u65b7\u9808\u6709\u591a\u5c11\u5175\u529b\uff0c\n\u8acb\u76f4\u63a5\u7d66\u4e88\u6307\u793a\u3002",
        issue_type="meaning_reversal_missing_negation",
        rationale=(
            "Current PC Korean says the required troop count can be determined, "
            "while both PC Chinese references explicitly say it cannot be determined."
        ),
    ),
    Candidate(
        coordinate="15:2249:0",
        current_ko=(
            "\uc678\uad50 \uad00\uacc4\uc0c1, \uc9c0\uae08\uc740 \uc5b4\ub290 \uc778\uc811 \uc138\ub825\uc5d0\ub3c4\n"
            "\uce68\uacf5\ud560 \uc218 \uc788\uc5b4"
        ),
        proposed_ko=(
            "\uc678\uad50 \uad00\uacc4\uc0c1, \uc9c0\uae08\uc740 \uc5b4\ub290 \uc778\uc811 \uc138\ub825\uc5d0\ub3c4\n"
            "\uce68\uacf5\ud560 \uc218 \uc5c6\uc5b4"
        ),
        source_jp=(
            "\u5916\u4ea4\u306e\u95a2\u4fc2\u4e0a\u3001\u4eca\u306f\u3044\u305a\u308c\u306e\u96a3\u63a5\u52e2\u529b\u306b\u3082\n"
            "\u4fb5\u653b\u3059\u308b\u3053\u3068\u304c\u3067\u304d"
        ),
        pc_sc=(
            "\u4ece\u5916\u4ea4\u5173\u7cfb\u4e0a\u6765\u8bf4\uff0c\u5df1\u65b9\u73b0\u5728\n"
            "\u65e0\u6cd5\u8fdb\u653b\u5468\u56f4\u4efb\u4f55\u4e00\u4e2a\u52bf\u529b\u3002"
        ),
        pc_tc=(
            "\u5f9e\u5916\u4ea4\u95dc\u4fc2\u4e0a\u4f86\u8aaa\uff0c\u76ee\u524d\u6211\u5011\u7121\u6cd5\u5c0d\n"
            "\u5468\u908a\u7684\u4efb\u4f55\u52e2\u529b\u767c\u52d5\u9032\u653b\u3002"
        ),
        issue_type="meaning_reversal_missing_negation",
        rationale=(
            "Current PC Korean says any neighbouring force can be invaded, "
            "while both PC Chinese references explicitly say no neighbouring force can be invaded."
        ),
    ),
)


class AuditError(ValueError):
    """Raised when a pinned input or safety contract diverges."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16-le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    lines = [
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for row in rows
    ]
    return (("\n".join(lines) + "\n") if lines else "").encode("utf-8")


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise AuditError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def coordinate_sort_key(coordinate: str) -> tuple[int, int, int]:
    try:
        block, record, literal = (int(piece) for piece in coordinate.split(":"))
    except ValueError as exc:
        raise AuditError(f"invalid literal coordinate: {coordinate!r}") from exc
    return block, record, literal


def id_hash(coordinates: Iterable[str]) -> str:
    values = sorted(coordinates, key=coordinate_sort_key)
    return sha256(json.dumps(values, separators=(",", ":")).encode("ascii"))


def is_cjk_or_hangul(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x3040 <= codepoint <= 0x30FF
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7A3
    )


def safe_input(root: Path, relative: Path) -> Path:
    base = root.resolve(strict=True)
    candidate = (base / relative).resolve(strict=True)
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise AuditError(f"input escaped root: {relative}") from exc
    if not candidate.is_file():
        raise AuditError(f"required input is not a file: {candidate}")
    return candidate


def safe_private_path(path: Path) -> Path:
    resolved = path.resolve(strict=True)
    root = TMP_ROOT.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise AuditError("source-free overlap ledger must be under repository tmp") from exc
    return resolved


def safe_output_root(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise AuditError("private output root must remain below repository tmp") from exc
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


def load_msggame_module() -> Any:
    path = REPO / "workstreams" / "msggame" / "msggame_format.py"
    spec = importlib.util.spec_from_file_location("base_msggame_reaudit_format", path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load msggame parser: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def literal_table(fmt: Any, archive: Any) -> dict[str, Any]:
    literals = list(fmt.iter_literals(archive))
    table = {
        f"{literal.block_id}:{literal.record_id}:{literal.literal_id}": literal
        for literal in literals
    }
    require(len(table), len(literals), "literal coordinate uniqueness")
    return table


def load_source(fmt: Any, path: Path, label: str) -> tuple[bytes, bytes, Any, dict[str, Any], dict[str, Any]]:
    packed = path.read_bytes()
    require(sha256(packed), EXPECTED_FILE_SHA256[label], f"{label} packed SHA-256 pin")
    try:
        parsed = fmt.parse_packed_msggame(packed)
        header, raw = fmt.decompress_wrapper(packed)
        rebuilt = fmt.rebuild_raw_msggame(parsed.archive)
    except Exception as exc:
        raise AuditError(f"cannot parse/rebuild {label}: {path}") from exc
    require(rebuilt, raw, f"{label} raw parse/rebuild byte exactness")
    return (
        packed,
        raw,
        parsed,
        {
            "packed_size": len(packed),
            "packed_sha256": sha256(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
            "wrapper_header": {
                "prefix": header.prefix.hex().upper(),
                "uncompressed_size": header.uncompressed_size,
                "compressed_size": header.compressed_size,
            },
            "block_count": len(parsed.archive.blocks),
            "record_count": parsed.archive.record_count,
        },
        {
            "raw_parse_rebuild_byte_exact": True,
            "wrapper_decompression": "OK",
        },
    )


def source_free_exclusions() -> tuple[dict[str, str], dict[str, Any]]:
    path = safe_private_path(SOURCE_FREE_LEDGER)
    raw = path.read_bytes()
    require(
        sha256(raw),
        EXPECTED_FILE_SHA256["source_free_coordinate_ledger"],
        "source-free overlap ledger SHA-256 pin",
    )
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuditError("source-free overlap ledger is not UTF-8") from exc
    if any(is_cjk_or_hangul(character) for character in decoded):
        raise AuditError("source-free overlap ledger unexpectedly contains CJK/Hangul source text")

    rows: dict[str, str] = {}
    for number, line in enumerate(decoded.splitlines(), start=1):
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AuditError(f"source-free overlap ledger JSON error at line {number}") from exc
        if row.get("resource") != "base_msggame":
            continue
        coordinate = row.get("coordinate")
        disposition = row.get("input_disposition")
        if not isinstance(coordinate, str) or not isinstance(disposition, str):
            raise AuditError(f"invalid base_msggame source-free row at line {number}")
        coordinate_sort_key(coordinate)
        if coordinate in rows:
            raise AuditError(f"duplicate base_msggame coordinate in source-free ledger: {coordinate}")
        rows[coordinate] = disposition

    frozen = {
        coordinate: disposition
        for coordinate, disposition in rows.items()
        if disposition == "frozen_pc_only_correction_status_recorded"
    }
    require(len(rows), EXPECTED_LITERAL_COUNT, "source-free base_msggame coordinate count")
    require(len(frozen), EXPECTED_FROZEN_COORDINATE_COUNT, "source-free frozen coordinate count")
    return frozen, {
        "relative_path": SOURCE_FREE_LEDGER.relative_to(REPO).as_posix(),
        "size": len(raw),
        "sha256": sha256(raw),
        "base_msggame_coordinate_count": len(rows),
        "frozen_coordinate_count": len(frozen),
        "generic_overlay_korean_text_read": False,
        "source_free_no_cjk_or_hangul_text": True,
    }


def format_profile(value: str) -> dict[str, Any]:
    escapes = list(ESC_RE.finditer(value))
    escape_offsets = {offset for match in escapes for offset in range(match.start(), match.end())}
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
    normalized = LINEBREAK_RE.sub("\n", visible_text(value))
    return [len(line) for line in normalized.split("\n")]


def changed_character_pairs(before: str, after: str) -> list[dict[str, str]]:
    if len(before) != len(after):
        raise AuditError("candidate changes codepoint length")
    return [
        {
            "before": f"U+{ord(old):04X}",
            "after": f"U+{ord(new):04X}",
        }
        for old, new in zip(before, after, strict=True)
        if old != new
    ]


def is_hangul_syllable(character: str) -> bool:
    return "\uac00" <= character <= "\ud7a3"


def candidate_map() -> dict[str, Candidate]:
    result = {candidate.coordinate: candidate for candidate in CANDIDATES}
    require(len(result), len(CANDIDATES), "candidate coordinate uniqueness")
    return result


def raw_candidate_gate(fmt: Any, packed: bytes, raw: bytes, archive: Any, replacements: Mapping[tuple[int, int, int], str]) -> dict[str, Any]:
    """Prove same-size literal changes preserve all untouched raw bytes."""
    rebuilt = fmt.rebuild_raw_with_literals(archive, replacements)
    require(len(rebuilt), len(raw), "candidate raw byte length")
    reparsed = fmt.parse_raw_msggame(rebuilt)
    require(fmt.rebuild_raw_msggame(reparsed), rebuilt, "candidate raw parse/rebuild")

    before_table = literal_table(fmt, archive)
    after_table = literal_table(fmt, reparsed)
    require(set(after_table), set(before_table), "candidate rebuilt literal coordinate topology")
    expected_texts = {
        f"{block}:{record}:{literal}": value
        for (block, record, literal), value in replacements.items()
    }
    for coordinate, before_literal in before_table.items():
        actual = after_table[coordinate].text
        expected = expected_texts.get(coordinate, before_literal.text)
        require(actual, expected, f"candidate rebuilt literal text {coordinate}")

    expected_changed_offsets: set[int] = set()
    record_index = {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }
    for (block_id, record_id, literal_id), replacement in replacements.items():
        coordinate = f"{block_id}:{record_id}:{literal_id}"
        literal = before_table[coordinate]
        record = record_index[(block_id, record_id)]
        start = record.relative_offset + literal.marker_offset + len(fmt.LITERAL_START)
        start += archive.blocks[block_id].offset
        before_bytes = literal.text.encode("utf-16-le")
        after_bytes = replacement.encode("utf-16-le")
        require(len(after_bytes), len(before_bytes), f"candidate raw literal width {coordinate}")
        expected_changed_offsets.update(
            start + offset
            for offset, (old, new) in enumerate(zip(before_bytes, after_bytes, strict=True))
            if old != new
        )

    actual_changed_offsets = {
        offset for offset, (old, new) in enumerate(zip(raw, rebuilt, strict=True)) if old != new
    }
    require(actual_changed_offsets, expected_changed_offsets, "candidate raw changed-byte surface")
    require(fmt.rebuild_packed_with_literals(packed, replacements), fmt.rebuild_packed_with_literals(packed, replacements), "candidate wrapper reproducibility")
    return {
        "raw_length_preserved": True,
        "raw_parse_rebuild_after_candidate": True,
        "literal_coordinate_topology_preserved": True,
        "untouched_literal_texts_preserved": True,
        "changed_raw_byte_count": len(actual_changed_offsets),
        "changed_raw_byte_offsets_sha256": sha256(
            json.dumps(sorted(actual_changed_offsets), separators=(",", ":")).encode("ascii")
        ),
        "raw_changed_byte_surface_limited_to_replaced_utf16le_code_units": True,
        "wrapper_rebuild_reproducible": True,
    }


def build_documents(steam_root: Path, pristine_root: Path) -> tuple[bytes, bytes, bytes, bytes, dict[str, Any]]:
    fmt = load_msggame_module()
    paths = {
        "pristine_pc_jp": safe_input(pristine_root, KO_RESOURCE),
        "current_pc_ko": safe_input(steam_root, KO_RESOURCE),
        "pc_sc": safe_input(steam_root, SC_RESOURCE),
        "pc_tc": safe_input(steam_root, TC_RESOURCE),
    }
    loaded = {label: load_source(fmt, path, label) for label, path in paths.items()}
    packed = {label: loaded[label][0] for label in loaded}
    raw = {label: loaded[label][1] for label in loaded}
    archive = {label: loaded[label][2].archive for label in loaded}
    input_specs = {label: loaded[label][3] for label in loaded}

    tables = {label: literal_table(fmt, archive[label]) for label in archive}
    jp_coordinates = set(tables["pristine_pc_jp"])
    ko_coordinates = set(tables["current_pc_ko"])
    require(len(jp_coordinates), EXPECTED_LITERAL_COUNT, "pristine PC JP literal count")
    require(len(ko_coordinates), EXPECTED_LITERAL_COUNT, "current PC KO literal count")
    require(ko_coordinates, jp_coordinates, "PC JP/KO literal coordinate topology")

    # The PC English resource is not present.  Do not substitute a PK English
    # table or any other language variant for it.
    steam_root_resolved = steam_root.resolve(strict=True)
    en_path = steam_root_resolved / EN_RESOURCE
    require(en_path.exists(), False, "same-resource PC EN availability")
    input_specs["pc_en"] = {
        "resource": EN_RESOURCE.as_posix(),
        "available": False,
        "reason": "Steam PC installation has no same-resource EN msggame.bin",
        "substituted_with_other_resource": False,
    }

    frozen, overlap_spec = source_free_exclusions()
    require(set(frozen).issubset(ko_coordinates), True, "frozen coordinates exist in current PC KO")

    candidates = candidate_map()
    overlap = sorted(set(candidates).intersection(frozen), key=coordinate_sort_key)
    if overlap:
        raise AuditError(f"new candidate overlaps frozen generic coordinate: {overlap}")

    candidate_rows: list[dict[str, Any]] = []
    hold_rows: list[dict[str, Any]] = []
    ledger_rows: list[dict[str, Any]] = []
    replacements: dict[tuple[int, int, int], str] = {}

    for coordinate in sorted(ko_coordinates, key=coordinate_sort_key):
        jp = tables["pristine_pc_jp"][coordinate].text
        ko = tables["current_pc_ko"][coordinate].text
        before_profile = format_profile(ko)
        candidate = candidates.get(coordinate)

        if coordinate in frozen:
            disposition = "excluded_preexisting_generic_overlay_coordinate_not_rejudged"
        elif candidate is None:
            disposition = "audited_pc_only_no_new_high_confidence_candidate"
        else:
            sc_literal = tables["pc_sc"].get(coordinate)
            tc_literal = tables["pc_tc"].get(coordinate)
            if sc_literal is None or tc_literal is None:
                raise AuditError(f"candidate has no same-coordinate Steam PC SC/TC evidence: {coordinate}")
            sc = sc_literal.text
            tc = tc_literal.text
            require(ko, candidate.current_ko, f"candidate current PC KO preimage {coordinate}")
            require(jp, candidate.source_jp, f"candidate pristine PC JP evidence {coordinate}")
            require(sc, candidate.pc_sc, f"candidate Steam PC SC evidence {coordinate}")
            require(tc, candidate.pc_tc, f"candidate Steam PC TC evidence {coordinate}")

            after_profile = format_profile(candidate.proposed_ko)
            require(after_profile, before_profile, f"candidate protected format profile {coordinate}")
            require(
                visible_line_codepoint_counts(candidate.proposed_ko),
                visible_line_codepoint_counts(ko),
                f"candidate visible per-line codepoint counts {coordinate}",
            )
            changes = changed_character_pairs(ko, candidate.proposed_ko)
            require(len(changes), 1, f"candidate changed codepoint count {coordinate}")
            changed_indexes = [
                index
                for index, (before, after) in enumerate(zip(ko, candidate.proposed_ko, strict=True))
                if before != after
            ]
            for index in changed_indexes:
                if not (is_hangul_syllable(ko[index]) and is_hangul_syllable(candidate.proposed_ko[index])):
                    raise AuditError(f"candidate is not a Hangul-to-Hangul replacement: {coordinate}")
            if LINEBREAK_RE.findall(ko) != LINEBREAK_RE.findall(candidate.proposed_ko):
                raise AuditError(f"candidate moves a manual line break: {coordinate}")

            block, record, literal = coordinate_sort_key(coordinate)
            replacements[(block, record, literal)] = candidate.proposed_ko
            candidate_rows.append(
                {
                    "schema": CANDIDATE_SCHEMA,
                    "resource": "base_msggame",
                    "coordinate": coordinate,
                    "issue_type": candidate.issue_type,
                    "confidence": "high",
                    "rationale": candidate.rationale,
                    "source_jp": jp,
                    "current_ko": ko,
                    "proposed_ko": candidate.proposed_ko,
                    "pc_reference_contexts": {"SC": sc, "TC": tc},
                    "source_hashes": {
                        "pristine_pc_jp_utf16le_sha256": text_hash(jp),
                        "current_pc_ko_utf16le_sha256": text_hash(ko),
                        "pc_sc_utf16le_sha256": text_hash(sc),
                        "pc_tc_utf16le_sha256": text_hash(tc),
                        "proposed_ko_utf16le_sha256": text_hash(candidate.proposed_ko),
                    },
                    "format_gate": {
                        "before_profile": before_profile,
                        "after_profile": after_profile,
                        "protected_profile_preserved": True,
                        "visible_line_codepoint_counts": visible_line_codepoint_counts(ko),
                        "manual_linebreak_moved": False,
                        "changed_character_pairs": changes,
                        "equal_width_proxy": "one same-line Hangul syllable replacement",
                    },
                    "scope": {
                        "pristine_pc_jp_used": True,
                        "current_pc_ko_used": True,
                        "steam_pc_sc_used": True,
                        "steam_pc_tc_used": True,
                        "same_resource_pc_en_available": False,
                        "pk_en_substituted": False,
                        "f_games_msg_pk_sc_used": False,
                        "switch_korean_translation_used": False,
                        "historic_korean_translation_used": False,
                        "generic_overlay_korean_text_read": False,
                        "steam_game_resource_written": False,
                        "generic_builder_modified": False,
                        "commit_created": False,
                    },
                }
            )
            disposition = "candidate_high_confidence"

        ledger_row: dict[str, Any] = {
            "schema": LEDGER_SCHEMA,
            "resource": "base_msggame",
            "coordinate": coordinate,
            "disposition": disposition,
            "source_free_evidence": {
                "pristine_pc_jp_utf16le_sha256": text_hash(jp),
                "current_pc_ko_utf16le_sha256": text_hash(ko),
                "current_pc_ko_format_profile_sha256": profile_hash(before_profile),
                "steam_pc_sc_present_at_same_coordinate": coordinate in tables["pc_sc"],
                "steam_pc_tc_present_at_same_coordinate": coordinate in tables["pc_tc"],
            },
        }
        if coordinate in frozen:
            ledger_row["prior_source_free_disposition"] = frozen[coordinate]
        if candidate is not None and coordinate not in frozen:
            ledger_row["issue_type"] = candidate.issue_type
        ledger_rows.append(ledger_row)

    raw_gate = raw_candidate_gate(fmt, packed["current_pc_ko"], raw["current_pc_ko"], archive["current_pc_ko"], replacements)

    candidate_blob = canonical_jsonl(candidate_rows)
    hold_blob = canonical_jsonl(hold_rows)
    ledger_blob = canonical_jsonl(ledger_rows)
    validation = {
        "schema": SCHEMA,
        "scope": {
            "translation_contexts": ["pristine_pc_jp", "current_pc_ko", "steam_pc_sc", "steam_pc_tc"],
            "same_resource_pc_en_available": False,
            "pk_en_substituted": False,
            "f_games_msg_pk_sc_used": False,
            "switch_korean_translation_used": False,
            "historic_korean_translation_used": False,
            "generic_overlay_korean_text_read": False,
            "generic_builder_read": False,
            "steam_game_resource_written": False,
            "generic_builder_modified": False,
            "commit_created": False,
        },
        "inputs": input_specs,
        "source_free_overlap_exclusions": overlap_spec,
        "selection": {
            "expected_coordinate_count": EXPECTED_LITERAL_COUNT,
            "ledger_coordinate_count": len(ledger_rows),
            "ledger_coordinate_ids_sha256": id_hash(row["coordinate"] for row in ledger_rows),
            "excluded_preexisting_generic_coordinate_count": len(frozen),
            "excluded_preexisting_generic_coordinate_ids_sha256": id_hash(frozen),
            "new_high_confidence_candidate_count": len(candidate_rows),
            "new_high_confidence_candidate_coordinates": [row["coordinate"] for row in candidate_rows],
            "new_high_confidence_candidate_coordinates_sha256": id_hash(row["coordinate"] for row in candidate_rows),
            "new_hold_count": len(hold_rows),
            "manual_linebreak_edit_candidate_count": 0,
            "semantic_completion": False,
            "semantic_completion_reason": (
                "All PC literal coordinates were inventoried and screened, but a resource-only "
                "review cannot prove complete in-game-context semantic completion."
            ),
        },
        "checks": {
            "all_24262_coordinates_accounted_for": len(ledger_rows) == EXPECTED_LITERAL_COUNT,
            "pc_jp_ko_coordinate_topology_equal": True,
            "source_file_pins": True,
            "source_free_overlap_ledger_pin": True,
            "source_free_overlap_ledger_contains_no_cjk_or_hangul_text": True,
            "existing_coordinates_excluded_without_generic_overlay_read": True,
            "candidate_source_preimages_pinned": True,
            "candidate_same_coordinate_pc_sc_tc_evidence_pinned": True,
            "candidate_format_profiles_preserved": True,
            "candidate_manual_linebreak_vectors_preserved": True,
            "candidate_visible_per_line_codepoint_counts_preserved": True,
            "candidate_hangul_replacements_equal_width": True,
            "candidate_raw_byte_surface_limited": raw_gate[
                "raw_changed_byte_surface_limited_to_replaced_utf16le_code_units"
            ],
            "candidate_raw_parse_rebuild": raw_gate["raw_parse_rebuild_after_candidate"],
            "no_new_linebreak_move_candidate": True,
            "private_candidate_only": True,
        },
        "aggregate_candidate_raw_rebuild": raw_gate,
        "outputs": {
            "private_candidates": {
                "relative_path": "tmp/translation_quality_base_msggame_pc_reaudit_v1/base_msggame_pc_reaudit_candidates.v1.jsonl",
                "size": len(candidate_blob),
                "sha256": sha256(candidate_blob),
            },
            "private_holds": {
                "relative_path": "tmp/translation_quality_base_msggame_pc_reaudit_v1/base_msggame_pc_reaudit_holds.v1.jsonl",
                "size": len(hold_blob),
                "sha256": sha256(hold_blob),
            },
            "source_free_coordinate_ledger": {
                "relative_path": "tmp/translation_quality_base_msggame_pc_reaudit_v1/base_msggame_pc_reaudit_coordinate_ledger.source_free.v1.jsonl",
                "size": len(ledger_blob),
                "sha256": sha256(ledger_blob),
            },
        },
    }
    return candidate_blob, hold_blob, ledger_blob, canonical_json(validation), validation


def output_paths(root: Path) -> tuple[Path, Path, Path]:
    return (
        root / "base_msggame_pc_reaudit_candidates.v1.jsonl",
        root / "base_msggame_pc_reaudit_holds.v1.jsonl",
        root / "base_msggame_pc_reaudit_coordinate_ledger.source_free.v1.jsonl",
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
        "excluded_preexisting_generic_coordinate_count": validation["selection"]["excluded_preexisting_generic_coordinate_count"],
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
        "all_24262_coordinates_accounted_for": "OK",
        "new_high_confidence_candidate_count": validation["selection"]["new_high_confidence_candidate_count"],
        "new_hold_count": validation["selection"]["new_hold_count"],
        "excluded_preexisting_generic_coordinate_count": validation["selection"]["excluded_preexisting_generic_coordinate_count"],
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
