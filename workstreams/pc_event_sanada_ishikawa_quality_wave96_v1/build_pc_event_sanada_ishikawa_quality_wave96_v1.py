#!/usr/bin/env python3
"""Build the private W96 Sanada/Ishikawa scene-quality candidate from W95c.

The only Korean input is the pinned on-disk W95c private candidate.  All 50
scene rows are rechecked against direct PC JP/EN/SC/TC context.  This builder
writes only its own private candidate; it has no Steam, Git, network, or
release operation.
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

W95C_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_tachibana_aftermath_quality_wave95c_v1"
    / "build_pc_event_tachibana_aftermath_quality_wave95c_v1.py"
)
MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_tachibana_aftermath_quality_wave95c_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W95C_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "C511A82E26762C6D5FC2573BE2E5B8B375A88C3B3C27E25FBECF5C51F2C48CA3",
    "raw_size": 995_864,
    "sha256": "2C22342032D494979D3BDE904648BCFD1BE5864169CB6F735B069C8025460BA2",
    "size": 999_795,
}

SCENE_IDS = tuple(range(8_442, 8_492))
CHANGED_IDS = (
    8442,
    8447,
    8449,
    8459,
    8460,
    8463,
    8466,
    8467,
    8471,
    8472,
    8473,
    8476,
    8479,
    8482,
    8484,
    8485,
    8489,
    8490,
)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# Text inside the pre-existing colour spans is corrected where needed, but the
# actual ESC wrappers, token positions, and message-table terminators remain
# exactly structurally compatible with the strict W95c predecessor.
TARGETS: Mapping[int, str] = {
    8442: (
        "\x1bCB오다 가문\x1bCZ 붕괴를 틈타,\n"
        "\x1bCB[bs1871]\x1bCZ·\x1bCB호조\x1bCZ·\x1bCB우에스기\x1bCZ\n"
        "세 세력을 손아귀에 넣고 다이묘로 일어선\n"
        "\x1bCB사나다 가문\x1bCZ——"
    ),
    8447: (
        "악꾀라니 섭섭하구나, \x1bCA노부유키\x1bCZ.\n"
        "나는 언제나 \x1bCB사나다 가문\x1bCZ을\n"
        "생각하고 있거늘."
    ),
    8449: (
        "장수는 \x1bCA[bm1871]\x1bCZ가 신임하는\n"
        "\x1bCA도리이 모토타다\x1bCZ, \x1bCA오쿠보 다다요\x1bCZ,\n"
        "\x1bCA히라이와 지카요시\x1bCZ이며,\n"
        "병력은 우리 군의 네 배다."
    ),
    8459: (
        "그리고 때를 놓치지 않고 \x1bCA마사유키\x1bCZ는\n"
        "추격을 시작했다. \x1bCA도리이 모토타다\x1bCZ 등은\n"
        "이를 막으려 했으나……"
    ),
    8460: (
        "지성에서 뛰쳐나온 \x1bCA노부유키\x1bCZ와\n"
        "\x1bCA요리야스\x1bCZ의 측면 공격까지 받아,\n"
        "마침내 군세는 와해되었다."
    ),
    8463: (
        "이리하여 이 싸움은 \x1bCB사나다 가문\x1bCZ의\n"
        "승리로 끝났다. 이후에도 작은 충돌은\n"
        "계속되었지만……"
    ),
    8466: (
        "하지만 얼마 뒤, \x1bCB사나다\x1bCZ와 \x1bCB우에스기\x1bCZ는 함께\n"
        "곧 \x1bCB[bs754] 가문\x1bCZ에 신종했다."
    ),
    8467: (
        "그리하여 \x1bCB[bs1871] 가문\x1bCZ도 더는\n"
        "\x1bCB사나다\x1bCZ에 손을 댈 수 없게 되어,\n"
        "이를 갈 뿐이었다."
    ),
    8471: (
        "\x1bCA가즈마사\x1bCZ는 \x1bCA[b1871]\x1bCZ의\n"
        "심복이었다. \x1bCB이마가와 가문\x1bCZ에서\n"
        "독립하기 전부터 \x1bCA이에야스\x1bCZ를 섬겨,\n"
        "수많은 전투에서 공을 세웠다."
    ),
    8472: (
        "\x1bCC혼노지\x1bCZ의 변 뒤 정세가 급변하자,\n"
        "\x1bCB[bs1871] 가문\x1bCZ이 가장 중시한\n"
        "\x1bCB[bs754] 가문\x1bCZ을 상대로 한 외교의\n"
        "책임자가 되었다."
    ),
    8473: (
        "\x1bCA이시카와\x1bCZ 님, 요즘 \x1bCB[bs754] 가문\x1bCZ에\n"
        "너무 치우치시는 것 아닙니까?\n"
        "당가의 주장도 제대로 전해\n"
        "협상해 주셔야 합니다."
    ),
    8476: (
        "옛 \x1bCA오다 노부카쓰\x1bCZ의 가로도\n"
        "\x1bCB[bs754] 가문\x1bCZ에 치우쳤다는 이유로\n"
        "\x1bCA노부카쓰\x1bCZ 님에게 베어 죽었다 하오……"
    ),
    8479: (
        "\x1bCA가즈마사\x1bCZ, \x1bCB[bs754] 가문\x1bCZ으로 달아나다——\n"
        "그 충격적인 소식에 \x1bCB[bs1871] 가문\x1bCZ은\n"
        "혼란에 빠졌다. 무리도 아니다.\n"
        "고참 중의 고참이 등을 돌렸다……"
    ),
    8482: (
        "군제를 모두 뜯어고쳐야 한다!\n"
        "\x1bCB다케다 가문\x1bCZ의 옛 가신들에게서 배워,\n"
        "병법을 모두 새롭게 바꾸어야 한다!"
    ),
    8484: "(\x1bCA가즈마사\x1bCZ, 미안하구나.\n그대의 고뇌를 알아차리지 못했구나……)",
    8485: (
        "(군제나 기밀 따위는 잃어도 상관없다.\n"
        "가장 책망받아야 할 자는,\n"
        "그대 같은 심복을 떠나게 한\n"
        "나 자신이다!)"
    ),
    8489: "(\x1bCA[bm1871]\x1bCZ 님, 송구하옵니다.\n이런 사태가 벌어진 것은 결코\n제 본의가 아니옵니다.)",
    8490: (
        "(하지만 안심하시오.\n"
        "나는 \x1bCB[bs754] 가문\x1bCZ 안에서\n"
        "\x1bCB[bs1871] 가문\x1bCZ이 유리하도록\n"
        "힘쓰겠소……)"
    ),
}
RATIONALES: Mapping[int, str] = {
    8442: "오다 가문 붕괴를 계기로 세 세력을 이용해 일어선 사나다 가문의 서술을 복원했다.",
    8447: "악꾀라는 지적에 대한 마사유키의 서운함과 가문을 위한 명분을 자연스럽게 옮겼다.",
    8449: "장수 세 명의 전체 이름과 병력 네 배라는 정보를 빠짐없이 복원했다.",
    8459: "마사유키의 즉시 추격과 도리이 모토타다 등의 저지 시도를 자연스럽게 정리했다.",
    8460: "지성에서 나온 노부유키·요리야스의 측면 공격과 군세 와해를 명확히 했다.",
    8463: "전투의 승패와 이후의 소규모 충돌을 원문 순서대로 정리했다.",
    8466: "사나다와 우에스기가 함께 기노시타 가문에 신종한 시점과 관계를 복원했다.",
    8467: "마츠다이라 가문이 사나다에 손을 쓰지 못하고 이를 간 결말을 복원했다.",
    8471: "가즈마사의 심복 지위, 이마가와 독립 전부터의 봉사, 전공을 모두 복원했다.",
    8472: "혼노지의 변 뒤 마츠다이라가 중시한 기노시타 외교의 책임자였다는 의미를 복원했다.",
    8473: "상대 가문 편향을 지적하고 당가의 주장을 전해 협상하라는 요구를 복원했다.",
    8476: "노부카쓰의 가로가 기노시타 편향으로 처형되었다는 경고를 복원했다.",
    8479: "가즈마사 이탈의 충격, 가문의 혼란, 원로의 배신이라는 이유를 모두 복원했다.",
    8482: "군제·병법을 다케다 옛 가신에게 배워 전면 개혁해야 한다는 결의를 복원했다.",
    8484: "가즈마사의 고뇌를 알아차리지 못한 후회를 자연스럽게 바로잡았다.",
    8485: "기밀 손실보다 심복을 떠나게 한 자신을 더 탓하는 독백을 복원했다.",
    8489: "사태가 본의가 아니었다는 가즈마사의 사과를 주어까지 포함해 복원했다.",
    8490: "기노시타 가문 안에서 마츠다이라 가문에 유리하도록 힘쓰겠다는 독백을 복원했다.",
}
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[b1871]": {
        "source_slot_id": 1871,
        "display": "마츠다이라 모토야스",
        "reserved_raw_g1n_width_px": 456,
        "scene_limited": True,
        "runtime_proven": False,
    },
    "[bm1871]": {
        "source_slot_id": 1871,
        "display": "마츠다이라 모토야스",
        "reserved_raw_g1n_width_px": 456,
        "scene_limited": True,
        "runtime_proven": False,
    },
    "[bs1871]": {
        "source_slot_id": 1871,
        "display": "마츠다이라",
        "reserved_raw_g1n_width_px": 240,
        "scene_limited": True,
        "runtime_proven": False,
    },
    "[bs754]": {
        "source_slot_id": 754,
        "display": "기노시타",
        "reserved_raw_g1n_width_px": 192,
        "scene_limited": True,
        "runtime_proven": False,
    },
}

# Pinned after the deterministic profile and layout pass.  Any later source or
# helper drift therefore fails closed before a private candidate is emitted.
TARGET_RAW_WIDTHS: Mapping[int, tuple[int, ...]] | None = {
    8442: (528, 576, 936, 312),
    8443: (696, 624, 624),
    8444: (504, 672, 792),
    8445: (552, 552, 840),
    8446: (432, 480, 744),
    8447: (720, 600, 384),
    8448: (504, 504, 480),
    8449: (888, 744, 528, 600),
    8450: (816, 888, 720),
    8451: (384, 792, 696),
    8452: (720, 360, 528),
    8453: (696, 816),
    8454: (792, 504, 480),
    8455: (696, 528, 816),
    8456: (864,),
    8457: (600, 576, 720),
    8458: (360, 624, 720),
    8459: (816, 888, 480),
    8460: (672, 720, 600),
    8461: (840, 504, 648),
    8462: (624, 456, 864),
    8463: (768, 840, 336),
    8464: (744, 504, 600),
    8465: (864, 624, 744),
    8466: (960, 672),
    8467: (744, 720, 408),
    8468: (624, 624, 768),
    8469: (480, 744),
    8470: (432, 456, 456),
    8471: (768, 696, 768, 672),
    8472: (744, 696, 768, 384),
    8473: (792, 672, 600, 504),
    8474: (672, 648, 648),
    8475: (528, 528, 912),
    8476: (600, 792, 816),
    8477: (840, 528, 888),
    8478: (720, 576, 168),
    8479: (912, 864, 696, 720),
    8480: (432, 360, 624),
    8481: (504, 552, 432),
    8482: (672, 840, 792),
    8483: (648, 816, 720),
    8484: (528, 864),
    8485: (864, 576, 624, 312),
    8486: (552,),
    8487: (432, 552, 744),
    8488: (72, 576, 792),
    8489: (912, 672, 528),
    8490: (456, 600, 672, 264),
    8491: (768, 720, 840, 504),
}
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "293D16C91520E455AA4FEB6539B00A7B1D4F207D66ADDCFF87F6EB9715524A94",
    "raw_size": 996_228,
    "sha256": "0FF01B159898CA5E9C1004CE030FE8B6B42B2618DD85821F6DE7AADA43CCCBD8",
    "size": 1_000_160,
}


class Wave96Error(RuntimeError):
    """Raised when the strict predecessor, direct context, or output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave96Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave96Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W95C_BUILDER.is_file(), f"W95c helper builder missing: {W95C_BUILDER}")
