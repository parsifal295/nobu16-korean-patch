#!/usr/bin/env python3
"""Build a private, PC-only Wave9 event-linebreak candidate.

The builder is deliberately candidate-only.  It validates the live Steam PC
tables, makes deterministic in-memory rebuilds, and writes artefacts only
under ``KR_PATCH_WORK/tmp`` when ``--write`` is supplied.  It never writes the
Steam install, an overlay, a release directory, or Git state.
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
from typing import Any, Callable, Iterable, Mapping


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

BASE_RESOURCE = "MSG/JP/ev_strdata.bin"
PK_RESOURCE = "MSG_PK/JP/msgev.bin"
RESOURCE_ORDER = ("base", "pk")
RESOURCE_PATHS = {"base": BASE_RESOURCE, "pk": PK_RESOURCE}
EXPECTED_STRING_COUNTS = {"base": 17868, "pk": 17916}

# These are the current Wave8-installed packed-resource preimages.  A change
# to either source stops the candidate rather than silently rebasing it.
EXPECTED_WAVE8_PACKED_SHA256 = {
    "base": "25D9C029F93788053720C04BAE0C0A14A1A5983F36C68BC2EC7C46C3340D5834",
    "pk": "1880A8052C916FAC7F262CCC8638477F5AA124F248A6468E0533A8E252AB55C5",
}
EXPECTED_FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"

# All references below are PC files.  No Switch resource or historic Korean
# payload is a build input.
PC_REFERENCE_SPECS = {
    "base": {
        "JP": (
            Path(
                r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
                r"\file_only_transaction\steam-jp-1.1.7-v0.8.0\originals"
                r"\MSG\JP\ev_strdata.bin"
            ),
            "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
        ),
        "SC": (Path("MSG/SC/ev_strdata.bin"), "77E87C6FEC67859543FCB4134660A7274A2374F6881B956421B561E61BD7B685"),
        "TC": (Path("MSG/TC/ev_strdata.bin"), "9E9346B942CAFA99432D675F6BA74DD04D48F56095F35F46392697011D9CFEF3"),
    },
    "pk": {
        "JP": (
            Path(
                r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
                r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals"
                r"\MSG_PK\JP\msgev.bin"
            ),
            "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
        ),
        "EN": (Path("MSG_PK/EN/msgev.bin"), "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E"),
        "SC": (Path("MSG_PK/SC/msgev.bin"), "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA"),
        "TC": (Path("MSG_PK/TC/msgev.bin"), "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6"),
    },
}

FONT_HELPER = REPO / "workstreams" / "steam_jp_msgev_full_layout_v1" / "build_steam_jp_msgev_full_layout_v1.py"
MAX_LINES = 3
PK_MAX_LINE_PX = 912
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
KANA_OR_HAN_RE = re.compile(r"[\u3041-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u9fff\uf900-\ufaff]")
ESC = "\x1b"


class CandidateError(ValueError):
    """Raised when a source pin, formatting contract, or layout guard differs."""


@dataclass(frozen=True)
class Candidate:
    resource_key: str
    identifier: int
    expected_current_sha256: str
    expected_target_sha256: str
    change_kind: str
    rationale: str
    target: str


def _text(value: str) -> str:
    """Keep colour controls readable in the source while preserving exact bytes."""

    return value.replace("<E>", ESC)


# 20 reviewed coordinates: 15 Base event entries and five PK entries.  Hashes
# pin both the exact current Korean cell and the intended Wave9 candidate text.
CANDIDATES: tuple[Candidate, ...] = (
    Candidate("base", 4558, "2C52E80DE4E1629C54927FE0E894C5D1CE90601B535D174B70796AC61183294F", "387A61A3B9B73E2E6C3FFF68F4EB7DBD7C47DB7C2E1493A578BBBE5C36FB567A", "wording_change_with_layout", "조사 분절을 없애고 문장을 압축한다.", _text("이제는 <E>CC기나이<E>CZ 전역을 지배하에 두고,\n쇼군의 권위마저 품은 <E>CB미요시<E>CZ 정권에서도\n<E>CA히사히데<E>CZ의 실력과 존재감은 발군이었다.")),
    Candidate("base", 4657, "1AB32CC0C368B7AAB121DFA81AD00E00B103527E1A2CD2F1100D56D7CEAB10E7", "84805C89E52DADBB63B613E6AD5CAA07C4982C90C3B6AA3EA7DF843CC6694B40", "wording_change_with_layout", "장소격 조사 분절을 제거하고 호칭을 간결화한다.", _text("조슈 호랑이, 최전선에서\n<E>CA[b1251]<E>CZ 침공을 막은\n<E>CC미노와<E>CZ 성주 <E>CA나가노 나리마사<E>CZ—")),
    Candidate("base", 4769, "2738AAA21BBABF9050C0620F5E9277E4D7DEFAB4484D58A806B63305CE02F4D7", "D5A9A6EBD9E1906F8878DC72C360A7338D0C723B5CE06F867C15ABAA46C9D0C5", "wording_change_with_layout", "접속 조사 분절을 제거하고 통치 관계를 자연스럽게 정리한다.", _text("<E>CC히다<E>CZ는 남북조 시대에 공가인\n<E>CB아네가코지가<E>CZ가 국사로 임명되고,\n막부의 슈고 <E>CB교고쿠가<E>CZ와 나눠 통치했다.")),
    Candidate("base", 4781, "EED0E4B698ADA2B24B195A8CA3C335B7447A5C30EC278D043FAEB94146887E40", "144CCC73B5D4FF3F669ED5AC504FABD9F33AC8671EA128313505BBEB0845767D", "wording_change_with_layout", "공가 격과 최고 관직의 관계가 완결되도록 자연스럽게 정리한다.", _text("<E>CC교토<E>CZ의 <E>CB아네가코지 가문<E>CZ은 공가 격으로\n‘<E>CB우린케<E>CZ’에 해당하며, 최고 관직은\n다이나곤이었다.")),
    Candidate("base", 5155, "374A02A025D89355A2DCFF3ECE0D1B9708510DFAB0BC8E9E4D59ACD70BD95F22", "C3CD9B6E378FE73261D0F8AF13BAEFE1A0E4531DD4AB51C50BE7996B6D3F51FB", "wording_change_with_layout", "인물명 뒤 조사 분절을 제거하고 영입 제안을 간결화한다.", _text("아버지 대부터 <E>CB사이토 가문<E>CZ에 시달린\n<E>CA오다 노부나가<E>CZ 등은 <E>CC미노 반국<E>CZ을 대가로\n성과 <E>CA한베에<E>CZ의 영입을 제안했으나…")),
    Candidate("base", 5403, "D850906A0587C77CC3423D2769469FBD4495336E0D764D91A39350A0911B3B36", "48EE6B71A22EBC3E5B969B6935EFC08B246A6271C3755F50F8D730447B62DE3C", "wording_change_with_layout", "원인절의 조사 분절을 제거한다.", _text("여러 성이 <E>CB다케다군<E>CZ 앞에 함락되고,\n회유로 배반한 탓에 거성 <E>CC미노와성<E>CZ은\n점차 고립되어 갔다…")),
    Candidate("base", 5492, "C4803703BC79ED0B56DA9D898DE51BCB1955ED2845EAC9CDF365A9BBAFB3C839", "CA16CAAB66DA0AC10D516C653D16105E84ED7DEFEDB702FA4D5DAE0396BB9170", "wording_change_with_layout", "인용 관형절 분절을 제거하고 전달 정보를 압축한다.", _text("적 <E>CB다케다가<E>CZ는 소금 부족에 시달렸고,\n한편, 그 소식은 <E>CC에치고<E>CZ의\n<E>CA[b1448]<E>CZ에게도 전해져 있었다…")),
    Candidate("base", 6233, "C5248EE9720A7D1E39AC8DE492D9A0C5CB0AD2220946219579AFB81D47EC6334", "75961C44FD085D1E1CF5C7EA9116E18E7C4E3BC04B035F526778118FF014FCA7", "wording_change_with_layout", "인용구와 조사 분절을 제거하고 설명을 압축한다.", _text("주인의 따뜻한 대접에 감동한 <E>CA다카토라<E>CZ는\n이후 ‘흰 떡 셋’을\n깃발 문양으로 삼았다고 한다…")),
    Candidate("base", 6365, "E24ABC8A3D1F0CD5CAB70773B8D1D81203A64AE886961B8D5E2C5EEC48E20CAD", "F45B33F6C61E2AA8A321077D50725A339D3C2E90B1AD256089123A7B4B471832", "wording_change_with_layout", "독백의 공백·조사 분절을 제거하고 호흡을 정리한다.", _text("(흠. 내 뜻을 헤아려 처음엔\n미지근한 차를 내고 차츰 뜨겁게 하는\n배려라… 얄미울 만큼 영리하구나)")),
    Candidate("base", 6401, "5F5B596BF8AF4727ACC42F7F3D0A1CED5FD5848F24DBE72757D4435934AD9653", "6728ACA9F46DC98DE86AB6AF3948147D0935028DAE87DEF3708AAF303D387FC5", "wording_change_with_layout", "가문명 뒤 주격 조사 분절을 제거하고 설명을 압축한다.", _text("<E>CC도사<E>CZ <E>CB이치조가<E>CZ는 이름 그대로\n최고위 다섯 공가인 고셋케의 <E>CC이치조가<E>CZ가\n오닌의 난 뒤 <E>CC도사<E>CZ에 뿌리내린 명문이다.")),
    Candidate("base", 6668, "DB2C9C40AF652B527A7A0F7F0F3AF0911EAC4817AEF8C114A7C9E7918B54B4B9", "853AFABFB9C96EBF03EE8B6CC3912BCAC85376CA69C9BAD1D147166E520D7BF5", "hard_break_reflow_only", "인용 종결 연결을 위한 순수 개행 재배치다.", _text("요컨대 <E>CB오다 님<E>CZ의 요망을 받아들여\n<E>CC교<E>CZ로 돌아가실 선택지는 없다…는\n말씀이시군요?")),
    Candidate("base", 7475, "B634713E57D190A2941B5B2EB82471DE9292DF1F06D676A2CBC7A0356A7FC195", "AC2CA0DDD3823AC15D041A78C9B75CA63B9B4556E7358F9FA7F0DC46D4E0EA98", "wording_change_with_layout", "인용 조사 분절을 제거하고 이름 풀이를 간결화한다.", _text("<E>CA다치바나 도세쓰<E>CZ의 딸은 <E>CA긴치요<E>CZ.\n‘긴’은 남의 말을 삼가 듣는다는 뜻.\n그 바람을 담은 이름이었다.")),
    Candidate("base", 9580, "DD6CC5003B8BA3F016262358FC13574ACE6221F265E811482775F43623C789E4", "8DBFBCFF4E2D6A1578A5468959296D7D72487A18FEC15CC79584B9966F591E91", "wording_change_with_layout", "인용 관형절 분절을 제거하고 의도를 자연스럽게 정리한다.", _text("양자라 말은 하나, 실은 우리 쪽의\n인질을 원한다는 뜻일 뿐이니라…")),
    Candidate("base", 9585, "D9C04F30ACAA7A4281D7C57B62A547719AFB3D0A0C92C567DA11B6B1D2BE9BE0", "9E358512D51E9DEC5BF82B9D44961A43545F5D553620AD8847E5D9524AD846C2", "wording_change_with_layout", "부자연스러운 요청 표현과 개행을 함께 교정한다.", _text("<E>CA사부로<E>CZ… <E>CB다케다<E>CZ를 멸하기 위해서다.\n아니, <E>CC간토<E>CZ의 안녕을 위해서\n다녀와 주겠는가? 부탁하네!")),
    Candidate("base", 16397, "A1599E172E1F078D6D900184B3E9DDF0EA8C510FF99134964A6EC2D822E80A86", "7D1C276D8445DC3EC16C99527F0A5025E5A447562A50C9A9492F9262C0C83915", "hard_break_reflow_only", "인용구와 목적격 조사를 결합하는 순수 개행 재배치다.", _text("취임하고 싶은 직책을 선택하면 엔딩이\n됩니다. 게임을 계속하려면\n「사퇴하기」를 선택해 주십시오.")),
    Candidate("pk", 3945, "FC803DA0515DF78D18F81E4054702D3F626A0A614F1B3CB968AE24BC35E59EF8", "13CB31B78BD18D15B140D8A011F5EE53252F7355717F836CB084810EF30DEC03", "hard_break_reflow_only", "인용된 사건명을 한 줄에 유지하는 순수 개행 재배치다.", _text("뼈아픈 패배를 당한 <E>CB다케다 측<E>CZ은\n이 싸움을 '도이시 붕괴'라\n불렀다고 한다……")),
    Candidate("pk", 4289, "AC3D3A73DB73EF024F9EC6699A6788DD1E8B163FB2042D1AD1E550CA7C7389A7", "2202F6CFA4FFF75E96C77FA0AEB30885C42F6DB2DB23A17B30291952C1FA03DD", "wording_change_with_layout", "런타임 인물명 뒤 조사를 피하면서 관계를 간결하고 자연스럽게 정리한다.", _text("줄곧 <E>CB[bs1448]<E>CZ 밑에서 일했고,\n<E>CA[bm1448]<E>CZ 옹립에도 힘쓴\n<E>CA오쿠마 도모히데<E>CZ도 <E>CB다케다<E>CZ에 붙었다……")),
    Candidate("pk", 6499, "C0A8BE3AB625CCF0A148DB951231089090F1306083F2FB05B437882E171C162A", "50DBBBE58CEBB18A318C77376AB5865872C198009ADAC7EF6BBC4288CDA0E410", "hard_break_reflow_only", "편제명을 한 줄에 유지하는 순수 개행 재배치다.", _text("<E>CB다케다군<E>CZ 최강의 붉은 군단―\n<E>CA야마가타 마사카게<E>CZ의 싸움은\n이 <E>CC나가시노<E>CZ에서 막을 내렸다.")),
    Candidate("pk", 6662, "31A88292E073DFA1254D73DB6725941DD8D1FD713743D6120E52E3D3901E00C2", "0E19E34C82467031B6674442DFCFE18FA72484309159AE9FE292DEB0434A06B1", "wording_change_with_layout", "수군 고유명사 분절을 제거하고 반격 표현을 자연스럽게 정리한다.", _text("<E>CA오다 노부나가<E>CZ·<E>CA구키 요시타카<E>CZ 주종은\n이 패전의 굴욕을 가슴에 새기고,\n<E>CB모리<E>CZ 수군에 맞선 반격을 맹세했다…")),
    Candidate("pk", 9585, "D9C04F30ACAA7A4281D7C57B62A547719AFB3D0A0C92C567DA11B6B1D2BE9BE0", "9E358512D51E9DEC5BF82B9D44961A43545F5D553620AD8847E5D9524AD846C2", "wording_change_with_layout", "Base와 같은 문장을 동기화해 요청 표현과 개행을 함께 교정한다.", _text("<E>CA사부로<E>CZ… <E>CB다케다<E>CZ를 멸하기 위해서다.\n아니, <E>CC간토<E>CZ의 안녕을 위해서\n다녀와 주겠는가? 부탁하네!")),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    ).encode("utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def safe_resource(root: Path, relative: str | Path) -> Path:
    root = root.resolve(strict=True)
    path = (root / relative).resolve(strict=True)
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise CandidateError(f"resource escapes Steam root: {path}") from exc
    return path


def require_private(path: Path) -> Path:
    path = path.resolve()
    private_root = (REPO / "tmp").resolve()
    try:
        path.relative_to(private_root)
    except ValueError as exc:
        raise CandidateError(f"private output escapes tmp: {path}") from exc
    return path


def atomic_write(path: Path, blob: bytes) -> None:
    path = require_private(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(blob)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def import_tools() -> tuple[Any, Callable[..., Any], Callable[..., Any], Callable[..., Any]]:
    sys.path.insert(0, str(TOOLS))
    import build_common_message_overlay as common
    from nobu16_lz4 import decompress_wrapper, recompress_wrapper
    from nobu16_msg_table import parse_message_table, rebuild_message_table

    return common, decompress_wrapper, recompress_wrapper, (parse_message_table, rebuild_message_table)


def import_font_helper() -> Any:
    require(FONT_HELPER.is_file(), f"event font helper is absent: {FONT_HELPER}")
    module_name = "_pc_event_linebreak_wave9_font_helper"
    spec = importlib.util.spec_from_file_location(module_name, FONT_HELPER)
    if spec is None or spec.loader is None:
        raise CandidateError("cannot load event-font helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_table(path: Path, decompress_wrapper: Callable[..., Any], parse_message_table: Callable[..., Any], rebuild_message_table: Callable[..., Any]) -> tuple[bytes, bytes, Any, Any]:
    packed = path.read_bytes()
    header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts) == raw, f"source table does not round-trip: {path}")
    return packed, header, raw, table


def profile(value: str, common: Any) -> dict[str, Any]:
    invariant = common.message_invariants(value)
    return {
        "esc": invariant["esc"],
        "printf": invariant["printf"],
        "unknown_percent_count": invariant["unknown_percent_count"],
        "controls": invariant["controls"],
        "pua": invariant["pua"],
        "runtime_tokens": RUNTIME_RE.findall(value),
        "leading_whitespace": invariant["leading_whitespace"],
        "trailing_whitespace": invariant["trailing_whitespace"],
    }


def whitespace_free_skeleton(value: str) -> str:
    return re.sub(r"[ \t\r\n]+", "", value)


def validate_tag_boundaries(value: str, identifier: int) -> None:
    for line_number, line in enumerate(LINEBREAK_RE.split(value), start=1):
        active: str | None = None
        for token in ESC_RE.findall(line):
            if token == "\x1bCZ":
                require(active is not None, f"{identifier}: unmatched colour reset on line {line_number}")
                active = None
            else:
                require(active is None, f"{identifier}: nested colour tag on line {line_number}")
                active = token
        require(active is None, f"{identifier}: colour tag crosses a hard break on line {line_number}")


def glyph_report(value: str, advance: Callable[[str], int]) -> dict[str, Any]:
    glyphs: list[str] = []
    for line in LINEBREAK_RE.split(value):
        cursor = 0
        while cursor < len(line):
            if line[cursor] == "\x1b":
                token = line[cursor : cursor + 3]
                require(ESC_RE.fullmatch(token) is not None, "malformed colour token in candidate")
                cursor += 3
                continue
            char = line[cursor]
            require(ord(char) >= 0x20 and char not in {"\x7f"}, f"unexpected control character U+{ord(char):04X}")
            advance(char)
            glyphs.append(char)
            cursor += 1
    return {
        "all_visible_glyphs_have_event_font_advance": True,
        "visible_glyph_count": len(glyphs),
        "unique_visible_glyph_count": len(set(glyphs)),
    }


def runtime_reservations(value: str, table: Any, visual_line_width: Callable[[str, Callable[[str], int]], int], advance: Callable[[str], int]) -> dict[str, int]:
    reservations: dict[str, int] = {}
    for token in sorted(set(RUNTIME_RE.findall(value))):
        identifier = int(re.search(r"\d+", token).group())
        require(identifier < table.string_count, f"runtime token references absent entry: {token}")
        width = visual_line_width(table.texts[identifier], advance)
        require(width > 0, f"runtime token reserves zero width: {token}")
        reservations[token] = width
    return reservations


def width_pairs(value: str, visual_line_width: Callable[[str, Callable[[str], int]], int], advance: Callable[[str], int], reservations: Mapping[str, int]) -> tuple[list[int], list[int]]:
    actual: list[int] = []
    reserved: list[int] = []
    for line in LINEBREAK_RE.split(value):
        width = visual_line_width(line, advance)
        projected = width
        for token in RUNTIME_RE.findall(line):
            require(token in reservations, f"runtime token is not reserved: {token}")
            projected += max(0, reservations[token] - visual_line_width(token, advance))
        actual.append(width)
        reserved.append(projected)
    return actual, reserved


def candidate_groups() -> dict[str, tuple[Candidate, ...]]:
    grouped: dict[str, list[Candidate]] = {key: [] for key in RESOURCE_ORDER}
    for candidate in CANDIDATES:
        require(candidate.resource_key in grouped, f"unknown candidate resource: {candidate.resource_key}")
        grouped[candidate.resource_key].append(candidate)
    result = {key: tuple(sorted(rows, key=lambda row: row.identifier)) for key, rows in grouped.items()}
    require(len(result["base"]) == 15 and len(result["pk"]) == 5, "candidate resource counts differ")
    require(len({(row.resource_key, row.identifier) for row in CANDIDATES}) == 20, "duplicate candidate coordinate")
    return result


def reference_path(steam_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else safe_resource(steam_root, path)


def source_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"path": str(path), "sha256": sha256_bytes(blob), "size": len(blob)}


def build(steam_root: Path) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], dict[str, dict[str, bytes]]]:
    steam_root = steam_root.resolve(strict=True)
    common, decompress_wrapper, recompress_wrapper, table_api = import_tools()
    parse_message_table, rebuild_message_table = table_api
    font_helper = import_font_helper()
    advance, font = font_helper.font_advance_function(steam_root)
    require(font["sha256"] == EXPECTED_FONT_SHA256, f"event font hash differs: {font['sha256']}")
    grouped = candidate_groups()

    audits: dict[str, list[dict[str, Any]]] = {}
    artefacts: dict[str, dict[str, bytes]] = {}
    source_contract: dict[str, Any] = {}

    for resource_key in RESOURCE_ORDER:
        target_path = safe_resource(steam_root, RESOURCE_PATHS[resource_key])
        packed, header, raw, table = load_table(target_path, decompress_wrapper, parse_message_table, rebuild_message_table)
        packed_hash = sha256_bytes(packed)
        require(packed_hash == EXPECTED_WAVE8_PACKED_SHA256[resource_key], f"{resource_key}: Wave8 packed preimage differs: {packed_hash}")
        require(table.string_count == EXPECTED_STRING_COUNTS[resource_key], f"{resource_key}: string count differs")

        references: dict[str, Any] = {}
        reference_tables: dict[str, Any] = {}
        for language, (configured_path, expected_hash) in PC_REFERENCE_SPECS[resource_key].items():
            path = reference_path(steam_root, configured_path)
            ref_packed, _ref_header, _ref_raw, ref_table = load_table(path, decompress_wrapper, parse_message_table, rebuild_message_table)
            ref_hash = sha256_bytes(ref_packed)
            require(ref_hash == expected_hash, f"{resource_key} {language}: PC reference hash differs: {ref_hash}")
            require(ref_table.string_count == table.string_count, f"{resource_key} {language}: coordinate domain differs")
            references[language] = source_spec(path)
            reference_tables[language] = ref_table

        rows = grouped[resource_key]
        reservations = runtime_reservations("\n".join(row.target for row in rows), table, font_helper.visual_line_width, advance)
        final_texts = list(table.texts)
        audit_rows: list[dict[str, Any]] = []

        for candidate in rows:
            current = table.texts[candidate.identifier]
            require(text_hash(current) == candidate.expected_current_sha256, f"{resource_key}:{candidate.identifier}: current text preimage differs")
            require(text_hash(candidate.target) == candidate.expected_target_sha256, f"{resource_key}:{candidate.identifier}: target literal differs")
            require("\x00" not in candidate.target and "\ufffd" not in candidate.target, f"{resource_key}:{candidate.identifier}: unsafe target character")
            require(KANA_OR_HAN_RE.search(candidate.target) is None, f"{resource_key}:{candidate.identifier}: non-Korean CJK residue")
            validate_tag_boundaries(candidate.target, candidate.identifier)
            current_profile = profile(current, common)
            target_profile = profile(candidate.target, common)
            require(current_profile == target_profile, f"{resource_key}:{candidate.identifier}: protected profile differs")

            is_reflow_only = candidate.change_kind == "hard_break_reflow_only"
            skeleton_matches = whitespace_free_skeleton(current) == whitespace_free_skeleton(candidate.target)
            if is_reflow_only:
                require(skeleton_matches, f"{resource_key}:{candidate.identifier}: reflow changed wording")
            else:
                require(not skeleton_matches, f"{resource_key}:{candidate.identifier}: wording candidate is only reflow")

            current_actual, current_reserved = width_pairs(current, font_helper.visual_line_width, advance, reservations)
            target_actual, target_reserved = width_pairs(candidate.target, font_helper.visual_line_width, advance, reservations)
            require(1 <= len(target_actual) <= MAX_LINES, f"{resource_key}:{candidate.identifier}: target line count differs")
            if resource_key == "pk":
                require(max(target_reserved) <= PK_MAX_LINE_PX, f"pk:{candidate.identifier}: reserved width over {PK_MAX_LINE_PX}px")

            glyphs = glyph_report(candidate.target, advance)
            final_texts[candidate.identifier] = candidate.target
            audit_rows.append(
                {
                    "schema": "nobu16.kr.pc-event-linebreak-wave9-candidate.v1",
                    "review_batch": "pc_event_linebreak_wave9_candidate_v1",
                    "resource": RESOURCE_PATHS[resource_key],
                    "id": candidate.identifier,
                    "coordinate": str(candidate.identifier),
                    "change_kind": candidate.change_kind,
                    "rationale": candidate.rationale,
                    "current_ko": current,
                    "proposed_ko": candidate.target,
                    "current_ko_utf16le_sha256": text_hash(current),
                    "proposed_ko_utf16le_sha256": text_hash(candidate.target),
                    "wave8_resource_preimage_sha256": packed_hash,
                    "pc_reference_contexts": {language: ref_table.texts[candidate.identifier] for language, ref_table in reference_tables.items()},
                    "pc_reference_text_sha256": {language: text_hash(ref_table.texts[candidate.identifier]) for language, ref_table in reference_tables.items()},
                    "format_contract": {
                        "protected_profile": "match",
                        "tag_scope_per_line": "match",
                        "runtime_tokens": "match",
                        "printf": "match",
                        "reflow_only_nonwhitespace_skeleton": skeleton_matches if is_reflow_only else None,
                    },
                    "glyph_check": glyphs,
                    "layout": {
                        "font_metric": "PC_RES_JP_res_lang_event_font",
                        "font_sha256": font["sha256"],
                        "current_actual_widths_px": current_actual,
                        "current_reserved_widths_px": current_reserved,
                        "target_actual_widths_px": target_actual,
                        "target_reserved_widths_px": target_reserved,
                        "target_line_count": len(target_actual),
                        "pk_three_lines_912px_enforced": resource_key == "pk",
                        "base_container_width_proven": False if resource_key == "base" else None,
                    },
                    "qa": {
                        "real_game_qa_required": True,
                        "status": "not_run",
                        "steam_game_resource_written": False,
                    },
                    "provenance": {
                        "pc_only": True,
                        "switch_korean_translation_used": False,
                        "historic_korean_translation_used": False,
                    },
                }
            )

        raw_a = rebuild_message_table(table, final_texts)
        raw_b = rebuild_message_table(table, final_texts)
        require(raw_a == raw_b, f"{resource_key}: raw rebuild is not deterministic")
        packed_a = recompress_wrapper(raw_a, header)
        packed_b = recompress_wrapper(raw_a, header)
        require(packed_a == packed_b, f"{resource_key}: packed rebuild is not deterministic")
        _candidate_header, checked_raw = decompress_wrapper(packed_a)
        checked = parse_message_table(checked_raw)
        require(checked_raw == raw_a and checked.texts == tuple(final_texts), f"{resource_key}: candidate parse round-trip differs")
        require(rebuild_message_table(checked, checked.texts) == checked_raw, f"{resource_key}: candidate rebuild round-trip differs")
        changed_ids = [identifier for identifier, pair in enumerate(zip(table.texts, checked.texts)) if pair[0] != pair[1]]
        expected_ids = [row.identifier for row in rows]
        require(changed_ids == expected_ids, f"{resource_key}: unexpected changed coordinates: {changed_ids}")

        audits[resource_key] = audit_rows
        artefacts[resource_key] = {"packed": packed_a, "raw": raw_a}
        source_contract[resource_key] = {
            "resource": RESOURCE_PATHS[resource_key],
            "source": source_spec(target_path),
            "references": references,
            "string_count": table.string_count,
            "candidate_ids": expected_ids,
            "candidate_count": len(expected_ids),
            "deterministic_rebuild": {
                "raw": True,
                "packed": True,
                "candidate_parse_rebuild": True,
                "nonselected_texts": True,
            },
            "candidate": {
                "packed_sha256": sha256_bytes(packed_a),
                "raw_sha256": sha256_bytes(raw_a),
                "packed_size": len(packed_a),
                "raw_size": len(raw_a),
            },
        }

    summary = {
        "schema": "nobu16.kr.pc-event-linebreak-wave9-summary.v1",
        "scope": {
            "base_resource": BASE_RESOURCE,
            "base_candidate_count": len(audits["base"]),
            "pk_resource": PK_RESOURCE,
            "pk_candidate_count": len(audits["pk"]),
            "total_candidate_count": sum(len(rows) for rows in audits.values()),
        },
        "inputs": source_contract,
        "font": {"resource": "RES_JP/res_lang.bin", "sha256": font["sha256"], "metric": "PC_RES_JP_res_lang_event_font"},
        "layout_policy": {
            "base": {"max_lines_checked": MAX_LINES, "container_width_proven": False, "real_game_qa_required": True},
            "pk": {"max_lines": MAX_LINES, "max_reserved_width_px": PK_MAX_LINE_PX, "enforced": True, "real_game_qa_required": True},
        },
        "provenance": {
            "pc_only": True,
            "switch_korean_translation_used": False,
            "historic_korean_translation_used": False,
        },
        "output_policy": {
            "private_tmp_only_when_write_requested": True,
            "steam_game_resource_written": False,
            "git_stage_or_commit_written": False,
            "release_or_overlay_written": False,
        },
        "real_game_qa": {"all_20_entries_required": True, "status": "not_run"},
    }
    return audits, summary, artefacts


def write_private(audits: Mapping[str, list[dict[str, Any]]], summary: Mapping[str, Any], artefacts: Mapping[str, Mapping[str, bytes]]) -> dict[str, Any]:
    root = require_private(TMP_ROOT)
    audit_path = root / "audit.v1.jsonl"
    summary_path = root / "summary.v1.json"
    candidate_root = root / "candidate"
    rows = [row for key in RESOURCE_ORDER for row in audits[key]]
    atomic_write(audit_path, jsonl_bytes(rows))
    atomic_write(summary_path, canonical_json(summary))

    candidate_entries: list[dict[str, Any]] = []
    for key in RESOURCE_ORDER:
        relative = Path(RESOURCE_PATHS[key])
        target = require_private(candidate_root / relative)
        atomic_write(target, artefacts[key]["packed"])
        candidate_entries.append(
            {
                "resource": relative.as_posix(),
                "relative_path": str(target.relative_to(root)).replace("\\", "/"),
                "packed_sha256": sha256_bytes(artefacts[key]["packed"]),
                "raw_sha256": sha256_bytes(artefacts[key]["raw"]),
            }
        )

    manifest = {
        "schema": "nobu16.kr.pc-event-linebreak-wave9-build-manifest.v1",
        "workstream": WORKSTREAM.name,
        "audit": {"relative_path": str(audit_path.relative_to(root)).replace("\\", "/"), "sha256": sha256_bytes(audit_path.read_bytes())},
        "summary": {"relative_path": str(summary_path.relative_to(root)).replace("\\", "/"), "sha256": sha256_bytes(summary_path.read_bytes())},
        "candidates": candidate_entries,
        "output_policy": {
            "private_tmp_only": True,
            "steam_game_resource_written": False,
            "git_stage_or_commit_written": False,
            "release_or_overlay_written": False,
        },
        "real_game_qa_required": True,
        "switch_korean_translation_used": False,
    }
    manifest_path = root / "build_manifest.v1.json"
    atomic_write(manifest_path, canonical_json(manifest))
    return {"root": str(root), "audit": str(audit_path), "summary": str(summary_path), "manifest": str(manifest_path)}


def validate(steam_root: Path = DEFAULT_STEAM_ROOT) -> dict[str, Any]:
    audits, summary, _artefacts = build(steam_root)
    return {
        "status": "ok",
        "base_candidate_count": len(audits["base"]),
        "pk_candidate_count": len(audits["pk"]),
        "total_candidate_count": summary["scope"]["total_candidate_count"],
        "base_ids": summary["inputs"]["base"]["candidate_ids"],
        "pk_ids": summary["inputs"]["pk"]["candidate_ids"],
        "steam_game_resource_written": False,
        "write_scope": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--write", action="store_true", help="write only private candidate/audit/manifest files under tmp")
    args = parser.parse_args()
    try:
        audits, summary, artefacts = build(args.steam_root)
        written = write_private(audits, summary, artefacts) if args.write else None
        print(
            json.dumps(
                {
                    "status": "ok",
                    "base_candidate_count": len(audits["base"]),
                    "pk_candidate_count": len(audits["pk"]),
                    "total_candidate_count": summary["scope"]["total_candidate_count"],
                    "steam_game_resource_written": False,
                    "write_scope": "tmp" if args.write else "none",
                    "private_outputs": written,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    except (CandidateError, OSError, ValueError, KeyError, IndexError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
