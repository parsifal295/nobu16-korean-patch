#!/usr/bin/env python3
"""Build the private W95 Tachibana-aftermath event-quality candidate from W94.

This workstream audits the complete ID 8392–8441 aftermath scene against
direct PC JP/EN/SC/TC context.  Dynamic name tokens are measured through the
scene-local conservative reservations below, never by stripping the tokens.
Only this workstream's private ``tmp`` root is writable by the build command.
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

W94_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_otomo_tachibana_quality_wave94_v1"
    / "build_pc_event_otomo_tachibana_quality_wave94_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_otomo_tachibana_quality_wave94_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W94_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "E323F774A74064DD00C8AD3670D76A03DCAE0C1100D1707DBA662EC999370358",
    "raw_size": 995_840,
    "sha256": "BC51F8954CA078D2BC96FCC8E82F7343F5DE5FB7892CE1954C1E987E8FAED7EE",
    "size": 999_771,
}

# 8392 continues the preceding exchange; 8441 closes the Ginchiyo aftermath
# narration.  8442 begins a separate scene and is deliberately excluded.
SCENE_IDS = tuple(range(8_392, 8_442))
CHANGED_IDS = (
    8392,
    8393,
    8394,
    8395,
    8397,
    8399,
    8405,
    8407,
    8410,
    8411,
    8412,
    8417,
    8419,
    8421,
    8423,
    8425,
    8426,
    8427,
    8428,
    8429,
    8432,
    8433,
    8435,
    8438,
    8441,
)
RETAINED_IDS = tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS)

# Static patch 007 baseline.  The raw 48/24 G1N measurement is the hard gate;
# the 30px effective width is audit evidence only.
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

# Conservative scene-local reservations; these are not runtime observations.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[bm1222]": {
        "display": "다카하시 무네토라",
        "source_slot_id": 1222,
        "reserved_raw_g1n_width_px": 408,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "officer-name slot 1222; conservative full-name reservation for this scene only",
    },
    "[b1222]": {
        "display": "다카하시 무네토라",
        "source_slot_id": 1222,
        "reserved_raw_g1n_width_px": 408,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "officer-name slot 1222; conservative full-name reservation for this scene only",
    },
    "[b1221]": {
        "display": "다카하시 조운",
        "source_slot_id": 1221,
        "reserved_raw_g1n_width_px": 312,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "officer-name slot 1221; conservative full-name reservation for this scene only",
    },
    "[bm1730]": {
        "display": "벳키 아키츠라",
        "source_slot_id": 1730,
        "reserved_raw_g1n_width_px": 312,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "officer-name slot 1730; conservative full-name reservation for this scene only",
    },
    "[b1730]": {
        "display": "벳키 아키츠라",
        "source_slot_id": 1730,
        "reserved_raw_g1n_width_px": 312,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "officer-name slot 1730; conservative full-name reservation for this scene only",
    },
}
ROW_RUNTIME_TOKENS: Mapping[int, tuple[str, ...]] = {
    8394: ("[bm1222]", "[bm1730]"),
    8396: ("[bm1730]",),
    8399: ("[b1222]", "[b1221]", "[b1730]"),
    8400: ("[bm1730]",),
    8404: ("[bm1730]",),
    8440: ("[bm1222]",),
}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    8392: "(이제 내가 아비라 불릴 일도\n없겠지……)",
    8393: "(그걸로 됐다……\n그래야 하는 거다……)",
    8394: (
        f"{E}CA[bm1222]{E}CZ가 이끄는 {E}CB오토모{E}CZ군은\n"
        f"{E}CA[bm1730]{E}CZ의 유해를 모시고\n"
        f"{E}CC다치바나야마성{E}CZ으로 돌아갔다."
    ),
    8395: "명장의 죽음을 애도한 적장들은\n그 장례 행렬을 조용히 배웅하며,\n끝내 손을 대지 않았다.",
    8397: "아……",
    8399: (
        f"{E}CA[b1222]{E}CZ는\n"
        f"{E}CA[b1221]{E}CZ의 적자였으나,\n"
        f"{E}CA[b1730]{E}CZ의 데릴사위 겸 양자가 되어\n"
        f"그 딸 {E}CA긴치요{E}CZ를 아내로 맞이했다."
    ),
    8405: "아버님 일은 미안하네.\n내 간병이 부족했던 탓이지.",
    8407: "아, 아아. 아버님의 분부를\n어기게 되어 버렸지만 말이다.",
    8410: "아버님께서는 유해를\n그 전장에 묻으라 말씀하셨던 것이다.",
    8411: "그런 것은 아무도 가르쳐주지 않았습니다.",
    8412: "뭐, 뭐…… 내가 아버님의 유언을\n어기게 된 셈이니.\n그리 떠벌릴 일은 아니겠지.",
    8417: "그런 말씀이 아닙니다.\n아버님께서…… 아버님과 당신께서\n나눈 이야기를 묻는 것입니다.",
    8419: "당신께서 오신 뒤로,\n아버님은 당신하고만 나가시고……\n저는 거들떠보지도 않으셨으니까요.",
    8421: "아버님 이야기인가, 그렇군…\n은어 먹는 법이 무사답지 않다고\n꾸중을 들었다든가.\n이런 이야기면 되겠는가?",
    8423: "생선을 손으로 뜯어 먹다니,\n무사가 할 짓이 아니다.\n쓸모없는 자가 된다며\n호되게 꾸짖음을 들었다.",
    8425: "그 밖에는, 길을 걷다가\n밤송이를 밟아 버려서\n가신에게 빼 달라 부탁했더니……",
    8426: "부탁했더니, 어떻게 되었습니까?",
    8427: "아버님의 신호에 달려온 그자는\n밤송이를 힘껏 내 발에\n밀어 넣었던 것이다.",
    8428: "무사가 아프다는 둥\n우는소리를 해서는 안 된다고 하셨지.",
    8429: "아버님 말씀대로이옵니다.\n무사가 우는소리를 해서는 아니 되옵니다!",
    8432: f"아버님이 안 계셔도 이 {E}CA무네시게{E}CZ가 있다.\n외로우면 언제든 찾아오면 될 것이다.",
    8433: "외, 외롭다니 그런 일은 없습니다!",
    8435: "나는, 아버님께 뒤지지 않는 무사가\n되도록 힘쓸 생각이다.\n그대도 건강하거라.",
    8438: "무사로서의 기량은 아버님을 넘는다…\n당신은\n아버님 말씀 그대로의 분이셨습니다.",
    8441: "두 사람이 헤어져 살게 된 까닭은\n‘불화’였다고 전해지지만, 그 말에 담긴\n미묘한 뜻을 아는 이는 이제 없다.",
}

# These rows intentionally alter only spacing/LF placement.  After every line
# break is normalized to one space, their target text must remain byte-for-byte
# equal to the strict W94 predecessor's visible text and control sequence.
LF_ONLY_IDS = (8407, 8410, 8411, 8421, 8423, 8427, 8429, 8432, 8435, 8438)

RATIONALES: Mapping[int, str] = {
    **{entry_id: "direct PC JP/EN/SC/TC context revalidated; retained" for entry_id in RETAINED_IDS},
    8392: "더는 아비라 불리지 않을 독백의 뜻과 자연스러운 한국어 개행을 복원",
    8393: "그것으로 충분하며 그래야 한다는 독백의 의미를 복원",
    8394: "유해를 모시고 성으로 돌아간 서술을 복원하고 예약폭 포함 개행 적용",
    8395: "적장이 장례 행렬을 애도하고 방해하지 않았다는 뜻을 복원",
    8397: "감탄사의 길이와 여운을 원문에 맞춤",
    8399: "적자·데릴사위·양자·혼인의 모든 관계를 보존하고 예약폭 포함 개행 적용",
    8405: "사과와 간병 부족의 인과를 자연스럽게 복원",
    8407: "원문의 단어를 보존한 채 아버님의 분부를 어긴 문장을 의미 단위로 재개행",
    8410: "원문의 단어를 보존한 채 유해와 전장 매장의 명령을 의미 단위로 재개행",
    8411: "원문의 단어를 보존한 채 주어만 남은 줄을 한 문장으로 재개행",
    8412: "유언을 어긴 사실과 떠벌리지 않겠다는 뜻을 복원",
    8417: "두 사람이 나눈 이야기를 묻는다는 대상을 명확히 복원",
    8419: "아버지가 상대와만 외출하고 자신을 돌보지 않았다는 원망을 복원",
    8421: "원문의 단어를 보존한 채 꾸중을 들은 일화의 어절 절단을 의미 단위로 재개행",
    8423: "원문의 단어를 보존한 채 쓸모없는 자라는 수식어 절단을 해소",
    8425: "밤송이와 가신에게 부탁한 일화를 자연스럽게 복원",
    8426: "부탁 뒤의 결과를 묻는 자연스러운 질문으로 복원",
    8427: "원문의 단어를 보존한 채 밤송이를 발에 밀어 넣은 사건을 의미 단위로 재개행",
    8428: "아픔을 호소하지 말라는 아버지의 말이라는 뜻을 복원",
    8429: "원문의 단어를 보존한 채 무사가 우는소리를 해서는 안 된다는 문장을 재개행",
    8432: "원문의 단어를 보존한 채 외로우면 찾아오라는 조건절의 단독 줄을 해소",
    8433: "외로움을 부정하는 더듬는 반응을 자연스럽게 복원",
    8435: "원문의 단어를 보존한 채 아버님께 뒤지지 않는 무사라는 수식어 절단을 해소",
    8438: "원문의 단어를 보존한 채 아버님 말씀 그대로라는 수식어 절단을 해소",
    8441: "불화라는 말의 미묘한 뜻을 아는 이가 없다는 결말을 복원",
}

# Every line below has its dynamic name token replaced by the appropriate
# reservation before measurement.  The map covers all 50 reviewed rows.
SCENE_RAW_WIDTHS: Mapping[int, tuple[int, ...]] = {
    8392: (648, 216),
    8393: (336, 456),
    8394: (888, 696, 672),
    8395: (696, 744, 528),
    8396: (864, 792, 768),
    8397: (96,),
    8398: (96,),
    8399: (456, 648, 936, 744),
    8400: (912, 888, 792),
    8401: (648, 480),
    8402: (216, 672),
    8403: (96,),
    8404: (528, 768, 744),
    8405: (504, 624),
    8406: (312, 792),
    8407: (600, 672),
    8408: (672,),
    8409: (528, 600),
    8410: (456, 840),
    8411: (936,),
    8412: (696, 408, 624),
    8413: (528,),
    8414: (768, 216),
    8415: (576,),
    8416: (792, 696),
    8417: (504, 720, 672),
    8418: (504,),
    8419: (456, 720, 792),
    8420: (648,),
    8421: (624, 720, 432, 552),
    8422: (384,),
    8423: (624, 528, 480, 552),
    8424: (120, 576),
    8425: (528, 480, 696),
    8426: (720,),
    8427: (696, 504, 456),
    8428: (432, 840),
    8429: (576, 936),
    8430: (336, 888),
    8431: (72,),
    8432: (912, 840),
    8433: (768,),
    8434: (480, 336),
    8435: (792, 504, 432),
    8436: (480,),
    8437: (96,),
    8438: (816, 144, 816),
    8439: (432,),
    8440: (840, 576, 600),
    8441: (744, 888, 768),
}

# Pinned from the one-time read-only W95 profile pass against strict W94.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "3401B422130D3E183EC249DFE2E243B95DF32CE8C385BB0AAD64756E4C6C492A",
    "raw_size": 995_848,
    "sha256": "93BAACFE32433E3E09555258FACFD44EFE09F0D1860EF6B496FFD38B16F847D4",
    "size": 999_779,
}

# This is the one exact private candidate produced before the ten LF-only
# reflows were added.  It is accepted only by the explicit rebuild command so
# the obsolete private directory can be atomically regenerated once.
STALE_PRE_LF_REBUILD_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "CD7443BF9F577F2101CCED4B504CEE85C78B1EA3267C80D803788CE831DD31F2",
    "raw_size": 995_848,
    "sha256": "3F2A6B1EA2CF6C137AE6AD4E58C676774D2FD363816BD531C5A414853109BFB9",
    "size": 999_779,
}


class Wave95Error(RuntimeError):
    """Raised when source, token reservation, layout, or candidate drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave95Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave95Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W94_BUILDER.is_file(), f"W94 helper builder missing: {W94_BUILDER}")
