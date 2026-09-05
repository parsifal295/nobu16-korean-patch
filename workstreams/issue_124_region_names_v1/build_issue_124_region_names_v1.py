#!/usr/bin/env python3
"""Build and strictly verify the complete issue #124 Korean place-name pass."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO / "tools"), str(REPO / "workstreams" / "strdata")]

from generate_officer_name_catalog import (  # noqa: E402
    INITIAL_STOP,
    MEDIAL_STOP,
    MORA_TO_HANGUL,
    Mora,
    OfficerNameError,
    add_final,
    kana_moras,
    mora_equal,
    romaji_moras,
)
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import (  # noqa: E402
    MessageTable,
    MessageTableError,
    parse_message_table,
    rebuild_message_table,
)
from strdata_format import (  # noqa: E402
    StrdataArchive,
    StrdataFormatError,
    parse_raw_strdata,
    rebuild_raw_strdata,
)


SCHEMA = "nobu16.kr.issue124-region-name-validation.v2"
AUDIT_SCHEMA = "nobu16.kr.issue124-region-name-audit.v2"
POLICY_SCHEMA = "nobu16.kr.issue124-region-name-policy.v2"
POLICY_PATH = HERE / "issue_124_region_names.policy.v2.json"
VALIDATION_NAME = "validation.issue124_region_names.v2.json"
AUDIT_NAME = "audit.issue124_region_names.v2.json"

MSG_DATA = Path("MSG_PK/JP/msgdata.bin")
STR_DATA = Path("MSG/JP/strdata.bin")
RESOURCE_ORDER = (MSG_DATA,)
READ_ONLY_DEPENDENCY_ORDER = (STR_DATA,)
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

DISPLAY_START = 9_947
DISPLAY_END = 11_960
READING_OFFSET = 2_014
STRDATA_OFFSET = 84
PAIR_COUNT = DISPLAY_END - DISPLAY_START + 1
SHARED_LABEL_COUNT = 720
PLACE_NAME_COUNT = 1_294
MULTIWORD_PLACE_COUNT = 88
STRDATA_SLOT_COUNTS = (25_069, 4_100, 3_000, 122, 20)
SOURCE_MAPPING_EXCEPTIONS = frozenset((11_310, 11_311))
MORA_MATCH_EXCEPTION_ID = 10_388

INPUT_SPECS = {
    MSG_DATA: {
        "packed_size": 476_860,
        "packed_sha256": "2528F53F6F4666DEFD36EA8D5BD577DD60C78630D8E3F63CA0E5A1FE75B60B62",
        "raw_size": 474_972,
        "raw_sha256": "8E70FB63AD145795421BBD6B129073C06D7DA3ECAE5EB430572E10B538111B28",
        "string_count": 29_218,
    },
    STR_DATA: {
        "packed_size": 940_981,
        "packed_sha256": "70FCB097EE999BA8E50723E262C232F782D7DE564DDAB84C9D28180A7AA7FF55",
        "raw_size": 937_280,
        "raw_sha256": "21DAFE66284D6B919B2A0B0E47C45A2058F0BE55A2EC9751F2816B9AC18E8947",
    },
}

JP_REFERENCE_SPECS = {
    MSG_DATA: {
        "packed_size": 272_453,
        "packed_sha256": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E",
        "raw_size": 434_000,
        "raw_sha256": "D09F61E34E4AA498F3DDEF23E7B7FD2CC8E9FE50B24F39D3BA1034BE82E6D0F6",
        "string_count": 29_218,
    },
    STR_DATA: {
        "packed_size": 507_054,
        "packed_sha256": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
        "raw_size": 763_928,
        "raw_sha256": "EAB14063C2060CE11794232F483F0B2210B3BD58118165CBEEC2F37176C25649",
    },
}

EN_REFERENCE_SPEC = {
    "packed_size": 271_952,
    "packed_sha256": "BDE25DFD7265C5B6E765F2FA2A8F800E171C6C2B23FB8A66F05AE239BF71E033",
    "raw_size": 750_760,
    "raw_sha256": "756009E6C8EDA82059BE365768B34CF8C030EB9E56C7D836FE567102B163D306",
    "string_count": 29_218,
}

FINAL_SPECS = {
    MSG_DATA: {
        "packed_size": 476_948,
        "packed_sha256": "5CDB755D88933218BEF8B97193F572CFDC9BAAA84D92A9E6E5508698106156F2",
        "raw_size": 475_060,
        "raw_sha256": "4EA834A1B91DBBDFDD4B650FC11A89BDD05FC29EC741F9E6411D16A26994D37D",
    },
}

EXPECTED_ID_DIGESTS = {
    "special_shared_label": "AD86595696CC69D9B5DDEE8694EE23E0FD55578EDC33CE8523B99BEC1A3568D9",
    "place_name": "5FCC389EA627DF17D28A085D459006CCAA3C177FE7B9706434CAC8171698CF0B",
    "changed_pair": "FBF8BC4EBABBADD83BF9C353313F2A0C76F51B81893CE9D39CC48B18D156739C",
    "display_changed": "5D0C7E027388387B4B87AADC83835497F071BFFE7C69A715060EC9AC66DA8BF4",
    "reading_changed": "4F1E7F88A5FAF453DAE53000C0EEE517BE12476B6AF9D58B648D3F2E54842215",
    "msg_changed": "B11671C80C6D700091E9C4F839F838FBE8EFDA7EDB0775EE7082899E291602D1",
}
EXPECTED_TARGET_RECORD_DIGEST = "2A41B32A8109CFC18BDD724BF786F011C0C73E913CFD010228060762A50ADF85"
EXPECTED_CHANGED_PAIR_COUNT = 306
EXPECTED_DISPLAY_CHANGED_COUNT = 240
EXPECTED_READING_CHANGED_COUNT = 108
EXPECTED_CHANGED_TEXT_COUNT = 348
EXPECTED_ALREADY_CORRECT_COUNT = 988

SOURCE_TEXT_HASHES = {
    "shared_label_display": "7BF66398B2319D3F6D0C76BE2E93B3780A34F24715D5986557941F160775F3E6",
    "shared_label_reading": "C3583ABDBC6945165D1D97969751E4EBA44BACB45D033233FF1E14F3330DB14F",
    "shared_label_en_reading": "BED4BDB99F09AA114B337A41E48E51A2608C52A0D980D1F6385D5E2B7EC73D5B",
}
SOURCE_MAPPING_EXCEPTION_HASHES = {
    11_310: (
        "DA1DD7A965EA6B3A84455887AA7561BB7549B0A407BC305C12747A2184E0C49A",
        "0CE6FD602B19F989F17BE2C3B84C0D16DDA8FED9253226E4EE16FBEE8F3EDB01",
    ),
    11_311: (
        "7B188D2E8F110A889B9F149F2157E6C7307DAD60EDA96E609C04ED044DC6F915",
        "9DFAF9D00BB4BA051D6B59C86FE8DE243B9380AF9BF45FB23E589E4634B079A8",
    ),
}
MORA_MATCH_EXCEPTION = {
    "id": MORA_MATCH_EXCEPTION_ID,
    "ko": "오지야",
    "source_utf16le_sha256": {
        "jp_display": "2FEE34369ACE99085CD6C2845A5C34072BED9C37E570F838F439B4F9CDFC1D18",
        "jp_reading": "895B5AD424DC226B0DC2E09A1B3C61B04949F0CE755AAE0EA2ECAD4C408884AB",
        "en_display": "4987060A2A6A3826F06AFF7E07D5273F94A6DFD7DA27226CD75F85A02E81CB0B",
        "en_reading": "4987060A2A6A3826F06AFF7E07D5273F94A6DFD7DA27226CD75F85A02E81CB0B",
    },
}


class BuildError(RuntimeError):
    """Raised when an input, policy, audit, or output contract differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def utf16le_sha256(text: str) -> str:
    return sha256(text.encode("utf-16le"))


