#!/usr/bin/env python3
"""Build the private W70 Anegawa event-quality candidate.

The candidate starts from the pinned W69 PC-only candidate and corrects only
the two non-contiguous Anegawa scene blocks in PK ``msgev.bin``.  It is a
literal, human-reviewed semantic pass: it has no Steam-write, Git, network,
release, or automatic-reflow capability.

Layout uses the user-confirmed static-patch-007 runtime contract, not the
legacy event checker: visible Hangul/Hanja count as raw G1N 48px, other
visible characters count as 24px, and the effective runtime width is
``ceil(raw * 30 / 48)``.  Four lines and 912 effective pixels are allowed.
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
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
W69_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_title_canonical_wave69_v1"
    / "build_pc_event_title_canonical_wave69_v1.py"
)

PK_BODY_START = 3_000
PK_BODY_END = 11_009
EXPECTED_PK_BODY_NONEMPTY_COUNT = 8_006
SCENE_RANGES = (range(5_777, 5_803), range(5_885, 5_915))
MAX_LINES = 4
MAX_EFFECTIVE_LINE_PX = 912
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
RUNTIME_SCALE_NUMERATOR = 30
RUNTIME_SCALE_DENOMINATOR = 48

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")


class Wave70Error(RuntimeError):
    """Raised when an Anegawa source, layout, or output pin drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave70Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave70Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w69 = load_module("pc_event_title_wave69_for_wave70", W69_BUILDER)
w66 = w69.w66
BASE = w69.BASE
PK = w69.PK
MSGDATA = w69.MSGDATA
MSGEV = w69.MSGEV
ALL_RESOURCES = (BASE, PK, MSGDATA, MSGEV)


@dataclass(frozen=True)
class DialogueTarget:
    entry_id: int
    current_ko: str
    target_ko: str
    direct_pc_jp: str
    rationale: str


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Any]
    effective: Mapping[int, str]
    classifications: Mapping[str, tuple[int, ...]]
    rows: tuple[Mapping[str, Any], ...]
    final_record_counts: Mapping[str, int]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# Every target was reviewed against the direct pristine PC Japanese row.  The
