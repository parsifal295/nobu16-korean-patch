#!/usr/bin/env python3
"""Build the W77 Komaki–Nagakute event-quality candidate from on-disk W76."""

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
W76_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_amago_quality_wave76_v1"
    / "build_pc_event_amago_quality_wave76_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
SCENE_IDS = tuple(range(8_235, 8_303))
CHANGED_IDS = (
    8_236,
    8_237,
    8_238,
    8_239,
    8_240,
    8_241,
    8_243,
    8_249,
    8_252,
    8_256,
    8_259,
    8_263,
    8_268,
    8_273,
    8_278,
    8_281,
    8_282,
    8_283,
    8_284,
    8_287,
    8_289,
    8_292,
    8_293,
    8_296,
    8_300,
    8_302,
)
RETAINED_IDS = (
    8_235,
    8_242,
    8_244,
    8_245,
    8_246,
    8_247,
    8_248,
    8_250,
    8_251,
    8_253,
    8_254,
    8_255,
    8_257,
    8_258,
    8_260,
    8_261,
    8_262,
    8_264,
    8_265,
    8_266,
    8_267,
    8_269,
    8_270,
    8_271,
    8_272,
    8_274,
    8_275,
    8_276,
    8_277,
    8_279,
    8_280,
    8_285,
    8_286,
    8_288,
    8_290,
    8_291,
    8_294,
    8_295,
    8_297,
    8_298,
    8_299,
    8_301,
)
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
STATIC_EFFECTIVE_LINE_LIMIT_PX = 912
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

EXPECTED_W76_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "34CEF870EA769ED4D0C89E002A795353AED92C79670FDCF729475A25D82D7949",
    "raw_size": 992_124,
    "sha256": "C4BB65199D1D8FAF7236A12B0BE07A875FE02D6764F8890B69E1423BCAB9F8A6",
    "size": 996_040,
}
# Pinned from the strict W76 on-disk predecessor before the single permitted
# W77 candidate write.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "1F191E28DCFF25D7BC619983782A136D1A6F5FA053C2AC432792256C54B9D3F1",
    "raw_size": 992_912,
    "sha256": "8B85E62DE5611DE14B51BA50B1C4F57F40DB56DFF6ADAC119594196B0FAADB9F",
    "size": 996_831,
}

# These are scene-limited *layout reservations*, not a claim that the running
# game has displayed these exact tokens in this scene.  They use the longest
# known spelling for the corresponding W76 name slot / surname family.
SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {
    "[b1871]": {
        "display": "마쓰다이라 모토야스",
        "source_slot_id": 1871,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W76 msgev slot 1871; 8 full-width characters plus one space",
    },
    "[bm1871]": {
        "display": "마쓰다이라 모토야스",
        "source_slot_id": 1871,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W76 msgev slot 1871; conservative for the historical-name variant",
    },
    "[bs1871]": {
        "display": "마쓰다이라",
        "source_slot_id": 1871,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "four full-width surname reservation",
    },
    "[b754]": {
        "display": "기노시타 히데요시",
        "source_slot_id": 754,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W76 msgev slot 754; 8 full-width characters plus one space",
    },
    "[bs754]": {
        "display": "기노시타",
        "source_slot_id": 754,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "four full-width surname reservation",
    },
    "[b1976]": {
        "display": "미요시 히데쓰구",
        "source_slot_id": 1976,
        "scene_limited": True,
        "runtime_proven": False,
        "basis": "W76 msgev slot 1976; 7 full-width characters plus one space",
    },
}

