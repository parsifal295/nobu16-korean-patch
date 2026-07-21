#!/usr/bin/env python3
"""Build a source-free Korean-Hanja-reading overlay for JP name reading fields.

The game's Japanese ``msgdata`` and shared ``strdata`` resources carry name
display fields and separate furigana fields.  Korean display names intentionally
remain Korean-Japanese names, while the furigana fields are rebuilt from the
original displayed Hanja using Korean Hanja readings.  Thus ``織田`` / ``信長``
become ``직전`` / ``신장`` and render together without a space.

The build is deliberately two-stage:

* private inputs are the locally backed-up original JP resources, Unicode
  Unihan reading data, and the pinned ``hanja`` table;
* the tracked output contains only numeric field IDs, source hashes, and
  Hangul replacements.  It contains no original game text or game resource.

The installed Steam tree is read only.  Candidate resources are written only
below the requested output directory and are verified by parse/rebuild and
source-hash gates before being emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
STRDATA_TOOLS = REPO / "workstreams" / "switch_msgbre_v11"
for _path in (TOOLS, STRDATA_TOOLS):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import (  # noqa: E402
    MessageTable,
    parse_message_table,
    rebuild_message_table,
)
from strdata_container import parse_strdata, rebuild_strdata  # noqa: E402


SCHEMA = "nobu16.kr.hanja-furigana.v1"
VALIDATION_SCHEMA = "nobu16.kr.hanja-furigana-validation.v1"
SOURCE_FREE_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uf900-\ufaff]")
HANGUL_RE = re.compile(r"^[\uac00-\ud7a3]+$")
TABLE_LINE_RE = re.compile(r'^"(?P<key>.*?)": "(?P<value>.*?)"$')

UNICODE_UNIHAN_READINGS_SHA256 = (
    "575E69C9AD85A4737A889A4F94CBD987042A90A1A6CC16DD3F4ED995C715B17C"
)
HANJA_WHEEL_SHA256 = (
    "66981F7DEDF7AD298661D7D58F2702EA84304617FBE52478A42833F9819D75BE"
)
HANJA_WHEEL_MEMBER = "hanja/table.yml"

DEFAULT_UNIHAN_READINGS = REPO / "tmp" / "Unihan-17.0.0" / "Unihan_Readings.txt"
DEFAULT_HANJA_WHEEL = REPO / "tmp" / "hanja-0.15.1-py3-none-any.whl"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_ORIGINAL_ROOT = (
    Path(r"F:\Games\NOBU16\KR_PATCH_BACKUP")
    / "file_only_transaction"
    / "jp-runtime-wave05-20260715-v1"
    / "originals"
)

PK_RESOURCE = "MSG_PK/JP/msgdata.bin"
BASE_RESOURCE = "MSG/JP/strdata.bin"

# These three contiguous groups are the complete name/ruby dictionaries.  The
# next group begins at 9151 and is a distinct castle/province/clan/title UI
# table, so it is deliberately out of scope.
PK_GROUPS: tuple[tuple[str, int, int, int], ...] = (
    ("primary", 0, 3332, 3332),
    ("fictional_princess", 6664, 6764, 100),
    ("secondary_name_dictionary", 6864, 8001, 1137),
)
BASE_GROUP_COUNTS = {
    "primary": 3_319,
    "fictional_princess": 100,
    "secondary_name_dictionary": 1_137,
}
EXPECTED_PK_READING_COUNT = 4_569
EXPECTED_BASE_READING_COUNT = 4_556
PK_READING_IDS_SHA256 = "924201D83B0F3190F1892EE21C4CF8C669A68AA8AFB3EE3F557118C7E2A94E70"
BASE_READING_IDS_SHA256 = "A9D650DB59A7FC91E485D3801FC998D6CAF5BCC6358AC806ED908418FE3460F3"

# Original JP has four font/encoding substitutions in the primary display
# table.  Their SC aligned source identifies the intended Han characters; the
# replacement is the Korean Hanja reading, not a Japanese kana transcription.
SPECIAL_PRIMARY_REPLACEMENTS = {
    2046: "은천대",
    2086: "차",
    2089: "미",
    2090: "송",
}

# Unihan kHangul is authoritative where present.  This one canonical override
# corrects the generic table with the Unicode value.
UNICODE_READING_OVERRIDES = {
    0x59EB: "희",  # 姫: Unicode kHangul, not the generic table's 진.
}

# These selected dictionary entries use a documented alternate Korean reading
# because the Japanese glyph is a shinjitai / target-name usage, not the
# unrelated base-codepoint sense.
TARGET_USAGE_READING_OVERRIDES = {
    0x82B8: "예",  # 芸: Japanese shinjitai of 藝 (安芸, 頼芸).
    0x8336: "차",  # 茶: tea/name usage, never the unrelated 다 reading here.
    0x8A3C: "증",  # 証: Japanese shinjitai of 證 (願証寺, 証恵, ...).
}

# 証 itself is only recorded under its base-codepoint Korean reading in
# Unihan.  Its Japanese form is explicitly the shinjitai of 證, whose Unicode
# kHangul record supplies 증; this is checked during build coverage.
TARGET_USAGE_UNIHAN_VARIANTS = {0x8A3C: 0x8B49}

# The selected source uses 79 Japanese shinjitai, variant, and uncommon
# characters that have no Unicode kHangul record.  These values are a reviewed
# target-specific Korean-Hanja map, pinned by code point rather than delegated
# to a generic third-party fallback at apply time.  U+6E13 is particularly
# important: the generic hanja table calls it 부, while the Korean reading of
# the Japanese variant of 溪 is 계 (瑞渓 -> 서계).
MISSING_KHANGUL_READINGS = {
    0x4E0E: "여",
    0x4E57: "승",
    0x4E80: "구",
    0x4F1D: "전",
    0x5185: "내",
    0x51A8: "부",
    0x53C2: "참",
    0x56E3: "단",
    0x5700: "국",
    0x57AA: "병",
    0x5897: "증",
    0x5965: "오",
    0x5B8D: "육",
    0x5BDD: "침",
    0x5C1A: "상",
    0x5C2D: "요",
    0x5DCC: "암",
    0x5DFB: "권",
    0x5E30: "귀",
    0x5F10: "이",
    0x5F53: "당",
    0x5F93: "종",
    0x5FDC: "응",
    0x6238: "호",
    0x62DD: "배",
    0x6319: "거",
    0x6442: "섭",
    0x6570: "수",
    0x658E: "재",
    0x66A6: "력",
    0x6761: "조",
    0x685C: "앵",
    0x691B: "화",
    # Japanese 楽 is the shinjitai of 樂.  The selected name dictionary uses
    # its Korean name reading (락; word-initially 낙), not the unrelated 악.
    0x697D: "락",
    0x698A: "신",
    0x69D9: "전",
    0x6A2A: "횡",
    0x6B73: "세",
    0x6CA2: "택",
    0x6D44: "정",
    0x6D45: "천",
    0x6E0B: "삽",
    0x6E13: "계",
    0x6E29: "온",
    0x6E80: "만",
    0x6EDD: "롱",
    0x702C: "뢰",
    0x70BA: "위",
    0x72EC: "독",
    0x767A: "발",
    0x7985: "선",
    0x7A32: "도",
    0x7C17: "량",
    0x7D4C: "경",
    0x7D99: "계",
    0x7D9A: "속",
    0x7DD1: "록",
    0x8358: "장",
    0x8535: "장",
    0x85AC: "약",
    0x86CD: "형",
    0x86EE: "만",
    0x899A: "각",
    0x8A89: "예",
    0x8EFD: "경",
    0x8FBA: "변",
    0x9065: "요",
    0x90F7: "향",
    0x93AE: "진",
    0x9453: "견",
    0x95A2: "관",
    0x9688: "외",
    0x96A0: "은",
    0x96D1: "잡",
    0x96EB: "놔",
    0x9834: "영",
    0x9D5C: "제",
    0x9EC4: "황",
    0x9ED2: "흑",
}


class FuriganaError(RuntimeError):
    """Raised when an input, mapping, or generated artifact is unsafe."""


@dataclass(frozen=True)
class Operation:
    entry_id: int
    replacement: str
    source_hash: str
    display_hash: str
    group: str


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256_bytes(text.encode("utf-16le"))


def compact_int_list_hash(values: Sequence[int]) -> str:
    encoded = json.dumps(list(values), separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def atomic_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def write_json(path: Path, value: Any) -> None:
    atomic_write(path, canonical_json(value))


def safe_resource_path(root: Path, relative: str) -> Path:
    root = root.resolve(strict=True)
    target = (root / Path(relative)).resolve(strict=True)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise FuriganaError(f"resource escapes input root: {relative}") from exc
    if not target.is_file():
        raise FuriganaError(f"resource is absent: {target}")
    return target


def load_hanja_table(wheel_path: Path) -> dict[str, str]:
    wheel_path = wheel_path.resolve(strict=True)
    if sha256_file(wheel_path) != HANJA_WHEEL_SHA256:
        raise FuriganaError("hanja wheel SHA-256 differs from the pinned 0.15.1 input")
    try:
        with zipfile.ZipFile(wheel_path, "r") as archive:
            payload = archive.read(HANJA_WHEEL_MEMBER).decode("utf-8")
    except (KeyError, UnicodeDecodeError, zipfile.BadZipFile) as exc:
        raise FuriganaError("cannot read the pinned hanja table from its wheel") from exc

    result: dict[str, str] = {}
    for number, line in enumerate(payload.splitlines(), 1):
        match = TABLE_LINE_RE.fullmatch(line)
        if match is None:
            raise FuriganaError(f"unexpected hanja table line {number}")
        try:
            key = json.loads(f'"{match.group("key")}"')
            value = json.loads(f'"{match.group("value")}"')
        except json.JSONDecodeError as exc:
            raise FuriganaError(f"invalid escaped hanja table line {number}") from exc
        if len(key) != 1 or not HANGUL_RE.fullmatch(value):
            raise FuriganaError(f"invalid hanja table entry at line {number}")
        if key in result:
            raise FuriganaError(f"duplicate hanja table key at line {number}")
        result[key] = value
    if len(result) != 27_497:
        raise FuriganaError(f"hanja table count differs: {len(result)}")
    return result


def load_unihan_khangul(readings_path: Path) -> dict[str, tuple[str, ...]]:
    readings_path = readings_path.resolve(strict=True)
    if sha256_file(readings_path) != UNICODE_UNIHAN_READINGS_SHA256:
        raise FuriganaError("Unihan_Readings.txt SHA-256 differs from the pinned Unicode 17 input")
    result: dict[str, tuple[str, ...]] = {}
    for line in readings_path.read_text(encoding="utf-8").splitlines():
        if "\tkHangul\t" not in line:
            continue
        code, field, value = line.split("\t")
        if field != "kHangul" or not code.startswith("U+"):
            raise FuriganaError("invalid kHangul row")
        readings = tuple(token.split(":", 1)[0] for token in value.split())
        if not readings or any(not HANGUL_RE.fullmatch(item) for item in readings):
            raise FuriganaError(f"invalid kHangul value for {code}")
        character = chr(int(code[2:], 16))
        if character in result:
            raise FuriganaError(f"duplicate kHangul character {code}")
        result[character] = readings
    if len(result) < 8_000:
        raise FuriganaError("Unihan kHangul map is unexpectedly small")
    return result


def load_kana_converter() -> Any:
    """Load the existing, tested kana -> Hangul converter without copying it."""
    path = TOOLS / "generate_officer_name_catalog.py"
    spec = importlib.util.spec_from_file_location("hanja_furigana_kana", path)
    if spec is None or spec.loader is None:
        raise FuriganaError("cannot load existing kana converter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    converter = getattr(module, "kana_to_hangul", None)
    if not callable(converter):
        raise FuriganaError("existing kana converter is unavailable")
    return converter


def is_hangul(value: str) -> bool:
    return len(value) == 1 and 0xAC00 <= ord(value) <= 0xD7A3


def hangul_parts(value: str) -> tuple[int, int, int]:
    if not is_hangul(value):
        raise FuriganaError(f"expected a Hangul syllable, got {value!r}")
    offset = ord(value) - 0xAC00
    return (offset // 588, (offset // 28) % 21, offset % 28)


def build_hangul(initial: int, medial: int, final: int) -> str:
    if not (0 <= initial < 19 and 0 <= medial < 21 and 0 <= final < 28):
        raise FuriganaError("invalid Hangul components")
    return chr(0xAC00 + ((initial * 21 + medial) * 28 + final))


def apply_initial_sound_rule(previous: str, current: str) -> str:
    """Apply Korean initial-sound law to one Hanja reading syllable."""
    p_initial, p_medial, p_final = hangul_parts(previous) if is_hangul(previous) else (0, 0, 0)
    c_initial, c_medial, c_final = hangul_parts(current)
    current_head = build_hangul(c_initial, c_medial, 0)
    offset = 0
    if previous.isalnum():
        if current in ("렬", "률") and is_hangul(previous) and p_final in (0, 2):
            offset = 6
    elif current_head in ("녀", "뇨", "뉴", "니"):
        offset = 9
    elif current_head in ("랴", "려", "례", "료", "류", "리"):
        offset = 6
    elif current_head in ("라", "래", "로", "뢰", "루", "르"):
        offset = -3
    return build_hangul(c_initial + offset, c_medial, c_final)


def require_hanja_inputs_covered(
    displays: Iterable[str],
    table: Mapping[str, str],
    khangul: Mapping[str, tuple[str, ...]],
) -> dict[str, int]:
    source_hanja = sorted(
        {
            character
            for display in displays
            for character in display
            if is_han_codepoint(character)
        }
    )
    missing_table = sorted(character for character in source_hanja if character not in table)
    if missing_table:
        values = ", ".join(f"U+{ord(value):04X}" for value in missing_table)
        raise FuriganaError(f"hanja table does not cover source characters: {values}")

    direct_characters = {character for character in source_hanja if character in khangul}
    missing_characters = set(source_hanja) - direct_characters
    missing_codepoints = {ord(character) for character in missing_characters}
    pinned_codepoints = set(MISSING_KHANGUL_READINGS)
    if missing_codepoints != pinned_codepoints:
        absent = sorted(pinned_codepoints - missing_codepoints)
        unpinned = sorted(missing_codepoints - pinned_codepoints)
        details: list[str] = []
        if absent:
            details.append("unused pinned=" + ",".join(f"U+{value:04X}" for value in absent))
        if unpinned:
            details.append("unmapped source=" + ",".join(f"U+{value:04X}" for value in unpinned))
        raise FuriganaError("pinned kHangul-missing map does not exactly match source: " + "; ".join(details))
    for codepoint, reading in MISSING_KHANGUL_READINGS.items():
        if not HANGUL_RE.fullmatch(reading):
            raise FuriganaError(f"invalid pinned missing kHangul reading U+{codepoint:04X}")

    official_override = 0
    target_usage_override = 0
    target_usage_variant_override = 0
    if not set(TARGET_USAGE_UNIHAN_VARIANTS) <= set(TARGET_USAGE_READING_OVERRIDES):
        raise FuriganaError("target usage Unicode-variant map has an unselected code point")
    for character in sorted(direct_characters):
        selected = select_hanja_reading(character, table)
        codepoint = ord(character)
        if codepoint in UNICODE_READING_OVERRIDES:
            official_override += 1
        if codepoint in TARGET_USAGE_READING_OVERRIDES:
            target_usage_override += 1
            variant = TARGET_USAGE_UNIHAN_VARIANTS.get(codepoint)
            if variant is not None:
                target_usage_variant_override += 1
                if selected not in khangul.get(chr(variant), ()):
                    raise FuriganaError(
                        f"selected target usage reading does not match Unicode variant "
                        f"for U+{codepoint:04X}"
                    )
            elif selected not in khangul[character]:
                raise FuriganaError(
                    f"selected target usage reading does not match Unicode kHangul "
                    f"for U+{codepoint:04X}"
                )
        elif selected not in khangul[character]:
            raise FuriganaError(
                f"selected reading does not match Unicode kHangul for U+{codepoint:04X}"
            )
    return {
        "source_hanja_unique": len(source_hanja),
        "unicode_khangul_direct_unique": len(direct_characters),
        "unicode_khangul_missing_unique": len(missing_characters),
        "pinned_missing_khangul_unique": len(pinned_codepoints),
        "unicode_override_unique": official_override,
        "target_usage_override_unique": target_usage_override,
        "target_usage_variant_override_unique": target_usage_variant_override,
    }


def is_han_codepoint(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0x20000 <= codepoint <= 0x323AF
    )


def select_hanja_reading(character: str, table: Mapping[str, str]) -> str:
    """Choose the reviewed Korean reading for a source Hanja character.

    ``require_hanja_inputs_covered`` proves every selected character is either
    Unicode ``kHangul``-covered or an exact member of the reviewed missing-map.
    Keep this selector free of generic fallbacks so a newly encountered variant
    cannot silently inherit a possibly wrong third-party table value.
    """
    codepoint = ord(character)
    if codepoint in TARGET_USAGE_READING_OVERRIDES:
        return TARGET_USAGE_READING_OVERRIDES[codepoint]
    if codepoint in UNICODE_READING_OVERRIDES:
        return UNICODE_READING_OVERRIDES[codepoint]
    if codepoint in MISSING_KHANGUL_READINGS:
        return MISSING_KHANGUL_READINGS[codepoint]
    try:
        return table[character]
    except KeyError as exc:
        raise FuriganaError(f"no Korean Hanja reading for U+{codepoint:04X}") from exc


def convert_display(
    display: str,
    original_reading: str,
    entry_id: int,
    table: Mapping[str, str],
    kana_to_hangul: Any,
) -> tuple[str, str]:
    """Return a no-space Korean reading and a deterministic conversion class."""
    if entry_id in SPECIAL_PRIMARY_REPLACEMENTS:
        return SPECIAL_PRIMARY_REPLACEMENTS[entry_id], "encoded_display_override"
    if not display or not original_reading:
        raise FuriganaError(f"source name/reading is empty at display id {entry_id}")

    if not any(character in table for character in display):
        try:
            converted = kana_to_hangul(original_reading)
        except Exception as exc:  # Existing converter raises its own typed error.
            raise FuriganaError(f"cannot transliterate kana-only field {entry_id}") from exc
        return converted, "kana_only_fallback"

    small_ke = chr(0x30F6)
    hiragana_ga = chr(0x304C)
    iteration_mark = chr(0x3005)
    output: list[str] = []
    literal: list[str] = []
    previous_hanja_reading = ""
    continuing_hanja = False

    def flush_literal() -> None:
        nonlocal literal, continuing_hanja, previous_hanja_reading
        if not literal:
            return
        text = "".join(literal).replace(small_ke, hiragana_ga)
        try:
            converted = kana_to_hangul(text)
        except Exception as exc:
            raise FuriganaError(f"cannot transliterate literal segment at display id {entry_id}") from exc
        output.append(converted)
        literal = []
        continuing_hanja = False
        previous_hanja_reading = ""

    for character in display:
        if character in table:
            flush_literal()
            reading = select_hanja_reading(character, table)
            prior = previous_hanja_reading if continuing_hanja else " "
            converted = apply_initial_sound_rule(prior, reading)
            output.append(converted)
            previous_hanja_reading = converted
            continuing_hanja = True
            continue
        if character == iteration_mark:
            flush_literal()
            if not continuing_hanja or not previous_hanja_reading:
                raise FuriganaError(f"unbound iteration mark at display id {entry_id}")
            output.append(previous_hanja_reading)
            continue
        literal.append(character)
    flush_literal()
    converted = "".join(output)
    if not converted:
        raise FuriganaError(f"conversion produced an empty reading at display id {entry_id}")
    return converted, "hanja_or_mixed"


def parse_common(path: Path) -> tuple[bytes, bytes, MessageTable]:
    packed = path.read_bytes()
    _, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise FuriganaError(f"common message parse/rebuild differs: {path}")
    return packed, raw, table


def parse_base(path: Path) -> tuple[bytes, bytes, Any]:
    packed = path.read_bytes()
    _, raw = decompress_wrapper(packed)
    container = parse_strdata(raw)
    if rebuild_strdata(container) != raw:
        raise FuriganaError(f"strdata parse/rebuild differs: {path}")
    return packed, raw, container


def assert_original_name_dictionaries_aligned(original_pk: MessageTable, original_base: Any) -> None:
    """Prove the selected Base dictionaries are the same JP source as PK."""
    base_block = original_base.blocks[0]
    for group, display_start, reading_start, pk_count in PK_GROUPS:
        base_count = BASE_GROUP_COUNTS[group]
        if base_count > pk_count:
            raise FuriganaError(f"Base {group} exceeds the PK dictionary")
        for offset in range(base_count):
            display_id = display_start + offset
            reading_id = reading_start + offset
            if original_pk.texts[display_id] != base_block.texts[display_id]:
                raise FuriganaError(f"PK/Base display dictionary differs at {display_id}")
            if original_pk.texts[reading_id] != base_block.texts[reading_id]:
                raise FuriganaError(f"PK/Base reading dictionary differs at {reading_id}")


def make_pk_operations(
    original: MessageTable,
    current: MessageTable,
    table: Mapping[str, str],
    kana_to_hangul: Any,
) -> tuple[list[Operation], list[dict[str, Any]], list[dict[str, Any]]]:
    if original.string_count != 29_210 or current.string_count != 29_218:
        raise FuriganaError("unexpected PK msgdata string count")
    operations: list[Operation] = []
    private_review: list[dict[str, Any]] = []
    used_read_ids: set[int] = set()
    group_reports: list[dict[str, Any]] = []
    for group, display_start, reading_start, count in PK_GROUPS:
        classes: dict[str, int] = {}
        for offset in range(count):
            display_id = display_start + offset
            reading_id = reading_start + offset
            if reading_id >= original.string_count or reading_id >= current.string_count:
                raise FuriganaError(f"PK {group} pair escapes msgdata")
            if reading_id in used_read_ids:
                raise FuriganaError(f"duplicate PK reading id {reading_id}")
            used_read_ids.add(reading_id)
            replacement, conversion_class = convert_display(
                original.texts[display_id],
                original.texts[reading_id],
                display_id,
                table,
                kana_to_hangul,
            )
            validate_replacement(replacement, f"PK id {reading_id}")
            operations.append(
                Operation(
                    entry_id=reading_id,
                    replacement=replacement,
                    source_hash=text_hash(current.texts[reading_id]),
                    display_hash=text_hash(original.texts[display_id]),
                    group=group,
                )
            )
            private_review.append(
                {
                    "display_id": display_id,
                    "reading_id": reading_id,
                    "display": original.texts[display_id],
                    "original_reading": original.texts[reading_id],
                    "replacement": replacement,
                    "conversion_class": conversion_class,
                }
            )
            classes[conversion_class] = classes.get(conversion_class, 0) + 1
        group_reports.append(
            {
                "name": group,
                "display_start": display_start,
                "reading_start": reading_start,
                "count": count,
                "conversion_classes": dict(sorted(classes.items())),
            }
        )
    if len(operations) != EXPECTED_PK_READING_COUNT:
        raise FuriganaError(f"PK operation count differs: {len(operations)}")
    return operations, group_reports, private_review


def make_base_operations(
    original: Any,
    current: Any,
    table: Mapping[str, str],
    kana_to_hangul: Any,
) -> tuple[list[Operation], dict[str, Any], list[dict[str, Any]]]:
    original_block = original.blocks[0]
    current_block = current.blocks[0]
    if original_block.slot_count != 25_069 or current_block.slot_count != 25_069:
        raise FuriganaError("unexpected base strdata block 0 count")
    operations: list[Operation] = []
    review: list[dict[str, Any]] = []
    classes: dict[str, int] = {}
    group_reports: dict[str, int] = {}
    for group, display_start, reading_start, pk_count in PK_GROUPS:
        count = BASE_GROUP_COUNTS[group]
        if count > pk_count:
            raise FuriganaError(f"Base {group} count exceeds PK group")
        for offset in range(count):
            display_id = display_start + offset
            reading_id = reading_start + offset
            display = original_block.texts[display_id]
            original_reading = original_block.texts[reading_id]
            if not display or not original_reading:
                raise FuriganaError(f"empty Base {group} pair at {display_id}/{reading_id}")
            replacement, conversion_class = convert_display(
                display, original_reading, display_id, table, kana_to_hangul
            )
            validate_replacement(replacement, f"Base slot {reading_id}")
            operations.append(
                Operation(
                    entry_id=reading_id,
                    replacement=replacement,
                    source_hash=text_hash(current_block.texts[reading_id]),
                    display_hash=text_hash(display),
                    group=group,
                )
            )
            review.append(
                {
                    "block": 0,
                    "display_slot": display_id,
                    "reading_slot": reading_id,
                    "display": display,
                    "original_reading": original_reading,
                    "replacement": replacement,
                    "conversion_class": conversion_class,
                }
            )
            classes[conversion_class] = classes.get(conversion_class, 0) + 1
        group_reports[group] = count
    if len(operations) != EXPECTED_BASE_READING_COUNT:
        raise FuriganaError(f"Base operation count differs: {len(operations)}")
    report = {
        "name": "base_aligned_name_dictionaries",
        "block": 0,
        "scope_anchor": "complete Base name dictionaries before castle/province/title ranges",
        "shared_group_counts": group_reports,
        "count": len(operations),
        "conversion_classes": dict(sorted(classes.items())),
    }
    return operations, report, review


def validate_replacement(value: str, label: str) -> None:
    if not value or any(character.isspace() for character in value):
        raise FuriganaError(f"{label} has an empty or spaced replacement")
    if not HANGUL_RE.fullmatch(value):
        raise FuriganaError(f"{label} replacement is not Hangul-only")
    if "\x00" in value:
        raise FuriganaError(f"{label} replacement contains NUL")


def apply_common_operations(
    packed: bytes,
    operations: Sequence[Operation],
) -> tuple[bytes, bytes, MessageTable]:
    _, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    texts = list(table.texts)
    seen: set[int] = set()
    for operation in operations:
        if operation.entry_id in seen:
            raise FuriganaError(f"duplicate common operation {operation.entry_id}")
        seen.add(operation.entry_id)
        if not 0 <= operation.entry_id < len(texts):
            raise FuriganaError(f"common operation escapes table {operation.entry_id}")
        if text_hash(texts[operation.entry_id]) != operation.source_hash:
            raise FuriganaError(f"common source hash mismatch at {operation.entry_id}")
        texts[operation.entry_id] = operation.replacement
    rebuilt_raw = rebuild_message_table(table, texts)
    parsed = parse_message_table(rebuilt_raw)
    if parsed.texts != tuple(texts):
        raise FuriganaError("common candidate parse verification failed")
    rebuilt_packed = recompress_wrapper(rebuilt_raw, packed)
    _, roundtrip = decompress_wrapper(rebuilt_packed)
    if roundtrip != rebuilt_raw:
        raise FuriganaError("common candidate wrapper verification failed")
    return rebuilt_packed, rebuilt_raw, parsed


def apply_base_operations(
    packed: bytes,
    operations: Sequence[Operation],
) -> tuple[bytes, bytes, Any]:
    _, raw = decompress_wrapper(packed)
    container = parse_strdata(raw)
    texts = list(container.blocks[0].texts)
    seen: set[int] = set()
    for operation in operations:
        if operation.entry_id in seen:
            raise FuriganaError(f"duplicate Base operation {operation.entry_id}")
        seen.add(operation.entry_id)
        if not 0 <= operation.entry_id < len(texts):
            raise FuriganaError(f"Base operation escapes block 0: {operation.entry_id}")
        if text_hash(texts[operation.entry_id]) != operation.source_hash:
            raise FuriganaError(f"Base source hash mismatch at {operation.entry_id}")
        texts[operation.entry_id] = operation.replacement
    rebuilt_raw = rebuild_strdata(container, {0: texts})
    parsed = parse_strdata(rebuilt_raw)
    if parsed.blocks[0].texts != tuple(texts):
        raise FuriganaError("Base candidate parse verification failed")
    rebuilt_packed = recompress_wrapper(rebuilt_raw, packed)
    _, roundtrip = decompress_wrapper(rebuilt_packed)
    if roundtrip != rebuilt_raw:
        raise FuriganaError("Base candidate wrapper verification failed")
    return rebuilt_packed, rebuilt_raw, parsed


def operation_json(operation: Operation) -> dict[str, Any]:
    return {
        "id": operation.entry_id,
        "source_utf16le_sha256": operation.source_hash,
        "display_source_utf16le_sha256": operation.display_hash,
        "replacement": operation.replacement,
        "group": operation.group,
    }


def assert_source_free(value: Any) -> None:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if SOURCE_FREE_RE.search(encoded):
        raise FuriganaError("public artifact contains CJK source text")


def assert_candidate_scope(
    source: Sequence[str], candidate: Sequence[str], operations: Sequence[Operation], label: str
) -> None:
    selected = {operation.entry_id: operation.replacement for operation in operations}
    if len(selected) != len(operations):
        raise FuriganaError(f"{label} duplicate operation scope")
    for entry_id, (before, after) in enumerate(zip(source, candidate, strict=True)):
        expected = selected.get(entry_id, before)
        if after != expected:
            raise FuriganaError(f"{label} scope changed unexpectedly at {entry_id}")


def build(args: argparse.Namespace) -> dict[str, Any]:
    steam_root = args.steam_root.resolve(strict=True)
    original_root = args.original_root.resolve(strict=True)
    output_root = args.output_root.resolve()
    if output_root.exists() and not output_root.is_dir():
        raise FuriganaError("output root is not a directory")

    table = load_hanja_table(args.hanja_wheel)
    khangul = load_unihan_khangul(args.unihan_readings)
    kana_to_hangul = load_kana_converter()

    original_pk_path = safe_resource_path(original_root, PK_RESOURCE)
    original_base_path = safe_resource_path(original_root, BASE_RESOURCE)
    current_pk_path = safe_resource_path(steam_root, PK_RESOURCE)
    current_base_path = safe_resource_path(steam_root, BASE_RESOURCE)
    original_pk_packed, original_pk_raw, original_pk = parse_common(original_pk_path)
    current_pk_packed, current_pk_raw, current_pk = parse_common(current_pk_path)
    original_base_packed, original_base_raw, original_base = parse_base(original_base_path)
    current_base_packed, current_base_raw, current_base = parse_base(current_base_path)
    assert_original_name_dictionaries_aligned(original_pk, original_base)

    source_displays = [
        original_pk.texts[display_start + offset]
        for _group, display_start, _reading_start, count in PK_GROUPS
        for offset in range(count)
    ] + [
        original_base.blocks[0].texts[display_start + offset]
        for _group, display_start, _reading_start, _pk_count in PK_GROUPS
        for offset in range(BASE_GROUP_COUNTS[_group])
    ]
    coverage = require_hanja_inputs_covered(source_displays, table, khangul)

    pk_operations, pk_groups, pk_review = make_pk_operations(
        original_pk, current_pk, table, kana_to_hangul
    )
    base_operations, base_group, base_review = make_base_operations(
        original_base, current_base, table, kana_to_hangul
    )
    if compact_int_list_hash([item.entry_id for item in pk_operations]) != PK_READING_IDS_SHA256:
        raise FuriganaError("PK reading-ID scope vector differs")
    if compact_int_list_hash([item.entry_id for item in base_operations]) != BASE_READING_IDS_SHA256:
        raise FuriganaError("Base reading-ID scope vector differs")
    pk_candidate_packed, pk_candidate_raw, pk_candidate = apply_common_operations(
        current_pk_packed, pk_operations
    )
    base_candidate_packed, base_candidate_raw, base_candidate = apply_base_operations(
        current_base_packed, base_operations
    )
    assert_candidate_scope(current_pk.texts, pk_candidate.texts, pk_operations, "PK")
    assert_candidate_scope(
        current_base.blocks[0].texts,
        base_candidate.blocks[0].texts,
        base_operations,
        "Base block 0",
    )

    # Regression examples requested by the user.  Both are separate no-space
    # fields and concatenate in the officer editor/UI as 직전신장.
    pk_by_id = {operation.entry_id: operation.replacement for operation in pk_operations}
    if pk_by_id.get(3416) != "직전" or pk_by_id.get(4598) != "신장":
        raise FuriganaError("Nobunaga Korean-Hanja reading regression failed")
    base_by_id = {operation.entry_id: operation.replacement for operation in base_operations}
    if base_by_id.get(3416) != "직전" or base_by_id.get(4598) != "신장":
        raise FuriganaError("Base Nobunaga Korean-Hanja reading regression failed")

    public = {
        "schema": SCHEMA,
        "scope": "complete name-dictionary furigana fields only; display-name fields are unchanged",
        "source_free": True,
        "contains_complete_game_resource": False,
        "contains_original_game_text": False,
        "reading_policy": {
            "hanja": "Korean Hanja reading with Korean initial-sound law",
            "spacing": "no whitespace in every replacement",
            "kana_only": "existing Japanese kana reading transliterated to Hangul when no Hanja exists",
            "encoded_display_exceptions": len(SPECIAL_PRIMARY_REPLACEMENTS),
            "scope_anchor": "three contiguous name dictionaries; castle/province/title ranges excluded",
            "pk_reading_ids_sha256": PK_READING_IDS_SHA256,
            "base_reading_ids_sha256": BASE_READING_IDS_SHA256,
        },
        "unicode_sources": {
            "unihan_version": "17.0.0",
            "unihan_readings_sha256": UNICODE_UNIHAN_READINGS_SHA256,
            "hanja_package": "hanja==0.15.1",
            "hanja_wheel_sha256": HANJA_WHEEL_SHA256,
            "coverage": coverage,
        },
        "resources": [
            {
                "resource": PK_RESOURCE,
                "kind": "common_message_table",
                "source": {
                    "size": len(current_pk_packed),
                    "sha256": sha256_bytes(current_pk_packed),
                    "raw_size": len(current_pk_raw),
                    "raw_sha256": sha256_bytes(current_pk_raw),
                    "string_count": current_pk.string_count,
                },
                "target": {
                    "size": len(pk_candidate_packed),
                    "sha256": sha256_bytes(pk_candidate_packed),
                    "raw_size": len(pk_candidate_raw),
                    "raw_sha256": sha256_bytes(pk_candidate_raw),
                },
                "groups": pk_groups,
                "operation_count": len(pk_operations),
                "operations": [operation_json(item) for item in pk_operations],
            },
            {
                "resource": BASE_RESOURCE,
                "kind": "strdata_block_zero",
                "source": {
                    "size": len(current_base_packed),
                    "sha256": sha256_bytes(current_base_packed),
                    "raw_size": len(current_base_raw),
                    "raw_sha256": sha256_bytes(current_base_raw),
                    "block_slot_counts": [block.slot_count for block in current_base.blocks],
                },
                "target": {
                    "size": len(base_candidate_packed),
                    "sha256": sha256_bytes(base_candidate_packed),
                    "raw_size": len(base_candidate_raw),
                    "raw_sha256": sha256_bytes(base_candidate_raw),
                },
                "groups": [base_group],
                "operation_count": len(base_operations),
                "operations": [operation_json(item) for item in base_operations],
            },
        ],
        "regression_examples": {
            "surname_reading": "직전",
            "given_reading": "신장",
            "combined_without_space": "직전신장",
        },
    }
    assert_source_free(public)

    validation = {
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "resources": [
            {
                "resource": PK_RESOURCE,
                "operation_count": len(pk_operations),
                "target_parse_verified": True,
                "wrapper_roundtrip_verified": True,
                "non_target_fields_unchanged": True,
                "all_replacements_hangul_only": True,
                "all_replacements_no_whitespace": True,
            },
            {
                "resource": BASE_RESOURCE,
                "operation_count": len(base_operations),
                "target_parse_verified": True,
                "wrapper_roundtrip_verified": True,
                "non_target_fields_unchanged": True,
                "all_replacements_hangul_only": True,
                "all_replacements_no_whitespace": True,
            },
        ],
        "pair_counts": {
            "pk": len(pk_operations),
            "base": len(base_operations),
            "combined_operation_count": len(pk_operations) + len(base_operations),
        },
        "regression_examples_verified": True,
    }
    assert_source_free(validation)

    public_path = output_root / "public" / "hanja_furigana_v0140.operations.json"
    validation_path = output_root / "validation.v1.json"
    review_path = output_root / "private" / "hanja_furigana_v0140.review.json"
    candidate_pk_path = output_root / "private" / "candidate" / PK_RESOURCE
    candidate_base_path = output_root / "private" / "candidate" / BASE_RESOURCE
    write_json(public_path, public)
    write_json(validation_path, validation)
    # This review is intentionally private: it contains original game text for
    # full human auditing, unlike the public operation ledger.
    write_json(
        review_path,
        {
            "schema": "nobu16.kr.hanja-furigana-private-review.v1",
            "pk": pk_review,
            "base": base_review,
        },
    )
    atomic_write(candidate_pk_path, pk_candidate_packed)
    atomic_write(candidate_base_path, base_candidate_packed)
    return {
        "public": public_path,
        "validation": validation_path,
        "private_review": review_path,
        "candidate_pk": candidate_pk_path,
        "candidate_base": candidate_base_path,
        "pk_operations": len(pk_operations),
        "base_operations": len(base_operations),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--original-root", type=Path, default=DEFAULT_ORIGINAL_ROOT)
    parser.add_argument("--hanja-wheel", type=Path, default=DEFAULT_HANJA_WHEEL)
    parser.add_argument("--unihan-readings", type=Path, default=DEFAULT_UNIHAN_READINGS)
    parser.add_argument("--output-root", type=Path, default=WORKSTREAM)
    return parser.parse_args(argv)


def main() -> int:
    try:
        result = build(parse_args())
    except FuriganaError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for key, value in result.items():
        print(f"{key}={value}")
    print("build=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
