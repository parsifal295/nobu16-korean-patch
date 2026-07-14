#!/usr/bin/env python3
"""Generate a private Korean officer-name catalog from aligned game tables.

The game supplies stable SC/JP/EN ids while the English table supplies name
readings and word order.  An optional, privately cached Japanese reading page
can correct spelling and alternate-name errors in the English localization.
Only the resulting private catalog is written; the official source strings are
later removed by ``export_common_message_overlay.py`` before distribution.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Sequence


PRIVATE_SCHEMA = "nobu16.kr.translation.v1"
RESOURCE_NAME = "msgev.bin"
OFFICER_SLOT_LIMIT = 2400
EXPECTED_OFFICER_COUNT = 2207
CUSTOM_ROMAJI = str.maketrans({"ª": "o", "¥": "O", "¨": "u"})
TITLE_WORDS = frozenset(("Lady", "Hime"))
DUMMY_BY_LANGUAGE = {"SC": "dummy", "JP": "ダミー", "EN": "dummy"}
ALTERNATE_SURNAME_READING_IDS = frozenset((45,))
MANUAL_OVERRIDES: dict[int, dict[str, Any]] = {
    # Confirmed name corrections are pinned to the UTF-16LE SHA-256 of every
    # aligned source string.  This keeps official source text out of the public
    # repository while an id shift or a different data revision still fails
    # closed instead of applying the Korean name to the wrong officer.
    162: {
        "source_utf16le_sha256": {
            "SC": "26D1E882F844754234204C6DB71441E0DA9F993BD10D3B6444CA56ADA25B5C12",
            "JP": "5CE98E35098A46A20944695CBE20FDC156B0A4B76B9CFC2EAA774DBC341FC2AA",
            "EN": "290522998EEF511024DF75963C32FC49DB862EBEA6A1DBB1C24D192358800F04",
        },
        "ko": "안요지 우지타네",
    },
    231: {
        "source_utf16le_sha256": {
            "SC": "A0FF66786B28DD9036573078F9BDC05FE2E22E02B7621CABA4C84472FCDF0476",
            "JP": "7033A719802DD1EAD70BC843F08280A56E831D0DA844A0ED9A2493DC51BEE0E2",
            "EN": "EFC1A344E48C65359A0694E0452F4E3BFE36C83F88FAD4BFF5A2F6A93F77A4BB",
        },
        "ko": "이즈모노 오쿠니",
    },
    516: {
        "source_utf16le_sha256": {
            "SC": "89449A88D79332F46DE12D518C5D2D098A27C16DA63EE0928FD5D61F6CB264C2",
            "JP": "0FA995CC81406F6D4BE096E01F6861CA2DBBB48D76E4CDD677EB21461E7F593F",
            "EN": "F4F25527B7D9FA5DBFDD85C2C5BF59E6DA14313424A00301F9FB0C024C4B5F37",
        },
        "ko": "오카모토 겐이츠",
    },
    # The EN localization splits one mononym into two pseudo-words.  It is a
    # single historical name, not a surname/given-name pair.
    843: {
        "source_utf16le_sha256": {
            "SC": "47FDCA41A77C5919987B500502B74F21B119B916500EC7ADF1E2DE811AEA5416",
            "JP": "47FDCA41A77C5919987B500502B74F21B119B916500EC7ADF1E2DE811AEA5416",
            "EN": "6CDB4AA898158792D423FABF75C5FF358209D13CB4FDFA5064ECD1BC421DC3B9",
        },
        "ko": "고마츠",
    },
    1179: {
        "source_utf16le_sha256": {
            "SC": "9A3BCB8FDFCE14A1CD146EEC59BB9BA3775E28E1ABFBE378B9BE43B3D0CDF329",
            "JP": "2BAF0BAAF691256710659875994B1DE5E43492FE36762AFFD4322E31F1C7C9CD",
            "EN": "AAA901FA736EDC10D27DFBA239F7C0425CFC1ACE53764F2435E648C3161A0C61",
        },
        "ko": "조슌인",
    },
    1302: {
        "source_utf16le_sha256": {
            "SC": "FD30EDC2A21FFF3B418AF7CF2DA39A7CDCB1783CB7CE946CBA80680BDCC2DAD7",
            "JP": "F4992B02919615843D21EE0CAE65A8D04B8A686C5DAB2D750E8824F5AF86D519",
            "EN": "EB8CC352CB68B2933665F46BFD071709A3A52740F154C6CD3964297923C46934",
        },
        "ko": "치지와 미게루",
    },
    1584: {
        "source_utf16le_sha256": {
            "SC": "4788768F37EC801BD78BBA5FF456A22368FC29D680010B07907E5504BA3B8ED7",
            "JP": "F66431DDBA42A1692566AC508271CD847126173CBDDEF4A33C8183A6126BF2CB",
            "EN": "DE958ABDFD7943A6BD249F96F94B293CBEF11BC59E66AA6F7497535B8A1E0B6B",
        },
        "ko": "네고로 긴세키사이",
    },
    1666: {
        "source_utf16le_sha256": {
            "SC": "F98518D35CC179D959703DDED0DB5641138F707FEC5D1040A25D37619FE46EFD",
            "JP": "6EB3CFF727ED9CE45AA57135252369DE9D2282CDEEE9B8E1DB0FE5DBDC193A4E",
            "EN": "03B0A77882108ED593581B64C7535E541232F1F516A3FB6C837C2BD855431A23",
        },
        "ko": "반 단에몬",
    },
    1674: {
        "source_utf16le_sha256": {
            "SC": "58C18A628C36ADE7E510795355F83F6BC471CA4CDB10C76ECD0CA59CE5C10104",
            "JP": "0D7A4450FAAD7A66EC08F19ECA3AF69020C30058DE6024747D64F50F4E800F56",
            "EN": "A2FB974D5B35FA429BF8461C86D49388E0AF863B0F1A8789E58C08DD27917029",
        },
        "ko": "히코츠루",
    },
    1739: {
        "source_utf16le_sha256": {
            "SC": "931515DB718832607B0736A5F7BC6954B3225924A126FBC7F6D9484ED656107D",
            "JP": "931515DB718832607B0736A5F7BC6954B3225924A126FBC7F6D9484ED656107D",
            "EN": "ED98BE49C31E01974BFBA55A50435D0CC4F3EAEBD27650AEDF637D81D7CDA2B5",
        },
        "ko": "호조 겐안",
    },
    1752: {
        "source_utf16le_sha256": {
            "SC": "ADFD31C0C1869881F3B5599DE9A0EFF9A3A55A5D40F811C2B0FC77568F731895",
            "JP": "CD536F30DA726B430B8CBAF2CEE3D3F5F40D73EB9B6B8A35858D4038AC438A8A",
            "EN": "FFA2B7B1FC9FAC55A2E964BB471417A04E6EB28946ABE8E86CBD257772741351",
        },
        "ko": "호조인 인에이",
    },
    1831: {
        "source_utf16le_sha256": {
            "SC": "F11979FD9EF3B7E13134BC34D75EE4D3859EE5EBECFFBFF0E65F6D62FD0D3410",
            "JP": "F11979FD9EF3B7E13134BC34D75EE4D3859EE5EBECFFBFF0E65F6D62FD0D3410",
            "EN": "71D412456DF45739A3B7D13281A1F32024E5073B7109E894BAB3D91B7CEDB676",
        },
        "ko": "마에다 겐이",
    },
    2134: {
        "source_utf16le_sha256": {
            "SC": "E8CF56EE524F987C996A8258A4090068C42BAEA25534346BC980842CB53D905D",
            "JP": "EBEFA1F7530A01FADF4E5767B88AB09872F4A9A78F0D0D13A9DFE0C6B9434EDA",
            "EN": "2C2F396EC179218EB6B3EBEEF25293F4FD4C359847782BAB911DB7E348CCC7C0",
        },
        "ko": "유지 사다토키",
    },
}


class OfficerNameError(ValueError):
    """Raised when aligned name inputs or a generated name are invalid."""


@dataclass(frozen=True)
class Mora:
    key: str
    source_start: int
    source_end: int


@dataclass(frozen=True)
class ReadingMatch:
    reading: str | None
    method: str


NAME_VARIANTS = str.maketrans(
    {
        "國": "国",
        "萬": "万",
        "德": "徳",
        "廣": "広",
        "惠": "恵",
        "眞": "真",
        "實": "実",
        "淸": "清",
        "龍": "竜",
        "齋": "斎",
        "齊": "斉",
        "邊": "辺",
        "邉": "辺",
        "濱": "浜",
        "澤": "沢",
        "髙": "高",
        "﨑": "崎",
        "嶋": "島",
        "冨": "富",
        "神": "神",
        "福": "福",
        "舊": "旧",
        "會": "会",
        "壽": "寿",
        "爲": "為",
        "彥": "彦",
        "將": "将",
        "從": "従",
        "處": "処",
        "蘆": "芦",
        "穗": "穂",
        "瀨": "瀬",
        "增": "増",
        "瀧": "滝",
        "曆": "暦",
    }
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_jsonl(path: Path) -> list[str]:
    rows: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise OfficerNameError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
        if not isinstance(row, dict) or set(row) != {"id", "text", "translation"}:
            raise OfficerNameError(f"unexpected JSONL row shape at {path}:{line_number}")
        if row["id"] != len(rows) or not isinstance(row["text"], str):
            raise OfficerNameError(f"unaligned id/text at {path}:{line_number}")
        rows.append(row["text"])
    if len(rows) < OFFICER_SLOT_LIMIT:
        raise OfficerNameError(f"{path} has only {len(rows)} rows")
    return rows


def pinned_manual_override(
    entry_id: int,
    sc_name: str,
    jp_name: str,
    en_name: str,
) -> str | None:
    override = MANUAL_OVERRIDES.get(entry_id)
    if override is None:
        return None
    expected = override.get("source_utf16le_sha256")
    languages = ("SC", "JP", "EN")
    if (
        not isinstance(expected, dict)
        or set(expected) != set(languages)
        or any(
            not isinstance(expected.get(language), str)
            or re.fullmatch(r"[0-9A-F]{64}", expected[language]) is None
            for language in languages
        )
    ):
        raise OfficerNameError(f"manual override source pin is invalid at id {entry_id}")
    actual = {"SC": sc_name, "JP": jp_name, "EN": en_name}
    actual_pins = {
        language: hashlib.sha256(actual[language].encode("utf-16le"))
        .hexdigest()
        .upper()
        for language in languages
    }
    if expected != actual_pins:
        mismatched = ", ".join(
            language
            for language in languages
            if expected[language] != actual_pins[language]
        )
        raise OfficerNameError(
            f"manual override source pin differs at id {entry_id}: {mismatched}"
        )
    korean = override.get("ko")
    if not isinstance(korean, str) or not korean:
        raise OfficerNameError(f"manual override Korean name is invalid at id {entry_id}")
    return korean


class ReadingTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_row = False
        self.in_cell = False
        self.cells: list[list[str]] = []
        self.rows: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self.in_row = True
            self.cells = []
        elif tag == "td" and self.in_row:
            self.in_cell = True
            self.cells.append([])

    def handle_endtag(self, tag: str) -> None:
        if tag == "td":
            self.in_cell = False
        elif tag == "tr" and self.in_row:
            if len(self.cells) >= 2:
                name = html.unescape("".join(self.cells[0])).strip()
                reading = html.unescape("".join(self.cells[1])).strip()
                if name and reading and all(is_kana(character) for character in reading):
                    self.rows.append((name, reading))
            self.in_row = False
            self.in_cell = False
            self.cells = []

    def handle_data(self, data: str) -> None:
        if self.in_row and self.in_cell and self.cells:
            self.cells[-1].append(data)


def is_kana(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x3040 <= codepoint <= 0x309F
        or 0x30A0 <= codepoint <= 0x30FF
        or character in "ー・"
    )


def normalize_japanese_name(value: str) -> str:
    return unicodedata.normalize("NFKC", value).translate(NAME_VARIANTS)


def parse_reading_table(path: Path) -> tuple[dict[str, tuple[str, ...]], int]:
    parser = ReadingTableParser()
    parser.feed(path.read_text(encoding="utf-8-sig", errors="strict"))
    readings: dict[str, set[str]] = {}
    for name, reading in parser.rows:
        readings.setdefault(normalize_japanese_name(name), set()).add(reading)
    return {name: tuple(sorted(values)) for name, values in readings.items()}, len(parser.rows)


def find_reading(japanese_name: str, readings: dict[str, tuple[str, ...]]) -> ReadingMatch:
    values = readings.get(normalize_japanese_name(japanese_name), ())
    if len(values) == 1:
        return ReadingMatch(values[0], "jp_name")
    if len(values) > 1:
        return ReadingMatch(None, "ambiguous_jp_name")
    return ReadingMatch(None, "missing_jp_name")


def to_hiragana(text: str) -> str:
    result: list[str] = []
    for character in unicodedata.normalize("NFKC", text):
        codepoint = ord(character)
        if 0x30A1 <= codepoint <= 0x30F6:
            result.append(chr(codepoint - 0x60))
        else:
            result.append(character)
    return "".join(result)


KANA_KEYS = (
    "きゃ", "きゅ", "きょ", "ぎゃ", "ぎゅ", "ぎょ",
    "しゃ", "しゅ", "しょ", "じゃ", "じゅ", "じょ", "ぢゃ", "ぢゅ", "ぢょ",
    "ちゃ", "ちゅ", "ちょ", "にゃ", "にゅ", "にょ",
    "ひゃ", "ひゅ", "ひょ", "びゃ", "びゅ", "びょ",
    "ぴゃ", "ぴゅ", "ぴょ", "みゃ", "みゅ", "みょ",
    "りゃ", "りゅ", "りょ", "しぇ", "じぇ", "ちぇ",
    "てぃ", "でぃ", "とぅ", "どぅ", "ふぁ", "ふぃ", "ふぇ", "ふぉ",
    "うぃ", "うぇ", "うぉ", "いぇ",
    "あ", "い", "う", "え", "お",
    "か", "き", "く", "け", "こ", "が", "ぎ", "ぐ", "げ", "ご",
    "さ", "し", "す", "せ", "そ", "ざ", "じ", "ず", "ぜ", "ぞ",
    "た", "ち", "つ", "て", "と", "だ", "ぢ", "づ", "で", "ど",
    "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "へ", "ほ",
    "ば", "び", "ぶ", "べ", "ぼ", "ぱ", "ぴ", "ぷ", "ぺ", "ぽ",
    "ま", "み", "む", "め", "も", "や", "ゆ", "よ",
    "ら", "り", "る", "れ", "ろ", "わ", "ゐ", "ゑ", "を", "ゔ",
)


KANA_TO_ROMAJI = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
    "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
    "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
    "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
    "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
    "わ": "wa", "ゐ": "i", "ゑ": "e", "を": "o", "ゔ": "vu",
    "きゃ": "kya", "きゅ": "kyu", "きょ": "kyo",
    "ぎゃ": "gya", "ぎゅ": "gyu", "ぎょ": "gyo",
    "しゃ": "sha", "しゅ": "shu", "しょ": "sho",
    "じゃ": "ja", "じゅ": "ju", "じょ": "jo",
    "ぢゃ": "ja", "ぢゅ": "ju", "ぢょ": "jo",
    "ちゃ": "cha", "ちゅ": "chu", "ちょ": "cho",
    "にゃ": "nya", "にゅ": "nyu", "にょ": "nyo",
    "ひゃ": "hya", "ひゅ": "hyu", "ひょ": "hyo",
    "びゃ": "bya", "びゅ": "byu", "びょ": "byo",
    "ぴゃ": "pya", "ぴゅ": "pyu", "ぴょ": "pyo",
    "みゃ": "mya", "みゅ": "myu", "みょ": "myo",
    "りゃ": "rya", "りゅ": "ryu", "りょ": "ryo",
    "しぇ": "she", "じぇ": "je", "ちぇ": "che",
    "てぃ": "ti", "でぃ": "di", "とぅ": "tu", "どぅ": "du",
    "ふぁ": "fa", "ふぃ": "fi", "ふぇ": "fe", "ふぉ": "fo",
    "うぃ": "wi", "うぇ": "we", "うぉ": "wo", "いぇ": "ye",
}


ROMAJI_KEYS = tuple(sorted(set(KANA_TO_ROMAJI.values()), key=lambda value: (-len(value), value)))


def vowel_of(mora: str) -> str | None:
    for character in reversed(mora):
        if character in "aeiou":
            return character
    return None


def kana_moras(text: str) -> list[Mora]:
    source = to_hiragana(text)
    raw: list[Mora] = []
    index = 0
    while index < len(source):
        character = source[index]
        if character == "っ":
            raw.append(Mora("Q", index, index + 1))
            index += 1
            continue
        if character == "ん":
            raw.append(Mora("n", index, index + 1))
            index += 1
            continue
        if character == "ー":
            raw.append(Mora("LONG", index, index + 1))
            index += 1
            continue
        matched = next((key for key in KANA_KEYS if source.startswith(key, index)), None)
        if matched is None:
            raise OfficerNameError(f"unsupported kana sequence {source[index:]!r} in {text!r}")
        raw.append(Mora(KANA_TO_ROMAJI[matched], index, index + len(matched)))
        index += len(matched)

    normalized: list[Mora] = []
    previous_vowel: str | None = None
    just_skipped_long = False
    for mora in raw:
        if mora.key == "LONG":
            if normalized:
                previous = normalized[-1]
                normalized[-1] = Mora(previous.key, previous.source_start, mora.source_end)
            just_skipped_long = True
            continue
        if (
            mora.key in ("u", "o")
            and not just_skipped_long
            and ((mora.key == "u" and previous_vowel in ("o", "u")) or (mora.key == "o" and previous_vowel == "o"))
        ):
            if normalized:
                previous = normalized[-1]
                normalized[-1] = Mora(previous.key, previous.source_start, mora.source_end)
            just_skipped_long = True
            continue
        normalized.append(mora)
        just_skipped_long = False
        previous_vowel = None if mora.key in ("n", "Q") else vowel_of(mora.key)
    return normalized


def romaji_moras(text: str) -> list[str]:
    source = unicodedata.normalize("NFKC", text.translate(CUSTOM_ROMAJI)).lower()
    if not source or not re.fullmatch(r"[a-z]+", source):
        raise OfficerNameError(f"unsupported romaji word {text!r}")
    result: list[str] = []
    index = 0
    while index < len(source):
        if (
            index + 1 < len(source)
            and source[index] == source[index + 1]
            and source[index] not in "aeioun"
        ):
            result.append("Q")
            index += 1
            continue
        matched = next((key for key in ROMAJI_KEYS if source.startswith(key, index)), None)
        if matched is not None:
            result.append(matched)
            index += len(matched)
            continue
        if source[index] == "n":
            result.append("n")
            index += 1
            continue
        raise OfficerNameError(f"unsupported romaji sequence {source[index:]!r} in {text!r}")
    return result


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


WORD_OVERRIDES = {
    ("cho", "so", "ka", "be"): "조소카베",
    ("ke", "i", "ji"): "케이지",
}


def add_final(text: str, jongseong: int, fallback: str) -> str:
    if not text:
        return fallback
    codepoint = ord(text[-1])
    if 0xAC00 <= codepoint <= 0xD7A3 and (codepoint - 0xAC00) % 28 == 0:
        return text[:-1] + chr(codepoint + jongseong)
    return text + fallback


def moras_to_hangul(keys: Sequence[str]) -> str:
    override = WORD_OVERRIDES.get(tuple(keys))
    if override is not None:
        return override
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
            raise OfficerNameError(f"unsupported mora {key!r}")
        output += syllable
        spoken_index += 1
    return output


def kana_to_hangul(text: str) -> str:
    return moras_to_hangul([mora.key for mora in kana_moras(text)])


def romaji_to_hangul(text: str) -> str:
    return moras_to_hangul(romaji_moras(text))


def match_signature(keys: Sequence[str]) -> tuple[str, ...]:
    """Normalize Hepburn long-e spellings (``bei`` vs kana ``べえ``)."""
    result: list[str] = []
    previous_vowel: str | None = None
    for key in keys:
        if key in ("e", "i") and previous_vowel == "e":
            continue
        result.append(key)
        previous_vowel = None if key in ("n", "Q") else vowel_of(key)
    return tuple(result)


def mora_equal(left: Sequence[str], right: Sequence[str]) -> bool:
    return match_signature(left) == match_signature(right)


def split_at(reading: str, full: Sequence[Mora], index: int) -> list[str]:
    if index <= 0 or index >= len(full):
        raise OfficerNameError(f"invalid reading boundary {index} for {reading!r}")
    source_index = full[index].source_start
    return [reading[:source_index], reading[source_index:]]


def split_reading(
    reading: str,
    english_name: str,
    *,
    allow_alternate_surname: bool = False,
) -> tuple[list[str], str]:
    words = english_name.split()
    if len(words) == 1 or (len(words) == 2 and words[1] in TITLE_WORDS):
        return [reading], "unspaced_name"
    if len(words) != 2:
        raise OfficerNameError(f"unexpected English officer name {english_name!r}")
    given, surname = words
    full = kana_moras(reading)
    full_keys = [mora.key for mora in full]
    surname_keys = romaji_moras(surname)
    given_keys = romaji_moras(given)
    normal_boundaries = [
        index
        for index in range(1, len(full))
        if mora_equal(full_keys[:index], surname_keys)
        and mora_equal(full_keys[index:], given_keys)
    ]
    if len(normal_boundaries) == 1:
        return split_at(reading, full, normal_boundaries[0]), "reading_exact"

    # The EN table occasionally uses an alternate surname even though its given
    # name agrees with the Japanese display name (for example Akechi/Dota).
    given_boundaries = [
        index
        for index in range(1, len(full))
        if mora_equal(full_keys[index:], given_keys)
    ]
    if allow_alternate_surname and len(given_boundaries) == 1:
        return split_at(reading, full, given_boundaries[0]), "reading_given_suffix"

    # A handful of titles/compound personal names are written in forward order
    # in EN instead of the usual Given Surname localization order.
    forward_boundaries = [
        index
        for index in range(1, len(full))
        if mora_equal(full_keys[:index], given_keys)
        and mora_equal(full_keys[index:], surname_keys)
    ]
    if len(forward_boundaries) == 1:
        return split_at(reading, full, forward_boundaries[0]), "reading_english_forward"
    return [surname, given], "romaji_fallback"


def generate_name(
    entry_id: int,
    japanese_name: str,
    english_name: str,
    match: ReadingMatch,
) -> tuple[str, str]:
    if match.reading is None:
        words = english_name.split()
        if len(words) == 1:
            return romaji_to_hangul(words[0]), "romaji_mononym"
        if len(words) == 2 and words[1] not in TITLE_WORDS:
            return f"{romaji_to_hangul(words[1])} {romaji_to_hangul(words[0])}", "romaji_only"
        raise OfficerNameError(
            f"no Japanese reading for nonstandard English name {japanese_name!r} / {english_name!r}"
        )
    parts, method = split_reading(
        match.reading,
        english_name,
        allow_alternate_surname=entry_id in ALTERNATE_SURNAME_READING_IDS,
    )
    if method == "romaji_fallback":
        return f"{romaji_to_hangul(parts[0])} {romaji_to_hangul(parts[1])}", method
    return " ".join(kana_to_hangul(part) for part in parts if part), method


def build_catalog(args: argparse.Namespace) -> dict[str, Any]:
    sc = read_jsonl(args.sc_jsonl)
    jp = read_jsonl(args.jp_jsonl)
    en = read_jsonl(args.en_jsonl)
    if not (len(sc) == len(jp) == len(en)):
        raise OfficerNameError("SC/JP/EN JSONL tables are not aligned")
    readings, parsed_row_count = parse_reading_table(args.reading_html)

    entries: list[dict[str, Any]] = []
    report_rows: list[dict[str, Any]] = []
    method_counts: dict[str, int] = {}
    for entry_id in range(OFFICER_SLOT_LIMIT):
        if sc[entry_id] == DUMMY_BY_LANGUAGE["SC"]:
            if (
                jp[entry_id] != DUMMY_BY_LANGUAGE["JP"]
                or en[entry_id] != DUMMY_BY_LANGUAGE["EN"]
            ):
                raise OfficerNameError(f"dummy alignment differs at id {entry_id}")
            continue
        if (
            jp[entry_id] == DUMMY_BY_LANGUAGE["JP"]
            or en[entry_id] == DUMMY_BY_LANGUAGE["EN"]
        ):
            raise OfficerNameError(f"live officer alignment differs at id {entry_id}")
        match = find_reading(jp[entry_id], readings)
        try:
            korean, method = generate_name(entry_id, jp[entry_id], en[entry_id], match)
            error = None
        except OfficerNameError as exc:
            korean = ""
            method = "unresolved"
            error = str(exc)
        override = pinned_manual_override(
            entry_id,
            sc[entry_id],
            jp[entry_id],
            en[entry_id],
        )
        if override is not None:
            korean = override
            method = "manual_override"
            error = None
        method_counts[method] = method_counts.get(method, 0) + 1
        report_rows.append(
            {
                "id": entry_id,
                "jp": jp[entry_id],
                "en": en[entry_id],
                "reading": match.reading,
                "ko": korean,
                "method": method,
                "error": error,
            }
        )
        if korean:
            entries.append(
                {
                    "id": entry_id,
                    "source": {"SC": sc[entry_id], "EN": en[entry_id], "JP": jp[entry_id]},
                    "ko": korean,
                    "status": "translated",
                }
            )

    if len(report_rows) != EXPECTED_OFFICER_COUNT:
        raise OfficerNameError(
            f"expected {EXPECTED_OFFICER_COUNT} officers, found {len(report_rows)}"
        )
    known = {entry["id"]: entry["ko"] for entry in entries}
    expected_known = {
        106: "아츠지 사다유키",
        216: "이시다 미츠나리",
        558: "오다 노부나가",
    }
    for entry_id, expected in expected_known.items():
        if known.get(entry_id) != expected:
            raise OfficerNameError(
                f"known-name regression at id {entry_id}: {known.get(entry_id)!r} != {expected!r}"
            )

    source_paths = {
        "SC": args.stock_sc,
        "EN": args.stock_en,
        "JP": args.stock_jp,
    }
    catalog = {
        "schema": PRIVATE_SCHEMA,
        "scope": "msgev_officer_names_0000_2399",
        "version": args.version,
        "base_languages": ["SC", "EN", "JP"],
        "source_files": {
            language: {
                "path": f"MSG_PK/{language}/{RESOURCE_NAME}",
                "sha256": sha256_file(path),
            }
            for language, path in source_paths.items()
        },
        "entries": entries,
    }
    report = {
        "schema": "nobu16.kr.officer-name-generation-report.v1",
        "officer_slot_limit": OFFICER_SLOT_LIMIT,
        "officer_count": len(report_rows),
        "generated_count": len(entries),
        "unresolved_count": len(report_rows) - len(entries),
        "reading_html_row_count": parsed_row_count,
        "unique_reading_name_count": len(readings),
        "method_counts": dict(sorted(method_counts.items())),
        "rows": report_rows,
    }
    args.output_catalog.parent.mkdir(parents=True, exist_ok=True)
    args.output_report.parent.mkdir(parents=True, exist_ok=True)
    args.output_catalog.write_bytes(encode_json(catalog))
    args.output_report.write_bytes(encode_json(report))
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sc-jsonl", type=Path, required=True)
    parser.add_argument("--jp-jsonl", type=Path, required=True)
    parser.add_argument("--en-jsonl", type=Path, required=True)
    parser.add_argument("--reading-html", type=Path, required=True)
    parser.add_argument("--stock-sc", type=Path, required=True)
    parser.add_argument("--stock-en", type=Path, required=True)
    parser.add_argument("--stock-jp", type=Path, required=True)
    parser.add_argument("--output-catalog", type=Path, required=True)
    parser.add_argument("--output-report", type=Path, required=True)
    parser.add_argument("--version", default="0.1")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = build_catalog(args)
    except (OSError, OfficerNameError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps({key: report[key] for key in ("officer_count", "generated_count", "unresolved_count", "method_counts")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
