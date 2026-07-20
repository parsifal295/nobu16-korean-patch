#!/usr/bin/env python3
"""Build the private W92 Honnōji-aftermath event-quality candidate from W91.

This workstream is deliberately private.  It consumes exactly the pinned W91
candidate and uses direct PC JP/EN/SC/TC tables only as review witnesses.
Its only output is below its own ``tmp`` root; it never writes Steam resources,
performs Git operations, or publishes a release.
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

# W91 supplies only parsing, packing, and control-signature helpers.  The
# strict content predecessor is pinned independently below.
W91_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_hieizan_shingen_quality_wave91_v1"
    / "build_pc_event_hieizan_shingen_quality_wave91_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_hieizan_shingen_quality_wave91_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W91_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "D021E15C4961C40287A76EBBC9B869CE69649D3898BD1F424842314CE6A5B233",
    "raw_size": 995_332,
    "sha256": "57EE87EE6899A4A723187AFA03AC0974D3BAB7085976BF845B775BDBD62818EF",
    "size": 999_261,
}

# These are direct PC resources.  The pinned JP backup is the pre-localization
# original; EN/SC/TC are read-only context witnesses, not text inputs.
DIRECT_CONTEXT_PATHS: Mapping[str, Path] = {
    "jp": Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
        r"\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msgev.bin"
    ),
    "en": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin"),
    "sc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin"),
    "tc": Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin"),
}
EXPECTED_CONTEXT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    "jp": {
        "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
        "raw_size": 894_800,
        "sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
        "size": 562_226,
    },
    "en": {
        "raw_sha256": "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
        "raw_size": 1_878_836,
        "sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
        "size": 762_196,
    },
    "sc": {
        "raw_sha256": "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E",
        "raw_size": 754_708,
        "sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
        "size": 522_177,
    },
    "tc": {
        "raw_sha256": "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6",
        "raw_size": 744_212,
        "sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
        "size": 524_909,
    },
}
EXPECTED_CONTEXT_ROW_COUNT = 17_916

# This is a complete, self-contained aftermath scene: the status card,
# Hideyoshi's march and Yamazaki, then Mitsuhide's end.  7850 begins a new
# scene and is intentionally out of scope.
SCENE_IDS = tuple(range(7_816, 7_850))
CHANGED_IDS = (
    7_817,
    7_818,
    7_819,
    7_820,
    7_821,
    7_823,
    7_824,
    7_825,
    7_827,
    7_828,
    7_829,
    7_830,
    7_831,
    7_833,
    7_834,
    7_835,
    7_836,
    7_838,
    7_839,
    7_841,
    7_842,
    7_845,
    7_846,
    7_847,
    7_848,
    7_849,
)
RETAINED_IDS = (7_816, 7_822, 7_826, 7_832, 7_837, 7_840, 7_843, 7_844)

# Static patch 007 baseline: the PK event widget permits four semantic lines.
# Use original-G1N 48/24 advances and enforce raw <= 960.  The 30px effective
# width is recorded as evidence only, never as a second layout gate.
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# This is a scene-local conservative reservation, not proof of the runtime
# replacement.  It derives from the checked officer-name slot 754 only.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[b754]": {
        "display": "기노시타 히데요시",
        "source_slot_id": 754,
        "reserved_raw_g1n_width_px": 408,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "officer-name slot 754; conservative full-name reservation for this scene only",
    },
    "[bs754]": {
        "display": "기노시타",
        "source_slot_id": 754,
        "reserved_raw_g1n_width_px": 192,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "officer-name slot 754; conservative short-name reservation for this scene only",
    },
}
ROW_RUNTIME_TOKENS: Mapping[int, tuple[str, ...]] = {
    7_816: ("[b754]",),
    7_827: ("[b754]",),
    7_830: ("[b754]",),
    7_841: ("[bs754]",),
}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    7817: (
        "미천한 출신에서 제 실력 하나로\n"
        "입신한, 사람을 끄는 사내.\n"
        "그 역시 전국시대가 아니었다면\n"
        "두각을 나타내지 못했을 인재일지 모른다."
    ),
    7818: (
        f"‘무명 {E}CA도키치{E}CZ’라 불리며, 누구의 부탁도\n"
        "싫은 내색 하나 없이 완벽히 해내는\n"
        "손재주가 뛰어나고 붙임성 좋은 사내였다."
    ),
    7819: (
        f"{E}CA노부나가{E}CZ의 신뢰를 등에 업고 차츰\n"
        "중신의 자리를 꿰찬 그는, 이제 강대한\n"
        f"{E}CB모리 가문{E}CZ도 홀로 압도할 만큼 성장했다."
    ),
    7820: (
        f"설마, {E}CA노부나가{E}CZ 님께서……\n"
        f"{E}CA미쓰히데{E}CZ 놈…… 그런 엄청난 일을\n"
        "저지를 사내였을 줄이야!"
    ),
    7821: (
        "주군께서 돌아가신 건 슬프지만,\n"
        "반대로 생각하면, 이건 호기일지도 모른다.\n"
        "뭐, 누구에게도 그런 말은 못 하겠지만."
    ),
    7823: (
        f"{E}CC교토{E}CZ를 되찾겠다! {E}CA미쓰히데{E}CZ를 베어\n"
        f"{E}CA노부나가{E}CZ 님의 원수를 갚고, 후계자로서\n"
        "천하의 인정을 받겠다!"
    ),
    7824: (
        f"{E}CA노부나가{E}CZ에게 가장 아낌받던 이\n"
        "유능한 인물도 주군의 유지를 이을 자는\n"
        "자신뿐이라 믿고, 기세 좋게 일어섰다——"
    ),
    7825: "저마다 각자의 뜻에 따라\n다음 시대를 짊어지려 하고 있었다……",
    7827: (
        "가문을 따지지 않고 실력 있는 가신을\n"
        f"중용한 {E}CA오다 노부나가{E}CZ가 가장 의지한\n"
        f"무장 쌍벽은 {E}CA아케치 미쓰히데{E}CZ와\n"
        f"{E}CA[b754]{E}CZ였다……"
    ),
    7828: (
        f"{E}CC혼노지{E}CZ의 변으로 옛 주군을 멸하고\n"
        f"새 천하인이 된 {E}CA미쓰히데{E}CZ 앞을\n"
        f"{E}CA히데요시{E}CZ가 가로막은 것도\n"
        "어찌 보면 필연이었을지 모른다."
    ),
    7829: (
        f"{E}CC주고쿠{E}CZ에서 {E}CB모리{E}CZ와 대치하고 있던 그가\n"
        "전격적으로 화친을 맺고,\n"
        f"주군의 원수를 갚고자 {E}CC셋쓰{E}CZ까지\n"
        "달려와 있었던 것이다……"
    ),
    7830: (
        "역시 내 앞길을 가로막는 자는\n"
        f"{E}CA[b754]{E}CZ였던가.\n"
        "생각해 보니, 그와도 기묘한 인연이로다……"
    ),
    7831: (
        f"함께 {E}CA노부나가{E}CZ 님에게 중용된 자끼리,\n"
        "누가 그 야망을 이어받을지……\n"
        "정정당당히 승부를 내자!"
    ),
    7833: (
        "모두, 뒷일은 생각지 마라!\n"
        "노리는 것은 오직 하나……\n"
        f"{E}CA미쓰히데{E}CZ의 목이다!\n"
        "절대로 놈을 놓치지 마라!"
    ),
    7834: (
        f"{E}CC야마자키{E}CZ·{E}CC덴노잔{E}CZ에서 맞선 {E}CA미쓰히데{E}CZ와\n"
        f"{E}CA히데요시{E}CZ는 결전을 벌였다. 기세가 오른\n"
        f"{E}CA히데요시{E}CZ군은 차츰 {E}CA아케치{E}CZ 군세를\n"
        "압박해 갔다."
    ),
    7835: (
        "승리는 거머쥐었다! 하지만 노리는 것은\n"
        f"{E}CA미쓰히데{E}CZ다! 놈을 쓰러뜨리지 못하면……\n"
        "원수를 갚는 싸움은 끝나지 않는다!"
    ),
    7836: (
        "큭…… 분하다!\n"
        "나는 그 사내를…… 이길 수 없단 말인가!\n"
        f"{E}CA노부나가{E}CZ 님의 야망을\n"
        "이을 수 없단 말인가!"
    ),
    7838: (
        "도망칠 수 있겠느냐!\n"
        "패왕을 쓰러뜨린 내가\n"
        "적에게 등을 돌리다니……\n"
        "결단코 그럴 수 없다!"
    ),
    7839: (
        "목숨만 부지하면 다시 일어설 수 있습니다!\n"
        "여기서는 무슨 일이 있어도\n"
        "피하셔야 합니다!"
    ),
    7841: (
        f"승부는 {E}CB[bs754]군{E}CZ의 압승으로 끝났지만,\n"
        f"{E}CA미쓰히데{E}CZ는 간신히 전장을 빠져나와\n"
        f"{E}CC교토{E}CZ를 향해 달렸다.\n"
        "살아남는 것만이 유일한 길이라 믿으며……"
    ),
    7842: f"그러나 운명은 {E}CA미쓰히데{E}CZ의 편이 아니었다.\n{E}CC오구루스 마을{E}CZ에서……",
    7845: "나…… 나는 이런 곳에서\n낙오 무사를 노리는 자의 손에\n삶을 마치는 것인가.",
    7846: "주군을 시해한 자에게……\n…… 이것이 정해진 운명이라는\n…… 말인가…… 크윽……!",
    7847: (
        "역사상 가장 유명한 반역자\n"
        f"{E}CA아케치 미쓰히데{E}CZ. 권력의 정점에 있던\n"
        "기간이 너무 짧아 ‘삼일천하’라\n"
        "불리게 되었다……"
    ),
    7848: "그가 무슨 의도로 주군을 친 것인지는\n이제 와서는 아무도 알 길이 없다……",
    7849: (
        f"확실한 것은 {E}CA노부나가{E}CZ 이후,\n"
        f"시대가 선택한 영웅은 {E}CA미쓰히데{E}CZ가 아니라\n"
        f"{E}CA히데요시{E}CZ였다는 냉혹한 현실뿐이었다……"
    ),
}

RATIONALES: Mapping[int, str] = {
    7816: "직접 PC 원문·다국어 문맥과 동적 인명 토큰을 재확인해 상태 카드 문안을 유지",
    7817: "미천한 출신에서 실력으로 성공한 사람을 끄는 인물이라는 서술을 자연스럽게 복원",
    7818: "‘무명 도키치’의 별명, 부탁을 완벽히 해내는 솜씨와 붙임성을 빠짐없이 복원",
    7819: "노부나가의 신뢰, 단계적 중신 진출, 모리 가문을 홀로 압도할 성장 과정을 복원",
    7820: "노부나가의 죽음과 미쓰히데의 배신에 대한 충격을 자연스러운 대사로 정리",
    7821: "주군의 죽음을 기회로 보는 내심을 뜻 손실 없이 자연스럽게 정리",
    7822: "직접 PC JP/EN/SC/TC 대조 후 원문 의미와 대사 어조가 온전하여 유지",
    7823: "교토 탈환, 원수 갚기, 후계자 인정이라는 세 가지 결의를 명확히 복원",
    7824: "가장 아낌받은 유능한 인물이 자신만이 유지를 이을 자라 믿는 서술을 복원",
    7825: "중복된 ‘저마다’를 고치고 각자의 뜻에 따라 다음 시대를 짊어진다는 뜻을 유지",
    7826: "직접 PC JP/EN/SC/TC 대조 후 다음 천하인에 대한 물음이 온전하여 유지",
    7827: "가문보다 실력을 중시한 노부나가와 두 무장 쌍벽이라는 원문 정보를 복원",
    7828: "혼노지의 변, 새 천하인 미쓰히데, 히데요시의 저지라는 인과를 온전히 복원",
    7829: "모리와의 전격 화친과 셋쓰까지 달려온 목적·경위를 자연스럽게 복원",
    7830: "동적 인명과의 기묘한 인연이라는 독백을 문맥상 자연스러운 줄바꿈으로 정리",
    7831: "함께 중용된 두 사람이 노부나가의 야망을 이을 자리를 다툰다는 뜻을 복원",
    7832: "직접 PC JP/EN/SC/TC 대조 후 주군 시해를 규탄하는 대사가 온전하여 유지",
    7833: "미쓰히데의 목만 노리고 절대 놓치지 말라는 명령을 명료하게 복원",
    7834: "야마자키·덴노잔 결전과 기세를 탄 히데요시군의 점진적 압박을 복원",
    7835: "승리 뒤에도 미쓰히데를 쓰러뜨려야 원수를 갚는 싸움이 끝난다는 뜻을 복원",
    7836: "패배의 분함과 노부나가의 야망을 잇지 못한다는 탄식을 자연스럽게 복원",
    7837: "직접 PC JP/EN/SC/TC 대조 후 퇴각 권유 대사가 온전하여 유지",
    7838: "패왕을 쓰러뜨린 자신이 적에게 등을 돌릴 수 없다는 결의를 복원",
    7839: "살아남아 재기하려면 반드시 피해야 한다는 간언을 자연스럽게 재배치",
    7840: "직접 PC JP/EN/SC/TC 대조 후 불가피한 퇴각 수용 대사가 온전하여 유지",
    7841: "동적 인명 군의 압승, 미쓰히데의 간신한 탈출과 생존만이 길이라는 서술을 복원",
    7842: "운명이 미쓰히데 편이 아니었고 오구루스 마을에서 끝났다는 연결을 복원",
    7843: "직접 PC JP/EN/SC/TC 대조 후 이미 올바른 피격 감탄사 ‘윽!?’여서 유지",
    7844: "직접 PC JP/EN/SC/TC 대조 후 낙오 무사 사냥꾼의 대사가 온전하여 유지",
    7845: "낙오 무사를 노리는 자의 손에 삶을 마친다는 공포를 자연스러운 호흡으로 복원",
    7846: "주군을 시해한 자에게 내려진 운명이라는 마지막 탄식을 문맥에 맞게 복원",
    7847: "짧은 권력 기간 때문에 ‘삼일천하’라 불리게 된 설명을 문법적으로 복원",
    7848: "주군을 친 의도는 이제 아무도 알 수 없다는 역사적 불확실성을 자연스럽게 정리",
    7849: "노부나가 이후 시대가 미쓰히데가 아닌 히데요시를 택한 냉혹한 현실을 복원",
}

TARGET_RAW_WIDTHS: Mapping[int, tuple[int, ...]] = {
    7817: (720, 600, 696, 936),
    7818: (888, 792, 936),
    7819: (768, 864, 912),
    7820: (552, 720, 552),
    7821: (720, 960, 888),
    7823: (768, 888, 504),
    7824: (696, 888, 888),
    7825: (552, 816),
    7827: (840, 816, 696, 552),
    7828: (768, 672, 576, 720),
    7829: (864, 552, 696, 528),
    7830: (672, 576, 936),
    7831: (840, 648, 552),
    7833: (600, 552, 432, 576),
    7834: (840, 888, 744, 288),
    7835: (888, 864, 792),
    7836: (288, 888, 480, 480),
    7838: (456, 480, 528, 480),
    7839: (960, 600, 384),
    7841: (912, 792, 456, 912),
    7842: (936, 456),
    7845: (504, 672, 456),
    7846: (528, 648, 456),
    7847: (600, 840, 696, 360),
    7848: (840, 792),
    7849: (624, 912, 864),
}

# Pinned from the one-time private W92 profile pass against strict W91.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "31E3CA37B1FBD7C30B3D0C403BBDFB1EB32AB6EE29E20D1D47C909DB830A9FFB",
    "raw_size": 995_712,
    "sha256": "E00438466EA21B3E23D5E690EE9820A943214B40B9846AFEDFABA0E34443F8B5",
    "size": 999_642,
}


class Wave92Error(RuntimeError):
    """Raised when the strict predecessor, layout, or candidate drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave92Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave92Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W91_BUILDER.is_file(), f"W91 helper builder missing: {W91_BUILDER}")
