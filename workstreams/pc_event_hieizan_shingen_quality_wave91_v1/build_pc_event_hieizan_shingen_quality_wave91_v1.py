#!/usr/bin/env python3
"""Build the private W91 Hieizan/Shingen event-quality candidate from W90.

The candidate reads exactly the verified W90 event candidate.  PC JP is the
translation source; direct PC EN/SC/TC are read-only context witnesses.  It
writes only beneath this workstream's private ``tmp`` root and never touches
Steam, Git, a remote, or a release.
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

# W90 contributes only stable parsing/control helpers.  The strict content
# predecessor is independently pinned below.
W90_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_xavier_quality_wave90_v1"
    / "build_pc_event_xavier_quality_wave90_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_xavier_quality_wave90_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W90_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "CF7AAF9F961DB855C52BFD7863EAA6482B830088B5E8A23759191DBC03F21DF8",
    "raw_size": 995_092,
    "sha256": "3D579EA37A68FE18379D961327EBB21BF2AB23E2130C96449539B1970EFC0CB5",
    "size": 999_020,
}

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

# 5955 closes the Honganji scene; 5977 begins Motonari's spring banquet.
SCENE_IDS = tuple(range(5_956, 5_977))
CHANGED_IDS = (
    5_956,
    5_957,
    5_958,
    5_959,
    5_960,
    5_961,
    5_962,
    5_963,
    5_964,
    5_965,
    5_966,
    5_967,
    5_968,
    5_969,
    5_971,
    5_972,
    5_973,
    5_974,
    5_975,
    5_976,
)
RETAINED_IDS = (5_970,)

# Static-patch-007 PK event layout: raw G1N 48/24 advances, maximum four
# semantic lines.  Effective 30px widths are evidence only, not a second gate.
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# Both dynamic references resolve scene-locally to the current full name.
# This is a conservative layout reservation, not a runtime observation.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[b1251]": {
        "display": "다케다 하루노부",
        "source_slot_id": 1251,
        "reserved_raw_g1n_width_px": 360,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W91 officer-name slot 1251; conservative full-name reservation",
    },
    "[bm1251]": {
        "display": "다케다 하루노부",
        "source_slot_id": 1251,
        "reserved_raw_g1n_width_px": 360,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W91 officer-name slot 1251; conservative full-name reservation",
    },
}
ROW_RUNTIME_TOKENS: Mapping[int, tuple[str, ...]] = {
    5958: ("[b1251]",),
    5959: ("[bm1251]",),
    5965: ("[bm1251]",),
    5966: ("[bm1251]",),
    5972: ("[bm1251]",),
    5973: ("[bm1251]",),
    5974: ("[bm1251]",),
    5976: ("[b1251]",),
}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    5956: (
        f"{E}CA노부나가{E}CZ가 히에이산을 불태운 일의 충격은\n"
        "전국 각지에 퍼졌고, 당연히\n"
        f"{E}CA노부나가{E}CZ를 비난하는 목소리도\n"
        "적지 않았다."
    ),
    5957: (
        f"그중 {E}CA노부나가{E}CZ를 특히 격노하게 한 것은,\n"
        "평소 신앙에 열심이지 않았다고 알려진\n"
        "어느 다이묘의 비판이었다."
    ),
    5958: f"{E}CA[b1251]{E}CZ에게서 터무니없는 서신이\n왔다고 하더군.",
    5959: (
        f"그 {E}CA[bm1251]{E}CZ 입도 녀석!\n"
        "출가한 몸이면서도 전쟁만 일삼는\n"
        "탐욕스러운 중 주제에, 건방지게도\n"
        "의견을 보내 왔어. 보아라."
    ),
    5960: (
        "실례하겠습니다. 읽어 보지요……\n"
        "‘요즈음 그대의 행실은\n"
        "신불을 두려워하지 않는,\n"
        "더없이 불경한 짓이오.’"
    ),
    5961: "‘그대 같은 천마의 화신을\n그대로 둘 수는 없다.\n머지않아 상경해 그 목을 취하겠다.’",
    5962: "그 말씀은 곧,\n우리와 절교하고 싶다는 뜻입니까……?",
    5963: (
        f"지금까지 {E}CB오다 가문{E}CZ과 {E}CB다케다 가문{E}CZ은\n"
        "겉으로나마 우호 관계를 유지했고,\n"
        "정면으로 적대한 적은 없었다."
    ),
    5964: "그러나 이 도발적인 글귀는\n지금까지의 관계를 청산하고\n적대 관계로 돌아서겠다는\n선언처럼 읽혔다.",
    5965: (
        f"흥, {E}CA[bm1251]{E}CZ 녀석도 진심으로\n"
        "우리 적이 될 생각은 없겠지.\n"
        "그래도 출가한 몸이니, 히에이산 일에\n"
        "불평을 늘어놓은 정도일 게다."
    ),
    5966: (
        f"그러고 보니 소각 때 {E}CC히에이산{E}CZ을 떠난\n"
        f"천태좌주 {E}CA가쿠조 법친왕{E}CZ이 {E}CC가이{E}CZ에서\n"
        f"{E}CA[bm1251]{E}CZ의 보호를 받고 있다는\n"
        "소문입니다."
    ),
    5967: "그 법친왕의 연줄로 조정에서\n권승정의 지위를 받더니 우쭐해진 게야.\n서신의 서명을 보아라.",
    5968: "오, 이거군요?\n‘천태좌주 사문 신겐’이라니……\n이거 참……",
    5969: "그놈, 천태좌주를 보호했을 뿐인데\n자기가 천태종을 대표하는 양\n여기고 있군.",
    5971: (
        "놈이 불교를 수호하겠다고 큰소리친다면,\n"
        "이쪽은 수행을 방해하는 마왕이라\n"
        "자칭해 주지. ‘제육천마왕’은 어떠냐?"
    ),
    5972: (
        "‘제육천마왕’ 말입니까……\n"
        f"{E}CA[bm1251]{E}CZ의 거짓된 불도 수행을\n"
        "방해하겠다는 풍자인지요?"
    ),
    5973: (
        "그래. 하지만…… 이제는\n"
        f"{E}CA[bm1251]{E}CZ 입도와 제대로 결판을\n"
        "내야 할 때가 다가왔는지도 모르겠군."
    ),
    5974: (
        f"오늘날에도 {E}CA노부나가{E}CZ를 묘사할 때 쓰이는\n"
        f"‘제육천마왕’은 {E}CA[bm1251]{E}CZ에게 보낸\n"
        "답서에서 풍자로 자칭한 말이라고\n"
        "전해진다."
    ),
    5975: (
        "하지만 두 사람이 풍자를 주고받던\n"
        f"서신과는 달리, {E}CB오다 가문{E}CZ과 {E}CB다케다 가문{E}CZ의\n"
        "관계는 점차 긴장감을 띠기 시작했다."
    ),
    5976: (
        f"{E}CA오다 노부나가{E}CZ와 {E}CA[b1251]{E}CZ―\n"
        "난세의 두 거두는 결전의 날이\n"
        "머지않았음을 서로 의식하기 시작했다."
    ),
}

RATIONALES: Mapping[int, str] = {
    5956: "히에이산을 불태운 주체와 전국적 충격·비난을 자연스러운 내레이션으로 복원",
    5957: "신앙에 열심이지 않았다고 알려진 다이묘라는 원문의 수식 관계를 복원",
    5958: "부자연스러운 ‘당치도 않은’을 서신의 성격에 맞는 ‘터무니없는’으로 교정",
    5959: "출가한 몸·전쟁만 일삼음·탐욕스러운 중이라는 비난을 의미 단위로 재배치",
    5960: "행실과 신불을 두려워하지 않는 불경을 인용문 문체로 자연화",
    5961: "‘목을 받겠다’ 직역을 원문의 위협 의미에 맞는 ‘목을 취하겠다’로 교정",
    5962: "手切れ의 관계 단절 의문을 자연스러운 발화로 복원",
    5963: "表向き의 겉으로나마 우호와 정면 적대 부재를 보존",
    5964: "도발적 문구가 적대 관계 전환 선언처럼 읽힌다는 인과를 명확화",
    5965: "출가한 몸이라는 유보와 히에이산 소각에 대한 불평의 뉘앙스를 복원",
    5966: "가쿠조 법친왕의 이탈·가이에서의 보호라는 소문 관계를 명료화",
    5967: "법친왕의 연줄로 받은 권승정 지위와 자만의 인과를 보존",
    5968: "‘천태좌주 사문 신겐’ 서명에 대한 놀람을 자연스럽게 정리",
    5969: "천태좌주 보호를 천태종 대표권으로 착각하는 오만을 자연화",
    5971: "불교 수호를 자처한 상대에 대한 제육천마왕 풍자를 원문 의미대로 복원",
    5972: "거짓된 불도 수행을 방해하겠다는 풍자의 대상을 명확화",
    5973: "本気で決着의 뜻을 ‘제대로 결판’으로 복원",
    5974: "오늘날 제육천마왕이라는 표현의 답서 기원과 풍자적 자칭을 명확화",
    5975: "서신의 풍자와 달리 오다·다케다 관계가 긴장된다는 대비를 복원",
    5976: "난세의 두 거두가 결전이 머지않음을 서로 의식했다는 결말을 재배치",
}

TARGET_RAW_WIDTHS: Mapping[int, tuple[int, ...]] = {
    5956: (960, 624, 672, 288),
    5957: (912, 864, 600),
    5958: (936, 336),
    5959: (696, 744, 768, 600),
    5960: (696, 504, 552, 528),
    5961: (576, 480, 816),
    5962: (312, 816),
    5963: (816, 768, 672),
    5964: (600, 624, 576, 384),
    5965: (840, 648, 840, 672),
    5966: (840, 792, 864, 264),
    5967: (648, 888, 504),
    5968: (312, 672, 216),
    5969: (768, 648, 288),
    5971: (912, 744, 840),
    5972: (552, 864, 576),
    5973: (504, 864, 840),
    5974: (912, 936, 744, 216),
    5975: (768, 960, 840),
    5976: (768, 672, 864),
}

# Pinned from the one-time read-only W91 profile pass against strict W90.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "D021E15C4961C40287A76EBBC9B869CE69649D3898BD1F424842314CE6A5B233",
    "raw_size": 995_332,
    "sha256": "57EE87EE6899A4A723187AFA03AC0974D3BAB7085976BF845B775BDBD62818EF",
    "size": 999_261,
}


class Wave91Error(RuntimeError):
    """Raised when the strict predecessor, layout, or candidate drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave91Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave91Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W90_BUILDER.is_file(), f"W90 helper builder missing: {W90_BUILDER}")