# two scene ranges are fully reviewed below; rows not listed here are retained.
TARGETS = (
    DialogueTarget(
        5780,
        "적 된 \x1bCB아자이\x1bCZ 신속히 멸하고\n\x1bCC오미\x1bCZ 차지해야 한다.\n\x1bCA[bm1871]\x1bCZ 후방 지원.",
        "적이 된 이상, \x1bCB아자이\x1bCZ를 신속히 멸하고\n\x1bCC오미\x1bCZ를 우리 것으로 만들어야 한다.\n이번에는 \x1bCA[bm1871]\x1bCZ에게 후방 지원을 부탁해 두었다.",
        "敵に回った以上、速やかに\x1bCB浅井\x1bCZを滅ぼし、\n\x1bCC近江\x1bCZを我らのものにせねばならぬ。\n此度は\x1bCA[bm1871]\x1bCZに後詰を頼んでおいた。",
        "적대 전환·오미 장악·동맹 측 후방 지원을 완결된 한국어 문장으로 복원한다.",
    ),
    DialogueTarget(
        5784,
        "우리가 \x1bCB[bs1871]\x1bCZ 원군을\n청하면, \x1bCB아자이\x1bCZ도 \x1bCB아사쿠라\x1bCZ에\n구원 청할 터. 큰 싸움이 되겠군.",
        "우리가 \x1bCB[bs1871] 가문\x1bCZ에 원군을 청한다면,\n\x1bCB아자이 가문\x1bCZ도 \x1bCB아사쿠라 가문\x1bCZ에 구원을 청하겠지……\n큰 싸움이 되겠군.",
        "こちらが\x1bCB[bs1871]家\x1bCZに援軍を頼むとなれば\nおそらく\x1bCB浅井家\x1bCZも\x1bCB朝倉家\x1bCZを頼るはず…\n大きな戦となりそうですな。",
        "양측의 원군 요청 관계와 가문 단위를 복원한다.",
    ),
    DialogueTarget(
        5785,
        "\x1bCA노부나가\x1bCZ가 \x1bCA[b1871]\x1bCZ 군과\n\x1bCC오미\x1bCZ 진군 소식은 \x1bCC오다니성\x1bCZ에도 닿아,\n\x1bCA나가마사\x1bCZ는 \x1bCA요시카게\x1bCZ에 구원 청했다.",
        "\x1bCA오다 노부나가\x1bCZ가 \x1bCA[b1871]\x1bCZ의 군과 함께\n\x1bCC오미\x1bCZ로 진군한다는 소식이 \x1bCC오다니성\x1bCZ에도 전해지자,\n\x1bCA아자이 나가마사\x1bCZ는 \x1bCA아사쿠라 요시카게\x1bCZ에게 구원을 청했다.",
        "\x1bCA織田信長\x1bCZが\x1bCA[b1871]\x1bCZの軍と共に\n\x1bCC近江\x1bCZへ進軍する報せは\x1bCC小谷城\x1bCZにも伝わり、\n\x1bCA浅井長政\x1bCZは\x1bCA朝倉義景\x1bCZに救援を求めた。",
        "오미 진군 소식에서 아사쿠라 원군 요청까지의 인과와 인명 표기를 복원한다.",
    ),
    DialogueTarget(
        5790,
        "어찌 이럴 수가!!\n의형 배신해 아사쿠라 택한 우리를\n직접 구원 않다니……",
        "어찌 이럴 수가!!\n의형을 배신하면서까지 오랜 인연을 중히 여겨\n아사쿠라 편에 선 우리를 직접 구원하지 않다니……",
        "なんということよ！！\n義兄を裏切ってまで古くからの絆を重んじ、\n味方した我らを自ら救援なされぬとは…",
        "나가마사가 의형을 배신하고 아사쿠라를 택한 동기와 탄식을 복원한다.",
    ),
    DialogueTarget(
        5792,
        "아니다, \x1bCB아사쿠라군\x1bCZ에 기대지 않겠다!\n\x1bCA노부나가\x1bCZ 배신은 내가 택한 길.\n\x1bCB아자이\x1bCZ 병사로 \x1bCA노부나가\x1bCZ 목을 베겠다!",
        "아니다, \x1bCB아사쿠라군\x1bCZ에 기대지 않겠다!\n\x1bCA노부나가\x1bCZ를 배신한 것은 내가 택한 길이다.\n\x1bCB아자이\x1bCZ 병사로 \x1bCA노부나가\x1bCZ의 목을 베겠다!",
        "いや、\x1bCB朝倉兵\x1bCZを当てにはするまい！\n\x1bCA信長\x1bCZを裏切ったは、私自身が決めた道。\n\x1bCB浅井\x1bCZの兵で\x1bCA信長\x1bCZの首を取るぞ！",
        "노부나가 배신과 목을 취한다는 대사의 조사·서술어를 복원한다.",
    ),
    DialogueTarget(
        5795,
        "아닙니다. 난 이미 \x1bCB아자이\x1bCZ 사람.\n오라버니보다 남편 주군을 따르겠습니다.\n마음에 두지 마시고…… 싸우십시오……",
        "아닙니다. 저는 이미 \x1bCB아자이 가문\x1bCZ의 사람입니다.\n오라버니보다 남편이신 주군을 따르겠습니다.\n부디 마음 쓰지 마시고…… 싸우십시오……",
        "いえ、私はすでに\x1bCB浅井家\x1bCZの人間。\n兄よりも夫たる殿について行きまする。\nどうか心置きなく…戦に…",
        "아자이 가문 소속과 남편이자 주군을 따르는 관계를 문법적으로 복원한다.",
    ),
    DialogueTarget(
        5802,
        "\x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ\n\x1bCB아자이\x1bCZ·\x1bCB아사쿠라\x1bCZ 네 다이묘 정예가\n아네가와 전투를 시작한다…",
        "\x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ·\x1bCB아자이\x1bCZ·\x1bCB아사쿠라\x1bCZ……\n네 다이묘의 정예가 모인 회전,\n아네가와 전투가 시작되려 했다……",
        "\x1bCB織田\x1bCZ・\x1bCB[bs1871]\x1bCZ・\x1bCB浅井\x1bCZ・\x1bCB朝倉\x1bCZ…\n四大名の精兵が集う会戦、\n姉川の戦いが始まろうとしていた…",
        "네 다이묘의 정예가 모여 전투가 시작되는 내레이션을 복원한다.",
    ),
    DialogueTarget(
        5885,
        "\x1bCC아네가와\x1bCZ서 \x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ\n대 \x1bCB아자이\x1bCZ·\x1bCB아사쿠라\x1bCZ 연합전은 초반부터\n\x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 우세.",
        "\x1bCC아네가와\x1bCZ에서 격돌한 \x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 연합군과\n\x1bCB아자이\x1bCZ·\x1bCB아사쿠라\x1bCZ 연합군의 전투는\n초반부터 \x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 측이 우세했다.",
        "\x1bCC姉川\x1bCZで激突した\x1bCB織田\x1bCZ・\x1bCB[bs1871]\x1bCZの連合軍と\n\x1bCB浅井\x1bCZ・\x1bCB朝倉\x1bCZの連合軍の戦いは、\n序盤から\x1bCB織田\x1bCZ・\x1bCB[bs1871]\x1bCZ方が有利となっていた。",
        "양 연합군의 격돌과 초반 우세라는 문장 구조를 복원한다.",
    ),
    DialogueTarget(
        5886,
        "\x1bCB아사쿠라군\x1bCZ 맹장 \x1bCA마가라 나오타카\x1bCZ는\n\x1bCB[bs1871]\x1bCZ군 맹공 속 싸우다,\n마지막엔 홀로 적진 돌격해 전사했다.",
        "\x1bCB아사쿠라군\x1bCZ에서 분전한 이는 \x1bCA마가라 나오타카\x1bCZ였다.\n\x1bCB[bs1871]\x1bCZ군의 맹공 속에서 칼을 휘두르며 싸웠으나,\n마지막에는 홀로 적진에 돌격해 전사했다.",
        "\x1bCB朝倉軍\x1bCZの中で気を吐いたのは\x1bCA真柄直隆\x1bCZ。\n\x1bCB[bs1871]軍\x1bCZの猛攻の中、太刀を振るい奮闘するも\n最期は敵陣に単騎で突撃して果てた。",
        "분전·칼을 휘두름·단독 돌격 후 전사의 서술을 복원한다.",
    ),
    DialogueTarget(
        5887,
        "\x1bCB아사쿠라군\x1bCZ이 \x1bCB[bs1871]\x1bCZ\n공격에 패할 때, \x1bCB아자이\x1bCZ 본대도 \x1bCB오다\x1bCZ\n정면공격 받아 패색이 짙어졌다.",
        "\x1bCB아사쿠라군\x1bCZ이 \x1bCB[bs1871]\x1bCZ의 공격에 패퇴할 무렵,\n\x1bCB아자이 가문\x1bCZ의 본대도 \x1bCB오다 가문\x1bCZ의 정면 공격을 받아,\n패색이 짙어지고 있었다.",
        "\x1bCB朝倉隊\x1bCZが\x1bCB[bs1871]\x1bCZの攻撃で敗退するのと同じころ\n\x1bCB浅井家\x1bCZ本隊も、\x1bCB織田家\x1bCZの正面攻撃を受け\n敗色濃厚となっていた。",
        "아사쿠라 패퇴와 아자이 본대의 패색이라는 동시 관계를 복원한다.",
    ),
    DialogueTarget(
        5906,
        "아군 대장 목 들고 \x1bCB오다\x1bCZ 본진 돌입한\n\x1bCA엔도 나오쓰네\x1bCZ는 \x1bCA노부나가\x1bCZ 걸상 앞서\n한 걸음 못 가 전사했다.",
        "아군 대장의 목을 내걸고 \x1bCB오다\x1bCZ 본진에 돌입한\n\x1bCA엔도 나오쓰네\x1bCZ는 \x1bCA노부나가\x1bCZ의 걸상까지 한 걸음을\n남기고, 한을 품은 채 전사했다.",
        "味方の大将首を掲げて\x1bCB織田\x1bCZ本陣へ突入した\n\x1bCA遠藤直経\x1bCZであったが、\x1bCA信長\x1bCZの床几まで\nあと一歩及ばず、無念の討死を遂げた。",
        "아군 대장의 목·노부나가의 걸상 한 걸음 앞·한스러운 전사를 복원한다.",
    ),
    DialogueTarget(
        5909,
        "상관없다. 벌레의 날갯짓일 뿐이다.",
        "상관없다. 벌레의 날갯짓 소리일 뿐이다.",
        "かまわぬ、虫の羽音よ。",
        "羽音의 소리 의미를 한국어 문장에 명시한다.",
    ),
    DialogueTarget(
        5912,
        "\x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 진영은\n대승했지만, \x1bCA나가마사\x1bCZ·\x1bCA요시카게\x1bCZ\n목은 못 베어 두 가문 여력은 남았다.",
        "\x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 진영은 대승에 들떴지만,\n\x1bCA나가마사\x1bCZ와 \x1bCA요시카게\x1bCZ의 목을 벤 것은 아니어서\n두 가문에는 아직 여력이 남아 있었다.",
        "快勝に沸く\x1bCB織田\x1bCZ・\x1bCB[bs1871]\x1bCZ陣営だったが\n\x1bCA浅井長政\x1bCZや\x1bCA朝倉義景\x1bCZの首を挙げたわけでなく\n両家にはまだ余力が残されていた。",
        "대승 뒤에도 두 수장의 목을 얻지 못해 여력이 남은 인과를 복원한다.",
    ),
    DialogueTarget(
        5913,
        "승리로 \x1bCA노부나가\x1bCZ 세력 커지자,\n\x1bCB미요시\x1bCZ·\x1bCC엔랴쿠지\x1bCZ·\x1bCB혼간지\x1bCZ 등이\n반\x1bCA노부나가\x1bCZ 노선 택했다.",
        "오히려 이 승리로 \x1bCA노부나가\x1bCZ의 세력이 커지는 것을\n경계한 \x1bCB미요시\x1bCZ·\x1bCC엔랴쿠지\x1bCZ·\x1bCB혼간지\x1bCZ 등이\n반 \x1bCA노부나가\x1bCZ 노선을 취하기 시작했다.",
        "むしろ、この勝利による\x1bCA信長\x1bCZの勢力拡大を\n警戒し、\x1bCB三好家\x1bCZ・\x1bCC延暦寺\x1bCZそして\x1bCB本願寺\x1bCZなどが\n反\x1bCA信長\x1bCZの姿勢を取り始めていく。",
        "세력 확대에 대한 경계와 반노부나가 자세가 시작된다는 의미를 복원한다.",
    ),
)