def canonical_id_sha256(values: Iterable[int]) -> str:
    payload = json.dumps(sorted(values), separators=(",", ":")).encode("ascii")
    return sha256(payload)


def canonical_record_sha256(records: Sequence[dict[str, Any]]) -> str:
    payload = json.dumps(
        records,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(payload)


def core_text(text: str) -> str:
    return text.strip()


def normalized_name(text: str) -> str:
    return "".join(text.split())


def preserve_outer_whitespace(before: str, replacement: str) -> str:
    if not replacement or replacement != replacement.strip() or "\x00" in replacement:
        raise BuildError(f"invalid replacement core: {replacement!r}")
    leading_count = len(before) - len(before.lstrip())
    trailing_count = len(before) - len(before.rstrip())
    leading = before[:leading_count]
    trailing = before[len(before) - trailing_count :] if trailing_count else ""
    return leading + replacement + trailing


def packed_raw_spec(packed: bytes) -> tuple[dict[str, int | str], Any, bytes]:
    header, raw = decompress_wrapper(packed)
    return (
        {
            "packed_size": len(packed),
            "packed_sha256": sha256(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
        },
        header,
        raw,
    )


def resolved_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _require_path_spec(
    path: Path,
    expected: dict[str, Any],
    label: str,
    *,
    require_packed_roundtrip: bool,
) -> tuple[bytes, Any, bytes]:
    try:
        packed = path.read_bytes()
    except OSError as exc:
        raise BuildError(f"cannot read pinned {label}: {path}") from exc
    actual, header, raw = packed_raw_spec(packed)
    pinned = {key: expected[key] for key in actual}
    if actual != pinned:
        raise BuildError(f"{label} packed/raw pin differs: {path}")
    if require_packed_roundtrip and recompress_wrapper(raw, header) != packed:
        raise BuildError(f"{label} wrapper is not a deterministic round trip: {path}")
    return packed, header, raw


def _require_message(
    path: Path,
    expected: dict[str, Any],
    label: str,
    *,
    require_packed_roundtrip: bool = False,
) -> tuple[bytes, Any, bytes, MessageTable]:
    packed, header, raw = _require_path_spec(
        path,
        expected,
        label,
        require_packed_roundtrip=require_packed_roundtrip,
    )
    table = parse_message_table(raw)
    if table.string_count != expected["string_count"]:
        raise BuildError(f"{label} string count differs: {table.string_count}")
    if rebuild_message_table(table, table.texts) != raw:
        raise BuildError(f"{label} unchanged message rebuild differs")
    return packed, header, raw, table


def _require_strdata(
    path: Path,
    expected: dict[str, Any],
    label: str,
    *,
    require_packed_roundtrip: bool = False,
) -> tuple[bytes, Any, bytes, StrdataArchive]:
    packed, header, raw = _require_path_spec(
        path,
        expected,
        label,
        require_packed_roundtrip=require_packed_roundtrip,
    )
    archive = parse_raw_strdata(raw)
    counts = tuple(block.slot_count for block in archive.blocks)
    if counts != STRDATA_SLOT_COUNTS:
        raise BuildError(f"{label} slot-count vector differs: {counts}")
    if rebuild_raw_strdata(archive) != raw:
        raise BuildError(f"{label} unchanged strdata rebuild differs")
    return packed, header, raw, archive


def load_policy() -> dict[str, Any]:
    try:
        payload = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"cannot load policy: {POLICY_PATH}") from exc
    if payload.get("schema") != POLICY_SCHEMA:
        raise BuildError("policy schema differs")
    if payload.get("policy_id") != "issue-124-all-place-names-v2":
        raise BuildError("policy id differs")
    if payload.get("source_profile") != {
        "release_id": "v0.95.0-event-dynamic-particle-candidate",
        "display_id_start": DISPLAY_START,
        "display_id_end": DISPLAY_END,
        "reading_offset": READING_OFFSET,
        "strdata_offset": STRDATA_OFFSET,
    }:
        raise BuildError("policy source profile differs")
    if payload.get("classifier") != {
        "total_pair_count": PAIR_COUNT,
        "shared_label_count": SHARED_LABEL_COUNT,
        "place_name_count": PLACE_NAME_COUNT,
        "place_name_id_sha256": EXPECTED_ID_DIGESTS["place_name"],
        "jp_en_mora_match_count": PLACE_NAME_COUNT - 1,
        "mora_match_exceptions": [MORA_MATCH_EXCEPTION],
        "multiword_place_count": MULTIWORD_PLACE_COUNT,
    }:
        raise BuildError("policy classifier contract differs")
    if payload.get("transcription") != {
        "english_role": "place_classifier_and_word_boundaries",
        "japanese_kana_role": "authoritative_reading",
        "tsu_hangul": "쓰",
        "write_same_value_to_display_and_reading": True,
        "target_record_sha256": EXPECTED_TARGET_RECORD_DIGEST,
    }:
        raise BuildError("policy transcription contract differs")
    if payload.get("expected_output") != {
        "changed_pair_count": EXPECTED_CHANGED_PAIR_COUNT,
        "already_correct_place_pair_count": EXPECTED_ALREADY_CORRECT_COUNT,
        "display_changed_count": EXPECTED_DISPLAY_CHANGED_COUNT,
        "reading_changed_count": EXPECTED_READING_CHANGED_COUNT,
        "changed_text_count": EXPECTED_CHANGED_TEXT_COUNT,
        "changed_pair_id_sha256": EXPECTED_ID_DIGESTS["changed_pair"],
        "display_changed_id_sha256": EXPECTED_ID_DIGESTS["display_changed"],
        "reading_changed_id_sha256": EXPECTED_ID_DIGESTS["reading_changed"],
        "changed_text_id_sha256": EXPECTED_ID_DIGESTS["msg_changed"],
    }:
        raise BuildError("policy output contract differs")
    distribution = payload.get("distribution_policy", {})
    if any(
        distribution.get(key) is not False
        for key in (
            "contains_commercial_source_text",
            "contains_complete_game_resource",
            "contains_switch_binary",
        )
    ):
        raise BuildError("policy distribution contract differs")
    return {"payload": payload, "sha256": sha256(POLICY_PATH.read_bytes())}


def _require_id_vector(label: str, values: Iterable[int], expected_count: int) -> tuple[int, ...]:
    vector = tuple(sorted(values))
    if len(vector) != expected_count:
        raise BuildError(f"{label} count differs: {len(vector)}")
    if canonical_id_sha256(vector) != EXPECTED_ID_DIGESTS[label]:
        raise BuildError(f"{label} id vector differs")
    return vector


def _source_hash(text: str) -> str:
    return utf16le_sha256(core_text(text))


def _require_source_pairing(jp_msg: Sequence[str], jp_str: Sequence[str]) -> None:
    mismatches: set[int] = set()
    for identifier in range(DISPLAY_START, DISPLAY_END + 1):
        display_slot = identifier - STRDATA_OFFSET
        reading_slot = identifier + READING_OFFSET - STRDATA_OFFSET
        if (
            jp_msg[identifier] != jp_str[display_slot]
            or jp_msg[identifier + READING_OFFSET] != jp_str[reading_slot]
        ):
            mismatches.add(identifier)
    if mismatches != set(SOURCE_MAPPING_EXCEPTIONS):
        raise BuildError(f"JP msgdata/strdata source exceptions differ: {sorted(mismatches)}")
    for identifier, (display_hash, reading_hash) in SOURCE_MAPPING_EXCEPTION_HASHES.items():
        if _source_hash(jp_msg[identifier]) != display_hash:
            raise BuildError(f"exception display source differs: {identifier}")
        if _source_hash(jp_msg[identifier + READING_OFFSET]) != reading_hash:
            raise BuildError(f"exception reading source differs: {identifier}")
        if _source_hash(jp_str[identifier - STRDATA_OFFSET]) != SOURCE_TEXT_HASHES["shared_label_display"]:
            raise BuildError(f"exception strdata display must remain the shared label: {identifier}")
        if _source_hash(jp_str[identifier + READING_OFFSET - STRDATA_OFFSET]) != SOURCE_TEXT_HASHES["shared_label_reading"]:
            raise BuildError(f"exception strdata reading must remain the shared label: {identifier}")


PLACE_MORA_TO_HANGUL = dict(MORA_TO_HANGUL)
PLACE_MORA_TO_HANGUL["tsu"] = "쓰"


def _place_moras_to_hangul(keys: Sequence[str]) -> str:
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
            syllable = PLACE_MORA_TO_HANGUL.get(key)
        if syllable is None:
            raise BuildError(f"unsupported place-name mora: {key!r}")
        output += syllable
        spoken_index += 1
    if not output:
        raise BuildError("empty place-name transcription")
    return output


def _unique_word_partition(
    identifier: int,
    full: Sequence[Mora],
    english_words: Sequence[Sequence[str]],
) -> tuple[tuple[Mora, ...], ...]:
    solutions: list[tuple[tuple[Mora, ...], ...]] = []

    def visit(word_index: int, start: int, parts: tuple[tuple[Mora, ...], ...]) -> None:
        if word_index == len(english_words):
            if start == len(full):
                solutions.append(parts)
            return
        remaining_words = len(english_words) - word_index - 1
        for end in range(start + 1, len(full) - remaining_words + 1):
            part = tuple(full[start:end])
            if mora_equal([mora.key for mora in part], english_words[word_index]):
                visit(word_index + 1, end, parts + (part,))

    visit(0, 0, ())
    if len(solutions) != 1:
        raise BuildError(
            f"place-name word partition is not unique at id {identifier}: {len(solutions)}"
        )
    return solutions[0]


def _require_mora_exception_sources(
    identifier: int,
    jp_msg: Sequence[str],
    en_msg: Sequence[str],
) -> None:
    expected = MORA_MATCH_EXCEPTION["source_utf16le_sha256"]
    actual = {
        "jp_display": _source_hash(jp_msg[identifier]),
        "jp_reading": _source_hash(jp_msg[identifier + READING_OFFSET]),
        "en_display": _source_hash(en_msg[identifier]),
        "en_reading": _source_hash(en_msg[identifier + READING_OFFSET]),
    }
    if actual != expected:
        raise BuildError(f"mora-match exception source differs at id {identifier}")


def derive_targets(
    jp_msg: Sequence[str],
    en_msg: Sequence[str],
    _policy: dict[str, Any],
) -> tuple[dict[int, dict[str, Any]], dict[str, tuple[int, ...]], dict[str, int]]:
    shared: set[int] = set()
    targets: dict[int, dict[str, Any]] = {}
    mora_match_count = 0
    mora_exception_ids: list[int] = []
    multiword_count = 0

    for identifier in range(DISPLAY_START, DISPLAY_END + 1):
        reading_id = identifier + READING_OFFSET
        jp_is_shared = (
            _source_hash(jp_msg[identifier]) == SOURCE_TEXT_HASHES["shared_label_display"]
            and _source_hash(jp_msg[reading_id]) == SOURCE_TEXT_HASHES["shared_label_reading"]
        )
        en_is_shared = (
            _source_hash(en_msg[reading_id]) == SOURCE_TEXT_HASHES["shared_label_en_reading"]
        )
        if en_is_shared:
            if not jp_is_shared:
                raise BuildError(f"shared-label JP/EN classification differs at id {identifier}")
            shared.add(identifier)
            continue
        if jp_is_shared:
            raise BuildError(f"place-name JP/EN classification differs at id {identifier}")

        japanese_reading = core_text(jp_msg[reading_id])
        english_reading = core_text(en_msg[reading_id])
        try:
            full = tuple(kana_moras(japanese_reading))
            english_text_words = english_reading.split()
            english_words = tuple(tuple(romaji_moras(word)) for word in english_text_words)
        except OfficerNameError as exc:
            raise BuildError(f"unsupported aligned reading at id {identifier}: {exc}") from exc
        if not full or not english_words:
            raise BuildError(f"empty aligned reading at id {identifier}")

        full_keys = [mora.key for mora in full]
        flattened_english = [key for word in english_words for key in word]
        aligned = mora_equal(full_keys, flattened_english)
        if aligned:
            mora_match_count += 1
        else:
            if identifier != MORA_MATCH_EXCEPTION_ID:
                raise BuildError(f"JP/EN mora sequence differs at id {identifier}")
            _require_mora_exception_sources(identifier, jp_msg, en_msg)
            mora_exception_ids.append(identifier)

        if len(english_words) == 1:
            parts = (full,)
        else:
            if not aligned:
                raise BuildError(f"multiword mora exception is unsupported at id {identifier}")
            parts = _unique_word_partition(identifier, full, english_words)
            multiword_count += 1
        korean = " ".join(
            _place_moras_to_hangul([mora.key for mora in part]) for part in parts
        )
        if identifier == MORA_MATCH_EXCEPTION_ID and korean != MORA_MATCH_EXCEPTION["ko"]:
            raise BuildError(f"mora exception Korean output differs at id {identifier}")
        targets[identifier] = {
            "display": korean,
            "reading": korean,
            "reason": "full_place_transcription",
            "word_count": len(english_words),
            "jp_en_mora_match": aligned,
        }

    shared_vector = _require_id_vector("special_shared_label", shared, SHARED_LABEL_COUNT)
    place_vector = _require_id_vector("place_name", targets, PLACE_NAME_COUNT)
    if mora_match_count != PLACE_NAME_COUNT - 1:
        raise BuildError(f"JP/EN mora match count differs: {mora_match_count}")
    if mora_exception_ids != [MORA_MATCH_EXCEPTION_ID]:
        raise BuildError(f"JP/EN mora exception vector differs: {mora_exception_ids}")
    if multiword_count != MULTIWORD_PLACE_COUNT:
        raise BuildError(f"multiword place count differs: {multiword_count}")
    records = [{"id": identifier, "ko": targets[identifier]["display"]} for identifier in place_vector]
    if canonical_record_sha256(records) != EXPECTED_TARGET_RECORD_DIGEST:
        raise BuildError("complete place-name target record vector differs")
    return (
        targets,
        {"special_shared_label": shared_vector, "place_name": place_vector},
        {
            "jp_en_mora_match_count": mora_match_count,
            "jp_en_mora_exception_count": len(mora_exception_ids),
            "multiword_place_count": multiword_count,
        },
    )


def _require_final(candidate: bytes, resource: Path) -> tuple[Any, bytes]:
    actual, header, raw = packed_raw_spec(candidate)
    if actual != FINAL_SPECS[resource]:
        raise BuildError(f"output packed/raw pin differs: {resource.as_posix()}: {actual}")
    return header, raw


def _audit_payload(
    current_msg: Sequence[str],
    final_msg: Sequence[str],
    current_str: Sequence[str],
    jp_msg: Sequence[str],
    en_msg: Sequence[str],
    targets: dict[int, dict[str, Any]],
    vectors: dict[str, tuple[int, ...]],
) -> dict[str, Any]:
    shared = set(vectors["special_shared_label"])
    rows: list[dict[str, Any]] = []
    for identifier in range(DISPLAY_START, DISPLAY_END + 1):
        reading_id = identifier + READING_OFFSET
        exception = identifier in SOURCE_MAPPING_EXCEPTIONS
        display_slot = identifier - STRDATA_OFFSET
        reading_slot = reading_id - STRDATA_OFFSET
        target = targets.get(identifier)
        rows.append(
            {
                "id": identifier,
                "reading_id": reading_id,
                "classification": (
                    "special_shared_label" if identifier in shared else "full_place_transcription"
                ),
                "action": "preserve" if target is None else "transcribe_from_jp_kana",
                "msgdata_changed": (
                    current_msg[identifier] != final_msg[identifier]
                    or current_msg[reading_id] != final_msg[reading_id]
                ),
                "display_changed": current_msg[identifier] != final_msg[identifier],
                "reading_changed": current_msg[reading_id] != final_msg[reading_id],
                "english_word_count": None if target is None else target["word_count"],
                "jp_en_mora_match": None if target is None else target["jp_en_mora_match"],
                "strdata_action": "preserve_read_only",
                "source_mapping_exception": exception,
                "strdata_display_slot": None if exception else display_slot,
                "strdata_reading_slot": None if exception else reading_slot,
                "before_ko": {
                    "display": current_msg[identifier],
                    "reading": current_msg[reading_id],
                    "strdata_display": None if exception else current_str[display_slot],
                    "strdata_reading": None if exception else current_str[reading_slot],
                },
                "after_ko": {
                    "display": final_msg[identifier],
                    "reading": final_msg[reading_id],
                    "strdata_display": None if exception else current_str[display_slot],
                    "strdata_reading": None if exception else current_str[reading_slot],
                },
                "source_evidence_utf16le_sha256": {
                    "jp_display": _source_hash(jp_msg[identifier]),
                    "jp_reading": _source_hash(jp_msg[reading_id]),
                    "en_display": _source_hash(en_msg[identifier]),
                    "en_reading": _source_hash(en_msg[reading_id]),
                },
            }
        )
    counts = Counter(row["classification"] for row in rows)
    expected_counts = {
        "special_shared_label": SHARED_LABEL_COUNT,
        "full_place_transcription": PLACE_NAME_COUNT,
    }
    if dict(sorted(counts.items())) != dict(sorted(expected_counts.items())):
        raise BuildError(f"audit classification counts differ: {dict(counts)}")
    return {
        "schema": AUDIT_SCHEMA,
        "issue": 124,
        "status": "PASS",
        "display_range": [DISPLAY_START, DISPLAY_END],
        "reading_offset": READING_OFFSET,
        "strdata_offset": STRDATA_OFFSET,
        "transcription_policy": {
            "english_role": "place_classifier_and_word_boundaries",
            "japanese_kana_role": "authoritative_reading",
            "display_and_reading_share_target": True,
        },
        "strdata_policy": "read_only_shared_translation_surface",
        "row_count": len(rows),
        "classification_counts": dict(sorted(counts.items())),
        "rows": rows,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "contains_switch_binary": False,
        },
    }