w91 = load_module("pc_event_wave91_base_for_wave92", W91_BUILDER)
parse_table = w91.parse_table
core = w91.core
control_signature = w91.control_signature
is_full_width_visible = w91.is_full_width_visible


@dataclass(frozen=True)
class Bundle:
    event: bytes
    changed: Mapping[int, str]
    rows: tuple[Mapping[str, Any], ...]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    profile: Mapping[str, Any]


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave92Error(f"candidate escapes tmp root: {resolved}") from exc
    return resolved


def profile(event: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "sha256": sha256(event),
        "size": len(event),
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
    }


def runtime_tokens(value: str) -> tuple[str, ...]:
    return tuple(RUNTIME_RE.findall(value))


def assert_no_break_inside_tag(value: str) -> None:
    in_colour_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token: {token!r}")
            if token == "\x1bCZ":
                require(in_colour_span, "unpaired ESC close")
                in_colour_span = False
            else:
                require(not in_colour_span, "nested ESC colour span")
                in_colour_span = True
            cursor += 3
            continue
        require(not (in_colour_span and value[cursor] in "\r\n"), "line break inside colour tag")
        cursor += 1
    require(not in_colour_span, "unterminated ESC colour span")


def raw_width(display: str) -> int:
    full = sum(1 for character in display if is_full_width_visible(character))
    half = len(display) - full
    return full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX


def validate_runtime_reservations() -> None:
    require(set(SCENE_RUNTIME_RESERVATIONS) == {"[b754]", "[bs754]"}, "W92 reservation scope drift")
    for token, reservation in SCENE_RUNTIME_RESERVATIONS.items():
        display = reservation.get("display")
        configured_raw = reservation.get("reserved_raw_g1n_width_px")
        require(isinstance(display, str) and display, f"invalid W92 reservation display: {token}")
        require(type(configured_raw) is int and configured_raw > 0, f"invalid W92 reservation raw width: {token}")
        require(raw_width(display) == configured_raw, f"W92 reservation raw width drift: {token}")
        require(reservation.get("scene_limited") is True, f"W92 reservation not scene-limited: {token}")
        require(reservation.get("runtime_proven") is False, f"W92 runtime proof unexpectedly asserted: {token}")


def rendered_display_line(value: str) -> str:
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
            reservation = SCENE_RUNTIME_RESERVATIONS.get(token)
            require(reservation is not None, f"missing W92 scene reservation: {token}")
            rendered.append(str(reservation["display"]))
            cursor = runtime.end()
            continue
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        rendered.append(character)
        cursor += 1
    return "".join(rendered)


def line_metrics(value: str) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        display = rendered_display_line(line)
        full = sum(1 for character in display if is_full_width_visible(character))
        half = len(display) - full
        raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
        rows.append(
            {
                "line_number": line_number,
                "display_string": display,
                "raw_g1n_width_px": raw,
                "effective_width_px": (raw * DRAW_FONT_PX + RAW_FULL_WIDTH_PX - 1) // RAW_FULL_WIDTH_PX,
                "full_width_character_count": full,
                "half_width_character_count": half,
                "over_live_raw_960px": raw > RAW_LINE_LIMIT_PX,
            }
        )
    return tuple(rows)