EXPECTED_TARGET_IDS = tuple(target.entry_id for target in TARGETS)
EXPECTED_CLASS_COUNTS = {"fresh": 14, "already": 0, "override": 0}
EXPECTED_EVENT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "B03345127B352616014D80041FD70C8D2EC40C7802AA175170C0E1F939B37E41",
    "raw_size": 991_380,
    "sha256": "8D05D35F965210DA9CA2C9E34434C0E5CBCEB51CE769DF4CA2857F17E504B568",
    "size": 995_293,
}
EXPECTED_EVENT_RECORD_COUNT: int | None = 258
EXPECTED_TOTAL_RECORDS: int | None = 717


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(value: Any) -> dict[str, Any]:
    return w66.profile_dict(value)


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave70Error(f"private candidate escapes tmp root: {resolved}") from exc
    return resolved


def target_map() -> dict[int, DialogueTarget]:
    mapped = {target.entry_id: target for target in TARGETS}
    require(len(mapped) == len(TARGETS), "duplicate W70 event target")
    require(tuple(mapped) == EXPECTED_TARGET_IDS, "W70 target order or scope drift")
    return mapped


def scene_ids() -> tuple[int, ...]:
    values = tuple(identifier for segment in SCENE_RANGES for identifier in segment)
    require(values == tuple(sorted(values)), "Anegawa scene ranges are not ascending")
    require(len(values) == len(set(values)) == 56, "Anegawa scene coverage differs")
    return values


