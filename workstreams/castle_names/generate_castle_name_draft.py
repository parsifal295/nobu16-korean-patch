#!/usr/bin/env python3
"""Generate a deterministic, source-text-free Korean castle-name draft.

Official SC/EN/JP strings are accepted only as SHA-pinned local verification
inputs.  They are written solely beneath the caller's private output folder;
the public overlay contains stable msgdata ids, Korean readings, and explicit
automatic-review status, but no commercial source text.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import struct
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable, Sequence


sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
PATCH_ROOT = SCRIPT_DIR.parents[1]
TOOLS_DIR = PATCH_ROOT / "tools"
FIRST_ID = 9151
LAST_ID = 9542
COUNT = LAST_ID - FIRST_ID + 1
READING_FIRST_ID = 9543
READING_LAST_ID = 9934
SUFFIX_FIRST_ID = 9936
SUFFIX_LAST_ID = 9940
SUFFIX_READING_FIRST_ID = 9942
SUFFIX_READING_LAST_ID = 9946
ADJACENT_UNCLASSIFIED_FIRST_ID = 9947
ADJACENT_UNCLASSIFIED_LAST_ID = 13974
PROVINCE_FIRST_ID = 13975
PROVINCE_LAST_ID = 14046
PROVINCE_READING_FIRST_ID = 14047
PROVINCE_READING_LAST_ID = 14118
EXPECTED_STRING_COUNT = 29210
OVERLAY_NAME = "castle_names_ko_9151_9542.v0.1.json"
STATUS = "automatic_draft_review_needed"
CUSTOM_ROMAJI = str.maketrans({"ª": "o", "¥": "O", "¨": "u"})
JP_SYLLABIC_N_Y = re.compile("\u3093[\u3084\u3086\u3088]")
EXPECTED_JP_SYLLABIC_N_Y_IDS = {9201, 9478}
RESOURCE_PINS = {
    "SC": {
        "logical_path": "MSG_PK/SC/msgdata.bin",
        "wrapper_size": 267385,
        "wrapper_sha256": "0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E",
        "raw_size": 499760,
        "raw_sha256": "1290BCDF6B00C6E4516061888C618BC66A246375E271C9D1330A9D168037FBCF",
    },
    "EN": {
        "logical_path": "MSG_PK/EN/msgdata.bin",
        "wrapper_size": 267550,
        "wrapper_sha256": "15142A9D252F1759364FEE5D090B0802C51D8355B2A24A1DC6F1300FBF1EC5E1",
        "raw_size": 744236,
        "raw_sha256": "DA913D870DA3C13F108E8E6727C9A8881B9E13A83F8EB7F02DD3C55D1D444B32",
    },
    "JP": {
        "logical_path": "MSG_PK/JP/msgdata.bin",
        "wrapper_size": 273734,
        "wrapper_sha256": "9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38",
        "raw_size": 431044,
        "raw_sha256": "119F10F28DAEEFFA7B231764BB5747A8837DEB487E4595504ADE2A77023148A0",
    },
}


class CastleNameError(ValueError):
    """Raised when an input pin, resource layout, or generated draft fails."""


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CastleNameError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LZ4 = load_module("nobu16_castle_name_lz4", TOOLS_DIR / "nobu16_lz4.py")
MSGTABLE = load_module("nobu16_castle_name_msgtable", TOOLS_DIR / "nobu16_msg_table.py")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_json(path: Path, value: Any) -> None:
    atomic_write(path, json_bytes(value))


def require_empty_output(path: Path) -> None:
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise CastleNameError(f"output root must not exist or must be empty: {path}")
    path.mkdir(parents=True, exist_ok=True)


def load_table(language: str, path: Path) -> dict[str, Any]:
    pin = RESOURCE_PINS[language]
    blob = path.read_bytes()
    if len(blob) != pin["wrapper_size"] or sha256_bytes(blob) != pin["wrapper_sha256"]:
        raise CastleNameError(f"{language} msgdata wrapper does not match the pinned game revision")
    _header, raw = LZ4.decompress_wrapper(blob)
    if len(raw) != pin["raw_size"] or sha256_bytes(raw) != pin["raw_sha256"]:
        raise CastleNameError(f"{language} decompressed msgdata does not match its pin")
    table = MSGTABLE.parse_message_table(raw)
    if table.string_count != EXPECTED_STRING_COUNT:
        raise CastleNameError(f"{language} msgdata string count is {table.string_count}")
    if MSGTABLE.rebuild_message_table(table, table.texts) != raw:
        raise CastleNameError(f"{language} msgdata parse/rebuild is not byte-exact")
    return {
        "language": language,
        "pin": pin,
        "texts": table.texts,
        "roundtrip_exact": True,
    }


def block_hash(texts: Sequence[str], first_id: int, last_id: int) -> str:
    payload = bytearray()
    for entry_id in range(first_id, last_id + 1):
        encoded = texts[entry_id].encode("utf-8")
        payload.extend(struct.pack("<II", entry_id, len(encoded)))
        payload.extend(encoded)
    return sha256_bytes(bytes(payload))


MORA_TO_HANGUL = {
    "a": "아", "i": "이", "u": "우", "e": "에", "o": "오",
    "ga": "가", "gi": "기", "gu": "구", "ge": "게", "go": "고",
    "gya": "갸", "gyu": "규", "gyo": "교",
    "sa": "사", "shi": "시", "su": "스", "se": "세", "so": "소",
    "sha": "샤", "shu": "슈", "sho": "쇼",
    "za": "자", "ji": "지", "zu": "즈", "ze": "제", "zo": "조",
    "chi": "치", "tsu": "츠", "cha": "차", "chu": "추", "cho": "초",
    "da": "다", "de": "데", "do": "도", "di": "디", "du": "두",
    "na": "나", "ni": "니", "nu": "누", "ne": "네", "no": "노",
    "nya": "냐", "nyu": "뉴", "nyo": "뇨",
    "ha": "하", "hi": "히", "fu": "후", "he": "헤", "ho": "호",
    "hya": "햐", "hyu": "휴", "hyo": "효",
    "ba": "바", "bi": "비", "bu": "부", "be": "베", "bo": "보",
    "bya": "뱌", "byu": "뷰", "byo": "뵤",
    "pa": "파", "pi": "피", "pu": "푸", "pe": "페", "po": "포",
    "pya": "퍄", "pyu": "퓨", "pyo": "표",
    "ma": "마", "mi": "미", "mu": "무", "me": "메", "mo": "모",
    "mya": "먀", "myu": "뮤", "myo": "묘",
    "ya": "야", "yu": "유", "yo": "요",
    "ra": "라", "ri": "리", "ru": "루", "re": "레", "ro": "로",
    "rya": "랴", "ryu": "류", "ryo": "료",
    "wa": "와", "wi": "위", "we": "웨", "wo": "워", "ye": "예",
    "ja": "자", "ju": "주", "jo": "조", "she": "셰", "je": "제", "che": "체",
    "ti": "티", "tu": "투", "fa": "파", "fi": "피", "fe": "페", "fo": "포",
    "vu": "부",
}
INITIAL_STOP = {
    "ka": "가", "ki": "기", "ku": "구", "ke": "게", "ko": "고",
    "kya": "갸", "kyu": "규", "kyo": "교",
    "ta": "다", "te": "데", "to": "도",
}
MEDIAL_STOP = {
    "ka": "카", "ki": "키", "ku": "쿠", "ke": "케", "ko": "코",
    "kya": "캬", "kyu": "큐", "kyo": "쿄",
    "ta": "타", "te": "테", "to": "토",
}
ROMAJI_MORAS = tuple(
    sorted(
        set(MORA_TO_HANGUL) | set(INITIAL_STOP) | set(MEDIAL_STOP),
        key=lambda value: (-len(value), value),
    )
)


def add_final(text: str, jongseong: int, fallback: str) -> str:
    if not text:
        return fallback
    codepoint = ord(text[-1])
    if 0xAC00 <= codepoint <= 0xD7A3 and (codepoint - 0xAC00) % 28 == 0:
        return text[:-1] + chr(codepoint + jongseong)
    return text + fallback


def romaji_moras(word: str, syllabic_n_y_count: int = 0) -> list[str]:
    source = unicodedata.normalize("NFKC", word.translate(CUSTOM_ROMAJI)).lower()
    if not source or not re.fullmatch(r"[a-z]+", source):
        raise CastleNameError(f"unsupported English romaji word: {word!r}")
    if syllabic_n_y_count:
        if source.count("ny") != syllabic_n_y_count:
            raise CastleNameError(
                f"cannot align {syllabic_n_y_count} Japanese syllabic n+y boundary/boundaries "
                f"with English romaji word: {word!r}"
            )
        source = source.replace("ny", "n'y")
    result: list[str] = []
    index = 0
    while index < len(source):
        if source[index] == "'":
            index += 1
            continue
        if (
            index + 1 < len(source)
            and source[index] == source[index + 1]
            and source[index] not in "aeioun"
        ):
            result.append("Q")
            index += 1
            continue
        matched = next((key for key in ROMAJI_MORAS if source.startswith(key, index)), None)
        if matched is not None:
            result.append(matched)
            index += len(matched)
            continue
        if source[index] == "n":
            result.append("n")
            index += 1
            continue
        raise CastleNameError(f"unsupported romaji sequence {source[index:]!r} in {word!r}")
    return result


def moras_to_hangul(keys: Sequence[str]) -> str:
    output = ""
    spoken_index = 0
    for key in keys:
        if key == "Q":
            output = add_final(output, 19, "ㅅ")
            continue
        if key == "n":
            output = add_final(output, 4, "ㄴ")
            continue
        if key in INITIAL_STOP and spoken_index == 0:
            syllable = INITIAL_STOP[key]
        elif key in MEDIAL_STOP:
            syllable = MEDIAL_STOP[key]
        else:
            syllable = MORA_TO_HANGUL.get(key)
        if syllable is None:
            raise CastleNameError(f"unsupported mora: {key}")
        output += syllable
        spoken_index += 1
    return output


def transliterate_name(english: str, japanese_reading: str) -> tuple[str, str]:
    if not re.fullmatch(r"[A-Za-zª¥¨]+(?: [A-Za-zª¥¨]+)*", english):
        raise CastleNameError(f"unsupported English castle-name form: {english!r}")
    words = english.split(" ")
    boundary_count = len(JP_SYLLABIC_N_Y.findall(japanese_reading))
    word_boundary_counts = [word.lower().count("ny") for word in words]
    if boundary_count and sum(word_boundary_counts) != boundary_count:
        raise CastleNameError(
            f"cannot align Japanese syllabic n+y boundary in {english!r} / {japanese_reading!r}"
        )
    korean = " ".join(
        moras_to_hangul(romaji_moras(word, count if boundary_count else 0))
        for word, count in zip(words, word_boundary_counts)
    )
    if boundary_count:
        method = "en_romaji_jp_n_y_boundary"
    else:
        method = "en_romaji_words" if len(words) > 1 else "en_romaji"
    return korean, method


def require_korean_name(value: str, entry_id: int) -> None:
    if not value or value.startswith(" ") or value.endswith(" ") or "  " in value:
        raise CastleNameError(f"invalid Korean spacing at id {entry_id}")
    if any(character != " " and not (0xAC00 <= ord(character) <= 0xD7A3) for character in value):
        raise CastleNameError(f"non-Hangul character in Korean draft at id {entry_id}")
    if unicodedata.normalize("NFC", value) != value:
        raise CastleNameError(f"non-NFC Korean draft at id {entry_id}")


def validate_resource_layout(tables: dict[str, dict[str, Any]]) -> dict[str, Any]:
    names = {
        language: tuple(table["texts"][FIRST_ID : LAST_ID + 1])
        for language, table in tables.items()
    }
    for language, values in names.items():
        if len(values) != COUNT or any(not value for value in values):
            raise CastleNameError(f"{language} primary castle-name block is incomplete")
    if len(set(names["SC"])) != 389 or len(set(names["JP"])) != 389 or len(set(names["EN"])) != 385:
        raise CastleNameError("primary castle-name uniqueness regression failed")

    for language, table in tables.items():
        texts = table["texts"]
        reading = texts[READING_FIRST_ID : READING_LAST_ID + 1]
        suffixes = texts[SUFFIX_FIRST_ID : SUFFIX_LAST_ID + 1]
        suffix_readings = texts[SUFFIX_READING_FIRST_ID : SUFFIX_READING_LAST_ID + 1]
        if len(reading) != COUNT or len(suffixes) != 5 or len(suffix_readings) != 5:
            raise CastleNameError(f"{language} adjacent castle metadata ranges are incomplete")
        if language == "EN":
            if any(reading) or any(suffix_readings):
                raise CastleNameError("EN castle reading blocks must remain empty")
        elif any(not value for value in reading) or any(not value for value in suffix_readings):
            raise CastleNameError(f"{language} castle reading blocks contain an empty value")
        if any(not value for value in suffixes) or texts[9941] != "":
            raise CastleNameError(f"{language} castle suffix block shape changed")

        adjacent = texts[ADJACENT_UNCLASSIFIED_FIRST_ID : ADJACENT_UNCLASSIFIED_LAST_ID + 1]
        provinces = texts[PROVINCE_FIRST_ID : PROVINCE_LAST_ID + 1]
        province_readings = texts[PROVINCE_READING_FIRST_ID : PROVINCE_READING_LAST_ID + 1]
        if len(adjacent) != 4028 or any(not value for value in adjacent):
            raise CastleNameError(f"{language} adjacent geographic/special-label block changed")
        if len(provinces) != 72 or any(not value for value in provinces):
            raise CastleNameError(f"{language} province-name block changed")
        if len(province_readings) != 72:
            raise CastleNameError(f"{language} province-reading block changed")
        if language == "EN":
            if any(province_readings):
                raise CastleNameError("EN province-reading block must remain empty")
        elif any(not value for value in province_readings):
            raise CastleNameError(f"{language} province-reading block contains an empty value")

    return {
        "name_blocks": {
            language: {
                "first_id": FIRST_ID,
                "last_id": LAST_ID,
                "count": COUNT,
                "nonempty_count": COUNT,
                "unique_text_count": len(set(values)),
                "text_block_sha256": block_hash(tables[language]["texts"], FIRST_ID, LAST_ID),
            }
            for language, values in names.items()
        },
        "reading_blocks": {
            language: {
                "first_id": READING_FIRST_ID,
                "last_id": READING_LAST_ID,
                "count": COUNT,
                "nonempty_count": sum(
                    bool(value)
                    for value in tables[language]["texts"][READING_FIRST_ID : READING_LAST_ID + 1]
                ),
                "text_block_sha256": block_hash(
                    tables[language]["texts"], READING_FIRST_ID, READING_LAST_ID
                ),
            }
            for language in ("SC", "EN", "JP")
        },
        "suffix_contract": {
            "name_ids": [SUFFIX_FIRST_ID, SUFFIX_LAST_ID],
            "reading_ids": [SUFFIX_READING_FIRST_ID, SUFFIX_READING_LAST_ID],
            "separator_id_9941_empty_all_languages": True,
            "suffix_count": 5,
        },
        "excluded_adjacent_ranges": [
            {
                "first_id": ADJACENT_UNCLASSIFIED_FIRST_ID,
                "last_id": ADJACENT_UNCLASSIFIED_LAST_ID,
                "count": ADJACENT_UNCLASSIFIED_LAST_ID - ADJACENT_UNCLASSIFIED_FIRST_ID + 1,
                "classification": "unclassified_geographic_and_special_labels",
                "reason_excluded": "not proven to be canonical castle-name ids",
            },
            {
                "first_id": PROVINCE_FIRST_ID,
                "last_id": PROVINCE_LAST_ID,
                "count": PROVINCE_LAST_ID - PROVINCE_FIRST_ID + 1,
                "classification": "province_names",
                "reason_excluded": "separate province-name block",
            },
            {
                "first_id": PROVINCE_READING_FIRST_ID,
                "last_id": PROVINCE_READING_LAST_ID,
                "count": PROVINCE_READING_LAST_ID - PROVINCE_READING_FIRST_ID + 1,
                "classification": "province_readings_sc_jp_only",
                "reason_excluded": "separate province-reading block",
            },
        ],
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    output_root = args.output_root.resolve()
    require_empty_output(output_root)
    tables = {
        "SC": load_table("SC", args.sc.resolve()),
        "EN": load_table("EN", args.en.resolve()),
        "JP": load_table("JP", args.jp.resolve()),
    }
    layout = validate_resource_layout(tables)

    public_entries: list[dict[str, Any]] = []
    private_entries: list[dict[str, Any]] = []
    method_counts: dict[str, int] = {}
    jp_syllabic_n_y_ids: set[int] = set()
    for entry_id in range(FIRST_ID, LAST_ID + 1):
        english = tables["EN"]["texts"][entry_id]
        japanese_reading = tables["JP"]["texts"][READING_FIRST_ID + entry_id - FIRST_ID]
        korean, method = transliterate_name(english, japanese_reading)
        require_korean_name(korean, entry_id)
        if method == "en_romaji_jp_n_y_boundary":
            jp_syllabic_n_y_ids.add(entry_id)
        method_counts[method] = method_counts.get(method, 0) + 1
        public_entries.append({"id": entry_id, "ko": korean, "method": method, "status": STATUS})
        private_entries.append(
            {
                "id": entry_id,
                "source": {language: tables[language]["texts"][entry_id] for language in ("SC", "EN", "JP")},
                "ko": korean,
                "method": method,
                "status": STATUS,
            }
        )

    if len(public_entries) != COUNT or [row["id"] for row in public_entries] != list(range(FIRST_ID, LAST_ID + 1)):
        raise CastleNameError("generated public overlay id coverage is incomplete")
    if jp_syllabic_n_y_ids != EXPECTED_JP_SYLLABIC_N_Y_IDS:
        raise CastleNameError(
            "Japanese syllabic n+y boundary ids changed: "
            f"{sorted(jp_syllabic_n_y_ids)}"
        )

    overlay = {
        "schema": "nobu16.kr.castle-name-overlay.v0.1",
        "source_text_free": True,
        "target": {
            "resource": "MSG_PK/SC/msgdata.bin",
            "first_id": FIRST_ID,
            "last_id": LAST_ID,
            "entry_count": COUNT,
            "shared_suffix_id_range_not_modified": {
                "first_id": SUFFIX_FIRST_ID,
                "last_id": SUFFIX_LAST_ID,
                "count": SUFFIX_LAST_ID - SUFFIX_FIRST_ID + 1,
            },
        },
        "translation_policy": {
            "base": "official EN romanized reading, mechanically converted to Korean",
            "castle_type_suffix_included": False,
            "jp_reading_use": "resolve ambiguous syllabic n followed by y",
            "reason": "the game composes castle type through shared ids 9936..9940",
            "review_required": True,
        },
        "entries": public_entries,
    }
    public_path = output_root / "public" / OVERLAY_NAME
    write_json(public_path, overlay)

    private_alignment = {
        "schema": "nobu16.kr.castle-name-private-alignment.v0.1",
        "distribution_forbidden": True,
        "entries": private_entries,
    }
    private_path = output_root / "private" / "castle_names_alignment.v0.1.json"
    write_json(private_path, private_alignment)

    resources = []
    for language in ("SC", "EN", "JP"):
        pin = tables[language]["pin"]
        resources.append(
            {
                "language": language,
                "logical_path": pin["logical_path"],
                "wrapper_size": pin["wrapper_size"],
                "wrapper_sha256": pin["wrapper_sha256"],
                "raw_size": pin["raw_size"],
                "raw_sha256": pin["raw_sha256"],
                "string_count": EXPECTED_STRING_COUNT,
                "unchanged_parse_rebuild_byte_exact": True,
            }
        )
    evidence = {
        "schema": "nobu16.kr.castle-name-resource-map.v0.1",
        "source_text_free": True,
        "resources": resources,
        "aligned_primary_block": {
            "resource": "msgdata.bin",
            "first_id": FIRST_ID,
            "last_id": LAST_ID,
            "entry_count": COUNT,
            "same_ids_in_languages": ["SC", "EN", "JP"],
            "all_nonempty": True,
        },
        **layout,
    }
    evidence_path = output_root / "evidence" / "resource_id_map.v0.1.json"
    write_json(evidence_path, evidence)

    validation = {
        "schema": "nobu16.kr.castle-name-draft-validation.v0.1",
        "passed": True,
        "input_wrapper_pins_exact": True,
        "raw_resource_pins_exact": True,
        "message_table_roundtrip_exact_all_languages": True,
        "aligned_id_range_exact": True,
        "adjacent_unclassified_ranges_excluded": True,
        "jp_syllabic_n_y_boundary_ids_exact": True,
        "jp_syllabic_n_y_boundary_ids": sorted(jp_syllabic_n_y_ids),
        "entry_count": COUNT,
        "automatic_review_needed_count": sum(row["status"] == STATUS for row in public_entries),
        "source_text_fields_in_public_overlay": 0,
        "public_ko_only_precomposed_hangul_and_ascii_space": True,
        "installed_game_files_modified": False,
        "process_memory_access": False,
        "registry_access": False,
        "private_alignment_distribution_forbidden": True,
    }
    validation_path = output_root / "validation.json"
    write_json(validation_path, validation)

    manifest = {
        "schema": "nobu16.kr.castle-name-draft-manifest.v0.1",
        "source_text_free_public_artifacts": True,
        "generator": {
            "path": "workstreams/castle_names/generate_castle_name_draft.py",
            "sha256": sha256_file(Path(__file__)),
        },
        "outputs": {
            "public_overlay": {
                "path": f"public/{OVERLAY_NAME}",
                "size": public_path.stat().st_size,
                "sha256": sha256_file(public_path),
            },
            "resource_evidence": {
                "path": "evidence/resource_id_map.v0.1.json",
                "size": evidence_path.stat().st_size,
                "sha256": sha256_file(evidence_path),
            },
            "validation": {
                "path": "validation.json",
                "size": validation_path.stat().st_size,
                "sha256": sha256_file(validation_path),
            },
            "private_alignment": {
                "path": "private/castle_names_alignment.v0.1.json",
                "size": private_path.stat().st_size,
                "sha256": sha256_file(private_path),
                "distribution_forbidden": True,
            },
        },
        "draft": {
            "entry_count": COUNT,
            "status": STATUS,
            "method_counts": dict(sorted(method_counts.items())),
            "unique_korean_name_count": len({row["ko"] for row in public_entries}),
            "max_korean_character_count_including_spaces": max(len(row["ko"]) for row in public_entries),
        },
        "safety": {
            "installed_game_files_modified": False,
            "process_memory_access": False,
            "registry_access": False,
            "commercial_source_text_in_public_artifacts": False,
            "private_alignment_distribution_forbidden": True,
        },
    }
    manifest_path = output_root / "manifest.json"
    write_json(manifest_path, manifest)

    return {
        "output_root": str(output_root),
        "entries": COUNT,
        "automatic_review_needed": COUNT,
        "overlay_sha256": sha256_file(public_path),
        "evidence_sha256": sha256_file(evidence_path),
        "manifest_sha256": sha256_file(manifest_path),
        "validation_sha256": sha256_file(validation_path),
        "private_alignment_sha256": sha256_file(private_path),
        "method_counts": method_counts,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sc", type=Path, required=True, help="pinned stock SC msgdata wrapper")
    parser.add_argument("--en", type=Path, required=True, help="pinned stock EN msgdata wrapper")
    parser.add_argument("--jp", type=Path, required=True, help="pinned stock JP msgdata wrapper")
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = build(args)
    except (OSError, CastleNameError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for key, value in result.items():
        if isinstance(value, dict):
            value = ",".join(f"{name}={count}" for name, count in sorted(value.items()))
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