def reservation_details(value: str) -> list[Mapping[str, Any]]:
    return [{"token": token, **SCENE_RUNTIME_RESERVATIONS[token]} for token in runtime_tokens(value)]


def validate_static_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "W92 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W92 retained scope drift")
    require(set(TARGET_RAW_WIDTHS) == set(CHANGED_IDS), "W92 target metric scope drift")
    validate_runtime_reservations()
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(runtime_tokens(target) == ROW_RUNTIME_TOKENS.get(entry_id, ()), f"W92 runtime token scope drift: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W92 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W92 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id], f"W92 pinned target widths drift: {entry_id}")


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W91 candidate file scope drift: {sorted(actual_files)}")

    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W91 Honnōji-aftermath predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W91_PROFILE, "W91 on-disk event profile drift")
    require(w91.EXPECTED_OUTPUT_PROFILE == EXPECTED_W91_PROFILE, "W91 pinned output profile drift")

    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W91_PROFILE, "W91 audit output profile drift")
    require(manifest.get("output") == EXPECTED_W91_PROFILE, "W91 manifest output profile drift")
    prior_changed = set(audit.get("coverage", {}).get("changed_row_ids", []))
    require(not prior_changed.intersection(SCENE_IDS), "W91 unexpectedly overlaps the W92 scene")
    return event, table, raw, predecessor_profile