def expected_final_profile_dicts() -> dict[str, Mapping[str, Any]]:
    require(EXPECTED_EVENT_PROFILE is not None, "W70 event profile is not pinned")
    expected = {resource: dict(value) for resource, value in w69.expected_final_profile_dicts().items()}
    expected[MSGEV] = dict(EXPECTED_EVENT_PROFILE)
    return expected


def expected_final_record_counts() -> dict[str, int]:
    require(EXPECTED_EVENT_RECORD_COUNT is not None, "W70 event record count is not pinned")
    expected = dict(w69.expected_final_record_counts())
    expected[MSGEV] = EXPECTED_EVENT_RECORD_COUNT
    return expected


def runtime_identifier(token: str) -> int:
    digits = "".join(character for character in token if character.isascii() and character.isdigit())
    require(bool(digits), f"runtime token has no numeric identifier: {token}")
    return int(digits)


def is_full_width_visible(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7AF
        or 0xF900 <= codepoint <= 0xFAFF
    )


def control_signature(value: str) -> Mapping[str, Any]:
    esc_tokens: list[str] = []
    controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token at offset {cursor}")
            esc_tokens.append(token)
            cursor += 3
            continue
        if character not in ("\r", "\n") and unicodedata.category(character) == "Cc":
            controls.append(f"U+{ord(character):04X}")
        cursor += 1
    printf = list(PRINTF_RE.finditer(value))
    percent_offsets = {match.start() for match in printf}
    return {
        "esc_tokens": esc_tokens,
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf],
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in percent_offsets
        ),
        "other_controls": controls,
    }