w90 = load_module("pc_event_wave90_base_for_wave91", W90_BUILDER)
parse_table = w90.parse_table
core = w90.core
control_signature = w90.control_signature
is_full_width_visible = w90.is_full_width_visible


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
        raise Wave91Error(f"candidate escapes tmp root: {resolved}") from exc
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
    require(set(SCENE_RUNTIME_RESERVATIONS) == {"[b1251]", "[bm1251]"}, "W91 reservation scope drift")
    for token, reservation in SCENE_RUNTIME_RESERVATIONS.items():
        display = reservation.get("display")
        configured_raw = reservation.get("reserved_raw_g1n_width_px")
        require(isinstance(display, str) and display, f"invalid W91 reservation display: {token}")
        require(type(configured_raw) is int and configured_raw > 0, f"invalid W91 reservation raw width: {token}")
        require(raw_width(display) == configured_raw, f"W91 reservation raw width drift: {token}")
        require(reservation.get("scene_limited") is True, f"W91 reservation not scene-limited: {token}")
        require(reservation.get("runtime_proven") is False, f"W91 runtime proof unexpectedly asserted: {token}")


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
            require(reservation is not None, f"missing W91 scene reservation: {token}")
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
    require(tuple(TARGETS) == CHANGED_IDS, "W91 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W91 retained scope drift")
    require(set(TARGET_RAW_WIDTHS) == set(CHANGED_IDS), "W91 target metrics scope drift")
    validate_runtime_reservations()
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(runtime_tokens(target) == ROW_RUNTIME_TOKENS.get(entry_id, ()), f"W91 runtime token scope drift: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W91 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W91 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id], f"W91 pinned target widths drift: {entry_id}")


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W90 candidate file scope drift: {sorted(actual_files)}")

    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W90 Hieizan predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W90_PROFILE, "W90 on-disk event profile drift")
    require(w90.EXPECTED_OUTPUT_PROFILE == EXPECTED_W90_PROFILE, "W90 pinned output profile drift")

    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W90_PROFILE, "W90 audit output profile drift")
    require(manifest.get("output") == EXPECTED_W90_PROFILE, "W90 manifest output profile drift")
    return event, table, raw, predecessor_profile