w95c = load_module("pc_event_wave95c_base_for_wave96", W95C_BUILDER)
parse_table = w95c.parse_table
core = w95c.core
control_signature = w95c.control_signature
is_full_width_visible = w95c.is_full_width_visible


@dataclass(frozen=True)
class Bundle:
    event: bytes
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
        raise Wave96Error(f"candidate escapes tmp root: {resolved}") from exc
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
    return full * RAW_FULL_WIDTH_PX + (len(display) - full) * RAW_HALF_WIDTH_PX


def validate_runtime_reservations() -> None:
    expected = {
        "[b1871]": (1871, "마츠다이라 모토야스", 456),
        "[bm1871]": (1871, "마츠다이라 모토야스", 456),
        "[bs1871]": (1871, "마츠다이라", 240),
        "[bs754]": (754, "기노시타", 192),
    }
    require(set(SCENE_RUNTIME_RESERVATIONS) == set(expected), "W96 reservation scope drift")
    for token, (slot_id, display, width) in expected.items():
        reservation = SCENE_RUNTIME_RESERVATIONS[token]
        require(reservation["source_slot_id"] == slot_id, f"W96 reservation slot drift: {token}")
        require(reservation["display"] == display, f"W96 reservation display drift: {token}")
        require(reservation["reserved_raw_g1n_width_px"] == width, f"W96 reservation width drift: {token}")
        require(raw_width(display) == width, f"W96 reservation measurement drift: {token}")
        require(reservation["scene_limited"] is True, f"W96 reservation not scene-limited: {token}")
        require(reservation["runtime_proven"] is False, f"W96 runtime proof unexpectedly asserted: {token}")