def rendered_display_line(value: str, texts: tuple[str, ...]) -> str:
    rendered: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token in layout: {token!r}")
            cursor += 3
            continue
        runtime = RUNTIME_RE.match(value, cursor)
        if runtime is not None:
            token = runtime.group(0)
            name_id = runtime_identifier(token)
            require(0 <= name_id < len(texts), f"runtime name is outside PK event table: {token}")
            name = texts[name_id]
            require(LINEBREAK_RE.search(name) is None, f"runtime name contains a line break: {token}")
            require("\x1b" not in name, f"runtime name contains an ESC tag: {token}")
            require(RUNTIME_RE.search(name) is None, f"runtime name nests a runtime token: {token}")
            rendered.append(name)
            cursor = runtime.end()
            continue
        require(unicodedata.category(character) != "Cc", f"unexpected visible control: U+{ord(character):04X}")
        rendered.append(character)
        cursor += 1
    return "".join(rendered)


def line_metrics(value: str, texts: tuple[str, ...]) -> tuple[Mapping[str, Any], ...]:
    metrics: list[Mapping[str, Any]] = []
    for line in LINEBREAK_RE.sub("\n", value).split("\n"):
        display = rendered_display_line(line, texts)
        full_width = sum(1 for character in display if is_full_width_visible(character))
        half_width = len(display) - full_width
        raw_width = full_width * RAW_FULL_WIDTH_PX + half_width * RAW_HALF_WIDTH_PX
        effective_width = (raw_width * RUNTIME_SCALE_NUMERATOR + RUNTIME_SCALE_DENOMINATOR - 1) // RUNTIME_SCALE_DENOMINATOR
        metrics.append(
            {
                "display_string": display,
                "raw_g1n_width_px": raw_width,
                "effective_width_px": effective_width,
                "full_width_character_count": full_width,
                "half_width_character_count": half_width,
                "over_912px": effective_width > MAX_EFFECTIVE_LINE_PX,
            }
        )
    return tuple(metrics)


def body_universe(before: Any, direct_jp: Any) -> tuple[int, ...]:
    require(len(before.texts) > PK_BODY_END and len(direct_jp.texts) > PK_BODY_END, "PK body domain is absent")
    values = tuple(
        identifier
        for identifier in range(PK_BODY_START, PK_BODY_END + 1)
        if before.texts[identifier] and direct_jp.texts[identifier]
    )
    require(len(values) == EXPECTED_PK_BODY_NONEMPTY_COUNT, "PK event-body nonempty coverage drift")
    return values


