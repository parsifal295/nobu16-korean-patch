#!/usr/bin/env python3
"""Build a private direct-PC candidate for PK event reflow batch D.

The candidate starts from the exact current Steam W45 Korean PK event table.
It inserts one manual LF into each approved one-line record; no visible Korean
wording, ESC markup, runtime token, or printf token is changed.  All output is
restricted to this workstream's private tmp directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate"
CANDIDATE_EVENT = CANDIDATE_ROOT / "MSG_PK" / "JP" / "msgev.bin"
CANDIDATE_AUDIT = CANDIDATE_ROOT / "audit.v1.json"
CANDIDATE_MANIFEST = CANDIDATE_ROOT / "manifest.v1.json"

# Direct PC inputs only.  This workstream never opens a Switch or non-PC
# language resource, and neither path can be selected from the CLI.
W45_KO_EVENT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgev.bin")
PRISTINE_PC_JP_EVENT = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msgev.bin"
)
EVENT_FONT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\RES_JP\res_lang.bin")

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, parse_link, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402
import validate_g1n_surgical as g1n  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-reflow-static-batch-d-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-reflow-static-batch-d-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-reflow-static-batch-d-manifest.v1"
PK_MAX_LINE_PX = 912
MAX_LINES = 3
FONT_OUTER_ENTRY = 6
FONT_TABLE = 0

LINEBREAK_RE = re.compile(r"\r\n|\r|\n")
LAYOUT_WHITESPACE_RE = re.compile(r"[ \t\r\n]+")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
WIDE_SCRIPT_RE = re.compile(
    r"[\u1100-\u11ff\u3130-\u318f\uac00-\ud7a3\u3040-\u30ff\u31f0-\u31ff"
    r"\uff66-\uff9f\u3400-\u9fff\uf900-\ufaff]"
)


class BatchDError(RuntimeError):
    """Raised when a pinned direct-PC input or private output drifts."""


@dataclass(frozen=True)
class Profile:
    packed_size: int
    packed_sha256: str
    raw_size: int
    raw_sha256: str
    record_count: int


@dataclass(frozen=True)
class TableResource:
    path: Path
    packed: bytes
    header: Any
    raw: bytes
    table: MessageTable


@dataclass(frozen=True)
class Change:
    entry_id: int
    current_utf16le_sha256: str
    target: str
    target_utf16le_sha256: str
    jp_utf16le_sha256: str
    target_line_widths_px: tuple[int, ...]
    rationale: str


@dataclass(frozen=True)
class Hold:
    entry_id: int
    current_utf16le_sha256: str
    jp_utf16le_sha256: str
    rationale: str


@dataclass(frozen=True)
class CandidateBundle:
    packed: bytes
    raw: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


W45_PROFILE = Profile(
    994_739,
    "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
    990_828,
    "F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC",
    17_916,
)
PRISTINE_PC_JP_PROFILE = Profile(
    562_226,
    "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    894_800,
    "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
    17_916,
)
EXPECTED_OUTPUT_PROFILE = Profile(
    994_743,
    "AB7B14FEFE360F6A5C48482A9B4866E8386CDF302FCAFD6C944AE7E9D6926C97",
    990_832,
    "70FAF792D88CA184A9E9A73C3CB825B7B1B872AFEADBA4CFFDD33587058303FB",
    17_916,
)
FONT_PROFILE = {
    "size": 161_428_458,
    "sha256": "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7",
    "g1n_raw_size": 21_720_288,
    "g1n_raw_sha256": "30F1AC5AEE1962826AE3D193E2AD6F18723402382D59B242E725E33D7E44F6A6",
    "sample_advances_px": {"ascii_space": 24, "ellipsis": 48, "hangul": 48},
}


# Each approved target adds exactly one LF.  Removing all linebreaks yields
# byte-for-byte identical visible/markup text to its W45 preimage.
CHANGES = (
    Change(3235, "94FA29B7B6279D7CEBD80B5F3AF83A982574335D8EB3EE2FC106A7A7EC65A303", "팥은 우리. 양 끝을 묶는 끈은\n\x1bCC아사쿠라\x1bCZ와 \x1bCC아자이\x1bCZ…", "B736C783E251CD10A83A4DAC741E0520055917971DDCF97B7746BCAE376B1B06", "737B64D1B24561774AF35F79A46306F5FD5CD75D8C8F6B8AADAB6B3A804B0D12", (672, 456), "비유의 전반부와 ‘아사쿠라와 아자이’의 대상을 분리한다."),
    Change(3238, "91BDB59BD8C8AD75EBD2C2557042C704164E92BC00934A33A44C927BF9E479CF", "\x1bCA노부나가\x1bCZ는 누이를 시집보내\n동맹에 끼어들었다.", "691FFF2384CEB395BFF0906C6C9C296424ECB20E7D7FBEDFC7B32E643A315222", "08A81A7CC1640B7BA922830E95B10970E525556D87CDD7C7F7E7A29A1563E7B8", (624, 432), "혼인 행위와 동맹 개입을 절 경계에서 나눈다."),
    Change(3269, "989B3A524B74CDB02A64584818B84979F3EE7315B66E7B10F9D1979DF8B1870A", "\x1bCB다케다\x1bCZ에게 \x1bCC미카와\x1bCZ 사나이의 기개를\n보여 주마!", "A4AA2964ECB688C98706DA779C928378913A66201789F38369901AE894BB4617", "817E599276EDE1210F2F514158359917545B4AA006357184731FF48663D3DD48", (792, 240), "대상·명사구를 보존하고 서술어 앞에서 끊는다."),
    Change(3284, "F4C3C5D24A7EDE701CC1DE55D355D4AE7E28CE0D36ACE1E070699B379D1CB451", "이 나라 사람들에게\n구원을 전해야 한다……", "FE2BF0CE9AB0B498955C1FEA3E9EBC0542B5D90EF7C53A530944D582E2D751EA", "D9E4A547EDC473A0B92CC96B3FCA0F846A332D208BA001B81EB2CB640FC14548", (432, 528), "대상과 ‘구원을 전하다’의 서술부를 분리한다."),
    Change(3847, "5DBCF362971E1322FB3EB9F05CFFB7F8D6FED0BF14DF9C75BAAA58238E8B91D5", "그러면 \x1bCC오카자키\x1bCZ의\n\x1bCB마쓰다이라 가문\x1bCZ은……?", "7857E4D0E473EE3A0459B79870084E472618C1B5C742853A496EE554ADC53408", "5584389632BBFBBDEAAFEBE47F23E7426FF890825A68A2BF2ADCA8FCA8F5B281", (408, 528), "오카자키의 가문을 질문 단위로 나눈다."),
    Change(3868, "84B1C601F024C58389FD9B39D315B86011750C92487AD156E91E545A44D433FC", "성주 \x1bCA나가오 마사카게\x1bCZ 님께서\n직접 오셨습니다.", "BE4151B73A25B9DC9F668CB4308885CFBE1996EBC8241764D95B44F4F347F43D", "FEB266C667940540EB49FC913B0AD78B81AFC2659D257FF9BD2634B372CF1D6C", (648, 384), "주어와 직접 방문이라는 술어를 분리한다."),
    Change(3886, "A50A0CA695E5811096F63DF029C7F165E65BF65ED510E7E27E461874D1907A0B", "그렇게 노골적으로\n싫은 얼굴을 하지 마라!", "4A1E750F72F12B19A58E1AB504DE14365F088D196B65C7991312B208ACB25E02", "A8C0DA0F4A2577171D6B7195FA93F1238E531CF6355F41520AB954D0B255B92E", (408, 528), "부사구와 명령문을 분리한다."),
    Change(4016, "09505C20D56790B34E39E99881E21E3ABCE2B97CEA1691FF3A3E457A7A210172", "그러던 중, 그는\n유행병으로 쓰러졌다……", "1860B601183EDC526E604610EA08FCE027CD8B192B79600FA9E9A4B95D8384FF", "B068106D99333D634E9E845CBAAB059DF133DAD86814DE81DB1C1C6DFFFBD514", (360, 552), "전환부·주어와 사건을 분리한다."),
    Change(4139, "C48A80866916ABF9F546D43F2B52003E92043BAEAF98007C4604E7135F4AB68A", "\x1bCB아사쿠라 가문\x1bCZ의 중신·\n\x1bCA아사쿠라 소테키\x1bCZ―", "D8787EC8ECDB412DD68C927E7391A221D2CB990746933536FB962C8899A60BD1", "B339C29648B214EBB06A59A615C3AA73892B13ECB97A60A5A8C77624A6DA4644", (528, 408), "직함과 인명 소개를 분리한다."),
    Change(4142, "27E6CEA1B7C35C20E6E116DCB26CC5E51C1A8643DE2823158B9F11E039F8BD6B", "하지만 그 \x1bCA소테키\x1bCZ도\n마침내 병으로 쓰러졌다……", "AE8772BD0A6B15EC30733F2E3A38F195CECB091D8C35C3FA207C9CD47ED2397B", "A94C761392CA685FD519B42BECD6E5B33FF43306A0947E6E8448FF652708BB32", (432, 624), "주제 전환·주어와 발병 사건을 분리한다."),
    Change(4329, "10729DEB72EEE857001EBD79C5D39262B1D9921E411CB8576F648343E92F6BCE", "말도 안 돼…… 이렇게 쉽게……\n패하다니!", "EE26FA34A2B891EC87269D888E6D354E82FFFA05C93EEC207EADA402D8C62807", "1650F96A1E76B0C60EDE8366C00E54D5A7F01719545142BA2BAEBA8B39AB3A61", (720, 216), "경악과 결말 감탄을 분리한다."),
    Change(4530, "461A9E0549A393690429AE89F9A27CA2A34539DDFCE2678C2649E3EF6BD44BF3", "그러나 \x1bCA구니치카\x1bCZ를\n병마가 무정하게 덮쳤다.", "20ED0D213F1E0496573984DFD79806CC6E7A05B71B44F344955D25910F5508AA", "6EEA1A7C6064B08758DF963EBDE4E8CF4D97E831C4DFB8A32BC2FE23EBD1979E", (408, 552), "대상과 병마의 서술을 분리한다."),
    Change(4752, "86898FA479A69340E839185EA47FBB8A4460BFEE1C0B5C1C17E74FA5261FB149", "이제 \x1bCA가게토라\x1bCZ는\n\x1bCC간토\x1bCZ의 구세주가 되었다.", "993E93B9A7C5B7BE2D1662BB096A7D88702654A9A578B4C55650E28A8DCCF6F9", "6B817B389B6F583D9C6E63FEEC98E0176614788BAE0ED78A6769EDC29C9E9890", (360, 552), "주어와 ‘간토의 구세주’라는 보어를 통째로 분리한다."),
    Change(4758, "8F6D56E2A2E971051E1A392514C3007EE27C204D69666636FDEB70EF6D271DCB", "\x1bCA가게이에\x1bCZ, 나는 이를 계기로\n이름을 바꾸겠다.", "9B4B712243B53E09275170BA9D0684CD09994667D370889CE0844B28A0576EE2", "792AFB6F1FEDAC8319A2E784208190096761DF5E882E15D17F2B5A34BD82A3FC", (624, 384), "계기와 개명 선언을 분리한다."),
    Change(4911, "8D60ADAB63DD24D7CA8537ABC3D491A477E88A86071E28889E1E68EFACD97410", "\x1bCA사나다 유키타카\x1bCZ의 셋째 아들\n\x1bCA겐고로\x1bCZ가 원복을 맞았다.", "02B598E802D6287B63EDE7BB3A712419AE8A87245F3EDCE82DE75159B82A8192", "B817DD751437332ABAD7B64D9693FFBC126DB1542B61F200139B78E1E685081C", (648, 552), "혈연 소개와 원복 사건을 분리한다."),
    Change(4929, "C4375859B1DD48E87331882243EC425FED178790BBAC345A2BC9CC0F030D2D6C", "……잘 들어라.\n가신들에게 이렇게 전하라.", "0E0BEB7767E19E95F5D83FF16FECCFE5140C9BF115623035C7C02363CCA2F4F3", "ABF1133EA1262E6C09C03BF09246D737602CCCD7560886F9224EAFF34330EE41", (336, 600), "호명과 전달 명령을 분리한다."),
    Change(5031, "1D83B1DFDF8853358756D92E6FFE21F67B7A340B289917BF859F7E8564CF3102", "훗날 도쿠가와 십육신장에도 꼽히는\n\x1bCA와타나베 모리쓰나\x1bCZ", "80B734F49A2A93893A361AE04B4794603D5037397242A53C49014C0CA76F625C", "8974398A9C846709A9619BBA8B320E76F74FA4C6F8B99C930BC81639967C024E", (792, 408), "수식절과 인명을 분리한다."),
    Change(5032, "C5BC45556D9C8797BE6053C378C0196FA1A755BE29096E2D66751EAD866B070B", "마찬가지로 \x1bCA하치야 한노조\x1bCZ라는\n이름으로 알려진 \x1bCA하치야 사다쓰구\x1bCZ", "AD92866FFD8DDDB4B89FB2E1ED47E6A6DEA2D5E1B138867812E17937396BF67D", "2291A4284167CBC6CD0FC5DA33297711E9BAF3C7D20FBA5E95ABB396EE926390", (672, 744), "별칭 절과 인명을 분리한다."),
    Change(5092, "284B8B274490789947C484BBC76F9CE6EC543C091A9934E1C601C17A4D3DE23C", "맞지는 않았지만,\n크게 빗나가지도 않았다.", "1FE1497872D6D2468D2DE3C2468D22FE4ABBAF6DA28E2595A6F2F6F03AE92D80", "AC81BF590E9D8117F821C3F14A1196F93AC90F4300317C47B9637224D76B57C5", (384, 552), "양보절과 결론을 분리한다."),
    Change(5187, "70DFF2FE999015DF343AB07C2C1C1847F8DFCF9454A1E3FA2AB0AD1BB64B4A79", "\x1bCC노지리호\x1bCZ 인근·\n\x1bCA우사미 사다미츠\x1bCZ의 저택――", "C7DC7C6EDF1E693F2949CF078BD2E38D92347661F09FCD5481521E6755697864", "2B6AD53820825956533C090C77C3DA91278E4085B5DF0406E2D05F3382B48F84", (360, 624), "지점 표기와 저택 표기를 분리한다."),
    Change(5209, "CC8E406688337B81A94020AABD7F6A1D3EF0D20DCA889BD74176872196C0EB1A", "언니, 무슨 말씀을 드려야 할지\n모르겠습니다.", "6A328E08A5776036D976A01032B20E2C390C4DB6E89398E223B5660800470415", "E77147F7B60EF5FE8019980452D379D40EDF92721725D02F021030DE62C33A81", (696, 312), "호명·머뭇거림과 결론을 분리한다."),
    Change(5334, "A08163158F0F1EF7381BB968FCFAFC2FEF7D4BD96BB4C24B3A1B44A8D881CA1E", "\x1bCA아케치 미쓰히데\x1bCZ의 전반생은\n수수께끼에 싸여 있다.", "32EDC4AEA95C2EE61C912EBAC637B4DCF098E02A8EA00ECDABAAEDC328ECD4A8", "4D4FCF9473E7F63AB9243ED872DCAE79D6E94B04A300C9D16FA2477FCFC37BDA", (624, 504), "주제와 평가를 분리한다."),
    Change(5411, "69515C1CE958E1FF81049A2F7FD5E9FADD0331C8F5A9CF1145D1F95BA2B950C4", "훗날 검성으로 칭송된\n신카게류의 창시자다.", "B2B465BCDB38484B235AA36BC06DB10D78A1A41F0680DEB7FBE868D71AE2FDEB", "66B732F511C494994647C571751CF2193FEF856F5959F6AF14FD350B704D7EB3", (480, 480), "수식절과 정의를 분리한다."),
    Change(5515, "48BCDB75D5B1317D659930BA63444EF9DEF829BBEDBF02B3CEF74ADBC2FD7078", "그러지 마시고,\n어떻게 좀 안 되겠습니까……", "40B676090DDC283B0AFFD7EDE7173BDB638B63BB994C022D1169318B9A0A368B", "5D5D8A9899D5DCB11FDCE80CB71DB351013B84738720F9AEE9B368ED48E097EF", (336, 648), "완곡한 거절과 부탁을 분리한다."),
)

# This title-style fragment has a separator and possessive relationship whose
# natural Korean break point is not unambiguous.  It is deliberately not
# changed by this batch.
HOLDS = (
    Hold(4999, "20964328F7DDC8F1A3438E6AEFFCAD1777EDC33CA711D7DF8FC43DB7FF3D5BC3", "EF221D0C9C5DEFDFE64CF12D4B0C48989E90CC8531711D355590073FC61ED86C", "가문·인명·거성이라는 제목형 구문은 구분점과 조사 경계가 애매해 실제 문맥 검토 전 보류한다."),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BatchDError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def file_profile(packed: bytes, raw: bytes, table: MessageTable) -> Profile:
    return Profile(len(packed), sha256_bytes(packed), len(raw), sha256_bytes(raw), table.string_count)


def require_profile(actual: Profile, expected: Profile, label: str) -> None:
    require(actual == expected, f"{label} profile differs: expected={expected!r}, actual={actual!r}")


def read_table(
    path: Path,
    expected: Profile,
    label: str,
    *,
    require_packed_roundtrip: bool = True,
) -> TableResource:
    require(path.is_file(), f"{label} is absent: {path}")
    packed = path.read_bytes()
    try:
        header, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
    except Exception as exc:  # pragma: no cover - precise provenance is in the message
        raise BatchDError(f"{label} cannot be parsed as a wrapped message table") from exc
    require_profile(file_profile(packed, raw, table), expected, label)
    require(rebuild_message_table(table, table.texts) == raw, f"{label} raw parse/rebuild differs")
    if require_packed_roundtrip:
        require(recompress_wrapper(raw, header) == packed, f"{label} packed parse/rebuild differs")
    return TableResource(path, packed, header, raw, table)


@dataclass(frozen=True)
class EventFont:
    raw: bytes
    table_offset: int

    def advance(self, character: str) -> int:
        codepoint = ord(character)
        if codepoint >= g1n.MAP_ENTRIES:
            raise BatchDError(f"event font has no map entry for U+{codepoint:04X}")
        ordinal = struct.unpack_from("<H", self.raw, self.table_offset + codepoint * 2)[0]
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(character) is not None:
                return 48
            raise BatchDError(f"event font glyph is absent: U+{codepoint:04X}")
        record_offset = self.table_offset + g1n.MAP_SIZE + ordinal * g1n.RECORD_SIZE
        if record_offset + g1n.RECORD_SIZE > len(self.raw):
            raise BatchDError(f"event font glyph record exceeds data: U+{codepoint:04X}")
        width = self.raw[record_offset]
        advance = self.raw[record_offset + 4]
        if width != advance or advance not in (24, 48):
            raise BatchDError(f"unexpected event font metric for U+{codepoint:04X}")
        return advance


def load_font() -> EventFont:
    require(EVENT_FONT.is_file(), f"event font is absent: {EVENT_FONT}")
    packed = EVENT_FONT.read_bytes()
    require(len(packed) == FONT_PROFILE["size"], "event font packed size differs")
    require(sha256_bytes(packed) == FONT_PROFILE["sha256"], "event font packed SHA-256 differs")
    archive = parse_link(packed)
    require(FONT_OUTER_ENTRY < len(archive.entries), "event font outer entry is absent")
    _header, raw = decompress_wrapper(archive.entries[FONT_OUTER_ENTRY].data)
    require(len(raw) == FONT_PROFILE["g1n_raw_size"], "event font raw size differs")
    require(sha256_bytes(raw) == FONT_PROFILE["g1n_raw_sha256"], "event font raw SHA-256 differs")
    require(raw[:8] == g1n.MAGIC, "event font G1N magic differs")
    table_count = struct.unpack_from("<I", raw, 0x1C)[0]
    require(FONT_TABLE < table_count, "event font table 0 is absent")
    table_offset = struct.unpack_from("<I", raw, g1n.FIXED_HEADER_SIZE + FONT_TABLE * 4)[0]
    require(g1n.FIXED_HEADER_SIZE <= table_offset < len(raw), "event font table offset differs")
    font = EventFont(raw, table_offset)
    require(
        {
            "ascii_space": font.advance(" "),
            "ellipsis": font.advance("…"),
            "hangul": font.advance("가"),
        }
        == FONT_PROFILE["sample_advances_px"],
        "event font sample advances differ",
    )
    return font


def escape_tokens(value: str) -> tuple[str, ...]:
    tokens: list[str] = []
    cursor = 0
    while cursor < len(value):
        if value[cursor] != "\x1b":
            cursor += 1
            continue
        token = value[cursor : cursor + 3]
        require(ESC_RE.fullmatch(token) is not None, f"malformed ESC-C token at {cursor}")
        tokens.append(token)
        cursor += 3
    return tuple(tokens)


def tag_structure(value: str) -> tuple[str, ...]:
    active: str | None = None
    structure: list[str] = []
    for token in escape_tokens(value):
        code = token[2]
        if code in "ABC":
            require(active is None, "nested color span is not supported")
            active = code
            structure.append(f"open:{code}")
        elif code == "Z":
            require(active is not None, "orphan color reset")
            structure.append(f"close:{active}")
            active = None
        else:
            raise BatchDError(f"unsupported ESC-C color code: {code!r}")
    require(active is None, "unclosed color span")
    return tuple(structure)


def printf_tokens(value: str) -> tuple[tuple[str, ...], int]:
    matches = list(PRINTF_RE.finditer(value))
    percent_offsets = {
        offset
        for match in matches
        for offset, character in enumerate(value[match.start() : match.end()], match.start())
        if character == "%"
    }
    unknown = sum(1 for offset, character in enumerate(value) if character == "%" and offset not in percent_offsets)
    return tuple(match.group(0) for match in matches), unknown


def control_signature(value: str) -> Mapping[str, Any]:
    printf, unknown_percent = printf_tokens(value)
    controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC-C token at {cursor}")
            cursor += 3
            continue
        character = value[cursor]
        if character not in "\r\n" and unicodedata.category(character) == "Cc":
            controls.append(f"U+{ord(character):04X}")
        cursor += 1
    return {
        "esc_tokens": list(escape_tokens(value)),
        "tag_structure": list(tag_structure(value)),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": list(printf),
        "unknown_percent_count": unknown_percent,
        "other_controls": controls,
    }


def line_widths(value: str, font: EventFont) -> tuple[int, ...]:
    widths: list[int] = []
    for line in LINEBREAK_RE.sub("\n", value).split("\n"):
        width = 0
        cursor = 0
        while cursor < len(line):
            if line[cursor] == "\x1b":
                token = line[cursor : cursor + 3]
                require(ESC_RE.fullmatch(token) is not None, "malformed ESC-C token in layout")
                cursor += 3
                continue
            character = line[cursor]
            require(unicodedata.category(character) != "Cc", f"unexpected control U+{ord(character):04X}")
            width += font.advance(character)
            cursor += 1
        widths.append(width)
    return tuple(widths)


def normalized_layout_text(value: str) -> str:
    """Compare visible word/markup tokens while allowing a space→LF reflow."""
    return LAYOUT_WHITESPACE_RE.sub(" ", value).strip()


def layout_equivalent(before: str, after: str) -> bool:
    """Allow an LF insertion at punctuation or in place of a word separator."""
    return LINEBREAK_RE.sub("", after) == before or normalized_layout_text(before) == normalized_layout_text(after)


def profile_dict(profile: Profile) -> dict[str, Any]:
    return {
        "packed_size": profile.packed_size,
        "packed_sha256": profile.packed_sha256,
        "raw_size": profile.raw_size,
        "raw_sha256": profile.raw_sha256,
        "record_count": profile.record_count,
    }


def require_private(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BatchDError(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def atomic_write(path: Path, value: bytes) -> None:
    path = require_private(path, "private output")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
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


def validate_declarations() -> None:
    ids = [change.entry_id for change in CHANGES]
    require(ids == sorted(ids), "changes must be in ascending ID order")
    require(len(ids) == len(set(ids)) == 24, "batch D must have exactly 24 approved targets")
    require(HOLDS[0].entry_id == 4999, "batch D title hold differs")
    require(set(ids).isdisjoint(hold.entry_id for hold in HOLDS), "hold overlaps target")


def prepare_candidate() -> CandidateBundle:
    validate_declarations()
    source = read_table(W45_KO_EVENT, W45_PROFILE, "W45 Steam PC Korean PK event")
    jp = read_table(
        PRISTINE_PC_JP_EVENT,
        PRISTINE_PC_JP_PROFILE,
        "pristine PC Japanese PK event",
        require_packed_roundtrip=False,
    )
    require(source.table.string_count == jp.table.string_count, "direct PC tables have different record counts")
    font = load_font()

    targets = list(source.table.texts)
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        require(change.entry_id < source.table.string_count, f"target {change.entry_id} is absent")
        before = source.table.texts[change.entry_id]
        jp_text = jp.table.texts[change.entry_id]
        require(text_hash(before) == change.current_utf16le_sha256, f"{change.entry_id} W45 preimage differs")
        require(text_hash(change.target) == change.target_utf16le_sha256, f"{change.entry_id} target declaration differs")
        require(text_hash(jp_text) == change.jp_utf16le_sha256, f"{change.entry_id} PC JP anchor differs")
        require(LINEBREAK_RE.findall(before) == [], f"{change.entry_id} source unexpectedly already has LF")
        require(LINEBREAK_RE.findall(change.target) == ["\n"], f"{change.entry_id} target must add exactly one LF")
        require(layout_equivalent(before, change.target), f"{change.entry_id} visible wording or markup changed")
        require(control_signature(before) == control_signature(change.target), f"{change.entry_id} token or tag signature changed")
        widths = line_widths(change.target, font)
        require(widths == change.target_line_widths_px, f"{change.entry_id} target width declaration differs")
        require(1 <= len(widths) <= MAX_LINES, f"{change.entry_id} exceeds {MAX_LINES} lines")
        require(max(widths, default=0) <= PK_MAX_LINE_PX, f"{change.entry_id} exceeds {PK_MAX_LINE_PX}px")
        targets[change.entry_id] = change.target
        rows.append(
            {
                "id": change.entry_id,
                "w45_utf16le_sha256": change.current_utf16le_sha256,
                "target_utf16le_sha256": change.target_utf16le_sha256,
                "pc_jp_utf16le_sha256": change.jp_utf16le_sha256,
                "source_manual_lf_count": 0,
                "target_manual_lf_count": 1,
                "target_line_widths_px": list(widths),
                "rationale": change.rationale,
            }
        )

    holds: list[dict[str, Any]] = []
    for hold in HOLDS:
        before = source.table.texts[hold.entry_id]
        jp_text = jp.table.texts[hold.entry_id]
        require(text_hash(before) == hold.current_utf16le_sha256, f"hold {hold.entry_id} W45 preimage differs")
        require(text_hash(jp_text) == hold.jp_utf16le_sha256, f"hold {hold.entry_id} PC JP anchor differs")
        require(targets[hold.entry_id] == before, f"hold {hold.entry_id} changed")
        holds.append({"id": hold.entry_id, "rationale": hold.rationale})

    raw = rebuild_message_table(source.table, tuple(targets))
    packed = recompress_wrapper(raw, source.header)
    output_header, output_raw = decompress_wrapper(packed)
    output_table = parse_message_table(output_raw)
    output_profile = file_profile(packed, output_raw, output_table)
    require_profile(output_profile, EXPECTED_OUTPUT_PROFILE, "batch D private output")
    require(rebuild_message_table(output_table, output_table.texts) == output_raw, "candidate raw round-trip differs")
    require(recompress_wrapper(output_raw, output_header) == packed, "candidate packed round-trip differs")
    changed_ids = [
        entry_id
        for entry_id, (before, after) in enumerate(zip(source.table.texts, output_table.texts))
        if before != after
    ]
    expected_ids = [change.entry_id for change in CHANGES]
    require(changed_ids == expected_ids, f"candidate changed scope differs: {changed_ids!r}")
    require(output_table.texts[HOLDS[0].entry_id] == source.table.texts[HOLDS[0].entry_id], "hold 4999 changed in candidate")

    audit = {
        "schema": AUDIT_SCHEMA,
        "candidate_only": True,
        "input_policy": {
            "korean_input": "current Steam W45 PC MSG_PK/JP/msgev.bin only",
            "semantic_reference": "pristine direct-PC Japanese MSG_PK/JP/msgev.bin only",
            "switch_or_other_language_read": False,
            "steam_written": False,
            "git_written": False,
            "network_or_release": False,
        },
        "source": profile_dict(W45_PROFILE),
        "pc_jp": profile_dict(PRISTINE_PC_JP_PROFILE),
        "candidate": profile_dict(EXPECTED_OUTPUT_PROFILE),
        "font": dict(FONT_PROFILE),
        "approved_change_count": len(CHANGES),
        "approved_ids": expected_ids,
        "holds": holds,
        "rows": rows,
        "invariants": {
            "all_source_rows_have_zero_manual_lf": True,
            "all_targets_add_exactly_one_manual_lf": True,
            "visible_wording_and_markup_preserved": True,
            "one_phrase_or_punctuation_boundary_reflowed_by_lf_per_target": True,
            "esc_runtime_printf_and_control_signatures_preserved": True,
            "max_lines": MAX_LINES,
            "max_line_width_px": PK_MAX_LINE_PX,
            "target_only_entry_scope": True,
        },
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_root": CANDIDATE_ROOT.relative_to(REPO).as_posix(),
        "resource": "MSG_PK/JP/msgev.bin",
        "source": profile_dict(W45_PROFILE),
        "output": profile_dict(EXPECTED_OUTPUT_PROFILE),
        "changed_ids": expected_ids,
        "held_ids": [hold.entry_id for hold in HOLDS],
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "capabilities": {
            "steam_write": False,
            "steam_transaction": False,
            "git": False,
            "github": False,
            "network": False,
            "release": False,
        },
    }
    return CandidateBundle(packed, raw, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> None:
    atomic_write(CANDIDATE_EVENT, bundle.packed)
    atomic_write(CANDIDATE_AUDIT, canonical_json(bundle.audit))
    atomic_write(CANDIDATE_MANIFEST, canonical_json(bundle.manifest))


def verify_private() -> CandidateBundle:
    bundle = prepare_candidate()
    for path, expected, label in (
        (CANDIDATE_EVENT, bundle.packed, "candidate event"),
        (CANDIDATE_AUDIT, canonical_json(bundle.audit), "candidate audit"),
        (CANDIDATE_MANIFEST, canonical_json(bundle.manifest), "candidate manifest"),
    ):
        path = require_private(path, label)
        require(path.is_file(), f"{label} is absent; run build first")
        require(path.read_bytes() == expected, f"{label} differs from deterministic private build")
    return bundle


def diff_check() -> CandidateBundle:
    bundle = verify_private()
    source = read_table(W45_KO_EVENT, W45_PROFILE, "W45 Steam PC Korean PK event")
    _header, raw = decompress_wrapper(CANDIDATE_EVENT.read_bytes())
    candidate = parse_message_table(raw)
    changed_ids = [
        entry_id
        for entry_id, (before, after) in enumerate(zip(source.table.texts, candidate.texts))
        if before != after
    ]
    require(changed_ids == [change.entry_id for change in CHANGES], "private candidate diff scope differs")
    return bundle


def result_summary(bundle: CandidateBundle) -> Mapping[str, Any]:
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "candidate": str(CANDIDATE_EVENT.relative_to(REPO)),
        "approved_change_count": len(CHANGES),
        "approved_ids": [change.entry_id for change in CHANGES],
        "held_ids": [hold.entry_id for hold in HOLDS],
        "output": profile_dict(EXPECTED_OUTPUT_PROFILE),
        "audit_sha256": sha256_bytes(canonical_json(bundle.audit)),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private", "diff-check"))
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            bundle = prepare_candidate()
            write_candidate(bundle)
        elif args.command == "verify-private":
            bundle = verify_private()
        else:
            bundle = diff_check()
        print(json.dumps(result_summary(bundle), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, BatchDError) as exc:
        print(json.dumps({"schema": SCHEMA, "status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