def load_direct_contexts() -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
    tables: dict[str, Any] = {}
    profiles: dict[str, Mapping[str, Any]] = {}
    for language, path in DIRECT_CONTEXT_PATHS.items():
        resolved = path.resolve(strict=True)
        parts = {part.casefold() for part in resolved.parts}
        require("switch" not in parts, f"non-PC context source forbidden: {resolved}")
        event = resolved.read_bytes()
        _header, raw, table = parse_table(f"direct PC {language.upper()} W92 context", event)
        source_profile = profile(event, raw)
        require(source_profile == EXPECTED_CONTEXT_PROFILES[language], f"direct PC {language.upper()} profile drift")
        require(len(table.texts) == EXPECTED_CONTEXT_ROW_COUNT, f"direct PC {language.upper()} row count drift")
        tables[language] = table
        profiles[language] = source_profile
    return tables, profiles


def prepare(*, require_output_profile: bool) -> Bundle:
    validate_static_targets()
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    contexts, context_profiles = load_direct_contexts()
    require(all(len(before.texts) == len(table.texts) for table in contexts.values()), "event table topology drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = contexts["jp"].texts[entry_id]
        source_en = contexts["en"].texts[entry_id]
        source_sc = contexts["sc"].texts[entry_id]
        source_tc = contexts["tc"].texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(all((current, source_jp, source_en, source_sc, source_tc)), f"empty W92 row: {entry_id}")

        current_signature = control_signature(current)
        source_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == source_signature, f"W91/direct-PC-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W92 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        require(runtime_tokens(target) == ROW_RUNTIME_TOKENS.get(entry_id, ()), f"W92 runtime token differs in row: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W92 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W92 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")

        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "direct_pc_en": source_en,
                "direct_pc_sc": source_sc,
                "direct_pc_tc": source_tc,
                "w91_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "direct_pc_en_utf16le_sha256": text_hash(source_en),
                "direct_pc_sc_utf16le_sha256": text_hash(source_sc),
                "direct_pc_tc_utf16le_sha256": text_hash(source_tc),
                "w91_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "review_disposition": "changed" if target != current else "retained_after_review",
                "rationale": RATIONALES[entry_id],
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": list(runtime_tokens(target)),
                "runtime_reservations": reservation_details(target),
                "runtime_proven": False,
                "control_signature": target_signature,
            }
        )

    require(tuple(sorted(changed)) == CHANGED_IDS, "W92 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W91 Honnōji-aftermath predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W92 Honnōji aftermath event", event)
    require(after_raw == rebuilt_raw, "W92 raw reparse mismatch")
    require({index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS), "W92 actual event diff scope drift")

    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W92 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W92 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-honnouji-aftermath-quality-wave92-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W91 PC Korean candidate plus direct PC JP/EN/SC/TC context",
            "switch_korean_used": False,
            "japanese_source_line_breaks_used": False,
            "korean_text_shortened_or_deleted": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "release_published": False,
        },
        "layout_policy": {
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "strict_live_raw_line_limit_px": RAW_LINE_LIMIT_PX,
            "max_lines": MAX_LINES,
            "draw_font_px": DRAW_FONT_PX,
            "display_effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_is_report_only": True,
            "runtime_reservations": SCENE_RUNTIME_RESERVATIONS,
            "runtime_reservations_scene_limited": True,
            "runtime_proven": False,
        },
        "coverage": {
            "reviewed_scene_ids": list(SCENE_IDS),
            "reviewed_scene_row_count": len(SCENE_IDS),
            "changed_row_ids": list(CHANGED_IDS),
            "changed_row_count": len(CHANGED_IDS),
            "unchanged_after_review_ids": list(RETAINED_IDS),
            "unchanged_after_review_count": len(RETAINED_IDS),
        },
        "input_w91_event_profile": predecessor_profile,
        "direct_pc_context_profiles": context_profiles,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-honnouji-aftermath-quality-wave92-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": PREDECESSOR_WORKSTREAM,
            "candidate_relative": (PREDECESSOR_CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
            "profile": predecessor_profile,
            "strict_on_disk": True,
        },
        "changed_row_ids": list(CHANGED_IDS),
        "output": event_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event, changed, tuple(rows), audit, manifest, event_profile)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W92 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W92 candidate staging exists: {staging}")
    staging.mkdir(parents=True)
    try:
        event_path = staging / MSGEV
        event_path.parent.mkdir(parents=True)
        event_path.write_bytes(bundle.event)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> Mapping[str, Any]:
    bundle = bundle or prepare(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"W92 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W92 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W92 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W92 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W92 candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": list(CHANGED_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "runtime_proven": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_honnouji_aftermath_quality_wave92_v1.py",
        WORKSTREAM / "test_pc_event_honnouji_aftermath_quality_wave92_v1.py",
    ):
        require(path.is_file(), f"W92 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W92 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        print(write_candidate(prepare(require_output_profile=True)))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    print(json.dumps({"changed_row_ids": list(bundle.changed), "event_profile": bundle.profile}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