def overlay_events(w69_blob: bytes) -> tuple[bytes, dict[int, str], dict[str, tuple[int, ...]], tuple[Mapping[str, Any], ...], Mapping[str, Any]]:
    header, _raw, before = w66.w60.parse_table("W69 event", w69_blob)
    direct_jp_blob, _direct_profile = w66.w62.load_direct_jp_event()
    _jp_header, _jp_raw, direct_jp = w66.w60.parse_table("pristine PC JP event", direct_jp_blob)
    require(len(before.texts) == len(direct_jp.texts), "W69/direct-PC-JP event table length drift")
    full_body = body_universe(before, direct_jp)
    reviewed = scene_ids()
    require(set(reviewed).issubset(full_body), "Anegawa review scope falls outside PK event-body universe")
    targets = target_map()
    retained = tuple(identifier for identifier in reviewed if identifier not in targets)
    classes: dict[str, list[int]] = {"fresh": [], "already": [], "override": []}
    effective: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id, target in targets.items():
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        require(current == target.current_ko, f"W69 event KO preimage drift: {entry_id}")
        require(source_jp == target.direct_pc_jp, f"direct PC JP event witness drift: {entry_id}")
        require(control_signature(current) == control_signature(target.target_ko), f"W70 token or tag drift: {entry_id}")
        metrics = line_metrics(target.target_ko, before.texts)
        require(1 <= len(metrics) <= MAX_LINES, f"W70 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_912px"] for metric in metrics), f"W70 effective width exceeds 912px: {entry_id}")
        if current == target.target_ko:
            classes["already"].append(entry_id)
        elif current == target.current_ko:
            classes["fresh"].append(entry_id)
            effective[entry_id] = target.target_ko
        else:
            classes["override"].append(entry_id)
        rows.append(
            {
                "entry_id": entry_id,
                "w69_current_ko": current,
                "target_ko": target.target_ko,
                "direct_pc_jp": source_jp,
                "w69_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target.target_ko),
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "source_manual_lf_count": current.count("\n"),
                "target_manual_lf_count": target.target_ko.count("\n"),
                "target_line_count": len(metrics),
                "target_lines": list(metrics),
                "control_signature": control_signature(target.target_ko),
                "rationale": target.rationale,
            }
        )
    frozen = {name: tuple(values) for name, values in classes.items()}
    require({name: len(values) for name, values in frozen.items()} == EXPECTED_CLASS_COUNTS, f"W70 classification drift: {frozen}")
    texts = list(before.texts)
    for entry_id, value in effective.items():
        texts[entry_id] = value
    raw = w66.w60.core.rebuild_message_table(before, tuple(texts))
    output = w66.w60.core.recompress_wrapper(raw, header)
    _header, output_raw, after = w66.w60.parse_table("W70 event", output)
    require(output_raw == raw, "W70 event raw mismatch")
    require({index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(effective), "W70 event scope drift")
    coverage = {
        "semantic_completion": False,
        "full_pk_event_body_range": [PK_BODY_START, PK_BODY_END],
        "full_pk_event_body_nonempty_rows": len(full_body),
        "reviewed_scene_ranges": [[segment.start, segment.stop - 1] for segment in SCENE_RANGES],
        "reviewed_scene_rows": len(reviewed),
        "retained_reviewed_rows": list(retained),
        "corrected_reviewed_rows": list(targets),
        "remaining_full_pk_event_body_rows": len(full_body) - len(reviewed),
    }
    return output, effective, frozen, tuple(rows), coverage


def prepare(*, require_output_profiles: bool) -> Bundle:
    base = w69.prepare(require_output_profiles=True)
    w69.verify_private_candidate(base)
    event_output, effective, classes, rows, coverage = overlay_events(base.outputs[MSGEV])
    outputs = {BASE: base.outputs[BASE], PK: base.outputs[PK], MSGDATA: base.outputs[MSGDATA], MSGEV: event_output}
    require(outputs[BASE] == base.outputs[BASE], "W70 Base retention drift")
    require(outputs[PK] == base.outputs[PK], "W70 PK MSGGAME retention drift")
    require(outputs[MSGDATA] == base.outputs[MSGDATA], "W70 MSGDATA retention drift")
    profiles = {resource: w66.w61.profile(blob) for resource, blob in outputs.items()}
    w45 = w66.w62.load_w45_backups()
    base_records, _ = w66.w60.msggame_counts(w45[BASE], outputs[BASE])
    pk_records, _ = w66.w60.msggame_counts(w45[PK], outputs[PK])
    final_record_counts = {
        BASE: base_records,
        PK: pk_records,
        MSGDATA: 4,
        MSGEV: w66.w60.event_count(w45[MSGEV], outputs[MSGEV]),
    }
    if require_output_profiles:
        require({resource: profile_dict(value) for resource, value in profiles.items()} == expected_final_profile_dicts(), "W70 output profile drift")
        require(final_record_counts == expected_final_record_counts(), "W70 record count drift")
        require(EXPECTED_TOTAL_RECORDS is not None, "W70 total records are not pinned")
        require(sum(final_record_counts.values()) == EXPECTED_TOTAL_RECORDS, "W70 total record drift")
    audit = {
        "schema": "nobu16.kr.pc-event-anegawa-static007-wave70-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "platform": "W69 Steam-PC Korean candidate and pristine PC Japanese only",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "layout_policy": {
            "baseline": "static patch 007",
            "runtime_font_px": 30,
            "line_spacing_setting": 8,
            "max_lines": MAX_LINES,
            "max_effective_line_px": MAX_EFFECTIVE_LINE_PX,
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "raw_equivalent_limit_px": 1440,
            "dynamic_runtime_names": "rendered from the W69 candidate table before measuring",
            "legacy_raw_912px_gate": "forbidden",
        },
        "coverage": coverage,
        "classifications": {name: list(values) for name, values in classes.items()},
        "rows": list(rows),
        "final_record_counts": final_record_counts,
        "final_total_records": sum(final_record_counts.values()),
        "outputs": {resource: profile_dict(profiles[resource]) for resource in ALL_RESOURCES},
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-anegawa-static007-wave70-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {"relative": resource, "output": profile_dict(profiles[resource]), "changed_record_count": final_record_counts[resource]}
            for resource in ALL_RESOURCES
        },
        "final_total_records": sum(final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(outputs, profiles, effective, classes, rows, final_record_counts, audit, manifest)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W70 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W70 candidate staging already exists: {staging}")
    staging.mkdir(parents=True)
    try:
        for relative, blob in bundle.outputs.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> dict[str, Any]:
    bundle = bundle or prepare(require_output_profiles=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"W70 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W70 candidate file scope drift: {sorted(actual_files)}")
    for relative, blob in bundle.outputs.items():
        require((root / relative).read_bytes() == blob, f"W70 candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W70 audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W70 manifest differs")
    return {
        "candidate_root": root.relative_to(REPO).as_posix(),
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "build_pc_event_anegawa_static007_wave70_v1.py",
        WORKSTREAM / "test_pc_event_anegawa_static007_wave70_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"W70 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W70 trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(
        json.dumps(
            {
                "profiles": {resource: profile_dict(value) for resource, value in bundle.profiles.items()},
                "classifications": {name: list(values) for name, values in bundle.classifications.items()},
                "final_record_counts": bundle.final_record_counts,
                "final_total_records": sum(bundle.final_record_counts.values()),
                "line_metrics": {str(row["entry_id"]): row["target_lines"] for row in bundle.rows},
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        return command_profile()
    if command == "build":
        bundle = prepare(require_output_profiles=True)
        write_candidate(bundle)
        print(json.dumps(verify_private_candidate(bundle), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if command == "verify-private":
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    bundle = prepare(require_output_profiles=True)
    source_whitespace_check()
    result = verify_private_candidate(bundle)
    result["private_authoring_whitespace_check"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