def build_candidate(
    input_root: Path,
    jp_reference_root: Path,
    en_reference_msgdata: Path,
    output_root: Path,
) -> dict[str, Any]:
    input_root = input_root.resolve()
    jp_reference_root = jp_reference_root.resolve()
    en_reference_msgdata = en_reference_msgdata.resolve()
    output_root = output_root.resolve()
    if resolved_under(output_root, input_root) or resolved_under(input_root, output_root):
        raise BuildError("output root must not overlap the input root")
    if resolved_under(output_root, jp_reference_root) or resolved_under(jp_reference_root, output_root):
        raise BuildError("output root must not overlap the JP reference root")
    if resolved_under(en_reference_msgdata, output_root):
        raise BuildError("output root must not contain the EN reference file")
    if resolved_under(output_root, DEFAULT_STEAM_ROOT):
        raise BuildError("output root must not be inside the Steam installation")
    if output_root.exists() and any(output_root.iterdir()):
        raise BuildError(f"output root is not empty: {output_root}")

    policy = load_policy()
    _input_msg_packed, input_msg_header, _input_msg_raw, input_msg = _require_message(
        input_root / MSG_DATA,
        INPUT_SPECS[MSG_DATA],
        "input msgdata",
        require_packed_roundtrip=True,
    )
    _input_str_packed, _input_str_header, _input_str_raw, input_str = _require_strdata(
        input_root / STR_DATA,
        INPUT_SPECS[STR_DATA],
        "input strdata",
        require_packed_roundtrip=True,
    )
    _jp_msg_packed, _jp_msg_header, _jp_msg_raw, jp_msg = _require_message(
        jp_reference_root / MSG_DATA,
        JP_REFERENCE_SPECS[MSG_DATA],
        "JP reference msgdata",
    )
    _jp_str_packed, _jp_str_header, _jp_str_raw, jp_str = _require_strdata(
        jp_reference_root / STR_DATA,
        JP_REFERENCE_SPECS[STR_DATA],
        "JP reference strdata",
    )
    _en_packed, _en_header, _en_raw, en_msg = _require_message(
        en_reference_msgdata,
        EN_REFERENCE_SPEC,
        "EN reference msgdata",
    )

    current_msg = input_msg.texts
    current_str = input_str.blocks[0].texts
    _require_source_pairing(jp_msg.texts, jp_str.blocks[0].texts)
    targets, vectors, derivation = derive_targets(jp_msg.texts, en_msg.texts, policy)

    final_msg = list(current_msg)
    for identifier, target in sorted(targets.items()):
        reading_id = identifier + READING_OFFSET
        final_msg[identifier] = preserve_outer_whitespace(final_msg[identifier], target["display"])
        final_msg[reading_id] = preserve_outer_whitespace(final_msg[reading_id], target["reading"])

    msg_raw = rebuild_message_table(input_msg, final_msg)
    msg_candidate = recompress_wrapper(msg_raw, input_msg_header)
    msg_output_header, msg_decoded = _require_final(msg_candidate, MSG_DATA)
    if msg_output_header.prefix != input_msg_header.prefix or msg_decoded != msg_raw:
        raise BuildError("msgdata output wrapper round trip differs")
    msg_check = parse_message_table(msg_decoded)
    if msg_check.texts != tuple(final_msg):
        raise BuildError("msgdata output text verification differs")

    msg_changed = tuple(
        identifier
        for identifier, (before, after) in enumerate(zip(current_msg, msg_check.texts, strict=True))
        if before != after
    )
    if len(msg_changed) != EXPECTED_CHANGED_TEXT_COUNT:
        raise BuildError(f"msgdata changed count differs: {len(msg_changed)}")
    if canonical_id_sha256(msg_changed) != EXPECTED_ID_DIGESTS["msg_changed"]:
        raise BuildError("msgdata changed id vector differs")
    allowed_msg = set(vectors["place_name"]) | {
        identifier + READING_OFFSET for identifier in vectors["place_name"]
    }
    if not set(msg_changed) <= allowed_msg:
        raise BuildError("msgdata changed outside the complete place-name coordinates")

    display_changed = tuple(
        identifier for identifier in vectors["place_name"] if current_msg[identifier] != final_msg[identifier]
    )
    reading_changed = tuple(
        identifier
        for identifier in vectors["place_name"]
        if current_msg[identifier + READING_OFFSET] != final_msg[identifier + READING_OFFSET]
    )
    changed_pairs = tuple(sorted(set(display_changed) | set(reading_changed)))
    _require_id_vector("display_changed", display_changed, EXPECTED_DISPLAY_CHANGED_COUNT)
    _require_id_vector("reading_changed", reading_changed, EXPECTED_READING_CHANGED_COUNT)
    _require_id_vector("changed_pair", changed_pairs, EXPECTED_CHANGED_PAIR_COUNT)
    if PLACE_NAME_COUNT - len(changed_pairs) != EXPECTED_ALREADY_CORRECT_COUNT:
        raise BuildError("already-correct place count differs")

    final_mismatches = {
        identifier
        for identifier in vectors["place_name"]
        if normalized_name(final_msg[identifier])
        != normalized_name(final_msg[identifier + READING_OFFSET])
    }
    if final_mismatches:
        raise BuildError(f"final place display/reading mismatches remain: {sorted(final_mismatches)}")

    audit = _audit_payload(
        current_msg,
        msg_check.texts,
        current_str,
        jp_msg.texts,
        en_msg.texts,
        targets,
        vectors,
    )
    audit_blob = (json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    report = {
        "schema": SCHEMA,
        "issue": 124,
        "status": "PASS",
        "policy_file": POLICY_PATH.name,
        "policy_sha256": policy["sha256"],
        "coverage": {
            "total_pair_count": PAIR_COUNT,
            "special_shared_label_count": SHARED_LABEL_COUNT,
            "actual_place_name_count": PLACE_NAME_COUNT,
            "target_pair_count": len(targets),
            "changed_pair_count": len(changed_pairs),
            "already_correct_place_pair_count": PLACE_NAME_COUNT - len(changed_pairs),
            "display_changed_count": len(display_changed),
            "reading_changed_count": len(reading_changed),
            "source_pair_match_count": PAIR_COUNT - len(SOURCE_MAPPING_EXCEPTIONS),
            "source_mapping_exception_ids": sorted(SOURCE_MAPPING_EXCEPTIONS),
            **derivation,
        },
        "target_reason_counts": dict(
            sorted(Counter(target["reason"] for target in targets.values()).items())
        ),
        "resources": [
            {
                "resource": MSG_DATA.as_posix(),
                "changed_text_count": len(msg_changed),
                "changed_id_sha256": canonical_id_sha256(msg_changed),
                "input": INPUT_SPECS[MSG_DATA],
                "target": FINAL_SPECS[MSG_DATA],
                "all_other_texts_unchanged": True,
            },
            {
                "resource": STR_DATA.as_posix(),
                "role": "read_only_dependency",
                "changed_text_count": 0,
                "input": INPUT_SPECS[STR_DATA],
                "target": INPUT_SPECS[STR_DATA],
                "output_emitted": False,
                "shared_translation_surface_preserved": True,
            },
        ],
        "changed_resource_count": 1,
        "output_resource_count": 1,
        "changed_text_count": len(msg_changed),
        "audit_file": AUDIT_NAME,
        "audit_sha256": sha256(audit_blob),
        "commercial_source_text_embedded": False,
        "steam_written": False,
    }

    output_root.mkdir(parents=True, exist_ok=True)
    destination = output_root / MSG_DATA
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(msg_candidate)
    (output_root / AUDIT_NAME).write_bytes(audit_blob)
    validation_blob = (
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    (output_root / VALIDATION_NAME).write_bytes(validation_blob)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--jp-reference-root", type=Path, required=True)
    parser.add_argument("--en-reference-msgdata", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_candidate(
            args.input_root,
            args.jp_reference_root,
            args.en_reference_msgdata,
            args.output_root,
        )
    except (BuildError, MessageTableError, StrdataFormatError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