TARGETS: Mapping[int, str] = {
    8236: (
        "\x1bCA노부카쓰\x1bCZ는 \x1bCA히데요시\x1bCZ 편의 외교를\n"
        "펼치던 \x1bCA쓰가와 요시후유\x1bCZ 등\n"
        "세 명의 가로를 살해했다. 이는\n"
        "\x1bCA히데요시\x1bCZ에게 선전포고한 것과 다름없었다."
    ),
    8237: (
        "\x1bCA노부카쓰\x1bCZ 공… 아니,\n"
        "\x1bCA노부카쓰\x1bCZ 놈! 돌아가신 주군의 혈통을\n"
        "이었다는 이유만으로 재주도 없는 놈을\n"
        "받들어 왔거늘…"
    ),
    8238: (
        "나를 적으로 삼겠다면, 그것도 끝이다.\n"
        "전군에 알려라. \x1bCA오다 노부카쓰\x1bCZ를 토벌한다.\n"
        "주변 세력에도 참전을 요구하라!"
    ),
    8239: (
        "홀로 \x1bCA히데요시\x1bCZ와 맞서는 것은\n"
        "불리하다고 본 \x1bCA노부카쓰\x1bCZ는 선친의\n"
        "맹우이자 \x1bCA히데요시\x1bCZ의 대두를 경계하던\n"
        "\x1bCA[b1871]\x1bCZ에게 도움을 청했다."
    ),
    8240: (
        "옛 주군의 유자에게 칼을 겨누다니…\n"
        "원숭이 공, 장난이 지나치구려.\n"
        "우리 가문은 \x1bCA노부카쓰\x1bCZ 공을 돕겠소!"
    ),
    8241: (
        "\x1bCA[bm1871]\x1bCZ는 \x1bCA히데요시\x1bCZ가\n"
        "다른 세력을 끌어들일 것을 예상하고,\n"
        "스스로도 \x1bCA히데요시\x1bCZ에게 반감을 품은 세력에\n"
        "공동 전선을 펼치자고 제안했다."
    ),
    8243: (
        "\x1bCA노부카쓰\x1bCZ와 \x1bCA히데요시\x1bCZ의 대립은\n"
        "\x1bCA[bm1871]\x1bCZ의 개입으로\n"
        "전국을 휩쓰는 천하를 가를\n"
        "싸움으로 번져 갔다."
    ),
    8249: (
        "\x1bCC고마키야마\x1bCZ에서 대치한\n"
        "\x1bCA[bs754]히데요시\x1bCZ군과 \x1bCA오다 노부카쓰\x1bCZ·\n"
        "\x1bCA[b1871]\x1bCZ의 연합군―"
    ),
    8252: (
        "\x1bCA[b1976]\x1bCZ는 \x1bCA히데요시\x1bCZ의 누이의\n"
        "아들이었다. 전쟁 경험이 적은 것을\n"
        "염려한 \x1bCA히데요시\x1bCZ는 그를 이번 출진에\n"
        "참가시켰다."
    ),
    8256: (
        "\x1bCA[bs1871]\x1bCZ가 없다면\n"
        "\x1bCA노부카쓰\x1bCZ 공 따위는 적수가 아닙니다.\n"
        "하지만 \x1bCA[bm1871]\x1bCZ도 이름난\n"
        "늙은 너구리. 일이 순조로울까요?"
    ),
    8259: (
        "\x1bCA이케다 쓰네오키\x1bCZ는 \x1bCA노부나가\x1bCZ의 젖형제이자\n"
        "측근으로, \x1bCC기요스\x1bCZ 회의에도 참석한\n"
        "중신이었다. 그러나 이 무렵에는\n"
        "\x1bCA히데요시\x1bCZ의 휘하에 머물러 있었다."
    ),
    8263: "예…!\n분부 받들겠나이다…",
    8268: (
        "\x1bCB[bs1871]\x1bCZ의 본국을 기습하려\n"
        "나카이리에 나선 \x1bCA[bs754]히데쓰구\x1bCZ의 군은\n"
        "\x1bCC나가쿠테\x1bCZ 부근에서 되레 \x1bCB도쿠가와\x1bCZ군의\n"
        "급습을 받아 혼란에 빠졌다."
    ),
    8273: (
        "\x1bCC나가쿠테\x1bCZ에서 \x1bCB[bs754]\x1bCZ군도 참패했다.\n"
        "\x1bCA이케다 쓰네오키\x1bCZ·\x1bCA모토스케\x1bCZ·\x1bCA모리 나가요시\x1bCZ는\n"
        "이때 장렬히 전사했다…"
    ),
    8278: (
        "한편 우회 기습대를 격퇴한 \x1bCB[bs1871]\x1bCZ군은\n"
        "사기가 올랐지만, \x1bCA[bm1871]\x1bCZ는\n"
        "냉정하게 전황을 지켜보고 있었다…"
    ),
    8281: (
        "\x1bCC나가쿠테\x1bCZ의 참패에도\n"
        "\x1bCB[bs754]\x1bCZ군은 동요하지 않았고,\n"
        "\x1bCC고마키야마\x1bCZ에서의 대치는 계속됐다…"
    ),
    8282: (
        "\x1bCC나가쿠테\x1bCZ에서 \x1bCA하시바 히데쓰구\x1bCZ 등을 꺾어\n"
        "사기가 오른 \x1bCB[bs1871]\x1bCZ군이었으나,\n"
        "그 뒤 전황은 다시 교착 상태에 빠졌다."
    ),
    8283: (
        "\x1bCC고마키야마\x1bCZ 전선 밖의 각지에서도\n"
        "\x1bCA히데요시\x1bCZ 측 군세와\n"
        "\x1bCA노부카쓰\x1bCZ·\x1bCA[bm1871]\x1bCZ 측 군세가\n"
        "충돌했지만 승패는 명확히 갈리지 않았다."
    ),
    8284: (
        "대치가 길어지며\n"
        "전쟁을 꺼리는 분위기가 짙어지는 가운데,\n"
        "\x1bCA[b1871]\x1bCZ의 진영에\n"
        "충격적인 소식이 전해졌다…"
    ),
    8287: (
        "있을 수 없다…! 우리 군은 아직\n"
        "\x1bCB[bs754]\x1bCZ 세력과 대치하고 있거늘!"
    ),
    8289: (
        "대장인 \x1bCA오다 노부카쓰\x1bCZ가 화친한 이상,\n"
        "\x1bCB[bs1871]\x1bCZ군도 더 싸울 이유가 없었다.\n"
        "\x1bCA[bm1871]\x1bCZ는 전군을 이끌고\n"
        "\x1bCC하마마쓰성\x1bCZ으로 철수했다."
    ),
    8292: (
        "하지만 \x1bCA노부카쓰\x1bCZ의 서신에는\n"
        "뜻밖의 요구가 담겨 있었다.\n"
        "\x1bCA노부카쓰\x1bCZ는 \x1bCA[bm1871]\x1bCZ에게\n"
        "\x1bCA히데요시\x1bCZ와 화친하라고 권하고 있었으니…"
    ),
    8293: (
        "그리하여 화친의 증표로\n"
        "\x1bCA[bm1871]\x1bCZ가 \x1bCA히데요시\x1bCZ에게\n"
        "인질을 보내도록 요청해 온 것이다."
    ),
    8296: (
        "아무리 그래도 맹을 맺은 분이다.\n"
        "\x1bCA노부카쓰\x1bCZ 님의 체면을 꺾을 수는 없다.\n"
        "게다가 화친을 거절하면, 우리는 홀로\n"
        "싸움을 이어 가야 한다."
    ),
    8300: (
        "\x1bCA[bm1871]\x1bCZ가 \x1bCA오기마루\x1bCZ(훗날의\n"
        "\x1bCA히데야스\x1bCZ)를 화친의 증표로 내어 줌으로써,\n"
        "천하를 가르는\n"
        "\x1bCC고마키나가쿠테\x1bCZ 전투는 막을 내렸다."
    ),
    8302: (
        "\x1bCA노부카쓰\x1bCZ·\x1bCA[bm1871]\x1bCZ라는\n"
        "반대파를 억누른 \x1bCA[b754]\x1bCZ는\n"
        "이후 더욱 천하인의 높은 곳으로\n"
        "올라가게 된다."
    ),
}