w94 = load_module("pc_event_wave94_base_for_wave95", W94_BUILDER)
parse_table = w94.parse_table
core = w94.core
control_signature = w94.control_signature
is_full_width_visible = w94.is_full_width_visible


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
        raise Wave95Error(f"candidate escapes tmp root: {resolved}") from exc
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
        "[bm1222]": (1222, "다카하시 무네토라", 408),
        "[b1222]": (1222, "다카하시 무네토라", 408),
        "[b1221]": (1221, "다카하시 조운", 312),
        "[bm1730]": (1730, "벳키 아키츠라", 312),
        "[b1730]": (1730, "벳키 아키츠라", 312),
    }
    require(set(SCENE_RUNTIME_RESERVATIONS) == set(expected), "W95 reservation scope drift")
    for token, (slot_id, display, raw) in expected.items():
        reservation = SCENE_RUNTIME_RESERVATIONS[token]
        require(reservation.get("source_slot_id") == slot_id, f"W95 reservation slot drift: {token}")
        require(reservation.get("display") == display, f"W95 reservation display drift: {token}")
        require(reservation.get("reserved_raw_g1n_width_px") == raw, f"W95 reservation raw width drift: {token}")
        require(raw_width(display) == raw, f"W95 reservation measured width drift: {token}")
        require(reservation.get("scene_limited") is True, f"W95 reservation not scene-limited: {token}")
        require(reservation.get("runtime_proven") is False, f"W95 runtime proof unexpectedly asserted: {token}")


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
            require(reservation is not None, f"missing W95 scene reservation: {token}")
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
    require(tuple(TARGETS) == CHANGED_IDS, "W95 target scope drift")
    require(tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS, "W95 retained scope drift")
    require(set(SCENE_RAW_WIDTHS) == set(SCENE_IDS), "W95 all-row metrics scope drift")
    require(LF_ONLY_IDS == (8407, 8410, 8411, 8421, 8423, 8427, 8429, 8432, 8435, 8438), "W95 LF-only scope drift")
    require(set(LF_ONLY_IDS).issubset(CHANGED_IDS), "W95 LF-only rows must be changed")
    validate_runtime_reservations()
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(runtime_tokens(target) == ROW_RUNTIME_TOKENS.get(entry_id, ()), f"W95 target runtime-token drift: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W95 target line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W95 target raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == SCENE_RAW_WIDTHS[entry_id], f"W95 target widths drift: {entry_id}")


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W94 candidate file scope drift: {sorted(actual_files)}")
    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W94 Tachibana-aftermath predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W94_PROFILE, "W94 on-disk event profile drift")
    require(w94.EXPECTED_OUTPUT_PROFILE == EXPECTED_W94_PROFILE, "W94 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W94_PROFILE, "W94 audit output profile drift")
    require(manifest.get("output") == EXPECTED_W94_PROFILE, "W94 manifest output profile drift")
    prior_changed = set(audit.get("coverage", {}).get("changed_row_ids", []))
    require(not prior_changed.intersection(SCENE_IDS), "W94 unexpectedly overlaps the W95 scene")
    return event, table, raw, predecessor_profile


def load_direct_contexts() -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
    tables: dict[str, Any] = {}
    profiles: dict[str, Mapping[str, Any]] = {}
    for language, path in w94.w93.w92.DIRECT_CONTEXT_PATHS.items():
        resolved = path.resolve(strict=True)
        parts = {part.casefold() for part in resolved.parts}
        require("switch" not in parts, f"non-PC context source forbidden: {resolved}")
        event = resolved.read_bytes()
        _header, raw, table = parse_table(f"direct PC {language.upper()} W95 context", event)
        source_profile = profile(event, raw)
        require(source_profile == w94.w93.w92.EXPECTED_CONTEXT_PROFILES[language], f"direct PC {language.upper()} profile drift")
        require(len(table.texts) == w94.w93.w92.EXPECTED_CONTEXT_ROW_COUNT, f"direct PC {language.upper()} row count drift")
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
        require(all((current, source_jp, source_en, source_sc, source_tc)), f"empty W95 row: {entry_id}")
        current_signature = control_signature(current)
        source_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == source_signature, f"W94/direct-PC-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W95 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        require(runtime_tokens(target) == ROW_RUNTIME_TOKENS.get(entry_id, ()), f"W95 runtime token differs in row: {entry_id}")
        if entry_id in LF_ONLY_IDS:
            require(
                LINEBREAK_RE.sub(" ", target) == LINEBREAK_RE.sub(" ", current),
                f"W95 LF-only visible text drift: {entry_id}",
            )
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W95 line count exceeds {MAX_LINES}: {entry_id}")
        require(not any(metric["over_live_raw_960px"] for metric in metrics), f"W95 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}")
        require(tuple(metric["raw_g1n_width_px"] for metric in metrics) == SCENE_RAW_WIDTHS[entry_id], f"W95 reservation-aware widths drift: {entry_id}")

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
                "w94_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "direct_pc_en_utf16le_sha256": text_hash(source_en),
                "direct_pc_sc_utf16le_sha256": text_hash(source_sc),
                "direct_pc_tc_utf16le_sha256": text_hash(source_tc),
                "w94_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "review_disposition": "changed" if target != current else "retained_after_review",
                "rationale": RATIONALES[entry_id],
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "lf_only_reflow": entry_id in LF_ONLY_IDS,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": list(runtime_tokens(target)),
                "runtime_reservations": reservation_details(target),
                "runtime_proven": False,
                "control_signature": target_signature,
            }
        )

    require(tuple(sorted(changed)) == CHANGED_IDS, "W95 changed ID scope drift")
    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W94 Tachibana-aftermath predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W95 Tachibana-aftermath event", event)
    require(after_raw == rebuilt_raw, "W95 raw reparse mismatch")
    require({index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS), "W95 actual event diff scope drift")
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W95 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W95 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-tachibana-aftermath-quality-wave95-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W94 PC Korean candidate plus direct PC JP/EN/SC/TC context",
            "switch_korean_used": False,
            "japanese_source_line_breaks_used": False,
            "korean_text_shortened_or_deleted": False,
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
        "input_w94_event_profile": predecessor_profile,
        "direct_pc_context_profiles": context_profiles,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-tachibana-aftermath-quality-wave95-manifest.v1",
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
        "network_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event, changed, tuple(rows), audit, manifest, event_profile)