def load_direct_contexts() -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
    tables: dict[str, Any] = {}
    profiles: dict[str, Mapping[str, Any]] = {}
    for language, path in DIRECT_CONTEXT_PATHS.items():
        resolved = path.resolve(strict=True)
        parts = {part.casefold() for part in resolved.parts}
        require("switch" not in parts, f"non-PC context source forbidden: {resolved}")
        event = resolved.read_bytes()
        _header, raw, table = parse_table(f"direct PC {language.upper()} W91 context", event)
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
        require(all((current, source_jp, source_en, source_sc, source_tc)), f"empty W91 row: {entry_id}")

        current_signature = control_signature(current)
        source_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == source_signature, f"W90/direct-PC-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W91 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        require(runtime_tokens(target) == ROW_RUNTIME_TOKENS.get(entry_id, ()), f"W91 runtime token differs in row: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W91 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W91 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")

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
                "w90_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "direct_pc_en_utf16le_sha256": text_hash(source_en),
                "direct_pc_sc_utf16le_sha256": text_hash(source_sc),
                "direct_pc_tc_utf16le_sha256": text_hash(source_tc),
                "w90_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "review_disposition": "changed" if target != current else "retained_after_review",
                "rationale": RATIONALES.get(entry_id, "direct PC JP/EN/SC/TC context revalidated; retained"),
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

    require(tuple(sorted(changed)) == CHANGED_IDS, "W91 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W90 Hieizan predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W91 Hieizan/Shingen event", event)
    require(after_raw == rebuilt_raw, "W91 raw reparse mismatch")
    require({index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS), "W91 actual event diff scope drift")

    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W91 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W91 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-hieizan-shingen-quality-wave91-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W90 PC Korean candidate plus direct PC JP/EN/SC/TC context",
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
        "input_w90_event_profile": predecessor_profile,
        "direct_pc_context_profiles": context_profiles,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-hieizan-shingen-quality-wave91-manifest.v1",
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
    require(not output.exists(), f"W91 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W91 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W91 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W91 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W91 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W91 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W91 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_hieizan_shingen_quality_wave91_v1.py",
        WORKSTREAM / "test_pc_event_hieizan_shingen_quality_wave91_v1.py",
    ):
        require(path.is_file(), f"W91 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W91 trailing whitespace: {path.name}:{number}")


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