RATIONALES: Mapping[int, str] = {
    8236: "세 명의 가로 살해와 선전포고의 인과를 복원한다.",
    8237: "망한 주군의 혈통과 지금껏 섬긴 원망을 복원한다.",
    8238: "참진 오기를 참전으로 고치고 주변 세력의 참전 요구를 명확히 한다.",
    8239: "단독 대결의 불리함, 선친의 맹우, 히데요시 대두 경계를 복원한다.",
    8240: "옛 주군의 유자에게 칼을 겨눈다는 의미와 조사를 복원한다.",
    8241: "타 세력 포섭 예측과 반히데요시 공동전선 제안을 복원한다.",
    8243: "전국을 휩쓰는 천하를 가를 싸움으로 번진다는 서술을 복원한다.",
    8249: "고마키야마에서 대치한 양군의 완결된 제목 문장으로 복원한다.",
    8252: "누이의 아들, 부족한 전쟁 경험, 이번 출진 참가의 인과를 복원한다.",
    8256: "반대 세력의 부재와 노회한 너구리 비유, 의문문을 복원한다.",
    8259: "젖형제이자 측근, 기요스 회의 참석, 히데요시 휘하라는 정보를 복원한다.",
    8263: "옛을 예로 정정한다.",
    8268: "나카이리 부대가 나가쿠테에서 역습을 받아 혼란에 빠진 사건을 복원한다.",
    8273: "이케다 쓰네오키의 전명과 세 장수의 전사를 복원한다.",
    8278: "우회 기습 격퇴 뒤의 사기와 냉정한 전황 관찰의 대비를 복원한다.",
    8281: "고마키야마 표기를 통일하고 대치 지속을 복원한다.",
    8282: "히데쓰구 등과 이후 재교착을 복원한다.",
    8283: "전선 밖 각지의 충돌과 명확한 승패 부재를 복원한다.",
    8284: "염전 동음오역을 전쟁을 꺼리는 분위기로 정정한다.",
    8287: "분리된 런타임 토큰과 세 파편을 세력으로 결합한다.",
    8289: "대장의 화친부터 전군 하마마쓰성 철수까지의 인과를 복원한다.",
    8292: "서신의 뜻밖 요구와 화친 권유 문장을 복원한다.",
    8293: "화친 증표로 인질을 보내도록 한 요구의 주체와 대상을 정리한다.",
    8296: "맹을 맺은 상대의 체면과 화친 거절 시 단독전 지속을 복원한다.",
    8300: "오기마루의 후일 이름, 화친 증표, 전투 종결을 복원한다.",
    8302: "조사 오류를 바로잡고 반대파 억제 뒤 천하인으로의 상승을 복원한다.",
}


