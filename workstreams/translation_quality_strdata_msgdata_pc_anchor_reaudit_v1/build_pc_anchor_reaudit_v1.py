#!/usr/bin/env python3
"""PC-only exact-context anchor audit for strdata and msgdata.

This script deliberately does not decode the Korean replacement strings in
the generic quality overlay.  A byte-level JSON reader extracts only its
ASCII resource name and coordinate fields, so already-pending coordinates can
be excluded without using those replacements as a translation authority.
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
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp" / "translation_quality_strdata_msgdata_pc_anchor_reaudit_v1"
TOOLS = REPO / "tools"
STRDATA_TOOLS = REPO / "workstreams" / "strdata"

sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(STRDATA_TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE = STEAM / "KR_PATCH_BACKUP" / "file_only_transaction" / "steam-jp-1.1.7-v0.6.0" / "originals"
GENERIC_OVERLAY = REPO / "workstreams" / "translation_quality_corrections_v1" / "public" / "translation_quality_corrections.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"

KANA_OR_HAN_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]")
RUNTIME_RE = re.compile(r"\[([a-z]+\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
IME_COORDINATES = {f"1:{slot}" for slot in (1921, 1923, 1924, 1927, 1928, 1929, 1930, 1931, 1932)}
AMBIGUOUS_STRDATA_COORDINATES = {"0:93", "1:1856"}


@dataclass(frozen=True)
class ResourceSpec:
    name: str
    relative: str
    parser: str
    contexts: tuple[str, ...]


SPECS = (
    ResourceSpec("strdata", "MSG/JP/strdata.bin", "strdata", ("SC", "TC")),
    ResourceSpec("msgdata", "MSG_PK/JP/msgdata.bin", "common", ("EN", "SC", "TC")),
)


# These are only coordinate pairs.  The Korean candidate is taken at runtime
# from the current PC Korean anchor after proving the complete PC context
# signature is identical.  No Korean wording is embedded here.
MSGDATA_ANCHOR_PAIRS: tuple[tuple[str, str, str], ...] = (
    ("285", "9236", "nihonmatsu_tsu_reading"),
    ("10072", "9236", "nihonmatsu_tsu_reading"),
    ("331", "9494", "matsumoto_tsu_reading"),
    ("629", "9536", "matsuoka_tsu_reading"),
    ("631", "9501", "matsumae_tsu_reading"),
    ("9952", "9501", "matsumae_tsu_reading"),
    ("632", "9185", "matsukura_tsu_reading"),
    ("798", "9197", "tsutsui_tsu_reading"),
    ("16605", "1138", "tenzen_name_reading"),
    ("17206", "3053", "toshima_romanization"),
    ("17262", "3109", "katsurayama_romanization"),
    ("17275", "3122", "tsumagi_romanization"),
    ("17276", "3123", "kitagata_romanization"),
    ("17304", "3151", "onabara_romanization"),
    ("17306", "3153", "kokura_romanization"),
    ("17314", "3161", "seno_romanization"),
    ("17315", "3162", "hanahara_romanization"),
    ("17329", "3065", "shiwaku_romanization"),
    ("17330", "3177", "takimiya_romanization"),
    ("17332", "3179", "isawa_romanization"),
    ("17344", "3191", "kizuki_romanization"),
    ("17360", "3207", "tsuruda_romanization"),
    ("17369", "3219", "minakawa_romanization"),
    ("17375", "3246", "kokubu_romanization"),
    ("17391", "3262", "maita_romanization"),
    ("17400", "3271", "mamushizuka_romanization"),
    ("17404", "3275", "aochi_romanization"),
    ("17407", "3278", "matta_romanization"),
    ("17413", "3284", "kundani_romanization"),
    ("17420", "3291", "kusami_romanization"),
    ("17430", "3301", "tokuda_romanization"),
    ("17432", "3303", "toichi_romanization"),
    ("17434", "3305", "kuge_romanization"),
    ("10820", "9192", "yakami_romanization"),
    ("11068", "9393", "kokura_romanization"),
)


class AuditError(ValueError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def safe_under_tmp(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP.resolve(strict=False)
    if resolved == root or root not in resolved.parents:
        raise AuditError(f"output escapes private tmp root: {path}")
    return resolved


def jsonl_bytes(rows: Sequence[Mapping[str, Any]], *, source_free: bool) -> bytes:
    payload = "".join(
        json.dumps(row, ensure_ascii=source_free, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    ).encode("utf-8")
    if source_free:
        assert_source_free(payload, "source-free JSONL")
    return payload


def pretty_json_bytes(value: Mapping[str, Any], *, source_free: bool) -> bytes:
    payload = (json.dumps(value, ensure_ascii=source_free, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if source_free:
        assert_source_free(payload, "source-free JSON")
    return payload


def assert_source_free(payload: bytes, label: str) -> None:
    text = payload.decode("utf-8")
    if KANA_OR_HAN_RE.search(text) or HANGUL_RE.search(text):
        raise AuditError(f"{label} contains source or Korean text")


def coordinate_key(value: str) -> tuple[int, ...]:
    try:
        parsed = tuple(int(part) for part in value.split(":"))
    except ValueError as exc:
        raise AuditError(f"invalid coordinate: {value!r}") from exc
    if not parsed or any(part < 0 for part in parsed):
        raise AuditError(f"invalid coordinate: {value!r}")
    return parsed


class SourceFreeOverlayCoordinates:
    """Extract generic-overlay names/coordinates without decoding ``ko`` values."""

    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.payload) and self.payload[self.index] in b" \t\r\n":
            self.index += 1

    def expect(self, token: int) -> None:
        self.whitespace()
        if self.index >= len(self.payload) or self.payload[self.index] != token:
            raise AuditError("source-free overlay parser encountered an invalid JSON token")
        self.index += 1

    def skip_string(self) -> None:
        self.expect(ord('"'))
        while self.index < len(self.payload):
            value = self.payload[self.index]
            self.index += 1
            if value == ord("\\"):
                if self.index >= len(self.payload):
                    raise AuditError("unterminated JSON escape")
                self.index += 1
            elif value == ord('"'):
                return
        raise AuditError("unterminated JSON string")

    def ascii_string(self) -> str:
        self.whitespace()
        start = self.index
        self.skip_string()
        raw = self.payload[start + 1 : self.index - 1]
        if any(value >= 0x80 for value in raw) or b"\\" in raw:
            raise AuditError("non-ASCII value was requested by the source-free overlay reader")
        return raw.decode("ascii")

    def skip_scalar(self) -> None:
        self.whitespace()
        if self.index >= len(self.payload):
            raise AuditError("unexpected end of JSON")
        value = self.payload[self.index]
        if value == ord('"'):
            self.skip_string()
            return
        for literal in (b"true", b"false", b"null"):
            if self.payload.startswith(literal, self.index):
                self.index += len(literal)
                return
        if value in b"-0123456789":
            while self.index < len(self.payload) and self.payload[self.index] not in b",]} \t\r\n":
                self.index += 1
            return
        raise AuditError("invalid source-free JSON scalar")

    def skip_value(self) -> None:
        self.whitespace()
        if self.index >= len(self.payload):
            raise AuditError("unexpected end of JSON")
        value = self.payload[self.index]
        if value == ord("{"):
            self.skip_object()
        elif value == ord("["):
            self.skip_array()
        else:
            self.skip_scalar()

    def skip_object(self) -> None:
        self.expect(ord("{"))
        while True:
            self.whitespace()
            if self.index < len(self.payload) and self.payload[self.index] == ord("}"):
                self.index += 1
                return
            self.skip_string()
            self.expect(ord(":"))
            self.skip_value()
            self.whitespace()
            if self.payload[self.index] == ord(","):
                self.index += 1
            elif self.payload[self.index] == ord("}"):
                self.index += 1
                return
            else:
                raise AuditError("invalid JSON object delimiter")

    def skip_array(self) -> None:
        self.expect(ord("["))
        while True:
            self.whitespace()
            if self.index < len(self.payload) and self.payload[self.index] == ord("]"):
                self.index += 1
                return
            self.skip_value()
            self.whitespace()
            if self.payload[self.index] == ord(","):
                self.index += 1
            elif self.payload[self.index] == ord("]"):
                self.index += 1
                return
            else:
                raise AuditError("invalid JSON array delimiter")

    def entry(self) -> str:
        self.expect(ord("{"))
        coordinate: str | None = None
        while True:
            self.whitespace()
            if self.index < len(self.payload) and self.payload[self.index] == ord("}"):
                self.index += 1
                break
            key = self.ascii_string()
            self.expect(ord(":"))
            self.whitespace()
            if key == "coordinate":
                coordinate = self.ascii_string()
            else:
                self.skip_value()
            self.whitespace()
            if self.payload[self.index] == ord(","):
                self.index += 1
            elif self.payload[self.index] == ord("}"):
                self.index += 1
                break
            else:
                raise AuditError("invalid entry delimiter")
        if coordinate is None:
            raise AuditError("generic overlay entry lacks coordinate")
        return coordinate

    def entries(self) -> list[str]:
        self.expect(ord("["))
        result: list[str] = []
        while True:
            self.whitespace()
            if self.index < len(self.payload) and self.payload[self.index] == ord("]"):
                self.index += 1
                return result
            result.append(self.entry())
            self.whitespace()
            if self.payload[self.index] == ord(","):
                self.index += 1
            elif self.payload[self.index] == ord("]"):
                self.index += 1
                return result
            else:
                raise AuditError("invalid entries delimiter")

    def resource(self) -> tuple[str, list[str]]:
        self.expect(ord("{"))
        name: str | None = None
        entries: list[str] | None = None
        while True:
            self.whitespace()
            if self.index < len(self.payload) and self.payload[self.index] == ord("}"):
                self.index += 1
                break
            key = self.ascii_string()
            self.expect(ord(":"))
            self.whitespace()
            if key == "name":
                name = self.ascii_string()
            elif key == "entries":
                entries = self.entries()
            else:
                self.skip_value()
            self.whitespace()
            if self.payload[self.index] == ord(","):
                self.index += 1
            elif self.payload[self.index] == ord("}"):
                self.index += 1
                break
            else:
                raise AuditError("invalid resource delimiter")
        if name is None or entries is None:
            raise AuditError("generic overlay resource lacks source-free fields")
        return name, entries

    def resources(self) -> list[tuple[str, list[str]]]:
        self.expect(ord("["))
        result: list[tuple[str, list[str]]] = []
        while True:
            self.whitespace()
            if self.index < len(self.payload) and self.payload[self.index] == ord("]"):
                self.index += 1
                return result
            result.append(self.resource())
            self.whitespace()
            if self.payload[self.index] == ord(","):
                self.index += 1
            elif self.payload[self.index] == ord("]"):
                self.index += 1
                return result
            else:
                raise AuditError("invalid resources delimiter")

    def parse(self) -> dict[str, set[str]]:
        self.expect(ord("{"))
        resources: list[tuple[str, list[str]]] | None = None
        while True:
            self.whitespace()
            if self.index < len(self.payload) and self.payload[self.index] == ord("}"):
                self.index += 1
                break
            key = self.ascii_string()
            self.expect(ord(":"))
            self.whitespace()
            if key == "resources":
                resources = self.resources()
            else:
                self.skip_value()
            self.whitespace()
            if self.payload[self.index] == ord(","):
                self.index += 1
            elif self.payload[self.index] == ord("}"):
                self.index += 1
                break
            else:
                raise AuditError("invalid overlay root delimiter")
        self.whitespace()
        if self.index != len(self.payload) or resources is None:
            raise AuditError("generic overlay source-free structure is invalid")
        result: dict[str, set[str]] = {}
        for name, coordinates in resources:
            if name in result or len(coordinates) != len(set(coordinates)):
                raise AuditError("generic overlay source-free coordinates are invalid")
            result[name] = set(coordinates)
        return result


@dataclass(frozen=True)
class Table:
    texts: Mapping[str, str]
    packed_sha256: str
    raw_sha256: str
    packed_size: int
    raw_size: int


def load_table(path: Path, parser: str) -> Table:
    if not path.is_file():
        raise AuditError(f"missing PC table: {path}")
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    if parser == "common":
        parsed = parse_message_table(raw)
        if rebuild_message_table(parsed, parsed.texts) != raw:
            raise AuditError(f"common-table no-op rebuild differs: {path}")
        texts = {str(identifier): value for identifier, value in enumerate(parsed.texts)}
    elif parser == "strdata":
        parsed = parse_raw_strdata(raw)
        if rebuild_raw_strdata(parsed) != raw:
            raise AuditError(f"strdata no-op rebuild differs: {path}")
        texts = {f"{block}:{slot}": value for (block, slot), value in coordinate_texts(parsed).items()}
    else:
        raise AuditError(f"unsupported parser: {parser}")
    return Table(texts, sha256_bytes(packed), sha256_bytes(raw), len(packed), len(raw))


def language_relative(relative: str, language: str) -> str:
    parts = list(Path(relative).parts)
    try:
        index = parts.index("JP")
    except ValueError as exc:
        raise AuditError(f"resource path lacks JP component: {relative}") from exc
    parts[index] = language
    return Path(*parts).as_posix()


def profile(value: str) -> dict[str, Any]:
    escape_ranges = {offset for match in ESC_RE.finditer(value) for offset in range(match.start(), match.end())}
    return {
        "runtime": RUNTIME_RE.findall(value),
        "printf": PRINTF_RE.findall(value),
        "escape": ESC_RE.findall(value),
        "linebreaks": LINEBREAK_RE.findall(value),
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
        "controls": [
            f"U+{ord(character):04X}"
            for index, character in enumerate(value)
            if unicodedata.category(character) == "Cc" and character not in ("\r", "\n") and index not in escape_ranges
        ],
    }


def core(value: str) -> str:
    return value.strip()


def transplant_anchor_core(current: str, anchor: str) -> str:
    leading = current[: len(current) - len(current.lstrip())]
    trailing = current[len(current.rstrip()) :]
    anchor_core = core(anchor)
    if not anchor_core:
        raise AuditError("anchor Korean core is empty")
    return leading + anchor_core + trailing


def display_cells(value: str) -> int:
    total = 0
    for character in value:
        if character in "\r\n" or unicodedata.combining(character):
            continue
        total += 2 if unicodedata.east_asian_width(character) in {"F", "W"} else 1
    return total


def signature(tables: Mapping[str, Table], spec: ResourceSpec, coordinate: str) -> tuple[str, ...]:
    return tuple(tables[language].texts[coordinate] for language in ("jp",) + spec.contexts)


def source_free_overlay_coordinates() -> tuple[dict[str, set[str]], str]:
    if not GENERIC_OVERLAY.is_file():
        raise AuditError("generic quality overlay is absent")
    payload = GENERIC_OVERLAY.read_bytes()
    # The reader intentionally does not decode any Korean replacement string.
    extracted = SourceFreeOverlayCoordinates(payload).parse()
    return extracted, sha256_bytes(payload)


def load_tables() -> tuple[dict[str, dict[str, Table]], dict[str, set[str]], str]:
    overlay_coordinates, overlay_hash = source_free_overlay_coordinates()
    loaded: dict[str, dict[str, Table]] = {}
    for spec in SPECS:
        tables = {
            "jp": load_table(PRISTINE / spec.relative, spec.parser),
            "ko": load_table(STEAM / spec.relative, spec.parser),
        }
        for language in spec.contexts:
            tables[language] = load_table(STEAM / language_relative(spec.relative, language), spec.parser)
        coordinate_sets = {frozenset(table.texts) for table in tables.values()}
        if len(coordinate_sets) != 1:
            raise AuditError(f"PC language coordinate sets differ for {spec.name}")
        for coordinate in overlay_coordinates.get(spec.name, set()):
            if coordinate not in tables["ko"].texts:
                raise AuditError(f"generic source-free coordinate is outside {spec.name}: {coordinate}")
        loaded[spec.name] = tables
    return loaded, overlay_coordinates, overlay_hash


def current_corpus_glyphs(table: Table) -> set[str]:
    return {character for text in table.texts.values() for character in text if not character.isspace()}


def protected_profile(value: str) -> dict[str, Any]:
    result = profile(value)
    return {key: result[key] for key in ("runtime", "printf", "escape", "linebreaks", "controls")}


def candidate_rows(
    tables: Mapping[str, Mapping[str, Table]], overlay_coordinates: Mapping[str, set[str]]
) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, str]]:
    spec = next(item for item in SPECS if item.name == "msgdata")
    resource = tables["msgdata"]
    covered = overlay_coordinates.get("msgdata", set())
    glyphs = current_corpus_glyphs(resource["ko"])
    candidates: list[dict[str, Any]] = []
    target_status: dict[str, str] = {}
    anchor_status: dict[str, str] = {}
    seen_targets: set[str] = set()
    for target, anchor, reason in MSGDATA_ANCHOR_PAIRS:
        if target in seen_targets:
            raise AuditError(f"duplicate candidate target definition: msgdata:{target}")
        seen_targets.add(target)
        if target in covered or anchor in covered:
            target_status[target] = "excluded_existing_generic_coordinate_source_free"
            continue
        if target not in resource["ko"].texts or anchor not in resource["ko"].texts:
            raise AuditError(f"candidate coordinate is absent: {target}/{anchor}")
        if signature(resource, spec, target) != signature(resource, spec, anchor):
            raise AuditError(f"PC context signature differs at msgdata:{target}/{anchor}")
        current = resource["ko"].texts[target]
        anchor_current = resource["ko"].texts[anchor]
        proposed = transplant_anchor_core(current, anchor_current)
        if profile(current) != profile(proposed) or protected_profile(resource["jp"].texts[target]) != protected_profile(proposed):
            raise AuditError(f"format profile differs at msgdata:{target}")
        if proposed == current or KANA_OR_HAN_RE.search(proposed) or not HANGUL_RE.search(proposed):
            raise AuditError(f"unsafe/effectless Korean anchor candidate at msgdata:{target}")
        if display_cells(proposed) > display_cells(current):
            target_status[target] = "hold_candidate_exceeds_current_cell_width"
            continue
        if any(character not in glyphs for character in proposed if not character.isspace()):
            raise AuditError(f"candidate needs a glyph outside current PC Korean corpus: msgdata:{target}")
        contexts = {language: resource[language].texts[target] for language in spec.contexts}
        candidates.append(
            {
                "schema": "nobu16.kr.pc-anchor-reaudit-candidate.v1",
                "resource": "msgdata",
                "coordinate": target,
                "id": int(target),
                "anchor_coordinate": anchor,
                "issue_type": "pc_exact_context_name_reading_inconsistency",
                "reason_code": reason,
                "source_jp": resource["jp"].texts[target],
                "current_korean": current,
                "proposed_korean": proposed,
                "anchor_current_korean": anchor_current,
                "source_jp_utf16le_sha256": sha256_text(resource["jp"].texts[target]),
                "current_text_utf16le_sha256": sha256_text(current),
                "proposed_text_utf16le_sha256": sha256_text(proposed),
                "anchor_current_utf16le_sha256": sha256_text(anchor_current),
                "reference_contexts": contexts,
                "reference_context_utf16le_sha256": {language: sha256_text(value) for language, value in contexts.items()},
                "source_format_profile": profile(resource["jp"].texts[target]),
                "current_format_profile": profile(current),
                "format_validation": {
                    "source_current_proposed_profiles_match": True,
                    "outer_whitespace_preserved_from_current": True,
                    "runtime_printf_esc_linebreak_control_contract_preserved": True,
                },
                "layout_validation": {
                    "current_display_cells": display_cells(current),
                    "proposed_display_cells": display_cells(proposed),
                    "proposed_does_not_exceed_current_cell_count": True,
                    "glyphs_already_present_in_current_pc_korean_corpus": True,
                    "runtime_render_claim": "not_made",
                },
                "audit_scope": {
                    "pristine_pc_japanese": True,
                    "current_pc_korean_target_only": True,
                    "pc_en_sc_tc_context": True,
                    "switch_korean_read": False,
                    "historic_korean_read": False,
                    "generic_korean_replacement_decoded": False,
                    "steam_game_resource_written": False,
                },
            }
        )
        target_status[target] = "candidate_high_confidence"
        anchor_status[anchor] = "reference_anchor_for_candidate"
    candidates.sort(key=lambda row: coordinate_key(row["coordinate"]))
    return candidates, target_status, anchor_status


def static_flags(value: str) -> list[str]:
    flags: list[str] = []
    if KANA_OR_HAN_RE.search(value):
        flags.append("kana_or_han_residual")
    return flags


def signature_groups(spec: ResourceSpec, tables: Mapping[str, Table], covered: set[str]) -> dict[tuple[str, ...], list[str]]:
    grouped: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for coordinate in tables["jp"].texts:
        if coordinate not in covered and tables["jp"].texts[coordinate].strip():
            grouped[signature(tables, spec, coordinate)].append(coordinate)
    return grouped


def normalized_core(value: str) -> str:
    return re.sub(r"[\s·・,，.。!?！？()（）\[\]「」『』“”\"'\-—/]+", "", core(value))


def hold_rows(
    tables: Mapping[str, Mapping[str, Table]],
    overlay_coordinates: Mapping[str, set[str]],
    candidate_status: Mapping[str, str],
    anchor_status: Mapping[str, str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in SPECS:
        resource = tables[spec.name]
        covered = overlay_coordinates.get(spec.name, set())
        groups = signature_groups(spec, resource, covered)
        by_coordinate: dict[str, tuple[int, int]] = {}
        for coordinates in groups.values():
            variants = {normalized_core(resource["ko"].texts[coordinate]) for coordinate in coordinates}
            for coordinate in coordinates:
                by_coordinate[coordinate] = (len(coordinates), len(variants))
        for coordinate in sorted(resource["ko"].texts, key=coordinate_key):
            if coordinate in covered:
                continue
            reasons: list[str] = []
            value = resource["ko"].texts[coordinate]
            if static_flags(value):
                if spec.name == "strdata" and coordinate in IME_COORDINATES:
                    reasons.append("ime_or_input_runtime_component")
                elif spec.name == "strdata" and coordinate.startswith("4:"):
                    reasons.append("credits_or_proper_names_preserved_without_auto_translation")
                else:
                    reasons.append("residual_script_requires_context_or_name_policy")
            if spec.name == "strdata" and coordinate in AMBIGUOUS_STRDATA_COORDINATES:
                reasons.append("same_jp_has_multiple_korean_terms_but_no_pc_en_reading_authority")
            group_size, variants = by_coordinate.get(coordinate, (0, 0))
            if variants > 1 and candidate_status.get(coordinate) != "candidate_high_confidence" and coordinate not in anchor_status:
                reasons.append("same_full_pc_signature_has_multiple_korean_renderings")
            if not reasons:
                continue
            contexts = {language: resource[language].texts[coordinate] for language in spec.contexts}
            rows.append(
                {
                    "schema": "nobu16.kr.pc-anchor-reaudit-hold.v1",
                    "resource": spec.name,
                    "coordinate": coordinate,
                    "source_jp": resource["jp"].texts[coordinate],
                    "current_korean": value,
                    "source_jp_utf16le_sha256": sha256_text(resource["jp"].texts[coordinate]),
                    "current_text_utf16le_sha256": sha256_text(value),
                    "reference_contexts": contexts,
                    "reference_context_utf16le_sha256": {language: sha256_text(text) for language, text in contexts.items()},
                    "same_full_pc_signature_coordinate_count": group_size,
                    "same_full_pc_signature_korean_variant_count": variants,
                    "hold_reasons": sorted(set(reasons)),
                    "audit_scope": {
                        "pristine_pc_japanese": True,
                        "current_pc_korean_target_only": True,
                        "pc_en_sc_tc_context": True,
                        "switch_korean_read": False,
                        "historic_korean_read": False,
                        "generic_korean_replacement_decoded": False,
                        "steam_game_resource_written": False,
                    },
                }
            )
    rows.sort(key=lambda row: (row["resource"], coordinate_key(row["coordinate"])))
    return rows


def full_scan_rows(
    tables: Mapping[str, Mapping[str, Table]],
    overlay_coordinates: Mapping[str, set[str]],
    candidate_status: Mapping[str, str],
    anchor_status: Mapping[str, str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in SPECS:
        resource = tables[spec.name]
        covered = overlay_coordinates.get(spec.name, set())
        groups = signature_groups(spec, resource, covered)
        group_data: dict[str, tuple[int, int]] = {}
        for coordinates in groups.values():
            variants = {normalized_core(resource["ko"].texts[coordinate]) for coordinate in coordinates}
            for coordinate in coordinates:
                group_data[coordinate] = (len(coordinates), len(variants))
        for coordinate in sorted(resource["ko"].texts, key=coordinate_key):
            source = resource["jp"].texts[coordinate]
            current = resource["ko"].texts[coordinate]
            group_size, variants = group_data.get(coordinate, (0, 0))
            covered_now = coordinate in covered
            if covered_now:
                disposition = "excluded_existing_generic_coordinate_source_free"
            elif candidate_status.get(coordinate) == "candidate_high_confidence":
                disposition = "new_high_confidence_anchor_candidate"
            elif candidate_status.get(coordinate, "").startswith("hold_"):
                disposition = candidate_status[coordinate]
            elif coordinate in anchor_status:
                disposition = "reference_anchor_retained"
            elif static_flags(current):
                disposition = "pc_only_hold_residual_or_runtime_component"
            elif variants > 1:
                disposition = "pc_only_hold_same_signature_korean_divergence"
            else:
                disposition = "pc_pair_screened_no_new_exact_anchor_signal"
            rows.append(
                {
                    "schema": "nobu16.kr.pc-anchor-reaudit-source-free-coordinate.v1",
                    "resource": spec.name,
                    "relative_path": spec.relative,
                    "coordinate": coordinate,
                    "disposition": disposition,
                    "existing_generic_coordinate_source_free": covered_now,
                    "source_jp_utf16le_sha256": sha256_text(source),
                    "current_ko_utf16le_sha256": sha256_text(current),
                    "context_utf16le_sha256": {language: sha256_text(resource[language].texts[coordinate]) for language in spec.contexts},
                    "static_flags": static_flags(current),
                    "same_full_pc_signature_coordinate_count": group_size,
                    "same_full_pc_signature_korean_variant_count": variants,
                    "switch_korean_translation_used": False,
                    "historic_korean_translation_used": False,
                    "generic_korean_replacement_decoded": False,
                    "steam_game_resource_written": False,
                    "semantic_completion": False,
                }
            )
    return rows


def build_state() -> tuple[dict[str, Any], dict[str, bytes]]:
    tables, overlay_coordinates, overlay_hash = load_tables()
    candidates, target_status, anchor_status = candidate_rows(tables, overlay_coordinates)
    holds = hold_rows(tables, overlay_coordinates, target_status, anchor_status)
    scan = full_scan_rows(tables, overlay_coordinates, target_status, anchor_status)
    expected_count = sum(len(resource["ko"].texts) for resource in tables.values())
    if len(scan) != expected_count:
        raise AuditError("full scan cardinality differs")
    candidate_coordinates = {(row["resource"], row["coordinate"]) for row in candidates}
    if len(candidate_coordinates) != len(candidates):
        raise AuditError("candidate coordinates are not unique")
    if any((row["resource"], row["coordinate"]) in candidate_coordinates for row in holds):
        raise AuditError("candidate and hold partitions overlap")
    scan_counts = Counter(row["disposition"] for row in scan)
    summary = {
        "schema": "nobu16.kr.pc-anchor-reaudit-summary.v1",
        "scope": "PC-only strdata/msgdata exact-context anchor re-audit",
        "coordinate_count": len(scan),
        "candidate_count": len(candidates),
        "hold_count": len(holds),
        "scan_disposition_counts": dict(sorted(scan_counts.items())),
        "resources": {
            spec.name: {
                "coordinate_count": len(tables[spec.name]["ko"].texts),
                "existing_generic_coordinate_source_free_count": len(overlay_coordinates.get(spec.name, set())),
                "pristine_pc_jp": {
                    "packed_sha256": tables[spec.name]["jp"].packed_sha256,
                    "raw_sha256": tables[spec.name]["jp"].raw_sha256,
                    "coordinate_count": len(tables[spec.name]["jp"].texts),
                },
                "current_pc_korean": {
                    "packed_sha256": tables[spec.name]["ko"].packed_sha256,
                    "raw_sha256": tables[spec.name]["ko"].raw_sha256,
                    "coordinate_count": len(tables[spec.name]["ko"].texts),
                },
                "pc_contexts": {
                    language: {
                        "packed_sha256": tables[spec.name][language].packed_sha256,
                        "raw_sha256": tables[spec.name][language].raw_sha256,
                    }
                    for language in spec.contexts
                },
            }
            for spec in SPECS
        },
        "generic_overlay_source_free_coordinate_extraction": {
            "overlay_sha256": overlay_hash,
            "korean_replacement_strings_decoded": False,
            "coordinate_counts": {name: len(coords) for name, coords in sorted(overlay_coordinates.items())},
        },
        "translation_completion_claim": "not_made: full coordinate screening and exact-anchor checks are not a blanket semantic-completion claim",
        "switch_korean_translation_used": False,
        "historic_korean_translation_used": False,
        "steam_game_resource_written": False,
        "generic_overlay_written": False,
    }
    artifacts = {
        "source_free_full_scan.v1.jsonl": jsonl_bytes(scan, source_free=True),
        "private_candidates.v1.jsonl": jsonl_bytes(candidates, source_free=False),
        "private_holds.v1.jsonl": jsonl_bytes(holds, source_free=False),
        "summary.source_free.v1.json": pretty_json_bytes(summary, source_free=True),
    }
    validation = {
        "schema": "nobu16.kr.pc-anchor-reaudit-validation.v1",
        "source_free": True,
        "coordinate_count": len(scan),
        "candidate_count": len(candidates),
        "hold_count": len(holds),
        "artifacts": {name: sha256_bytes(blob) for name, blob in sorted(artifacts.items())},
        "generic_overlay_source_free_coordinate_extraction": summary["generic_overlay_source_free_coordinate_extraction"],
        "checks": {
            "all_pc_tables_noop_parse_rebuild": "OK",
            "pc_language_coordinate_sets": "OK",
            "candidate_anchor_full_pc_context_signature": "OK",
            "candidate_runtime_outer_whitespace_contract": "OK",
            "candidate_display_cells_do_not_expand": "OK",
            "candidate_glyphs_in_current_pc_korean_corpus": "OK",
            "generic_korean_replacement_strings_decoded": False,
            "switch_korean_translation_used": False,
            "historic_korean_translation_used": False,
            "steam_game_resource_written": False,
        },
        "semantic_completion": False,
    }
    validation_blob = pretty_json_bytes(validation, source_free=True)
    artifacts["validation.v1.json"] = validation_blob
    return summary, artifacts


def write_artifacts(artifacts: Mapping[str, bytes]) -> None:
    for name in ("source_free_full_scan.v1.jsonl", "private_candidates.v1.jsonl", "private_holds.v1.jsonl", "summary.source_free.v1.json"):
        target = safe_under_tmp(TMP / name)
        atomic_write(target, artifacts[name])
    atomic_write(VALIDATION, artifacts["validation.v1.json"])


def validate_artifacts(artifacts: Mapping[str, bytes]) -> None:
    paths = {
        "source_free_full_scan.v1.jsonl": TMP / "source_free_full_scan.v1.jsonl",
        "private_candidates.v1.jsonl": TMP / "private_candidates.v1.jsonl",
        "private_holds.v1.jsonl": TMP / "private_holds.v1.jsonl",
        "summary.source_free.v1.json": TMP / "summary.source_free.v1.json",
        "validation.v1.json": VALIDATION,
    }
    for name, path in paths.items():
        if not path.is_file() or path.read_bytes() != artifacts[name]:
            raise AuditError(f"deterministic artifact differs or is absent: {path}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="build and write private/source-free audit artifacts")
    mode.add_argument("--validate", action="store_true", help="recompute and require byte-identical artifacts")
    args = parser.parse_args(argv)
    try:
        summary, artifacts = build_state()
        if args.write:
            write_artifacts(artifacts)
        else:
            validate_artifacts(artifacts)
    except (AuditError, OSError, KeyError, ValueError, IndexError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"candidate_count": summary["candidate_count"], "hold_count": summary["hold_count"], "coordinate_count": summary["coordinate_count"], "steam_installation_written": False}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