def write_candidate(bundle: Bundle, *, replace_stale_private_candidate: bool = False) -> Path:
    output = require_private(CANDIDATE_ROOT)
    if output.exists():
        require(replace_stale_private_candidate, f"W95 candidate already exists: {output}")
        expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
        actual_files = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
        require(actual_files == expected_files, f"W95 stale candidate file scope drift: {sorted(actual_files)}")
        stale_audit = json.loads((output / "audit.v1.json").read_text(encoding="utf-8"))
        stale_manifest = json.loads((output / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
        require(stale_audit.get("output_event_profile") == STALE_PRE_LF_REBUILD_PROFILE, "W95 stale audit profile is not the pre-LF candidate")
        require(stale_manifest.get("output") == STALE_PRE_LF_REBUILD_PROFILE, "W95 stale manifest profile is not the pre-LF candidate")
        shutil.rmtree(output)
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W95 candidate staging exists: {staging}")
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
    require(root.is_dir(), f"W95 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W95 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W95 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W95 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W95 candidate manifest differs")
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
        WORKSTREAM / "build_pc_event_tachibana_aftermath_quality_wave95_v1.py",
        WORKSTREAM / "test_pc_event_tachibana_aftermath_quality_wave95_v1.py",
    ):
        require(path.is_file(), f"W95 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W95 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "rebuild-stale-private", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "W95 output profile is not pinned")
        print(write_candidate(prepare(require_output_profile=True)))
        return 0
    if command == "rebuild-stale-private":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "W95 output profile is not pinned")
        print(write_candidate(prepare(require_output_profile=True), replace_stale_private_candidate=True))
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