class Wave77Error(RuntimeError):
    """Raised when the W76 predecessor or W77 contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave77Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave77Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w76 = load_module("pc_event_wave76_for_wave77", W76_BUILDER)
parse_table = w76.w75.w74.w73.w72.w71.w66.w60.parse_table
core = w76.w75.w74.w73.w72.w71.w66.w60.core
control_signature = w76.w75.w74.w73.w72.w71.w70.control_signature
is_full_width_visible = w76.w75.w74.w73.w72.is_full_width_visible


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
        raise Wave77Error(f"candidate escapes tmp root: {resolved}") from exc
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
            require(reservation is not None, f"missing W77 scene reservation: {token}")
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
        effective = (raw * DRAW_FONT_PX + RAW_FULL_WIDTH_PX - 1) // RAW_FULL_WIDTH_PX
        rows.append(
            {
                "line_number": line_number,
                "display_string": display,
                "raw_g1n_width_px": raw,
                "effective_width_px": effective,
                "full_width_character_count": full,
                "half_width_character_count": half,
                "over_live_raw_960px": raw > RAW_LINE_LIMIT_PX,
                "over_static_patch_912px": effective > STATIC_EFFECTIVE_LINE_LIMIT_PX,
            }
        )
    return tuple(rows)


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = w76.CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W76 candidate file scope drift: {sorted(actual_files)}")
    path = root / MSGEV
    event = path.read_bytes()
    _header, raw, table = parse_table("on-disk W76 Komaki predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W76_PROFILE, "W76 on-disk event profile drift")
    require(w76.EXPECTED_OUTPUT_PROFILE == EXPECTED_W76_PROFILE, "W76 pinned output profile drift")
    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit["output_event_profile"] == EXPECTED_W76_PROFILE, "W76 audit output profile drift")
    require(manifest["output"] == EXPECTED_W76_PROFILE, "W76 manifest output profile drift")
    return event, table, raw, predecessor_profile


def load_direct_jp() -> Any:
    blob, _profile = w76.w75.w74.w73.w72.w71.w66.w62.load_direct_jp_event()
    _header, _raw, table = parse_table("direct PC Japanese event", blob)
    return table


def prepare(*, require_output_profile: bool) -> Bundle:
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    direct_jp = load_direct_jp()
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")
    require(tuple(TARGETS) == CHANGED_IDS, "W77 target scope drift")
    require(tuple(identifier for identifier in SCENE_IDS if identifier not in CHANGED_IDS) == RETAINED_IDS, "W77 retained scope drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS.get(entry_id, current)
        require(bool(current) and bool(source_jp), f"empty Komaki row: {entry_id}")
        current_signature = control_signature(current)
        jp_signature = control_signature(source_jp)
        target_signature = control_signature(target)
        require(current_signature == jp_signature, f"W76/direct-JP control drift: {entry_id}")
        require(target_signature == current_signature, f"W77 control/token drift: {entry_id}")
        assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W77 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W77 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        require(
            not any(metric["over_static_patch_912px"] for metric in metrics),
            f"W77 effective width exceeds {STATIC_EFFECTIVE_LINE_LIMIT_PX}px: {entry_id}",
        )
        if target != current:
            changed[entry_id] = target
            texts[entry_id] = target
        tokens = runtime_tokens(target)
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w76_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w76_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": target != current,
                "review_disposition": "changed" if target != current else "retained_after_review",
                "rationale": RATIONALES.get(entry_id, "직접 PC JP와 PC EN/SC/TC 문맥 대조 후 유지한다."),
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": list(tokens),
                "runtime_layout_proven": not bool(tokens),
                "control_signature": target_signature,
            }
        )
    require(tuple(sorted(changed)) == CHANGED_IDS, "W77 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("on-disk W76 Komaki predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W77 Komaki event", event)
    require(after_raw == rebuilt_raw, "W77 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W77 actual event diff scope drift",
    )
    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W77 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W77 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-komaki-nagakute-quality-wave77-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W76 Steam-PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
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
            "static_patch_effective_line_limit_px": STATIC_EFFECTIVE_LINE_LIMIT_PX,
            "max_lines": MAX_LINES,
            "draw_font_px": DRAW_FONT_PX,
            "display_effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "runtime_reservations": SCENE_RUNTIME_RESERVATIONS,
            "runtime_reservations_scene_limited": True,
            "runtime_reservations_runtime_proven": False,
        },
        "coverage": {
            "reviewed_scene_ids": list(SCENE_IDS),
            "reviewed_scene_row_count": len(SCENE_IDS),
            "changed_row_ids": list(CHANGED_IDS),
            "changed_row_count": len(CHANGED_IDS),
            "unchanged_after_review_ids": list(RETAINED_IDS),
            "unchanged_after_review_count": len(RETAINED_IDS),
        },
        "input_w76_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-komaki-nagakute-quality-wave77-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": w76.WORKSTREAM.name,
            "candidate_relative": (w76.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
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
    require(not output.exists(), f"W77 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W77 candidate staging exists: {staging}")
    staging.mkdir(parents=True)
    try:
        event_path = staging / MSGEV
        event_path.parent.mkdir(parents=True, exist_ok=True)
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
    require(root.is_dir(), f"W77 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W77 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W77 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W77 candidate audit differs")
    require(
        (root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "W77 candidate manifest differs",
    )
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": list(CHANGED_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "runtime_reservations_runtime_proven": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_komaki_nagakute_quality_wave77_v1.py",
        WORKSTREAM / "test_pc_event_komaki_nagakute_quality_wave77_v1.py",
    ):
        require(path.is_file(), f"W77 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W77 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        bundle = prepare(require_output_profile=False)
        print(json.dumps(bundle.profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        bundle = prepare(require_output_profile=True)
        output = write_candidate(bundle)
        print(output)
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