def rendered_display_line(value: str) -> str:
    rendered: list[str] = []
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token in layout: {token!r}")
            cursor += 3
            continue
        runtime = RUNTIME_RE.match(value, cursor)
        if runtime is not None:
            token = runtime.group(0)
            reservation = SCENE_RUNTIME_RESERVATIONS.get(token)
            require(reservation is not None, f"missing W96 scene reservation: {token}")
            rendered.append(str(reservation["display"]))
            cursor = runtime.end()
            continue
        character = value[cursor]
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        rendered.append(character)
        cursor += 1
    return "".join(rendered)


def line_metrics(value: str) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for number, line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        display = rendered_display_line(line)
        full = sum(1 for character in display if is_full_width_visible(character))
        half = len(display) - full
        raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
        rows.append(
            {
                "line_number": number,
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
    require(len(SCENE_IDS) == 50, "W96 scene length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W96 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W96 retained scope drift")
    require(len(RETAINED_IDS) == 32, "W96 retained count drift")
    validate_runtime_reservations()
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(set(runtime_tokens(target)).issubset(SCENE_RUNTIME_RESERVATIONS), f"W96 unknown target runtime token: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W96 target line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W96 target raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        if TARGET_RAW_WIDTHS is not None:
            require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id], f"W96 target widths drift: {entry_id}")


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W95c candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W95c predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W95C_PROFILE, "W95c on-disk event profile drift")
    require(w95c.EXPECTED_OUTPUT_PROFILE == EXPECTED_W95C_PROFILE, "W95c pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W95C_PROFILE, "W95c audit output profile drift")
    require(manifest.get("output") == EXPECTED_W95C_PROFILE, "W95c manifest output profile drift")
    return event, table, raw, predecessor_profile


def load_direct_contexts() -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
    loader = getattr(w95c, "load_direct_contexts", None)
    require(callable(loader), "W95c direct-PC context loader missing")
    tables, profiles = loader()
    require(tuple(sorted(tables)) == ("en", "jp", "sc", "tc"), "direct PC context language scope drift")
    require(tuple(sorted(profiles)) == ("en", "jp", "sc", "tc"), "direct PC context profile scope drift")
    return tables, profiles


def prepare(*, require_output_profile: bool) -> Bundle:
    validate_static_targets()
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    contexts, context_profiles = load_direct_contexts()
    require(all(len(before.texts) == len(table.texts) for table in contexts.values()), "event table topology drift")

    texts = list(before.texts)
    rows: list[Mapping[str, Any]] = []
    observed_runtime_tokens: set[str] = set()
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = contexts["jp"].texts[entry_id]
        source_en = contexts["en"].texts[entry_id]
        source_sc = contexts["sc"].texts[entry_id]
        source_tc = contexts["tc"].texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(all((current, source_jp, source_en, source_sc, source_tc, target)), f"empty W96 row: {entry_id}")
        current_signature = control_signature(current)
        require(current_signature == control_signature(source_jp), f"W95c/direct-PC-JP control drift: {entry_id}")
        require(control_signature(target) == current_signature, f"W96 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        tokens = runtime_tokens(target)
        require(set(tokens).issubset(SCENE_RUNTIME_RESERVATIONS), f"W96 unknown runtime token: {entry_id}")
        observed_runtime_tokens.update(tokens)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W96 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W96 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        if TARGET_RAW_WIDTHS is not None:
            require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id], f"W96 measured widths drift: {entry_id}")
        changed = entry_id in CHANGED_IDS
        require((target != current) == changed, f"W96 expected change disposition drift: {entry_id}")
        if changed:
            texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "direct_pc_en": source_en,
                "direct_pc_sc": source_sc,
                "direct_pc_tc": source_tc,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "direct_pc_en_utf16le_sha256": text_hash(source_en),
                "direct_pc_sc_utf16le_sha256": text_hash(source_sc),
                "direct_pc_tc_utf16le_sha256": text_hash(source_tc),
                "w95c_current_ko": current,
                "target_ko": target,
                "w95c_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": changed,
                "review_disposition": "semantic_correction" if changed else "retained_after_semantic_lf_reservation_audit",
                "rationale": RATIONALES[entry_id] if changed else "직접 PC 4언어 대조, 의미·수동 개행·예약폭 검사를 통과하여 유지.",
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "lf_only_reflow": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": list(tokens),
                "runtime_reservations": reservation_details(target),
                "runtime_proven": False,
                "control_signature": control_signature(target),
            }
        )

    require(observed_runtime_tokens == set(SCENE_RUNTIME_RESERVATIONS), "W96 observed runtime token scope drift")
    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W95c predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W96 Sanada/Ishikawa event", event)
    require(after_raw == rebuilt_raw, "W96 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W96 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W96 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W96 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-sanada-ishikawa-quality-wave96-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W95c PC Korean candidate plus direct PC JP/EN/SC/TC context",
            "strict_input_only": PREDECESSOR_CANDIDATE_ROOT.relative_to(REPO).as_posix(),
            "switch_korean_used": False,
            "japanese_source_line_breaks_used": False,
            "korean_sentence_shortened_or_deleted": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "network_operation_performed": False,
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
        "input_w95c_event_profile": predecessor_profile,
        "direct_pc_context_profiles": context_profiles,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-sanada-ishikawa-quality-wave96-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": PREDECESSOR_WORKSTREAM,
            "candidate_relative": (PREDECESSOR_CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
            "profile": predecessor_profile,
            "strict_on_disk": True,
        },
        "direct_pc_context_languages": ["jp", "en", "sc", "tc"],
        "changed_row_ids": list(CHANGED_IDS),
        "output": event_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event, audit, manifest, event_profile)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W96 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W96 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W96 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W96 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W96 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W96 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W96 candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": list(CHANGED_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "network_operation_performed": False,
        "runtime_proven": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_sanada_ishikawa_quality_wave96_v1.py",
        WORKSTREAM / "test_pc_event_sanada_ishikawa_quality_wave96_v1.py",
    ):
        require(path.is_file(), f"W96 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W96 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "W96 output profile is not pinned")
        print(write_candidate(prepare(require_output_profile=True)))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    print(json.dumps({"changed_row_ids": list(CHANGED_IDS), "event_profile": bundle.profile}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
